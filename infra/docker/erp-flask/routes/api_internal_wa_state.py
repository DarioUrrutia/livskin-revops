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
    PUBLIC_ENDPOINTS.add("api_internal_wa_state.pending_followup")
    PUBLIC_ENDPOINTS.add("api_internal_wa_state.cold_candidates")
    PUBLIC_ENDPOINTS.add("api_internal_wa_state.gdpr_pending")
    PUBLIC_ENDPOINTS.add("api_internal_wa_state.gdpr_execute")


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


@bp.get("/pending-followup")
def pending_followup():  # type: ignore[no-untyped-def]
    """GET /api/internal/wa-state/pending-followup?hours_since_inbound=4

    Devuelve lista de leads que:
    - state = 'qualifying' (flow incompleto)
    - last_inbound_at < NOW() - hours_since_inbound
    - context_json.followup_sent != true

    Usado por workflow re-engagement-4h-followup (cron) para enviar template Meta.
    """
    _check_internal_token()

    try:
        hours = int(request.args.get("hours_since_inbound", "4"))
    except ValueError:
        abort(400, description="hours_since_inbound debe ser int")

    from datetime import timedelta
    from models.wa_conversation_state import WaConversationState

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    with session_scope() as db:
        rows = db.execute(
            select(WaConversationState)
            .where(WaConversationState.state == "qualifying")
            .where(WaConversationState.last_inbound_at < cutoff)
            .order_by(WaConversationState.id.desc())
            .limit(100)
        ).scalars().all()

        # Filter: skip followup_sent=true AND skip leads en snooze activo
        from datetime import datetime as _dt
        out = []
        now_utc = _dt.now(timezone.utc)
        for r in rows:
            ctx = r.context_json or {}
            if ctx.get("followup_sent"):
                continue
            # Snooze check: si snoozed_until > NOW, skip
            snoozed = ctx.get("snoozed_until")
            if snoozed:
                try:
                    snoozed_dt = _dt.fromisoformat(snoozed.replace("Z", "+00:00"))
                    if snoozed_dt > now_utc:
                        continue
                except (ValueError, AttributeError):
                    pass
            out.append(_row_to_dict(r))

        return jsonify({"items": out, "count": len(out)})


@bp.get("/cold-candidates")
def cold_candidates():  # type: ignore[no-untyped-def]
    """GET /api/internal/wa-state/cold-candidates?hours_since_inbound=72

    Lista leads en 'qualifying' con followup_sent=true y last_inbound > N horas.
    Workflow F2 los marca como closed_cold.
    """
    _check_internal_token()
    try:
        hours = int(request.args.get("hours_since_inbound", "72"))
    except ValueError:
        abort(400, description="hours_since_inbound debe ser int")

    from datetime import timedelta
    from models.wa_conversation_state import WaConversationState

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    with session_scope() as db:
        rows = db.execute(
            select(WaConversationState)
            .where(WaConversationState.state == "qualifying")
            .where(WaConversationState.last_inbound_at < cutoff)
            .order_by(WaConversationState.id.desc())
            .limit(200)
        ).scalars().all()

        out = []
        for r in rows:
            ctx = r.context_json or {}
            if not ctx.get("followup_sent"):
                continue
            d = _row_to_dict(r)
            now = datetime.now(timezone.utc)
            if r.last_inbound_at:
                d["hours_silent"] = round((now - r.last_inbound_at).total_seconds() / 3600, 1)
            out.append(d)

        return jsonify({"items": out, "count": len(out)})


@bp.get("/gdpr-pending")
def gdpr_pending():  # type: ignore[no-untyped-def]
    """GET /api/internal/wa-state/gdpr-pending

    Lista leads con context_json.request_data_deletion=true y state='closed'.
    Workflow F3 los procesa para eliminar PII cross-system.
    """
    _check_internal_token()

    from models.wa_conversation_state import WaConversationState

    with session_scope() as db:
        rows = db.execute(
            select(WaConversationState)
            .where(WaConversationState.state == "closed")
            .order_by(WaConversationState.id.desc())
            .limit(200)
        ).scalars().all()

        out = []
        for r in rows:
            ctx = r.context_json or {}
            if not ctx.get("request_data_deletion"):
                continue
            # NO incluir si ya fue procesado
            if ctx.get("gdpr_deleted_at"):
                continue
            out.append(_row_to_dict(r))

        return jsonify({"items": out, "count": len(out)})


