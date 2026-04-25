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

    next_num = max_num + 1
    width = max(4, len(str(next_num)))
    return f"{prefijo}{next_num:0{width}d}"
