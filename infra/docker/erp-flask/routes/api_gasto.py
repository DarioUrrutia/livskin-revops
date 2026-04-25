"""Rutas /api/gastos — CRUD de gastos."""
from datetime import date
from typing import Optional

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from db import session_scope
from schemas.gasto import GastoCreate, GastoListResponse, GastoOut
from services import gasto_service

bp = Blueprint("api_gasto", __name__)


@bp.get("/api/gastos")
def list_gastos():  # type: ignore[no-untyped-def]
    try:
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        return jsonify({"error": "limit/offset inválidos"}), 400

    fecha_desde_raw = request.args.get("fecha_desde")
    fecha_desde: Optional[date] = None
    if fecha_desde_raw:
        try:
            fecha_desde = date.fromisoformat(fecha_desde_raw)
        except ValueError:
            return jsonify({"error": "fecha_desde inválida (formato YYYY-MM-DD)"}), 400

    with session_scope() as db:
        gastos = gasto_service.list_recent(db, limit=limit, offset=offset, fecha_desde=fecha_desde)
        items = [GastoOut.model_validate(g) for g in gastos]
        response_json = GastoListResponse(
            items=items, limit=limit, offset=offset, count=len(items)
        ).model_dump(mode="json")

    return jsonify(response_json), 200


@bp.post("/api/gastos")
def create_gasto():  # type: ignore[no-untyped-def]
    try:
        body = GastoCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    with session_scope() as db:
        gasto = gasto_service.create(
            db,
            fecha=body.fecha,
            monto=body.monto,
            tipo=body.tipo,
            descripcion=body.descripcion,
            destinatario=body.destinatario,
            metodo_pago=body.metodo_pago,
            notas=body.notas,
        )
        response_json = GastoOut.model_validate(gasto).model_dump(mode="json")

    return jsonify(response_json), 201
