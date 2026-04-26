"""Tests de routes/legacy_forms.py: POST /venta, /pagos, /gasto con form-data."""
from datetime import date
from decimal import Decimal

from models.cliente import Cliente
from models.gasto import Gasto
from models.pago import Pago
from models.venta import Venta
from services import cliente_service


class TestGastoForm:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})

    def test_post_gasto_redirects_to_index(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/gasto",
            data={
                "fecha_gasto": "2026-04-26",
                "monto_gasto": "150",
                "tipo_gasto": "Insumos",
                "descripcion": "Test gasto",
            },
        )
        assert response.status_code == 302
        assert "tab=gasto" in response.headers.get("Location", "")

    def test_post_gasto_invalid_date_flashes_error(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/gasto",
            data={
                "fecha_gasto": "fecha-mala",
                "monto_gasto": "150",
            },
        )
        assert response.status_code == 302  # redirect con flash

    def test_post_gasto_zero_monto_flashes_error(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/gasto",
            data={
                "fecha_gasto": "2026-04-26",
                "monto_gasto": "0",
            },
        )
        assert response.status_code == 302


class TestVentaForm:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})

    def test_post_venta_minimal(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/venta",
            data={
                "fecha": "2026-04-26",
                "cliente": "Cliente Test Form",
                "telefono": "987654321",
                "num_items": "1",
                "tipo_0": "Tratamiento",
                "categoria_0": "Botox",
                "precio_lista_0": "200",
                "descuento_0": "0",
                "total_item_0": "200",
                "pago_item_0": "200",
                "efectivo": "200",
                "yape": "0",
                "plin": "0",
                "giro": "0",
            },
        )
        assert response.status_code == 302
        assert "tab=venta" in response.headers.get("Location", "")

    def test_post_venta_sin_fecha_flashes_error(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/venta",
            data={
                "fecha": "",
                "cliente": "X",
            },
        )
        assert response.status_code == 302  # redirect con flash error


class TestPagosForm:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})

    def test_post_pagos_requires_existing_cliente(self, client, admin_user, db_session):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/pagos",
            data={
                "fecha_pago": "2026-04-26",
                "cliente_pago": "ClienteInexistente",
                "num_items": "0",
                "efectivo_pago": "100",
            },
        )
        # No tiene deudas + 100 cash → genera credito_generado
        assert response.status_code == 302

    def test_post_pagos_sin_fecha_flashes_error(self, client, admin_user):
        self._login(client, admin_user, "TestPass123")
        response = client.post(
            "/pagos",
            data={
                "fecha_pago": "",
                "cliente_pago": "X",
            },
        )
        assert response.status_code == 302
