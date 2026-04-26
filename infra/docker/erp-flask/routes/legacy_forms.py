"""Capa de compatibilidad form-data → JSON (preserva HTML del Flask original).

El template formulario.html (3500+ líneas) tiene 3 forms que POST con
application/x-www-form-urlencoded a /venta, /pagos, /gasto. Estos endpoints
parsean los form fields y llaman a los services correspondientes (que
internamente usan JSON shapes).

Cada endpoint redirect a / con flash message — patrón legacy preservado
para no romper el JS del template.
"""
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

from flask import Blueprint, flash, redirect, request, url_for
from sqlalchemy import select

from db import session_scope
from models.cliente import Cliente
from services import audit_service, cliente_service, gasto_service, pago_service, venta_service

bp = Blueprint("legacy_forms", __name__)


def _to_decimal(raw: Optional[str], default: Decimal = Decimal("0")) -> Decimal:
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return Decimal(str(raw).replace(",", "."))
    except (InvalidOperation, ValueError):
        return default


def _to_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


@bp.post("/gasto")
def gasto_form():  # type: ignore[no-untyped-def]
    """POST /gasto — form-data del HTML legacy."""
    fecha = _to_date(request.form.get("fecha_gasto"))
    if not fecha:
        flash("Error al guardar: fecha inválida.")
        return redirect(url_for("views.index", tab="gasto"))

    monto = _to_decimal(request.form.get("monto_gasto"))
    if monto <= 0:
        flash("Error al guardar: monto debe ser > 0.")
        return redirect(url_for("views.index", tab="gasto"))

    try:
        with session_scope() as db:
            gasto = gasto_service.create(
                db,
                fecha=fecha,
                monto=monto,
                tipo=request.form.get("tipo_gasto") or None,
                descripcion=request.form.get("descripcion") or None,
                destinatario=request.form.get("destinatario") or None,
                metodo_pago=request.form.get("metodo_pago_gasto") or None,
            )
            audit_service.log(
                db,
                action="gasto.created",
                entity_type="gasto",
                entity_id=getattr(gasto, "id", None),
                after_state={
                    "fecha": fecha.isoformat(),
                    "monto": str(monto),
                    "tipo": request.form.get("tipo_gasto") or None,
                    "destinatario": request.form.get("destinatario") or None,
                },
            )
        flash("Gasto guardado correctamente.")
    except Exception as e:
        audit_service.log_isolated(
            action="gasto.created",
            result="failure",
            error_detail=str(e),
        )
        flash(f"Error al guardar: {e}")

    return redirect(url_for("views.index", tab="gasto"))


