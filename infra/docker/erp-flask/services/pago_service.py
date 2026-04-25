"""PagoService — 4 tipos preservados del Flask actual (ADR-0011 v1.1).

Tipos:
- normal: pago regular de venta
- credito_generado: cliente pagó más, sobra → crédito a su favor
- credito_aplicado: usa crédito previo (NO cuenta en cobrado_total)
- abono_deuda: paga deuda anterior (de venta antigua)

Lógica de negocio densa preservada del Flask para no perder paridad con
producción al cutover (ADR-0023 § 6.7).
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.cliente import Cliente
from models.pago import Pago
from models.venta import Venta
from services.codgen_service import next_codigo


VALID_TIPOS = {"normal", "credito_generado", "credito_aplicado", "abono_deuda"}


class PagoTipoInvalido(Exception):
    pass


class AbonoCodItemInvalido(Exception):
    """abono_deuda apunta a un cod_item que no existe en ventas (abono fantasma)."""
    pass


def create_pago(
    db: Session,
    cod_cliente: str,
    fecha: date,
    monto: Decimal,
    tipo_pago: str,
    cod_item: Optional[str] = None,
    categoria: Optional[str] = None,
    cliente_nombre: Optional[str] = None,
    efectivo: Optional[Decimal] = None,
    yape: Optional[Decimal] = None,
    plin: Optional[Decimal] = None,
    giro: Optional[Decimal] = None,
    notas: Optional[str] = None,
    created_by: Optional[int] = None,
) -> Pago:
    if tipo_pago not in VALID_TIPOS:
        raise PagoTipoInvalido(
            f"tipo_pago '{tipo_pago}' no valido. Valores: {sorted(VALID_TIPOS)}"
        )

    if tipo_pago == "abono_deuda" and cod_item:
        existe = db.execute(
            select(Venta.id).where(Venta.cod_item == cod_item)
        ).scalar_one_or_none()
        if existe is None:
            raise AbonoCodItemInvalido(
                f"cod_item '{cod_item}' no existe en ventas; no se puede crear abono"
            )

    cod_pago = next_codigo(db, Pago, "cod_pago", "LIVPAGO")

    pago = Pago(
        cod_pago=cod_pago,
        fecha=fecha,
        cod_cliente=cod_cliente,
        cliente_nombre=cliente_nombre,
        cod_item=cod_item,
        categoria=categoria,
        monto=monto,
        efectivo=efectivo,
        yape=yape,
        plin=plin,
        giro=giro,
        tipo_pago=tipo_pago,
        notas=notas,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(pago)
    db.flush()
    return pago


def list_by_cliente(db: Session, cod_cliente: str) -> list[Pago]:
    return list(
        db.execute(
            select(Pago)
            .where(Pago.cod_cliente == cod_cliente)
            .order_by(Pago.fecha.desc(), Pago.id.desc())
        )
        .scalars()
        .all()
    )


def list_by_item(db: Session, cod_item: str) -> list[Pago]:
    return list(
        db.execute(
            select(Pago).where(Pago.cod_item == cod_item).order_by(Pago.fecha, Pago.id)
        )
        .scalars()
        .all()
    )


def total_pagado_for_item(db: Session, cod_item: str) -> Decimal:
    """Suma de TODOS los pagos linkeados a un cod_item específico.

    Incluye credito_aplicado: cuando un cliente aplica crédito previo a un
    item, eso reduce el DEBE de ese item (es "pago" desde la perspectiva
    del item, aunque a nivel agregado no sea dinero nuevo).

    Para el cálculo de cobrado_total agregado del cliente, usar otra función
    que excluya credito_aplicado (ese sí es transferencia interna sin
    dinero nuevo).
    """
    result = db.execute(
        select(func.coalesce(func.sum(Pago.monto), 0)).where(
            Pago.cod_item == cod_item,
        )
    ).scalar()
    return Decimal(result or 0)


@dataclass
class PagoIndividualInput:
    """Pago individual a un cod_item específico (input para save_pagos_dia_posterior)."""
    cod_item: str
    monto: Decimal
    categoria: Optional[str] = None
    notas: Optional[str] = None


@dataclass
class SavePagosResult:
    pagos: list[Pago] = field(default_factory=list)
    total_pagos_explicitos: Decimal = Decimal("0")
    auto_abonos_total: Decimal = Decimal("0")
    excedente_credito_generado: Decimal = Decimal("0")


def save_pagos_dia_posterior(
    db: Session,
    cod_cliente: str,
    fecha: date,
    metodos_pago: dict[str, Decimal],
    pagos_explicitos: list[PagoIndividualInput],
    auto_aplicar_a_deudas: bool = True,
    notas: Optional[str] = None,
    created_by: Optional[int] = None,
) -> SavePagosResult:
    """Endpoint /api/pagos: pagos día posterior, sin nueva venta.

    Casos de uso:
    - Cliente vuelve días después solo a pagar deudas
    - Pago parcial a multiples deudas en un solo evento
    - Pago adelantado (sin deudas → genera crédito)

    Lógica:
    1. Validar cliente existe
    2. Crear pagos explícitos (cada cod_item se valida vía AbonoCodItemInvalido)
    3. Si auto_aplicar=True y leftover > 0: aplicar FIFO a deudas restantes
    4. Si todavía leftover: credito_generado por sobrante
    """
    cliente = db.execute(
        select(Cliente).where(Cliente.cod_cliente == cod_cliente)
    ).scalar_one_or_none()
    if cliente is None:
        raise ValueError(f"Cliente {cod_cliente} no existe")

    metodos_pago = {k: Decimal(str(v)) for k, v in metodos_pago.items()}
    total_cash = sum(metodos_pago.values(), Decimal("0"))

    if total_cash <= 0:
        raise ValueError("Total de métodos de pago debe ser > 0")

    result = SavePagosResult()

    cod_items_pagados: set[str] = set()
    total_explicitos = Decimal("0")

    for pago_in in pagos_explicitos:
        if pago_in.monto <= 0:
            continue
        pago = create_pago(
            db,
            cod_cliente=cod_cliente,
            fecha=fecha,
            monto=pago_in.monto,
            tipo_pago="abono_deuda",
            cod_item=pago_in.cod_item,
            categoria=pago_in.categoria,
            cliente_nombre=cliente.nombre,
            notas=pago_in.notas or notas or f"Pago a {pago_in.cod_item}",
            created_by=created_by,
        )
        result.pagos.append(pago)
        cod_items_pagados.add(pago_in.cod_item)
        total_explicitos += pago_in.monto

    result.total_pagos_explicitos = total_explicitos

    if total_explicitos > total_cash + Decimal("0.01"):
        raise ValueError(
            f"Suma de pagos explicitos ({total_explicitos}) excede el cash recibido ({total_cash})"
        )

    leftover = total_cash - total_explicitos

    auto_abonos_total = Decimal("0")
    if auto_aplicar_a_deudas and leftover > Decimal("0.01"):
        deudas_query = select(Venta).where(
            Venta.cod_cliente == cod_cliente,
            Venta.debe > 0,
        )
        if cod_items_pagados:
            deudas_query = deudas_query.where(~Venta.cod_item.in_(cod_items_pagados))
        deudas_query = deudas_query.order_by(Venta.fecha, Venta.id)

        deudas_abiertas = list(db.execute(deudas_query).scalars().all())

        for deuda in deudas_abiertas:
            if leftover <= Decimal("0.01"):
                break
            debe_actual = deuda.debe or Decimal("0")
            if debe_actual <= 0:
                continue
            monto_abono = min(debe_actual, leftover).quantize(Decimal("0.01"))
            if monto_abono <= 0:
                continue
            pago_auto = create_pago(
                db,
                cod_cliente=cod_cliente,
                fecha=fecha,
                monto=monto_abono,
                tipo_pago="abono_deuda",
                cod_item=deuda.cod_item,
                categoria=deuda.categoria,
                cliente_nombre=cliente.nombre,
                notas=f"Auto-abono a {deuda.cod_item} (deuda anterior FIFO)",
                created_by=created_by,
            )
            result.pagos.append(pago_auto)
            leftover -= monto_abono
            auto_abonos_total += monto_abono

    result.auto_abonos_total = auto_abonos_total

    if leftover > Decimal("0.01"):
        pago_credito = create_pago(
            db,
            cod_cliente=cod_cliente,
            fecha=fecha,
            monto=leftover,
            tipo_pago="credito_generado",
            cliente_nombre=cliente.nombre,
            notas=f"Crédito generado por excedente del {fecha}",
            created_by=created_by,
        )
        result.pagos.append(pago_credito)
        result.excedente_credito_generado = leftover

    db.flush()
    return result


def credito_balance(db: Session, cod_cliente: str) -> Decimal:
    """Crédito disponible del cliente = sum(credito_generado) - sum(credito_aplicado)."""
    generado = (
        db.execute(
            select(func.coalesce(func.sum(Pago.monto), 0)).where(
                Pago.cod_cliente == cod_cliente,
                Pago.tipo_pago == "credito_generado",
            )
        ).scalar()
        or 0
    )
    aplicado = (
        db.execute(
            select(func.coalesce(func.sum(Pago.monto), 0)).where(
                Pago.cod_cliente == cod_cliente,
                Pago.tipo_pago == "credito_aplicado",
            )
        ).scalar()
        or 0
    )
    return Decimal(generado) - Decimal(aplicado)
