"""Catálogo — listas editables (ADR-0011 v1.1, ADR-0014).

Reemplaza la hoja "Listas" del Sheets. Una fila = una entrada de cualquier
catálogo (tipo, cat_Tratamiento, cat_Producto, area, fuente, etc.).

Las listas EDITABLES por admin via UI son las "data-only" (cat_*, area).
Las "code-tied" (estado_lead, intent_level, etc.) se gestionan junto con
cambios de código.
"""
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class Catalogo(Base, TimestampMixin):
    __tablename__ = "catalogos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lista: Mapped[str] = mapped_column(String, nullable=False)
    valor: Mapped[str] = mapped_column(String, nullable=False)
    orden: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("lista", "valor", name="uq_catalogos_lista_valor"),
        Index("idx_catalogos_lista_activo", "lista", "activo"),
    )
