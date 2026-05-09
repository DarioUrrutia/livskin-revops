"""Tests de appointment_service (CRUD + transiciones de estado, ADR-0035)."""
from datetime import datetime, timedelta, timezone

import pytest

from models.appointment import Appointment
from models.audit_log import AuditLog
from models.cliente import Cliente
from models.lead import Lead
from services import appointment_service, cliente_service


def _future_dt(hours: int = 24) -> datetime:
    """Helper: datetime futuro N horas adelante (timezone-aware)."""
    return datetime.now(timezone.utc) + timedelta(hours=hours)


@pytest.fixture
def lead(db_session):
    """Lead minimo para tests."""
    from services import lead_sync_service

    lead = Lead(
        cod_lead="LIVLEAD0001",
        vtiger_id="V-1001",
        nombre="Maria Test",
        phone_e164="+51987654321",
        fuente="digital",
        canal_adquisicion="form_web",
        utm_source_at_capture="facebook",
        utm_medium_at_capture="cpc",
        utm_campaign_at_capture="dia-madre-test",
        fbclid_at_capture="fb.1.test",
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.fixture
def cliente(db_session):
    """Cliente walk-in minimo para tests."""
    c = cliente_service.create(
        db_session, nombre="Cliente Existente", phone_raw="987111222"
    )
    db_session.commit()
    return c


# ============================================================
# CREATE
# ============================================================
class TestCreate:
    def test_create_with_lead(self, db_session, lead):
        apt = appointment_service.create(
            db_session,
            treatment="Botox",
            scheduled_for=_future_dt(48),
            cod_lead=lead.cod_lead,
        )
        assert apt.cod_appointment.startswith("LIVAPT")
        assert apt.lead_id == lead.id
        assert apt.cod_cliente is None
        assert apt.vtiger_lead_id == "V-1001"
        assert apt.status == "scheduled"
        assert apt.duration_min == 60

    def test_create_with_cliente_walk_in(self, db_session, cliente):
        apt = appointment_service.create(
            db_session,
            treatment="Limpieza",
            scheduled_for=_future_dt(24),
            cod_cliente=cliente.cod_cliente,
        )
        assert apt.cod_cliente == cliente.cod_cliente
        assert apt.lead_id is None
        assert apt.status == "scheduled"

    def test_create_without_subject_raises(self, db_session):
        with pytest.raises(appointment_service.SubjectMissingError):
            appointment_service.create(
                db_session,
                treatment="Botox",
                scheduled_for=_future_dt(24),
            )

    def test_create_with_unknown_lead_raises(self, db_session):
        with pytest.raises(appointment_service.LeadNotFoundError):
            appointment_service.create(
                db_session,
                treatment="Botox",
                scheduled_for=_future_dt(24),
                cod_lead="LIVLEAD9999",
            )

    def test_create_with_unknown_cliente_raises(self, db_session):
        with pytest.raises(appointment_service.ClienteNotFoundError):
            appointment_service.create(
                db_session,
                treatment="Botox",
                scheduled_for=_future_dt(24),
                cod_cliente="LIVCLIENT9999",
            )

    def test_codes_are_unique_sequential(self, db_session, lead, cliente):
        apt1 = appointment_service.create(
            db_session,
            treatment="A",
            scheduled_for=_future_dt(24),
            cod_lead=lead.cod_lead,
        )
        apt2 = appointment_service.create(
            db_session,
            treatment="B",
            scheduled_for=_future_dt(48),
            cod_cliente=cliente.cod_cliente,
        )
        assert apt1.cod_appointment != apt2.cod_appointment
        # ambos siguen formato LIVAPT####
        assert apt1.cod_appointment.startswith("LIVAPT")
        assert apt2.cod_appointment.startswith("LIVAPT")

    def test_create_emits_audit_log(self, db_session, lead):
        appointment_service.create(
            db_session,
            treatment="Botox",
            scheduled_for=_future_dt(24),
            cod_lead=lead.cod_lead,
        )
        events = (
            db_session.query(AuditLog)
            .filter_by(action="appointment.created")
            .all()
        )
        assert len(events) == 1
        assert events[0].entity_type == "appointment"

    def test_create_with_optional_fields(self, db_session, lead):
        apt = appointment_service.create(
            db_session,
            treatment="HIFU",
            scheduled_for=_future_dt(72),
            cod_lead=lead.cod_lead,
            duration_min=90,
            channel="whatsapp",
            notes="Cliente prefiere tarde",
        )
        assert apt.duration_min == 90
        assert apt.channel == "whatsapp"
        assert apt.notes == "Cliente prefiere tarde"


# ============================================================
# GET / LIST
# ============================================================
class TestGetByCod:
    def test_get_existing(self, db_session, lead):
        apt = appointment_service.create(
            db_session,
            treatment="Botox",
            scheduled_for=_future_dt(24),
            cod_lead=lead.cod_lead,
        )
        found = appointment_service.get_by_cod(db_session, apt.cod_appointment)
        assert found.id == apt.id

    def test_get_unknown_raises(self, db_session):
        with pytest.raises(appointment_service.AppointmentNotFoundError):
            appointment_service.get_by_cod(db_session, "LIVAPT9999")


class TestList:
    def test_list_empty(self, db_session):
        items, total = appointment_service.list_with_filters(db_session)
        assert items == []
        assert total == 0

    def test_list_returns_all_no_filter(self, db_session, lead, cliente):
        appointment_service.create(
            db_session, treatment="A", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.create(
            db_session, treatment="B", scheduled_for=_future_dt(48), cod_cliente=cliente.cod_cliente
        )
        items, total = appointment_service.list_with_filters(db_session)
        assert total == 2
        assert len(items) == 2

    def test_filter_by_status(self, db_session, lead):
        apt1 = appointment_service.create(
            db_session, treatment="A", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.confirm(db_session, apt1.cod_appointment)
        appointment_service.create(
            db_session, treatment="B", scheduled_for=_future_dt(48), cod_lead=lead.cod_lead
        )
        items, total = appointment_service.list_with_filters(db_session, status="confirmed")
        assert total == 1
        assert items[0].cod_appointment == apt1.cod_appointment

    def test_filter_by_cod_cliente(self, db_session, cliente, lead):
        appointment_service.create(
            db_session, treatment="A", scheduled_for=_future_dt(24), cod_cliente=cliente.cod_cliente
        )
        appointment_service.create(
            db_session, treatment="B", scheduled_for=_future_dt(48), cod_lead=lead.cod_lead
        )
        items, total = appointment_service.list_with_filters(
            db_session, cod_cliente=cliente.cod_cliente
        )
        assert total == 1

    def test_filter_by_date_range(self, db_session, lead):
        apt_near = appointment_service.create(
            db_session, treatment="Soon", scheduled_for=_future_dt(2), cod_lead=lead.cod_lead
        )
        apt_far = appointment_service.create(
            db_session, treatment="Far", scheduled_for=_future_dt(120), cod_lead=lead.cod_lead
        )
        items, total = appointment_service.list_with_filters(
            db_session,
            scheduled_from=datetime.now(timezone.utc),
            scheduled_to=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        assert total == 1
        assert items[0].cod_appointment == apt_near.cod_appointment

    def test_pagination(self, db_session, lead):
        for i in range(5):
            appointment_service.create(
                db_session,
                treatment=f"T{i}",
                scheduled_for=_future_dt(24 + i),
                cod_lead=lead.cod_lead,
            )
        items, total = appointment_service.list_with_filters(db_session, limit=2, offset=2)
        assert total == 5
        assert len(items) == 2


# ============================================================
# UPDATE
# ============================================================
class TestUpdate:
    def test_update_editable_fields(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="Old", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        new_dt = _future_dt(48)
        updated = appointment_service.update(
            db_session,
            apt.cod_appointment,
            treatment="New",
            scheduled_for=new_dt,
            duration_min=120,
            channel="phone",
            notes="Cambio horario",
        )
        assert updated.treatment == "New"
        assert updated.scheduled_for == new_dt
        assert updated.duration_min == 120
        assert updated.channel == "phone"
        assert updated.notes == "Cambio horario"

    def test_update_terminal_raises(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.cancel(db_session, apt.cod_appointment)
        with pytest.raises(appointment_service.InvalidTransitionError):
            appointment_service.update(db_session, apt.cod_appointment, treatment="Y")


# ============================================================
# CONFIRM
# ============================================================
class TestConfirm:
    def test_confirm_scheduled(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="Botox", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        confirmed = appointment_service.confirm(db_session, apt.cod_appointment)
        assert confirmed.status == "confirmed"
        assert confirmed.confirmed_at is not None

    def test_confirm_already_confirmed_raises(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.confirm(db_session, apt.cod_appointment)
        with pytest.raises(appointment_service.InvalidTransitionError):
            appointment_service.confirm(db_session, apt.cod_appointment)


# ============================================================
# MARK ATTENDED — workflow critico ADR-0035 § 7
# ============================================================
class TestMarkAttended:
    def test_mark_attended_from_scheduled(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="Botox", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        attended = appointment_service.mark_attended(db_session, apt.cod_appointment)
        assert attended.status == "attended"
        assert attended.attended_at is not None

    def test_mark_attended_from_confirmed(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="Botox", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.confirm(db_session, apt.cod_appointment)
        attended = appointment_service.mark_attended(db_session, apt.cod_appointment)
        assert attended.status == "attended"

    def test_mark_attended_creates_cliente_with_lead_origen(self, db_session, lead):
        """ADR-0033: cliente creado al marcar attended hereda cod_lead_origen + UTMs."""
        apt = appointment_service.create(
            db_session, treatment="Botox", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        attended = appointment_service.mark_attended(db_session, apt.cod_appointment)

        # Cliente fue creado y vinculado
        assert attended.cod_cliente is not None
        cliente = cliente_service.get_by_cod(db_session, attended.cod_cliente)
        assert cliente.cod_lead_origen == lead.cod_lead
        assert cliente.vtiger_lead_id_origen == lead.vtiger_id
        # Attribution heredada (ADR-0011 v1.1 first-touch sagrada)
        assert cliente.utm_source_at_capture == "facebook"
        assert cliente.utm_campaign_at_capture == "dia-madre-test"
        assert cliente.fbclid_at_capture == "fb.1.test"

    def test_mark_attended_walk_in_no_cliente_creation(self, db_session, cliente):
        """Si ya tiene cod_cliente (walk-in), NO crea cliente nuevo."""
        apt = appointment_service.create(
            db_session,
            treatment="Limpieza",
            scheduled_for=_future_dt(24),
            cod_cliente=cliente.cod_cliente,
        )
        attended = appointment_service.mark_attended(db_session, apt.cod_appointment)
        assert attended.cod_cliente == cliente.cod_cliente

    def test_mark_attended_terminal_raises(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.cancel(db_session, apt.cod_appointment)
        with pytest.raises(appointment_service.InvalidTransitionError):
            appointment_service.mark_attended(db_session, apt.cod_appointment)

    def test_mark_attended_emits_audit(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.mark_attended(db_session, apt.cod_appointment)
        events = (
            db_session.query(AuditLog)
            .filter_by(action="appointment.marked_attended")
            .all()
        )
        assert len(events) == 1

    def test_mark_attended_transitions_lead_to_cliente(self, db_session, lead):
        """Auto-transicion: lead.estado_lead pasa a 'cliente' al marcar attended."""
        assert lead.estado_lead in ("nuevo", "contactado", "agendado")  # estado inicial activo
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.mark_attended(db_session, apt.cod_appointment)
        db_session.refresh(lead)
        assert lead.estado_lead == "cliente"
        # cod_cliente_vinculado debe apuntar al cliente recien creado
        assert lead.cod_cliente_vinculado is not None
        assert lead.cod_cliente_vinculado.startswith("LIVCLIENT")


# ============================================================
# MARK NO_SHOW
# ============================================================
class TestMarkNoShow:
    def test_mark_no_show_from_confirmed(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.confirm(db_session, apt.cod_appointment)
        ns = appointment_service.mark_no_show(db_session, apt.cod_appointment)
        assert ns.status == "no_show"
        assert ns.no_show_at is not None

    def test_mark_no_show_from_terminal_raises(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.mark_attended(db_session, apt.cod_appointment)
        with pytest.raises(appointment_service.InvalidTransitionError):
            appointment_service.mark_no_show(db_session, apt.cod_appointment)

    def test_mark_no_show_transitions_lead_to_contactado(self, db_session, lead):
        """Auto-transicion: lead.estado_lead vuelve a 'contactado' (re-nurturing)."""
        # Forzar lead a 'agendado' (simula flujo: cita confirmada antes del no-show)
        lead.estado_lead = "agendado"
        db_session.commit()
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.confirm(db_session, apt.cod_appointment)
        appointment_service.mark_no_show(db_session, apt.cod_appointment)
        db_session.refresh(lead)
        assert lead.estado_lead == "contactado"


class TestClienteRecurrente:
    """ADR-0035 v2: si phone del lead matchea con cliente activo,
    mark_attended no crea cliente nuevo, vincula al existente."""

    def test_lead_with_existing_client_phone_links_not_creates(self, db_session):
        # 1. Crear cliente existente con phone X
        cliente_existente = cliente_service.create(
            db_session, nombre="Cliente Recurrente", phone_raw="987111000"
        )
        db_session.commit()

        # 2. Crear lead nuevo con MISMO phone (simula "vio el ad de nuevo")
        recurring_lead = Lead(
            cod_lead="LIVLEAD0099",
            vtiger_id="V-9099",
            nombre="Mismo Cliente Diferente Forma",
            phone_e164="+51987111000",
            fuente="digital",
            canal_adquisicion="form_web",
            utm_campaign_at_capture="dia-madre-2026",
        )
        db_session.add(recurring_lead)
        db_session.commit()
        db_session.refresh(recurring_lead)

        # 3. Crear appointment + mark attended
        apt = appointment_service.create(
            db_session,
            treatment="Botox refresh",
            scheduled_for=_future_dt(24),
            cod_lead=recurring_lead.cod_lead,
        )
        appointment_service.mark_attended(db_session, apt.cod_appointment)

        # 4. Asserts: NO se creo cliente nuevo, se vinculo al existente
        assert apt.cod_cliente == cliente_existente.cod_cliente
        # El lead apunta al cliente original, no a uno nuevo
        db_session.refresh(recurring_lead)
        assert recurring_lead.cod_cliente_vinculado == cliente_existente.cod_cliente


# ============================================================
# CANCEL
# ============================================================
class TestCancel:
    def test_cancel_scheduled(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        cancelled = appointment_service.cancel(db_session, apt.cod_appointment)
        assert cancelled.status == "cancelled"
        assert cancelled.cancelled_at is not None

    def test_cancel_already_terminal_raises(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.cancel(db_session, apt.cod_appointment)
        with pytest.raises(appointment_service.InvalidTransitionError):
            appointment_service.cancel(db_session, apt.cod_appointment)


# ============================================================
# RESCHEDULE
# ============================================================
class TestReschedule:
    def test_reschedule_creates_new_and_marks_original(self, db_session, lead):
        original = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        new_dt = _future_dt(72)
        original_after, new_apt = appointment_service.reschedule(
            db_session,
            original.cod_appointment,
            new_scheduled_for=new_dt,
            notes_addendum="Cliente pidio cambio",
        )
        assert original_after.status == "rescheduled"
        assert original_after.rescheduled_to == new_apt.id
        assert new_apt.status == "scheduled"
        assert new_apt.scheduled_for == new_dt
        assert new_apt.treatment == original.treatment
        assert new_apt.lead_id == original.lead_id

    def test_reschedule_terminal_raises(self, db_session, lead):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=_future_dt(24), cod_lead=lead.cod_lead
        )
        appointment_service.mark_attended(db_session, apt.cod_appointment)
        with pytest.raises(appointment_service.InvalidTransitionError):
            appointment_service.reschedule(
                db_session, apt.cod_appointment, new_scheduled_for=_future_dt(48)
            )

    def test_reschedule_carries_notes_with_addendum(self, db_session, lead):
        original = appointment_service.create(
            db_session,
            treatment="X",
            scheduled_for=_future_dt(24),
            cod_lead=lead.cod_lead,
            notes="Original notes",
        )
        _, new_apt = appointment_service.reschedule(
            db_session,
            original.cod_appointment,
            new_scheduled_for=_future_dt(48),
            notes_addendum="Razon del cambio",
        )
        assert "Original notes" in (new_apt.notes or "")
        assert "Razon del cambio" in (new_apt.notes or "")
