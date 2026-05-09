"""0007 appointments — modulo agenda minima ERP

Revision ID: 0007_appointments
Revises: 0006_capi_match_quality
Create Date: 2026-05-09 12:00:00.000000+00:00

Crea tabla `appointments` con schema completo del ADR-0035.

Cierra el agujero del funnel operativo entre lead capturado y venta registrada:
lead -> appointment -> attended -> cliente (con cod_lead_origen heredado).

La tabla soporta:
- Lead origen (lead_id) O walk-in directo (cod_cliente sin lead_id)
- Constraint: al menos uno de los dos requerido
- 6 estados (scheduled, confirmed, attended, no_show, cancelled, rescheduled)
- Lifecycle timestamps por transicion (confirmed_at, attended_at, no_show_at, etc.)
- Reagendamiento via FK auto-referencial rescheduled_to
- 5 indices para queries comunes (proximas citas, por status, por lead/cliente)

Migration 100% reversible: la tabla es nueva, el downgrade hace DROP simple.
No toca data existente de clientes/leads/ventas/pagos.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_appointments"
down_revision: Union[str, None] = "0006_capi_match_quality"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        # PK + codigo
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("cod_appointment", sa.String(), nullable=False),

        # Referencias (al menos una requerida via CHECK constraint)
        sa.Column("lead_id", sa.BigInteger(), nullable=True),
        sa.Column("cod_cliente", sa.String(), nullable=True),
        sa.Column("vtiger_lead_id", sa.String(), nullable=True),

        # Datos de la cita
        sa.Column("treatment", sa.String(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("status", sa.String(), nullable=False, server_default="scheduled"),
        sa.Column("channel", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),

        # Lifecycle timestamps
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("no_show_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rescheduled_to", sa.BigInteger(), nullable=True),

        # Auditoria estandar
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cod_appointment", name="uq_appointments_cod_appointment"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], name="fk_appointments_lead_id"),
        sa.ForeignKeyConstraint(["cod_cliente"], ["clientes.cod_cliente"], name="fk_appointments_cod_cliente"),
        sa.ForeignKeyConstraint(["rescheduled_to"], ["appointments.id"], name="fk_appointments_rescheduled_to"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_appointments_created_by"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], name="fk_appointments_updated_by"),
        sa.CheckConstraint(
            "lead_id IS NOT NULL OR cod_cliente IS NOT NULL",
            name="ck_appointments_has_subject",
        ),
        sa.CheckConstraint(
            "status IN ('scheduled', 'confirmed', 'attended', 'no_show', 'cancelled', 'rescheduled')",
            name="ck_appointments_status_valido",
        ),
    )

    # Indices para queries comunes
    op.create_index("idx_appointments_scheduled_for", "appointments", ["scheduled_for"])
    op.create_index("idx_appointments_status", "appointments", ["status"])
    op.create_index(
        "idx_appointments_lead_id",
        "appointments",
        ["lead_id"],
        postgresql_where=sa.text("lead_id IS NOT NULL"),
    )
    op.create_index(
        "idx_appointments_cod_cliente",
        "appointments",
        ["cod_cliente"],
        postgresql_where=sa.text("cod_cliente IS NOT NULL"),
    )
    op.create_index(
        "idx_appointments_status_scheduled",
        "appointments",
        ["status", "scheduled_for"],
    )


def downgrade() -> None:
    op.drop_index("idx_appointments_status_scheduled", table_name="appointments")
    op.drop_index("idx_appointments_cod_cliente", table_name="appointments")
    op.drop_index("idx_appointments_lead_id", table_name="appointments")
    op.drop_index("idx_appointments_status", table_name="appointments")
    op.drop_index("idx_appointments_scheduled_for", table_name="appointments")
    op.drop_table("appointments")
