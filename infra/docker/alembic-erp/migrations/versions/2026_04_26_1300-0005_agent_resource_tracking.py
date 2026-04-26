"""0005 agent resource tracking — agent_api_calls + agent_budgets + alerts

Revision ID: 0005_agent_resource_tracking
Revises: 0004_infra_snapshots
Create Date: 2026-04-26 13:00:00.000000+00:00

Tablas para tracking preciso de uso de recursos por agentes IA.

`agent_api_calls`: append-only raw events de cada llamada Claude API.
   Se llena desde POST /api/internal/agent-api-call. Retención 90 días
   (cleanup cron diario). Aggregación a analytics.llm_costs en Fase 3.

`agent_budgets`: configuración de límites por agente. Solo admin modifica.

`agent_budget_alerts`: estado de alertas para deduplicar (no spamear
   WhatsApp si ya alertamos por el mismo budget hoy).

Triggers:
- Función `record_agent_api_call(...)` que inserta en agent_api_calls Y
  evalúa budget actual. Si excedió: trigger BEFORE INSERT bloquea + raises
- Función `daily_budget_consumed(agent_name)` retorna USD consumido hoy
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_agent_resource_tracking"
down_revision: Union[str, None] = "0004_infra_snapshots"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # agent_api_calls — raw events
    # ============================================================
    op.create_table(
        "agent_api_calls",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),

        # Identificación
        sa.Column("agent_name", sa.String(64), nullable=False),
        sa.Column("task_id", sa.String(128), nullable=True),  # ej: lead_id, campaign_id
        sa.Column("prompt_template_id", sa.String(128), nullable=True),  # versionado del prompt

        # Detalles del provider
        sa.Column("provider", sa.String(32), nullable=False, server_default="anthropic"),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("request_id", sa.String(128), nullable=True),  # del Anthropic API response

        # Tokens (precisión total)
        sa.Column("input_tokens", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("cache_creation_input_tokens", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("cache_read_input_tokens", sa.BigInteger, nullable=False, server_default="0"),

        # Costo en USD (calculado al instante con precios al momento del call)
        sa.Column("cost_usd", sa.Numeric(10, 6), nullable=False, server_default="0"),

        # Performance
        sa.Column("latency_ms", sa.Integer, nullable=True),

        # Outcome
        sa.Column("outcome", sa.String(32), nullable=False, server_default="success"),
        sa.Column("error_detail", sa.Text, nullable=True),

        # Metadata adicional (contexto específico del agente)
        sa.Column("metadata", sa.dialects.postgresql.JSONB, nullable=True),

        sa.CheckConstraint(
            "outcome IN ('success', 'error', 'rate_limited', 'budget_blocked')",
            name="ck_agent_api_calls_outcome",
        ),
    )
    op.create_index(
        "idx_agent_api_calls_occurred",
        "agent_api_calls",
        [sa.text("occurred_at DESC")],
    )
    op.create_index(
        "idx_agent_api_calls_agent_occurred",
        "agent_api_calls",
        ["agent_name", sa.text("occurred_at DESC")],
    )
    op.create_index(
        "idx_agent_api_calls_task",
        "agent_api_calls",
        ["task_id"],
    )

    # ============================================================
    # agent_budgets — configuración por agente
    # ============================================================
    op.create_table(
        "agent_budgets",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("agent_name", sa.String(64), nullable=False, unique=True),

        # Límites
        sa.Column("daily_usd_limit", sa.Numeric(10, 2), nullable=False),
        sa.Column("monthly_usd_limit", sa.Numeric(10, 2), nullable=False),

        # Alertas
        sa.Column("alert_threshold_pct", sa.Integer, nullable=False, server_default="80"),
        sa.Column("hard_block_at_limit", sa.Boolean, nullable=False, server_default="true"),

        # Status
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notes", sa.Text, nullable=True),

        # Audit
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=True),

        sa.CheckConstraint(
            "alert_threshold_pct > 0 AND alert_threshold_pct <= 100",
            name="ck_agent_budgets_threshold",
        ),
        sa.CheckConstraint(
            "daily_usd_limit > 0 AND monthly_usd_limit > 0",
            name="ck_agent_budgets_limits_positive",
        ),
    )

    # Seed defaults MVP-light ($134/mes total — decision Dario 2026-04-26)
    # Subir budgets cuando los agentes generen ROI claro (esperar Fase 5+ data real).
    op.execute("""
        INSERT INTO agent_budgets (agent_name, daily_usd_limit, monthly_usd_limit, alert_threshold_pct, hard_block_at_limit, active, notes)
        VALUES
            ('conversation', 1.50, 45.00, 80, true, true, 'MVP-light: subir cuando volumen real lo justifique'),
            ('content', 2.00, 60.00, 80, true, true, 'MVP-light: Brand Orchestrator director creativo (Fase 5)'),
            ('acquisition', 0.50, 15.00, 80, true, true, 'MVP-light: Meta + Google ads optimization'),
            ('growth', 0.30, 9.00, 80, true, true, 'MVP-light: weekly digest analitico'),
            ('infra-security', 0.20, 5.00, 80, true, true, 'MVP-light: 5to agente post-Fase 6');
    """)

    # ============================================================
    # agent_budget_alerts — dedup state
    # ============================================================
    op.create_table(
        "agent_budget_alerts",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("agent_name", sa.String(64), nullable=False),
        sa.Column("alert_type", sa.String(32), nullable=False),  # warning | exceeded | reset
        sa.Column("scope", sa.String(16), nullable=False),  # daily | monthly
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("usd_at_trigger", sa.Numeric(10, 4), nullable=False),
        sa.Column("limit_at_trigger", sa.Numeric(10, 2), nullable=False),
        sa.Column("notified_via", sa.String(32), nullable=True),  # whatsapp | email | none

        sa.CheckConstraint("alert_type IN ('warning', 'exceeded', 'reset')",
                          name="ck_alerts_type"),
        sa.CheckConstraint("scope IN ('daily', 'monthly')", name="ck_alerts_scope"),
    )
    op.create_index(
        "idx_agent_budget_alerts_agent_scope_triggered",
        "agent_budget_alerts",
        ["agent_name", "scope", sa.text("triggered_at DESC")],
    )

    # ============================================================
    # Funciones SQL helper
    # ============================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION daily_budget_consumed(p_agent_name TEXT)
        RETURNS NUMERIC AS $$
        DECLARE
            consumed NUMERIC(10,4);
        BEGIN
            SELECT COALESCE(SUM(cost_usd), 0) INTO consumed
            FROM agent_api_calls
            WHERE agent_name = p_agent_name
              AND occurred_at::date = CURRENT_DATE
              AND outcome IN ('success', 'error');  -- rate_limited y budget_blocked no cuentan
            RETURN consumed;
        END;
        $$ LANGUAGE plpgsql STABLE;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION monthly_budget_consumed(p_agent_name TEXT)
        RETURNS NUMERIC AS $$
        DECLARE
            consumed NUMERIC(10,4);
        BEGIN
            SELECT COALESCE(SUM(cost_usd), 0) INTO consumed
            FROM agent_api_calls
            WHERE agent_name = p_agent_name
              AND date_trunc('month', occurred_at) = date_trunc('month', NOW())
              AND outcome IN ('success', 'error');
            RETURN consumed;
        END;
        $$ LANGUAGE plpgsql STABLE;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS monthly_budget_consumed(TEXT);")
    op.execute("DROP FUNCTION IF EXISTS daily_budget_consumed(TEXT);")
    op.drop_index("idx_agent_budget_alerts_agent_scope_triggered", table_name="agent_budget_alerts")
    op.drop_table("agent_budget_alerts")
    op.drop_table("agent_budgets")
    op.drop_index("idx_agent_api_calls_task", table_name="agent_api_calls")
    op.drop_index("idx_agent_api_calls_agent_occurred", table_name="agent_api_calls")
    op.drop_index("idx_agent_api_calls_occurred", table_name="agent_api_calls")
    op.drop_table("agent_api_calls")
