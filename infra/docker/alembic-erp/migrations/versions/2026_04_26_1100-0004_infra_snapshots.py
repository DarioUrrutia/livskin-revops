"""0004 infra_snapshots: tabla de snapshots cross-VPS (Bloque 0.4)

Revision ID: 0004_infra_snapshots
Revises: 0003_audit_immutable
Create Date: 2026-04-26 11:00:00.000000+00:00

Tabla append-only que guarda el resultado de pollear los sensors de los 3 VPS.
Cron en VPS 3 (cada 5 min) hace curl /api/system-state a livskin-wp,
livskin-ops y al endpoint local de erp-flask, y persiste el snapshot acá.

Retención: 30 días (autolimpieza diaria).
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_infra_snapshots"
down_revision: Union[str, None] = "0003_audit_immutable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "infra_snapshots",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("vps_alias", sa.String(64), nullable=False),
        sa.Column("vps_role", sa.String(32), nullable=False),
        sa.Column("uptime_seconds", sa.BigInteger, nullable=True),
        sa.Column("disk_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("disk_used_gb", sa.Numeric(10, 2), nullable=True),
        sa.Column("disk_total_gb", sa.Numeric(10, 2), nullable=True),
        sa.Column("ram_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("ram_used_mb", sa.BigInteger, nullable=True),
        sa.Column("ram_total_mb", sa.BigInteger, nullable=True),
        sa.Column("containers_count", sa.Integer, nullable=True),
        sa.Column("last_deploy_sha", sa.String(40), nullable=True),
        # Raw response del sensor (todos los campos del JSON)
        sa.Column("raw_payload", sa.dialects.postgresql.JSONB, nullable=True),
        # Si el sensor no respondió o respondió con error
        sa.Column("error", sa.Text, nullable=True),
    )
    op.create_index(
        "idx_infra_snapshots_vps_captured",
        "infra_snapshots",
        ["vps_alias", "captured_at"],
    )
    op.create_index(
        "idx_infra_snapshots_captured",
        "infra_snapshots",
        [sa.text("captured_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("idx_infra_snapshots_captured", table_name="infra_snapshots")
    op.drop_index("idx_infra_snapshots_vps_captured", table_name="infra_snapshots")
    op.drop_table("infra_snapshots")
