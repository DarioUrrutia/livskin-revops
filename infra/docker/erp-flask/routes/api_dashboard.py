"""Route /api/dashboard — preserva contrato HTTP del Flask original."""
from datetime import date, datetime
from typing import Optional

from flask import Blueprint, jsonify, request

from db import session_scope
from services import dashboard_service

bp = Blueprint("api_dashboard", __name__)


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


@bp.get("/api/dashboard")
def get_dashboard():  # type: ignore[no-untyped-def]
    desde = _parse_fecha(request.args.get("desde"))
    hasta = _parse_fecha(request.args.get("hasta"))

    with session_scope() as db:
        result = dashboard_service.compute_dashboard(db, desde=desde, hasta=hasta)

    return jsonify(result), 200
