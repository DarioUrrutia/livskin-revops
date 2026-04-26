"""Tests de cliente_service (CRUD + history)."""
from datetime import date
from decimal import Decimal

import pytest

from models.cliente import Cliente
from models.pago import Pago
from models.venta import Venta
from services import cliente_service


class TestGetByCod:
    def test_get_existing(self, db_session):
        c = cliente_service.create(db_session, nombre="Ana", phone_raw="987654321")
        found = cliente_service.get_by_cod(db_session, c.cod_cliente)
        assert found.id == c.id

    def test_get_unknown_raises(self, db_session):
        with pytest.raises(cliente_service.ClienteNotFoundError):
            cliente_service.get_by_cod(db_session, "LIVCLIENT9999")


class TestGetByPhone:
    def test_finds_by_phone(self, db_session):
        cliente_service.create(db_session, nombre="Ana", phone_raw="987654321")
        found = cliente_service.get_by_phone(db_session, "987654321")
        assert found is not None
        assert found.nombre == "Ana"

    def test_normalizes_phone_for_lookup(self, db_session):
        cliente_service.create(db_session, nombre="Bea", phone_raw="987654321")
        # Mismo número pero con espacios/dashes — el normalize_phone debe matcheaarlo
        found = cliente_service.get_by_phone(db_session, "987-654-321")
        assert found is not None
        assert found.nombre == "Bea"

    def test_returns_none_when_no_match(self, db_session):
        assert cliente_service.get_by_phone(db_session, "+51900000999") is None

    def test_invalid_phone_returns_none(self, db_session):
        assert cliente_service.get_by_phone(db_session, "abc") is None


class TestCreate:
    def test_create_minimal(self, db_session):
        c = cliente_service.create(db_session, nombre="Carmen")
        assert c.cod_cliente.startswith("LIVCLIENT")
        assert c.nombre == "Carmen"
        assert c.activo is True

    def test_create_with_phone_and_email(self, db_session):
        c = cliente_service.create(
            db_session,
            nombre="Dora",
            phone_raw="987654321",
            email_raw="DORA@example.com",
        )
        assert c.phone_e164 == "+51987654321"
        assert c.email_lower == "dora@example.com"
        assert c.email_hash_sha256 is not None

    def test_create_duplicate_phone_raises(self, db_session):
        cliente_service.create(db_session, nombre="Ana", phone_raw="987654321")
        with pytest.raises(cliente_service.ClienteDuplicadoError):
            cliente_service.create(db_session, nombre="Ana2", phone_raw="987654321")

    def test_create_assigns_unique_cod(self, db_session):
        c1 = cliente_service.create(db_session, nombre="C1")
        c2 = cliente_service.create(db_session, nombre="C2")
        assert c1.cod_cliente != c2.cod_cliente


class TestGetOrCreate:
    def test_creates_when_not_exists(self, db_session):
        c = cliente_service.get_or_create(db_session, nombre="Eva")
        assert c.cod_cliente.startswith("LIVCLIENT")

    def test_finds_case_insensitive(self, db_session):
        cliente_service.create(db_session, nombre="Eva")
        c = cliente_service.get_or_create(db_session, nombre="EVA")
        assert c.nombre == "Eva"  # devuelve el original, no crea nuevo

    def test_fills_empty_phone_without_actualizar(self, db_session):
        c = cliente_service.create(db_session, nombre="Eva")
        c2 = cliente_service.get_or_create(
            db_session, nombre="Eva", phone_raw="987654321"
        )
        assert c2.phone_e164 == "+51987654321"
        assert c2.id == c.id

    def test_does_not_overwrite_phone_without_actualizar(self, db_session):
        cliente_service.create(db_session, nombre="Eva", phone_raw="987111111")
        c2 = cliente_service.get_or_create(
            db_session, nombre="Eva", phone_raw="987222222", actualizar=False
        )
        assert c2.phone_e164 == "+51987111111"

    def test_overwrites_phone_when_actualizar_true(self, db_session):
        cliente_service.create(db_session, nombre="Eva", phone_raw="987111111")
        c2 = cliente_service.get_or_create(
            db_session, nombre="Eva", phone_raw="987222222", actualizar=True
        )
        assert c2.phone_e164 == "+51987222222"

    def test_actualizar_blocked_if_phone_belongs_to_another_cliente(self, db_session):
        cliente_service.create(db_session, nombre="Ana", phone_raw="987111111")
        cliente_service.create(db_session, nombre="Bea", phone_raw="987222222")
        with pytest.raises(cliente_service.ClienteDuplicadoError):
            cliente_service.get_or_create(
                db_session, nombre="Ana", phone_raw="987222222", actualizar=True
            )

    def test_empty_nombre_raises(self, db_session):
        with pytest.raises(ValueError):
            cliente_service.get_or_create(db_session, nombre="")


