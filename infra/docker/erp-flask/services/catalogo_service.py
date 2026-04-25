"""CatalogoService — listas editables + seed inicial (ADR-0011 v1.1, ADR-0014).

Listas EDITABLES por admin via UI (/admin/catalogos):
- cat_Tratamiento, cat_Producto, cat_Certificado, area

Listas CODE-TIED (no editables sin cambio de código):
- tipo, fuente, canal_adquisicion, metodo_pago, tipo_pago,
  estado_lead, intent_level, nurture_state
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.catalogo import Catalogo


CATALOGOS_HARDCODED: dict[str, list[str]] = {
    # Code-tied — no se editan via UI sin cambio de código
    "tipo": ["Tratamiento", "Producto", "Certificado", "Promocion"],
    "fuente": [
        "meta_ad",
        "instagram_organic",
        "facebook_organic",
        "google_search",
        "google_ad",
        "tiktok_organic",
        "form_web",
        "whatsapp_directo",
        "referido",
        "walk_in",
        "otro",
        "organico",
    ],
    "canal_adquisicion": ["paid", "organic", "referral", "walk_in", "direct", "legacy"],
    "metodo_pago": ["efectivo", "yape", "plin", "giro", "tc"],
    "tipo_pago": ["normal", "credito_generado", "credito_aplicado", "abono_deuda"],
    "estado_lead": ["nuevo", "contactado", "agendado", "asistio", "cliente", "perdido"],
    "intent_level": ["investigando", "evaluando", "listo_comprar", "cold"],
    "nurture_state": ["inactivo", "activo", "pausado", "handed_off"],
}

CATALOGOS_SEED_FROM_EXCEL: dict[str, list[str]] = {
    # Editables — vienen del Excel Listas, evolucionan con el negocio
    "cat_Tratamiento": [
        "Botox",
        "Ácido Hialurónico",
        "PRP",
        "Hilos",
        "Limpieza Facial",
        "Exosoma / Vtech",
        "Esperma de Salmón",
        "Vitamina C / Cóctel de vida",
        "Ozono",
        "Autohemoterapia",
        "Infiltración",
        "Bioestimuladores",
        "Rinomodelación con Ac. Hialurónico",
        "Bléfaroplastia",
        "Cauterización",
        "Lifting Facial",
        "Microblending",
        "Pigmentación de Labios",
        "Retiro de Lipoma",
        "Subcisión con PRP",
        "Endovenosos",
    ],
    "cat_Producto": [
        "Aceite",
        "Bloqueador",
        "Centella Asiatica",
        "Crema",
        "Exfoliante",
        "Hidratante Forte",
        "Jabón",
        "Loción",
        "Mascarilla",
        "Shampoo",
        "Despigmentante",
        "Vitamina C Sérum",
    ],
    "cat_Certificado": ["Certificado Médico"],
    "area": [
        "3 Superior",
        "3 Inferior",
        "Ojeras",
        "Labios",
        "Patitas de Gallo",
        "Abdomen",
        "Piernas",
        "Espalda",
        "HF",
    ],
}


class CatalogoNotFoundError(Exception):
    pass


class CatalogoDuplicadoError(Exception):
    pass


def get_config_dict(db: Session) -> dict[str, list[str]]:
    """Retorna {lista: [valores activos]} — shape esperado por formulario.html.

    Usado por GET /api/config para poblar selects del formulario (tipo,
    cat_Tratamiento, cat_Producto, cat_Certificado, area).
    """
    rows = db.execute(
        select(Catalogo)
        .where(Catalogo.activo.is_(True))
        .order_by(Catalogo.lista, Catalogo.orden.nullslast(), Catalogo.valor)
    ).scalars().all()

    result: dict[str, list[str]] = {}
    for c in rows:
        result.setdefault(c.lista, []).append(c.valor)
    return result


def get_by_lista(db: Session, lista: str, only_active: bool = True) -> list[Catalogo]:
    stmt = select(Catalogo).where(Catalogo.lista == lista)
    if only_active:
        stmt = stmt.where(Catalogo.activo.is_(True))
    return list(
        db.execute(stmt.order_by(Catalogo.orden.nullslast(), Catalogo.valor)).scalars().all()
    )


def all_listas(db: Session) -> list[str]:
    return list(
        db.execute(select(Catalogo.lista).distinct().order_by(Catalogo.lista)).scalars().all()
    )


def add_valor(
    db: Session, lista: str, valor: str, orden: Optional[int] = None
) -> Catalogo:
    valor = valor.strip()
    if not valor:
        raise ValueError("valor no puede estar vacío")

    existing = db.execute(
        select(Catalogo).where(Catalogo.lista == lista, Catalogo.valor == valor)
    ).scalar_one_or_none()
    if existing is not None:
        if existing.activo:
            raise CatalogoDuplicadoError(f"Valor '{valor}' ya existe en lista '{lista}'")
        existing.activo = True
        db.flush()
        return existing

    cat = Catalogo(lista=lista, valor=valor, orden=orden, activo=True)
    db.add(cat)
    db.flush()
    return cat


def deactivate(db: Session, cat_id: int) -> Catalogo:
    cat = db.get(Catalogo, cat_id)
    if cat is None:
        raise CatalogoNotFoundError(f"Catálogo id={cat_id} no existe")
    cat.activo = False
    db.flush()
    return cat


def reactivate(db: Session, cat_id: int) -> Catalogo:
    cat = db.get(Catalogo, cat_id)
    if cat is None:
        raise CatalogoNotFoundError(f"Catálogo id={cat_id} no existe")
    cat.activo = True
    db.flush()
    return cat


def seed_initial(db: Session, force: bool = False) -> dict[str, int]:
    """Pobla la tabla catalogos con valores hardcoded + del Excel Listas.

    Idempotente: si una entrada ya existe, no la duplica.
    Returns: dict con count por lista de cuántos se insertaron.
    """
    inserted: dict[str, int] = {}

    all_seeds: dict[str, list[str]] = {**CATALOGOS_HARDCODED, **CATALOGOS_SEED_FROM_EXCEL}

    for lista, valores in all_seeds.items():
        count = 0
        for orden, valor in enumerate(valores, start=1):
            existing = db.execute(
                select(Catalogo).where(Catalogo.lista == lista, Catalogo.valor == valor)
            ).scalar_one_or_none()
            if existing is None:
                db.add(Catalogo(lista=lista, valor=valor, orden=orden, activo=True))
                count += 1
        inserted[lista] = count

    db.flush()
    return inserted
