"""Appointment — modulo agenda minima ERP (ADR-0035, Fase 4A).

SoT: ERP Postgres. La doctora opera el modulo desde la pestana AGENDA del ERP.
Cierra el agujero del funnel operativo: lead -> appointment -> attended -> cliente
con cod_lead_origen heredado automaticamente al marcar asistencia (ADR-0033).

Una appointment puede tener:
- lead_id (cita agendada para un lead Vtiger ya capturado), O
- cod_cliente (walk-in directo o cita de cliente existente que vuelve)
- al menos una de las dos requerida (CHECK constraint a nivel DB)

Estados validos (enum aplicacion-level + CHECK constraint DB):
    scheduled    - cita creada, sin confirmar
    confirmed    - lead/cliente confirmo la cita
    attended     - vino a la cita -> trigger creacion cliente automatica
    no_show      - no vino el dia acordado
    cancelled    - cancelada antes del dia
    rescheduled  - reagendada (rescheduled_to apunta a la nueva)

Reglas de transicion:
    scheduled  -> confirmed | cancelled | rescheduled
    confirmed  -> attended | no_show | cancelled | rescheduled
    attended | no_show | cancelled | rescheduled -> (terminal, no mas transiciones)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


# Estados validos del appointment (enum aplicacion-level)
APPOINTMENT_STATUS_VALUES = (
    "scheduled",
    "confirmed",
    "attended",
    "no_show",
    "cancelled",
    "rescheduled",
)

# Estados que permiten transicion a attended/no_show (citas activas)
APPOINTMENT_ACTIVE_STATUSES = ("scheduled", "confirmed")

# Estados terminales (no mas transiciones permitidas)
APPOINTMENT_TERMINAL_STATUSES = ("attended", "no_show", "cancelled", "rescheduled")

# Canales validos donde se acordo la cita
APPOINTMENT_CHANNEL_VALUES = ("whatsapp", "phone", "walk_in", "form_web", "instagram", "other")


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "lead_id IS NOT NULL OR cod_cliente IS NOT NULL",
            name="ck_appointments_has_subject",
        ),
        CheckConstraint(
            "status IN ('scheduled', 'confirmed', 'attended', 'no_show', 'cancelled', 'rescheduled')",
            name="ck_appointments_status_valido",
        ),
    )

    # PK + codigo
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cod_appointment: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Referencias (al menos una requerida)
    lead_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("leads.id"), nullable=True
    )
    cod_cliente: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("clientes.cod_cliente"), nullable=True
    )
    vtiger_lead_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Datos de la cita
    treatment: Mapped[str] = mapped_column(String, nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    status: Mapped[str] = mapped_column(String, nullable=False, default="scheduled")
    channel: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Lifecycle timestamps
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    no_show_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rescheduled_to: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("appointments.id"), nullable=True
    )

    # Auditoria estandar
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<Appointment(cod={self.cod_appointment}, "
            f"status={self.status}, scheduled_for={self.scheduled_for}, "
            f"treatment={self.treatment})>"
        )

    @property
    def is_active(self) -> bool:
        """True si la cita esta en estado activo (puede transicionar a attended)."""
        return self.status in APPOINTMENT_ACTIVE_STATUSES

    @property
    def is_terminal(self) -> bool:
        """True si la cita esta en estado terminal (no mas transiciones)."""
        return self.status in APPOINTMENT_TERMINAL_STATUSES
