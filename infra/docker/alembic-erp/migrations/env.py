"""Alembic environment — livskin_erp.

Mismo patron que alembic-brain — env.py es identico; la diferencia
esta en ALEMBIC_DB_NAME (seteado en docker-compose.yml).
"""
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

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
        "ALEMBIC_DB_NAME no seteado. Revisar environment en docker-compose.yml."
    )

database_url = f"postgresql+psycopg2://postgres:{password}@{db_host}:5432/{db_name}"
config.set_main_option("sqlalchemy.url", database_url)

# Modelos del ERP refactorizado (Fase 2). Montados via volume read-only
# desde erp-flask/models/ (ver docker-compose.yml).
from models import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
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
