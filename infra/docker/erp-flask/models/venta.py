"""Venta — flat 1-fila-por-item (ADR-0011 v1.1).

Preserva estructura del Flask actual: una fila = un item vendido.
Múltiples items en misma transacción = múltiples filas con mismo cliente+fecha.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class Venta(Base, TimestampMixin):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    num_secuencial: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    cod_cliente: Mapped[str] = mapped_column(
        String, ForeignKey("clientes.cod_cliente"), nullable=False
    )
    cliente_nombre: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cliente_telefono: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    tipo: Mapped[str] = mapped_column(String, nullable=False)
    cod_item: Mapped[str] = mapped_column(String, nullable=False)
    categoria: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    zona_cantidad_envase: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    proxima_cita: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_nac_cliente: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    moneda: Mapped[str] = mapped_column(String, nullable=False, default="PEN")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    efectivo: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    yape: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    plin: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    giro: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    debe: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    pagado: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    tc: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    precio_lista: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    descuento: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))

    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('Tratamiento', 'Producto', 'Certificado', 'Promocion')",
            name="ck_ventas_tipo_valido",
        ),
        Index("idx_ventas_cod_cliente_fecha", "cod_cliente", "fecha"),
        Index("idx_ventas_fecha", "fecha"),
        Index("idx_ventas_cod_item", "cod_item"),
    )
