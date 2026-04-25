"""ClienteService — CRUD + lookups (ADR-0011 v1.1, ADR-0013 v2)."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.cliente import Cliente
from services.codgen_service import next_codigo
from services.normalize_service import (
    hash_email,
    normalize_email,
    normalize_nombre,
    normalize_phone,
)


class ClienteNotFoundError(Exception):
    pass


class ClienteDuplicadoError(Exception):
    pass


def get_by_cod(db: Session, cod_cliente: str) -> Cliente:
    cliente = db.execute(
        select(Cliente).where(Cliente.cod_cliente == cod_cliente)
    ).scalar_one_or_none()
    if cliente is None:
        raise ClienteNotFoundError(f"Cliente {cod_cliente} no existe")
    return cliente


def get_by_phone(db: Session, phone_raw: str) -> Optional[Cliente]:
    phone_e164 = normalize_phone(phone_raw)
    if phone_e164 is None:
        return None
    return db.execute(
        select(Cliente).where(Cliente.phone_e164 == phone_e164, Cliente.activo.is_(True))
    ).scalar_one_or_none()


def list_active(db: Session, limit: int = 100, offset: int = 0) -> list[Cliente]:
    return list(
        db.execute(
            select(Cliente)
            .where(Cliente.activo.is_(True))
            .order_by(Cliente.fecha_registro.desc().nullslast(), Cliente.id.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )


def create(
    db: Session,
    nombre: str,
    phone_raw: Optional[str] = None,
    email_raw: Optional[str] = None,
    fecha_nacimiento: Optional[datetime] = None,
    fuente: str = "organico",
    canal_adquisicion: str = "legacy",
    tratamiento_interes: Optional[str] = None,
    consent_marketing: bool = False,
    notas: Optional[str] = None,
    cod_lead_origen: Optional[str] = None,
    created_by: Optional[int] = None,
) -> Cliente:
    """Crea un Cliente nuevo. Detecta duplicado por phone si existe.

    Raises:
        ClienteDuplicadoError: si phone normalizado ya existe en clientes activos
    """
    nombre_norm = normalize_nombre(nombre) or nombre.strip()
    phone_e164 = normalize_phone(phone_raw)
    email_lower = normalize_email(email_raw)
    email_hash = hash_email(email_lower) if email_lower else None

    if phone_e164:
        existing = db.execute(
            select(Cliente).where(Cliente.phone_e164 == phone_e164, Cliente.activo.is_(True))
        ).scalar_one_or_none()
        if existing is not None:
            raise ClienteDuplicadoError(
                f"Phone {phone_e164} ya existe (cliente {existing.cod_cliente})"
            )

    cod_cliente = next_codigo(db, Cliente, "cod_cliente", "LIVCLIENT")

    cliente = Cliente(
        cod_cliente=cod_cliente,
        nombre=nombre.strip(),
        phone_e164=phone_e164,
        email_lower=email_lower,
        email_hash_sha256=email_hash,
        fecha_nacimiento=fecha_nacimiento,
        fuente=fuente,
        canal_adquisicion=canal_adquisicion,
        tratamiento_interes=tratamiento_interes,
        consent_marketing=consent_marketing,
        notas=notas,
        cod_lead_origen=cod_lead_origen,
        activo=True,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(cliente)
    db.flush()
    return cliente


def update(
    db: Session,
    cod_cliente: str,
    nombre: Optional[str] = None,
    phone_raw: Optional[str] = None,
    email_raw: Optional[str] = None,
    fecha_nacimiento: Optional[datetime] = None,
    tratamiento_interes: Optional[str] = None,
    consent_marketing: Optional[bool] = None,
    notas: Optional[str] = None,
    updated_by: Optional[int] = None,
) -> Cliente:
    """Actualiza campos de un Cliente. Solo modifica los campos pasados (no None)."""
    cliente = get_by_cod(db, cod_cliente)

    if nombre is not None:
        cliente.nombre = nombre.strip()
    if phone_raw is not None:
        new_phone = normalize_phone(phone_raw)
        if new_phone and new_phone != cliente.phone_e164:
            existing = db.execute(
                select(Cliente).where(
                    Cliente.phone_e164 == new_phone,
                    Cliente.activo.is_(True),
                    Cliente.cod_cliente != cod_cliente,
                )
            ).scalar_one_or_none()
            if existing is not None:
                raise ClienteDuplicadoError(
                    f"Phone {new_phone} ya existe en cliente {existing.cod_cliente}"
                )
        cliente.phone_e164 = new_phone
    if email_raw is not None:
        new_email = normalize_email(email_raw)
        cliente.email_lower = new_email
        cliente.email_hash_sha256 = hash_email(new_email) if new_email else None
    if fecha_nacimiento is not None:
        cliente.fecha_nacimiento = fecha_nacimiento
    if tratamiento_interes is not None:
        cliente.tratamiento_interes = tratamiento_interes
    if consent_marketing is not None:
        cliente.consent_marketing = consent_marketing
    if notas is not None:
        cliente.notas = notas
    if updated_by is not None:
        cliente.updated_by = updated_by

    db.flush()
    return cliente
