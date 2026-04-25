"""Rutas /api/pagos — pagos día posterior (cliente regresa solo a pagar)."""
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from db import session_scope
from schemas.pago import PagoOut, PagosCreate, PagosSaveResponse
from services import pago_service

bp = Blueprint("api_pagos", __name__)


@bp.post("/api/pagos")
def create_pagos():  # type: ignore[no-untyped-def]
    """Cliente vuelve días después solo a pagar deudas (sin nueva venta).

    Acepta lista de pagos explícitos a cod_items específicos. Si cash recibido
    excede los pagos explícitos:
    - auto_aplicar_a_deudas=true (default): leftover a deudas restantes FIFO
    - auto_aplicar_a_deudas=false: leftover directo a credito_generado
    """
    try:
        body = PagosCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    pagos_input = [
        pago_service.PagoIndividualInput(
            cod_item=p.cod_item,
            monto=p.monto,
            categoria=p.categoria,
            notas=p.notas,
        )
        for p in body.pagos
    ]

    metodos_pago = {
        "efectivo": body.metodos_pago.efectivo,
        "yape": body.metodos_pago.yape,
        "plin": body.metodos_pago.plin,
        "giro": body.metodos_pago.giro,
    }

    try:
        with session_scope() as db:
            result = pago_service.save_pagos_dia_posterior(
                db,
                cod_cliente=body.cod_cliente,
                fecha=body.fecha,
                metodos_pago=metodos_pago,
                pagos_explicitos=pagos_input,
                auto_aplicar_a_deudas=body.auto_aplicar_a_deudas,
                notas=body.notas,
            )

            response_json = PagosSaveResponse(
                cod_cliente=body.cod_cliente,
                fecha=body.fecha,
                pagos=[PagoOut.model_validate(p) for p in result.pagos],
                total_pagos_explicitos=result.total_pagos_explicitos,
                auto_abonos_total=result.auto_abonos_total,
                excedente_credito_generado=result.excedente_credito_generado,
            ).model_dump(mode="json")
    except pago_service.AbonoCodItemInvalido as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(response_json), 201
