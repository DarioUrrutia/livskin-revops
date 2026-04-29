"""Schemas Pydantic para /api/leads/intake (mini-bloque 3.3 Fase 3)."""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LeadIntakeRequest(BaseModel):
    """Payload aceptado en POST /api/leads/intake.

    Campos required minimos: nombre + telefono. Tratamiento es muy recomendable
    pero opcional (si SureForms lo enviara vacio, el lead aun se captura).

    UTMs / click_ids / event_id son optional — vendran del Tracking Engine GTM
    via hidden fields en SureForms 1569. Si el visitante llego directo (sin
    campania), todos esos quedan vacios y la atribucion sera 'organic/direct'.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    # Required
    nombre: str = Field(..., min_length=1, max_length=200)
    telefono: str = Field(..., min_length=6, max_length=30)

    # Recommended
    tratamiento: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=200)

    # UTMs (capturados por Tracking Engine GTM via cookies + hidden fields)
    utm_source: Optional[str] = Field(default=None, max_length=200)
    utm_medium: Optional[str] = Field(default=None, max_length=200)
    utm_campaign: Optional[str] = Field(default=None, max_length=200)
    utm_content: Optional[str] = Field(default=None, max_length=200)
    utm_term: Optional[str] = Field(default=None, max_length=200)

    # Click IDs (per-platform attribution)
    fbclid: Optional[str] = Field(default=None, max_length=500)
    gclid: Optional[str] = Field(default=None, max_length=500)
    ttclid: Optional[str] = Field(default=None, max_length=500)
    msclkid: Optional[str] = Field(default=None, max_length=500)

    # Capture context
    landing_url: Optional[str] = Field(default=None, max_length=2000)
    first_referrer: Optional[str] = Field(default=None, max_length=2000)

    # event_id del Tracking Engine — sirve para dedup CAPI server-side mini-bloque 3.4
    event_id: Optional[str] = Field(default=None, max_length=100)

    # Consent (SureForms enviara True si el form fue submiteado tras consent banner)
    consent_marketing: bool = True

    # Turnstile token (Cloudflare). Required cuando lead_intake_require_turnstile=True.
    cf_turnstile_response: Optional[str] = Field(default=None, max_length=2048, alias="cf-turnstile-response")


class LeadIntakeResponse(BaseModel):
    """Respuesta tras INSERT exitoso en leads + lead_touchpoints."""
    model_config = ConfigDict(from_attributes=True)

    ok: bool
    cod_lead: str
    is_new_lead: bool  # True si lead nuevo, False si touchpoint adicional sobre existente
    touchpoint_id: int


class LeadIntakeError(BaseModel):
    """Respuesta de error generica para el endpoint."""
    ok: bool = False
    error: str
    detail: Optional[str] = None
