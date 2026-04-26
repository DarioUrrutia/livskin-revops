"""Tests de audit_service (ADR-0027)."""
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from models.audit_log import AuditLog
from services import audit_service


class TestLog:
    def test_log_success_creates_entry(self, db_session, admin_user):
        audit_service.log(
            db_session,
            action="auth.login_success",
            entity_type="user",
            entity_id=str(admin_user.id),
            user_id=admin_user.id,
            user_username=admin_user.username,
            user_role=admin_user.rol,
            ip="1.2.3.4",
        )
        db_session.flush()
        entries = db_session.query(AuditLog).all()
        assert len(entries) == 1
        e = entries[0]
        assert e.action == "auth.login_success"
        assert e.category == "auth"
        assert e.entity_type == "user"
        assert e.user_id == admin_user.id
        assert e.user_username == admin_user.username
        assert e.user_role == "admin"
        assert str(e.ip) == "1.2.3.4"
        assert e.result == "success"

    def test_log_with_failure_result(self, db_session):
        audit_service.log(
            db_session,
            action="auth.login_failed",
            user_username="ghost",
            ip="5.6.7.8",
            result="failure",
            error_detail="CredencialesInvalidas",
        )
        db_session.flush()
        e = db_session.query(AuditLog).first()
        assert e.result == "failure"
        assert e.error_detail == "CredencialesInvalidas"

    def test_log_with_before_after_state(self, db_session):
        audit_service.log(
            db_session,
            action="cliente.updated",
            entity_type="cliente",
            entity_id="LIVCLIENT0001",
            before_state={"phone": "+5198888"},
            after_state={"phone": "+5199999"},
        )
        db_session.flush()
        e = db_session.query(AuditLog).first()
        assert e.before_state == {"phone": "+5198888"}
        assert e.after_state == {"phone": "+5199999"}

    def test_log_with_metadata(self, db_session):
        audit_service.log(
            db_session,
            action="venta.created",
            entity_type="venta",
            entity_id="LIVTRAT0001,LIVTRAT0002",
            metadata={"items_count": 2, "total": "200.00"},
        )
        db_session.flush()
        e = db_session.query(AuditLog).first()
        assert e.audit_metadata == {"items_count": 2, "total": "200.00"}

    def test_log_unknown_action_still_writes(self, db_session, caplog):
        audit_service.log(db_session, action="custom.brand_new_event")
        db_session.flush()
        e = db_session.query(AuditLog).first()
        assert e is not None
        assert e.action == "custom.brand_new_event"
        assert e.category == "custom"

    def test_log_action_without_dot_uses_unknown_category(self, db_session):
        audit_service.log(db_session, action="weird")
        db_session.flush()
        e = db_session.query(AuditLog).first()
        assert e.category == "unknown"

    def test_category_derived_from_action(self, db_session):
        audit_service.log(db_session, action="venta.created")
        db_session.flush()
        e = db_session.query(AuditLog).first()
        assert e.category == "venta"


