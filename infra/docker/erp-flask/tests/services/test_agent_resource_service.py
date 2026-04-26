"""Tests de agent_resource_service (Bloque 0.10)."""
from decimal import Decimal

import pytest

from models.agent_api_call import AgentApiCall, AgentBudget, AgentBudgetAlert
from models.audit_log import AuditLog
from services import agent_resource_service as ars


def _seed_budget(db_session, agent="conversation", daily=Decimal("3"), monthly=Decimal("60")):
    b = AgentBudget(
        agent_name=agent,
        daily_usd_limit=daily,
        monthly_usd_limit=monthly,
        alert_threshold_pct=80,
        hard_block_at_limit=True,
        active=True,
    )
    db_session.add(b)
    db_session.commit()
    return b


class TestCalculateCostUsd:
    def test_sonnet_input_only(self):
        # 1M input tokens × $3 = $3
        cost = ars.calculate_cost_usd("claude-sonnet-4-6", 1_000_000, 0)
        assert cost == Decimal("3.000000")

    def test_sonnet_input_and_output(self):
        # 1M input × $3 + 1M output × $15 = $18
        cost = ars.calculate_cost_usd("claude-sonnet-4-6", 1_000_000, 1_000_000)
        assert cost == Decimal("18.000000")

    def test_opus_more_expensive(self):
        # 1M input × $15 + 1M output × $75 = $90
        cost = ars.calculate_cost_usd("claude-opus-4-7", 1_000_000, 1_000_000)
        assert cost == Decimal("90.000000")

    def test_haiku_cheaper(self):
        # 1M input × $1 + 1M output × $5 = $6
        cost = ars.calculate_cost_usd("claude-haiku-4-5-20251001", 1_000_000, 1_000_000)
        assert cost == Decimal("6.000000")

    def test_cache_read_90pct_discount(self):
        # 1M cache_read × $0.30 (Sonnet) = $0.30 (vs $3 sin cache)
        cost = ars.calculate_cost_usd(
            "claude-sonnet-4-6", 0, 0, cache_read_input_tokens=1_000_000
        )
        assert cost == Decimal("0.300000")

    def test_unknown_model_falls_back_to_sonnet(self, caplog):
        cost = ars.calculate_cost_usd("inventado-model", 1_000_000, 0)
        # Fallback Sonnet → $3 por 1M input
        assert cost == Decimal("3.000000")

    def test_small_call_precision(self):
        # 100 tokens input + 50 output con Sonnet
        # (100 × $3 + 50 × $15) / 1M = (300 + 750) / 1M = 1050/1M = $0.001050
        cost = ars.calculate_cost_usd("claude-sonnet-4-6", 100, 50)
        assert cost == Decimal("0.001050")


class TestCheckBudgetOrBlock:
    def test_no_budget_blocks(self, db_session):
        result = ars.check_budget_or_block(
            db_session,
            agent_name="ghost-agent",
            estimated_cost_usd=Decimal("0.01"),
        )
        assert result.can_proceed is False
        assert "no tiene budget" in (result.reason or "").lower()

    def test_inactive_budget_blocks(self, db_session):
        b = _seed_budget(db_session, agent="inactive-test")
        b.active = False
        db_session.commit()
        result = ars.check_budget_or_block(
            db_session,
            agent_name="inactive-test",
            estimated_cost_usd=Decimal("0.01"),
        )
        assert result.can_proceed is False

    def test_within_budget_proceeds(self, db_session):
        _seed_budget(db_session, agent="conv-1", daily=Decimal("1"), monthly=Decimal("30"))
        result = ars.check_budget_or_block(
            db_session,
            agent_name="conv-1",
            estimated_cost_usd=Decimal("0.05"),
        )
        assert result.can_proceed is True
        assert result.daily_consumed == Decimal("0")
        assert result.daily_limit == Decimal("1")

    def test_estimated_exceeds_daily_blocks(self, db_session):
        _seed_budget(db_session, agent="conv-2", daily=Decimal("0.10"), monthly=Decimal("30"))
        # Pre-existente call de 0.08 → daily=0.08
        ars.record_call(
            db_session,
            agent_name="conv-2",
            model="claude-sonnet-4-6",
            input_tokens=20_000,  # 20k × $3 / 1M = $0.06
            output_tokens=2_000,  # 2k × $15 / 1M = $0.03
        )
        # cost = 0.06 + 0.03 = 0.09. daily_after = 0.09 + 0.05 estimated = 0.14 > 0.10
        db_session.commit()

        result = ars.check_budget_or_block(
            db_session,
            agent_name="conv-2",
            estimated_cost_usd=Decimal("0.05"),
        )
        assert result.can_proceed is False
        assert "daily" in result.reason.lower()


