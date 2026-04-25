"""Schemas Pydantic para /api/clientes."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ClienteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=200)
    fecha_nacimiento: Optional[date] = None
    fuente: str = "organico"
    canal_adquisicion: str = "legacy"
    tratamiento_interes: Optional[str] = None
    consent_marketing: bool = False
    notas: Optional[str] = None


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=200)
    fecha_nacimiento: Optional[date] = None
    tratamiento_interes: Optional[str] = None
    consent_marketing: Optional[bool] = None
    notas: Optional[str] = None


class ClienteFull(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cod_cliente: str
    nombre: str
    phone_e164: Optional[str]
    email_lower: Optional[str]
    fecha_nacimiento: Optional[date]
    fecha_registro: Optional[date]
    fuente: Optional[str]
    canal_adquisicion: Optional[str]
    tratamiento_interes: Optional[str]
    consent_marketing: bool
    notas: Optional[str]
    cod_lead_origen: Optional[str]
    activo: bool


class ClienteListItem(BaseModel):
    """Shape compacto para autocomplete y listados."""

    model_config = ConfigDict(from_attributes=True)

    cod_cliente: str
    nombre: str
    phone_e164: Optional[str]
    fuente: Optional[str]


class ClienteListResponse(BaseModel):
    items: list[ClienteListItem]
    limit: int
    offset: int
    count: int
