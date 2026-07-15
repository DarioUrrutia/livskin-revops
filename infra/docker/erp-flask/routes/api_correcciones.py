"""Rutas de corrección controlada de registros — ADR-0040 (2026-07-15).

Permite corregir campos NO-monetarios de ventas y pagos ya guardados,
con audit trail before/after obligatorio. Nace del incidente 2026-07-15:
venta LIVTRAT0081 ingresada con fecha default (hoy) en vez de la histórica,
sin ninguna vía de corrección en la app (Libro es read-only, no existía
ningún endpoint UPDATE).

Endpoints (requieren auth bcrypt session via middleware — NO son públicos):

    PATCH /api/ventas/<cod_item>/corregir    body: subset de VENTA_CAMPOS_CORREGIBLES
    PATCH /api/pagos/<cod_pago>/corregir     body: subset de PAGO_CAMPOS_CORREGIBLES

Reglas duras:
- Whitelist server-side de campos: montos (total, pagado, debe, descuento,
  monto, efectivo, yape, plin, giro) NUNCA son corregibles por esta vía.
  La integridad debe/pagado depende del trigger Postgres sobre `pagos`
  (migración 0002) y de la lógica de venta_service — editar montos aquí
  los desincronizaría. Corrección de montos: futuro patrón anulación.
- Cada corrección emite audit_log `venta.corrected` / `pago.corrected`
  con before_state/after_state.
- Feature flag CORRECTIONS_ENABLED (default False) — si off, 404.
"""
from datetime import date, datetime
from typing import Any, Optional

from flask import Blueprint, abort, g, jsonify, request
from sqlalchemy import select

from config import settings
from db import session_scope
from models.pago import Pago
from models.venta import Venta
from services import audit_service

bp = Blueprint("api_correcciones", __name__)

# Whitelist dura de campos corregibles. Cualquier otro campo en el body → 400.
VENTA_CAMPOS_CORREGIBLES = {"fecha", "notas", "proxima_cita", "categoria"}
PAGO_CAMPOS_CORREGIBLES = {"fecha", "notas"}

# Campos de tipo Date que requieren parseo ISO
_CAMPOS_DATE = {"fecha", "proxima_cita"}


def _check_feature_enabled() -> None:
    """Si feature flag desactivado, 404 (endpoint no existe)."""
    if not getattr(settings, "corrections_enabled", False):
        abort(404)


def _parse_iso_date(value: Any, campo: str) -> Optional[date]:
    """Parsea YYYY-MM-DD. None/'' → None (para campos nullable como proxima_cita)."""
    if value is None or str(value).strip() == "":
        return None
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        abort(400, description=f"Campo '{campo}' debe ser fecha YYYY-MM-DD")


def _validar_body(payload: dict[str, Any], whitelist: set[str]) -> dict[str, Any]:
    """Valida que el body tenga SOLO campos whitelisted y al menos uno.

    Returns dict campo→valor_parseado listo para setattr.
    """
    if not payload:
        abort(400, description="Body JSON vacío — enviar al menos un campo corregible")

    campos_invalidos = set(payload.keys()) - whitelist
    if campos_invalidos:
        abort(
            400,
            description=(
                f"Campos no corregibles: {sorted(campos_invalidos)}. "
                f"Corregibles: {sorted(whitelist)}. "
                "Montos nunca son editables (integridad contable — ADR-0040)."
            ),
        )

    cambios: dict[str, Any] = {}
    for campo, valor in payload.items():
        if campo in _CAMPOS_DATE:
            parsed = _parse_iso_date(valor, campo)
            # fecha es NOT NULL en ventas y pagos — no permitir vaciarla
            if campo == "fecha" and parsed is None:
                abort(400, description="Campo 'fecha' no puede quedar vacío")
            cambios[campo] = parsed
        else:
            # Campos texto: normalizar '' → None
            cambios[campo] = str(valor).strip() if valor not in (None, "") else None
    return cambios


def _serializar(valor: Any) -> Any:
    """date → ISO string para audit JSON."""
    if isinstance(valor, date):
        return valor.isoformat()
    return valor


@bp.patch("/api/ventas/<cod_item>/corregir")
def corregir_venta(cod_item: str):  # type: ignore[no-untyped-def]
    """Corrige campos no-monetarios de UNA venta (por cod_item).

    Nota: cod_item es único por ítem vendido (1 fila = 1 ítem, ADR-0011).
    """
    _check_feature_enabled()
    payload = request.get_json(silent=True) or {}
    cambios = _validar_body(payload, VENTA_CAMPOS_CORREGIBLES)

    with session_scope() as db:
        venta = db.execute(
            select(Venta).where(Venta.cod_item == cod_item)
        ).scalar_one_or_none()
        if venta is None:
            abort(404, description=f"Venta {cod_item} no existe")

        before = {c: _serializar(getattr(venta, c)) for c in cambios}
        for campo, valor in cambios.items():
            setattr(venta, campo, valor)
        venta.updated_by = getattr(g, "current_user_id", None)
        after = {c: _serializar(getattr(venta, c)) for c in cambios}

        audit_service.log(
            db,
            action="venta.corrected",
            entity_type="venta",
            entity_id=cod_item,
            before_state=before,
            after_state=after,
        )

        return jsonify(
            {
                "ok": True,
                "cod_item": cod_item,
                "campos_corregidos": sorted(cambios.keys()),
                "before": before,
                "after": after,
            }
        ), 200


@bp.patch("/api/pagos/<cod_pago>/corregir")
def corregir_pago(cod_pago: str):  # type: ignore[no-untyped-def]
    """Corrige campos no-monetarios de UN pago (por cod_pago, unique)."""
    _check_feature_enabled()
    payload = request.get_json(silent=True) or {}
    cambios = _validar_body(payload, PAGO_CAMPOS_CORREGIBLES)

    with session_scope() as db:
        pago = db.execute(
            select(Pago).where(Pago.cod_pago == cod_pago)
        ).scalar_one_or_none()
        if pago is None:
            abort(404, description=f"Pago {cod_pago} no existe")

        before = {c: _serializar(getattr(pago, c)) for c in cambios}
        for campo, valor in cambios.items():
            setattr(pago, campo, valor)
        pago.updated_by = getattr(g, "current_user_id", None)
        after = {c: _serializar(getattr(pago, c)) for c in cambios}

        audit_service.log(
            db,
            action="pago.corrected",
            entity_type="pago",
            entity_id=cod_pago,
            before_state=before,
            after_state=after,
        )

        return jsonify(
            {
                "ok": True,
                "cod_pago": cod_pago,
                "campos_corregidos": sorted(cambios.keys()),
                "before": before,
                "after": after,
            }
        ), 200