class TestRecordCall:
    def test_basic_record(self, db_session):
        _seed_budget(db_session, agent="rec-1")
        call = ars.record_call(
            db_session,
            agent_name="rec-1",
            model="claude-sonnet-4-6",
            input_tokens=1000,
            output_tokens=500,
            task_id="lead_42",
        )
        db_session.flush()
        assert call.id is not None
        assert call.agent_name == "rec-1"
        assert call.input_tokens == 1000
        assert call.cost_usd > Decimal("0")
        # 1k × $3 + 500 × $15 / 1M = (3000 + 7500) / 1M = 0.0105
        assert call.cost_usd == Decimal("0.010500")

    def test_record_emits_audit_event(self, db_session):
        _seed_budget(db_session, agent="rec-2")
        ars.record_call(
            db_session,
            agent_name="rec-2",
            model="claude-sonnet-4-6",
            input_tokens=100,
            output_tokens=50,
        )
        db_session.flush()
        events = db_session.query(AuditLog).filter(
            AuditLog.action == "agent.api_call_completed"
        ).all()
        assert len(events) >= 1

    def test_record_with_cache_metadata(self, db_session):
        _seed_budget(db_session, agent="rec-3")
        call = ars.record_call(
            db_session,
            agent_name="rec-3",
            model="claude-sonnet-4-6",
            input_tokens=10000,
            output_tokens=2000,
            cache_creation_input_tokens=5000,
            cache_read_input_tokens=20000,
            metadata={"prompt_version": "v2", "lead_score_pre": 65},
        )
        assert call.cache_creation_input_tokens == 5000
        assert call.cache_read_input_tokens == 20000
        assert call.call_metadata["prompt_version"] == "v2"


class TestThresholdAlerts:
    def test_warning_emitted_at_80pct(self, db_session):
        _seed_budget(db_session, agent="alert-1", daily=Decimal("0.10"))
        # Cargar hasta 0.085 (>80% de 0.10)
        ars.record_call(
            db_session,
            agent_name="alert-1",
            model="claude-sonnet-4-6",
            input_tokens=20000,  # ~0.06
            output_tokens=2000,
        )
        # Acumulado debería ser ~0.09
        ars.record_call(
            db_session,
            agent_name="alert-1",
            model="claude-sonnet-4-6",
            input_tokens=1,
            output_tokens=1,
        )
        db_session.flush()

        # Debe haber warning (>=80%) pero NO exceeded (sigue debajo de 100%)
        alerts = db_session.query(AgentBudgetAlert).filter(
            AgentBudgetAlert.agent_name == "alert-1"
        ).all()
        assert any(a.alert_type == "warning" and a.scope == "daily" for a in alerts)
        assert all(a.alert_type != "exceeded" for a in alerts)

    def test_exceeded_emitted_above_100pct(self, db_session):
        _seed_budget(db_session, agent="alert-2", daily=Decimal("0.05"))
        ars.record_call(
            db_session,
            agent_name="alert-2",
            model="claude-sonnet-4-6",
            input_tokens=20000,
            output_tokens=2000,  # ~0.09 USD > 0.05 limit
        )
        db_session.flush()
        alerts = db_session.query(AgentBudgetAlert).filter(
            AgentBudgetAlert.agent_name == "alert-2"
        ).all()
        assert any(a.alert_type == "exceeded" and a.scope == "daily" for a in alerts)

    def test_alerts_dedup_per_day(self, db_session):
        _seed_budget(db_session, agent="alert-3", daily=Decimal("0.05"))
        # 2 calls que ambas exceden — solo debe haber 1 alert
        for _ in range(2):
            ars.record_call(
                db_session,
                agent_name="alert-3",
                model="claude-sonnet-4-6",
                input_tokens=20000,
                output_tokens=2000,
            )
        db_session.flush()

        exceeded_alerts = db_session.query(AgentBudgetAlert).filter(
            AgentBudgetAlert.agent_name == "alert-3",
            AgentBudgetAlert.alert_type == "exceeded",
            AgentBudgetAlert.scope == "daily",
        ).all()
        assert len(exceeded_alerts) == 1


class TestQueryCosts:
    def test_empty_returns_budgets_only(self, db_session):
        _seed_budget(db_session, agent="qc-1")
        result = ars.query_costs(db_session, days=30)
        assert "budgets" in result
        assert any(b["agent"] == "qc-1" for b in result["budgets"])
        assert result["daily"] == []

    def test_with_calls_returns_aggregates(self, db_session):
        _seed_budget(db_session, agent="qc-2")
        for _ in range(3):
            ars.record_call(
                db_session,
                agent_name="qc-2",
                model="claude-sonnet-4-6",
                input_tokens=1000,
                output_tokens=500,
            )
        db_session.flush()

        result = ars.query_costs(db_session, days=30)
        assert len(result["daily"]) >= 1
        budget = next(b for b in result["budgets"] if b["agent"] == "qc-2")
        assert budget["daily_consumed_usd"] > 0
