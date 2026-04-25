"""Schemas Pydantic para /api/gastos."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GastoCreate(BaseModel):
    fecha: date
    monto: Decimal = Field(..., ge=0)
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    destinatario: Optional[str] = None
    metodo_pago: Optional[str] = None
    notas: Optional[str] = None


class GastoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    num_secuencial: Optional[int]
    fecha: date
    tipo: Optional[str]
    descripcion: Optional[str]
    destinatario: Optional[str]
    monto: Decimal
    metodo_pago: Optional[str]
    notas: Optional[str]


class GastoListResponse(BaseModel):
    items: list[GastoOut]
    limit: int
    offset: int
    count: int
