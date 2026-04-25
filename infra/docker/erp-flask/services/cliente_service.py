"""ClienteService — CRUD + lookups (ADR-0011 v1.1, ADR-0013 v2)."""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.cliente import Cliente
from models.pago import Pago
from models.venta import Venta
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


def get_or_create(
    db: Session,
    nombre: str,
    phone_raw: Optional[str] = None,
    email_raw: Optional[str] = None,
    fecha_nacimiento: Optional[Any] = None,
    fuente: str = "organico",
    canal_adquisicion: str = "legacy",
    actualizar: bool = False,
    created_by: Optional[int] = None,
) -> Cliente:
    """Busca cliente por nombre case-insensitive. Si existe, opcionalmente
    actualiza campos vacíos (siempre) o todos los distintos (si actualizar=True).
    Si no existe, lo crea. Replica `get_or_create_cliente` del Flask original.
    """
    nombre_clean = (nombre or "").strip()
    if not nombre_clean:
        raise ValueError("nombre no puede estar vacío")
    nombre_lower = nombre_clean.lower()

    cliente = db.execute(
        select(Cliente).where(
            func.lower(Cliente.nombre) == nombre_lower, Cliente.activo.is_(True)
        )
    ).scalar_one_or_none()

    if cliente is None:
        return create(
            db,
            nombre=nombre_clean,
            phone_raw=phone_raw,
            email_raw=email_raw,
            fecha_nacimiento=fecha_nacimiento,
            fuente=fuente,
            canal_adquisicion=canal_adquisicion,
            created_by=created_by,
        )

    # Existe — actualizar selectivamente
    new_phone = normalize_phone(phone_raw) if phone_raw else None
    if new_phone:
        if not cliente.phone_e164:
            cliente.phone_e164 = new_phone
        elif actualizar and new_phone != cliente.phone_e164:
            other = db.execute(
                select(Cliente).where(
                    Cliente.phone_e164 == new_phone,
                    Cliente.activo.is_(True),
                    Cliente.cod_cliente != cliente.cod_cliente,
                )
            ).scalar_one_or_none()
            if other is not None:
                raise ClienteDuplicadoError(
                    f"Phone {new_phone} ya existe en cliente {other.cod_cliente}"
                )
            cliente.phone_e164 = new_phone

    new_email = normalize_email(email_raw) if email_raw else None
    if new_email:
        if not cliente.email_lower:
            cliente.email_lower = new_email
            cliente.email_hash_sha256 = hash_email(new_email)
        elif actualizar and new_email != cliente.email_lower:
            cliente.email_lower = new_email
            cliente.email_hash_sha256 = hash_email(new_email)

    if fecha_nacimiento:
        if not cliente.fecha_nacimiento:
            cliente.fecha_nacimiento = fecha_nacimiento
        elif actualizar:
            cliente.fecha_nacimiento = fecha_nacimiento

    if created_by is not None:
        cliente.updated_by = created_by

    db.flush()
    return cliente


