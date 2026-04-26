"""Agent API Calls + Budgets — tracking preciso de uso recursos LLM (Bloque 0.10).

Implementa el principio operativo `feedback_agent_resource_optimization`:
cada llamada a Claude/Anthropic API queda persistida con tokens + costo,
sujeta a budgets hard-limit por agente.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index,
    Integer, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models.base import Base


class AgentApiCall(Base):
    __tablename__ = "agent_api_calls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    task_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    prompt_template_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="anthropic")
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    request_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    input_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    cache_creation_input_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    cache_read_input_tokens: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=Decimal("0"))

    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    outcome: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    call_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "outcome IN ('success', 'error', 'rate_limited', 'budget_blocked')",
            name="ck_agent_api_calls_outcome",
        ),
        Index("idx_agent_api_calls_agent_occurred", "agent_name", "occurred_at"),
        Index("idx_agent_api_calls_task", "task_id"),
    )


class AgentBudget(Base):
    __tablename__ = "agent_budgets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    daily_usd_limit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_usd_limit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    alert_threshold_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    hard_block_at_limit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )


class AgentBudgetAlert(Base):
    __tablename__ = "agent_budget_alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope: Mapped[str] = mapped_column(String(16), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    usd_at_trigger: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    limit_at_trigger: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notified_via: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "alert_type IN ('warning', 'exceeded', 'reset')",
            name="ck_alerts_type",
        ),
        CheckConstraint("scope IN ('daily', 'monthly')", name="ck_alerts_scope"),
        Index("idx_agent_budget_alerts_agent_scope_triggered", "agent_name", "scope", "triggered_at"),
    )
