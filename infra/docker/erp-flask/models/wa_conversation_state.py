"""WaConversationState — state machine del bot WhatsApp Yossie.

SoT: ERP Postgres. Una row por phone_lead activo (UNIQUE PARTIAL WHERE state != 'closed').
Consumida por workflow n8n d1-wa-handoff-v2 via /api/internal/wa-state.

Estados validos (definidos en migration 0008):
    new            cliente acaba de escribir 1ra vez
    qualifying_q1  bot mando saludo + pregunta tratamiento
    qualifying_q2  bot mando pregunta primera-vez vs experiencia
    qualifying_q3  bot mando pregunta urgencia
    escalated      bot paso conversacion a humano (Dario o doctora)
    closed         conversacion cerrada (asistencia / inactiva / cancelada)
"""
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class WaConversationState(Base):
    __tablename__ = "wa_conversation_state"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    phone_lead: Mapped[str] = mapped_column(String, nullable=False)
    phone_doctora: Mapped[Optional[str]] = mapped_column(String)
    state: Mapped[str] = mapped_column(String, nullable=False, default="new")
    last_intent: Mapped[Optional[str]] = mapped_column(String)
    proposed_dates: Mapped[Optional[Any]] = mapped_column(JSONB)
    doctora_response: Mapped[Optional[Any]] = mapped_column(JSONB)
    context_json: Mapped[Optional[Any]] = mapped_column(JSONB)
    last_inbound_text: Mapped[Optional[str]] = mapped_column(Text)
    last_inbound_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_outbound_text: Mapped[Optional[str]] = mapped_column(Text)
    last_outbound_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    message_count_inbound: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message_count_outbound: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cod_appointment: Mapped[Optional[str]] = mapped_column(String)
    appointment_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    lead_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    vtiger_lead_id: Mapped[Optional[str]] = mapped_column(String)
    escalated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    escalation_reason: Mapped[Optional[str]] = mapped_column(String)
    escalation_to: Mapped[Optional[str]] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