def get_full_history(db: Session, nombre: str) -> dict[str, Any]:
    """Retorna historial completo del cliente — formato compatible con formulario.html.

    Lógica preservada del Flask original (`/cliente` endpoint):
    - Búsqueda case-insensitive por nombre
    - Excluye pagos tipo 'credito_aplicado' del listado (es transferencia interna)
    - Recalcula DEBE dinámicamente: max(0, total - sum(pagos_no_credito_aplicado por cod_item))
    - cobrado_total = sum(pagos.monto) excluyendo credito_aplicado
    - facturado_total = sum(ventas.total)
    - saldo = facturado - cobrado

    Si no existe cliente, retorna estructura vacía (no error) — el form
    legacy lo trata como "cliente nuevo".
    """
    nombre_lower = (nombre or "").strip().lower()
    if not nombre_lower:
        return _empty_history()

    cliente = db.execute(
        select(Cliente)
        .where(func.lower(Cliente.nombre) == nombre_lower, Cliente.activo.is_(True))
    ).scalar_one_or_none()

    if cliente is None:
        return _empty_history()

    ventas = list(
        db.execute(
            select(Venta)
            .where(Venta.cod_cliente == cliente.cod_cliente)
            .order_by(Venta.fecha.desc(), Venta.id.desc())
        )
        .scalars()
        .all()
    )

    todos_pagos = list(
        db.execute(
            select(Pago)
            .where(Pago.cod_cliente == cliente.cod_cliente)
            .order_by(Pago.fecha.desc(), Pago.id.desc())
        )
        .scalars()
        .all()
    )

    pagos_por_item: dict[str, Decimal] = {}
    for p in todos_pagos:
        if p.cod_item:
            pagos_por_item[p.cod_item] = pagos_por_item.get(p.cod_item, Decimal("0")) + p.monto

    facturado_total = Decimal("0")
    ventas_out: list[dict[str, Any]] = []
    for v in ventas:
        cobrado_item = min(pagos_por_item.get(v.cod_item, Decimal("0")), v.total)
        debe_real = max(Decimal("0"), v.total - cobrado_item)
        ventas_out.append(_venta_to_dict(v, debe_real, cobrado_item))
        facturado_total += v.total

    pagos_for_display = [p for p in todos_pagos if p.tipo_pago != "credito_aplicado"]
    cobrado_total = sum((p.monto for p in pagos_for_display), Decimal("0"))
    saldo = max(Decimal("0"), facturado_total - cobrado_total)

    credito_dep = (
        db.execute(
            select(func.coalesce(func.sum(Pago.monto), 0)).where(
                Pago.cod_cliente == cliente.cod_cliente,
                Pago.tipo_pago == "credito_generado",
            )
        ).scalar()
        or 0
    )
    credito_usado = (
        db.execute(
            select(func.coalesce(func.sum(Pago.monto), 0)).where(
                Pago.cod_cliente == cliente.cod_cliente,
                Pago.tipo_pago == "credito_aplicado",
            )
        ).scalar()
        or 0
    )
    credito_disponible = max(Decimal("0"), Decimal(credito_dep) - Decimal(credito_usado))

    return {
        "codigo": cliente.cod_cliente,
        "nombre": cliente.nombre,
        "telefono": cliente.phone_e164 or "",
        "email": cliente.email_lower or "",
        "cumpleanos": cliente.fecha_nacimiento.isoformat() if cliente.fecha_nacimiento else "",
        "ventas": ventas_out,
        "pagos": [_pago_to_dict(p) for p in pagos_for_display],
        "facturado_total": float(facturado_total),
        "cobrado_total": float(cobrado_total),
        "saldo": float(saldo),
        "credito_disponible": float(credito_disponible),
    }


def _empty_history() -> dict[str, Any]:
    return {
        "codigo": "",
        "nombre": "",
        "telefono": "",
        "email": "",
        "cumpleanos": "",
        "ventas": [],
        "pagos": [],
        "facturado_total": 0.0,
        "cobrado_total": 0.0,
        "saldo": 0.0,
        "credito_disponible": 0.0,
    }


def _venta_to_dict(v: Venta, debe_real: Decimal, pagado_real: Decimal) -> dict[str, Any]:
    """Mapea Venta a dict con keys del Sheets original (preserva contrato HTTP)."""
    return {
        "#": v.num_secuencial or "",
        "FECHA": v.fecha.isoformat(),
        "COD_CLIENTE": v.cod_cliente,
        "CLIENTE": v.cliente_nombre or "",
        "TELEFONO": v.cliente_telefono or "",
        "TIPO": v.tipo,
        "COD_ITEM": v.cod_item,
        "CATEGORIA": v.categoria or "",
        "ZONA/CANTIDAD/ENVASE": v.zona_cantidad_envase or "",
        "PROXIMA CITA": v.proxima_cita.isoformat() if v.proxima_cita else "",
        "FECHA_NAC": v.fecha_nac_cliente.isoformat() if v.fecha_nac_cliente else "",
        "MONEDA": v.moneda,
        "TOTAL S/ (PEN)": float(v.total),
        "EFECTIVO": float(v.efectivo) if v.efectivo else "",
        "YAPE": float(v.yape) if v.yape else "",
        "PLIN": float(v.plin) if v.plin else "",
        "GIRO": float(v.giro) if v.giro else "",
        "DEBE": float(debe_real),
        "PAGADO": float(pagado_real),
        "TC": str(v.tc) if v.tc else "",
        "PRECIO LISTA S/": float(v.precio_lista) if v.precio_lista else "",
        "DESCUENTO S/": float(v.descuento or 0),
    }


def _pago_to_dict(p: Pago) -> dict[str, Any]:
    """Mapea Pago a dict con keys del Sheets original (preserva contrato HTTP)."""
    return {
        "#": p.num_secuencial or "",
        "FECHA": p.fecha.isoformat(),
        "COD_CLIENTE": p.cod_cliente,
        "CLIENTE": p.cliente_nombre or "",
        "MONTO": float(p.monto),
        "EFECTIVO": float(p.efectivo) if p.efectivo else "",
        "YAPE": float(p.yape) if p.yape else "",
        "PLIN": float(p.plin) if p.plin else "",
        "GIRO": float(p.giro) if p.giro else "",
        "NOTAS": p.notas or "",
        "COD_ITEM": p.cod_item or "",
        "CATEGORIA": p.categoria or "",
        "COD_PAGO": p.cod_pago,
    }


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
