"""Tests para routes/api_leads.py — POST /api/leads/intake (mini-bloque 3.3 Fase 3)."""
import json

import pytest
from sqlalchemy import select

from models.audit_log import AuditLog
from models.lead import Lead
from models.lead_touchpoint import LeadTouchpoint


# Payload base reutilizable
BASE_PAYLOAD = {
    "nombre": "Maria Test",
    "telefono": "987654321",
    "tratamiento": "Botox",
    "email": "maria.test@gmail.com",
    "utm_source": "instagram",
    "utm_medium": "social",
    "utm_campaign": "abril2026",
    "utm_content": "story_anuncio_001",
    "fbclid": "FB_xyz_test",
    "landing_url": "https://www.livskin.site/?utm_source=instagram",
    "first_referrer": "https://www.instagram.com/",
    "event_id": "lead_1745847123456_xtest9h",
    "consent_marketing": True,
}


class TestLeadIntakeHappyPath:
    def test_creates_new_lead_and_touchpoint(self, client, db_session):
        response = client.post(
            "/api/leads/intake",
            data=json.dumps(BASE_PAYLOAD),
            content_type="application/json",
        )
        assert response.status_code == 201, f"Body: {response.data!r}"
        body = json.loads(response.data)
        assert body["ok"] is True
        assert body["is_new_lead"] is True
        assert body["cod_lead"].startswith("LIVLEAD")
        assert body["touchpoint_id"] > 0

        # Verificar que el lead se persistio con UTMs at_capture
        lead = db_session.execute(
            select(Lead).where(Lead.cod_lead == body["cod_lead"])
        ).scalar_one()
        assert lead.nombre == "Maria Test"
        assert lead.phone_e164 == "+51987654321"  # E164 con prefix Peru
        assert lead.email_lower == "maria.test@gmail.com"
        assert lead.email_hash_sha256 is not None
        assert lead.utm_source_at_capture == "instagram"
        assert lead.utm_campaign_at_capture == "abril2026"
        assert lead.fbclid_at_capture == "FB_xyz_test"
        assert lead.tratamiento_interes == "Botox"
        assert lead.consent_marketing is True
        assert lead.estado_lead == "nuevo"
        assert lead.score == 0
        assert lead.canal_adquisicion == "form_web"
        assert lead.fuente == "web"

        # Verificar touchpoint
        touchpoint = db_session.execute(
            select(LeadTouchpoint).where(LeadTouchpoint.id == body["touchpoint_id"])
        ).scalar_one()
        assert touchpoint.lead_id == lead.id
        assert touchpoint.canal == "form_web"
        assert touchpoint.utm_source == "instagram"
        assert touchpoint.landing_url == "https://www.livskin.site/?utm_source=instagram"
        assert touchpoint.form_data_json is not None
        assert touchpoint.form_data_json.get("event_id") == "lead_1745847123456_xtest9h"
        assert touchpoint.form_data_json.get("first_referrer") == "https://www.instagram.com/"

    def test_creates_audit_log_entry(self, client, db_session):
        response = client.post(
            "/api/leads/intake",
            data=json.dumps(BASE_PAYLOAD),
            content_type="application/json",
        )
        assert response.status_code == 201
        cod_lead = json.loads(response.data)["cod_lead"]

        audit = db_session.execute(
            select(AuditLog).where(
                AuditLog.action == "lead.created",
                AuditLog.entity_id == cod_lead,
            )
        ).scalar_one()
        assert audit.entity_type == "lead"
        assert audit.result == "success"
        assert audit.user_username == "system_intake"
        assert audit.user_role == "system"

    def test_accepts_form_encoded_too(self, client, db_session):
        """SureForms suele enviar form-encoded, no JSON."""
        # Phone distinto para no colisionar con test anterior
        payload = {**BASE_PAYLOAD, "telefono": "987111222", "nombre": "Maria FormEnc"}
        response = client.post(
            "/api/leads/intake",
            data=payload,
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 201
        body = json.loads(response.data)
        assert body["ok"] is True


class TestLeadIntakeIdempotency:
    def test_same_phone_creates_touchpoint_not_new_lead(self, client, db_session):
        # Primera captura
        r1 = client.post(
            "/api/leads/intake",
            data=json.dumps({**BASE_PAYLOAD, "telefono": "987333444"}),
            content_type="application/json",
        )
        assert r1.status_code == 201
        body1 = json.loads(r1.data)
        cod_lead = body1["cod_lead"]
        assert body1["is_new_lead"] is True

        # Segunda captura mismo phone, distinta campaña
        r2 = client.post(
            "/api/leads/intake",
            data=json.dumps({
                **BASE_PAYLOAD,
                "telefono": "987333444",
                "utm_campaign": "mayo2026",
                "event_id": "lead_segundo_touchpoint_xyz",
            }),
            content_type="application/json",
        )
        assert r2.status_code == 201
        body2 = json.loads(r2.data)
        assert body2["cod_lead"] == cod_lead, "mismo cod_lead esperado"
        assert body2["is_new_lead"] is False, "no debe crear lead nuevo"
        assert body2["touchpoint_id"] != body1["touchpoint_id"], "touchpoint distinto"

        # Verificar que el lead tiene 2 touchpoints
        tps = db_session.execute(
            select(LeadTouchpoint).join(Lead).where(Lead.cod_lead == cod_lead).order_by(LeadTouchpoint.id)
        ).scalars().all()
        assert len(tps) == 2
        # First-touch UTM se preserva en lead.utm_campaign_at_capture
        lead = db_session.execute(select(Lead).where(Lead.cod_lead == cod_lead)).scalar_one()
        assert lead.utm_campaign_at_capture == "abril2026"  # primer touch
        # Second-touch UTM en touchpoint mas reciente
        assert tps[-1].utm_campaign == "mayo2026"


class TestLeadIntakeValidation:
    def test_rejects_missing_nombre(self, client):
        payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "nombre"}
        response = client.post(
            "/api/leads/intake",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_rejects_missing_telefono(self, client):
        payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "telefono"}
        response = client.post(
            "/api/leads/intake",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_rejects_invalid_phone(self, client):
        # Phone que no normaliza (muy corto, mas chars que numeros)
        payload = {**BASE_PAYLOAD, "telefono": "abc"}
        response = client.post(
            "/api/leads/intake",
            data=json.dumps(payload),
            content_type="application/json",
        )
        # Pydantic acepta el string (cumple min_length=6), pero normalize_phone lo rechaza
        # → IntakeValidationError → 422
        assert response.status_code == 422


class TestLeadIntakeMinimalFields:
    def test_works_without_email_or_utms(self, client, db_session):
        """Lead sin email ni UTMs (visitante directo). Debe funcionar igual."""
        minimal = {
            "nombre": "Visitante Directo",
            "telefono": "987555666",
            "consent_marketing": True,
        }
        response = client.post(
            "/api/leads/intake",
            data=json.dumps(minimal),
            content_type="application/json",
        )
        assert response.status_code == 201
        body = json.loads(response.data)
        assert body["ok"] is True

        lead = db_session.execute(select(Lead).where(Lead.cod_lead == body["cod_lead"])).scalar_one()
        assert lead.email_lower is None
        assert lead.utm_source_at_capture is None
        assert lead.tratamiento_interes is None
