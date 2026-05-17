"""0008 wa_conversation_state + wa_messages — bot-broker bidireccional Fase 4A.3

Revision ID: 0008_wa_conversation
Revises: 0007_appointments
Create Date: 2026-05-16 19:30:00.000000+00:00

Crea 2 tablas para el chatbot WhatsApp como bot-broker bidireccional entre
leads y doctora (memoria `project_chatbot_broker_architecture.md`).

Tabla `wa_conversation_state`:
  Estado por phone_lead (UNIQUE). Una row activa por número que escribe al
  bot. Cuando la conversación termina (state='closed'), la row queda en DB
  para consulta historica pero ya no es la "activa" (queries deben filtrar
  por state).

  8 estados validos:
    - new            cliente acabó de escribir por 1ra vez, sin trato aún
    - qualifying     bot está pidiendo info (tratamiento de interes, urgencia)
    - waiting_doctora  lead propuso fecha, bot esperando respuesta de doctora
    - waiting_lead     doctora propuso alternativa, bot espera respuesta lead
    - negotiating    lead y doctora en loop de propuestas
    - confirmed      acuerdo cerrado, appointment creado
    - escalated      bot pasó la conversacion a humano (Dario o doctora)
    - closed         conversacion terminada (cita ocurrida, lead silencio 24h, cancelada)

Tabla `wa_messages`:
  Historial inmutable de cada mensaje inbound u outbound. `meta_message_id
  UNIQUE` es defensa contra re-entregas Meta (Meta puede reenviar el mismo
  mensaje si nuestro webhook tarda >5s o falla). Insertar el mismo id dos
  veces falla con conflict y el segundo procesamiento se descarta.

Migration 100% reversible. Downgrade hace DROP simple en orden inverso.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_wa_conversation"
down_revision: Union[str, None] = "0007_appointments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ────────────────────────────────────────────────────────────────────
    # Tabla wa_conversation_state
    # ────────────────────────────────────────────────────────────────────
    op.create_table(
        "wa_conversation_state",
        sa.Column("id", sa.BigInteger(), nullable=False),

        # Identificación
        sa.Column("phone_lead", sa.String(), nullable=False),
        sa.Column("phone_doctora", sa.String(), nullable=True),

        # Estado del flujo
        sa.Column("state", sa.String(), nullable=False, server_default="new"),
        sa.Column("last_intent", sa.String(), nullable=True),

        # Contexto del intercambio
        sa.Column("proposed_dates", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("doctora_response", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("context_json", sa.dialects.postgresql.JSONB(), nullable=True),

        # Últimos mensajes (snapshot para queries rápidos sin join a wa_messages)
        sa.Column("last_inbound_text", sa.Text(), nullable=True),
        sa.Column("last_inbound_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_outbound_text", sa.Text(), nullable=True),
        sa.Column("last_outbound_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("message_count_inbound", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("message_count_outbound", sa.Integer(), nullable=False, server_default="0"),

        # Output: appointment cuando confirma
        sa.Column("cod_appointment", sa.String(), nullable=True),
        sa.Column("appointment_created_at", sa.DateTime(timezone=True), nullable=True),

        # Cross-references (cuando lead se identifica via match by phone)
        sa.Column("lead_id", sa.BigInteger(), nullable=True),
        sa.Column("vtiger_lead_id", sa.String(), nullable=True),

        # Escalation
        sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("escalation_reason", sa.String(), nullable=True),
        sa.Column("escalation_to", sa.String(), nullable=True),  # 'doctora', 'dario'

        # Lifecycle timestamps
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("close_reason", sa.String(), nullable=True),  # 'cita_confirmada', 'lead_silencio_24h', 'lead_cancelo', etc.

        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        # UNIQUE phone_lead partial: solo una conv ACTIVA per phone (cerradas pueden coexistir si historicamente)
        # Indice partial DDL no se puede declarar como UniqueConstraint, se crea como op.execute abajo
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], name="fk_wa_conv_lead_id"),
        sa.ForeignKeyConstraint(["cod_appointment"], ["appointments.cod_appointment"], name="fk_wa_conv_cod_appointment"),
        sa.CheckConstraint(
            "state IN ('new', 'qualifying', 'waiting_doctora', 'waiting_lead', 'negotiating', 'confirmed', 'escalated', 'closed')",
            name="ck_wa_conv_state_valido",
        ),
        sa.CheckConstraint(
            "escalation_to IS NULL OR escalation_to IN ('doctora', 'dario')",
            name="ck_wa_conv_escalation_to_valido",
        ),
    )

    # Partial unique index: solo una conv ACTIVA (state != 'closed') per phone_lead
    op.execute(
        "CREATE UNIQUE INDEX uq_wa_conv_active_phone ON wa_conversation_state(phone_lead) WHERE state != 'closed'"
    )

    # Indices para queries comunes
    op.create_index("idx_wa_conv_phone_lead", "wa_conversation_state", ["phone_lead"])
    op.create_index("idx_wa_conv_state", "wa_conversation_state", ["state"])
    op.create_index(
        "idx_wa_conv_lead_id",
        "wa_conversation_state",
        ["lead_id"],
        postgresql_where=sa.text("lead_id IS NOT NULL"),
    )
    op.create_index("idx_wa_conv_state_updated", "wa_conversation_state", ["state", "updated_at"])
    op.create_index(
        "idx_wa_conv_last_inbound",
        "wa_conversation_state",
        ["last_inbound_at"],
        postgresql_where=sa.text("last_inbound_at IS NOT NULL"),
    )

    # ────────────────────────────────────────────────────────────────────
    # Tabla wa_messages — historial inmutable con idempotency
    # ────────────────────────────────────────────────────────────────────
    op.create_table(
        "wa_messages",
        sa.Column("id", sa.BigInteger(), nullable=False),

        # Identificación
        sa.Column("conversation_id", sa.BigInteger(), nullable=False),
        sa.Column("meta_message_id", sa.String(), nullable=True),  # UNIQUE — defensa reentrega Meta
        sa.Column("phone_lead", sa.String(), nullable=False),

        # Direction + content
        sa.Column("direction", sa.String(), nullable=False),  # 'inbound' o 'outbound'
        sa.Column("message_type", sa.String(), nullable=False),  # 'text', 'template', 'image', 'document', 'audio', etc.
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("template_name", sa.String(), nullable=True),  # solo si type=template
        sa.Column("template_params", sa.dialects.postgresql.JSONB(), nullable=True),

        # Meta enriquecida
        sa.Column("meta_status", sa.String(), nullable=True),  # 'sent', 'delivered', 'read', 'failed' (outbound)
        sa.Column("meta_status_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_error_code", sa.String(), nullable=True),
        sa.Column("meta_error_message", sa.Text(), nullable=True),

        # Intent detectado (inbound) o categoria del envío (outbound)
        sa.Column("intent", sa.String(), nullable=True),
        sa.Column("parsed_dates", sa.dialects.postgresql.JSONB(), nullable=True),  # fechas extraídas por parser regex

        # Raw payload completo de Meta (debug + futura migracion)
        sa.Column("meta_payload_raw", sa.dialects.postgresql.JSONB(), nullable=True),

        # Timestamps
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),  # cuando se envio o se recibio
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meta_message_id", name="uq_wa_messages_meta_message_id"),
        sa.ForeignKeyConstraint(["conversation_id"], ["wa_conversation_state.id"], name="fk_wa_messages_conversation_id"),
        sa.CheckConstraint(
            "direction IN ('inbound', 'outbound')",
            name="ck_wa_messages_direction_valido",
        ),
        sa.CheckConstraint(
            "message_type IN ('text', 'template', 'image', 'document', 'audio', 'video', 'sticker', 'location', 'contacts', 'interactive', 'reaction', 'system', 'unknown')",
            name="ck_wa_messages_type_valido",
        ),
        sa.CheckConstraint(
            "meta_status IS NULL OR meta_status IN ('sent', 'delivered', 'read', 'failed', 'deleted')",
            name="ck_wa_messages_status_valido",
        ),
    )

    # Indices wa_messages
    op.create_index("idx_wa_messages_conv_sent", "wa_messages", ["conversation_id", "sent_at"])
    op.create_index("idx_wa_messages_phone_sent", "wa_messages", ["phone_lead", "sent_at"])
    op.create_index("idx_wa_messages_direction_sent", "wa_messages", ["direction", "sent_at"])
    op.create_index(
        "idx_wa_messages_meta_status",
        "wa_messages",
        ["meta_status"],
        postgresql_where=sa.text("meta_status IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_wa_messages_meta_status", table_name="wa_messages")
    op.drop_index("idx_wa_messages_direction_sent", table_name="wa_messages")
    op.drop_index("idx_wa_messages_phone_sent", table_name="wa_messages")
    op.drop_index("idx_wa_messages_conv_sent", table_name="wa_messages")
    op.drop_table("wa_messages")

    op.drop_index("idx_wa_conv_last_inbound", table_name="wa_conversation_state")
    op.drop_index("idx_wa_conv_state_updated", table_name="wa_conversation_state")
    op.drop_index("idx_wa_conv_lead_id", table_name="wa_conversation_state")
    op.drop_index("idx_wa_conv_state", table_name="wa_conversation_state")
    op.drop_index("idx_wa_conv_phone_lead", table_name="wa_conversation_state")
    op.execute("DROP INDEX IF EXISTS uq_wa_conv_active_phone")
    op.drop_table("wa_conversation_state")
