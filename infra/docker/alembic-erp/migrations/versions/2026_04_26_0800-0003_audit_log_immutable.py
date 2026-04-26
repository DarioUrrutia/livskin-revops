"""0003 audit_log inmutable: trigger anti UPDATE/DELETE (ADR-0027)

Revision ID: 0003_audit_immutable
Revises: 0002_debe_dinamico
Create Date: 2026-04-26 08:00:00.000000+00:00

Trigger BEFORE UPDATE/DELETE en audit_log que lanza excepción. Garantiza que
ningún path —incluso superuser— pueda modificar registros una vez escritos.

Permisos restrictivos a nivel DB se aplican post-cutover (Fase 6) cuando
exista rol erp_user separado del superuser. Hoy todo corre como postgres
superuser y el trigger es la única barrera real.
"""
from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0003_audit_immutable"
down_revision: Union[str, None] = "0002_debe_dinamico"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION audit_log_immutable()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log es inmutable — UPDATE/DELETE no permitidos';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS prevent_audit_modification ON audit_log;
        CREATE TRIGGER prevent_audit_modification
            BEFORE UPDATE OR DELETE ON audit_log
            FOR EACH ROW
            EXECUTE FUNCTION audit_log_immutable();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS prevent_audit_modification ON audit_log;")
    op.execute("DROP FUNCTION IF EXISTS audit_log_immutable();")
