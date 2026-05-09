"""Schemas Pydantic para /api/appointments (ADR-0035, Fase 4A)."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Status validos (espejo del enum aplicacion-level del modelo)
AppointmentStatus = Literal[
    "scheduled",
    "confirmed",
    "attended",
    "no_show",
    "cancelled",
    "rescheduled",
]

AppointmentChannel = Literal[
    "whatsapp",
    "phone",
    "walk_in",
    "form_web",
    "instagram",
    "other",
]


class AppointmentCreate(BaseModel):
    """Payload para POST /api/appointments — crear cita nueva."""

    # Una de las dos referencias requeridas (validado en model_validator)
    cod_lead: Optional[str] = Field(
        default=None,
        max_length=30,
        description="cod_lead del Lead origen (LIVLEAD####). Excluyente con cod_cliente.",
    )
    cod_cliente: Optional[str] = Field(
        default=None,
        max_length=30,
        description="cod_cliente del Cliente existente (LIVCLIENT####). Walk-in o cliente recurrente.",
    )

    # Datos de la cita
    treatment: str = Field(..., min_length=1, max_length=200)
    scheduled_for: datetime = Field(..., description="Fecha + hora de la cita (timezone-aware)")
    duration_min: int = Field(default=60, ge=15, le=480, description="Duracion en minutos (15-480)")
    channel: Optional[AppointmentChannel] = Field(
        default=None, description="Canal donde se acordo la cita"
    )
    notes: Optional[str] = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def at_least_one_subject(self) -> "AppointmentCreate":
        if not self.cod_lead and not self.cod_cliente:
            raise ValueError(
                "Debe especificarse cod_lead O cod_cliente (al menos uno)"
            )
        return self


class AppointmentUpdate(BaseModel):
    """Payload para PATCH /api/appointments/<cod> — solo campos editables.

    NO se actualiza status via PATCH (eso requiere los endpoints especificos
    /confirm, /mark-attended, etc. para mantener auditoria estricta).
    """

    treatment: Optional[str] = Field(default=None, min_length=1, max_length=200)
    scheduled_for: Optional[datetime] = None
    duration_min: Optional[int] = Field(default=None, ge=15, le=480)
    channel: Optional[AppointmentChannel] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class AppointmentRescheduleRequest(BaseModel):
    """Payload para POST /api/appointments/<cod>/reschedule.

    Crea una appointment NUEVA con la nueva fecha/hora y marca la original
    como `rescheduled` con FK rescheduled_to apuntando a la nueva.
    """

    new_scheduled_for: datetime = Field(..., description="Nueva fecha + hora")
    new_duration_min: int = Field(default=60, ge=15, le=480)
    notes_addendum: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Notas adicionales sobre el motivo del reagendamiento",
    )


class AppointmentRead(BaseModel):
    """Shape completo para GET /api/appointments/<cod> y POST responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cod_appointment: str
    lead_id: Optional[int]
    cod_cliente: Optional[str]
    vtiger_lead_id: Optional[str]

    treatment: str
    scheduled_for: datetime
    duration_min: int
    status: AppointmentStatus
    channel: Optional[AppointmentChannel]
    notes: Optional[str]

    confirmed_at: Optional[datetime]
    attended_at: Optional[datetime]
    no_show_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    rescheduled_to: Optional[int]

    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime


class AppointmentListItem(BaseModel):
    """Shape compacto para GET /api/appointments listado."""

    model_config = ConfigDict(from_attributes=True)

    cod_appointment: str
    cod_cliente: Optional[str]
    lead_id: Optional[int]
    treatment: str
    scheduled_for: datetime
    duration_min: int
    status: AppointmentStatus
    channel: Optional[AppointmentChannel]


class AppointmentListResponse(BaseModel):
    """Respuesta paginada para GET /api/appointments."""

    items: list[AppointmentListItem]
    total: int
    limit: int
    offset: int
