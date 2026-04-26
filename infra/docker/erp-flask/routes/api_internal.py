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


# Asegurar que estos endpoints estén en allowlist del middleware auth
def register_public_endpoints() -> None:
    """Marca los endpoints públicos (sin sesión bcrypt) en el middleware."""
    PUBLIC_ENDPOINTS.add("api_internal.system_map_json")
    PUBLIC_ENDPOINTS.add("api_internal.receive_audit_event")
    PUBLIC_ENDPOINTS.add("api_internal.internal_health")
