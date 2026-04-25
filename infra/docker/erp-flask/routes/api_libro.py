"""Route /api/libro — export plano de ventas/pagos/gastos."""
from datetime import date, datetime
from typing import Optional

from flask import Blueprint, jsonify, request

from db import session_scope
from services import libro_service

bp = Blueprint("api_libro", __name__)


def _parse_fecha(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


@bp.get("/api/libro")
def get_libro():  # type: ignore[no-untyped-def]
    desde = _parse_fecha(request.args.get("desde"))
    hasta = _parse_fecha(request.args.get("hasta"))

    with session_scope() as db:
        result = libro_service.compute_libro(db, desde=desde, hasta=hasta)

    return jsonify(result), 200
