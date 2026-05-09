"""AppointmentService — CRUD + transiciones de estado del modulo Agenda (ADR-0035).

Cierra el agujero del funnel operativo lead -> appointment -> attended -> cliente
con cod_lead_origen heredado automaticamente al marcar asistencia (via ADR-0033).

Endpoints expuestos via routes/api_appointments.py. Cada accion emite audit_log.
"""
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from models.appointment import (
    APPOINTMENT_ACTIVE_STATUSES,
    Appointment,
)
from models.cliente import Cliente
from models.lead import Lead
from services import audit_service, cliente_service
from services.codgen_service import next_codigo


class AppointmentNotFoundError(Exception):
    pass


class LeadNotFoundError(Exception):
    pass


class ClienteNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    """Se intento transicionar el appointment a un estado no permitido desde el actual."""

    pass


class SubjectMissingError(Exception):
    """Ni cod_lead ni cod_cliente fueron proveidos."""

    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_by_cod(db: Session, cod_appointment: str) -> Appointment:
    apt = db.execute(
        select(Appointment).where(Appointment.cod_appointment == cod_appointment)
    ).scalar_one_or_none()
    if apt is None:
        raise AppointmentNotFoundError(f"Appointment {cod_appointment} no existe")
    return apt


def list_with_filters(
    db: Session,
    *,
    status: Optional[str] = None,
    cod_cliente: Optional[str] = None,
    cod_lead: Optional[str] = None,
    scheduled_from: Optional[datetime] = None,
    scheduled_to: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Appointment], int]:
    """Lista appointments paginadas con filtros opcionales.

    Returns:
        (items, total_count) — total para paginacion frontend.
    """
    base_query = select(Appointment)
    count_query = select(func.count(Appointment.id))

    conditions = []
    if status:
        conditions.append(Appointment.status == status)
    if cod_cliente:
        conditions.append(Appointment.cod_cliente == cod_cliente)
    if cod_lead:
        # cod_lead -> resolver a lead.id internamente
        lead = db.execute(
            select(Lead).where(Lead.cod_lead == cod_lead)
        ).scalar_one_or_none()
        if lead is None:
            return [], 0
        conditions.append(Appointment.lead_id == lead.id)
    if scheduled_from:
        conditions.append(Appointment.scheduled_for >= scheduled_from)
    if scheduled_to:
        conditions.append(Appointment.scheduled_for <= scheduled_to)

    if conditions:
        where = and_(*conditions)
        base_query = base_query.where(where)
        count_query = count_query.where(where)

    total = db.execute(count_query).scalar_one()

    base_query = (
        base_query.order_by(Appointment.scheduled_for.asc())
        .limit(limit)
        .offset(offset)
    )
    items = list(db.execute(base_query).scalars().all())
    return items, total


