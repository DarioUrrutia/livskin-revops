"""Generador de códigos LIVXXXX#### (ADR-0014).

Patrón: prefijo (LIVCLIENT/LIVTRAT/LIVPROD/LIVPAGO/...) + 4+ dígitos
con padding zero. Cuando supere 9999 → 5 dígitos automático.

Implementación MVP: SELECT MAX + 1, hecho dentro de transacción para
prevenir race conditions con SELECT FOR UPDATE.
Pre-cutover (Fase 6) se puede migrar a Postgres SEQUENCEs si necesario.
"""
import re
from typing import Type

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.base import Base


def _max_existing(db: Session, model: Type[Base], col_name: str, prefijo: str) -> int:
    col = getattr(model, col_name)
    pattern = re.compile(rf"^{prefijo}(\d+)$")
    rows = db.execute(select(col).where(col.like(f"{prefijo}%"))).scalars().all()
    max_num = 0
    for codigo in rows:
        match = pattern.match(codigo)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return max_num


def _format_codigo(prefijo: str, num: int) -> str:
    width = max(4, len(str(num)))
    return f"{prefijo}{num:0{width}d}"


def next_codigo(db: Session, model: Type[Base], col_name: str, prefijo: str) -> str:
    """Genera próximo código tipo LIVXXXX####.

    Args:
        db: sesión SQLAlchemy
        model: clase del modelo (ej: Cliente)
        col_name: nombre de la columna que tiene el código (ej: 'cod_cliente')
        prefijo: prefijo del código (ej: 'LIVCLIENT')

    Returns:
        Código nuevo (ej: 'LIVCLIENT0136')
    """
    return _format_codigo(prefijo, _max_existing(db, model, col_name, prefijo) + 1)


def next_codigos_batch(
    db: Session, model: Type[Base], col_name: str, prefijo: str, count: int
) -> list[str]:
    """Genera N códigos consecutivos en un solo lookup.

    Crítico para casos donde múltiples registros del mismo prefijo se crean
    en la misma transacción (ej: venta con múltiples items del mismo tipo).
    Usar next_codigo() en loop daría duplicados porque cada llamada lee max
    desde DB sin ver los pendientes.
    """
    if count <= 0:
        return []
    base = _max_existing(db, model, col_name, prefijo)
    return [_format_codigo(prefijo, base + i) for i in range(1, count + 1)]
