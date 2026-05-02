"""Routes internas para ETL warehouse sync (Mini-bloque 3.5 - ADR-0032).

Endpoints:
- GET /api/internal/sync/<resource>?since=<ISO>&limit=N

Recursos soportados:
- leads
- clientes
- ventas
- pagos
- audit-log
- infra-snapshots

Auth: X-Internal-Token (mismo shared secret que api_internal).

Idempotente: el cliente debe pasar `since` (ISO timestamp) — devuelve filas
con updated_at > since, ordenadas ASC, hasta `limit` (default 500, max 5000).
El cliente usa `MAX(updated_at)` del response como `since` del próximo request
(con overlap de unos segundos para no perder filas en boundary).
"""
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import select

from db import session_scope
from middleware.auth_middleware import PUBLIC_ENDPOINTS
from models.lead import Lead
from models.cliente import Cliente
from models.venta import Venta
from models.pago import Pago
from models.audit_log import AuditLog
from models.infra_snapshot import InfraSnapshot

bp = Blueprint("api_internal_sync", __name__, url_prefix="/api/internal/sync")


def _check_internal_token() -> None:
    """Aborta con 403 si el header X-Internal-Token no coincide."""
    from config import settings

    expected = getattr(settings, "audit_internal_token", None)
    if not expected:
        abort(503, description="audit_internal_token no configurado")

    received = request.headers.get("X-Internal-Token", "")
    if received != expected:
        abort(403, description="X-Internal-Token invalido")


def _parse_since() -> datetime:
    """Parse ?since= query param. Default = epoch (sync inicial)."""
    raw = request.args.get("since", "1970-01-01T00:00:00Z")
    try:
        # Aceptar ISO con o sin Z
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw).astimezone(timezone.utc)
    except ValueError:
        abort(400, description=f"since invalido: {raw!r} (esperado ISO 8601)")


def _parse_limit() -> int:
    raw = request.args.get("limit", "500")
    try:
        n = int(raw)
    except ValueError:
        abort(400, description=f"limit invalido: {raw!r}")
    if n < 1:
        n = 1
    if n > 5000:
        n = 5000
    return n


def _serialize_lead(l: Lead) -> dict[str, Any]:
    return {
        "id": l.id,
        "cod_lead": l.cod_lead,
        "vtiger_id": l.vtiger_id,
        "nombre": l.nombre,
        "phone_e164": l.phone_e164,
        "email_lower": l.email_lower,
        "email_hash_sha256": l.email_hash_sha256,
        "fuente": l.fuente,
        "canal_adquisicion": l.canal_adquisicion,
        "utm_source_at_capture": l.utm_source_at_capture,
        "utm_medium_at_capture": l.utm_medium_at_capture,
        "utm_campaign_at_capture": l.utm_campaign_at_capture,
        "utm_content_at_capture": l.utm_content_at_capture,
        "utm_term_at_capture": l.utm_term_at_capture,
        "fbclid_at_capture": l.fbclid_at_capture,
        "gclid_at_capture": l.gclid_at_capture,
        "fbc_at_capture": l.fbc_at_capture,
        "ga_at_capture": l.ga_at_capture,
        "event_id_at_capture": l.event_id_at_capture,
        "tratamiento_interes": l.tratamiento_interes,
        "consent_marketing": l.consent_marketing,
        "consent_date": l.consent_date.isoformat() if l.consent_date else None,
        "estado_lead": l.estado_lead,
        "fecha_captura": l.fecha_captura.isoformat() if l.fecha_captura else None,
        "score": l.score,
        "intent_level": l.intent_level,
        "nurture_state": l.nurture_state,
        "handoff_to_doctora_at": l.handoff_to_doctora_at.isoformat() if l.handoff_to_doctora_at else None,
        "es_reactivacion": l.es_reactivacion,
        "cod_cliente_vinculado": l.cod_cliente_vinculado,
        "created_at": l.created_at.isoformat() if l.created_at else None,
        "updated_at": l.updated_at.isoformat() if l.updated_at else None,
    }


