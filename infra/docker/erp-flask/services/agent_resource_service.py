"""AgentResourceService — tracking + budgets de uso de LLM API por agentes.

Implementa el principio operativo (memoria `feedback_agent_resource_optimization`):
cada llamada queda persistida + budgets hard-limit + alertas.

Uso típico desde wrapper de agente (post-Fase 4):

    from services import agent_resource_service as ars

    # 1. Pre-check
    result = ars.check_budget_or_block(db, agent_name="conversation",
                                        estimated_cost_usd=Decimal("0.05"))
    if not result.can_proceed:
        raise BudgetExceeded(result.reason)

    # 2. Hacer call a Claude API
    response = anthropic_client.messages.create(...)

    # 3. Registrar (calcula cost desde tokens + model price)
    ars.record_call(
        db,
        agent_name="conversation",
        task_id=lead_id,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cache_read_input_tokens=getattr(response.usage, 'cache_read_input_tokens', 0),
        cache_creation_input_tokens=getattr(response.usage, 'cache_creation_input_tokens', 0),
        request_id=response.id,
        latency_ms=elapsed_ms,
        outcome="success",
    )

    # 4. AgentResourceService evalúa post-call si superó threshold
    #    → genera audit event infra.budget_warning o infra.budget_exceeded
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from models.agent_api_call import AgentApiCall, AgentBudget, AgentBudgetAlert
from services import audit_service

logger = logging.getLogger(__name__)


# Precios USD por 1M tokens para los modelos que vamos a usar.
# Fuente: https://www.anthropic.com/pricing
# Actualizar cuando cambien precios.
MODEL_PRICES = {
    # Opus 4.7
    "claude-opus-4-7": {
        "input": Decimal("15.00"),
        "output": Decimal("75.00"),
        "cache_write": Decimal("18.75"),  # 25% premium sobre input
        "cache_read": Decimal("1.50"),    # 90% descuento sobre input
    },
    "claude-opus-4-7-1m": {
        # 1M context — 2× pricing
        "input": Decimal("30.00"),
        "output": Decimal("150.00"),
        "cache_write": Decimal("37.50"),
        "cache_read": Decimal("3.00"),
    },
    # Sonnet 4.6
    "claude-sonnet-4-6": {
        "input": Decimal("3.00"),
        "output": Decimal("15.00"),
        "cache_write": Decimal("3.75"),
        "cache_read": Decimal("0.30"),
    },
    # Haiku 4.5
    "claude-haiku-4-5-20251001": {
        "input": Decimal("1.00"),
        "output": Decimal("5.00"),
        "cache_write": Decimal("1.25"),
        "cache_read": Decimal("0.10"),
    },
}


def calculate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
) -> Decimal:
    """Calcula costo USD para una llamada API según el modelo + tokens.

    Si modelo desconocido, asume Sonnet 4.6 pricing y log warning.
    """
    prices = MODEL_PRICES.get(model)
    if prices is None:
        logger.warning("agent_resource: modelo %s desconocido, asumiendo Sonnet 4.6", model)
        prices = MODEL_PRICES["claude-sonnet-4-6"]

    cost = (
        (Decimal(input_tokens) * prices["input"])
        + (Decimal(output_tokens) * prices["output"])
        + (Decimal(cache_creation_input_tokens) * prices["cache_write"])
        + (Decimal(cache_read_input_tokens) * prices["cache_read"])
    ) / Decimal("1000000")
    return cost.quantize(Decimal("0.000001"))


@dataclass
class BudgetCheckResult:
    can_proceed: bool
    reason: Optional[str] = None
    daily_consumed: Optional[Decimal] = None
    daily_limit: Optional[Decimal] = None
    monthly_consumed: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None


def check_budget_or_block(
    db: Session,
    *,
    agent_name: str,
    estimated_cost_usd: Decimal = Decimal("0.01"),
) -> BudgetCheckResult:
    """Pre-check antes de hacer un call. Returns can_proceed + razón.

    Si hard_block_at_limit=True y excedería, retorna can_proceed=False.
    """
    budget = db.execute(
        select(AgentBudget).where(AgentBudget.agent_name == agent_name)
    ).scalar_one_or_none()

    if budget is None or not budget.active:
        return BudgetCheckResult(
            can_proceed=False,
            reason=f"agent '{agent_name}' no tiene budget configurado o está inactivo",
        )

    daily = _get_daily_consumed(db, agent_name)
    monthly = _get_monthly_consumed(db, agent_name)

    daily_after = daily + estimated_cost_usd
    monthly_after = monthly + estimated_cost_usd

    if budget.hard_block_at_limit:
        if daily_after > budget.daily_usd_limit:
            return BudgetCheckResult(
                can_proceed=False,
                reason=f"daily budget exceeded ({daily_after} > {budget.daily_usd_limit})",
                daily_consumed=daily,
                daily_limit=budget.daily_usd_limit,
                monthly_consumed=monthly,
                monthly_limit=budget.monthly_usd_limit,
            )
        if monthly_after > budget.monthly_usd_limit:
            return BudgetCheckResult(
                can_proceed=False,
                reason=f"monthly budget exceeded ({monthly_after} > {budget.monthly_usd_limit})",
                daily_consumed=daily,
                daily_limit=budget.daily_usd_limit,
                monthly_consumed=monthly,
                monthly_limit=budget.monthly_usd_limit,
            )

    return BudgetCheckResult(
        can_proceed=True,
        daily_consumed=daily,
        daily_limit=budget.daily_usd_limit,
        monthly_consumed=monthly,
        monthly_limit=budget.monthly_usd_limit,
    )


def record_call(
    db: Session,
    *,
    agent_name: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
    task_id: Optional[str] = None,
    prompt_template_id: Optional[str] = None,
    request_id: Optional[str] = None,
    latency_ms: Optional[int] = None,
    outcome: str = "success",
    error_detail: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    cost_usd_override: Optional[Decimal] = None,
) -> AgentApiCall:
    """Persiste una llamada Claude API + actualiza budget tracking.

    Calcula `cost_usd` automáticamente desde tokens + model si no se
    proporciona override.

    Después del INSERT, evalúa si cruzó threshold (80% por default) y emite
    audit event correspondiente:
    - infra.budget_warning si cruzó por primera vez en el día/mes
    - infra.budget_exceeded si superó hard limit
    """
    cost_usd = cost_usd_override
    if cost_usd is None:
        cost_usd = calculate_cost_usd(
            model, input_tokens, output_tokens,
            cache_creation_input_tokens, cache_read_input_tokens,
        )

    call = AgentApiCall(
        agent_name=agent_name,
        task_id=task_id,
        prompt_template_id=prompt_template_id,
        provider="anthropic",
        model=model,
        request_id=request_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_input_tokens=cache_creation_input_tokens,
        cache_read_input_tokens=cache_read_input_tokens,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        outcome=outcome,
        error_detail=error_detail,
        call_metadata=metadata,
    )
    db.add(call)
    db.flush()

    # Audit event para el call mismo
    audit_service.log(
        db,
        action="agent.api_call_completed",
        entity_type="agent_api_call",
        entity_id=str(call.id),
        metadata={
            "agent": agent_name,
            "model": model,
            "tokens": input_tokens + output_tokens,
            "cost_usd": str(cost_usd),
            "outcome": outcome,
        },
        result=outcome if outcome in ("success", "error") else "success",
    )

    # Evaluar threshold post-INSERT
    _evaluate_thresholds(db, agent_name)

    return call


def _get_daily_consumed(db: Session, agent_name: str) -> Decimal:
    result = db.execute(
        text("SELECT daily_budget_consumed(:n)"), {"n": agent_name}
    ).scalar_one()
    return Decimal(str(result or 0))


def _get_monthly_consumed(db: Session, agent_name: str) -> Decimal:
    result = db.execute(
        text("SELECT monthly_budget_consumed(:n)"), {"n": agent_name}
    ).scalar_one()
    return Decimal(str(result or 0))


def _evaluate_thresholds(db: Session, agent_name: str) -> None:
    """Tras un INSERT, chequea si cruzamos warning/exceeded threshold.

    Genera audit event una sola vez por (agent, scope, alert_type, día):
    no spamear WhatsApp si ya alertamos hoy.
    """
    budget = db.execute(
        select(AgentBudget).where(AgentBudget.agent_name == agent_name)
    ).scalar_one_or_none()
    if budget is None:
        return

    daily = _get_daily_consumed(db, agent_name)
    monthly = _get_monthly_consumed(db, agent_name)

    # Daily warning
    daily_threshold = budget.daily_usd_limit * Decimal(budget.alert_threshold_pct) / 100
    if daily >= daily_threshold and daily < budget.daily_usd_limit:
        _emit_alert_if_new(
            db, agent_name, "warning", "daily", daily, budget.daily_usd_limit,
        )
    elif daily >= budget.daily_usd_limit:
        _emit_alert_if_new(
            db, agent_name, "exceeded", "daily", daily, budget.daily_usd_limit,
        )

    # Monthly warning
    monthly_threshold = budget.monthly_usd_limit * Decimal(budget.alert_threshold_pct) / 100
    if monthly >= monthly_threshold and monthly < budget.monthly_usd_limit:
        _emit_alert_if_new(
            db, agent_name, "warning", "monthly", monthly, budget.monthly_usd_limit,
        )
    elif monthly >= budget.monthly_usd_limit:
        _emit_alert_if_new(
            db, agent_name, "exceeded", "monthly", monthly, budget.monthly_usd_limit,
        )


def _emit_alert_if_new(
    db: Session,
    agent_name: str,
    alert_type: str,
    scope: str,
    consumed: Decimal,
    limit: Decimal,
) -> None:
    """Emite alert solo si no hay otra del mismo tipo HOY (dedup)."""
    today = datetime.now(timezone.utc).date()
    existing = db.execute(
        select(AgentBudgetAlert)
        .where(
            AgentBudgetAlert.agent_name == agent_name,
            AgentBudgetAlert.alert_type == alert_type,
            AgentBudgetAlert.scope == scope,
            func.date(AgentBudgetAlert.triggered_at) == today,
        )
        .limit(1)
    ).scalar_one_or_none()

    if existing is not None:
        return  # ya alertamos hoy del mismo tipo

    alert = AgentBudgetAlert(
        agent_name=agent_name,
        alert_type=alert_type,
        scope=scope,
        usd_at_trigger=consumed,
        limit_at_trigger=limit,
    )
    db.add(alert)

    audit_action = (
        "infra.budget_warning" if alert_type == "warning" else "infra.budget_exceeded"
    )
    audit_service.log(
        db,
        action=audit_action,
        entity_type="agent_budget",
        entity_id=agent_name,
        metadata={
            "scope": scope,
            "usd_consumed": str(consumed),
            "usd_limit": str(limit),
            "pct": float((consumed / limit) * 100) if limit > 0 else None,
        },
        result="success",
    )
    logger.warning(
        "agent_budget_%s: %s %s — %s/%s USD",
        alert_type, agent_name, scope, consumed, limit,
    )


def query_costs(
    db: Session,
    *,
    agent_name: Optional[str] = None,
    days: int = 30,
) -> dict[str, Any]:
    """Resumen de costos para dashboards.

    Returns:
        {
          "daily": [{"date": "2026-04-26", "agent": "conversation", "cost_usd": "1.25", "calls": 12}, ...],
          "totals": {
            "today": {agent: cost_usd},
            "this_month": {agent: cost_usd},
            "last_30_days": {agent: cost_usd},
          },
          "budgets": [{"agent": "conversation", "daily_limit": 3.00, "monthly_limit": 60.00, ...}]
        }
    """
    from sqlalchemy import case

    where_agent = (AgentApiCall.agent_name == agent_name) if agent_name else None

    # Daily breakdown
    daily_query = (
        select(
            func.date(AgentApiCall.occurred_at).label("date"),
            AgentApiCall.agent_name,
            func.sum(AgentApiCall.cost_usd).label("cost_usd"),
            func.count().label("calls"),
        )
        .where(AgentApiCall.occurred_at >= func.now() - text(f"INTERVAL '{days} days'"))
        .group_by(text("1"), AgentApiCall.agent_name)
        .order_by(text("1 DESC"))
    )
    if where_agent is not None:
        daily_query = daily_query.where(where_agent)

    daily = [
        {"date": str(r.date), "agent": r.agent_name, "cost_usd": float(r.cost_usd), "calls": r.calls}
        for r in db.execute(daily_query).all()
    ]

    # Totales
    today_total: dict[str, float] = {}
    month_total: dict[str, float] = {}
    last_30_total: dict[str, float] = {}

    today_q = select(AgentApiCall.agent_name, func.sum(AgentApiCall.cost_usd)).where(
        func.date(AgentApiCall.occurred_at) == func.current_date()
    ).group_by(AgentApiCall.agent_name)
    for ag, cost in db.execute(today_q).all():
        today_total[ag] = float(cost or 0)

    month_q = select(AgentApiCall.agent_name, func.sum(AgentApiCall.cost_usd)).where(
        func.date_trunc("month", AgentApiCall.occurred_at) == func.date_trunc("month", func.now())
    ).group_by(AgentApiCall.agent_name)
    for ag, cost in db.execute(month_q).all():
        month_total[ag] = float(cost or 0)

    last_30_q = select(AgentApiCall.agent_name, func.sum(AgentApiCall.cost_usd)).where(
        AgentApiCall.occurred_at >= func.now() - text("INTERVAL '30 days'")
    ).group_by(AgentApiCall.agent_name)
    for ag, cost in db.execute(last_30_q).all():
        last_30_total[ag] = float(cost or 0)

    # Budgets
    budgets = [
        {
            "agent": b.agent_name,
            "daily_limit_usd": float(b.daily_usd_limit),
            "monthly_limit_usd": float(b.monthly_usd_limit),
            "alert_threshold_pct": b.alert_threshold_pct,
            "hard_block_at_limit": b.hard_block_at_limit,
            "active": b.active,
            "daily_consumed_usd": today_total.get(b.agent_name, 0.0),
            "monthly_consumed_usd": month_total.get(b.agent_name, 0.0),
        }
        for b in db.execute(select(AgentBudget)).scalars()
    ]

    return {
        "daily": daily,
        "totals": {
            "today": today_total,
            "this_month": month_total,
            "last_30_days": last_30_total,
        },
        "budgets": budgets,
    }


def cleanup_old_calls(db: Session, *, retention_days: int = 90) -> int:
    """Borra raw events más viejos que retention_days. Retención corta porque
    la agregación a analytics.llm_costs (Fase 3+) preserva el histórico.
    """
    from sqlalchemy import delete
    cutoff = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    result = db.execute(
        delete(AgentApiCall).where(
            AgentApiCall.occurred_at < cutoff - text(f"INTERVAL '{retention_days} days'")
        )
    )
    return result.rowcount or 0
