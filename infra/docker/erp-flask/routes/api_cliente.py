"""Rutas /api/clientes — CRUD del Cliente (ADR-0011 v1.1)."""
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
from services import audit_service, cliente_service

bp = Blueprint("api_cliente", __name__)


@bp.get("/cliente")
def get_cliente_history():  # type: ignore[no-untyped-def]
    """Historial completo del cliente — preserva contrato del Flask original.

    GET /cliente?nombre=Carmen+Lopez
    Retorna: { codigo, nombre, telefono, email, cumpleanos, ventas, pagos,
               facturado_total, cobrado_total, saldo, credito_disponible }

    DEBE de cada venta se RECALCULA dinámicamente desde pagos_por_cod_item
    (excluyendo credito_aplicado). Si no existe el cliente, retorna estructura
    vacía (no error) — el form legacy lo trata como "cliente nuevo".
    """
    nombre = request.args.get("nombre", "").strip()
    with session_scope() as db:
        result = cliente_service.get_full_history(db, nombre)
    return jsonify(result), 200


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
        response_json = ClienteListResponse(
            items=items, limit=limit, offset=offset, count=len(items)
        ).model_dump(mode="json")

    return jsonify(response_json), 200


@bp.get("/api/clientes/<cod_cliente>")
def get_cliente(cod_cliente: str):  # type: ignore[no-untyped-def]
    try:
        with session_scope() as db:
            cliente = cliente_service.get_by_cod(db, cod_cliente)
            response_json = ClienteFull.model_validate(cliente).model_dump(mode="json")
    except cliente_service.ClienteNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify(response_json), 200


@bp.post("/api/clientes")
def create_cliente():  # type: ignore[no-untyped-def]
    try:
        body = ClienteCreate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    try:
        with session_scope() as db:
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
                cod_lead_origen=body.cod_lead_origen,
            )
            response_json = ClienteFull.model_validate(cliente).model_dump(mode="json")
            # ADR-0033: audit event canónico según vinculación
            if body.cod_lead_origen:
                audit_service.log(
                    db,
                    action="cliente.created_with_lead_match",
                    entity_type="cliente",
                    entity_id=cliente.cod_cliente,
                    after_state={
                        "cod_cliente": cliente.cod_cliente,
                        "cod_lead_origen": cliente.cod_lead_origen,
                        "vtiger_lead_id_origen": cliente.vtiger_lead_id_origen,
                        "match_confirmed_in": "api_clientes",
                    },
                )
            else:
                audit_service.log(
                    db,
                    action="cliente.created_walk_in",
                    entity_type="cliente",
                    entity_id=cliente.cod_cliente,
                    after_state={"cod_cliente": cliente.cod_cliente},
                )
    except cliente_service.ClienteDuplicadoError as e:
        return jsonify({"error": str(e)}), 409
    except cliente_service.LeadOrigenNotFoundError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(response_json), 201


@bp.put("/api/clientes/<cod_cliente>")
def update_cliente(cod_cliente: str):  # type: ignore[no-untyped-def]
    try:
        body = ClienteUpdate.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    try:
        with session_scope() as db:
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
            response_json = ClienteFull.model_validate(cliente).model_dump(mode="json")
    except cliente_service.ClienteNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except cliente_service.ClienteDuplicadoError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(response_json), 200
