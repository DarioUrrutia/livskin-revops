"""LibroService — export plano de ventas, pagos y gastos.

Replica /api/libro del Flask original (preserva contrato HTTP — keys
snake_case en cada fila, exclusión de filas vacías).
"""
from datetime import date
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.gasto import Gasto
from models.pago import Pago
from models.venta import Venta


def _f(v: Any) -> float:
    return float(v) if v is not None else 0.0


def _venta_row(v: Venta) -> dict[str, Any]:
    return {
        "num": v.num_secuencial or "",
        "fecha": v.fecha.isoformat(),
        "cod_cliente": v.cod_cliente,
        "cliente": v.cliente_nombre or "",
        "telefono": v.cliente_telefono or "",
        "tipo": v.tipo,
        "cod_item": v.cod_item,
        "categoria": v.categoria or "",
        "zona": v.zona_cantidad_envase or "",
        "proxima_cita": v.proxima_cita.isoformat() if v.proxima_cita else "",
        "fecha_nac": v.fecha_nac_cliente.isoformat() if v.fecha_nac_cliente else "",
        "moneda": v.moneda,
        "total": _f(v.total),
        "efectivo": _f(v.efectivo),
        "yape": _f(v.yape),
        "plin": _f(v.plin),
        "giro": _f(v.giro),
        "debe": _f(v.debe),
        "pagado": _f(v.pagado),
        "tc": str(v.tc) if v.tc else "",
        "precio_lista": _f(v.precio_lista),
        "descuento": _f(v.descuento or 0),
    }


def _pago_row(p: Pago) -> dict[str, Any]:
    return {
        "num": p.num_secuencial or "",
        "fecha": p.fecha.isoformat(),
        "cod_cliente": p.cod_cliente,
        "cliente": p.cliente_nombre or "",
        "monto": _f(p.monto),
        "efectivo": _f(p.efectivo),
        "yape": _f(p.yape),
        "plin": _f(p.plin),
        "giro": _f(p.giro),
        "notas": p.notas or "",
        "cod_item": p.cod_item or "",
        "categoria": p.categoria or "",
        "cod_pago": p.cod_pago,
        "tipo_pago": p.tipo_pago,
    }


def _gasto_row(g: Gasto) -> dict[str, Any]:
    return {
        "num": g.num_secuencial or "",
        "fecha": g.fecha.isoformat(),
        "tipo": g.tipo or "",
        "descripcion": g.descripcion or "",
        "destinatario": g.destinatario or "",
        "monto": _f(g.monto),
        "metodo_pago": g.metodo_pago or "",
    }


def compute_libro(
    db: Session,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
) -> dict[str, Any]:
    ventas_q = select(Venta)
    if desde:
        ventas_q = ventas_q.where(Venta.fecha >= desde)
    if hasta:
        ventas_q = ventas_q.where(Venta.fecha <= hasta)
    ventas_q = ventas_q.order_by(Venta.fecha, Venta.id)

    pagos_q = select(Pago)
    if desde:
        pagos_q = pagos_q.where(Pago.fecha >= desde)
    if hasta:
        pagos_q = pagos_q.where(Pago.fecha <= hasta)
    pagos_q = pagos_q.order_by(Pago.fecha, Pago.id)

    gastos_q = select(Gasto)
    if desde:
        gastos_q = gastos_q.where(Gasto.fecha >= desde)
    if hasta:
        gastos_q = gastos_q.where(Gasto.fecha <= hasta)
    gastos_q = gastos_q.order_by(Gasto.fecha, Gasto.id)

    return {
        "ventas": [_venta_row(v) for v in db.execute(ventas_q).scalars()],
        "pagos": [_pago_row(p) for p in db.execute(pagos_q).scalars()],
        "gastos": [_gasto_row(g) for g in db.execute(gastos_q).scalars()],
    }
