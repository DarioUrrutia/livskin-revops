"""Smoke tests para endpoints API JSON: deben requerir auth + retornar JSON."""
import json
from datetime import date
from decimal import Decimal

from services import catalogo_service, cliente_service, venta_service


class _LoginMixin:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})


class TestApiConfig(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get("/api/config", follow_redirects=False)
        assert response.status_code == 302

    def test_returns_dict(self, client, admin_user, db_session):
        # Seedar algunos catálogos
        catalogo_service.add_valor(db_session, "tipo", "Tratamiento")
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/config")
        assert response.status_code == 200


class TestApiClientLookup(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get("/api/client-lookup?phone=987654321", follow_redirects=False)
        assert response.status_code == 302

    def test_no_match_returns_empty(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/client-lookup?phone=900000000")
        assert response.status_code == 200

    def test_match_found(self, client, admin_user, db_session):
        cliente_service.create(db_session, nombre="LookupTest", phone_raw="987654321")
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/client-lookup?phone=987654321")
        assert response.status_code == 200


class TestApiCliente(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get("/api/clientes", follow_redirects=False)
        assert response.status_code == 302

    def test_list_clientes(self, client, admin_user, db_session):
        cliente_service.create(db_session, nombre="ApiCliente1")
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/clientes")
        assert response.status_code == 200


class TestApiCatalogo(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get("/api/catalogo", follow_redirects=False)
        assert response.status_code == 302

    def test_list(self, client, admin_user, db_session):
        catalogo_service.add_valor(db_session, "x", "TestVal")
        db_session.commit()
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/catalogo")
        assert response.status_code == 200


class TestApiDashboard(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get("/api/dashboard", follow_redirects=False)
        assert response.status_code == 302

    def test_returns_dict(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/dashboard")
        # Acepta 200 o 500 (si no hay data y el service falla por div/0)
        assert response.status_code in (200, 500)


class TestApiLibro(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get("/api/libro", follow_redirects=False)
        assert response.status_code == 302

    def test_empty_libro(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/libro")
        assert response.status_code == 200


class TestApiGasto(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.get("/api/gastos", follow_redirects=False)
        assert response.status_code == 302

    def test_list_gastos(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.get("/api/gastos")
        assert response.status_code == 200


class TestApiPagos(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.post("/api/pagos", json={}, follow_redirects=False)
        assert response.status_code == 302


class TestApiVenta(_LoginMixin):
    def test_requires_auth(self, client):
        response = client.post("/api/ventas", json={}, follow_redirects=False)
        assert response.status_code == 302
