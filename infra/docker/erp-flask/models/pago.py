"""Pago — cobros y créditos (ADR-0011 v1.1).

Preserva los 4 tipos del Flask actual:
- normal: pago regular de venta
- credito_generado: cliente pagó más, sobra → crédito a su favor
- credito_aplicado: usa crédito previo (NO cuenta en cobrado_total)
- abono_deuda: paga deuda anterior

Un pago vincula a venta vía cod_item (FK lógico, no duro: abono_deuda
puede no tener venta asociada actual).
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class Pago(Base, TimestampMixin):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    num_secuencial: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cod_pago: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    cod_cliente: Mapped[str] = mapped_column(
        String, ForeignKey("clientes.cod_cliente"), nullable=False
    )
    cliente_nombre: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    cod_item: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    categoria: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    efectivo: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    yape: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    plin: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    giro: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    tipo_pago: Mapped[str] = mapped_column(String, nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "tipo_pago IN ('normal', 'credito_generado', 'credito_aplicado', 'abono_deuda')",
            name="ck_pagos_tipo_valido",
        ),
        Index("idx_pagos_cod_item", "cod_item"),
        Index("idx_pagos_cod_cliente_fecha", "cod_cliente", "fecha"),
        Index("idx_pagos_tipo_pago", "tipo_pago"),
    )
