"""Rutas /api/clientes — CRUD del Cliente (ADR-0011 v1.1).

Sin auth en MVP — agregar @authenticated cuando se implemente middleware ADR-0026.
"""
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from db import session_scope
from schemas.cliente import (
    ClienteCreate,
    ClienteFull,
    ClienteListItem,
    ClienteListResponse,
    ClienteUpdate,
)
from services import cliente_service

bp = Blueprint("api_cliente", __name__)


@bp.get("/api/clientes")
def list_clientes():  # type: ignore[no-untyped-def]
    try:
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        return jsonify({"error": "limit/offset inválidos"}), 400

    with session_scope() as db:
        clientes = cliente_service.list_active(db, limit=limit, offset=offset)
        items = [ClienteListItem.model_validate(c) for c in clientes]

    return jsonify(
        ClienteListResponse(items=items, limit=limit, offset=offset, count=len(items)).model_dump(
            mode="json"
        )
    ), 200


@bp.get("/api/clientes/<cod_cliente>")
def get_cliente(cod_cliente: str):  # type: ignore[no-untyped-def]
    with session_scope() as db:
        try:
            cliente = cliente_service.get_by_cod(db, cod_cliente)
        except cliente_service.ClienteNotFoundError as e:
            return jsonify({"error": str(e)}), 404

        result = ClienteFull.model_validate(cliente)

    return jsonify(result.model_dump(mode="json")), 200


@bp.post("/api/clientes")
def create_cliente():  # type: ignore[no-untyped-def]
    try:
        body = ClienteCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    with session_scope() as db:
        try:
            cliente = cliente_service.create(
                db,
                nombre=body.nombre,
                phone_raw=body.phone,
                email_raw=body.email,
                fecha_nacimiento=body.fecha_nacimiento,
                fuente=body.fuente,
                canal_adquisicion=body.canal_adquisicion,
                tratamiento_interes=body.tratamiento_interes,
                consent_marketing=body.consent_marketing,
                notas=body.notas,
            )
        except cliente_service.ClienteDuplicadoError as e:
            return jsonify({"error": str(e)}), 409

        result = ClienteFull.model_validate(cliente)

    return jsonify(result.model_dump(mode="json")), 201


@bp.put("/api/clientes/<cod_cliente>")
def update_cliente(cod_cliente: str):  # type: ignore[no-untyped-def]
    try:
        body = ClienteUpdate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    with session_scope() as db:
        try:
            cliente = cliente_service.update(
                db,
                cod_cliente=cod_cliente,
                nombre=body.nombre,
                phone_raw=body.phone,
                email_raw=body.email,
                fecha_nacimiento=body.fecha_nacimiento,
                tratamiento_interes=body.tratamiento_interes,
                consent_marketing=body.consent_marketing,
                notas=body.notas,
            )
        except cliente_service.ClienteNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except cliente_service.ClienteDuplicadoError as e:
            return jsonify({"error": str(e)}), 409

        result = ClienteFull.model_validate(cliente)

    return jsonify(result.model_dump(mode="json")), 200
