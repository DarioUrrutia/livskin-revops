"""0002 trigger debe dinamico en ventas

Revision ID: 0002_debe_dinamico
Revises: 0f0dad927b76
Create Date: 2026-04-25 22:00:00.000000+00:00

Trigger AFTER INSERT/UPDATE/DELETE en pagos: recalcula ventas.pagado y
ventas.debe en función de la suma de pagos linkeados al mismo cod_item.
Incluye TODOS los tipos de pago (incluyendo credito_aplicado) en la suma
porque cada uno reduce el DEBE del item al que se aplica.
"""
from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0002_debe_dinamico"
down_revision: Union[str, None] = "0f0dad927b76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION recompute_venta_debe(target_cod_item TEXT)
        RETURNS VOID AS $$
        DECLARE
            sum_pagos NUMERIC(10,2);
        BEGIN
            IF target_cod_item IS NULL OR target_cod_item = '' THEN
                RETURN;
            END IF;

            SELECT COALESCE(SUM(monto), 0) INTO sum_pagos
            FROM pagos
            WHERE cod_item = target_cod_item;

            UPDATE ventas
            SET pagado = LEAST(total, sum_pagos),
                debe = GREATEST(0, total - sum_pagos),
                updated_at = NOW()
            WHERE cod_item = target_cod_item;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION trigger_recompute_venta_debe()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                PERFORM recompute_venta_debe(OLD.cod_item);
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                IF NEW.cod_item IS DISTINCT FROM OLD.cod_item THEN
                    PERFORM recompute_venta_debe(OLD.cod_item);
                END IF;
                PERFORM recompute_venta_debe(NEW.cod_item);
                RETURN NEW;
            ELSE
                PERFORM recompute_venta_debe(NEW.cod_item);
                RETURN NEW;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS pagos_recompute_venta_debe ON pagos;
        CREATE TRIGGER pagos_recompute_venta_debe
        AFTER INSERT OR UPDATE OR DELETE ON pagos
        FOR EACH ROW
        EXECUTE FUNCTION trigger_recompute_venta_debe();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS pagos_recompute_venta_debe ON pagos;")
    op.execute("DROP FUNCTION IF EXISTS trigger_recompute_venta_debe();")
    op.execute("DROP FUNCTION IF EXISTS recompute_venta_debe(TEXT);")
