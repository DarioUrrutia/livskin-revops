"""Rutas /admin/* — solo accesibles por rol admin (ADR-0026 + ADR-0027).

Endpoints:
- /admin/audit-log              — dashboard audit log (filtros + CSV)
- /admin/audit-log/export.csv
- /admin/system-health          — dashboard cross-VPS sensors (Bloque 0.4)
- /admin/agent-costs            — dashboard uso recursos LLM API (Bloque 0.10)
"""
import csv
import io
from datetime import date

from flask import Blueprint, Response, render_template, request

from db import session_scope
from middleware.auth_middleware import require_role
from services import agent_resource_service, audit_service, infra_snapshot_service

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _parse_date(raw: str) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _build_filters() -> dict:
    return {
        "fecha_desde": _parse_date(request.args.get("fecha_desde", "")),
        "fecha_hasta": _parse_date(request.args.get("fecha_hasta", "")),
        "action": (request.args.get("action") or "").strip() or None,
        "category": (request.args.get("category") or "").strip() or None,
        "user_username": (request.args.get("user_username") or "").strip() or None,
        "result": (request.args.get("result") or "").strip() or None,
        "entity_type": (request.args.get("entity_type") or "").strip() or None,
        "entity_id": (request.args.get("entity_id") or "").strip() or None,
    }


@bp.get("/audit-log")
@require_role("admin")
def audit_log_view():  # type: ignore[no-untyped-def]
    filters = _build_filters()
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1
    try:
        per_page = min(500, max(1, int(request.args.get("per_page", "50"))))
    except ValueError:
        per_page = 50

    with session_scope() as db:
        entries_db, total = audit_service.query_audit(
            db,
            page=page,
            per_page=per_page,
            **filters,
        )
        distinct = audit_service.list_distinct_values(db)
        entries = [_serialize_entry(e) for e in entries_db]

    total_pages = (total + per_page - 1) // per_page if per_page else 1

    return render_template(
        "admin_audit_log.html",
        entries=entries,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        filters_raw={
            "fecha_desde": request.args.get("fecha_desde", ""),
            "fecha_hasta": request.args.get("fecha_hasta", ""),
            "action": request.args.get("action", ""),
            "category": request.args.get("category", ""),
            "user_username": request.args.get("user_username", ""),
            "result": request.args.get("result", ""),
            "entity_type": request.args.get("entity_type", ""),
            "entity_id": request.args.get("entity_id", ""),
        },
        distinct=distinct,
    )


@bp.get("/audit-log/export.csv")
@require_role("admin")
def audit_log_export():  # type: ignore[no-untyped-def]
    filters = _build_filters()

    with session_scope() as db:
        entries_db, _ = audit_service.query_audit(
            db,
            page=1,
            per_page=10000,
            **filters,
        )
        entries = [_serialize_entry(e) for e in entries_db]

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "id", "occurred_at", "action", "category", "user_username", "user_role",
        "entity_type", "entity_id", "ip", "result", "error_detail",
        "before_state", "after_state", "metadata",
    ])
    for e in entries:
        writer.writerow([
            e["id"], e["occurred_at"], e["action"], e["category"],
            e["user_username"] or "", e["user_role"] or "",
            e["entity_type"] or "", e["entity_id"] or "", e["ip"] or "",
            e["result"], e["error_detail"] or "",
            _json_short(e["before_state"]), _json_short(e["after_state"]),
            _json_short(e["metadata"]),
        ])

    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log.csv"},
    )


def _serialize_entry(e) -> dict:  # type: ignore[no-untyped-def]
    return {
        "id": e.id,
        "occurred_at": e.occurred_at.strftime("%Y-%m-%d %H:%M:%S") if e.occurred_at else "",
        "action": e.action,
        "category": e.category,
        "user_username": e.user_username,
        "user_role": e.user_role,
        "entity_type": e.entity_type,
        "entity_id": e.entity_id,
        "ip": str(e.ip) if e.ip else None,
        "user_agent": e.user_agent,
        "result": e.result,
        "error_detail": e.error_detail,
        "before_state": e.before_state,
        "after_state": e.after_state,
        "metadata": e.audit_metadata,
    }


def _json_short(value) -> str:  # type: ignore[no-untyped-def]
    import json
    if value is None:
        return ""
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(value)


@bp.get("/system-health")
@require_role("admin")
def system_health_view():  # type: ignore[no-untyped-def]
    """Dashboard cross-VPS — última snapshot de cada VPS (Bloque 0.4)."""
    with session_scope() as db:
        latest = infra_snapshot_service.latest_per_vps(db)
        snapshots = []
        for alias, snap in latest.items():
            if snap is None:
                snapshots.append({"alias": alias, "error": "sin snapshot todavía", "captured_at": None})
                continue
            snapshots.append({
                "alias": snap.vps_alias,
                "role": snap.vps_role,
                "captured_at": snap.captured_at.strftime("%Y-%m-%d %H:%M:%S UTC") if snap.captured_at else "",
                "uptime_h": round((snap.uptime_seconds or 0) / 3600, 1),
                "disk_pct": float(snap.disk_pct) if snap.disk_pct is not None else None,
                "disk_used_gb": float(snap.disk_used_gb) if snap.disk_used_gb is not None else None,
                "disk_total_gb": float(snap.disk_total_gb) if snap.disk_total_gb is not None else None,
                "ram_pct": float(snap.ram_pct) if snap.ram_pct is not None else None,
                "ram_used_mb": snap.ram_used_mb,
                "ram_total_mb": snap.ram_total_mb,
                "containers_count": snap.containers_count,
                "last_deploy_sha": snap.last_deploy_sha,
                "error": snap.error,
                "raw": snap.raw_payload,
            })

    return render_template("admin_system_health.html", snapshots=snapshots)


@bp.get("/agent-costs")
@require_role("admin")
def agent_costs_view():  # type: ignore[no-untyped-def]
    """Dashboard de uso de recursos LLM API por agente (Bloque 0.10).

    Solo está vacío hoy — se llena con data real cuando los agentes operen
    (Fase 4+ Conversation Agent es el primero).
    """
    try:
        days = max(1, min(365, int(request.args.get("days", "30"))))
    except ValueError:
        days = 30

    with session_scope() as db:
        data = agent_resource_service.query_costs(db, days=days)

    return render_template("admin_agent_costs.html", data=data, days=days)
