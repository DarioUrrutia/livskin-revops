"""Routes internas para distributed locks (Redis SETNX wrapper).

Sprint 1.3 (2026-05-28). Defensa contra overlap concurrente de:
- Crons n8n F1/F2/F3/B3 que se solapan en tiempo
- Webhooks burst para mismo phone_lead
- Cualquier sección crítica cross-VPS

Endpoints:
- POST /api/internal/lock/acquire  — try-acquire (NX + EX)
- POST /api/internal/lock/release  — release explícito
- GET  /api/internal/lock/ping     — health Redis

Patron de uso (n8n cron):
    1. POST /lock/acquire {key, ttl_seconds}
    2. Si 200 + {acquired: true} → continuar workflow
    3. Si 200 + {acquired: false} → skip (lock held)
    4. Si 5xx → fail-OPEN (Redis down; proceder sin lock)
"""
from flask import Blueprint, abort, jsonify, request

from middleware.auth_middleware import PUBLIC_ENDPOINTS
from services import distributed_lock_service

bp = Blueprint("api_internal_lock", __name__, url_prefix="/api/internal/lock")


def register_public_endpoints() -> None:
    PUBLIC_ENDPOINTS.add("api_internal_lock.acquire_lock")
    PUBLIC_ENDPOINTS.add("api_internal_lock.release_lock")
    PUBLIC_ENDPOINTS.add("api_internal_lock.ping_redis")


def _check_internal_token() -> None:
    from config import settings

    expected = getattr(settings, "audit_internal_token", None)
    if not expected:
        abort(503, description="audit_internal_token no configurado")
    received = request.headers.get("X-Internal-Token", "")
    if received != expected:
        abort(403, description="X-Internal-Token inválido")


@bp.post("/acquire")
def acquire_lock():  # type: ignore[no-untyped-def]
    """POST /api/internal/lock/acquire

    Body JSON:
        {
          "key": "cron:b3" or "phone:+51947...",
          "ttl_seconds": 600,          # default 600
          "value": "host-vps2-pid-123" # opcional, para debug
        }

    Returns:
        200 {"acquired": true,  "key": "...", "ttl_seconds": 600}  → got lock
        200 {"acquired": false, "key": "...", "reason": "held"}     → already locked
        503 {"acquired": false, "error": "redis_unreachable"}       → Redis down (fail-open caller decision)
    """
    _check_internal_token()

    payload = request.get_json(silent=True) or {}
    key = (payload.get("key") or "").strip()
    ttl = int(payload.get("ttl_seconds") or 600)
    value = (payload.get("value") or "1").strip() or "1"

    if not key:
        abort(400, description="key requerido")
    if ttl < 1 or ttl > 86400:
        abort(400, description="ttl_seconds fuera de rango (1-86400)")

    try:
        acquired = distributed_lock_service.acquire(key, ttl_seconds=ttl, value=value)
        if acquired:
            return jsonify({"acquired": True, "key": key, "ttl_seconds": ttl}), 200
        return jsonify({"acquired": False, "key": key, "reason": "held"}), 200
    except Exception as e:
        return jsonify({"acquired": False, "error": f"redis_error: {e}"}), 503


@bp.post("/release")
def release_lock():  # type: ignore[no-untyped-def]
    """POST /api/internal/lock/release

    Body JSON: { "key": "cron:b3" }
    Returns: 200 {"released": true/false}  (false si ya no existía o Redis down)
    """
    _check_internal_token()

    payload = request.get_json(silent=True) or {}
    key = (payload.get("key") or "").strip()
    if not key:
        abort(400, description="key requerido")

    try:
        released = distributed_lock_service.release(key)
        return jsonify({"released": released, "key": key}), 200
    except Exception as e:
        return jsonify({"released": False, "error": f"redis_error: {e}"}), 503


@bp.get("/ping")
def ping_redis():  # type: ignore[no-untyped-def]
    """GET /api/internal/lock/ping  — health Redis."""
    _check_internal_token()
    ok = distributed_lock_service.ping()
    return jsonify({"redis": "ok" if ok else "unreachable"}), 200 if ok else 503
