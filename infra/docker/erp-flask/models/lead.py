"""Lead — prospecto digital pre-primera-venta (ADR-0011 v1.1, ADR-0012, ADR-0013 v2).

SoT principal: Vtiger (lifecycle del lead). Esta tabla es replica en Postgres
para lookups rápidos de dedup cross-system y joins analíticos.
"""
from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cod_lead: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    vtiger_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    nombre: Mapped[str] = mapped_column(String, nullable=False)
    phone_e164: Mapped[str] = mapped_column(String, nullable=False)
    email_lower: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_hash_sha256: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    fuente: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    canal_adquisicion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_source_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_medium_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_campaign_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_content_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_term_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fbclid_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gclid_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tratamiento_interes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    consent_marketing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    estado_lead: Mapped[str] = mapped_column(String, nullable=False, default="nuevo")
    fecha_captura: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scoring_signals_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    intent_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    nurture_state: Mapped[str] = mapped_column(String, nullable=False, default="inactivo")
    nurture_stream: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    handoff_to_doctora_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    handoff_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    handoff_notified_via: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    es_reactivacion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cod_cliente_vinculado: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("clientes.cod_cliente"), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "estado_lead IN ('nuevo', 'contactado', 'agendado', 'asistio', 'cliente', 'perdido')",
            name="ck_leads_estado_valido",
        ),
        CheckConstraint("score >= 0 AND score <= 100", name="ck_leads_score_rango"),
        Index("idx_leads_phone_e164", "phone_e164"),
        Index("idx_leads_email_lower", "email_lower"),
        Index("idx_leads_estado_score", "estado_lead", "score"),
        Index("idx_leads_vtiger_id", "vtiger_id"),
    )
