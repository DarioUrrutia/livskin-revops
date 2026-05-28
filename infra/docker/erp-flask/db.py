"""Gestión de conexión a Postgres — engine + session factory.

Sprint 1.13 (2026-05-28): pool sizing tuneado para soportar carga
cron paralela (F1 + F2 + F3 + B3 + webhooks Yossie + dashboards humanos)
sin agotar el max_connections=100 de PG.

Cálculo:
- 4 crons concurrentes worst case × 5 conn = 20
- 5 gunicorn workers × 2 conn (request + audit) = 10
- 10 conn headroom para dashboards humanos + dev tools
- Total dedicated erp-flask = 40 (de 100 total)

pool_size=20 = baseline siempre disponible.
max_overflow=20 = picos hasta 40 conexiones.
pool_pre_ping=True = detectar conexiones muertas (PG idle timeout).
pool_recycle=3600 = reciclar conexiones cada 1h (evita stale).
"""
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings

engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager para una sesión transaccional. Commit on success, rollback on error."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
