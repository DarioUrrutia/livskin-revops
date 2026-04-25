"""Schemas Pydantic para /api/ventas (las 6 fases)."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemVentaIn(BaseModel):
    tipo: str = Field(..., description="Tratamiento | Producto | Certificado | Promocion")
    categoria: Optional[str] = None
    zona_cantidad_envase: Optional[str] = None
    precio_lista: Optional[Decimal] = None
    descuento: Decimal = Decimal("0")
    pago_item: Decimal = Decimal("0")
    proxima_cita: Optional[date] = None
    notas: Optional[str] = None


class MetodosPagoIn(BaseModel):
    efectivo: Decimal = Decimal("0")
    yape: Decimal = Decimal("0")
    plin: Decimal = Decimal("0")
    giro: Decimal = Decimal("0")


class AbonoDeudaIn(BaseModel):
    cod_item: str
    monto: Decimal
    notas: Optional[str] = None


class VentaCreate(BaseModel):
    cod_cliente: str
    fecha: date
    items: list[ItemVentaIn] = Field(..., min_length=1)
    metodos_pago: MetodosPagoIn = Field(default_factory=MetodosPagoIn)
    credito_aplicado: Decimal = Decimal("0")
    abonos_deudas: list[AbonoDeudaIn] = Field(default_factory=list)
    moneda: str = "PEN"
    tc: Optional[Decimal] = None


class VentaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cod_item: str
    tipo: str
    categoria: Optional[str]
    zona_cantidad_envase: Optional[str]
    precio_lista: Optional[Decimal]
    descuento: Decimal
    total: Decimal
    pagado: Optional[Decimal]
    debe: Optional[Decimal]


class PagoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cod_pago: str
    fecha: date
    monto: Decimal
    tipo_pago: str
    cod_item: Optional[str]
    notas: Optional[str]


class VentaSaveResponse(BaseModel):
    cod_cliente: str
    fecha: date
    ventas: list[VentaItemOut]
    pagos: list[PagoOut]
    total_venta: Decimal
    total_pagado: Decimal
    excedente_credito_generado: Decimal
    credito_aplicado: Decimal
    abonos_deudas: Decimal


class VentaSimpleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cod_item: str
    fecha: date
    tipo: str
    categoria: Optional[str]
    total: Decimal
    pagado: Optional[Decimal]
    debe: Optional[Decimal]
