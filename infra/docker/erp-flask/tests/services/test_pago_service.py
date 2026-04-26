"""Tests de pago_service: 4 tipos de pago + día posterior + abono fantasma."""
from datetime import date
from decimal import Decimal

import pytest

from models.cliente import Cliente
from models.pago import Pago
from models.venta import Venta
from services import cliente_service, pago_service, venta_service


def _seed_cliente_con_venta(db_session, debe=Decimal("0")) -> tuple[Cliente, Venta]:
    """Cliente + 1 venta opcionalmente con deuda."""
    c = cliente_service.create(db_session, nombre="PagoTest")
    pago_inicial = Decimal("100") - debe
    result = venta_service.save_venta(
        db_session,
        fecha=date(2026, 4, 1),
        items=[venta_service.ItemVentaInput(
            tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=pago_inicial
        )],
        metodos_pago={"efectivo": pago_inicial, "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
        cod_cliente=c.cod_cliente,
    )
    return c, result.ventas[0]


class TestCreatePago:
    def test_pago_normal_basic(self, db_session):
        c, v = _seed_cliente_con_venta(db_session, debe=Decimal("50"))
        p = pago_service.create_pago(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 26),
            monto=Decimal("50"),
            tipo_pago="normal",
            cod_item=v.cod_item,
        )
        assert p.cod_pago.startswith("LIVPAGO")
        assert p.tipo_pago == "normal"

    def test_pago_tipo_invalido_raise(self, db_session):
        c, _ = _seed_cliente_con_venta(db_session)
        with pytest.raises(pago_service.PagoTipoInvalido):
            pago_service.create_pago(
                db_session,
                cod_cliente=c.cod_cliente,
                fecha=date(2026, 4, 26),
                monto=Decimal("10"),
                tipo_pago="inventado",
            )

    def test_abono_fantasma_raise(self, db_session):
        """Abono a cod_item que no existe en ventas → AbonoCodItemInvalido."""
        c, _ = _seed_cliente_con_venta(db_session)
        with pytest.raises(pago_service.AbonoCodItemInvalido):
            pago_service.create_pago(
                db_session,
                cod_cliente=c.cod_cliente,
                fecha=date(2026, 4, 26),
                monto=Decimal("50"),
                tipo_pago="abono_deuda",
                cod_item="LIVTRAT9999",
            )


