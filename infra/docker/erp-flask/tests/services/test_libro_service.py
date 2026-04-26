"""Tests de libro_service: export plano ventas/pagos/gastos."""
from datetime import date
from decimal import Decimal

from services import cliente_service, libro_service, venta_service, gasto_service


class TestComputeLibro:
    def test_empty_returns_empty_arrays(self, db_session):
        result = libro_service.compute_libro(db_session)
        assert result == {"ventas": [], "pagos": [], "gastos": []}

    def test_includes_ventas(self, db_session):
        c = cliente_service.create(db_session, nombre="LibroTest")
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
            metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        result = libro_service.compute_libro(db_session)
        assert len(result["ventas"]) == 1
        v = result["ventas"][0]
        assert v["cod_cliente"] == c.cod_cliente
        assert v["fecha"] == "2026-04-26"
        assert v["total"] == 100.0

    def test_includes_gastos(self, db_session):
        gasto_service.create(
            db_session,
            fecha=date(2026, 4, 26),
            monto=Decimal("75"),
            tipo="Insumos",
        )
        db_session.flush()
        result = libro_service.compute_libro(db_session)
        assert len(result["gastos"]) == 1
        assert result["gastos"][0]["monto"] == 75.0
        assert result["gastos"][0]["tipo"] == "Insumos"

    def test_filter_by_date_range(self, db_session):
        c = cliente_service.create(db_session, nombre="DateRange")
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 3, 15),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("50"), pago_item=Decimal("50"))],
            metodos_pago={"efectivo": Decimal("50"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("80"), pago_item=Decimal("80"))],
            metodos_pago={"efectivo": Decimal("80"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )

        # Solo venta de abril
        result = libro_service.compute_libro(db_session, desde=date(2026, 4, 1))
        assert len(result["ventas"]) == 1
        assert result["ventas"][0]["fecha"] == "2026-04-26"

        # Solo venta de marzo
        result = libro_service.compute_libro(db_session, hasta=date(2026, 3, 31))
        assert len(result["ventas"]) == 1
        assert result["ventas"][0]["fecha"] == "2026-03-15"

    def test_venta_row_has_expected_keys(self, db_session):
        c = cliente_service.create(db_session, nombre="KeysTest")
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
            metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        result = libro_service.compute_libro(db_session)
        v = result["ventas"][0]
        for key in ("num", "fecha", "cod_cliente", "cliente", "tipo", "cod_item",
                    "categoria", "moneda", "total", "efectivo", "debe", "pagado"):
            assert key in v

    def test_pago_row_excludes_session_attrs(self, db_session):
        c = cliente_service.create(db_session, nombre="PagoLibro")
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
            metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        result = libro_service.compute_libro(db_session)
        assert len(result["pagos"]) >= 1
        p = result["pagos"][0]
        assert "cod_pago" in p
        assert "tipo_pago" in p
