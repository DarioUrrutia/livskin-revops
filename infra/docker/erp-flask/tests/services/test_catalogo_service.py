"""Tests de catalogo_service: listas editables + seed."""
import pytest

from models.catalogo import Catalogo
from services import catalogo_service


class TestGetConfigDict:
    def test_empty_db_returns_empty(self, db_session):
        assert catalogo_service.get_config_dict(db_session) == {}

    def test_groups_by_lista(self, db_session):
        db_session.add(Catalogo(lista="cat_Producto", valor="Crema", orden=1, activo=True))
        db_session.add(Catalogo(lista="cat_Producto", valor="Aceite", orden=2, activo=True))
        db_session.add(Catalogo(lista="cat_Tratamiento", valor="Botox", orden=1, activo=True))
        db_session.flush()

        result = catalogo_service.get_config_dict(db_session)
        assert "cat_Producto" in result
        assert "cat_Tratamiento" in result
        assert "Crema" in result["cat_Producto"]
        assert "Botox" in result["cat_Tratamiento"]

    def test_excludes_inactive(self, db_session):
        db_session.add(Catalogo(lista="x", valor="A", orden=1, activo=True))
        db_session.add(Catalogo(lista="x", valor="B", orden=2, activo=False))
        db_session.flush()

        result = catalogo_service.get_config_dict(db_session)
        assert "A" in result["x"]
        assert "B" not in result["x"]


class TestGetByLista:
    def test_returns_only_active_by_default(self, db_session):
        db_session.add(Catalogo(lista="x", valor="A", orden=1, activo=True))
        db_session.add(Catalogo(lista="x", valor="B", orden=2, activo=False))
        db_session.flush()

        rows = catalogo_service.get_by_lista(db_session, "x")
        assert len(rows) == 1
        assert rows[0].valor == "A"

    def test_includes_inactive_with_flag(self, db_session):
        db_session.add(Catalogo(lista="y", valor="A", orden=1, activo=True))
        db_session.add(Catalogo(lista="y", valor="B", orden=2, activo=False))
        db_session.flush()

        rows = catalogo_service.get_by_lista(db_session, "y", only_active=False)
        assert len(rows) == 2


class TestAllListas:
    def test_distinct_listas(self, db_session):
        db_session.add(Catalogo(lista="x", valor="A", orden=1, activo=True))
        db_session.add(Catalogo(lista="x", valor="B", orden=2, activo=True))
        db_session.add(Catalogo(lista="y", valor="C", orden=1, activo=True))
        db_session.flush()

        listas = catalogo_service.all_listas(db_session)
        assert set(listas) == {"x", "y"}


class TestAddValor:
    def test_add_new_valor(self, db_session):
        cat = catalogo_service.add_valor(db_session, "x", "Nuevo")
        assert cat.id is not None
        assert cat.activo is True
        assert cat.valor == "Nuevo"

    def test_add_strip_whitespace(self, db_session):
        cat = catalogo_service.add_valor(db_session, "x", "  espaciado  ")
        assert cat.valor == "espaciado"

    def test_add_empty_valor_raises(self, db_session):
        with pytest.raises(ValueError):
            catalogo_service.add_valor(db_session, "x", "")
        with pytest.raises(ValueError):
            catalogo_service.add_valor(db_session, "x", "   ")

    def test_add_duplicate_active_raises(self, db_session):
        catalogo_service.add_valor(db_session, "x", "Dup")
        with pytest.raises(catalogo_service.CatalogoDuplicadoError):
            catalogo_service.add_valor(db_session, "x", "Dup")

    def test_add_inactive_reactivates(self, db_session):
        cat = catalogo_service.add_valor(db_session, "x", "Foo")
        catalogo_service.deactivate(db_session, cat.id)
        cat2 = catalogo_service.add_valor(db_session, "x", "Foo")
        assert cat2.id == cat.id
        assert cat2.activo is True


class TestDeactivateReactivate:
    def test_deactivate_existing(self, db_session):
        cat = catalogo_service.add_valor(db_session, "x", "Foo")
        catalogo_service.deactivate(db_session, cat.id)
        db_session.refresh(cat)
        assert cat.activo is False

    def test_deactivate_unknown_raises(self, db_session):
        with pytest.raises(catalogo_service.CatalogoNotFoundError):
            catalogo_service.deactivate(db_session, 9999)

    def test_reactivate_existing(self, db_session):
        cat = catalogo_service.add_valor(db_session, "x", "Foo")
        catalogo_service.deactivate(db_session, cat.id)
        catalogo_service.reactivate(db_session, cat.id)
        db_session.refresh(cat)
        assert cat.activo is True

    def test_reactivate_unknown_raises(self, db_session):
        with pytest.raises(catalogo_service.CatalogoNotFoundError):
            catalogo_service.reactivate(db_session, 9999)


class TestSeedInitial:
    def test_seed_inserts_canonical(self, db_session):
        result = catalogo_service.seed_initial(db_session)
        # CATALOGOS_HARDCODED + CATALOGOS_SEED_FROM_EXCEL combinados
        assert "tipo" in result
        assert "cat_Tratamiento" in result
        assert result["tipo"] >= 4  # 4 tipos hardcoded
        assert result["cat_Tratamiento"] >= 20  # ~21 tratamientos

    def test_seed_idempotent(self, db_session):
        first = catalogo_service.seed_initial(db_session)
        db_session.flush()
        second = catalogo_service.seed_initial(db_session)
        # Segunda llamada inserta 0 (todo ya existe)
        assert all(v == 0 for v in second.values())
        # Pero la primera sí insertó cosas
        assert sum(first.values()) > 0
