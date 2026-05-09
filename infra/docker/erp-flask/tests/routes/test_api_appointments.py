"""Smoke tests para /api/appointments (ADR-0035, Fase 4A).

Cubre:
- Auth requerida (302 redirect sin sesión)
- Feature flag (404 cuando AGENDA_FEATURE_ENABLED=False)
- CRUD basico happy path
- Transiciones de estado via endpoints
"""
from datetime import datetime, timedelta, timezone

import pytest

from config import settings
from models.lead import Lead
from services import appointment_service, cliente_service


def _future_iso(hours: int = 24) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


@pytest.fixture
def feature_enabled(monkeypatch):
    """Activa el feature flag AGENDA_FEATURE_ENABLED durante el test."""
    monkeypatch.setattr(settings, "agenda_feature_enabled", True)
    yield


@pytest.fixture
def feature_disabled(monkeypatch):
    """Confirma que el feature flag esta apagado (default)."""
    monkeypatch.setattr(settings, "agenda_feature_enabled", False)
    yield


@pytest.fixture
def lead(db_session):
    lead = Lead(
        cod_lead="LIVLEAD0010",
        vtiger_id="V-2010",
        nombre="API Test Lead",
        phone_e164="+51900111222",
        fuente="digital",
        canal_adquisicion="form_web",
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.fixture
def cliente(db_session):
    c = cliente_service.create(db_session, nombre="Walk In Test", phone_raw="900333444")
    db_session.commit()
    return c


class _LoginMixin:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})


class TestAuthRequired(_LoginMixin):
    """Sin sesion -> 302 redirect a /login."""

    def test_list_requires_auth(self, client, feature_enabled):
        response = client.get("/api/appointments", follow_redirects=False)
        assert response.status_code == 302

    def test_create_requires_auth(self, client, feature_enabled):
        response = client.post("/api/appointments", json={}, follow_redirects=False)
        assert response.status_code == 302


class TestFeatureFlagDisabled(_LoginMixin):
    """Con flag OFF -> 404 (endpoint no existe)."""

    def test_list_returns_404(self, client, admin_user, feature_disabled):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/appointments")
        assert response.status_code == 404

    def test_create_returns_404(self, client, admin_user, feature_disabled):
        self._login(client, admin_user, "TestPass123")
        response = client.post("/api/appointments", json={"treatment": "X"})
        assert response.status_code == 404


class TestCreateAppointment(_LoginMixin):
    def test_create_with_lead(self, client, admin_user, lead, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/api/appointments",
            json={
                "cod_lead": lead.cod_lead,
                "treatment": "Botox",
                "scheduled_for": _future_iso(48),
                "channel": "whatsapp",
            },
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["cod_appointment"].startswith("LIVAPT")
        assert body["status"] == "scheduled"
        assert body["lead_id"] == lead.id

    def test_create_with_cliente(self, client, admin_user, cliente, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/api/appointments",
            json={
                "cod_cliente": cliente.cod_cliente,
                "treatment": "Limpieza",
                "scheduled_for": _future_iso(24),
            },
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["cod_cliente"] == cliente.cod_cliente
        assert body["lead_id"] is None

    def test_create_without_subject_returns_400(self, client, admin_user, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/api/appointments",
            json={"treatment": "X", "scheduled_for": _future_iso(24)},
        )
        assert response.status_code == 400

    def test_create_with_unknown_lead_returns_404(self, client, admin_user, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/api/appointments",
            json={
                "cod_lead": "LIVLEAD9999",
                "treatment": "X",
                "scheduled_for": _future_iso(24),
            },
        )
        assert response.status_code == 404


class TestListAppointments(_LoginMixin):
    def test_empty_list(self, client, admin_user, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/appointments")
        assert response.status_code == 200
        body = response.get_json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_filter_by_status(self, client, admin_user, db_session, lead, feature_enabled):
        appointment_service.create(
            db_session, treatment="A", scheduled_for=datetime.now(timezone.utc) + timedelta(hours=24),
            cod_lead=lead.cod_lead,
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/appointments?status=scheduled")
        assert response.status_code == 200
        body = response.get_json()
        assert body["total"] == 1


class TestGetAppointment(_LoginMixin):
    def test_get_existing(self, client, admin_user, db_session, lead, feature_enabled):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=datetime.now(timezone.utc) + timedelta(hours=24),
            cod_lead=lead.cod_lead,
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.get(f"/api/appointments/{apt.cod_appointment}")
        assert response.status_code == 200

    def test_get_unknown_returns_404(self, client, admin_user, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/appointments/LIVAPT9999")
        assert response.status_code == 404


class TestTransitionEndpoints(_LoginMixin):
    def test_confirm_endpoint(self, client, admin_user, db_session, lead, feature_enabled):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=datetime.now(timezone.utc) + timedelta(hours=24),
            cod_lead=lead.cod_lead,
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.post(f"/api/appointments/{apt.cod_appointment}/confirm")
        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "confirmed"

    def test_mark_attended_endpoint(self, client, admin_user, db_session, lead, feature_enabled):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=datetime.now(timezone.utc) + timedelta(hours=24),
            cod_lead=lead.cod_lead,
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.post(f"/api/appointments/{apt.cod_appointment}/mark-attended")
        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "attended"
        # Cliente fue creado y vinculado (ADR-0033)
        assert body["cod_cliente"] is not None
        assert body["cod_cliente"].startswith("LIVCLIENT")

    def test_cancel_endpoint(self, client, admin_user, db_session, lead, feature_enabled):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=datetime.now(timezone.utc) + timedelta(hours=24),
            cod_lead=lead.cod_lead,
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.post(f"/api/appointments/{apt.cod_appointment}/cancel")
        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "cancelled"

    def test_invalid_transition_returns_409(self, client, admin_user, db_session, lead, feature_enabled):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=datetime.now(timezone.utc) + timedelta(hours=24),
            cod_lead=lead.cod_lead,
        )
        appointment_service.cancel(db_session, apt.cod_appointment)
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        # Intento confirmar una cancelled
        response = client.post(f"/api/appointments/{apt.cod_appointment}/confirm")
        assert response.status_code == 409

    def test_reschedule_endpoint(self, client, admin_user, db_session, lead, feature_enabled):
        apt = appointment_service.create(
            db_session, treatment="X", scheduled_for=datetime.now(timezone.utc) + timedelta(hours=24),
            cod_lead=lead.cod_lead,
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            f"/api/appointments/{apt.cod_appointment}/reschedule",
            json={"new_scheduled_for": _future_iso(72), "notes_addendum": "API test"},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["original"]["status"] == "rescheduled"
        assert body["new"]["status"] == "scheduled"