class TestSavePagosDiaPosterior:
    def test_pago_explicito_a_deuda_existente(self, db_session):
        c, v = _seed_cliente_con_venta(db_session, debe=Decimal("80"))
        result = pago_service.save_pagos_dia_posterior(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 26),
            metodos_pago={"efectivo": Decimal("80"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            pagos_explicitos=[
                pago_service.PagoIndividualInput(cod_item=v.cod_item, monto=Decimal("80")),
            ],
        )
        assert len(result.pagos) == 1
        assert result.total_pagos_explicitos == Decimal("80")
        assert result.excedente_credito_generado == Decimal("0")
        db_session.refresh(v)
        assert v.debe == Decimal("0")

    def test_excedente_genera_credito(self, db_session):
        c, v = _seed_cliente_con_venta(db_session, debe=Decimal("50"))
        result = pago_service.save_pagos_dia_posterior(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 26),
            metodos_pago={"efectivo": Decimal("80"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            pagos_explicitos=[
                pago_service.PagoIndividualInput(cod_item=v.cod_item, monto=Decimal("50")),
            ],
            auto_aplicar_a_deudas=False,
        )
        assert result.excedente_credito_generado == Decimal("30")
        # Verificar que existe un pago tipo credito_generado
        creditos = [p for p in result.pagos if p.tipo_pago == "credito_generado"]
        assert len(creditos) == 1
        assert creditos[0].monto == Decimal("30")

    def test_auto_aplicar_a_deuda_anterior(self, db_session):
        c = cliente_service.create(db_session, nombre="AutoApply")
        # Crear 2 ventas con deuda en distintos cod_item
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 1),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("0"))],
            metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 5),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("80"), pago_item=Decimal("0"))],
            metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )

        result = pago_service.save_pagos_dia_posterior(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 26),
            metodos_pago={"efectivo": Decimal("130"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            pagos_explicitos=[],
        )
        # leftover = 130 → debería distribuirse FIFO entre las 2 ventas (100 + 30 a la segunda)
        assert result.auto_abonos_total == Decimal("130")
        ventas = db_session.query(Venta).filter_by(cod_cliente=c.cod_cliente).order_by(Venta.fecha).all()
        assert ventas[0].debe == Decimal("0")
        assert ventas[1].debe == Decimal("50")  # 80 - 30

    def test_cliente_inexistente_raise(self, db_session):
        with pytest.raises(ValueError):
            pago_service.save_pagos_dia_posterior(
                db_session,
                cod_cliente="LIVCLIENT9999",
                fecha=date(2026, 4, 26),
                metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                pagos_explicitos=[],
            )

    def test_total_pagado_zero_raise(self, db_session):
        c, _ = _seed_cliente_con_venta(db_session)
        with pytest.raises(ValueError):
            pago_service.save_pagos_dia_posterior(
                db_session,
                cod_cliente=c.cod_cliente,
                fecha=date(2026, 4, 26),
                metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                pagos_explicitos=[],
            )

    def test_explicitos_exceden_cash_raise(self, db_session):
        c, v = _seed_cliente_con_venta(db_session, debe=Decimal("100"))
        with pytest.raises(ValueError):
            pago_service.save_pagos_dia_posterior(
                db_session,
                cod_cliente=c.cod_cliente,
                fecha=date(2026, 4, 26),
                metodos_pago={"efectivo": Decimal("50"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                pagos_explicitos=[
                    pago_service.PagoIndividualInput(cod_item=v.cod_item, monto=Decimal("100")),
                ],
            )


class TestCreditoBalance:
    def test_balance_zero_sin_pagos(self, db_session):
        c = cliente_service.create(db_session, nombre="ZeroCredit")
        assert pago_service.credito_balance(db_session, c.cod_cliente) == Decimal("0")

    def test_balance_solo_credito_generado(self, db_session):
        c = cliente_service.create(db_session, nombre="OnlyGen")
        pago_service.create_pago(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 1),
            monto=Decimal("50"),
            tipo_pago="credito_generado",
            cliente_nombre=c.nombre,
        )
        assert pago_service.credito_balance(db_session, c.cod_cliente) == Decimal("50")

    def test_balance_genera_y_aplica(self, db_session):
        c = cliente_service.create(db_session, nombre="GenAp")
        pago_service.create_pago(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 1),
            monto=Decimal("100"),
            tipo_pago="credito_generado",
        )
        pago_service.create_pago(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 5),
            monto=Decimal("30"),
            tipo_pago="credito_aplicado",
        )
        assert pago_service.credito_balance(db_session, c.cod_cliente) == Decimal("70")


class TestTotalPagadoForItem:
    def test_total_pagado_incluye_todos_los_tipos(self, db_session):
        c, v = _seed_cliente_con_venta(db_session, debe=Decimal("80"))
        # Pago normal
        pago_service.create_pago(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 5),
            monto=Decimal("30"),
            tipo_pago="abono_deuda",
            cod_item=v.cod_item,
        )
        # Crédito aplicado al mismo item
        pago_service.create_pago(
            db_session,
            cod_cliente=c.cod_cliente,
            fecha=date(2026, 4, 6),
            monto=Decimal("20"),
            tipo_pago="credito_aplicado",
            cod_item=v.cod_item,
        )
        # Pago inicial fue Decimal("20") (100 - debe 80) durante el seed
        # Suma total = 20 (inicial) + 30 + 20 = 70
        total = pago_service.total_pagado_for_item(db_session, v.cod_item)
        assert total == Decimal("70")