def create(
    db: Session,
    *,
    treatment: str,
    scheduled_for: datetime,
    cod_lead: Optional[str] = None,
    cod_cliente: Optional[str] = None,
    duration_min: int = 60,
    channel: Optional[str] = None,
    notes: Optional[str] = None,
    created_by: Optional[int] = None,
) -> Appointment:
    """Crea una nueva appointment en estado 'scheduled'.

    Una de las dos referencias debe estar presente (cod_lead O cod_cliente).
    El cod_appointment se genera automatico (LIVAPT####).
    Emite audit_log appointment.created.

    Raises:
        SubjectMissingError: si ni cod_lead ni cod_cliente fueron pasados
        LeadNotFoundError: si cod_lead no existe
        ClienteNotFoundError: si cod_cliente no existe
    """
    if not cod_lead and not cod_cliente:
        raise SubjectMissingError("Debe especificarse cod_lead O cod_cliente")

    lead_id: Optional[int] = None
    vtiger_lead_id: Optional[str] = None
    if cod_lead:
        lead = db.execute(
            select(Lead).where(Lead.cod_lead == cod_lead)
        ).scalar_one_or_none()
        if lead is None:
            raise LeadNotFoundError(f"Lead {cod_lead} no existe")
        lead_id = lead.id
        vtiger_lead_id = lead.vtiger_id

    if cod_cliente:
        cliente = db.execute(
            select(Cliente).where(Cliente.cod_cliente == cod_cliente)
        ).scalar_one_or_none()
        if cliente is None:
            raise ClienteNotFoundError(f"Cliente {cod_cliente} no existe")

    cod_appointment = next_codigo(db, Appointment, "cod_appointment", "LIVAPT")

    apt = Appointment(
        cod_appointment=cod_appointment,
        lead_id=lead_id,
        cod_cliente=cod_cliente,
        vtiger_lead_id=vtiger_lead_id,
        treatment=treatment.strip(),
        scheduled_for=scheduled_for,
        duration_min=duration_min,
        status="scheduled",
        channel=channel,
        notes=notes,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(apt)
    db.flush()

    audit_service.log(
        db,
        action="appointment.created",
        entity_type="appointment",
        entity_id=apt.cod_appointment,
        after_state={
            "cod_appointment": apt.cod_appointment,
            "treatment": apt.treatment,
            "scheduled_for": apt.scheduled_for.isoformat(),
            "status": apt.status,
            "lead_id": apt.lead_id,
            "cod_cliente": apt.cod_cliente,
            "channel": apt.channel,
        },
        user_id=created_by,
    )
    return apt


def update(
    db: Session,
    cod_appointment: str,
    *,
    treatment: Optional[str] = None,
    scheduled_for: Optional[datetime] = None,
    duration_min: Optional[int] = None,
    channel: Optional[str] = None,
    notes: Optional[str] = None,
    updated_by: Optional[int] = None,
) -> Appointment:
    """Update PATCH de campos editables. NO toca status.

    Solo permitido en estados activos (scheduled/confirmed). Estados terminales
    son inmutables — para cambiar fecha de uno terminal, usar reschedule.
    """
    apt = get_by_cod(db, cod_appointment)

    if apt.is_terminal:
        raise InvalidTransitionError(
            f"Appointment {cod_appointment} esta en estado terminal "
            f"({apt.status}) — no se puede editar. Use reschedule si necesita."
        )

    before = {
        "treatment": apt.treatment,
        "scheduled_for": apt.scheduled_for.isoformat(),
        "duration_min": apt.duration_min,
        "channel": apt.channel,
        "notes": apt.notes,
    }

    if treatment is not None:
        apt.treatment = treatment.strip()
    if scheduled_for is not None:
        apt.scheduled_for = scheduled_for
    if duration_min is not None:
        apt.duration_min = duration_min
    if channel is not None:
        apt.channel = channel
    if notes is not None:
        apt.notes = notes
    apt.updated_by = updated_by
    db.flush()

    after = {
        "treatment": apt.treatment,
        "scheduled_for": apt.scheduled_for.isoformat(),
        "duration_min": apt.duration_min,
        "channel": apt.channel,
        "notes": apt.notes,
    }

    audit_service.log(
        db,
        action="appointment.updated",
        entity_type="appointment",
        entity_id=apt.cod_appointment,
        before_state=before,
        after_state=after,
        user_id=updated_by,
    )
    return apt


def confirm(
    db: Session,
    cod_appointment: str,
    *,
    updated_by: Optional[int] = None,
) -> Appointment:
    """Transicion: scheduled -> confirmed.

    Marca confirmed_at y emite audit appointment.confirmed.
    """
    apt = get_by_cod(db, cod_appointment)

    if apt.status != "scheduled":
        raise InvalidTransitionError(
            f"Solo citas en 'scheduled' pueden confirmarse "
            f"(actual: {apt.status})"
        )

    before_status = apt.status
    apt.status = "confirmed"
    apt.confirmed_at = _utc_now()
    apt.updated_by = updated_by
    db.flush()

    audit_service.log(
        db,
        action="appointment.confirmed",
        entity_type="appointment",
        entity_id=apt.cod_appointment,
        before_state={"status": before_status},
        after_state={"status": apt.status, "confirmed_at": apt.confirmed_at.isoformat()},
        user_id=updated_by,
    )
    return apt


def mark_attended(
    db: Session,
    cod_appointment: str,
    *,
    updated_by: Optional[int] = None,
) -> Appointment:
    """Transicion critica: scheduled/confirmed -> attended.

    Si el appointment tiene lead_id pero NO cod_cliente, crea automaticamente
    un Cliente desde el Lead heredando cod_lead_origen + attribution UTMs
    (ADR-0033 + ADR-0011 v1.1).

    Emite audit appointment.marked_attended + cliente.created_with_lead_match
    (este ultimo via cliente_service.create cuando aplica).
    """
    apt = get_by_cod(db, cod_appointment)

    if apt.status not in APPOINTMENT_ACTIVE_STATUSES:
        raise InvalidTransitionError(
            f"Solo citas en 'scheduled' o 'confirmed' pueden marcarse attended "
            f"(actual: {apt.status})"
        )

    before_status = apt.status
    cliente_created_cod: Optional[str] = None

    # Si tiene lead pero no cliente, crear cliente con cod_lead_origen heredado
    if apt.lead_id and not apt.cod_cliente:
        lead = db.execute(
            select(Lead).where(Lead.id == apt.lead_id)
        ).scalar_one_or_none()
        if lead is not None:
            try:
                # Reutiliza cliente_service.create que ya maneja lead_origen + attribution
                cliente = cliente_service.create(
                    db,
                    nombre=lead.nombre,
                    phone_raw=lead.phone_e164,
                    email_raw=lead.email_lower,
                    fuente=lead.fuente or "digital",
                    canal_adquisicion=lead.canal_adquisicion or "form_web",
                    tratamiento_interes=apt.treatment,
                    consent_marketing=False,  # default; se actualiza desde lead si aplica
                    cod_lead_origen=lead.cod_lead,
                    created_by=updated_by,
                )
                apt.cod_cliente = cliente.cod_cliente
                cliente_created_cod = cliente.cod_cliente
            except cliente_service.ClienteDuplicadoError:
                # Phone ya existe -> resolver al cliente existente y vincular
                existing = cliente_service.get_by_phone(db, lead.phone_e164)
                if existing is not None:
                    apt.cod_cliente = existing.cod_cliente
                    cliente_created_cod = None  # no se creo, se vinculo

    apt.status = "attended"
    apt.attended_at = _utc_now()
    apt.updated_by = updated_by
    db.flush()

    audit_service.log(
        db,
        action="appointment.marked_attended",
        entity_type="appointment",
        entity_id=apt.cod_appointment,
        before_state={"status": before_status, "cod_cliente": None if cliente_created_cod else apt.cod_cliente},
        after_state={
            "status": apt.status,
            "attended_at": apt.attended_at.isoformat(),
            "cod_cliente": apt.cod_cliente,
            "cliente_created": cliente_created_cod is not None,
        },
        user_id=updated_by,
    )
    return apt


def mark_no_show(
    db: Session,
    cod_appointment: str,
    *,
    updated_by: Optional[int] = None,
) -> Appointment:
    """Transicion: scheduled/confirmed -> no_show."""
    apt = get_by_cod(db, cod_appointment)

    if apt.status not in APPOINTMENT_ACTIVE_STATUSES:
        raise InvalidTransitionError(
            f"Solo citas en 'scheduled' o 'confirmed' pueden marcarse no_show "
            f"(actual: {apt.status})"
        )

    before_status = apt.status
    apt.status = "no_show"
    apt.no_show_at = _utc_now()
    apt.updated_by = updated_by
    db.flush()

    audit_service.log(
        db,
        action="appointment.marked_no_show",
        entity_type="appointment",
        entity_id=apt.cod_appointment,
        before_state={"status": before_status},
        after_state={"status": apt.status, "no_show_at": apt.no_show_at.isoformat()},
        user_id=updated_by,
    )
    return apt


def cancel(
    db: Session,
    cod_appointment: str,
    *,
    updated_by: Optional[int] = None,
) -> Appointment:
    """Transicion: scheduled/confirmed -> cancelled."""
    apt = get_by_cod(db, cod_appointment)

    if apt.status not in APPOINTMENT_ACTIVE_STATUSES:
        raise InvalidTransitionError(
            f"Solo citas en 'scheduled' o 'confirmed' pueden cancelarse "
            f"(actual: {apt.status})"
        )

    before_status = apt.status
    apt.status = "cancelled"
    apt.cancelled_at = _utc_now()
    apt.updated_by = updated_by
    db.flush()

    audit_service.log(
        db,
        action="appointment.cancelled",
        entity_type="appointment",
        entity_id=apt.cod_appointment,
        before_state={"status": before_status},
        after_state={"status": apt.status, "cancelled_at": apt.cancelled_at.isoformat()},
        user_id=updated_by,
    )
    return apt


def reschedule(
    db: Session,
    cod_appointment: str,
    *,
    new_scheduled_for: datetime,
    new_duration_min: int = 60,
    notes_addendum: Optional[str] = None,
    updated_by: Optional[int] = None,
) -> tuple[Appointment, Appointment]:
    """Reagendar: crea NUEVA appointment y marca la original como rescheduled.

    Returns:
        (original_appointment_marked_rescheduled, new_appointment_scheduled)
    """
    original = get_by_cod(db, cod_appointment)

    if original.status not in APPOINTMENT_ACTIVE_STATUSES:
        raise InvalidTransitionError(
            f"Solo citas en 'scheduled' o 'confirmed' pueden reagendarse "
            f"(actual: {original.status})"
        )

    # Crear la nueva appointment con mismos datos pero nueva fecha
    new_cod = next_codigo(db, Appointment, "cod_appointment", "LIVAPT")
    new_notes = original.notes or ""
    if notes_addendum:
        new_notes = (new_notes + "\n--- " + notes_addendum).strip()

    new_apt = Appointment(
        cod_appointment=new_cod,
        lead_id=original.lead_id,
        cod_cliente=original.cod_cliente,
        vtiger_lead_id=original.vtiger_lead_id,
        treatment=original.treatment,
        scheduled_for=new_scheduled_for,
        duration_min=new_duration_min,
        status="scheduled",
        channel=original.channel,
        notes=new_notes or None,
        created_by=updated_by,
        updated_by=updated_by,
    )
    db.add(new_apt)
    db.flush()

    # Marcar original como rescheduled apuntando a la nueva
    before_status = original.status
    original.status = "rescheduled"
    original.rescheduled_to = new_apt.id
    original.updated_by = updated_by
    db.flush()

    audit_service.log(
        db,
        action="appointment.rescheduled",
        entity_type="appointment",
        entity_id=original.cod_appointment,
        before_state={
            "status": before_status,
            "scheduled_for": original.scheduled_for.isoformat(),
        },
        after_state={
            "status": original.status,
            "rescheduled_to": new_apt.cod_appointment,
            "new_scheduled_for": new_apt.scheduled_for.isoformat(),
        },
        user_id=updated_by,
    )
    return original, new_apt
