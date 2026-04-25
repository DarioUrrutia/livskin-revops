"""Cliente — master de identidad de humanos que compraron (ADR-0011 v1.1, ADR-0015).

SoT: ERP Postgres (NO Vtiger). Incluye todos los humanos: walk-ins, referidos,
digitales, y los 135 históricos word-of-mouth.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class Cliente(Base, TimestampMixin):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cod_cliente: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    phone_e164: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_lower: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_hash_sha256: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_registro: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    fuente: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="organico")
    canal_adquisicion: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="legacy")
    utm_source_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_medium_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_campaign_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_content_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    utm_term_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fbclid_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gclid_at_capture: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tratamiento_interes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    consent_marketing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cod_lead_origen: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    vtiger_lead_id_origen: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    merged_to: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("clientes.id"), nullable=True
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    __table_args__ = (
        Index("idx_clientes_phone_e164", "phone_e164"),
        Index("idx_clientes_email_lower", "email_lower"),
        Index("idx_clientes_nombre_lower", "nombre"),
    )
