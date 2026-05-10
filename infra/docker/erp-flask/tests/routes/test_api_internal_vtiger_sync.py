"""Tests para routes/api_internal_vtiger_sync.py — endpoint GET /api/internal/leads/pending-vtiger-sync.

Endpoint consumido por n8n Workflow [A2] (cron 2min) para propagar cambios de
estado lead disparados desde ERP hacia Vtiger leadstatus.

Auth: shared secret X-Internal-Token.
Cursor: integer audit_log.id, > since.
Filtros: solo audit.action en {appointment.marked_attended, appointment.marked_no_show},
solo leads con vtiger_id NOT NULL.
"""
import json
from datetime import datetime, timezone

from models.appointment import Appointment
from models.audit_log import AuditLog
from models.lead import Lead


VALID_TOKEN = "test-internal-token-do-not-use-in-prod"
ENDPOINT = "/api/internal/leads/pending-vtiger-sync"


def _create_lead(db, vtiger_id: str = "10x100", cod_lead: str = "LIVLEAD0001") -> Lead:
    """Crea Lead con vtiger_id para testing."""
    lead = Lead(
        cod_lead=cod_lead,
        vtiger_id=vtiger_id,
        nombre="Test Lead Vtiger Sync",
        phone_e164="+51999000100",
        email_lower="testvtigersync@example.com",
        fuente="form_web",
        canal_adquisicion="form_web",
        estado_lead="agendado",
        fecha_captura=datetime.now(timezone.utc),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def _create_lead_no_vtiger(db, cod_lead: str = "LIVLEAD9001") -> Lead:
    """Crea Lead sin vtiger_id (manual ERP, walk-in convertido)."""
    lead = Lead(
        cod_lead=cod_lead,
        vtiger_id=None,  # explicito para testing
        nombre="Walk-in Test",
        phone_e164="+51999009001",
        email_lower="walkin@example.com",
        fuente="organico",
        canal_adquisicion="organico",
        estado_lead="agendado",
        fecha_captura=datetime.now(timezone.utc),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def _create_appointment(db, lead: Lead, cod: str = "LIVAPT0001") -> Appointment:
    """Crea Appointment vinculada a un lead."""
    apt = Appointment(
        cod_appointment=cod,
        lead_id=lead.id,
        treatment="botox",
        scheduled_for=datetime.now(timezone.utc),
        status="scheduled",
    )
    db.add(apt)
    db.commit()
    db.refresh(apt)
    return apt


def _create_audit_event(
    db,
    appointment_cod: str,
    action: str,
    after_state: dict | None = None,
) -> AuditLog:
    """Crea audit_log row con entity_type=appointment + action especifica."""
    event = AuditLog(
        action=action,
        category="appointment",
        entity_type="appointment",
        entity_id=appointment_cod,
        after_state=after_state or {"status": "attended"},
        result="success",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# ─────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_rejects_without_token(self, client):
        response = client.get(ENDPOINT)
        assert response.status_code == 403

    def test_rejects_invalid_token(self, client):
        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": "garbage"},
        )
        assert response.status_code == 403

    def test_accepts_valid_token_empty(self, client, db_session):
        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["count"] == 0
        assert data["items"] == []
        assert data["next_cursor"] == 0  # default since=0
        assert data["has_more"] is False


# ─────────────────────────────────────────────────────────────────────
# Filtrado por audit.action
# ─────────────────────────────────────────────────────────────────────

class TestActionFilter:
    def test_marked_attended_returns_target_cliente(self, client, db_session):
        lead = _create_lead(db_session, vtiger_id="10x200")
        apt = _create_appointment(db_session, lead, cod="LIVAPT0010")
        _create_audit_event(db_session, "LIVAPT0010", "appointment.marked_attended")

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)

        assert data["count"] == 1
        item = data["items"][0]
        assert item["audit_action"] == "appointment.marked_attended"
        assert item["cod_appointment"] == "LIVAPT0010"
        assert item["vtiger_id"] == "10x200"
        assert item["target_vtiger_leadstatus"] == "Cliente"

    def test_marked_no_show_returns_target_contactado(self, client, db_session):
        lead = _create_lead(db_session, vtiger_id="10x201", cod_lead="LIVLEAD0002")
        apt = _create_appointment(db_session, lead, cod="LIVAPT0011")
        _create_audit_event(
            db_session, "LIVAPT0011", "appointment.marked_no_show",
            after_state={"status": "no_show"},
        )

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)

        assert data["count"] == 1
        assert data["items"][0]["target_vtiger_leadstatus"] == "Contactado"

    def test_excludes_unrelated_actions(self, client, db_session):
        """Eventos como appointment.created / cancelled / confirmed NO entran al sync."""
        lead = _create_lead(db_session, vtiger_id="10x202", cod_lead="LIVLEAD0003")
        apt = _create_appointment(db_session, lead, cod="LIVAPT0012")

        # 3 eventos no relevantes + 1 relevante
        for action in ("appointment.created", "appointment.confirmed",
                       "appointment.cancelled", "appointment.updated"):
            _create_audit_event(db_session, "LIVAPT0012", action)
        _create_audit_event(db_session, "LIVAPT0012", "appointment.marked_attended")

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)

        # Solo 1 (el marked_attended), los otros 4 filtrados
        assert data["count"] == 1
        assert data["items"][0]["audit_action"] == "appointment.marked_attended"


