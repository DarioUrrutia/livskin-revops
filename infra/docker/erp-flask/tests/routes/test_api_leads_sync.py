"""Tests para routes/api_leads_sync.py — endpoint POST /api/leads/sync-from-vtiger.

Endpoint recibido por n8n Workflow [B1] (Vtiger lead on-change → ERP espejo).

Auth: shared secret X-Internal-Token (mismo que /api/internal/audit-event).
Idempotencia: por vtiger_id (CREATE si no existe, UPDATE si sí).
At_capture fields: inmutables en UPDATE (first-touch attribution sagrada).
"""
import json

from models.audit_log import AuditLog
from models.lead import Lead


VALID_TOKEN = "test-internal-token-do-not-use-in-prod"
ENDPOINT = "/api/leads/sync-from-vtiger"


def _payload(**overrides):
    """Helper: payload base con required fields + overrides opcionales."""
    base = {
        "vtiger_id": "10x123",
        "nombre": "Test Lead Sync",
        "phone_e164": "+51999000001",
    }
    base.update(overrides)
    return base


# ─────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_rejects_without_token(self, client):
        response = client.post(
            ENDPOINT,
            data=json.dumps(_payload()),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_rejects_invalid_token(self, client):
        response = client.post(
            ENDPOINT,
            data=json.dumps(_payload()),
            content_type="application/json",
            headers={"X-Internal-Token": "garbage"},
        )
        assert response.status_code == 403

    def test_accepts_valid_token(self, client, db_session):
        response = client.post(
            ENDPOINT,
            data=json.dumps(_payload()),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────
# Schema validation (400)
# ─────────────────────────────────────────────────────────────────────

class TestSchemaValidation:
    def test_rejects_missing_vtiger_id(self, client):
        body = _payload()
        del body["vtiger_id"]
        response = client.post(
            ENDPOINT,
            data=json.dumps(body),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400
        assert json.loads(response.data)["error"] == "validation_error"

    def test_rejects_missing_phone(self, client):
        body = _payload()
        del body["phone_e164"]
        response = client.post(
            ENDPOINT,
            data=json.dumps(body),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400

    def test_rejects_missing_nombre(self, client):
        body = _payload()
        del body["nombre"]
        response = client.post(
            ENDPOINT,
            data=json.dumps(body),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 400


# ─────────────────────────────────────────────────────────────────────
# Create operation (lead nuevo)
# ─────────────────────────────────────────────────────────────────────

class TestCreateOperation:
    def test_creates_lead_returns_200(self, client, db_session):
        response = client.post(
            ENDPOINT,
            data=json.dumps(_payload()),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["ok"] is True
        assert body["operation"] == "created"
        assert body["vtiger_id"] == "10x123"
        assert body["lead_id"] > 0
        assert body["cod_lead"].startswith("LIVLEAD")

    def test_create_persists_to_db(self, client, db_session):
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10x999")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x999").first()
        assert lead is not None
        assert lead.nombre == "Test Lead Sync"
        assert lead.phone_e164 == "+51999000001"

    def test_create_with_full_attribution(self, client, db_session):
        full = _payload(
            vtiger_id="10x500",
            email="full@test.com",
            tratamiento_interes="Botox",
            utm_source="facebook",
            utm_medium="cpc",
            utm_campaign="test-campaign",
            fbclid="IwAR1xyz",
            fbc="fb.1.1714.IwAR1xyz",
            ga="GA1.2.123.456",
            event_id="550e8400-e29b-41d4-a716-446655440000",
            landing_url="https://livskin.site/botox",
            consent_marketing=True,
        )
        client.post(
            ENDPOINT,
            data=json.dumps(full),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x500").first()
        assert lead is not None
        assert lead.utm_source_at_capture == "facebook"
        assert lead.utm_campaign_at_capture == "test-campaign"
        assert lead.fbclid_at_capture == "IwAR1xyz"
        assert lead.fbc_at_capture == "fb.1.1714.IwAR1xyz"
        assert lead.ga_at_capture == "GA1.2.123.456"
        assert lead.event_id_at_capture == "550e8400-e29b-41d4-a716-446655440000"
        assert lead.tratamiento_interes == "Botox"
        assert lead.consent_marketing is True


# ─────────────────────────────────────────────────────────────────────
# Update operation (lead existente)
# ─────────────────────────────────────────────────────────────────────

class TestUpdateOperation:
    def test_second_call_returns_updated(self, client, db_session):
        # Primera llamada → CREATE
        r1 = client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10x777")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert json.loads(r1.data)["operation"] == "created"
        lead_id_first = json.loads(r1.data)["lead_id"]

        # Segunda llamada con mismo vtiger_id → UPDATE
        r2 = client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10x777", nombre="Test Updated")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        assert r2.status_code == 200
        body = json.loads(r2.data)
        assert body["operation"] == "updated"
        assert body["lead_id"] == lead_id_first  # mismo ID, no duplica

    def test_update_preserves_at_capture_fields(self, client, db_session):
        # CREATE con attribution full
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(
                vtiger_id="10x800",
                utm_source="facebook",
                fbclid="ORIGINAL_FBCLID",
                event_id="ORIGINAL_EVENT_ID",
            )),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        # UPDATE con attribution distinta — debe ignorarse (at_capture inmutable)
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(
                vtiger_id="10x800",
                utm_source="google",
                fbclid="NEW_FBCLID",
                event_id="NEW_EVENT_ID",
            )),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x800").first()
        assert lead.utm_source_at_capture == "facebook"  # preserved
        assert lead.fbclid_at_capture == "ORIGINAL_FBCLID"  # preserved
        assert lead.event_id_at_capture == "ORIGINAL_EVENT_ID"  # preserved

    def test_update_modifies_mutable_fields(self, client, db_session):
        # CREATE inicial
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(
                vtiger_id="10x801",
                nombre="Original Name",
                email="original@test.com",
                tratamiento_interes="Botox",
            )),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        # UPDATE — campos mutables deben actualizarse
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(
                vtiger_id="10x801",
                nombre="Updated Name",
                email="updated@test.com",
                tratamiento_interes="PRP",
                leadstatus="Contacted",
            )),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x801").first()
        assert lead.nombre == "Updated Name"
        assert lead.email_lower == "updated@test.com"
        assert lead.tratamiento_interes == "PRP"
        assert lead.estado_lead == "contactado"  # mapeado de "Contacted"


# ─────────────────────────────────────────────────────────────────────
# Status / source mapping
# ─────────────────────────────────────────────────────────────────────

class TestStatusMapping:
    def test_status_new_maps_to_nuevo(self, client, db_session):
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10x900", leadstatus="New")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x900").first()
        assert lead.estado_lead == "nuevo"

    def test_status_junk_lead_maps_to_perdido(self, client, db_session):
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10x901", leadstatus="Junk Lead")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x901").first()
        assert lead.estado_lead == "perdido"

    def test_status_qualified_maps_to_agendado(self, client, db_session):
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10x902", leadstatus="Qualified")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x902").first()
        assert lead.estado_lead == "agendado"

    def test_status_unknown_falls_back_to_nuevo(self, client, db_session):
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10x903", leadstatus="UnknownStatus")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        lead = db_session.query(Lead).filter_by(vtiger_id="10x903").first()
        assert lead.estado_lead == "nuevo"