@bp.post("/gdpr-execute")
def gdpr_execute():  # type: ignore[no-untyped-def]
    """POST /api/internal/wa-state/gdpr-execute

    Body: { "phone_lead": "+51..." }

    Ejecuta DELETE cross-system para un lead que pidió eliminación:
    - wa_messages WHERE phone_lead
    - wa_conversation_state WHERE phone_lead (MARK gdpr_deleted_at en context, NO delete row)
    - leads ERP asociados (phone match)
    - lead_touchpoints (cascade)
    - form_submissions (cascade)
    Audit log: system.gdpr_data_deletion (con phone hasheado para compliance trail).

    NO toca: audit_log (inmutable), analytics.opportunities historicas.
    """
    _check_internal_token()

    payload = request.get_json(silent=True) or {}
    phone = (payload.get("phone_lead") or "").strip()
    if not phone:
        abort(400, description="phone_lead requerido")

    import hashlib
    from sqlalchemy import text as sa_text
    from models.wa_conversation_state import WaConversationState
    from models.lead import Lead
    from models.lead_touchpoint import LeadTouchpoint
    from models.form_submission import FormSubmission

    deleted = {"wa_messages": 0, "leads": 0, "lead_touchpoints": 0, "form_submissions": 0, "wa_state_marked": 0}
    phone_hash = hashlib.sha256(phone.encode()).hexdigest()[:16]

    with session_scope() as db:
        # 1. wa_messages
        res = db.execute(
            sa_text("DELETE FROM wa_messages WHERE phone_lead = :phone"),
            {"phone": phone},
        )
        deleted["wa_messages"] = res.rowcount

        # 2. Leads asociados (phone match)
        leads = db.execute(
            select(Lead).where(Lead.phone_e164 == phone)
        ).scalars().all()
        lead_ids = [l.id for l in leads]

        if lead_ids:
            # 2a. lead_touchpoints
            res = db.execute(
                sa_text("DELETE FROM lead_touchpoints WHERE lead_id = ANY(:ids)"),
                {"ids": lead_ids},
            )
            deleted["lead_touchpoints"] = res.rowcount

            # 2b. form_submissions
            res = db.execute(
                sa_text("DELETE FROM form_submissions WHERE lead_id = ANY(:ids)"),
                {"ids": lead_ids},
            )
            deleted["form_submissions"] = res.rowcount

            # 2c. leads (después de cascades)
            for l in leads:
                db.delete(l)
            deleted["leads"] = len(leads)

        # 3. wa_conversation_state: marcar (NO delete — preservar para audit)
        # Pero ANONIMIZAR el phone y context_json (eliminar PII pero preservar row)
        ws_rows = db.execute(
            select(WaConversationState).where(WaConversationState.phone_lead == phone)
        ).scalars().all()
        for ws in ws_rows:
            old_ctx = dict(ws.context_json or {})  # copy
            name_hash = (
                hashlib.sha256((old_ctx.get("profile_name") or "").encode()).hexdigest()[:16]
                if old_ctx.get("profile_name") else None
            )
            new_ctx = {k: v for k, v in old_ctx.items() if k not in ("profile_name", "last_inbound_text")}
            new_ctx["gdpr_deleted_at"] = datetime.now(timezone.utc).isoformat()
            new_ctx["profile_name_hash"] = name_hash
            # Reasignar el dict completo — SQLAlchemy JSONB requiere reasignacion (no muta in-place)
            ws.context_json = new_ctx
            ws.last_inbound_text = None
            ws.last_outbound_text = None
            ws.phone_lead = f"DELETED_{phone_hash}"  # anonimizar phone
            deleted["wa_state_marked"] += 1

        db.flush()

        # Audit log: documentar deletion (con phone hasheado para trazabilidad sin PII)
        from models.audit_log import AuditLog
        audit_entry = AuditLog(
            action="system.gdpr_data_deletion",
            category="infra",
            entity_type="system",
            entity_id=f"gdpr-{phone_hash}",
            occurred_at=datetime.now(timezone.utc),
            result="success",
            audit_metadata={
                "phone_hash_sha256_16": phone_hash,
                "deleted_counts": deleted,
                "executed_via": "workflow_F3_gdpr",
            },
        )
        db.add(audit_entry)

        return jsonify({"ok": True, "phone_hash": phone_hash, "deleted": deleted}), 200


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

        # ─────────────────────────────────────────────────────────────────
        # Persistir wa_messages rows si el payload incluye inbound_message/outbound_message.
        # Fix bug 2026-05-27: el bot v2 actualizaba solo last_inbound/outbound_text pero NO
        # persistía bodies en wa_messages. Sin esto no podemos analizar copy quality
        # post-campaña ni debuggear conversaciones específicas.
        # Idempotency: meta_message_id UNIQUE — segunda inserción del mismo id retorna OK silently.
        # ─────────────────────────────────────────────────────────────────
        inbound_msg = payload.get("inbound_message")
        outbound_msg = payload.get("outbound_message")
        if inbound_msg or outbound_msg:
            from models.wa_message import WaMessage  # type: ignore[import-not-found]
            from sqlalchemy.exc import IntegrityError

            def _insert_message(msg_data: dict[str, Any], direction: str) -> None:
                if not msg_data:
                    return
                meta_id = msg_data.get("meta_message_id")
                if meta_id:
                    existing_msg = db.execute(
                        select(WaMessage).where(WaMessage.meta_message_id == meta_id).limit(1)
                    ).scalar_one_or_none()
                    if existing_msg:
                        return  # ya persistido, skip (idempotency)
                msg = WaMessage(
                    conversation_id=row.id,
                    meta_message_id=meta_id,
                    phone_lead=phone,
                    direction=direction,
                    message_type=msg_data.get("message_type") or "text",
                    body=msg_data.get("body"),
                    template_name=msg_data.get("template_name"),
                    template_params=msg_data.get("template_params"),
                    meta_status=msg_data.get("meta_status"),
                    meta_status_updated_at=now if msg_data.get("meta_status") else None,
                    meta_error_code=msg_data.get("meta_error_code"),
                    meta_error_message=msg_data.get("meta_error_message"),
                    intent=msg_data.get("intent"),
                    parsed_dates=msg_data.get("parsed_dates"),
                    meta_payload_raw=msg_data.get("meta_payload_raw"),
                    sent_at=now,
                    processed_at=now,
                    created_at=now,
                )
                try:
                    db.add(msg)
                    db.flush()
                except IntegrityError:
                    db.rollback()  # race en meta_message_id duplicate, ya está persistido por otra request

            _insert_message(inbound_msg, "inbound")
            _insert_message(outbound_msg, "outbound")

        return jsonify(_row_to_dict(row)), 200
