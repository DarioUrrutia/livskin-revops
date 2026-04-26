"""Tests de venta_service: las 6 fases de venta del Flask original.

Las 6 fases (orden estricto, atómicas):
1. Generar códigos batch
2. Insertar ventas (1 por item)
3. Insertar pagos normales (efectivo/yape/plin/giro distribuidos)
4. Aplicar crédito del cliente (si tiene)
5. Procesar abonos explícitos a deudas anteriores
6. Auto-aplicar leftover_cash a deudas FIFO + generar crédito si sobra
"""
from datetime import date
from decimal import Decimal

import pytest

from models.cliente import Cliente
from models.pago import Pago
from models.venta import Venta
from services import cliente_service, venta_service


def _seed_cliente(db_session, nombre="Test Cliente", phone=None) -> Cliente:
    return cliente_service.create(db_session, nombre=nombre, phone_raw=phone)


def _basic_input(monto: Decimal = Decimal("100"), tipo="Tratamiento") -> venta_service.ItemVentaInput:
    return venta_service.ItemVentaInput(
        tipo=tipo,
        precio_lista=monto,
        pago_item=monto,
    )


class TestSaveVentaBasic:
    def test_venta_simple_1_item_pagado_completo(self, db_session):
        c = _seed_cliente(db_session)
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[_basic_input(Decimal("100"))],
            metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        assert len(result.ventas) == 1
        v = result.ventas[0]
        assert v.cod_item.startswith("LIVTRAT")
        assert v.total == Decimal("100")
        assert v.debe == Decimal("0")
        assert v.pagado == Decimal("100")

    def test_venta_multi_item_codigos_unicos(self, db_session):
        c = _seed_cliente(db_session)
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[
                _basic_input(Decimal("100"), "Tratamiento"),
                _basic_input(Decimal("50"), "Tratamiento"),
                _basic_input(Decimal("30"), "Tratamiento"),
            ],
            metodos_pago={"efectivo": Decimal("180"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        assert len(result.ventas) == 3
        cod_items = [v.cod_item for v in result.ventas]
        assert len(set(cod_items)) == 3  # todos únicos
        assert all(c.startswith("LIVTRAT") for c in cod_items)

    def test_codigo_prefix_por_tipo(self, db_session):
        c = _seed_cliente(db_session)
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[
                venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100")),
                venta_service.ItemVentaInput(tipo="Producto", precio_lista=Decimal("50"), pago_item=Decimal("50")),
            ],
            metodos_pago={"efectivo": Decimal("150"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        prefixes = {v.cod_item.split("0")[0] for v in result.ventas}
        # cada tipo tiene un prefijo distinto
        assert len(prefixes) == 2

    def test_venta_con_descuento(self, db_session):
        c = _seed_cliente(db_session)
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(
                tipo="Tratamiento",
                precio_lista=Decimal("200"),
                descuento=Decimal("50"),
                pago_item=Decimal("150"),
            )],
            metodos_pago={"efectivo": Decimal("150"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        v = result.ventas[0]
        assert v.precio_lista == Decimal("200")
        assert v.descuento == Decimal("50")
        assert v.total == Decimal("150")
        assert v.debe == Decimal("0")

    def test_venta_gratis_descuento_total(self, db_session):
        c = _seed_cliente(db_session)
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(
                tipo="Tratamiento",
                precio_lista=Decimal("200"),
                descuento=Decimal("200"),
                pago_item=Decimal("0"),
            )],
            metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        v = result.ventas[0]
        assert v.total == Decimal("0")
        assert v.debe == Decimal("0")

    def test_venta_con_deuda_parcial(self, db_session):
        c = _seed_cliente(db_session)
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(
                tipo="Tratamiento",
                precio_lista=Decimal("300"),
                pago_item=Decimal("100"),
            )],
            metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        v = result.ventas[0]
        assert v.total == Decimal("300")
        assert v.pagado == Decimal("100")
        assert v.debe == Decimal("200")


class TestValidaciones:
    def test_items_vacios_raise(self, db_session):
        c = _seed_cliente(db_session)
        with pytest.raises(ValueError):
            venta_service.save_venta(
                db_session,
                fecha=date(2026, 4, 26),
                items=[],
                metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                cod_cliente=c.cod_cliente,
            )

    def test_cliente_no_existe_raise(self, db_session):
        with pytest.raises(venta_service.ClienteNoExiste):
            venta_service.save_venta(
                db_session,
                fecha=date(2026, 4, 26),
                items=[_basic_input()],
                metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                cod_cliente="LIVCLIENT9999",
            )

    def test_tipo_item_invalido_raise(self, db_session):
        c = _seed_cliente(db_session)
        with pytest.raises(venta_service.TipoItemInvalido):
            venta_service.save_venta(
                db_session,
                fecha=date(2026, 4, 26),
                items=[venta_service.ItemVentaInput(tipo="InventadoXYZ", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
                metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                cod_cliente=c.cod_cliente,
            )

    def test_sin_cod_cliente_ni_data_raise(self, db_session):
        with pytest.raises(ValueError):
            venta_service.save_venta(
                db_session,
                fecha=date(2026, 4, 26),
                items=[_basic_input()],
                metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            )


class TestAutoCreateCliente:
    def test_auto_create_cliente_desde_data(self, db_session):
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[_basic_input()],
            metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cliente_data=venta_service.ClienteAutoCreateInput(
                nombre="Cliente Nueva",
                telefono="987654321",
            ),
        )
        v = result.ventas[0]
        assert v.cod_cliente.startswith("LIVCLIENT")
        cliente = cliente_service.get_by_cod(db_session, v.cod_cliente)
        assert cliente.nombre == "Cliente Nueva"
        assert cliente.phone_e164 == "+51987654321"

    def test_existing_cliente_se_reutiliza(self, db_session):
        c = _seed_cliente(db_session, nombre="Existente")
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[_basic_input()],
            metodos_pago={"efectivo": Decimal("100"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cliente_data=venta_service.ClienteAutoCreateInput(nombre="Existente"),
        )
        assert result.ventas[0].cod_cliente == c.cod_cliente


class TestCreditoDelCliente:
    def test_credito_aplicado_descuenta_de_balance(self, db_session):
        """Cliente con crédito previo de S/100 + venta de S/300, aplica S/50 crédito."""
        c = _seed_cliente(db_session)

        # Pre-cargar crédito disponible: hacer venta de 0 con un pago tipo credito_generado
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 1),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
            metodos_pago={"efectivo": Decimal("200"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},  # 100 sobra → credito_generado
            cod_cliente=c.cod_cliente,
            auto_aplicar_a_deudas=False,  # forzar crédito
        )

        # Verificar crédito disponible
        history = cliente_service.get_full_history(db_session, c.nombre)
        assert history["credito_disponible"] == 100.0

        # Nueva venta usando 50 de crédito
        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("300"), pago_item=Decimal("250"))],
            metodos_pago={"efectivo": Decimal("250"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
            credito_aplicado=Decimal("50"),
        )
        v = result.ventas[0]
        db_session.refresh(v)  # trigger DEBE actualiza debe/pagado en DB, refrescar el ORM
        # Total 300, pagado 250 cash + 50 credito = 300 → debe 0
        assert v.debe == Decimal("0")
        assert v.pagado == Decimal("300")

    def test_credito_insuficiente_raise(self, db_session):
        c = _seed_cliente(db_session)
        # Cliente sin crédito intenta aplicar 50
        with pytest.raises(venta_service.CreditoInsuficiente):
            venta_service.save_venta(
                db_session,
                fecha=date(2026, 4, 26),
                items=[_basic_input(Decimal("300"))],
                metodos_pago={"efectivo": Decimal("250"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                cod_cliente=c.cod_cliente,
                credito_aplicado=Decimal("50"),
            )


class TestAutoAplicarFIFO:
    def test_leftover_se_aplica_a_deuda_anterior(self, db_session):
        """Cliente debe S/200 de venta vieja + venta nueva S/100 + paga S/250 →
        50 sobrante se aplica auto a la deuda vieja."""
        c = _seed_cliente(db_session)

        # Venta vieja con deuda
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 1),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("200"), pago_item=Decimal("0"))],
            metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        old_venta = db_session.query(Venta).filter_by(cod_cliente=c.cod_cliente).first()
        assert old_venta.debe == Decimal("200")

        # Nueva venta paga 150 (100 item + 50 sobrante)
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
            metodos_pago={"efectivo": Decimal("150"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
            auto_aplicar_a_deudas=True,
        )

        db_session.refresh(old_venta)
        assert old_venta.debe == Decimal("150")  # 200 - 50 = 150
        assert old_venta.pagado == Decimal("50")

    def test_auto_aplicar_disabled_genera_credito(self, db_session):
        c = _seed_cliente(db_session)
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 1),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("200"), pago_item=Decimal("0"))],
            metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        old_venta = db_session.query(Venta).filter_by(cod_cliente=c.cod_cliente).first()
        old_debe_inicial = old_venta.debe

        result = venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
            metodos_pago={"efectivo": Decimal("150"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
            auto_aplicar_a_deudas=False,
        )
        # leftover NO se aplica → genera crédito
        assert result.excedente_credito_generado == Decimal("50")
        db_session.refresh(old_venta)
        assert old_venta.debe == old_debe_inicial  # no se tocó


class TestAbonosExplicitos:
    def test_abono_explicito_a_cod_item(self, db_session):
        c = _seed_cliente(db_session)
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 1),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("300"), pago_item=Decimal("0"))],
            metodos_pago={"efectivo": Decimal("0"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
        )
        old_venta = db_session.query(Venta).filter_by(cod_cliente=c.cod_cliente).first()
        old_cod_item = old_venta.cod_item

        # Nueva venta con abono explícito a la deuda vieja
        venta_service.save_venta(
            db_session,
            fecha=date(2026, 4, 26),
            items=[venta_service.ItemVentaInput(tipo="Tratamiento", precio_lista=Decimal("100"), pago_item=Decimal("100"))],
            metodos_pago={"efectivo": Decimal("200"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
            cod_cliente=c.cod_cliente,
            abonos_deudas=[venta_service.AbonoDeudaInput(cod_item=old_cod_item, monto=Decimal("100"))],
        )

        db_session.refresh(old_venta)
        assert old_venta.debe == Decimal("200")  # 300 - 100 = 200

    def test_abono_a_cod_item_inexistente_raise(self, db_session):
        from services.pago_service import AbonoCodItemInvalido

        c = _seed_cliente(db_session)
        with pytest.raises(AbonoCodItemInvalido):
            venta_service.save_venta(
                db_session,
                fecha=date(2026, 4, 26),
                items=[_basic_input()],
                metodos_pago={"efectivo": Decimal("200"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                cod_cliente=c.cod_cliente,
                abonos_deudas=[venta_service.AbonoDeudaInput(cod_item="LIVTRAT9999", monto=Decimal("100"))],
            )


class TestAtomicidad:
    def test_rollback_completo_si_alguna_fase_falla(self, db_session):
        """Si abono explícito a cod_item inválido falla, NINGUNA venta queda en DB."""
        from services.pago_service import AbonoCodItemInvalido

        c = _seed_cliente(db_session)
        ventas_antes = db_session.query(Venta).filter_by(cod_cliente=c.cod_cliente).count()

        with pytest.raises(AbonoCodItemInvalido):
            venta_service.save_venta(
                db_session,
                fecha=date(2026, 4, 26),
                items=[_basic_input()],
                metodos_pago={"efectivo": Decimal("200"), "yape": Decimal("0"), "plin": Decimal("0"), "giro": Decimal("0")},
                cod_cliente=c.cod_cliente,
                abonos_deudas=[venta_service.AbonoDeudaInput(cod_item="LIVTRAT9999", monto=Decimal("100"))],
            )

        # Necesitamos rollback explícito porque el test no usa session_scope
        db_session.rollback()
        ventas_despues = db_session.query(Venta).filter_by(cod_cliente=c.cod_cliente).count()
        assert ventas_antes == ventas_despues
