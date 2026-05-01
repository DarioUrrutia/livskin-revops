"""Tests para services/capi_emitter_service.py — Mini-bloque 3.4.

Service interno que emite Meta CAPI events vía n8n webhook.
NON-BLOCKING: si n8n cae, audit log + return ok=False, NO raise.

Auth: shared via X-Internal-Token (n8n valida).
Hashing PII: lo hace n8n, no este service (ver ADR-0019).
"""
import time
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest
import requests

from models.audit_log import AuditLog


# ─────────────────────────────────────────────────────────────────────
# Fixtures + helpers
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def emitter(monkeypatch):
    """Service module with capi_emit_enabled forced to True (overrides conftest disable)."""
    from services import capi_emitter_service
    from config import settings
    monkeypatch.setattr(settings, "capi_emit_enabled", True)
    return capi_emitter_service


def _base_lead_event_kwargs():
    """Common kwargs para un evento Lead típico."""
    return {
        "event_name": "Lead",
        "event_id": "test-event-id-abc-123",
        "event_source_url": "https://livskin.site/?utm_source=facebook",
        "email": "test@example.com",
        "phone_e164": "+51999000111",
        "fbc": "fb.1.1777.IwAR_test",
        "client_ip_address": "78.213.23.237",
        "client_user_agent": "Mozilla/5.0 (Test)",
        "external_id": "LIVLEAD0001",
        "trigger_entity_type": "lead",
        "trigger_entity_id": "1",
    }


# ─────────────────────────────────────────────────────────────────────
# Validación schema
# ─────────────────────────────────────────────────────────────────────

class TestValidation:
    def test_rejects_invalid_event_name(self, db_session, emitter):
        with pytest.raises(ValueError, match="event_name"):
            emitter.emit_event(
                db_session,
                event_name="InvalidEventXYZ",
                event_id="test-id",
            )

    def test_rejects_missing_event_id(self, db_session, emitter):
        with pytest.raises(ValueError, match="event_id"):
            emitter.emit_event(
                db_session,
                event_name="Lead",
                event_id="",
            )

    def test_accepts_valid_lead_event(self, db_session, emitter):
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            result = emitter.emit_event(db_session, **_base_lead_event_kwargs())
        assert result["ok"] is True

    def test_accepts_valid_purchase_event_with_value(self, db_session, emitter):
        kwargs = _base_lead_event_kwargs()
        kwargs["event_name"] = "Purchase"
        kwargs["value"] = Decimal("250.00")
        kwargs["currency"] = "PEN"
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            result = emitter.emit_event(db_session, **kwargs)
        assert result["ok"] is True


# ─────────────────────────────────────────────────────────────────────
# Payload construido correctamente
# ─────────────────────────────────────────────────────────────────────

class TestPayloadConstruction:
    def test_payload_has_event_name_and_id(self, db_session, emitter):
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            emitter.emit_event(db_session, **_base_lead_event_kwargs())
        called_args, called_kwargs = mock_post.call_args
        body = called_kwargs.get("json", {})
        assert body["event_name"] == "Lead"
        assert body["event_id"] == "test-event-id-abc-123"

    def test_payload_includes_user_data(self, db_session, emitter):
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            emitter.emit_event(db_session, **_base_lead_event_kwargs())
        body = mock_post.call_args.kwargs["json"]
        ud = body["user_data"]
        # Raw values — n8n hashea
        assert ud["email"] == "test@example.com"
        assert ud["phone_e164"] == "+51999000111"
        assert ud["fbc"] == "fb.1.1777.IwAR_test"
        assert ud["client_ip_address"] == "78.213.23.237"
        assert ud["external_id"] == "LIVLEAD0001"

    def test_payload_includes_custom_data_purchase(self, db_session, emitter):
        kwargs = _base_lead_event_kwargs()
        kwargs["event_name"] = "Purchase"
        kwargs["value"] = Decimal("250.00")
        kwargs["currency"] = "PEN"
        kwargs["content_name"] = "Botox"
        kwargs["content_category"] = "Tratamiento"
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            emitter.emit_event(db_session, **kwargs)
        body = mock_post.call_args.kwargs["json"]
        cd = body["custom_data"]
        assert cd["currency"] == "PEN"
        assert str(cd["value"]) == "250.00"
        assert cd["content_name"] == "Botox"
        assert cd["content_category"] == "Tratamiento"

    def test_payload_event_time_defaults_to_now(self, db_session, emitter):
        before = int(time.time())
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            emitter.emit_event(db_session, **_base_lead_event_kwargs())
        body = mock_post.call_args.kwargs["json"]
        after = int(time.time())
        assert before <= body["event_time"] <= after + 1

    def test_payload_action_source_is_website(self, db_session, emitter):
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            emitter.emit_event(db_session, **_base_lead_event_kwargs())
        body = mock_post.call_args.kwargs["json"]
        assert body["action_source"] == "website"


# ─────────────────────────────────────────────────────────────────────
# Feature flag (capi_emit_enabled)
# ─────────────────────────────────────────────────────────────────────

class TestFeatureFlag:
    def test_disabled_returns_early_without_post(self, db_session, emitter, monkeypatch):
        from config import settings
        monkeypatch.setattr(settings, "capi_emit_enabled", False)
        with patch("requests.post") as mock_post:
            result = emitter.emit_event(db_session, **_base_lead_event_kwargs())
        assert result["ok"] is False
        assert result["error"] == "capi_emit_disabled"
        mock_post.assert_not_called()


# ─────────────────────────────────────────────────────────────────────
# Audit log integration
# ─────────────────────────────────────────────────────────────────────

class TestAuditLog:
    def test_success_writes_audit_emitted(self, db_session, emitter):
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, ok=True)
            mock_post.return_value.json.return_value = {"ok": True}
            emitter.emit_event(db_session, **_base_lead_event_kwargs())
        entry = (
            db_session.query(AuditLog)
            .filter_by(action="tracking.capi_event_emitted")
            .order_by(AuditLog.id.desc())
            .first()
        )
        assert entry is not None
        assert entry.audit_metadata["event_name"] == "Lead"
        assert entry.audit_metadata["event_id"] == "test-event-id-abc-123"
        assert entry.audit_metadata["trigger_entity_type"] == "lead"
        assert entry.audit_metadata["trigger_entity_id"] == "1"

    def test_failure_writes_audit_failed_no_raise(self, db_session, emitter):
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("n8n unreachable")
            # Service no debe raise
            result = emitter.emit_event(db_session, **_base_lead_event_kwargs())
        assert result["ok"] is False
        assert "n8n" in result["error"].lower() or "connection" in result["error"].lower()
        # Audit log entry de failure debe existir
        entry = (
            db_session.query(AuditLog)
            .filter_by(action="tracking.capi_event_failed")
            .order_by(AuditLog.id.desc())
            .first()
        )
        assert entry is not None

    def test_n8n_returns_5xx_logs_failure(self, db_session, emitter):
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock(status_code=502, ok=False)
            mock_resp.text = "Bad Gateway"
            mock_post.return_value = mock_resp
            result = emitter.emit_event(db_session, **_base_lead_event_kwargs())
        assert result["ok"] is False
        entry = (
            db_session.query(AuditLog)
            .filter_by(action="tracking.capi_event_failed")
            .order_by(AuditLog.id.desc())
            .first()
        )
        assert entry is not None
