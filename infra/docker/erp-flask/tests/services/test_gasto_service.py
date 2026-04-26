"""Tests de gasto_service (CRUD básico)."""
from datetime import date
from decimal import Decimal

from models.gasto import Gasto
from services import gasto_service


class TestCreateGasto:
    def test_create_minimal(self, db_session):
        g = gasto_service.create(
            db_session,
            fecha=date(2026, 4, 26),
            monto=Decimal("100"),
        )
        assert g.id is not None
        assert g.fecha == date(2026, 4, 26)
        assert g.monto == Decimal("100")

    def test_create_with_full_fields(self, db_session):
        g = gasto_service.create(
            db_session,
            fecha=date(2026, 4, 26),
            monto=Decimal("250.50"),
            tipo="Insumos",
            descripcion="Compra de jeringas",
            destinatario="Proveedor X",
            metodo_pago="efectivo",
        )
        assert g.tipo == "Insumos"
        assert g.descripcion == "Compra de jeringas"
        assert g.destinatario == "Proveedor X"
        assert g.metodo_pago == "efectivo"

    def test_create_persists(self, db_session):
        g = gasto_service.create(
            db_session,
            fecha=date(2026, 4, 26),
            monto=Decimal("50"),
        )
        db_session.flush()
        found = db_session.query(Gasto).filter_by(id=g.id).first()
        assert found is not None
        assert found.monto == Decimal("50")