@bp.post("/venta")
def venta_form():  # type: ignore[no-untyped-def]
    """POST /venta — form-data del HTML legacy con N items.

    Parsea: cliente data + lista items (tipo_0, categoria_0, ..., tipo_N, ...)
    + métodos pago + crédito + abonos + flag actualizar_cliente.
    """
    fecha = _to_date(request.form.get("fecha"))
    nombre = (request.form.get("cliente") or "").strip()
    if not fecha or not nombre:
        flash("Error al guardar: fecha y cliente son requeridos.")
        return redirect(url_for("views.index", tab="venta"))

    cliente_data = venta_service.ClienteAutoCreateInput(
        nombre=nombre,
        telefono=request.form.get("telefono") or None,
        email=request.form.get("email") or None,
        fecha_nacimiento=_to_date(request.form.get("cumpleanos")),
    )
    actualizar_cliente = request.form.get("actualizar_cliente") == "1"

    try:
        num_items = int(request.form.get("num_items", "1"))
    except ValueError:
        num_items = 1

    items: list[venta_service.ItemVentaInput] = []
    for i in range(num_items):
        tipo = request.form.get(f"tipo_{i}", "").strip()
        if not tipo:
            continue

        categoria = request.form.get(f"categoria_{i}", "").strip()
        if categoria == "__otro__":
            categoria = request.form.get(f"categoria_otro_{i}", "").strip()

        es_gratis = request.form.get(f"es_gratis_{i}") == "1"
        precio_lista = _to_decimal(request.form.get(f"precio_lista_{i}"))
        descuento = _to_decimal(request.form.get(f"descuento_{i}"))
        total_item = _to_decimal(request.form.get(f"total_item_{i}"))
        pago_item = _to_decimal(request.form.get(f"pago_item_{i}"))

        if es_gratis or (precio_lista > 0 and descuento >= precio_lista):
            descuento = precio_lista

        items.append(
            venta_service.ItemVentaInput(
                tipo=tipo,
                categoria=categoria or None,
                zona_cantidad_envase=request.form.get(f"zona_{i}") or None,
                precio_lista=precio_lista if precio_lista > 0 else (total_item if total_item > 0 else None),
                descuento=descuento,
                pago_item=pago_item,
            )
        )

    if not items:
        flash("Error al guardar: ningún item válido.")
        return redirect(url_for("views.index", tab="venta"))

    metodos_pago = {
        "efectivo": _to_decimal(request.form.get("efectivo")),
        "yape": _to_decimal(request.form.get("yape")),
        "plin": _to_decimal(request.form.get("plin")),
        "giro": _to_decimal(request.form.get("giro")),
    }
    credito_aplicado = _to_decimal(request.form.get("credito_aplicado"))

    abonos: list[venta_service.AbonoDeudaInput] = []
    try:
        num_deudas = int(request.form.get("num_deudas", "0"))
    except ValueError:
        num_deudas = 0
    for i in range(num_deudas):
        cod = request.form.get(f"deuda_cod_{i}", "").strip()
        monto = _to_decimal(request.form.get(f"deuda_monto_{i}"))
        if cod and monto > 0:
            abonos.append(venta_service.AbonoDeudaInput(cod_item=cod, monto=monto))

    try:
        with session_scope() as db:
            result = venta_service.save_venta(
                db,
                fecha=fecha,
                items=items,
                metodos_pago=metodos_pago,
                cliente_data=cliente_data,
                actualizar_cliente=actualizar_cliente,
                credito_aplicado=credito_aplicado,
                abonos_deudas=abonos,
            )
            cod_items = [v.cod_item for v in result.ventas]
            audit_service.log(
                db,
                action="venta.created",
                entity_type="venta",
                entity_id=",".join(cod_items) if cod_items else None,
                after_state={
                    "fecha": fecha.isoformat(),
                    "cliente": nombre,
                    "cod_cliente": result.ventas[0].cod_cliente if result.ventas else None,
                    "items_count": len(result.ventas),
                    "cod_items": cod_items,
                    "credito_generado": str(result.excedente_credito_generado),
                    "abonos_deudas": str(result.abonos_deudas),
                },
            )
        msg = f"Venta guardada ({len(result.ventas)} ítem(s))"
        if result.excedente_credito_generado > 0:
            msg += f" — Crédito generado: S/ {result.excedente_credito_generado}"
        if result.abonos_deudas > 0:
            msg += f" — Abonos a deudas: S/ {result.abonos_deudas}"
        flash(msg)
    except (venta_service.ClienteNoExiste, venta_service.CreditoInsuficiente) as e:
        audit_service.log_isolated(
            action="venta.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")
    except (venta_service.TipoItemInvalido, ValueError) as e:
        audit_service.log_isolated(
            action="venta.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")
    except pago_service.AbonoCodItemInvalido as e:
        audit_service.log_isolated(
            action="venta.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")
    except cliente_service.ClienteDuplicadoError as e:
        audit_service.log_isolated(
            action="venta.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")
    except Exception as e:
        audit_service.log_isolated(
            action="venta.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")

    return redirect(url_for("views.index", tab="venta"))


