"""Schemas Pydantic para POST /api/leads/sync-from-vtiger.

Endpoint recibido desde n8n Workflow [B1] (Vtiger lead on-change → ERP espejo).
"""
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class LeadSyncRequest(BaseModel):
    """Payload entrante del workflow [B1] de n8n.

    Sólo `vtiger_id`, `nombre`, `phone_e164` son obligatorios. El resto es
    opcional porque Vtiger podría no tener todos los fields poblados.
    """
    model_config = ConfigDict(extra="ignore")

    # Required
    vtiger_id: str = Field(..., min_length=1, max_length=64)
    nombre: str = Field(..., min_length=1, max_length=200)
    phone_e164: str = Field(..., min_length=1, max_length=20)

    # Optional native Vtiger fields
    email: Optional[str] = Field(default=None, max_length=200)
    leadstatus: Optional[str] = Field(default=None, max_length=64)
    leadsource: Optional[str] = Field(default=None, max_length=64)

    # Optional custom fields (cf_NNN en Vtiger)
    tratamiento_interes: Optional[str] = Field(default=None, max_length=64)
    utm_source: Optional[str] = Field(default=None, max_length=100)
    utm_medium: Optional[str] = Field(default=None, max_length=100)
    utm_campaign: Optional[str] = Field(default=None, max_length=200)
    utm_content: Optional[str] = Field(default=None, max_length=200)
    utm_term: Optional[str] = Field(default=None, max_length=200)
    fbclid: Optional[str] = Field(default=None, max_length=300)
    gclid: Optional[str] = Field(default=None, max_length=300)
    fbc: Optional[str] = Field(default=None, max_length=300)
    ga: Optional[str] = Field(default=None, max_length=200)
    event_id: Optional[str] = Field(default=None, max_length=128)
    landing_url: Optional[str] = Field(default=None, max_length=1000)

    # Misc
    consent_marketing: bool = False


class LeadSyncResponse(BaseModel):
    ok: Literal[True] = True
    operation: Literal["created", "updated"]
    vtiger_id: str
    lead_id: int
    cod_lead: str
