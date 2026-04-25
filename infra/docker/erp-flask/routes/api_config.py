"""Route /api/config — preserva contrato HTTP del Flask original.

Frontend (formulario.html) hace GET /api/config al cargar y espera dict
{lista: [valores activos]}. Usado para poblar selects de tipo, categoria,
área, etc.
"""
from flask import Blueprint, jsonify

from db import session_scope
from services import catalogo_service

bp = Blueprint("api_config", __name__)


@bp.get("/api/config")
def get_config():  # type: ignore[no-untyped-def]
    with session_scope() as db:
        config = catalogo_service.get_config_dict(db)
    return jsonify(config), 200
