"""Routes internas para Workflow [A2] sync ERP -> Vtiger (ADR-0036).

Endpoint:
- GET /api/internal/leads/pending-vtiger-sync?since=<audit_log_id>&limit=N

Lista eventos audit_log pendientes de propagar a Vtiger leadstatus.
Solo eventos que afectan lead.estado_lead son sincronizados:
  - appointment.marked_attended -> Vtiger leadstatus=Cliente
  - appointment.marked_no_show  -> Vtiger leadstatus=Contactado

Filtros aplicados:
  - audit_log.action en lista de eventos relevantes
  - audit_log.id > since (cursor avanza)
  - JOIN appointments + leads
  - WHERE leads.vtiger_id IS NOT NULL (skip leads sin contraparte Vtiger)

Auth: X-Internal-Token (mismo shared secret que api_internal_sync).

Idempotente via cursor: el cliente (workflow n8n A2) pasa el max audit_log_id
procesado en la iteracion anterior. Server filtra estrictamente > since,
ordena ASC, devuelve hasta limit (default 50, max 500). Cliente actualiza
cursor con items[-1].audit_log_id si hubo items.

Doctrina: feedback_congruencia_nombres_cross_system.md (mapping 1:1
Title Case Vtiger <-> lowercase ASCII ERP).
"""
from typing import Any

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import and_, select

from db import session_scope
from middleware.auth_middleware import PUBLIC_ENDPOINTS
from models.appointment import Appointment
from models.audit_log import AuditLog
from models.lead import Lead

bp = Blueprint("api_internal_vtiger_sync", __name__, url_prefix="/api/internal/leads")


# Mapeo audit.action -> target Vtiger leadstatus.
# Ver ADR-0036 seccion "Eventos en scope" + integrations/vtiger/fields-mapping.md.
ACTION_TO_VTIGER_LEADSTATUS: dict[str, str] = {
    "appointment.marked_attended": "Cliente",
    "appointment.marked_no_show": "Contactado",
}


def _check_internal_token() -> None:
    """Aborta con 403 si el header X-Internal-Token no coincide."""
    from config import settings

    expected = getattr(settings, "audit_internal_token", None)
    if not expected:
        abort(503, description="audit_internal_token no configurado")

    received = request.headers.get("X-Internal-Token", "")
    if received != expected:
        abort(403, description="X-Internal-Token invalido")


def _parse_since() -> int:
    """Parse ?since= como entero (audit_log.id cursor). Default 0 (sync inicial)."""
    raw = request.args.get("since", "0")
    try:
        n = int(raw)
    except ValueError:
        abort(400, description=f"since invalido: {raw!r} (esperado int audit_log.id)")
    if n < 0:
        n = 0
    return n


def _parse_limit() -> int:
    raw = request.args.get("limit", "50")
    try:
        n = int(raw)
    except ValueError:
        abort(400, description=f"limit invalido: {raw!r}")
    if n < 1:
        n = 1
    if n > 500:
        n = 500
    return n


@bp.get("/pending-vtiger-sync")
def get_pending_vtiger_sync():  # type: ignore[no-untyped-def]
    """Lista eventos audit pendientes de propagar a Vtiger leadstatus.

    Returns JSON:
        {
          "items": [
            {
              "audit_log_id": int,
              "audit_action": str,
              "occurred_at": str (ISO),
              "cod_appointment": str,
              "cod_lead": str,
              "vtiger_id": str,
              "current_erp_estado_lead": str,
              "target_vtiger_leadstatus": str
            },
            ...
          ],
          "count": int,
          "next_cursor": int,  # max audit_log_id en items, o since si vacio
          "has_more": bool     # True si count == limit (puede haber mas paginas)
        }
    """
    _check_internal_token()
    since = _parse_since()
    limit = _parse_limit()

    relevant_actions = list(ACTION_TO_VTIGER_LEADSTATUS.keys())

    with session_scope() as db:
        rows = db.execute(
            select(
                AuditLog.id,
                AuditLog.action,
                AuditLog.occurred_at,
                AuditLog.entity_id,
                Lead.cod_lead,
                Lead.vtiger_id,
                Lead.estado_lead,
            )
            .join(
                Appointment,
                and_(
                    AuditLog.entity_type == "appointment",
                    AuditLog.entity_id == Appointment.cod_appointment,
                ),
            )
            .join(Lead, Appointment.lead_id == Lead.id)
            .where(
                AuditLog.id > since,
                AuditLog.action.in_(relevant_actions),
                Lead.vtiger_id.is_not(None),
            )
            .order_by(AuditLog.id.asc())
            .limit(limit)
        ).all()

        items: list[dict[str, Any]] = []
        for r in rows:
            items.append({
                "audit_log_id": r.id,
                "audit_action": r.action,
                "occurred_at": r.occurred_at.isoformat() if r.occurred_at else None,
                "cod_appointment": r.entity_id,
                "cod_lead": r.cod_lead,
                "vtiger_id": r.vtiger_id,
                "current_erp_estado_lead": r.estado_lead,
                "target_vtiger_leadstatus": ACTION_TO_VTIGER_LEADSTATUS[r.action],
            })

    next_cursor = items[-1]["audit_log_id"] if items else since

    return jsonify({
        "items": items,
        "count": len(items),
        "next_cursor": next_cursor,
        "has_more": len(items) == limit,
    })


def register_public_endpoints() -> None:
    """Marca el endpoint como publico (bypassa auth middleware bcrypt).

    NO significa "sin auth" — significa "no requiere session bcrypt".
    El endpoint internamente requiere X-Internal-Token via _check_internal_token().
    Mismo patron que api_internal_sync_bp.
    """
    PUBLIC_ENDPOINTS.add("api_internal_vtiger_sync.get_pending_vtiger_sync")
