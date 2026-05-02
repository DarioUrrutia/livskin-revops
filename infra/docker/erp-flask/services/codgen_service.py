"""Generador de códigos LIVXXXX#### (ADR-0014).

Patrón: prefijo (LIVCLIENT/LIVTRAT/LIVPROD/LIVPAGO/...) + 4+ dígitos
con padding zero. Cuando supere 9999 → 5 dígitos automático.

Implementación: SELECT MAX + 1 con pg_advisory_xact_lock por prefijo para
prevenir race conditions cuando múltiples transacciones concurrentes generan
códigos del mismo prefijo. El advisory lock se libera automáticamente al
COMMIT/ROLLBACK de la transacción.

Pre-cutover (Fase 6) se puede migrar a Postgres SEQUENCEs si necesario;
este patrón cumple para volumen MVP.
"""
import hashlib
import re
from typing import Type

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from models.base import Base


def _advisory_lock_key(prefijo: str) -> int:
    """Genera int64 estable a partir del prefijo para usar con pg_advisory_xact_lock.

    Postgres acepta bigint signed (-2^63 a 2^63-1). Usamos los primeros 8 bytes
    de SHA-256 como signed bigint (puede ser negativo, válido).
    """
    h = hashlib.sha256(prefijo.encode()).digest()[:8]
    return int.from_bytes(h, byteorder="big", signed=True)


def _acquire_lock(db: Session, prefijo: str) -> None:
    """Bloquea generación concurrente de códigos del mismo prefijo dentro de la transacción.

    pg_advisory_xact_lock se libera automáticamente al COMMIT/ROLLBACK.
    Si otra transacción tiene el lock, esta espera (no race).
    """
    key = _advisory_lock_key(prefijo)
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})


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
    """Genera próximo código tipo LIVXXXX#### con lock atomicidad.

    Args:
        db: sesión SQLAlchemy (debe estar dentro de una transacción)
        model: clase del modelo (ej: Cliente)
        col_name: nombre de la columna que tiene el código (ej: 'cod_cliente')
        prefijo: prefijo del código (ej: 'LIVCLIENT')

    Returns:
        Código nuevo (ej: 'LIVCLIENT0136')

    Concurrency: usa pg_advisory_xact_lock para serializar generación por prefijo.
    Otras transacciones concurrentes con el mismo prefijo esperan hasta el COMMIT.
    """
    _acquire_lock(db, prefijo)
    return _format_codigo(prefijo, _max_existing(db, model, col_name, prefijo) + 1)


def next_codigos_batch(
    db: Session, model: Type[Base], col_name: str, prefijo: str, count: int
) -> list[str]:
    """Genera N códigos consecutivos en un solo lookup.

    Crítico para casos donde múltiples registros del mismo prefijo se crean
    en la misma transacción (ej: venta con múltiples items del mismo tipo).
    Usar next_codigo() en loop daría duplicados porque cada llamada lee max
    desde DB sin ver los pendientes.

    Concurrency: igual que next_codigo, usa pg_advisory_xact_lock.
    """
    if count <= 0:
        return []
    _acquire_lock(db, prefijo)
    base = _max_existing(db, model, col_name, prefijo)
    return [_format_codigo(prefijo, base + i) for i in range(1, count + 1)]
