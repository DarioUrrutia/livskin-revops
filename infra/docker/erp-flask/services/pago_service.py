"""PagoService — 4 tipos preservados del Flask actual (ADR-0011 v1.1).

Tipos:
- normal: pago regular de venta
- credito_generado: cliente pagó más, sobra → crédito a su favor
- credito_aplicado: usa crédito previo (NO cuenta en cobrado_total)
- abono_deuda: paga deuda anterior (de venta antigua)

Lógica de negocio densa preservada del Flask para no perder paridad con
producción al cutover (ADR-0023 § 6.7).
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

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
