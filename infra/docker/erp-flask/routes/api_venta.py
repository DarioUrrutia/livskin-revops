"""Rutas /api/ventas — las 6 fases del Flask preservadas."""
from decimal import Decimal

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from db import session_scope
from schemas.venta import PagoOut, VentaCreate, VentaItemOut, VentaSaveResponse, VentaSimpleOut
from services import pago_service, venta_service

bp = Blueprint("api_venta", __name__)


@bp.post("/api/ventas")
def create_venta():  # type: ignore[no-untyped-def]
    try:
        body = VentaCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    items_input = [
        venta_service.ItemVentaInput(
            tipo=it.tipo,
            categoria=it.categoria,
            zona_cantidad_envase=it.zona_cantidad_envase,
            precio_lista=it.precio_lista,
            descuento=it.descuento or Decimal("0"),
            pago_item=it.pago_item or Decimal("0"),
            proxima_cita=it.proxima_cita,
            notas=it.notas,
        )
        for it in body.items
    ]

    abonos_input = [
        venta_service.AbonoDeudaInput(
            cod_item=a.cod_item, monto=a.monto, notas=a.notas
        )
        for a in body.abonos_deudas
    ]

    metodos_pago = {
        "efectivo": body.metodos_pago.efectivo,
        "yape": body.metodos_pago.yape,
        "plin": body.metodos_pago.plin,
        "giro": body.metodos_pago.giro,
    }

    with session_scope() as db:
        try:
            result = venta_service.save_venta(
                db,
                cod_cliente=body.cod_cliente,
                fecha=body.fecha,
                items=items_input,
                metodos_pago=metodos_pago,
                credito_aplicado=body.credito_aplicado or Decimal("0"),
                abonos_deudas=abonos_input,
                moneda=body.moneda,
                tc=body.tc,
            )
        except venta_service.ClienteNoExiste as e:
            return jsonify({"error": str(e)}), 404
        except venta_service.CreditoInsuficiente as e:
            return jsonify({"error": str(e)}), 409
        except pago_service.AbonoCodItemInvalido as e:
            return jsonify({"error": str(e)}), 400
        except (venta_service.TipoItemInvalido, ValueError) as e:
            return jsonify({"error": str(e)}), 400

        response = VentaSaveResponse(
            cod_cliente=body.cod_cliente,
            fecha=body.fecha,
            ventas=[VentaItemOut.model_validate(v) for v in result.ventas],
            pagos=[PagoOut.model_validate(p) for p in result.pagos],
            total_venta=result.total_venta,
            total_pagado=result.total_pagado,
            excedente_credito_generado=result.excedente_credito_generado,
            credito_aplicado=result.credito_aplicado,
            abonos_deudas=result.abonos_deudas,
        )

    return jsonify(response.model_dump(mode="json")), 201


@bp.get("/api/ventas/cliente/<cod_cliente>")
def list_by_cliente(cod_cliente: str):  # type: ignore[no-untyped-def]
    with session_scope() as db:
        ventas = venta_service.list_by_cliente(db, cod_cliente)
        items = [VentaSimpleOut.model_validate(v) for v in ventas]
    return jsonify({"cod_cliente": cod_cliente, "ventas": [i.model_dump(mode="json") for i in items], "count": len(items)}), 200
