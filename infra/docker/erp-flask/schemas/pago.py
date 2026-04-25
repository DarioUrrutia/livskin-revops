"""Schemas Pydantic para /api/pagos (pagos día posterior)."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PagoIndividualIn(BaseModel):
    cod_item: str
    monto: Decimal = Field(..., gt=0)
    categoria: Optional[str] = None
    notas: Optional[str] = None


class MetodosPagoIn(BaseModel):
    efectivo: Decimal = Field(default=Decimal("0"), ge=0)
    yape: Decimal = Field(default=Decimal("0"), ge=0)
    plin: Decimal = Field(default=Decimal("0"), ge=0)
    giro: Decimal = Field(default=Decimal("0"), ge=0)


class PagosCreate(BaseModel):
    cod_cliente: str
    fecha: date
    metodos_pago: MetodosPagoIn
    pagos: list[PagoIndividualIn] = Field(default_factory=list)
    auto_aplicar_a_deudas: bool = True
    notas: Optional[str] = None


class PagoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cod_pago: str
    fecha: date
    cod_cliente: str
    cod_item: Optional[str]
    categoria: Optional[str]
    monto: Decimal
    tipo_pago: str
    notas: Optional[str]


class PagosSaveResponse(BaseModel):
    cod_cliente: str
    fecha: date
    pagos: list[PagoOut]
    total_pagos_explicitos: Decimal
    auto_abonos_total: Decimal
    excedente_credito_generado: Decimal
