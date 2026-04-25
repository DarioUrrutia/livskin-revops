"""Rutas /api/catalogos — listas editables + admin."""
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from db import session_scope
from schemas.catalogo import (
    CatalogoAddRequest,
    CatalogoItem,
    CatalogoListResponse,
    CatalogoSeedResponse,
)
from services import catalogo_service

bp = Blueprint("api_catalogo", __name__)


@bp.get("/api/catalogos")
def list_listas():  # type: ignore[no-untyped-def]
    with session_scope() as db:
        listas = catalogo_service.all_listas(db)
    return jsonify({"listas": listas, "count": len(listas)}), 200


@bp.get("/api/catalogos/<lista>")
def get_catalogo(lista: str):  # type: ignore[no-untyped-def]
    only_active = request.args.get("only_active", "true").lower() != "false"
    with session_scope() as db:
        items = catalogo_service.get_by_lista(db, lista, only_active=only_active)
        items_out = [CatalogoItem.model_validate(c) for c in items]
    return jsonify(
        CatalogoListResponse(lista=lista, items=items_out, count=len(items_out)).model_dump(
            mode="json"
        )
    ), 200


@bp.post("/api/catalogos")
def add_valor():  # type: ignore[no-untyped-def]
    try:
        body = CatalogoAddRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validacion fallida", "detalle": e.errors()}), 400

    with session_scope() as db:
        try:
            cat = catalogo_service.add_valor(db, body.lista, body.valor, body.orden)
        except catalogo_service.CatalogoDuplicadoError as e:
            return jsonify({"error": str(e)}), 409
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        result = CatalogoItem.model_validate(cat)
    return jsonify(result.model_dump(mode="json")), 201


@bp.post("/api/catalogos/<int:cat_id>/deactivate")
def deactivate(cat_id: int):  # type: ignore[no-untyped-def]
    with session_scope() as db:
        try:
            cat = catalogo_service.deactivate(db, cat_id)
        except catalogo_service.CatalogoNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        result = CatalogoItem.model_validate(cat)
    return jsonify(result.model_dump(mode="json")), 200


@bp.post("/api/catalogos/<int:cat_id>/reactivate")
def reactivate(cat_id: int):  # type: ignore[no-untyped-def]
    with session_scope() as db:
        try:
            cat = catalogo_service.reactivate(db, cat_id)
        except catalogo_service.CatalogoNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        result = CatalogoItem.model_validate(cat)
    return jsonify(result.model_dump(mode="json")), 200


@bp.post("/admin/catalogos/seed")
def seed_initial():  # type: ignore[no-untyped-def]
    """Idempotente: pobla catálogos con valores hardcoded + Excel.
    Útil al inicializar el sistema. Re-correr no duplica.
    """
    with session_scope() as db:
        inserted = catalogo_service.seed_initial(db)
        total = sum(inserted.values())

    return jsonify(
        CatalogoSeedResponse(inserted=inserted, total_inserted=total).model_dump(mode="json")
    ), 200
