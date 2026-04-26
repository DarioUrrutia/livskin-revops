"""Conftest: fixtures comunes para todos los tests.

Estrategia:
- DB de tests SEPARADA (livskin_erp_test) en el mismo Postgres.
- Schema completo aplicado vía SQLAlchemy create_all() + triggers SQL extra
  (DEBE dinámico + audit_log immutable) replicando las migrations 0002 + 0003.
- Cada test corre dentro de un SAVEPOINT que se rollbackea al final → tests
  isolados, sin necesidad de TRUNCATE explícito entre runs.
- Sesión Flask test_client construido sobre `app.create_app()` con override
  de SECRET_KEY y la URL de la test DB.

Uso:
    docker exec erp-flask pytest /app/tests/
"""
import os
import sys

# Apuntar Settings a test DB ANTES de importar config.
# Forzamos override (no setdefault) porque el container ya tiene
# ERP_DB_NAME=livskin_erp del docker-compose.
os.environ["ERP_DB_NAME"] = "livskin_erp_test"
os.environ["FLASK_ENV"] = "testing"

sys.path.insert(0, "/app")

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from config import settings  # noqa: E402
from models.base import Base  # noqa: E402

# Importar todos los models para que Base.metadata los registre
from models import audit_log  # noqa: F401, E402
from models import catalogo  # noqa: F401, E402
from models import cliente  # noqa: F401, E402
from models import dedup_candidate  # noqa: F401, E402
from models import form_submission  # noqa: F401, E402
from models import gasto  # noqa: F401, E402
from models import lead  # noqa: F401, E402
from models import lead_touchpoint  # noqa: F401, E402
from models import pago  # noqa: F401, E402
from models import user  # noqa: F401, E402
from models import user_session  # noqa: F401, E402
from models import venta  # noqa: F401, E402


TRIGGER_DEBE_SQL = """
CREATE OR REPLACE FUNCTION recompute_venta_debe(target_cod_item TEXT)
RETURNS VOID AS $$
DECLARE
    sum_pagos NUMERIC(10,2);
BEGIN
    IF target_cod_item IS NULL OR target_cod_item = '' THEN
        RETURN;
    END IF;
    SELECT COALESCE(SUM(monto), 0) INTO sum_pagos
    FROM pagos WHERE cod_item = target_cod_item;
    UPDATE ventas
    SET pagado = LEAST(total, sum_pagos),
        debe = GREATEST(0, total - sum_pagos),
        updated_at = NOW()
    WHERE cod_item = target_cod_item;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trigger_recompute_debe()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM recompute_venta_debe(OLD.cod_item);
        RETURN OLD;
    ELSE
        PERFORM recompute_venta_debe(NEW.cod_item);
        IF TG_OP = 'UPDATE' AND OLD.cod_item IS DISTINCT FROM NEW.cod_item THEN
            PERFORM recompute_venta_debe(OLD.cod_item);
        END IF;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pagos_recompute_debe ON pagos;
CREATE TRIGGER pagos_recompute_debe
    AFTER INSERT OR UPDATE OR DELETE ON pagos
    FOR EACH ROW
    EXECUTE FUNCTION trigger_recompute_debe();
"""

TRIGGER_AUDIT_IMMUTABLE_SQL = """
CREATE OR REPLACE FUNCTION audit_log_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log es inmutable — UPDATE/DELETE no permitidos';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_audit_modification ON audit_log;
CREATE TRIGGER prevent_audit_modification
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW
    EXECUTE FUNCTION audit_log_immutable();
"""


@pytest.fixture(scope="session")
def engine():
    """Engine apuntado a la test DB. Crea schema + triggers una sola vez por session."""
    eng = create_engine(settings.database_url, future=True)

    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    with eng.begin() as conn:
        conn.execute(text(TRIGGER_DEBE_SQL))
        conn.execute(text(TRIGGER_AUDIT_IMMUTABLE_SQL))

    yield eng
    eng.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """Sesión SQLAlchemy. Cleanup via TRUNCATE de todas las tablas al final.

    Más simple que SAVEPOINTs porque permite que sessions abiertas por
    session_scope() (en routes) vean datos creados por la session principal
    sin pelearse con savepoints anidados.
    """
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        with engine.begin() as conn:
            conn.execute(
                text(
                    "TRUNCATE TABLE audit_log, user_sessions, users, pagos, ventas, "
                    "gastos, leads, lead_touchpoints, dedup_candidates, form_submissions, "
                    "catalogos, clientes RESTART IDENTITY CASCADE;"
                )
            )


@pytest.fixture(scope="function")
def patched_session_scope(monkeypatch, engine):
    """Override db.session_scope con session real (commit funcional).

    Las routes ven datos commiteados por db_session (vía session.commit()
    explícito en los fixtures user/cliente). El cleanup via TRUNCATE
    de db_session los limpia al final.
    """
    from contextlib import contextmanager

    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    @contextmanager
    def _scope():
        s = Session()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    import db
    monkeypatch.setattr(db, "session_scope", _scope)
    yield _scope


@pytest.fixture(scope="function")
def app(engine, patched_session_scope):
    """Flask app con DB de tests."""
    from app import create_app

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"

    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Usuario admin commiteado para tests de auth/admin (visible por session_scope)."""
    from models.user import User
    from services.auth_service import hash_password

    u = User(
        cod_usuario="USR-TEST-ADMIN",
        username="testadmin",
        nombre_completo="Test Admin",
        email="admin@test.com",
        password_hash=hash_password("TestPass123"),
        rol="admin",
        activo=True,
        failed_login_count=0,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture(scope="function")
def operadora_user(db_session):
    """Usuario operadora commiteado para tests de roles/permisos."""
    from models.user import User
    from services.auth_service import hash_password

    u = User(
        cod_usuario="USR-TEST-OP",
        username="testop",
        nombre_completo="Test Operadora",
        email=None,
        password_hash=hash_password("TestPass456"),
        rol="operadora",
        activo=True,
        failed_login_count=0,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u
