"""Tests para cliente_service.search_lead_match() + extensión create() con cod_lead_origen.

ADR-0033 — Match automático lead↔cliente al crear cliente en ERP.

Cubre:
- search_lead_match: prioridad phone > email > nombre fuzzy; ambigüedad → None
- search_lead_match: excluye leads ya convertidos (cod_lead aparece en clientes.cod_lead_origen)
- create con cod_lead_origen: copia attribution UTMs del lead al cliente y setea vtiger_lead_id_origen
"""
from datetime import date, datetime, timezone

import pytest

from models.cliente import Cliente
from models.lead import Lead
from services import cliente_service


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _make_lead(
    db,
    *,
    cod_lead: str,
    nombre: str = "Sofia Test",
    phone_e164: str = "+51999111222",
    email_lower: str | None = None,
    vtiger_id: str | None = "10x100",
    fuente: str = "facebook",
    canal_adquisicion: str = "meta-ads",
    utm_source: str = "facebook",
    utm_campaign: str = "botox-mvp",
    fbclid: str | None = "IwAR1xyz",
    event_id: str | None = "evt-uuid-1",
    tratamiento_interes: str = "Botox",
    fecha_captura: datetime | None = None,
) -> Lead:
    lead = Lead(
        cod_lead=cod_lead,
        vtiger_id=vtiger_id,
        nombre=nombre,
        phone_e164=phone_e164,
        email_lower=email_lower,
        fuente=fuente,
        canal_adquisicion=canal_adquisicion,
        utm_source_at_capture=utm_source,
        utm_campaign_at_capture=utm_campaign,
        fbclid_at_capture=fbclid,
        event_id_at_capture=event_id,
        tratamiento_interes=tratamiento_interes,
        consent_marketing=True,
        estado_lead="nuevo",
        fecha_captura=fecha_captura or datetime.now(timezone.utc),
    )
    db.add(lead)
    db.flush()
    return lead


# ─────────────────────────────────────────────────────────────────────
# search_lead_match — match por phone (priority 1)
# ─────────────────────────────────────────────────────────────────────

