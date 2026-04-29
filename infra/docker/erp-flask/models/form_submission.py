"""FormSubmission — raw audit trail de submits del form (ADR-0011 v1.1).

Almacena cada form submit ANTES de procesarlo. Permite reprocesar si falla
el flujo lead+touchpoint o auditar sin tocar leads/touchpoints.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models.base import Base


class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    landing_slug: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    landing_url_completa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    phone_raw: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_e164: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_raw: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    nombre_raw: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tratamiento_interes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    utm_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_content: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_term: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fbclid: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gclid: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fbc: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ga: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    event_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    consent_marketing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="received")
    lead_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("leads.id"), nullable=True)
    lead_touchpoint_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("lead_touchpoints.id"), nullable=True
    )
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_form_submissions_fecha_status", "fecha", "status"),
        Index("idx_form_submissions_event_id", "event_id"),
    )