@bp.post("/pagos")
def pagos_form():  # type: ignore[no-untyped-def]
    """POST /pagos — form-data del HTML legacy.

    Soporta dos formatos:
    - Nuevo: item_cod_0, item_monto_0, item_cod_1, item_monto_1, ...
    - Legacy: cod_item_pago[], monto_item_pago[], categoria_pago[]
    """
    fecha = _to_date(request.form.get("fecha_pago"))
    nombre_cliente = (request.form.get("cliente_pago") or "").strip()
    if not fecha or not nombre_cliente:
        flash("Error al guardar: fecha y cliente son requeridos.")
        return redirect(url_for("views.index", tab="pagos"))

    metodos_pago = {
        "efectivo": _to_decimal(request.form.get("efectivo_pago")),
        "yape": _to_decimal(request.form.get("yape_pago")),
        "plin": _to_decimal(request.form.get("plin_pago")),
        "giro": _to_decimal(request.form.get("giro_pago")),
    }
    notas = request.form.get("notas_pago") or None

    pagos_input: list[pago_service.PagoIndividualInput] = []
    try:
        n = int(request.form.get("num_items", "0"))
    except ValueError:
        n = 0

    if n > 0:
        for i in range(n):
            cod = request.form.get(f"item_cod_{i}", "").strip()
            monto = _to_decimal(request.form.get(f"item_monto_{i}"))
            if cod and monto > 0:
                pagos_input.append(
                    pago_service.PagoIndividualInput(cod_item=cod, monto=monto)
                )
    else:
        cod_items = request.form.getlist("cod_item_pago[]")
        montos = request.form.getlist("monto_item_pago[]")
        categorias = request.form.getlist("categoria_pago[]")
        if not cod_items:
            single_cod = request.form.get("cod_item_pago", "").strip()
            single_monto = request.form.get("monto_pago")
            if single_cod and single_monto:
                cod_items = [single_cod]
                montos = [single_monto]
                categorias = [request.form.get("categoria_pago", "")]
        for cod, monto, cat in zip(cod_items, montos, categorias or [None] * len(cod_items)):
            cod = cod.strip()
            monto_d = _to_decimal(monto)
            if cod and monto_d > 0:
                pagos_input.append(
                    pago_service.PagoIndividualInput(
                        cod_item=cod, monto=monto_d, categoria=cat or None
                    )
                )

    try:
        with session_scope() as db:
            cliente = db.execute(
                select(Cliente).where(
                    Cliente.activo.is_(True),
                    Cliente.nombre.ilike(nombre_cliente),
                )
            ).scalar_one_or_none()
            if cliente is None:
                cliente = cliente_service.get_or_create(
                    db,
                    nombre=nombre_cliente,
                )
            cod_cliente = cliente.cod_cliente

            pago_service.save_pagos_dia_posterior(
                db,
                cod_cliente=cod_cliente,
                fecha=fecha,
                metodos_pago=metodos_pago,
                pagos_explicitos=pagos_input,
                notas=notas,
            )
            audit_service.log(
                db,
                action="pago.created",
                entity_type="pago",
                entity_id=cod_cliente,
                after_state={
                    "cod_cliente": cod_cliente,
                    "cliente": nombre_cliente,
                    "fecha": fecha.isoformat(),
                    "items_count": len(pagos_input),
                    "cod_items": [p.cod_item for p in pagos_input],
                },
            )
        flash(f"Pagos guardados ({len(pagos_input)} ítem(s)).")
    except pago_service.AbonoCodItemInvalido as e:
        audit_service.log_isolated(
            action="pago.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre_cliente, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")
    except ValueError as e:
        audit_service.log_isolated(
            action="pago.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre_cliente, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")
    except Exception as e:
        audit_service.log_isolated(
            action="pago.created",
            result="failure",
            error_detail=str(e),
            metadata={"cliente": nombre_cliente, "fecha": fecha.isoformat()},
        )
        flash(f"Error al guardar: {e}")

    return redirect(url_for("views.index", tab="pagos"))
