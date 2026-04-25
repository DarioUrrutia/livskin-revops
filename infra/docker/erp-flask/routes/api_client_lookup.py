"""Route /api/client-lookup — bridge digital→físico.

GET /api/client-lookup?phone=+51987654321
Retorna match a Cliente existente o Lead activo, o 'none' si no encuentra.

NO requiere auth en MVP (futuras sesiones añaden @authenticated cuando se
implemente middleware ADR-0026).
"""
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

from db import session_scope
from schemas.client_lookup import ClienteShort, ClientLookupResponse, LeadShort
from services.client_lookup_service import lookup_by_phone

bp = Blueprint("api_client_lookup", __name__)


@bp.get("/api/client-lookup")
def client_lookup():  # type: ignore[no-untyped-def]
    phone = request.args.get("phone", "").strip()
    if not phone:
        return jsonify({"error": "phone parameter required"}), 400

    with session_scope() as db:
        result = lookup_by_phone(db, phone)

        response = ClientLookupResponse(
            phone_input=result.phone_input,
            phone_e164=result.phone_e164,
            match_type=result.match_type,  # type: ignore[arg-type]
            cliente=ClienteShort.model_validate(result.cliente) if result.cliente else None,
            lead=LeadShort.model_validate(result.lead) if result.lead else None,
        )

    return jsonify(response.model_dump(mode="json")), 200