# ─────────────────────────────────────────────────────────────────────
# Filtrado por vtiger_id
# ─────────────────────────────────────────────────────────────────────

class TestVtigerIdFilter:
    def test_excludes_leads_without_vtiger_id(self, client, db_session):
        """Walk-in / referido convertido sin vtiger_id NO entra al sync."""
        lead_walkin = _create_lead_no_vtiger(db_session)
        apt = _create_appointment(db_session, lead_walkin, cod="LIVAPT0020")
        _create_audit_event(db_session, "LIVAPT0020", "appointment.marked_attended")

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)

        # 0 items — el lead no tiene vtiger_id, nada que sincronizar
        assert data["count"] == 0

    def test_includes_leads_with_vtiger_id(self, client, db_session):
        """Lead que vino de Vtiger SI entra al sync."""
        lead = _create_lead(db_session, vtiger_id="10x300", cod_lead="LIVLEAD0030")
        apt = _create_appointment(db_session, lead, cod="LIVAPT0030")
        _create_audit_event(db_session, "LIVAPT0030", "appointment.marked_attended")

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)
        assert data["count"] == 1


# ─────────────────────────────────────────────────────────────────────
# Cursor & paginacion
# ─────────────────────────────────────────────────────────────────────

class TestCursor:
    def test_cursor_filters_strictly_greater_than(self, client, db_session):
        """since=N debe excluir audit_log_id <= N."""
        lead = _create_lead(db_session, vtiger_id="10x400", cod_lead="LIVLEAD0040")
        apt = _create_appointment(db_session, lead, cod="LIVAPT0040")

        ev1 = _create_audit_event(db_session, "LIVAPT0040", "appointment.marked_attended")
        ev2 = _create_audit_event(db_session, "LIVAPT0040", "appointment.marked_no_show")

        # Pide eventos con id > ev1.id → solo ev2 entra
        response = client.get(
            f"{ENDPOINT}?since={ev1.id}",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)
        assert data["count"] == 1
        assert data["items"][0]["audit_log_id"] == ev2.id
        assert data["next_cursor"] == ev2.id

    def test_next_cursor_advances_to_max_id(self, client, db_session):
        """next_cursor = max audit_log_id en items devueltos (el ultimo, ASC order)."""
        lead = _create_lead(db_session, vtiger_id="10x500", cod_lead="LIVLEAD0050")
        apt = _create_appointment(db_session, lead, cod="LIVAPT0050")

        ev1 = _create_audit_event(db_session, "LIVAPT0050", "appointment.marked_attended")
        ev2 = _create_audit_event(db_session, "LIVAPT0050", "appointment.marked_no_show")
        ev3 = _create_audit_event(db_session, "LIVAPT0050", "appointment.marked_attended")

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)
        assert data["count"] == 3
        # Order ASC: ev1, ev2, ev3
        ids = [it["audit_log_id"] for it in data["items"]]
        assert ids == sorted(ids)
        assert data["next_cursor"] == ev3.id

    def test_empty_response_keeps_cursor_at_since(self, client, db_session):
        """Si no hay eventos nuevos, next_cursor = since (no avanza)."""
        response = client.get(
            f"{ENDPOINT}?since=12345",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)
        assert data["count"] == 0
        assert data["next_cursor"] == 12345


