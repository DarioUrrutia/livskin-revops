"""Alembic environment — shared pattern para brain y erp.

Lee credentials desde env vars (seteadas por docker-compose):
  POSTGRES_SUPERUSER_PASSWORD  — del env_file ../postgres-data/.env
  ALEMBIC_DB_NAME              — livskin_brain o livskin_erp
  ALEMBIC_DB_HOST              — normalmente 'postgres-data'

Usa usuario 'postgres' (superuser) porque Alembic necesita permisos DDL
amplios (CREATE/ALTER/DROP) y el ownership de tablas puede variar.
"""
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

# Logging desde alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Construir DATABASE_URL desde env vars (no hardcodear password en ini)
password = os.environ.get("POSTGRES_SUPERUSER_PASSWORD")
db_name = os.environ.get("ALEMBIC_DB_NAME")
db_host = os.environ.get("ALEMBIC_DB_HOST", "postgres-data")

if not password:
    raise RuntimeError(
        "POSTGRES_SUPERUSER_PASSWORD no seteado. "
        "Revisar env_file en docker-compose.yml (../postgres-data/.env)."
    )
if not db_name:
    raise RuntimeError(
        "ALEMBIC_DB_NAME no seteado. "
        "Revisar environment en docker-compose.yml."
    )

database_url = f"postgresql+psycopg2://postgres:{password}@{db_host}:5432/{db_name}"
config.set_main_option("sqlalchemy.url", database_url)

# target_metadata: para autogenerate. None = migrations manuales.
# Cuando Fase 2 agregue modelos SQLAlchemy, aqui se importan:
#   from livskin_models import Base
#   target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Genera SQL sin conectar al DB (modo offline, para CI/CD dry-run)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta al DB y aplica migrations."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
