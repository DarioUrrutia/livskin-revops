"""Audit service — escribe + consulta eventos inmutables en audit_log (ADR-0027)."""
import logging
from datetime import date, datetime, time, timezone
from typing import Any, Optional

from flask import g, has_request_context, request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.audit_log import AuditLog

logger = logging.getLogger(__name__)


# Lista canónica de actions reconocidas. Extender al agregar nuevos tipos.
KNOWN_ACTIONS = {
    # Auth (7)
    "auth.login_success",
    "auth.login_failed",
    "auth.lockout_triggered",
    "auth.logout_voluntary",
    "auth.logout_inactivity",
    "auth.logout_expired",
    "auth.password_changed",
    "auth.password_reset_by_admin",
    # Venta (3)
    "venta.created",
    "venta.updated",
    "venta.deleted",
    # Pago (3)
    "pago.created",
    "pago.updated",
    "pago.deleted",
    # Gasto (3)
    "gasto.created",
    "gasto.updated",
    "gasto.deleted",
    # Cliente (3)
    "cliente.created",
    "cliente.updated",
    "cliente.merged",
    # Lead (5)
    "lead.created",
    "lead.score_updated",
    "lead.handoff_to_doctora",
    "lead.converted",
    "lead.discarded",
    # Admin (4)
    "admin.user_created",
    "admin.user_deactivated",
    "admin.config_changed",
    "admin.dedup_resolved",
    # Webhooks (2)
    "webhook.form_submit_received",
    "webhook.whatsapp_received",
}


def _category_from_action(action: str) -> str:
    return action.split(".", 1)[0] if "." in action else "unknown"


def _request_context() -> dict[str, Any]:
    """Extrae IP, user-agent, user_id, session_id de Flask context (si existe)."""
    if not has_request_context():
        return {}
    ip = (
        request.headers.get("X-Forwarded-For", request.remote_addr or "")
        .split(",")[0]
        .strip()
        or None
    )
    return {
        "ip": ip,
        "user_agent": request.headers.get("User-Agent"),
        "user_id": getattr(g, "current_user_id", None),
        "user_username": getattr(getattr(g, "current_user", None), "username", None),
        "user_role": getattr(g, "current_user_rol", None),
    }


def log(
    db: Session,
    *,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    before_state: Optional[dict[str, Any]] = None,
    after_state: Optional[dict[str, Any]] = None,
    result: str = "success",
    error_detail: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    user_id: Optional[int] = None,
    user_username: Optional[str] = None,
    user_role: Optional[str] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Escribe un evento al audit_log.

    Toma context HTTP de Flask.g/request automáticamente si está disponible.
    Los argumentos explícitos (user_id, ip, etc.) sobreescriben el context.
    Nunca lanza excepción al caller — los errores se loguean.
    """
    if action not in KNOWN_ACTIONS:
        logger.warning("audit: action desconocido %s — registrando igualmente", action)

    ctx = _request_context()
    entry = AuditLog(
        action=action,
        category=_category_from_action(action),
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        before_state=before_state,
        after_state=after_state,
        result=result,
        error_detail=error_detail,
        audit_metadata=metadata,
        user_id=user_id if user_id is not None else ctx.get("user_id"),
        user_username=user_username if user_username is not None else ctx.get("user_username"),
        user_role=user_role if user_role is not None else ctx.get("user_role"),
        ip=ip if ip is not None else ctx.get("ip"),
        user_agent=user_agent if user_agent is not None else ctx.get("user_agent"),
    )
    try:
        db.add(entry)
        db.flush()
    except Exception:
        logger.exception("audit: error escribiendo evento %s — silenciado", action)


def log_isolated(
    *,
    action: str,
    **kwargs: Any,
) -> None:
    """Versión que abre su propia session_scope. Usar cuando el flujo principal
    no tiene un session activo, p.ej. login fallido (no hay db open).

    Nunca lanza excepción al caller.
    """
    from db import session_scope

    try:
        with session_scope() as db:
            log(db, action=action, **kwargs)
    except Exception:
        logger.exception("audit_isolated: error con %s", action)


def query_audit(
    db: Session,
    *,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    action: Optional[str] = None,
    category: Optional[str] = None,
    user_username: Optional[str] = None,
    result: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[AuditLog], int]:
    """Lista entries del audit_log filtrados + paginados.

    Returns: (entries, total_count) — total_count para calcular num páginas.
    """
    stmt = select(AuditLog)
    count_stmt = select(func.count()).select_from(AuditLog)

    if fecha_desde is not None:
        ts_desde = datetime.combine(fecha_desde, time.min, tzinfo=timezone.utc)
        stmt = stmt.where(AuditLog.occurred_at >= ts_desde)
        count_stmt = count_stmt.where(AuditLog.occurred_at >= ts_desde)
    if fecha_hasta is not None:
        ts_hasta = datetime.combine(fecha_hasta, time.max, tzinfo=timezone.utc)
        stmt = stmt.where(AuditLog.occurred_at <= ts_hasta)
        count_stmt = count_stmt.where(AuditLog.occurred_at <= ts_hasta)
    if action:
        stmt = stmt.where(AuditLog.action == action)
        count_stmt = count_stmt.where(AuditLog.action == action)
    if category:
        stmt = stmt.where(AuditLog.category == category)
        count_stmt = count_stmt.where(AuditLog.category == category)
    if user_username:
        stmt = stmt.where(AuditLog.user_username == user_username)
        count_stmt = count_stmt.where(AuditLog.user_username == user_username)
    if result:
        stmt = stmt.where(AuditLog.result == result)
        count_stmt = count_stmt.where(AuditLog.result == result)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
        count_stmt = count_stmt.where(AuditLog.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(AuditLog.entity_id.ilike(f"%{entity_id}%"))
        count_stmt = count_stmt.where(AuditLog.entity_id.ilike(f"%{entity_id}%"))

    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.order_by(AuditLog.occurred_at.desc()).offset((page - 1) * per_page).limit(per_page)
    entries = list(db.execute(stmt).scalars().all())

    return entries, total


def list_distinct_values(db: Session) -> dict[str, list[str]]:
    """Lista valores únicos para los filtros del dropdown del dashboard."""
    actions = [
        r[0] for r in db.execute(
            select(AuditLog.action).distinct().order_by(AuditLog.action)
        ).all()
    ]
    categories = [
        r[0] for r in db.execute(
            select(AuditLog.category).distinct().order_by(AuditLog.category)
        ).all()
    ]
    users = [
        r[0] for r in db.execute(
            select(AuditLog.user_username)
            .where(AuditLog.user_username.is_not(None))
            .distinct()
            .order_by(AuditLog.user_username)
        ).all()
    ]
    return {"actions": actions, "categories": categories, "users": users}
