"""Tests para routes/api_correcciones.py — ADR-0040 corrección controlada.

Cubre:
- Auth requerida (302 redirect sin sesión)
- Feature flag (404 cuando CORRECTIONS_ENABLED=False)
- PATCH venta fecha OK + audit venta.corrected con before/after
- Whitelist dura: campo monetario (total) → 400; campo inexistente → 400
- PATCH pago fecha OK
- fecha no vaciable; proxima_cita sí (nullable)
- debe/pagado intactos tras corrección de fecha
"""
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from config import settings
from models.audit_log import AuditLog
from models.pago import Pago
from models.venta import Venta
from services import cliente_service


@pytest.fixture
def feature_enabled(monkeypatch):
    monkeypatch.setattr(settings, "corrections_enabled", True)
    yield


@pytest.fixture
def feature_disabled(monkeypatch):
    monkeypatch.setattr(settings, "corrections_enabled", False)
    yield


@pytest.fixture
def cliente(db_session):
    c = cliente_service.create(db_session, nombre="Cliente Correccion Test", phone_raw="900555666")
    db_session.commit()
    return c


@pytest.fixture
def venta(db_session, cliente):
    v = Venta(
        fecha=date(2026, 7, 15),  # fecha "equivocada" a corregir
        cod_cliente=cliente.cod_cliente,
        cliente_nombre=cliente.nombre,
        tipo="Tratamiento",
        cod_item="TESTTRAT9001",
        categoria="Botox",
        moneda="PEN",
        total=Decimal("175.00"),
        pagado=Decimal("175.00"),
        debe=Decimal("0.00"),
        descuento=Decimal("0"),
    )
    db_session.add(v)
    db_session.commit()
    db_session.refresh(v)
    return v


@pytest.fixture
def pago(db_session, cliente, venta):
    p = Pago(
        cod_pago="TESTPAGO9001",
        fecha=date(2026, 7, 15),
        cod_cliente=cliente.cod_cliente,
        cliente_nombre=cliente.nombre,
        cod_item=venta.cod_item,
        monto=Decimal("175.00"),
        tipo_pago="normal",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


class _LoginMixin:
    def _login(self, client, user, password):
        client.post("/login", data={"username": user.username, "password": password})


class TestAuthRequired(_LoginMixin):
    def test_corregir_venta_requires_auth(self, client, feature_enabled):
        response = client.patch(
            "/api/ventas/TESTTRAT9001/corregir", json={"fecha": "2025-11-21"}, follow_redirects=False
        )
        assert response.status_code == 302

    def test_corregir_pago_requires_auth(self, client, feature_enabled):
        response = client.patch(
            "/api/pagos/TESTPAGO9001/corregir", json={"fecha": "2025-11-21"}, follow_redirects=False
        )
        assert response.status_code == 302


class TestFeatureFlagDisabled(_LoginMixin):
    def test_corregir_venta_returns_404(self, client, admin_user, feature_disabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch("/api/ventas/X/corregir", json={"fecha": "2025-11-21"})
        assert response.status_code == 404


class TestCorregirVenta(_LoginMixin):
    def test_corregir_fecha_ok_con_audit(self, client, admin_user, venta, db_session, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/ventas/{venta.cod_item}/corregir", json={"fecha": "2025-11-21"}
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["ok"] is True
        assert body["before"]["fecha"] == "2026-07-15"
        assert body["after"]["fecha"] == "2025-11-21"

        db_session.expire_all()
        v = db_session.execute(
            select(Venta).where(Venta.cod_item == venta.cod_item)
        ).scalar_one()
        assert v.fecha == date(2025, 11, 21)

        audit = db_session.execute(
            select(AuditLog)
            .where(AuditLog.action == "venta.corrected")
            .where(AuditLog.entity_id == venta.cod_item)
        ).scalar_one()
        assert audit.before_state["fecha"] == "2026-07-15"
        assert audit.after_state["fecha"] == "2025-11-21"

    def test_campo_monetario_rechazado_400(self, client, admin_user, venta, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/ventas/{venta.cod_item}/corregir", json={"total": "999.00"}
        )
        assert response.status_code == 400

    def test_campo_inexistente_rechazado_400(self, client, admin_user, venta, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/ventas/{venta.cod_item}/corregir", json={"campo_falso": "x"}
        )
        assert response.status_code == 400

    def test_body_vacio_400(self, client, admin_user, venta, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(f"/api/ventas/{venta.cod_item}/corregir", json={})
        assert response.status_code == 400

    def test_fecha_invalida_400(self, client, admin_user, venta, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/ventas/{venta.cod_item}/corregir", json={"fecha": "21/11/2025"}
        )
        assert response.status_code == 400

    def test_fecha_no_vaciable_400(self, client, admin_user, venta, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(f"/api/ventas/{venta.cod_item}/corregir", json={"fecha": ""})
        assert response.status_code == 400

    def test_venta_inexistente_404(self, client, admin_user, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            "/api/ventas/NOEXISTE999/corregir", json={"fecha": "2025-11-21"}
        )
        assert response.status_code == 404

    def test_notas_y_proxima_cita_corregibles(self, client, admin_user, venta, db_session, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/ventas/{venta.cod_item}/corregir",
            json={"notas": "corregido en test", "proxima_cita": "2026-08-01"},
        )
        assert response.status_code == 200
        db_session.expire_all()
        v = db_session.execute(
            select(Venta).where(Venta.cod_item == venta.cod_item)
        ).scalar_one()
        assert v.notas == "corregido en test"
        assert v.proxima_cita == date(2026, 8, 1)

    def test_debe_pagado_intactos_tras_correccion_fecha(
        self, client, admin_user, venta, db_session, feature_enabled
    ):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/ventas/{venta.cod_item}/corregir", json={"fecha": "2025-11-21"}
        )
        assert response.status_code == 200
        db_session.expire_all()
        v = db_session.execute(
            select(Venta).where(Venta.cod_item == venta.cod_item)
        ).scalar_one()
        assert v.total == Decimal("175.00")
        assert v.pagado == Decimal("175.00")
        assert v.debe == Decimal("0.00")


class TestCorregirPago(_LoginMixin):
    def test_corregir_fecha_pago_ok(self, client, admin_user, pago, db_session, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/pagos/{pago.cod_pago}/corregir", json={"fecha": "2025-11-21"}
        )
        assert response.status_code == 200
        db_session.expire_all()
        p = db_session.execute(
            select(Pago).where(Pago.cod_pago == pago.cod_pago)
        ).scalar_one()
        assert p.fecha == date(2025, 11, 21)
        # Monto intacto (trigger DEBE no afectado por fecha)
        assert p.monto == Decimal("175.00")

        audit = db_session.execute(
            select(AuditLog)
            .where(AuditLog.action == "pago.corrected")
            .where(AuditLog.entity_id == pago.cod_pago)
        ).scalar_one()
        assert audit.after_state["fecha"] == "2025-11-21"

    def test_monto_pago_rechazado_400(self, client, admin_user, pago, feature_enabled):
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/pagos/{pago.cod_pago}/corregir", json={"monto": "1.00"}
        )
        assert response.status_code == 400

    def test_proxima_cita_no_corregible_en_pago_400(self, client, admin_user, pago, feature_enabled):
        """proxima_cita es whitelisted para VENTAS pero no para pagos."""
        self._login(client, admin_user, "TestPass123")
        response = client.patch(
            f"/api/pagos/{pago.cod_pago}/corregir", json={"proxima_cita": "2026-08-01"}
        )
        assert response.status_code == 400
