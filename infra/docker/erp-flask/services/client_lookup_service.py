"""Bridge digital → físico (ADR-0011 v1.1, ADR-0013 v2).

Endpoint /api/client-lookup busca por phone si la persona ya existe como
Cliente (en ERP) o Lead activo (en Vtiger replica). Permite al ERP detectar
durante registro de venta si el phone tipeado corresponde a un lead digital
vivo o a un cliente histórico.
"""
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.cliente import Cliente
from models.lead import Lead
from services.normalize_service import normalize_phone


@dataclass
class ClientLookupResult:
    phone_input: str
    phone_e164: Optional[str]
    match_type: str  # 'cliente' | 'lead' | 'none' | 'invalid_phone'
    cliente: Optional[Cliente] = None
    lead: Optional[Lead] = None


def lookup_by_phone(db: Session, phone_raw: str) -> ClientLookupResult:
    """Busca match por phone en clientes (master) y leads (digital activos).

    Flujo (ADR-0013 v2 § 6.4):
    1. Normalizar phone a E.164
    2. Si inválido → match_type='invalid_phone'
    3. Buscar en clientes activos por phone_e164
       - Si match → existing client (puede ser reactivación digital)
    4. Si no, buscar en leads NO terminales (no convertidos, no perdidos)
       - Si match → lead en funnel
    5. Si nada → match_type='none' (lead nuevo)
    """
    phone_e164 = normalize_phone(phone_raw)

    if phone_e164 is None:
        return ClientLookupResult(
            phone_input=phone_raw, phone_e164=None, match_type="invalid_phone"
        )

    cliente = db.execute(
        select(Cliente).where(Cliente.phone_e164 == phone_e164, Cliente.activo.is_(True))
    ).scalar_one_or_none()

    if cliente is not None:
        return ClientLookupResult(
            phone_input=phone_raw,
            phone_e164=phone_e164,
            match_type="cliente",
            cliente=cliente,
        )

    lead = db.execute(
        select(Lead).where(
            Lead.phone_e164 == phone_e164,
            Lead.estado_lead.notin_(["cliente", "perdido"]),
        )
    ).scalar_one_or_none()

    if lead is not None:
        return ClientLookupResult(
            phone_input=phone_raw,
            phone_e164=phone_e164,
            match_type="lead",
            lead=lead,
        )

    return ClientLookupResult(phone_input=phone_raw, phone_e164=phone_e164, match_type="none")