class TestSearchByPhone:
    def test_finds_by_exact_phone_e164(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0001", phone_e164="+51900111222")
        match = cliente_service.search_lead_match(db_session, phone_e164="+51900111222")
        assert match is not None
        assert match.cod_lead == "LIVLEAD0001"

    def test_normalizes_phone_before_lookup(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0001", phone_e164="+51987654321")
        # Mismo número con guiones — service debe normalizar
        match = cliente_service.search_lead_match(db_session, phone_raw="987-654-321")
        assert match is not None
        assert match.cod_lead == "LIVLEAD0001"

    def test_phone_match_ignores_email_and_nombre_when_phone_present(self, db_session):
        # Phone es priority 1: si hay match por phone, ignora email/nombre conflictivos
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0001",
            phone_e164="+51999111111",
            email_lower="distinto@test.com",
            nombre="Juan Distinto",
        )
        match = cliente_service.search_lead_match(
            db_session,
            phone_e164="+51999111111",
            email_lower="otro@test.com",
            nombre="Otro Nombre",
        )
        assert match is not None
        assert match.cod_lead == "LIVLEAD0001"

    def test_no_phone_match_returns_none(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0001", phone_e164="+51999111111")
        match = cliente_service.search_lead_match(db_session, phone_e164="+51999999999")
        assert match is None


# ─────────────────────────────────────────────────────────────────────
# search_lead_match — match por email (priority 2)
# ─────────────────────────────────────────────────────────────────────

class TestSearchByEmail:
    def test_finds_by_email_lower_when_no_phone(self, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0002",
            phone_e164="+51900222333",
            email_lower="sofia@test.com",
        )
        match = cliente_service.search_lead_match(db_session, email_lower="sofia@test.com")
        assert match is not None
        assert match.cod_lead == "LIVLEAD0002"

    def test_normalizes_email_case_and_whitespace(self, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0002",
            email_lower="sofia@test.com",
        )
        match = cliente_service.search_lead_match(db_session, email_raw="  SOFIA@TEST.COM  ")
        assert match is not None
        assert match.cod_lead == "LIVLEAD0002"

    def test_no_email_match_returns_none(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0002", email_lower="x@test.com")
        match = cliente_service.search_lead_match(db_session, email_lower="otro@test.com")
        assert match is None


# ─────────────────────────────────────────────────────────────────────
# search_lead_match — match por nombre fuzzy (priority 3)
# ─────────────────────────────────────────────────────────────────────

class TestSearchByNombreFuzzy:
    def test_finds_by_exact_nombre_when_no_phone_no_email(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0003", nombre="Sofia Mendoza")
        match = cliente_service.search_lead_match(db_session, nombre="Sofia Mendoza")
        assert match is not None
        assert match.cod_lead == "LIVLEAD0003"

    def test_finds_by_nombre_case_insensitive(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0003", nombre="Sofia Mendoza")
        match = cliente_service.search_lead_match(db_session, nombre="SOFIA mendoza")
        assert match is not None
        assert match.cod_lead == "LIVLEAD0003"

    def test_no_nombre_match_returns_none(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0003", nombre="Sofia Mendoza")
        match = cliente_service.search_lead_match(db_session, nombre="Pedro Otro")
        assert match is None


# ─────────────────────────────────────────────────────────────────────
# search_lead_match — ambigüedad y exclusiones
# ─────────────────────────────────────────────────────────────────────

class TestSearchAmbiguity:
    def test_multiple_phone_matches_returns_none(self, db_session):
        # 2 leads con mismo phone (no debería pasar en prod pero el service no
        # debe auto-vincular cuando hay ambigüedad)
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0010",
            phone_e164="+51900555000",
            vtiger_id="10x10",
        )
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0011",
            phone_e164="+51900555000",
            vtiger_id="10x11",
        )
        match = cliente_service.search_lead_match(db_session, phone_e164="+51900555000")
        assert match is None

    def test_multiple_email_matches_returns_none(self, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0020",
            phone_e164="+51900666000",
            email_lower="dup@test.com",
            vtiger_id="10x20",
        )
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0021",
            phone_e164="+51900666001",
            email_lower="dup@test.com",
            vtiger_id="10x21",
        )
        match = cliente_service.search_lead_match(db_session, email_lower="dup@test.com")
        assert match is None

    def test_multiple_nombre_matches_returns_none(self, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0030",
            phone_e164="+51900777000",
            nombre="Maria Gonzalez",
            vtiger_id="10x30",
        )
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0031",
            phone_e164="+51900777001",
            nombre="Maria Gonzalez",
            vtiger_id="10x31",
        )
        match = cliente_service.search_lead_match(db_session, nombre="Maria Gonzalez")
        assert match is None


class TestSearchExcludesConverted:
    def test_lead_already_converted_to_cliente_excluded(self, db_session):
        # Crear lead + cliente que ya tiene cod_lead_origen apuntando al lead
        _make_lead(db_session, cod_lead="LIVLEAD0040", phone_e164="+51900888000")

        # Cliente convertido (vincula al lead)
        cliente_service.create(
            db_session,
            nombre="Sofia Convertida",
            phone_raw="+51900888999",
            cod_lead_origen="LIVLEAD0040",
        )

        # Search por phone del lead → no match (lead excluido por estar convertido)
        match = cliente_service.search_lead_match(db_session, phone_e164="+51900888000")
        assert match is None

    def test_other_unconverted_lead_still_matches(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0050", phone_e164="+51900999000")
        _make_lead(db_session, cod_lead="LIVLEAD0051", phone_e164="+51900999111")

        cliente_service.create(
            db_session,
            nombre="Sofia Convertida",
            phone_raw="+51900999000",
            cod_lead_origen="LIVLEAD0050",
        )

        # El segundo lead sigue match-eable
        match = cliente_service.search_lead_match(db_session, phone_e164="+51900999111")
        assert match is not None
        assert match.cod_lead == "LIVLEAD0051"


# ─────────────────────────────────────────────────────────────────────
# search_lead_match — sin parámetros / params vacíos
# ─────────────────────────────────────────────────────────────────────

class TestSearchEmptyParams:
    def test_no_params_returns_none(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0001", phone_e164="+51900111222")
        match = cliente_service.search_lead_match(db_session)
        assert match is None

    def test_only_empty_strings_returns_none(self, db_session):
        _make_lead(db_session, cod_lead="LIVLEAD0001", phone_e164="+51900111222")
        match = cliente_service.search_lead_match(
            db_session, phone_e164="", email_lower="", nombre=""
        )
        assert match is None

    def test_invalid_phone_treated_as_no_phone(self, db_session):
        # Phone inválido → no normaliza → service intenta email/nombre
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0001",
            phone_e164="+51900111222",
            email_lower="x@test.com",
        )
        match = cliente_service.search_lead_match(
            db_session, phone_raw="abc", email_raw="x@test.com"
        )
        assert match is not None
        assert match.cod_lead == "LIVLEAD0001"


# ─────────────────────────────────────────────────────────────────────
# create() extension — cod_lead_origen copia attribution
# ─────────────────────────────────────────────────────────────────────

class TestCreateWithCodLeadOrigen:
    def test_create_with_cod_lead_origen_copies_attribution(self, db_session):
        _make_lead(
            db_session,
            cod_lead="LIVLEAD0100",
            vtiger_id="10x100",
            phone_e164="+51900100100",
            utm_source="facebook",
            utm_campaign="botox-mvp",
            fbclid="IwAR_origin",
            event_id="evt-origin-uuid",
        )

        cliente = cliente_service.create(
            db_session,
            nombre="Sofia Walk-in",
            phone_raw="+51900100200",
            cod_lead_origen="LIVLEAD0100",
        )

        assert cliente.cod_lead_origen == "LIVLEAD0100"
        assert cliente.vtiger_lead_id_origen == "10x100"
        assert cliente.utm_source_at_capture == "facebook"
        assert cliente.utm_campaign_at_capture == "botox-mvp"
        assert cliente.fbclid_at_capture == "IwAR_origin"
        # canal_adquisicion debe pasarse a "digital" o equivalente del lead
        assert cliente.canal_adquisicion in ("meta-ads", "digital", "facebook")

    def test_create_without_cod_lead_origen_leaves_attribution_empty(self, db_session):
        cliente = cliente_service.create(
            db_session,
            nombre="Carmen Walk-in",
            phone_raw="+51900100300",
        )
        assert cliente.cod_lead_origen is None
        assert cliente.vtiger_lead_id_origen is None
        assert cliente.utm_source_at_capture is None

    def test_create_with_invalid_cod_lead_origen_raises(self, db_session):
        with pytest.raises(cliente_service.LeadOrigenNotFoundError):
            cliente_service.create(
                db_session,
                nombre="Sofia Bad Link",
                phone_raw="+51900100400",
                cod_lead_origen="LIVLEAD9999",
            )
