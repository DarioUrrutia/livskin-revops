"""0009 is_test BOOLEAN flag para distinguir data de pruebas de data productiva

Revision ID: 0009_is_test_flag
Revises: 0008_wa_conversation
Create Date: 2026-05-24 13:00:00.000000+00:00

Motivacion (incoherencia #4 audit 2026-05-24):
Hasta hoy, smoke tests creaban filas reales en `leads`, `clientes`, `ventas`,
`pagos` sin manera programatica de filtrarlas. Esto contamino dashboards
Metabase con ventas falsas (LIVTRAT0071+72 = S/1400 fake) y obligo a cleanup
manual cross-system (ERP + Vtiger + Analytics).

Patron defensivo:
  - Columna `is_test BOOLEAN NOT NULL DEFAULT FALSE` en 5 tablas operacionales.
  - Todas las cards Metabase deben filtrar `WHERE is_test = false`.
  - Smoke tests setean `is_test=true` al insertar.
  - Workflow n8n A1 (form->Vtiger Lead) detecta tel/email con sufijo `+TEST`
    o flag `?test=1` y propaga `is_test=true` cuando aplica.

Esto NO bloquea cleanups manuales (se sigue pudiendo DELETE), pero permite
filtrar sin borrar — utiles para QA/regresion sin perder histórico.
"""
from alembic import op
import sqlalchemy as sa


revision = "0009_is_test_flag"
down_revision = "0008_wa_conversation"
branch_labels = None
depends_on = None


TABLES = ["leads", "clientes", "ventas", "pagos", "appointments"]


def upgrade() -> None:
    for tbl in TABLES:
        op.add_column(
            tbl,
            sa.Column(
                "is_test",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
        op.create_index(
            f"ix_{tbl}_is_test",
            tbl,
            ["is_test"],
            postgresql_where=sa.text("is_test = true"),
        )


def downgrade() -> None:
    for tbl in TABLES:
        op.drop_index(f"ix_{tbl}_is_test", table_name=tbl)
        op.drop_column(tbl, "is_test")
