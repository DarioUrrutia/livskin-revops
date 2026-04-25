"""GastoService — egresos operativos (ADR-0011 v1.1).

CRUD simple. Sin lógica especial — gastos son registro plano.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.gasto import Gasto


class GastoNotFoundError(Exception):
    pass


def get_by_id(db: Session, gasto_id: int) -> Gasto:
    gasto = db.get(Gasto, gasto_id)
    if gasto is None:
        raise GastoNotFoundError(f"Gasto id={gasto_id} no existe")
    return gasto


def list_recent(
    db: Session, limit: int = 100, offset: int = 0, fecha_desde: Optional[date] = None
) -> list[Gasto]:
    stmt = select(Gasto)
    if fecha_desde:
        stmt = stmt.where(Gasto.fecha >= fecha_desde)
    return list(
        db.execute(stmt.order_by(Gasto.fecha.desc(), Gasto.id.desc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )


def create(
    db: Session,
    fecha: date,
    monto: Decimal,
    tipo: Optional[str] = None,
    descripcion: Optional[str] = None,
    destinatario: Optional[str] = None,
    metodo_pago: Optional[str] = None,
    notas: Optional[str] = None,
    created_by: Optional[int] = None,
) -> Gasto:
    gasto = Gasto(
        fecha=fecha,
        tipo=tipo,
        descripcion=descripcion,
        destinatario=destinatario,
        monto=monto,
        metodo_pago=metodo_pago,
        notas=notas,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(gasto)
    db.flush()
    return gasto
