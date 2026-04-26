"""InfraSnapshot — snapshot del estado de cada VPS (Bloque 0.4).

Tabla append-only poblada por el cron recolector cross-VPS. Retención 30 días
(autolimpieza diaria). Lectura via /admin/system-health.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models.base import Base


class InfraSnapshot(Base):
    __tablename__ = "infra_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    vps_alias: Mapped[str] = mapped_column(String(64), nullable=False)
    vps_role: Mapped[str] = mapped_column(String(32), nullable=False)

    uptime_seconds: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    disk_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    disk_used_gb: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    disk_total_gb: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    ram_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    ram_used_mb: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    ram_total_mb: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    containers_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_deploy_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    raw_payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_infra_snapshots_vps_captured", "vps_alias", "captured_at"),
    )
