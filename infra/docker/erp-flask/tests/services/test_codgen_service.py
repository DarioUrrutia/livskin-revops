"""Tests de codgen_service: generación de códigos LIVXXXX####."""
from models.cliente import Cliente
from services import cliente_service, codgen_service


class TestNextCodigo:
    def test_first_codigo_is_0001(self, db_session):
        cod = codgen_service.next_codigo(db_session, Cliente, "cod_cliente", "LIVCLIENT")
        assert cod == "LIVCLIENT0001"

    def test_returns_max_plus_1(self, db_session):
        cliente_service.create(db_session, nombre="A")
        cliente_service.create(db_session, nombre="B")
        cod = codgen_service.next_codigo(db_session, Cliente, "cod_cliente", "LIVCLIENT")
        assert cod == "LIVCLIENT0003"

    def test_padding_4_digits(self, db_session):
        cod = codgen_service.next_codigo(db_session, Cliente, "cod_cliente", "LIVCLIENT")
        assert len(cod.replace("LIVCLIENT", "")) == 4


class TestNextCodigosBatch:
    def test_batch_returns_consecutive(self, db_session):
        cods = codgen_service.next_codigos_batch(db_session, Cliente, "cod_cliente", "LIVCLIENT", 3)
        assert cods == ["LIVCLIENT0001", "LIVCLIENT0002", "LIVCLIENT0003"]

    def test_batch_empty_when_count_zero(self, db_session):
        cods = codgen_service.next_codigos_batch(db_session, Cliente, "cod_cliente", "LIVCLIENT", 0)
        assert cods == []

    def test_batch_starts_from_max_existing_plus_1(self, db_session):
        cliente_service.create(db_session, nombre="X")
        cods = codgen_service.next_codigos_batch(db_session, Cliente, "cod_cliente", "LIVCLIENT", 2)
        assert cods == ["LIVCLIENT0002", "LIVCLIENT0003"]

    def test_batch_no_duplicates_within(self, db_session):
        cods = codgen_service.next_codigos_batch(db_session, Cliente, "cod_cliente", "LIVCLIENT", 5)
        assert len(set(cods)) == 5
