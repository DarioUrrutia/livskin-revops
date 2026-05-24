"""Routes internas para wa_conversation_state (cross-VPS desde n8n).

Endpoints:
- GET  /api/internal/wa-state?phone=+51947... → devuelve state row o {} si no existe
- POST /api/internal/wa-state → UPSERT (insert si no existe, update si sí)

Auth: X-Internal-Token header con audit_internal_token de settings.

Diseñado para n8n d1-wa-handoff-v2 — consulta state + persiste tras procesar inbound.
"""
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import select

from db import session_scope
from middleware.auth_middleware import PUBLIC_ENDPOINTS


bp = Blueprint("api_internal_wa_state", __name__, url_prefix="/api/internal/wa-state")


def register_public_endpoints() -> None:
    """Llamar desde app.py para que estos endpoints no requieran login bcrypt."""
    PUBLIC_ENDPOINTS.add("api_internal_wa_state.get_state")
    PUBLIC_ENDPOINTS.add("api_internal_wa_state.upsert_state")


def _check_internal_token() -> None:
    """Aborta con 403 si el header X-Internal-Token no coincide con settings."""
    from config import settings

    expected = getattr(settings, "audit_internal_token", None)
    if not expected:
        abort(503, description="audit_internal_token no configurado")

    received = request.headers.get("X-Internal-Token", "")
    if received != expected:
        abort(403, description="X-Internal-Token inválido")


def _row_to_dict(row: Any) -> dict[str, Any]:
    """Serializa una row de wa_conversation_state a dict JSON-safe."""
    if not row:
        return {}
    return {
        "id": row.id,
        "phone_lead": row.phone_lead,
        "state": row.state,
        "last_intent": row.last_intent,
        "context_json": row.context_json or {},
        "last_inbound_text": row.last_inbound_text,
        "last_inbound_at": row.last_inbound_at.isoformat() if row.last_inbound_at else None,
        "last_outbound_text": row.last_outbound_text,
        "last_outbound_at": row.last_outbound_at.isoformat() if row.last_outbound_at else None,
        "message_count_inbound": row.message_count_inbound or 0,
        "message_count_outbound": row.message_count_outbound or 0,
        "lead_id": row.lead_id,
        "vtiger_lead_id": row.vtiger_lead_id,
        "escalated_at": row.escalated_at.isoformat() if row.escalated_at else None,
        "escalation_reason": row.escalation_reason,
        "escalation_to": row.escalation_to,
        "started_at": row.started_at.isoformat() if row.started_at else None,
    }


@bp.get("")
def get_state():  # type: ignore[no-untyped-def]
    """GET /api/internal/wa-state?phone=+51947...

    Devuelve la row activa (state != 'closed') del phone_lead, o {} si no existe.
    """
    _check_internal_token()

    phone = request.args.get("phone", "").strip()
    if not phone:
        abort(400, description="phone query param requerido")

    from models.wa_conversation_state import WaConversationState

    with session_scope() as db:
        row = db.execute(
            select(WaConversationState)
            .where(WaConversationState.phone_lead == phone)
            .where(WaConversationState.state != "closed")
            .order_by(WaConversationState.id.desc())
            .limit(1)
        ).scalar_one_or_none()

        return jsonify(_row_to_dict(row))


@bp.post("")
def upsert_state():  # type: ignore[no-untyped-def]
    """POST /api/internal/wa-state

    Body JSON:
    {
      "phone_lead": "+51947...",        # required
      "state": "qualifying_q1",          # required
      "last_intent": "botox",            # opcional (q1_treatment)
      "context_json": {...},             # opcional (q1/q2/q3 data + flags)
      "last_inbound_text": "...",        # opcional
      "last_outbound_text": "...",       # opcional
      "increment_inbound_count": true,   # default false
      "increment_outbound_count": true,  # default false
      "escalation_reason": "...",        # opcional, setea escalated_at = now
      "escalation_to": "dario|doctora",  # opcional
      "lead_id": 123,                    # opcional, set cuando se crea Lead en ERP
      "vtiger_lead_id": "10x72"          # opcional
    }

    UPSERT: si phone_lead+state activo no existe → INSERT. Si existe → UPDATE.
    Returns: la row resultante serializada.
    """
    _check_internal_token()

    payload = request.get_json(silent=True) or {}
    phone = (payload.get("phone_lead") or "").strip()
    state = (payload.get("state") or "").strip()

    if not phone:
        abort(400, description="phone_lead requerido en body")
    if not state:
        abort(400, description="state requerido en body")

    from models.wa_conversation_state import WaConversationState

    with session_scope() as db:
        # Buscar row activa (no closed) existente
        existing = db.execute(
            select(WaConversationState)
            .where(WaConversationState.phone_lead == phone)
            .where(WaConversationState.state != "closed")
            .order_by(WaConversationState.id.desc())
            .limit(1)
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        inc_in = bool(payload.get("increment_inbound_count"))
        inc_out = bool(payload.get("increment_outbound_count"))

        if existing:
            existing.state = state
            if "last_intent" in payload:
                existing.last_intent = payload["last_intent"]
            if "context_json" in payload:
                existing.context_json = payload["context_json"]
            if "last_inbound_text" in payload:
                existing.last_inbound_text = payload["last_inbound_text"]
                existing.last_inbound_at = now
            if "last_outbound_text" in payload:
                existing.last_outbound_text = payload["last_outbound_text"]
                existing.last_outbound_at = now
            if inc_in:
                existing.message_count_inbound = (existing.message_count_inbound or 0) + 1
            if inc_out:
                existing.message_count_outbound = (existing.message_count_outbound or 0) + 1
            if payload.get("escalation_reason"):
                existing.escalated_at = now
                existing.escalation_reason = payload["escalation_reason"]
                existing.escalation_to = payload.get("escalation_to")
            if "lead_id" in payload:
                existing.lead_id = payload["lead_id"]
            if "vtiger_lead_id" in payload:
                existing.vtiger_lead_id = payload["vtiger_lead_id"]
            db.flush()
            db.refresh(existing)
            row = existing
        else:
            new_row = WaConversationState(
                phone_lead=phone,
                state=state,
                last_intent=payload.get("last_intent"),
                context_json=payload.get("context_json"),
                last_inbound_text=payload.get("last_inbound_text"),
                last_inbound_at=now if "last_inbound_text" in payload else None,
                last_outbound_text=payload.get("last_outbound_text"),
                last_outbound_at=now if "last_outbound_text" in payload else None,
                message_count_inbound=1 if inc_in else 0,
                message_count_outbound=1 if inc_out else 0,
                escalated_at=now if payload.get("escalation_reason") else None,
                escalation_reason=payload.get("escalation_reason"),
                escalation_to=payload.get("escalation_to"),
                lead_id=payload.get("lead_id"),
                vtiger_lead_id=payload.get("vtiger_lead_id"),
                started_at=now,
            )
            db.add(new_row)
            db.flush()
            db.refresh(new_row)
            row = new_row

        return jsonify(_row_to_dict(row)), 200
