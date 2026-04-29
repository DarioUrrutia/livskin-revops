"""Lógica de negocio para sync Vtiger → ERP espejo.

Implementa CREATE/UPDATE de filas en `leads` desde data Vtiger,
preservando first-touch attribution (at_capture fields inmutables).

Llamado desde routes/api_leads_sync.py — endpoint /api/leads/sync-from-vtiger.
"""
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.lead import Lead
from schemas.lead_sync import LeadSyncRequest
from services import codgen_service


# Mapeo Vtiger leadstatus → ERP estado_lead (ADR-0011 v1.1, ADR-0012)
_STATUS_MAP: dict[str, str] = {
    "New": "nuevo",
    "Not Contacted": "nuevo",
    "Attempted to Contact": "contactado",
    "Contact in Future": "contactado",
    "Contacted": "contactado",
    "Pre Qualified": "agendado",
    "Qualified": "agendado",
    "Hot": "agendado",
    "Junk Lead": "perdido",
    "Lost Lead": "perdido",
    "Cold": "perdido",
}

# Mapeo Vtiger leadsource → ERP fuente (ver integrations/vtiger/fields-mapping.md)
_SOURCE_MAP: dict[str, str] = {
    "Existing Customer": "referido",
    "Partner": "referido",
    "Conference": "evento",
    "Trade Show": "evento",
    "Web Site": "form_web",
    "Word of mouth": "organico",
    "Other": "otro",
}


def _map_status(vtiger_status: str | None) -> str:
    """Vtiger leadstatus → ERP estado_lead. Fallback `nuevo`."""
    if not vtiger_status:
        return "nuevo"
    return _STATUS_MAP.get(vtiger_status, "nuevo")


def _map_source(vtiger_source: str | None) -> str:
    """Vtiger leadsource → ERP fuente. Fallback `otro`."""
    if not vtiger_source:
        return "otro"
    return _SOURCE_MAP.get(vtiger_source, "otro")


def upsert_lead(
    db: Session, payload: LeadSyncRequest
) -> tuple[Lead, Literal["created", "updated"]]:
    """Crea o actualiza un Lead en ERP basándose en vtiger_id.

    - Si NO existe lead con ese vtiger_id → CREATE con TODOS los at_capture
    - Si EXISTE → UPDATE solo campos mutables, preservando at_capture inmutables

    Returns:
        (Lead row, "created" | "updated")
    """
    existing = db.execute(
        select(Lead).where(Lead.vtiger_id == payload.vtiger_id)
    ).scalar_one_or_none()

    estado = _map_status(payload.leadstatus)
    fuente = _map_source(payload.leadsource)
    email_lower = payload.email.lower().strip() if payload.email else None

    if existing is None:
        # CREATE — generar cod_lead + poblar at_capture fields
        cod_lead = codgen_service.next_codigo(db, Lead, "cod_lead", "LIVLEAD")
        lead = Lead(
            cod_lead=cod_lead,
            vtiger_id=payload.vtiger_id,
            nombre=payload.nombre,
            phone_e164=payload.phone_e164,
            email_lower=email_lower,
            fuente=fuente,
            tratamiento_interes=payload.tratamiento_interes,
            consent_marketing=payload.consent_marketing,
            estado_lead=estado,
            fecha_captura=datetime.now(timezone.utc),
            # at_capture fields — first-touch immutable
            utm_source_at_capture=payload.utm_source,
            utm_medium_at_capture=payload.utm_medium,
            utm_campaign_at_capture=payload.utm_campaign,
            utm_content_at_capture=payload.utm_content,
            utm_term_at_capture=payload.utm_term,
            fbclid_at_capture=payload.fbclid,
            gclid_at_capture=payload.gclid,
            fbc_at_capture=payload.fbc,
            ga_at_capture=payload.ga,
            event_id_at_capture=payload.event_id,
        )
        db.add(lead)
        db.flush()  # asignar lead.id
        return lead, "created"

    # UPDATE — solo campos mutables; at_capture preserved
    existing.nombre = payload.nombre
    if email_lower is not None:
        existing.email_lower = email_lower
    if payload.tratamiento_interes is not None:
        existing.tratamiento_interes = payload.tratamiento_interes
    existing.estado_lead = estado
    if payload.leadsource is not None:
        existing.fuente = fuente
    if payload.consent_marketing:
        existing.consent_marketing = True
    db.flush()
    return existing, "updated"