# ─────────────────────────────────────────────────────────────────────
# Limit & has_more
# ─────────────────────────────────────────────────────────────────────

class TestLimit:
    def test_default_limit_50_with_has_more_flag(self, client, db_session):
        """Si hay >= 50 items y limit default 50 → has_more=True."""
        lead = _create_lead(db_session, vtiger_id="10x600", cod_lead="LIVLEAD0060")

        # Crear 51 appointments + 51 audit events
        for i in range(51):
            cod = f"LIVAPT{6000 + i}"
            apt = Appointment(
                cod_appointment=cod, lead_id=lead.id, treatment="botox",
                scheduled_for=datetime.now(timezone.utc), status="scheduled",
            )
            db_session.add(apt)
            db_session.commit()
            _create_audit_event(db_session, cod, "appointment.marked_attended")

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)
        assert data["count"] == 50
        assert data["has_more"] is True

    def test_limit_param_respected(self, client, db_session):
        lead = _create_lead(db_session, vtiger_id="10x700", cod_lead="LIVLEAD0070")
        for i in range(5):
            cod = f"LIVAPT{7000 + i}"
            apt = Appointment(
                cod_appointment=cod, lead_id=lead.id, treatment="botox",
                scheduled_for=datetime.now(timezone.utc), status="scheduled",
            )
            db_session.add(apt)
            db_session.commit()
            _create_audit_event(db_session, cod, "appointment.marked_attended")

        response = client.get(
            f"{ENDPOINT}?limit=3",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)
        assert data["count"] == 3
        assert data["has_more"] is True  # 3 == limit, may have more

    def test_limit_caps_at_500(self, client, db_session):
        """limit=99999 se cappea a 500."""
        response = client.get(
            f"{ENDPOINT}?limit=99999",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        # Sin data, count=0, pero el endpoint no falla
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────
# Validacion params (400)
# ─────────────────────────────────────────────────────────────────────

class TestParamValidation:
    def test_rejects_invalid_since(self, client):
        response = client.get(
            f"{ENDPOINT}?since=not-an-int",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400

    def test_rejects_invalid_limit(self, client):
        response = client.get(
            f"{ENDPOINT}?limit=foo",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400


# ─────────────────────────────────────────────────────────────────────
# Schema del response
# ─────────────────────────────────────────────────────────────────────

class TestResponseSchema:
    def test_item_has_all_expected_fields(self, client, db_session):
        lead = _create_lead(db_session, vtiger_id="10x800", cod_lead="LIVLEAD0080")
        apt = _create_appointment(db_session, lead, cod="LIVAPT0080")
        _create_audit_event(db_session, "LIVAPT0080", "appointment.marked_attended")

        response = client.get(
            ENDPOINT,
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        data = json.loads(response.data)
        item = data["items"][0]

        # Todos los fields documentados en ADR-0036 deben estar
        for field in (
            "audit_log_id",
            "audit_action",
            "occurred_at",
            "cod_appointment",
            "cod_lead",
            "vtiger_id",
            "current_erp_estado_lead",
            "target_vtiger_leadstatus",
        ):
            assert field in item, f"Falta field {field!r} en item"
