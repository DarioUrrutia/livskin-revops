"""Gasto — egresos operativos (ADR-0011 v1.1).

Preservado del Flask actual. Simple, sin FK a clientes.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class Gasto(Base, TimestampMixin):
    __tablename__ = "gastos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    num_secuencial: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    destinatario: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    metodo_pago: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