class TestGetFullHistory:
    def test_unknown_cliente_returns_empty(self, db_session):
        history = cliente_service.get_full_history(db_session, "Inexistente")
        assert history["codigo"] == ""
        assert history["ventas"] == []
        assert history["pagos"] == []
        assert history["facturado_total"] == 0.0
        assert history["saldo"] == 0.0

    def test_history_with_one_venta_no_pagos(self, db_session):
        c = cliente_service.create(db_session, nombre="Hist1")
        v = Venta(
            num_secuencial=1,
            fecha=date(2026, 4, 1),
            cod_cliente=c.cod_cliente,
            cliente_nombre=c.nombre,
            tipo="Tratamiento",
            cod_item="LIVTRAT0001",
            moneda="PEN",
            total=Decimal("300.00"),
            debe=Decimal("300.00"),
            pagado=Decimal("0.00"),
            descuento=Decimal("0"),
        )
        db_session.add(v)
        db_session.flush()

        h = cliente_service.get_full_history(db_session, "Hist1")
        assert h["codigo"] == c.cod_cliente
        assert len(h["ventas"]) == 1
        assert h["ventas"][0]["DEBE"] == 300.0
        assert h["ventas"][0]["PAGADO"] == 0.0
        assert h["facturado_total"] == 300.0
        assert h["cobrado_total"] == 0.0
        assert h["saldo"] == 300.0
        assert h["credito_disponible"] == 0.0

    def test_history_excludes_credito_aplicado_from_pagos_display(self, db_session):
        c = cliente_service.create(db_session, nombre="Hist2")
        v = Venta(
            num_secuencial=1,
            fecha=date(2026, 4, 1),
            cod_cliente=c.cod_cliente,
            cliente_nombre=c.nombre,
            tipo="Tratamiento",
            cod_item="LIVTRAT0010",
            moneda="PEN",
            total=Decimal("200.00"),
            debe=Decimal("0.00"),
            pagado=Decimal("200.00"),
            descuento=Decimal("0"),
        )
        db_session.add(v)
        db_session.flush()
        # 1 pago normal + 1 credito_aplicado
        db_session.add(Pago(
            cod_pago="LIVPAGO0001",
            num_secuencial=1,
            fecha=date(2026, 4, 2),
            cod_cliente=c.cod_cliente,
            cliente_nombre=c.nombre,
            cod_item="LIVTRAT0010",
            monto=Decimal("150.00"),
            tipo_pago="normal",
        ))
        db_session.add(Pago(
            cod_pago="LIVPAGO0002",
            num_secuencial=2,
            fecha=date(2026, 4, 3),
            cod_cliente=c.cod_cliente,
            cliente_nombre=c.nombre,
            cod_item="LIVTRAT0010",
            monto=Decimal("50.00"),
            tipo_pago="credito_aplicado",
        ))
        db_session.flush()

        h = cliente_service.get_full_history(db_session, "Hist2")
        # cobrado_total NO incluye credito_aplicado (es transferencia interna)
        assert h["cobrado_total"] == 150.0
        # pero el listado de pagos display tampoco lo incluye
        assert len(h["pagos"]) == 1
        # DEBE per item INCLUYE credito_aplicado en el cálculo
        assert h["ventas"][0]["DEBE"] == 0.0  # 200 - 150 (normal) - 50 (credito) = 0
        assert h["ventas"][0]["PAGADO"] == 200.0


class TestUpdate:
    def test_update_partial_fields(self, db_session):
        c = cliente_service.create(db_session, nombre="Upd1", phone_raw="987111111")
        cliente_service.update(
            db_session,
            cod_cliente=c.cod_cliente,
            nombre="Upd1 actualizado",
            email_raw="upd1@test.com",
        )
        updated = cliente_service.get_by_cod(db_session, c.cod_cliente)
        assert updated.nombre == "Upd1 actualizado"
        assert updated.email_lower == "upd1@test.com"
        assert updated.phone_e164 == "+51987111111"  # no se tocó

    def test_update_phone_collision_raises(self, db_session):
        cliente_service.create(db_session, nombre="A", phone_raw="987111111")
        b = cliente_service.create(db_session, nombre="B", phone_raw="987222222")
        with pytest.raises(cliente_service.ClienteDuplicadoError):
            cliente_service.update(db_session, cod_cliente=b.cod_cliente, phone_raw="987111111")

    def test_update_unknown_raises(self, db_session):
        with pytest.raises(cliente_service.ClienteNotFoundError):
            cliente_service.update(db_session, cod_cliente="LIVCLIENT9999", nombre="x")
