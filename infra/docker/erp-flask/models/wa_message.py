"""WaMessage — historial inmutable de mensajes WhatsApp inbound/outbound.

Tabla creada en migration 0008. Persiste cada body individual para análisis
post-campaña, debugging conversaciones, y compliance (audit trail Meta).

`meta_message_id UNIQUE` garantiza idempotency contra re-entregas Meta
(Meta reenvía si webhook tarda >5s o falla).

Consumida por workflow n8n d1-wa-yossie-v2 via /api/internal/wa-state
(endpoint extendido con payloads inbound_message / outbound_message).
"""
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import BigInteger, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class WaMessage(Base):
    __tablename__ = "wa_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("wa_conversation_state.id"), nullable=False
    )
    meta_message_id: Mapped[Optional[str]] = mapped_column(String)
    phone_lead: Mapped[str] = mapped_column(String, nullable=False)
    direction: Mapped[str] = mapped_column(String, nullable=False)  # inbound | outbound
    message_type: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    template_name: Mapped[Optional[str]] = mapped_column(String)
    template_params: Mapped[Optional[Any]] = mapped_column(JSONB)
    meta_status: Mapped[Optional[str]] = mapped_column(String)
    meta_status_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    meta_error_code: Mapped[Optional[str]] = mapped_column(String)
    meta_error_message: Mapped[Optional[str]] = mapped_column(Text)
    intent: Mapped[Optional[str]] = mapped_column(String)
    parsed_dates: Mapped[Optional[Any]] = mapped_column(JSONB)
    meta_payload_raw: Mapped[Optional[Any]] = mapped_column(JSONB)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
