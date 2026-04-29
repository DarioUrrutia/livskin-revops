"""0006 capi match quality — fbc/ga/event_id en leads + touchpoints + form_submissions

Revision ID: 0006_capi_match_quality
Revises: 0005_agent_resource_tracking
Create Date: 2026-04-29 22:00:00.000000+00:00

Agrega 9 columnas (3 por tabla) para soportar match quality CAPI:
- _fbc cookie (Facebook click cookie, distinto a fbclid URL param)
- _ga cookie (Google Analytics client ID)
- event_id (UUID generado en GTM para deduplicar CAPI client+server)

Razon: ADR-0011 v1.1 (escrito en abril) no anticipo estas 3 cookies/IDs.
La conversacion 2026-04-29 sobre CAPI match quality identifico que estos
3 identifiers son criticos para attribution Meta + Google y deben viajar
end-to-end form -> Vtiger -> ERP -> emision CAPI.

Ver memoria `project_capi_match_quality.md` y backlog Mini-bloque 3.4.

Migration 100% reversible: solo agrega columnas con default NULL, no toca
data existente. Downgrade simetrico drop_column de las 9 columnas + 3 indices.
"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_capi_match_quality"
down_revision: Union[str, None] = "0005_agent_resource_tracking"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # leads — first-touch capture (al crear el lead)
    op.add_column("leads", sa.Column("fbc_at_capture", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("ga_at_capture", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("event_id_at_capture", sa.String(), nullable=True))
    op.create_index("idx_leads_event_id_at_capture", "leads", ["event_id_at_capture"])

    # lead_touchpoints — snapshot por touchpoint
    op.add_column("lead_touchpoints", sa.Column("fbc", sa.String(), nullable=True))
    op.add_column("lead_touchpoints", sa.Column("ga", sa.String(), nullable=True))
    op.add_column("lead_touchpoints", sa.Column("event_id", sa.String(), nullable=True))
    op.create_index("idx_lead_touchpoints_event_id", "lead_touchpoints", ["event_id"])

    # form_submissions — raw audit
    op.add_column("form_submissions", sa.Column("fbc", sa.String(), nullable=True))
    op.add_column("form_submissions", sa.Column("ga", sa.String(), nullable=True))
    op.add_column("form_submissions", sa.Column("event_id", sa.String(), nullable=True))
    op.create_index("idx_form_submissions_event_id", "form_submissions", ["event_id"])


def downgrade() -> None:
    op.drop_index("idx_form_submissions_event_id", table_name="form_submissions")
    op.drop_column("form_submissions", "event_id")
    op.drop_column("form_submissions", "ga")
    op.drop_column("form_submissions", "fbc")

    op.drop_index("idx_lead_touchpoints_event_id", table_name="lead_touchpoints")
    op.drop_column("lead_touchpoints", "event_id")
    op.drop_column("lead_touchpoints", "ga")
    op.drop_column("lead_touchpoints", "fbc")

    op.drop_index("idx_leads_event_id_at_capture", table_name="leads")
    op.drop_column("leads", "event_id_at_capture")
    op.drop_column("leads", "ga_at_capture")
    op.drop_column("leads", "fbc_at_capture")
