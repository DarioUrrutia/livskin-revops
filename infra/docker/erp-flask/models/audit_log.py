"""AuditLog — registro inmutable de TODO movimiento del sistema (ADR-0027).

Tabla append-only. Permisos DB + trigger defensivo aseguran inmutabilidad.
~30 tipos de eventos canónicos cubriendo auth, ventas, pagos, gastos,
clientes, leads, admin, webhooks.
"""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    user_username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_role: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    action: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    before_state: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("user_sessions.id"), nullable=True
    )
    request_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    result: Mapped[str] = mapped_column(String, nullable=False, default="success")
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    audit_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    __table_args__ = (
        Index("idx_audit_occurred", "occurred_at"),
        Index("idx_audit_user_occurred", "user_id", "occurred_at"),
        Index("idx_audit_action_occurred", "action", "occurred_at"),
        Index("idx_audit_entity", "entity_type", "entity_id", "occurred_at"),
        Index("idx_audit_category_occurred", "category", "occurred_at"),
    )