def _serialize_cliente(c: Cliente) -> dict[str, Any]:
    return {
        "id": c.id,
        "cod_cliente": c.cod_cliente,
        "nombre": c.nombre,
        "phone_e164": c.phone_e164,
        "email_lower": c.email_lower,
        "fecha_nacimiento": c.fecha_nacimiento.isoformat() if c.fecha_nacimiento else None,
        "tipo": c.tipo,
        "fuente_origen": c.fuente_origen,
        "cod_lead_origen": c.cod_lead_origen,
        "vtiger_lead_id_origen": c.vtiger_lead_id_origen,
        "fecha_primera_visita": c.fecha_primera_visita.isoformat() if c.fecha_primera_visita else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _serialize_venta(v: Venta) -> dict[str, Any]:
    return {
        "id": v.id,
        "cod_venta": v.cod_venta,
        "cliente_id": v.cliente_id,
        "tratamiento": v.tratamiento,
        "cantidad_sesiones": v.cantidad_sesiones,
        "monto_neto": float(v.monto_neto) if v.monto_neto is not None else None,
        "monto_descuento": float(v.monto_descuento) if v.monto_descuento is not None else None,
        "monto_total": float(v.monto_total) if v.monto_total is not None else None,
        "monto_pagado": float(v.monto_pagado) if v.monto_pagado is not None else None,
        "saldo_pendiente": float(v.saldo_pendiente) if v.saldo_pendiente is not None else None,
        "moneda": v.moneda,
        "estado_venta": v.estado_venta,
        "estado_pago": v.estado_pago,
        "vendedor": v.vendedor,
        "fecha_venta": v.fecha_venta.isoformat() if v.fecha_venta else None,
        "created_at": v.created_at.isoformat() if v.created_at else None,
        "updated_at": v.updated_at.isoformat() if v.updated_at else None,
    }


def _serialize_pago(p: Pago) -> dict[str, Any]:
    return {
        "id": p.id,
        "cod_pago": p.cod_pago,
        "venta_id": p.venta_id,
        "cliente_id": p.cliente_id,
        "fecha_pago": p.fecha_pago.isoformat() if p.fecha_pago else None,
        "monto": float(p.monto) if p.monto is not None else None,
        "metodo": p.metodo,
        "moneda": p.moneda,
        "estado": p.estado,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def _serialize_audit(a: AuditLog) -> dict[str, Any]:
    return {
        "id": a.id,
        "occurred_at": a.occurred_at.isoformat() if a.occurred_at else None,
        "user_id": a.user_id,
        "user_username": a.user_username,
        "user_role": a.user_role,
        "action": a.action,
        "category": a.category,
        "entity_type": a.entity_type,
        "entity_id": a.entity_id,
        "ip": str(a.ip) if a.ip else None,
    }


def _serialize_infra_snapshot(s: InfraSnapshot) -> dict[str, Any]:
    return {
        "id": s.id,
        "vps_alias": s.vps_alias,
        "captured_at": s.captured_at.isoformat() if s.captured_at else None,
        "cpu_pct": float(s.cpu_pct) if s.cpu_pct is not None else None,
        "mem_pct": float(s.mem_pct) if s.mem_pct is not None else None,
        "disk_pct": float(s.disk_pct) if s.disk_pct is not None else None,
        "containers_total": s.containers_total,
        "containers_unhealthy": s.containers_unhealthy,
    }


# Resource registry — maps resource_name -> (Model, time_column, serializer)
_RESOURCES = {
    "leads":            (Lead, "updated_at", _serialize_lead),
    "clientes":         (Cliente, "updated_at", _serialize_cliente),
    "ventas":           (Venta, "updated_at", _serialize_venta),
    "pagos":            (Pago, "updated_at", _serialize_pago),
    "audit-log":        (AuditLog, "occurred_at", _serialize_audit),
    "infra-snapshots":  (InfraSnapshot, "captured_at", _serialize_infra_snapshot),
}


@bp.get("/<string:resource>")
def sync_resource(resource: str):  # type: ignore[no-untyped-def]
    """GET /api/internal/sync/<resource>?since=<ISO>&limit=N

    Devuelve filas con time_column > since, ordenadas ASC, hasta limit.
    """
    _check_internal_token()

    if resource not in _RESOURCES:
        abort(404, description=f"resource desconocido: {resource}. Validos: {list(_RESOURCES.keys())}")

    Model, time_col_name, serializer = _RESOURCES[resource]
    since = _parse_since()
    limit = _parse_limit()

    time_col = getattr(Model, time_col_name)

    with session_scope() as s:
        rows = (
            s.execute(
                select(Model)
                .where(time_col > since)
                .order_by(time_col.asc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
        items = [serializer(r) for r in rows]

        # Compute next_since hint (max time_col en el batch)
        next_since = None
        if items:
            last_row_time = getattr(rows[-1], time_col_name)
            if last_row_time:
                next_since = last_row_time.astimezone(timezone.utc).isoformat()

    return jsonify({
        "ok": True,
        "resource": resource,
        "since_used": since.isoformat(),
        "count": len(items),
        "next_since_hint": next_since,
        "items": items,
    })


# Marcar el endpoint de sync como público para auth_middleware (auth via X-Internal-Token, no bcrypt)
PUBLIC_ENDPOINTS.add("api_internal_sync.sync_resource")