# ─────────────────────────────────────────────────────────────────────
# Audit log entry
# ─────────────────────────────────────────────────────────────────────

class TestAuditLogIntegration:
    def test_create_writes_audit_entry(self, client, db_session):
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10xAUDIT1")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        entry = (
            db_session.query(AuditLog)
            .filter_by(action="lead.synced_from_vtiger")
            .order_by(AuditLog.id.desc())
            .first()
        )
        assert entry is not None
        assert entry.audit_metadata["vtiger_id"] == "10xAUDIT1"
        assert entry.audit_metadata["operation"] == "created"

    def test_update_writes_separate_audit_entry(self, client, db_session):
        # CREATE
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10xAUDIT2")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        # UPDATE
        client.post(
            ENDPOINT,
            data=json.dumps(_payload(vtiger_id="10xAUDIT2", nombre="Updated")),
            content_type="application/json",
            headers={"X-Internal-Token": VALID_TOKEN},
        )
        entries = (
            db_session.query(AuditLog)
            .filter_by(action="lead.synced_from_vtiger")
            .filter(AuditLog.audit_metadata["vtiger_id"].astext == "10xAUDIT2")
            .all()
        )
        assert len(entries) == 2
        operations = [e.audit_metadata["operation"] for e in entries]
        assert "created" in operations
        assert "updated" in operations
