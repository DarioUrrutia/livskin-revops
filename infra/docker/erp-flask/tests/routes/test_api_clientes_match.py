"""Tests para el endpoint GET /api/leads/search-match + extensión POST /api/clientes con cod_lead_origen.

ADR-0033 — Match automático lead↔cliente al crear cliente en ERP.

Endpoints:
- GET /api/leads/search-match?phone=X&email=Y&nombre=Z → busca lead candidate por
  phone/email/nombre. Retorna {match: {...}} o {match: null}.
- POST /api/clientes con cod_lead_origen opcional → crea cliente vinculado al lead.

Auth: session-based (admin_user) — son endpoints UI usados por la pestaña CLIENTE.

Feature flag: settings.auto_match_lead_enabled (default True). Si False:
GET /api/leads/search-match retorna 404.
"""
import json
from datetime import datetime, timezone

from models.cliente import Cliente
from models.lead import Lead


class _LoginMixin:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})


def _make_lead(
    db,
    *,
    cod_lead: str,
    nombre: str = "Sofia Test",
    phone_e164: str = "+51999111222",
    email_lower: str | None = None,
    vtiger_id: str | None = "10x100",
    fuente: str = "facebook",
    canal_adquisicion: str = "meta-ads",
    utm_source: str = "facebook",
    utm_campaign: str = "botox-mvp",
    fbclid: str | None = "IwAR1xyz",
    event_id: str | None = "evt-uuid-1",
    tratamiento_interes: str = "Botox",
) -> Lead:
    lead = Lead(
        cod_lead=cod_lead,
        vtiger_id=vtiger_id,
        nombre=nombre,
        phone_e164=phone_e164,
        email_lower=email_lower,
        fuente=fuente,
        canal_adquisicion=canal_adquisicion,
        utm_source_at_capture=utm_source,
        utm_campaign_at_capture=utm_campaign,
        fbclid_at_capture=fbclid,
        event_id_at_capture=event_id,
        tratamiento_interes=tratamiento_interes,
        consent_marketing=True,
        estado_lead="nuevo",
        fecha_captura=datetime.now(timezone.utc),
    )
    db.add(lead)
    db.flush()
    return lead


# ─────────────────────────────────────────────────────────────────────
# GET /api/leads/search-match
# ─────────────────────────────────────────────────────────────────────

class TestSearchMatchEndpoint(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get(
            "/api/leads/search-match?phone=987654321", follow_redirects=False
        )
        assert response.status_code == 302

    def test_returns_match_when_phone_found(self, client, admin_user, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0001",
            nombre="Sofia Test",
            phone_e164="+51987654321",
            vtiger_id="10x100",
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")

        response = client.get("/api/leads/search-match?phone=987654321")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["match"] is not None
        assert body["match"]["cod_lead"] == "LIVLEAD0001"
        assert body["match"]["vtiger_lead_id"] == "10x100"
        assert body["match"]["nombre"] == "Sofia Test"
        assert body["match"]["fuente"] == "facebook"
        assert body["match"]["tratamiento_interes"] == "Botox"

    def test_returns_match_when_email_found(self, client, admin_user, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0002",
            email_lower="sofia@test.com",
            phone_e164="+51900000001",
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")

        response = client.get("/api/leads/search-match?email=SOFIA@test.com")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["match"] is not None
        assert body["match"]["cod_lead"] == "LIVLEAD0002"

    def test_returns_match_when_nombre_found(self, client, admin_user, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0003",
            nombre="Pedro Unique",
            phone_e164="+51900000002",
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")

        response = client.get("/api/leads/search-match?nombre=Pedro%20Unique")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["match"] is not None
        assert body["match"]["cod_lead"] == "LIVLEAD0003"

    def test_returns_null_when_no_match(self, client, admin_user, db_session):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/leads/search-match?phone=999999999")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["match"] is None

    def test_returns_null_when_no_params(self, client, admin_user, db_session):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/leads/search-match")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["match"] is None

    def test_excludes_already_converted_lead(self, client, admin_user, db_session):
        from services import cliente_service

        _make_lead(
            db_session,
            cod_lead="LIVLEAD0040",
            phone_e164="+51900400400",
        )
        cliente_service.create(
            db_session,
            nombre="Sofia Convertida",
            phone_raw="+51900400500",
            cod_lead_origen="LIVLEAD0040",
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")

        response = client.get("/api/leads/search-match?phone=900400400")
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["match"] is None


# ─────────────────────────────────────────────────────────────────────
# Feature flag — auto_match_lead_enabled = False → 404
# ─────────────────────────────────────────────────────────────────────

class TestSearchMatchFeatureFlag(_LoginMixin):
    def test_disabled_returns_404(self, client, admin_user, db_session, monkeypatch):
        from config import settings

        monkeypatch.setattr(settings, "auto_match_lead_enabled", False)
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0001",
            phone_e164="+51999111222",
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")

        response = client.get("/api/leads/search-match?phone=999111222")
        assert response.status_code == 404

    def test_enabled_returns_200(self, client, admin_user, db_session, monkeypatch):
        from config import settings

        monkeypatch.setattr(settings, "auto_match_lead_enabled", True)
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/leads/search-match?phone=999111222")
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────
# POST /api/clientes con cod_lead_origen
# ─────────────────────────────────────────────────────────────────────

class TestPostClienteWithCodLeadOrigen(_LoginMixin):
    def test_post_with_cod_lead_origen_links_attribution(
        self, client, admin_user, db_session
    ):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0100",
            vtiger_id="10x100",
            phone_e164="+51900100100",
            utm_source="facebook",
            utm_campaign="botox-mvp",
            fbclid="IwAR_origin",
            event_id="evt-origin-uuid",
        )
        db_session.commit()
        self._login(client, admin_user, "TestPass123")

        response = client.post(
            "/api/clientes",
            data=json.dumps(
                {
                    "nombre": "Sofia Convertida",
                    "phone": "+51900100200",
                    "cod_lead_origen": "LIVLEAD0100",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        body = json.loads(response.data)
        assert body["cod_lead_origen"] == "LIVLEAD0100"

        # Verificar en DB que attribution fue copiada
        c = (
            db_session.query(Cliente)
            .filter_by(cod_cliente=body["cod_cliente"])
            .first()
        )
        assert c.cod_lead_origen == "LIVLEAD0100"
        assert c.vtiger_lead_id_origen == "10x100"
        assert c.utm_source_at_capture == "facebook"
        assert c.fbclid_at_capture == "IwAR_origin"

    def test_post_without_cod_lead_origen_creates_walkin(
        self, client, admin_user, db_session
    ):
        self._login(client, admin_user, "TestPass123")

        response = client.post(
            "/api/clientes",
            data=json.dumps(
                {
                    "nombre": "Carmen Walk-in",
                    "phone": "+51900100300",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        body = json.loads(response.data)
        assert body["cod_lead_origen"] is None

    def test_post_with_invalid_cod_lead_origen_returns_400(
        self, client, admin_user, db_session
    ):
        self._login(client, admin_user, "TestPass123")

        response = client.post(
            "/api/clientes",
            data=json.dumps(
                {
                    "nombre": "Sofia Bad Link",
                    "phone": "+51900100400",
                    "cod_lead_origen": "LIVLEAD9999",  # no existe
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400
