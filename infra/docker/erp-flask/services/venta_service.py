"""VentaService — las 6 fases del Flask preservadas (ADR-0011 v1.1, ADR-0023).

Las 6 fases de save_venta:
1. Generar códigos cod_item para cada item (LIVTRAT/LIVPROD/LIVCERT/LIVPROM)
2. Insertar 1 fila en ventas por cada item (estructura flat preservada)
3. Insertar pagos normales (distribución proporcional métodos de pago)
4. Crédito generado si total_pagado > total_venta_dia (excedente)
5. Crédito aplicado si cliente usa crédito previo (valida balance disponible)
6. Abonos a deudas anteriores (1 pago abono_deuda por item con deuda abierta)
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.cliente import Cliente
from models.pago import Pago
from models.venta import Venta
from services import cliente_service, pago_service
from services.codgen_service import next_codigos_batch


PREFIX_BY_TIPO: dict[str, str] = {
    "Tratamiento": "LIVTRAT",
    "Producto": "LIVPROD",
    "Certificado": "LIVCERT",
    "Promocion": "LIVPROM",
}


class ClienteNoExiste(Exception):
    pass


class CreditoInsuficiente(Exception):
    pass


class TipoItemInvalido(Exception):
    pass


@dataclass
class ItemVentaInput:
    tipo: str
    categoria: Optional[str] = None
    zona_cantidad_envase: Optional[str] = None
    precio_lista: Optional[Decimal] = None
    descuento: Decimal = Decimal("0")
    pago_item: Decimal = Decimal("0")
    proxima_cita: Optional[date] = None
    notas: Optional[str] = None
    cod_item: Optional[str] = None  # se llena en Phase 1
    total: Decimal = Decimal("0")  # se calcula
    efectivo: Decimal = Decimal("0")  # asignados en Phase 3
    yape: Decimal = Decimal("0")
    plin: Decimal = Decimal("0")
    giro: Decimal = Decimal("0")


@dataclass
class AbonoDeudaInput:
    cod_item: str
    monto: Decimal
    notas: Optional[str] = None


@dataclass
class ClienteAutoCreateInput:
    """Datos para auto-crear o resolver cliente desde POST /venta (per Flask original)."""
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    # ADR-0033: vinculación opcional a lead origen confirmada via UI tip
    cod_lead_origen: Optional[str] = None


@dataclass
class SaveVentaResult:
    ventas: list[Venta] = field(default_factory=list)
    pagos: list[Pago] = field(default_factory=list)
    total_venta: Decimal = Decimal("0")
    total_pagado: Decimal = Decimal("0")
    excedente_credito_generado: Decimal = Decimal("0")
    credito_aplicado: Decimal = Decimal("0")
    abonos_deudas: Decimal = Decimal("0")
    # ADR-0033 — informa al caller si el cliente fue creado en esta venta
    # (vs ya existía) y si quedó vinculado a un lead origen.
    cliente_was_created: bool = False
    cliente_cod_lead_origen: Optional[str] = None
    cliente_vtiger_lead_id_origen: Optional[str] = None


def save_venta(
    db: Session,
    fecha: date,
    items: list[ItemVentaInput],
    metodos_pago: dict[str, Decimal],
    cod_cliente: Optional[str] = None,
    cliente_data: Optional[ClienteAutoCreateInput] = None,
    actualizar_cliente: bool = False,
    credito_aplicado: Decimal = Decimal("0"),
    abonos_deudas: Optional[list[AbonoDeudaInput]] = None,
    auto_aplicar_a_deudas: bool = True,
    moneda: str = "PEN",
    tc: Optional[Decimal] = None,
    created_by: Optional[int] = None,
) -> SaveVentaResult:
    """Procesa las 6 fases en una sola transacción.

    Cliente puede pasarse vía:
    - cod_cliente: lookup directo (rechaza si no existe)
    - cliente_data: nombre + datos opcionales — replica `get_or_create_cliente`
      del Flask original. Si actualizar_cliente=True, sobrescribe campos
      no vacíos del cliente existente con datos nuevos.

    Si cualquier fase falla → rollback completo (atomicidad).
    """
    if not items:
        raise ValueError("items no puede estar vacío")

    cliente_was_created = False
    if cod_cliente:
        cliente = db.execute(
            select(Cliente).where(Cliente.cod_cliente == cod_cliente)
        ).scalar_one_or_none()
        if cliente is None:
            raise ClienteNoExiste(f"Cliente {cod_cliente} no existe")
    elif cliente_data:
        # ADR-0033: detect si get_or_create va a CREATE (no existe por nombre)
        # para emitir el audit event canónico desde el caller.
        from sqlalchemy import func
        nombre_lower = (cliente_data.nombre or "").strip().lower()
        existed_before = db.execute(
            select(Cliente).where(
                func.lower(Cliente.nombre) == nombre_lower,
                Cliente.activo.is_(True),
            )
        ).scalar_one_or_none()
        cliente_was_created = existed_before is None

        cliente = cliente_service.get_or_create(
            db,
            nombre=cliente_data.nombre,
            phone_raw=cliente_data.telefono,
            email_raw=cliente_data.email,
            fecha_nacimiento=cliente_data.fecha_nacimiento,
            actualizar=actualizar_cliente,
            created_by=created_by,
            cod_lead_origen=cliente_data.cod_lead_origen,
        )
        cod_cliente = cliente.cod_cliente
    else:
        raise ValueError("Debe pasar cod_cliente o cliente_data")

    for item in items:
        if item.tipo not in PREFIX_BY_TIPO:
            raise TipoItemInvalido(
                f"tipo '{item.tipo}' inválido. Válidos: {sorted(PREFIX_BY_TIPO.keys())}"
            )

    abonos_deudas = abonos_deudas or []
    metodos_pago = {k: Decimal(str(v)) for k, v in metodos_pago.items()}

    # Cálculos pre-fase
    for item in items:
        item.descuento = item.descuento or Decimal("0")
        if item.precio_lista is None:
            item.precio_lista = item.pago_item + item.descuento
        if item.precio_lista <= item.descuento:
            item.total = Decimal("0")
        else:
            item.total = item.precio_lista - item.descuento
        if item.pago_item > item.total:
            item.pago_item = item.total

    total_venta_dia = sum((it.total for it in items), Decimal("0"))
    total_pagado_hoy = sum(metodos_pago.values(), Decimal("0"))

    suma_pagos_items = sum((it.pago_item for it in items), Decimal("0"))
    if suma_pagos_items > total_pagado_hoy and suma_pagos_items > 0:
        ratio = total_pagado_hoy / suma_pagos_items
        for item in items:
            item.pago_item = (item.pago_item * ratio).quantize(Decimal("0.01"))
        suma_pagos_items = sum((it.pago_item for it in items), Decimal("0"))

    if suma_pagos_items > 0:
        for item in items:
            r = item.pago_item / suma_pagos_items
            item.efectivo = (metodos_pago.get("efectivo", Decimal("0")) * r).quantize(
                Decimal("0.01")
            )
            item.yape = (metodos_pago.get("yape", Decimal("0")) * r).quantize(Decimal("0.01"))
            item.plin = (metodos_pago.get("plin", Decimal("0")) * r).quantize(Decimal("0.01"))
            item.giro = (metodos_pago.get("giro", Decimal("0")) * r).quantize(Decimal("0.01"))

    result = SaveVentaResult(total_venta=total_venta_dia, total_pagado=total_pagado_hoy)

    # ============================================================
    # FASE 1: generar códigos cod_item (batch por prefijo para evitar
    # duplicados cuando hay múltiples items del mismo tipo en la venta)
    # ============================================================
    items_por_prefijo: dict[str, list[ItemVentaInput]] = {}
    for item in items:
        prefijo = PREFIX_BY_TIPO[item.tipo]
        items_por_prefijo.setdefault(prefijo, []).append(item)

    for prefijo, items_grupo in items_por_prefijo.items():
        codigos = next_codigos_batch(db, Venta, "cod_item", prefijo, len(items_grupo))
        for item, codigo in zip(items_grupo, codigos):
            item.cod_item = codigo

    # ============================================================
    # FASE 2: insertar 1 fila en ventas por item + FASE 3: pagos normales
    # ============================================================
    for item in items:
        venta = Venta(
            fecha=fecha,
            cod_cliente=cod_cliente,
            cliente_nombre=cliente.nombre,
            cliente_telefono=cliente.phone_e164,
            tipo=item.tipo,
            cod_item=item.cod_item,
            categoria=item.categoria,
            zona_cantidad_envase=item.zona_cantidad_envase,
            proxima_cita=item.proxima_cita,
            fecha_nac_cliente=cliente.fecha_nacimiento,
            moneda=moneda,
            total=item.total,
            efectivo=item.efectivo,
            yape=item.yape,
            plin=item.plin,
            giro=item.giro,
            pagado=item.pago_item,
            debe=item.total - item.pago_item,
            precio_lista=item.precio_lista,
            descuento=item.descuento,
            tc=tc,
            notas=item.notas,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(venta)
        result.ventas.append(venta)

        if item.pago_item > 0:
            pago = pago_service.create_pago(
                db,
                cod_cliente=cod_cliente,
                fecha=fecha,
                monto=item.pago_item,
                tipo_pago="normal",
                cod_item=item.cod_item,
                categoria=item.categoria,
                cliente_nombre=cliente.nombre,
                efectivo=item.efectivo,
                yape=item.yape,
                plin=item.plin,
                giro=item.giro,
                notas=f"Pago venta {fecha}",
                created_by=created_by,
            )
            result.pagos.append(pago)

    # ============================================================
    # FASE 4: crédito aplicado — distribuido proporcional por item
    # (igual que el Flask original — permite trackear cuál item recibió
    # el crédito + reduce el DEBE de cada item via trigger en pagos)
    # ============================================================
    if credito_aplicado > 0:
        balance = pago_service.credito_balance(db, cod_cliente)
        if credito_aplicado > balance:
            raise CreditoInsuficiente(
                f"Cliente {cod_cliente} tiene crédito S/.{balance} disponible, "
                f"solicitado S/.{credito_aplicado}"
            )

        items_con_total = [it for it in items if it.total > 0]
        suma_totales = sum((it.total for it in items_con_total), Decimal("0"))

        if suma_totales > 0:
            credito_restante = credito_aplicado
            for idx, item in enumerate(items_con_total):
                if idx == len(items_con_total) - 1:
                    credito_item = credito_restante
                else:
                    proporcion = item.total / suma_totales
                    credito_item = (credito_aplicado * proporcion).quantize(Decimal("0.01"))
                    credito_item = min(credito_item, credito_restante)

                if credito_item <= 0:
                    continue

                credito_restante -= credito_item
                pago_aplicado = pago_service.create_pago(
                    db,
                    cod_cliente=cod_cliente,
                    fecha=fecha,
                    monto=credito_item,
                    tipo_pago="credito_aplicado",
                    cod_item=item.cod_item,
                    categoria=item.categoria,
                    cliente_nombre=cliente.nombre,
                    notas=f"Crédito aplicado del {fecha}",
                    created_by=created_by,
                )
                result.pagos.append(pago_aplicado)
        result.credito_aplicado = credito_aplicado

    # ============================================================
    # FASE 5: abonos EXPLÍCITOS a deudas anteriores (input del operador)
    # ============================================================
    total_abonos_explicitos = Decimal("0")
    cod_items_abonados_explicitos: set[str] = set()
    for abono in abonos_deudas:
        if abono.monto <= 0:
            continue
        pago_abono = pago_service.create_pago(
            db,
            cod_cliente=cod_cliente,
            fecha=fecha,
            monto=abono.monto,
            tipo_pago="abono_deuda",
            cod_item=abono.cod_item,
            cliente_nombre=cliente.nombre,
            notas=abono.notas or f"Abono a deuda de {abono.cod_item}",
            created_by=created_by,
        )
        result.pagos.append(pago_abono)
        total_abonos_explicitos += abono.monto
        cod_items_abonados_explicitos.add(abono.cod_item)

    # ============================================================
    # FASE 6 (NUEVA): auto-aplicar leftover_cash a deudas anteriores (FIFO)
    # Solo si auto_aplicar_a_deudas=True (default). Si operador envía
    # auto_aplicar_a_deudas=False, el sobrante va directo a crédito (Fase 7).
    # ============================================================
    total_pago_items = sum((it.pago_item for it in items), Decimal("0"))
    leftover_cash = total_pagado_hoy - total_pago_items - total_abonos_explicitos

    auto_abonos_total = Decimal("0")
    if auto_aplicar_a_deudas and leftover_cash > Decimal("0.01"):
        cod_items_to_skip = cod_items_abonados_explicitos | {
            it.cod_item for it in items if it.cod_item is not None
        }

        deudas_query = select(Venta).where(
            Venta.cod_cliente == cod_cliente,
            Venta.debe > 0,
        )
        if cod_items_to_skip:
            deudas_query = deudas_query.where(~Venta.cod_item.in_(cod_items_to_skip))
        deudas_query = deudas_query.order_by(Venta.fecha, Venta.id)

        deudas_abiertas = list(db.execute(deudas_query).scalars().all())

        for deuda in deudas_abiertas:
            if leftover_cash <= Decimal("0.01"):
                break
            debe_actual = deuda.debe or Decimal("0")
            if debe_actual <= 0:
                continue
            monto_abono = min(debe_actual, leftover_cash).quantize(Decimal("0.01"))
            if monto_abono <= 0:
                continue

            pago_auto = pago_service.create_pago(
                db,
                cod_cliente=cod_cliente,
                fecha=fecha,
                monto=monto_abono,
                tipo_pago="abono_deuda",
                cod_item=deuda.cod_item,
                categoria=deuda.categoria,
                cliente_nombre=cliente.nombre,
                notas=f"Auto-abono a {deuda.cod_item} (deuda anterior FIFO)",
                created_by=created_by,
            )
            result.pagos.append(pago_auto)
            leftover_cash -= monto_abono
            auto_abonos_total += monto_abono

    result.abonos_deudas = total_abonos_explicitos + auto_abonos_total

    # ============================================================
    # FASE 7: crédito_generado por sobrante remanente
    # (cualquier cash que aún sobra después de items + abonos explícitos +
    # auto-abonos a deudas) → se convierte en crédito a favor del cliente.
    # ============================================================
    if leftover_cash > Decimal("0.01"):
        pago_excedente = pago_service.create_pago(
            db,
            cod_cliente=cod_cliente,
            fecha=fecha,
            monto=leftover_cash,
            tipo_pago="credito_generado",
            cliente_nombre=cliente.nombre,
            notas=f"Crédito generado por excedente del {fecha}",
            created_by=created_by,
        )
        result.pagos.append(pago_excedente)
        result.excedente_credito_generado = leftover_cash

    # ADR-0033: expose cliente creation status para audit log en caller
    result.cliente_was_created = cliente_was_created
    result.cliente_cod_lead_origen = cliente.cod_lead_origen
    result.cliente_vtiger_lead_id_origen = cliente.vtiger_lead_id_origen

    db.flush()
    return result


def list_by_cliente(db: Session, cod_cliente: str) -> list[Venta]:
    return list(
        db.execute(
            select(Venta)
            .where(Venta.cod_cliente == cod_cliente)
            .order_by(Venta.fecha.desc(), Venta.id.desc())
        )
        .scalars()
        .all()
    )


def get_by_cod_item(db: Session, cod_item: str) -> Optional[Venta]:
    return db.execute(select(Venta).where(Venta.cod_item == cod_item)).scalar_one_or_none()
