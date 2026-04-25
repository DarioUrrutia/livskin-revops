"""Schemas Pydantic para /api/client-lookup."""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class ClienteShort(BaseModel):
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
    cod_lead_origen: Optional[str]


class LeadShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cod_lead: str
    nombre: str
    phone_e164: str
    email_lower: Optional[str]
    fuente: Optional[str]
    canal_adquisicion: Optional[str]
    utm_campaign_at_capture: Optional[str]
    fbclid_at_capture: Optional[str]
    estado_lead: str
    score: int
    intent_level: Optional[str]
    fecha_captura: Optional[datetime]
    tratamiento_interes: Optional[str]


MatchType = Literal["cliente", "lead", "none", "invalid_phone"]


class ClientLookupResponse(BaseModel):
    phone_input: str
    phone_e164: Optional[str]
    match_type: MatchType
    cliente: Optional[ClienteShort] = None
    lead: Optional[LeadShort] = None
