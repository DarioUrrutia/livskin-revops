"""Routes internas (cross-VPS) — autenticadas por shared secret.

NO requieren login bcrypt (no es para usuarios humanos), pero requieren
el header `X-Internal-Token` con el valor de settings.audit_internal_token.

Endpoints:
- GET  /api/system-map.json — devuelve el system-map parseado como JSON
- POST /api/internal/audit-event — recibe eventos de infra (workflows GHA, cron)
- GET  /api/internal/health — healthcheck para sensors cross-VPS
"""
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, abort, jsonify, request

from db import session_scope
from services import audit_service, system_map_service
from middleware.auth_middleware import PUBLIC_ENDPOINTS

bp = Blueprint("api_internal", __name__, url_prefix="/api")


def _check_internal_token() -> None:
    """Aborta con 403 si el header X-Internal-Token no coincide con settings."""
    from config import settings

    expected = getattr(settings, "audit_internal_token", None)
    if not expected:
        # Settings no tiene el token — fallar cerrado
        abort(503, description="audit_internal_token no configurado")

    received = request.headers.get("X-Internal-Token", "")
    if received != expected:
        abort(403, description="X-Internal-Token inválido")


@bp.get("/system-map.json")
def system_map_json():  # type: ignore[no-untyped-def]
    """Sirve el system-map parseado como JSON.

    Acceso público (read-only) — es el mapa del sistema, no contiene secretos.
    Si en el futuro queremos restringir, agregar _check_internal_token() acá.
    """
    sm = system_map_service.get_system_map()
    return jsonify(sm)


