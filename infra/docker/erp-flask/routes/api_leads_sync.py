"""Route POST /api/leads/sync-from-vtiger — espejo Vtiger Lead → ERP.

Recibe payload de n8n Workflow [B1] (Vtiger lead on-change).
Auth: shared secret X-Internal-Token (mismo patrón que /api/internal/audit-event).

Idempotencia: por `vtiger_id`. CREATE si no existe, UPDATE si sí.
At_capture fields (first-touch attribution) inmutables en UPDATE.
"""
from flask import Blueprint, abort, jsonify, request
from pydantic import ValidationError

from db import session_scope
from schemas.lead_sync import LeadSyncRequest, LeadSyncResponse
from services import audit_service, capi_emitter_service, lead_sync_service

bp = Blueprint("api_leads_sync", __name__, url_prefix="/api/leads")


def _check_internal_token() -> None:
    """403 si X-Internal-Token no coincide con settings."""
    from config import settings

    expected = getattr(settings, "audit_internal_token", None)
    if not expected:
        abort(503, description="audit_internal_token no configurado")
    received = request.headers.get("X-Internal-Token", "")
    if received != expected:
        abort(403, description="X-Internal-Token inválido")


@bp.post("/sync-from-vtiger")
def sync_from_vtiger():  # type: ignore[no-untyped-def]
    """Recibe Vtiger Lead data y espeja a livskin_erp.leads.

    Body JSON: schema LeadSyncRequest (ver schemas/lead_sync.py).
    Returns 200 con LeadSyncResponse.
    """
    _check_internal_token()

    raw = request.get_json(silent=True) or {}
    try:
        payload = LeadSyncRequest(**raw)
    except ValidationError as e:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "validation_error",
                    "details": [
                        {"field": ".".join(str(x) for x in err["loc"]), "msg": err["msg"]}
                        for err in e.errors()
                    ],
                }
            ),
            400,
        )

    raw_xff = request.headers.get("X-Forwarded-For", "") or ""
    client_ip = raw_xff.split(",")[0].strip() if raw_xff else (request.remote_addr or None)

    try:
        with session_scope() as db:
            lead, operation = lead_sync_service.upsert_lead(db, payload)
            audit_service.log(
                db,
                action="lead.synced_from_vtiger",
                entity_type="lead",
                entity_id=str(lead.id),
                metadata={
                    "vtiger_id": payload.vtiger_id,
                    "lead_id": lead.id,
                    "cod_lead": lead.cod_lead,
                    "operation": operation,
                    "source": "n8n-B1",
                },
                user_username="n8n-workflow-b1",
                user_role="system",
                ip=client_ip,
            )

            # Mini-bloque 3.4 — auto-emit Meta CAPI Lead event SOLO en CREATE.
            # ADR-0019 § 6: event_id coherente con Pixel client-side firing.
            # Non-blocking: fallo de n8n NO rompe el sync (capi_emitter loguea audit).
            if operation == "created" and lead.event_id_at_capture:
                capi_emitter_service.emit_event(
                    db,
                    event_name="Lead",
                    event_id=lead.event_id_at_capture,
                    event_source_url="https://livskin.site/",
                    email=lead.email_lower,
                    phone_e164=lead.phone_e164,
                    fbc=lead.fbc_at_capture,
                    external_id=lead.cod_lead,
                    content_name=lead.tratamiento_interes,
                    content_category="lead_acquisition",
                    trigger_entity_type="lead",
                    trigger_entity_id=str(lead.id),
                )

            response = LeadSyncResponse(
                operation=operation,
                vtiger_id=payload.vtiger_id,
                lead_id=lead.id,
                cod_lead=lead.cod_lead,
            )
        return jsonify(response.model_dump()), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "internal", "detail": str(e)}), 500


def register_public_endpoints() -> None:
    """Marca el endpoint como público (auth-middleware skip)."""
    from middleware.auth_middleware import PUBLIC_ENDPOINTS

    PUBLIC_ENDPOINTS.add("api_leads_sync.sync_from_vtiger")