class TestQueryAudit:
    def _seed(self, db_session, count_per_category: int = 2):
        """Ayudante: inserta N entries por cada categoría con timestamps escalonados."""
        actions = ["auth.login_success", "venta.created", "pago.created", "gasto.created"]
        for i, a in enumerate(actions):
            for j in range(count_per_category):
                audit_service.log(
                    db_session,
                    action=a,
                    user_username="dario" if i % 2 == 0 else "claudia",
                    user_role="admin" if i % 2 == 0 else "operadora",
                    result="success",
                    ip="1.2.3.4",
                )
        db_session.flush()

    def test_query_no_filters_returns_all_paginated(self, db_session):
        self._seed(db_session)
        entries, total = audit_service.query_audit(db_session, page=1, per_page=100)
        assert total == 8
        assert len(entries) == 8

    def test_query_pagination(self, db_session):
        self._seed(db_session)
        page1, total1 = audit_service.query_audit(db_session, page=1, per_page=3)
        page2, total2 = audit_service.query_audit(db_session, page=2, per_page=3)
        page3, total3 = audit_service.query_audit(db_session, page=3, per_page=3)
        assert total1 == total2 == total3 == 8
        assert len(page1) == 3
        assert len(page2) == 3
        assert len(page3) == 2
        ids = {e.id for e in page1} | {e.id for e in page2} | {e.id for e in page3}
        assert len(ids) == 8

    def test_query_filter_by_action(self, db_session):
        self._seed(db_session)
        entries, total = audit_service.query_audit(
            db_session, action="venta.created", page=1, per_page=100
        )
        assert total == 2
        assert all(e.action == "venta.created" for e in entries)

    def test_query_filter_by_category(self, db_session):
        self._seed(db_session)
        entries, total = audit_service.query_audit(
            db_session, category="auth", page=1, per_page=100
        )
        assert total == 2
        assert all(e.category == "auth" for e in entries)

    def test_query_filter_by_user(self, db_session):
        self._seed(db_session)
        entries, total = audit_service.query_audit(
            db_session, user_username="claudia", page=1, per_page=100
        )
        assert total == 4
        assert all(e.user_username == "claudia" for e in entries)

    def test_query_filter_by_result(self, db_session):
        audit_service.log(db_session, action="auth.login_success", result="success")
        audit_service.log(db_session, action="auth.login_failed", result="failure")
        audit_service.log(db_session, action="auth.login_failed", result="failure")
        db_session.flush()

        _, total_failure = audit_service.query_audit(db_session, result="failure", page=1, per_page=100)
        _, total_success = audit_service.query_audit(db_session, result="success", page=1, per_page=100)
        assert total_failure == 2
        assert total_success == 1

    def test_query_filter_by_entity_id_partial_match(self, db_session):
        audit_service.log(db_session, action="venta.created", entity_id="LIVTRAT0001")
        audit_service.log(db_session, action="venta.created", entity_id="LIVTRAT0002")
        audit_service.log(db_session, action="venta.created", entity_id="LIVPROD0010")
        db_session.flush()

        _, total = audit_service.query_audit(db_session, entity_id="LIVTRAT", page=1, per_page=100)
        assert total == 2

    def test_query_filter_by_date_range(self, db_session):
        # Insertar entries con timestamps específicos NO es trivial porque
        # occurred_at usa server_default=func.now(). Verificamos que el filtro
        # NO devuelve entries fuera del rango con un rango futuro.
        audit_service.log(db_session, action="auth.login_success")
        db_session.flush()

        future_date = date.today() + timedelta(days=10)
        _, total = audit_service.query_audit(
            db_session, fecha_desde=future_date, page=1, per_page=100
        )
        assert total == 0

    def test_query_ordered_desc_by_occurred_at(self, db_session):
        for i in range(3):
            audit_service.log(db_session, action="auth.login_success", metadata={"seq": i})
            db_session.flush()
        entries, _ = audit_service.query_audit(db_session, page=1, per_page=100)
        # Más reciente primero
        seqs = [e.audit_metadata["seq"] for e in entries]
        assert seqs == [2, 1, 0]


class TestListDistinctValues:
    def test_distinct_includes_canonical_actions(self, db_session):
        # Sin entries, debe retornar igual las KNOWN_ACTIONS canónicas
        result = audit_service.list_distinct_values(db_session)
        assert "auth.login_success" in result["actions"]
        assert "venta.created" in result["actions"]
        assert "pago.created" in result["actions"]
        assert "gasto.created" in result["actions"]
        assert "auth" in result["categories"]
        assert "venta" in result["categories"]
        assert "pago" in result["categories"]
        assert "gasto" in result["categories"]
        assert "cliente" in result["categories"]
        assert "lead" in result["categories"]
        assert "admin" in result["categories"]
        assert "webhook" in result["categories"]

    def test_distinct_users_from_db_only(self, db_session):
        audit_service.log(db_session, action="auth.login_success", user_username="dario")
        audit_service.log(db_session, action="auth.login_success", user_username="claudia")
        audit_service.log(db_session, action="auth.login_failed", user_username=None)  # sin user
        db_session.flush()

        result = audit_service.list_distinct_values(db_session)
        assert set(result["users"]) == {"dario", "claudia"}

    def test_distinct_includes_custom_action_in_db(self, db_session):
        audit_service.log(db_session, action="custom.event")
        db_session.flush()
        result = audit_service.list_distinct_values(db_session)
        assert "custom.event" in result["actions"]
        assert "custom" in result["categories"]


class TestImmutability:
    def test_update_audit_log_blocked_by_trigger(self, db_session):
        audit_service.log(db_session, action="auth.login_success", user_username="dario")
        db_session.flush()
        e = db_session.query(AuditLog).first()
        e.action = "hacked"
        with pytest.raises(Exception, match="audit_log es inmutable"):
            db_session.flush()
        db_session.rollback()

    def test_delete_audit_log_blocked_by_trigger(self, db_session):
        audit_service.log(db_session, action="auth.login_success", user_username="dario")
        db_session.flush()
        e = db_session.query(AuditLog).first()
        db_session.delete(e)
        with pytest.raises(Exception, match="audit_log es inmutable"):
            db_session.flush()
        db_session.rollback()

    def test_raw_sql_update_also_blocked(self, db_session):
        audit_service.log(db_session, action="auth.login_success")
        db_session.flush()
        with pytest.raises(Exception, match="audit_log es inmutable"):
            db_session.execute(text("UPDATE audit_log SET action='hacked'"))
            db_session.flush()
        db_session.rollback()
