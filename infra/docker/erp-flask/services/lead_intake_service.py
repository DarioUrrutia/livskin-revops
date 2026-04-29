"""Lead intake service — orchestrates capture pipeline (mini-bloque 3.3 Fase 3).

Pipeline:
1. Verify Turnstile token (si lead_intake_require_turnstile=True)
2. Normalize phone (E.164 +51 prefix Peru) + email + nombre
3. Lookup existing lead by phone_e164 (idempotencia)
4. Si lead nuevo: generar cod_lead (LIVLEAD####) + INSERT en leads
5. Siempre: INSERT touchpoint en lead_touchpoints
6. Audit log entry (lead.created si nuevo, lead.touchpoint si recurrente)

Las llamadas a Vtiger + emision GA4 MP / Meta CAPI se hacen en mini-bloque 3.4
(tracking_emitter listener del audit_log).
"""
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import settings
from models.lead import Lead
from models.lead_touchpoint import LeadTouchpoint
from schemas.lead import LeadIntakeRequest
from services import audit_service, codgen_service, normalize_service

# Cloudflare Turnstile siteverify endpoint
TURNSTILE_SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


class TurnstileVerificationError(Exception):
    """Token Turnstile invalido o ausente cuando es required."""


class IntakeValidationError(Exception):
    """Datos del intake invalidos (phone que no normaliza, etc.)."""


def verify_turnstile(token: Optional[str], remote_ip: Optional[str] = None) -> bool:
    """Verify Cloudflare Turnstile token via siteverify API.

    Si lead_intake_require_turnstile=False, retorna True sin verificar (modo dev).
    Si require=True y token vacio o falla verificacion, retorna False.
    """
    if not settings.lead_intake_require_turnstile:
        return True
    if not token or not settings.cf_turnstile_secret_key:
        return False

    try:
        resp = requests.post(
            TURNSTILE_SITEVERIFY_URL,
            data={
                "secret": settings.cf_turnstile_secret_key,
                "response": token,
                "remoteip": remote_ip or "",
            },
            timeout=5,
        )
        if resp.status_code != 200:
            return False
        data = resp.json()
        return bool(data.get("success", False))
    except (requests.RequestException, ValueError):
        return False


def intake_lead(
    db: Session,
    payload: LeadIntakeRequest,
    *,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[str] = None,
) -> tuple[Lead, LeadTouchpoint, bool]:
    """Captura un lead nuevo o agrega touchpoint a uno existente.

    Returns:
        (lead, touchpoint, is_new_lead)

    Raises:
        IntakeValidationError: phone no normaliza correctamente
    """
    # 1) Normalizacion
    phone_e164 = normalize_service.normalize_phone(payload.telefono)
    if not phone_e164:
        raise IntakeValidationError(f"telefono invalido: {payload.telefono!r}")

    nombre_norm = normalize_service.normalize_nombre(payload.nombre) or payload.nombre.strip()
    email_lower = normalize_service.normalize_email(payload.email)
    email_hash = normalize_service.hash_email(email_lower) if email_lower else None

    # 2) Lookup existing lead by phone
    existing = db.execute(select(Lead).where(Lead.phone_e164 == phone_e164)).scalar_one_or_none()

    if existing is None:
        # Nuevo lead
        cod_lead = codgen_service.next_codigo(db, Lead, "cod_lead", "LIVLEAD")
        lead = Lead(
            cod_lead=cod_lead,
            nombre=nombre_norm,
            phone_e164=phone_e164,
            email_lower=email_lower,
            email_hash_sha256=email_hash,
            fuente="web",
            canal_adquisicion="form_web",
            utm_source_at_capture=payload.utm_source,
            utm_medium_at_capture=payload.utm_medium,
            utm_campaign_at_capture=payload.utm_campaign,
            utm_content_at_capture=payload.utm_content,
            utm_term_at_capture=payload.utm_term,
            fbclid_at_capture=payload.fbclid,
            gclid_at_capture=payload.gclid,
            tratamiento_interes=payload.tratamiento,
            consent_marketing=payload.consent_marketing,
            consent_date=datetime.now(timezone.utc) if payload.consent_marketing else None,
            estado_lead="nuevo",
            fecha_captura=datetime.now(timezone.utc),
            score=0,
            nurture_state="inactivo",
            es_reactivacion=False,
        )
        db.add(lead)
        db.flush()  # asegurar lead.id disponible para FK del touchpoint
        is_new_lead = True
    else:
        lead = existing
        # Update email si llega y antes era None
        if email_lower and not lead.email_lower:
            lead.email_lower = email_lower
            lead.email_hash_sha256 = email_hash
        # NO sobrescribir UTMs at_capture (esos son first-touch). Los nuevos
        # UTMs van al touchpoint (last-touch).
        is_new_lead = False

    # 3) INSERT touchpoint (siempre — multi-touch tracking)
    # form_data_json absorbe campos extra: ttclid, msclkid, first_referrer, event_id
    form_extras = {
        "ttclid": payload.ttclid or None,
        "msclkid": payload.msclkid or None,
        "first_referrer": payload.first_referrer or None,
        "event_id": payload.event_id or None,
        "raw_nombre": payload.nombre,
        "raw_telefono": payload.telefono,
    }
    # Drop None entries para JSON limpio
    form_extras = {k: v for k, v in form_extras.items() if v}

    touchpoint = LeadTouchpoint(
        lead_id=lead.id,
        canal="form_web",
        landing_url=payload.landing_url,
        fecha_contacto=datetime.now(timezone.utc),
        utm_source=payload.utm_source,
        utm_medium=payload.utm_medium,
        utm_campaign=payload.utm_campaign,
        utm_content=payload.utm_content,
        utm_term=payload.utm_term,
        fbclid=payload.fbclid,
        gclid=payload.gclid,
        form_data_json=form_extras or None,
        ip=client_ip,
        user_agent=user_agent,
        session_id=session_id,
    )
    db.add(touchpoint)
    db.flush()  # asegurar touchpoint.id disponible para response

    # 4) Audit log — solo para leads nuevos (lead.created es canonico).
    # Repeat touchpoints quedan en lead_touchpoints table (naturalmente auditable).
    # Evita ruido en audit_log para visitantes que rebotan en el form 5 veces el
    # mismo dia.
    if is_new_lead:
        audit_service.log(
            db,
            action="lead.created",
            entity_type="lead",
            entity_id=lead.cod_lead,
            metadata={
                "touchpoint_id": touchpoint.id,
                "tratamiento": payload.tratamiento,
                "utm_source": payload.utm_source,
                "utm_medium": payload.utm_medium,
                "utm_campaign": payload.utm_campaign,
                "event_id": payload.event_id,
                "channel": "form_web",
            },
            result="success",
            ip=client_ip,
            user_username="system_intake",
            user_role="system",
        )

    return lead, touchpoint, is_new_lead
