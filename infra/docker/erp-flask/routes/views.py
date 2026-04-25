"""Routes UI — sirve formulario.html del Flask original (preservado).

GET / construye el contexto Jinja2 que el template espera:
- clientes: lista de nombres (para datalist autocomplete)
- clientes_codigos: dict {nombre: cod_cliente}
- clientes_data: dict {nombre: {telefono, cumpleanos, email}}
- next_client_num: próximo número para LIVCLIENT####
- active_tab: pestaña por default (venta/gasto/pagos/cliente/dashboard/libro)
- messages: flash messages
"""
import re
from typing import Any

from flask import Blueprint, get_flashed_messages, render_template, request
from sqlalchemy import select

from db import session_scope
from models.cliente import Cliente

bp = Blueprint("views", __name__)

_LIVCLIENT_PATTERN = re.compile(r"^LIVCLIENT(\d+)$")


@bp.get("/")
def index() -> str:
    with session_scope() as db:
        clientes = list(
            db.execute(
                select(Cliente)
                .where(Cliente.activo.is_(True))
                .order_by(Cliente.nombre)
            )
            .scalars()
            .all()
        )

        clientes_nombres = [c.nombre for c in clientes]
        clientes_codigos: dict[str, str] = {c.nombre: c.cod_cliente for c in clientes}
        clientes_data: dict[str, dict[str, Any]] = {
            c.nombre: {
                "telefono": c.phone_e164 or "",
                "cumpleanos": c.fecha_nacimiento.isoformat() if c.fecha_nacimiento else "",
                "email": c.email_lower or "",
            }
            for c in clientes
        }

        max_num = 0
        for c in clientes:
            m = _LIVCLIENT_PATTERN.match(c.cod_cliente)
            if m:
                num = int(m.group(1))
                if num > max_num:
                    max_num = num
        next_client_num = max_num + 1

    active_tab = request.args.get("tab", "venta")
    messages = get_flashed_messages()

    return render_template(
        "formulario.html",
        clientes=clientes_nombres,
        clientes_codigos=clientes_codigos,
        clientes_data=clientes_data,
        next_client_num=next_client_num,
        active_tab=active_tab,
        messages=messages,
    )
