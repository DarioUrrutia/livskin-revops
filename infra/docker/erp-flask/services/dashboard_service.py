"""DashboardService — KPIs + agregaciones del Flask original.

Replica el shape de GET /api/dashboard preservando contrato HTTP. Calcula:
- KPIs core (ventas/cobrado/pendiente/ticket/tasa/balance)
- Distribución por método de pago (efectivo/yape/plin/giro)
- Distribución por tipo (Tratamiento/Producto/Otro)
- Series temporales por mes
- Top clientes (10) y top 20% con detalles
- Top categorías (10) y top mes actual (8)
- Recientes (ventas + pagos)
- Comparativas mes actual vs anterior + año actual vs anterior
- Aging deudores (4 buckets)
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from models.cliente import Cliente
from models.gasto import Gasto
from models.pago import Pago
from models.venta import Venta


def _f(v: Any) -> float:
    return float(v) if v is not None else 0.0


def compute_dashboard(
    db: Session,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
) -> dict[str, Any]:
    today = date.today()

    ventas_w = []
    if desde:
        ventas_w.append(Venta.fecha >= desde)
    if hasta:
        ventas_w.append(Venta.fecha <= hasta)

    pagos_w = []
    if desde:
        pagos_w.append(Pago.fecha >= desde)
    if hasta:
        pagos_w.append(Pago.fecha <= hasta)

    pagos_w_no_credito = pagos_w + [Pago.tipo_pago != "credito_aplicado"]

    gastos_w = []
    if desde:
        gastos_w.append(Gasto.fecha >= desde)
    if hasta:
        gastos_w.append(Gasto.fecha <= hasta)

    ventas_total = _f(
        db.execute(select(func.coalesce(func.sum(Venta.total), 0)).where(*ventas_w)).scalar()
    )
    cobrado_total = _f(
        db.execute(
            select(func.coalesce(func.sum(Pago.monto), 0)).where(*pagos_w_no_credito)
        ).scalar()
    )
    pendiente_total = _f(
        db.execute(select(func.coalesce(func.sum(Venta.debe), 0)).where(*ventas_w)).scalar()
    )
    total_gastos = _f(
        db.execute(select(func.coalesce(func.sum(Gasto.monto), 0)).where(*gastos_w)).scalar()
    )
    num_atenciones = (
        db.execute(select(func.count(Venta.id)).where(*ventas_w)).scalar() or 0
    )
    num_clientes = (
        db.execute(
            select(func.count(func.distinct(Venta.cod_cliente))).where(*ventas_w)
        ).scalar()
        or 0
    )
    num_promociones = (
        db.execute(
            select(func.count(Venta.id)).where(*ventas_w, Venta.descuento > 0)
        ).scalar()
        or 0
    )
    total_descuentos = _f(
        db.execute(
            select(func.coalesce(func.sum(Venta.descuento), 0)).where(*ventas_w)
        ).scalar()
    )

    ticket_promedio = ventas_total / num_atenciones if num_atenciones > 0 else 0.0
    tasa_cobro = (cobrado_total / ventas_total * 100) if ventas_total > 0 else 0.0
    balance_neto = cobrado_total - total_gastos

    metodos_ventas = db.execute(
        select(
            func.coalesce(func.sum(Venta.efectivo), 0),
            func.coalesce(func.sum(Venta.yape), 0),
            func.coalesce(func.sum(Venta.plin), 0),
            func.coalesce(func.sum(Venta.giro), 0),
        ).where(*ventas_w)
    ).one()
    ef_efectivo, ef_yape, ef_plin, ef_giro = (_f(x) for x in metodos_ventas)

    metodos_pagos = db.execute(
        select(
            func.coalesce(func.sum(Pago.efectivo), 0),
            func.coalesce(func.sum(Pago.yape), 0),
            func.coalesce(func.sum(Pago.plin), 0),
            func.coalesce(func.sum(Pago.giro), 0),
        ).where(*pagos_w_no_credito)
    ).one()
    pagos_ef_efectivo, pagos_ef_yape, pagos_ef_plin, pagos_ef_giro = (_f(x) for x in metodos_pagos)

    tipo_aggs = db.execute(
        select(
            Venta.tipo,
            func.coalesce(func.sum(Venta.total), 0),
        )
        .where(*ventas_w)
        .group_by(Venta.tipo)
    ).all()
    tipo_map = {t: _f(s) for t, s in tipo_aggs}
    total_tratamientos = tipo_map.get("Tratamiento", 0.0)
    total_productos = tipo_map.get("Producto", 0.0)
    total_otros = sum(v for k, v in tipo_map.items() if k not in ("Tratamiento", "Producto"))

    por_mes_rows = db.execute(
        select(
            func.to_char(Venta.fecha, "YYYY-MM").label("mes"),
            func.coalesce(func.sum(Venta.total), 0).label("total"),
            func.coalesce(func.sum(Venta.pagado), 0).label("cobrado"),
            func.coalesce(func.sum(Venta.debe), 0).label("debe"),
        )
        .where(*ventas_w)
        .group_by("mes")
        .order_by("mes")
    ).all()
    por_mes = [
        {"mes": r.mes, "total": _f(r.total), "cobrado": _f(r.cobrado), "debe": _f(r.debe)}
        for r in por_mes_rows
    ]

    top_clientes_rows = db.execute(
        select(
            Venta.cliente_nombre.label("cliente"),
            func.coalesce(func.sum(Venta.total), 0).label("total"),
            func.count(func.distinct(Venta.fecha)).label("visitas"),
        )
        .where(*ventas_w, Venta.cliente_nombre.is_not(None))
        .group_by(Venta.cliente_nombre)
        .order_by(func.sum(Venta.total).desc())
        .limit(10)
    ).all()
    top_clientes = [
        {"cliente": r.cliente, "total": _f(r.total), "visitas": int(r.visitas or 0)}
        for r in top_clientes_rows
    ]

    n_top20 = max(1, int(num_clientes * 0.2)) if num_clientes else 0
    top20_rows = db.execute(
        select(
            Venta.cliente_nombre.label("cliente"),
            Venta.cod_cliente.label("cod_cliente"),
            func.coalesce(func.sum(Venta.total), 0).label("total"),
            func.count(func.distinct(Venta.fecha)).label("visitas"),
            func.coalesce(func.sum(Venta.debe), 0).label("debe"),
        )
        .where(*ventas_w, Venta.cliente_nombre.is_not(None))
        .group_by(Venta.cliente_nombre, Venta.cod_cliente)
        .order_by(func.sum(Venta.total).desc())
        .limit(n_top20)
    ).all() if n_top20 else []
    top20_clientes = [
        {
            "cliente": r.cliente,
            "total": _f(r.total),
            "visitas": int(r.visitas or 0),
            "debe": _f(r.debe),
        }
        for r in top20_rows
    ]

    cats_rows = db.execute(
        select(
            Venta.categoria.label("categoria"),
            func.coalesce(func.sum(Venta.total), 0).label("total"),
            func.count(Venta.id).label("count"),
        )
        .where(*ventas_w, Venta.tipo != "Promocion", Venta.categoria.is_not(None))
        .group_by(Venta.categoria)
        .order_by(func.sum(Venta.total).desc())
        .limit(10)
    ).all()
    por_categoria = [
        {"categoria": r.categoria, "total": _f(r.total), "count": int(r.count or 0)}
        for r in cats_rows
    ]

    mes_actual_start = today.replace(day=1)
    if mes_actual_start.month == 1:
        mes_ant_start = mes_actual_start.replace(year=mes_actual_start.year - 1, month=12)
    else:
        mes_ant_start = mes_actual_start.replace(month=mes_actual_start.month - 1)
    mes_actual_str = mes_actual_start.strftime("%Y-%m")
    mes_ant_str = mes_ant_start.strftime("%Y-%m")

    top_cats_mes_rows = db.execute(
        select(
            Venta.categoria.label("cat"),
            func.coalesce(func.sum(Venta.total), 0).label("total"),
        )
        .where(
            Venta.fecha >= mes_actual_start,
            Venta.fecha <= today,
            Venta.tipo != "Promocion",
            Venta.categoria.is_not(None),
        )
        .group_by(Venta.categoria)
        .order_by(func.sum(Venta.total).desc())
        .limit(8)
    ).all()
    top_cats_mes = [{"cat": r.cat, "total": _f(r.total)} for r in top_cats_mes_rows]

    recientes_rows = db.execute(
        select(Venta).order_by(Venta.fecha.desc(), Venta.id.desc()).limit(20)
    ).scalars().all()
    recientes = [
        {
            "fecha": v.fecha.isoformat(),
            "cliente": v.cliente_nombre or "",
            "categoria": v.categoria or "",
            "total": _f(v.total),
            "debe": _f(v.debe),
        }
        for v in recientes_rows
    ]

    pagos_recientes_rows = db.execute(
        select(Pago)
        .where(Pago.tipo_pago != "credito_aplicado")
        .order_by(Pago.fecha.desc(), Pago.id.desc())
        .limit(20)
    ).scalars().all()

    def _metodo_str(p: Pago) -> str:
        partes = []
        if p.efectivo and p.efectivo > 0:
            partes.append("Efectivo")
        if p.yape and p.yape > 0:
            partes.append("Yape")
        if p.plin and p.plin > 0:
            partes.append("Plin")
        if p.giro and p.giro > 0:
            partes.append("Giro")
        return " + ".join(partes) if partes else "-"

    pagos_recientes = [
        {
            "fecha": p.fecha.isoformat(),
            "cliente": p.cliente_nombre or "",
            "monto": _f(p.monto),
            "metodo": _metodo_str(p),
            "categoria": p.categoria or "",
            "cod_item": p.cod_item or "",
        }
        for p in pagos_recientes_rows
    ]

    año_actual = today.year
    año_anterior = año_actual - 1

    comp_mes_actual = _f(
        db.execute(
            select(func.coalesce(func.sum(Venta.total), 0)).where(
                Venta.fecha >= mes_actual_start, Venta.fecha <= today
            )
        ).scalar()
    )
    comp_mes_anterior = _f(
        db.execute(
            select(func.coalesce(func.sum(Venta.total), 0)).where(
                Venta.fecha >= mes_ant_start, Venta.fecha < mes_actual_start
            )
        ).scalar()
    )
    comp_mes_delta = (
        ((comp_mes_actual - comp_mes_anterior) / comp_mes_anterior * 100)
        if comp_mes_anterior > 0
        else 0.0
    )

    año_actual_start = date(año_actual, 1, 1)
    año_anterior_start = date(año_anterior, 1, 1)
    año_anterior_end = date(año_anterior, 12, 31)

    comp_año_actual = _f(
        db.execute(
            select(func.coalesce(func.sum(Venta.total), 0)).where(
                Venta.fecha >= año_actual_start, Venta.fecha <= today
            )
        ).scalar()
    )
    comp_año_anterior = _f(
        db.execute(
            select(func.coalesce(func.sum(Venta.total), 0)).where(
                Venta.fecha >= año_anterior_start, Venta.fecha <= año_anterior_end
            )
        ).scalar()
    )
    comp_año_delta = (
        ((comp_año_actual - comp_año_anterior) / comp_año_anterior * 100)
        if comp_año_anterior > 0
        else 0.0
    )

    tipo_mes_actual_rows = db.execute(
        select(
            Venta.tipo,
            func.coalesce(func.sum(Venta.total), 0),
        )
        .where(Venta.fecha >= mes_actual_start, Venta.fecha <= today)
        .group_by(Venta.tipo)
    ).all()
    tipo_mes_actual_map = {t: _f(s) for t, s in tipo_mes_actual_rows}
    tipo_mes_actual = {
        "Tratamiento": tipo_mes_actual_map.get("Tratamiento", 0.0),
        "Producto": tipo_mes_actual_map.get("Producto", 0.0),
        "Otro": sum(
            v for k, v in tipo_mes_actual_map.items() if k not in ("Tratamiento", "Producto")
        ),
    }

    tipo_mes_anterior_rows = db.execute(
        select(
            Venta.tipo,
            func.coalesce(func.sum(Venta.total), 0),
        )
        .where(Venta.fecha >= mes_ant_start, Venta.fecha < mes_actual_start)
        .group_by(Venta.tipo)
    ).all()
    tipo_mes_anterior_map = {t: _f(s) for t, s in tipo_mes_anterior_rows}
    tipo_mes_anterior = {
        "Tratamiento": tipo_mes_anterior_map.get("Tratamiento", 0.0),
        "Producto": tipo_mes_anterior_map.get("Producto", 0.0),
        "Otro": sum(
            v for k, v in tipo_mes_anterior_map.items() if k not in ("Tratamiento", "Producto")
        ),
    }

    deudores_aging = _compute_aging(db, today)

    return {
        "ventas_total": ventas_total,
        "cobrado_total": cobrado_total,
        "pendiente_total": pendiente_total,
        "ticket_promedio": ticket_promedio,
        "tasa_cobro": tasa_cobro,
        "balance_neto": balance_neto,
        "total_gastos": total_gastos,
        "num_atenciones": int(num_atenciones),
        "num_clientes": int(num_clientes),
        "num_promociones": int(num_promociones),
        "total_descuentos": total_descuentos,
        "ef_efectivo": ef_efectivo,
        "ef_yape": ef_yape,
        "ef_plin": ef_plin,
        "ef_giro": ef_giro,
        "pagos_ef_efectivo": pagos_ef_efectivo,
        "pagos_ef_yape": pagos_ef_yape,
        "pagos_ef_plin": pagos_ef_plin,
        "pagos_ef_giro": pagos_ef_giro,
        "total_tratamientos": total_tratamientos,
        "total_productos": total_productos,
        "total_otros": total_otros,
        "por_mes": por_mes,
        "top_clientes": top_clientes,
        "top20_clientes": top20_clientes,
        "por_categoria": por_categoria,
        "top_cats_mes": top_cats_mes,
        "recientes": recientes,
        "pagos_recientes": pagos_recientes,
        "comp_mes_actual": comp_mes_actual,
        "comp_mes_anterior": comp_mes_anterior,
        "comp_mes_delta": comp_mes_delta,
        "comp_año_actual": comp_año_actual,
        "comp_año_anterior": comp_año_anterior,
        "comp_año_delta": comp_año_delta,
        "tipo_mes_actual": tipo_mes_actual,
        "tipo_mes_anterior": tipo_mes_anterior,
        "mes_actual_str": mes_actual_str,
        "mes_ant_str": mes_ant_str,
        "deudores_aging": deudores_aging,
        "pendientes_pago": deudores_aging,
    }


def _compute_aging(db: Session, today: date) -> dict[str, Any]:
    """Aging deudores en 4 buckets: <30 / 30-60 / 60-90 / >90 días."""
    deudas = list(
        db.execute(
            select(Venta).where(Venta.debe > 0).order_by(Venta.fecha)
        ).scalars().all()
    )

    buckets: dict[str, dict[str, Any]] = {
        "menos_30": {"total": 0.0, "count": 0, "items": []},
        "30_60": {"total": 0.0, "count": 0, "items": []},
        "60_90": {"total": 0.0, "count": 0, "items": []},
        "mas_90": {"total": 0.0, "count": 0, "items": []},
    }

    for v in deudas:
        dias = (today - v.fecha).days
        if dias < 30:
            key = "menos_30"
        elif dias < 60:
            key = "30_60"
        elif dias < 90:
            key = "60_90"
        else:
            key = "mas_90"

        debe_f = _f(v.debe)
        buckets[key]["total"] += debe_f
        buckets[key]["count"] += 1
        buckets[key]["items"].append(
            {
                "cliente": v.cliente_nombre or "",
                "categoria": v.categoria or "",
                "debe": debe_f,
                "fecha": v.fecha.isoformat(),
                "dias": dias,
                "cod_item": v.cod_item,
            }
        )

    return buckets
