"""LeadTouchpoint — cada captura de un lead via form o WA (ADR-0011 v1.1, ADR-0013 v2).

Multi-touch tracking: un lead puede tener N touchpoints en el tiempo.
Permite first-touch vs last-touch attribution + reconstrucción del journey.
"""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models.base import Base


class LeadTouchpoint(Base):
    __tablename__ = "lead_touchpoints"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lead_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("leads.id"), nullable=False)
    canal: Mapped[str] = mapped_column(String, nullable=False)

    landing_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_contacto: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

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

    primer_mensaje: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    form_data_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "canal IN ('form_web', 'whatsapp_cloud_api')",
            name="ck_lead_touchpoints_canal_valido",
        ),
        Index("idx_lead_touchpoints_lead_fecha", "lead_id", "fecha_contacto"),
        Index("idx_lead_touchpoints_fecha", "fecha_contacto"),
        Index("idx_lead_touchpoints_utm_campaign", "utm_campaign"),
        Index("idx_lead_touchpoints_event_id", "event_id"),
    )
