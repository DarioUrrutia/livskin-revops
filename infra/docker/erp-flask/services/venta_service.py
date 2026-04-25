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
from services import pago_service
from services.codgen_service import next_codigo


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
class SaveVentaResult:
    ventas: list[Venta] = field(default_factory=list)
    pagos: list[Pago] = field(default_factory=list)
    total_venta: Decimal = Decimal("0")
    total_pagado: Decimal = Decimal("0")
    excedente_credito_generado: Decimal = Decimal("0")
    credito_aplicado: Decimal = Decimal("0")
    abonos_deudas: Decimal = Decimal("0")


def save_venta(
    db: Session,
    cod_cliente: str,
    fecha: date,
    items: list[ItemVentaInput],
    metodos_pago: dict[str, Decimal],
    credito_aplicado: Decimal = Decimal("0"),
    abonos_deudas: Optional[list[AbonoDeudaInput]] = None,
    moneda: str = "PEN",
    tc: Optional[Decimal] = None,
    created_by: Optional[int] = None,
) -> SaveVentaResult:
    """Procesa las 6 fases en una sola transacción.

    Si cualquier fase falla → rollback completo (atomicidad).
    """
    if not items:
        raise ValueError("items no puede estar vacío")

    cliente = db.execute(
        select(Cliente).where(Cliente.cod_cliente == cod_cliente)
    ).scalar_one_or_none()
    if cliente is None:
        raise ClienteNoExiste(f"Cliente {cod_cliente} no existe")

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
    # FASE 1: generar códigos cod_item
    # ============================================================
    for item in items:
        prefijo = PREFIX_BY_TIPO[item.tipo]
        item.cod_item = next_codigo(db, Venta, "cod_item", prefijo)

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
    # FASE 4: crédito generado por excedente
    # ============================================================
    excedente = total_pagado_hoy - total_venta_dia
    if excedente > 0:
        pago_excedente = pago_service.create_pago(
            db,
            cod_cliente=cod_cliente,
            fecha=fecha,
            monto=excedente,
            tipo_pago="credito_generado",
            cliente_nombre=cliente.nombre,
            notas=f"Crédito generado por excedente del {fecha}",
            created_by=created_by,
        )
        result.pagos.append(pago_excedente)
        result.excedente_credito_generado = excedente

    # ============================================================
    # FASE 5: crédito aplicado
    # ============================================================
    if credito_aplicado > 0:
        balance = pago_service.credito_balance(db, cod_cliente)
        if credito_aplicado > balance:
            raise CreditoInsuficiente(
                f"Cliente {cod_cliente} tiene crédito S/.{balance} disponible, "
                f"solicitado S/.{credito_aplicado}"
            )
        pago_aplicado = pago_service.create_pago(
            db,
            cod_cliente=cod_cliente,
            fecha=fecha,
            monto=credito_aplicado,
            tipo_pago="credito_aplicado",
            cliente_nombre=cliente.nombre,
            notas=f"Crédito aplicado del {fecha}",
            created_by=created_by,
        )
        result.pagos.append(pago_aplicado)
        result.credito_aplicado = credito_aplicado

    # ============================================================
    # FASE 6: abonos a deudas anteriores
    # ============================================================
    total_abonos = Decimal("0")
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
        total_abonos += abono.monto
    result.abonos_deudas = total_abonos

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
