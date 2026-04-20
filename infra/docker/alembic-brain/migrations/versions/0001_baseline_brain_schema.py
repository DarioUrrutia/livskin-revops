"""Baseline — schema livskin_brain creado por init scripts de Postgres.

Revision ID: 0001
Revises:
Create Date: 2026-04-20

Este es un 'baseline migration'. El schema real (pgvector, pgcrypto, las
6 tablas de las capas del segundo cerebro, los indices HNSW) fue creado
por los init scripts de Postgres que corren al levantar el container la
primera vez:

  infra/docker/postgres-data/init/03-brain-schema.sh

Esta migration NO crea nada. Solo sirve como marker para que Alembic
sepa "el DB ya esta en este estado, no intentar aplicar nada".

Para marcar como aplicado sin correr upgrade:
  docker compose run --rm alembic-brain stamp head

Migrations futuras (0002, 0003, ...) se crean con:
  docker compose run --rm alembic-brain revision -m "descripcion corta"

Y se aplican con:
  docker compose run --rm alembic-brain upgrade head
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: el schema ya existe por init scripts de Postgres.

    Si en el futuro alguien necesita recrear el brain desde cero sin
    correr init scripts, habra que mover la logica de 03-brain-schema.sh
    aqui. Por ahora los init scripts son la fuente de verdad del baseline.
    """
    pass


def downgrade() -> None:
    """No-op: para rollback total del schema brain, usar:
      docker compose -f ../postgres-data/docker-compose.yml down -v
    (destruye el volumen y obliga re-init completo).
    """
    pass