@bp.post("/internal/audit-event")
def receive_audit_event():  # type: ignore[no-untyped-def]
    """Recibe eventos de infra desde workflows CI/CD, cron de backups, etc.

    Body JSON esperado:
        {
          "action": "infra.deploy_completed",
          "metadata": {
            "vps": "vps3",
            "sha": "abc123",
            "actor": "DarioUrrutia",
            "outcome": "success"
          }
        }

    Inserta entry en audit_log usando audit_service.log() — atómico con la
    transacción. Sin auth user (es cross-system event).
    """
    _check_internal_token()

    body = request.get_json(silent=True) or {}
    action = body.get("action", "").strip()
    if not action:
        abort(400, description="action requerido")

    metadata: dict[str, Any] = body.get("metadata") or {}
    entity_type = body.get("entity_type")
    entity_id = body.get("entity_id")
    result_str = body.get("result", "success")
    error_detail = body.get("error_detail")

    try:
        with session_scope() as db:
            audit_service.log(
                db,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id is not None else None,
                metadata=metadata,
                result=result_str,
                error_detail=error_detail,
                user_username="ci-cd",  # marcar como sistema, no humano
                user_role="system",
                ip=request.headers.get("X-Forwarded-For", request.remote_addr),
            )
        return jsonify({"ok": True, "action": action}), 201
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.get("/internal/health")
def internal_health():  # type: ignore[no-untyped-def]
    """Healthcheck básico cross-VPS. Sin auth (read-only, no PII).

    Útil para sensors uniformes. Devuelve 200 si la app responde y la DB
    está accesible.
    """
    try:
        with session_scope() as db:
            db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return jsonify({
            "status": "ok",
            "service": "erp-flask",
            "vps": "livskin-erp",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        return jsonify({"status": "degraded", "error": str(e)}), 503


@bp.get("/internal/system-state")
def internal_system_state():  # type: ignore[no-untyped-def]
    """Snapshot detallado del estado del VPS 3 (Bloque 0.4).

    Mismo schema que livskin-sensor:9100/api/system-state — para uniformidad
    el recolector cross-VPS puede consumir tanto este endpoint como el de
    los containers livskin-sensor en VPS 1 y 2.
    """
    _check_internal_token()

    import os
    import socket
    import subprocess
    from pathlib import Path

    try:
        import psutil  # type: ignore
    except ImportError:
        psutil = None  # type: ignore

    def _disk():  # type: ignore[no-untyped-def]
        if psutil is None:
            return {"error": "psutil no instalado"}
        u = psutil.disk_usage("/")
        return {
            "total_gb": round(u.total / 1024**3, 2),
            "used_gb": round(u.used / 1024**3, 2),
            "free_gb": round(u.free / 1024**3, 2),
            "percent": u.percent,
        }

    def _ram():  # type: ignore[no-untyped-def]
        if psutil is None:
            return {"error": "psutil no instalado"}
        m = psutil.virtual_memory()
        return {
            "total_mb": round(m.total / 1024**2),
            "used_mb": round(m.used / 1024**2),
            "available_mb": round(m.available / 1024**2),
            "percent": m.percent,
        }

    def _uptime() -> int:
        if psutil is not None:
            import time as _time
            return int(_time.time() - psutil.boot_time())
        try:
            with open("/proc/uptime", encoding="utf-8") as f:
                return int(float(f.read().split()[0]))
        except OSError:
            return 0

    def _last_sha() -> str:
        head = Path("/repo/.git/HEAD")
        if not head.exists():
            return "unknown"
        try:
            content = head.read_text(encoding="utf-8").strip()
            if content.startswith("ref:"):
                ref_path = Path("/repo/.git") / content.split(" ", 1)[1].strip()
                if ref_path.exists():
                    return ref_path.read_text(encoding="utf-8").strip()[:7]
            return content[:7]
        except OSError:
            return "unknown"

    def _containers():  # type: ignore[no-untyped-def]
        # Container erp-flask no tiene acceso a docker.sock por seguridad,
        # así que retornamos lista vacía. El livskin-sensor (que SÍ tiene
        # acceso) reportará containers de VPS 2.
        return []

    return jsonify({
        "vps_alias": os.environ.get("VPS_ALIAS", socket.gethostname()),
        "vps_role": "vps3-erp",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": _uptime(),
        "disk": _disk(),
        "ram": _ram(),
        "containers": _containers(),
        "host_services": [],
        "last_deploy_sha": _last_sha(),
    })


@bp.post("/internal/agent-api-call")
def receive_agent_api_call():  # type: ignore[no-untyped-def]
    """Recibe registros de llamadas Claude API desde wrappers de agentes (Bloque 0.10).

    Body JSON esperado:
        {
          "agent_name": "conversation",
          "model": "claude-sonnet-4-6",
          "input_tokens": 1234,
          "output_tokens": 567,
          "cache_read_input_tokens": 0,
          "cache_creation_input_tokens": 0,
          "task_id": "lead_LIVCLIENT0042",
          "prompt_template_id": "conversation-greeting-v1.2",
          "request_id": "msg_abc123",
          "latency_ms": 1245,
          "outcome": "success",
          "metadata": {...}
        }

    AgentResourceService calcula cost_usd, persiste, evalúa thresholds, y
    emite audit events si cruzó budget.
    """
    _check_internal_token()

    body = request.get_json(silent=True) or {}
    required = ["agent_name", "model", "input_tokens", "output_tokens"]
    missing = [f for f in required if f not in body]
    if missing:
        abort(400, description=f"campos requeridos: {missing}")

    from services import agent_resource_service as ars

    try:
        with session_scope() as db:
            call = ars.record_call(
                db,
                agent_name=body["agent_name"],
                model=body["model"],
                input_tokens=int(body["input_tokens"]),
                output_tokens=int(body["output_tokens"]),
                cache_creation_input_tokens=int(body.get("cache_creation_input_tokens", 0)),
                cache_read_input_tokens=int(body.get("cache_read_input_tokens", 0)),
                task_id=body.get("task_id"),
                prompt_template_id=body.get("prompt_template_id"),
                request_id=body.get("request_id"),
                latency_ms=body.get("latency_ms"),
                outcome=body.get("outcome", "success"),
                error_detail=body.get("error_detail"),
                metadata=body.get("metadata"),
            )
            return jsonify({
                "ok": True,
                "id": call.id,
                "cost_usd": str(call.cost_usd),
            }), 201
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.get("/internal/agent-budget-check")
def agent_budget_check():  # type: ignore[no-untyped-def]
    """Pre-check antes de hacer llamada API. Devuelve can_proceed + razón."""
    _check_internal_token()

    agent_name = request.args.get("agent_name", "").strip()
    if not agent_name:
        abort(400, description="agent_name requerido")

    from decimal import Decimal as _D
    try:
        estimated = _D(request.args.get("estimated_cost_usd", "0.01"))
    except Exception:
        abort(400, description="estimated_cost_usd inválido")

    from services import agent_resource_service as ars

    with session_scope() as db:
        result = ars.check_budget_or_block(
            db, agent_name=agent_name, estimated_cost_usd=estimated
        )
        return jsonify({
            "can_proceed": result.can_proceed,
            "reason": result.reason,
            "daily_consumed_usd": str(result.daily_consumed) if result.daily_consumed is not None else None,
            "daily_limit_usd": str(result.daily_limit) if result.daily_limit is not None else None,
            "monthly_consumed_usd": str(result.monthly_consumed) if result.monthly_consumed is not None else None,
            "monthly_limit_usd": str(result.monthly_limit) if result.monthly_limit is not None else None,
        })


# Asegurar que estos endpoints estén en allowlist del middleware auth
def register_public_endpoints() -> None:
    """Marca los endpoints públicos (sin sesión bcrypt) en el middleware."""
    PUBLIC_ENDPOINTS.add("api_internal.system_map_json")
    PUBLIC_ENDPOINTS.add("api_internal.receive_audit_event")
    PUBLIC_ENDPOINTS.add("api_internal.internal_health")
    PUBLIC_ENDPOINTS.add("api_internal.internal_system_state")
    PUBLIC_ENDPOINTS.add("api_internal.receive_agent_api_call")
    PUBLIC_ENDPOINTS.add("api_internal.agent_budget_check")
