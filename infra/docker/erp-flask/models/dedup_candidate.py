"""DedupCandidate — casos ambiguos para revisión manual (ADR-0013 v2).

Se generan cuando un nuevo lead/cliente coincide solo por nombre (no por
phone ni email). Admin (Dario) los revisa via UI y decide merge o keep separate.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models.base import Base


class DedupCandidate(Base):
    __tablename__ = "dedup_candidates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    nuevo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nuevo_tipo: Mapped[str] = mapped_column(String, nullable=False)
    existente_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    existente_tipo: Mapped[str] = mapped_column(String, nullable=False)

    razon: Mapped[str] = mapped_column(String, nullable=False)
    score_similitud: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 3), nullable=True)

    resuelto: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolucion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    resuelto_por: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )
    resuelto_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_dedup_candidates_resuelto", "resuelto"),
    )
