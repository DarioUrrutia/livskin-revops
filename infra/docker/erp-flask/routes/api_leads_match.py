"""Route GET /api/leads/search-match — match automático lead→cliente al crear cliente.

ADR-0033 — usado por la UI de la pestaña CLIENTE en el ERP. Cuando la doctora
está creando un cliente walk-in, el frontend llama a este endpoint con
phone/email/nombre debounced para detectar si hay un lead reciente NO convertido
que pueda corresponder. Si hay match único, el frontend muestra un tip con
botón "Vincular" / "Descartar".

Auth: session-based (admin/operadora).

Feature flag: settings.auto_match_lead_enabled. Si False → 404 (UI tip nunca aparece).
"""
from flask import Blueprint, jsonify, request

from config import settings
from db import session_scope
from services import cliente_service

bp = Blueprint("api_leads_match", __name__)


@bp.get("/api/leads/search-match")
def search_lead_match():  # type: ignore[no-untyped-def]
    if not settings.auto_match_lead_enabled:
        return jsonify({"error": "feature disabled"}), 404

    phone = request.args.get("phone", "").strip() or None
    email = request.args.get("email", "").strip() or None
    nombre = request.args.get("nombre", "").strip() or None

    with session_scope() as db:
        lead = cliente_service.search_lead_match(
            db,
            phone_raw=phone,
            email_raw=email,
            nombre=nombre,
        )

        if lead is None:
            return jsonify({"match": None}), 200

        match = {
            "cod_lead": lead.cod_lead,
            "vtiger_lead_id": lead.vtiger_id,
            "nombre": lead.nombre,
            "phone_e164": lead.phone_e164,
            "email_lower": lead.email_lower,
            "fuente": lead.fuente,
            "canal_adquisicion": lead.canal_adquisicion,
            "fecha_captura": (
                lead.fecha_captura.isoformat() if lead.fecha_captura else None
            ),
            "tratamiento_interes": lead.tratamiento_interes,
            "utm_source": lead.utm_source_at_capture,
            "utm_campaign": lead.utm_campaign_at_capture,
        }

    return jsonify({"match": match}), 200
