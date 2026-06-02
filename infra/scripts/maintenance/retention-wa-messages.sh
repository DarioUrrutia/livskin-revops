#!/bin/bash
# Retention wa_messages — purga mensajes WhatsApp > 365 dias.
#
# Sprint 1.6 (2026-05-28): wa_messages crece ~18k rows/año a escala actual
# (10 conv/dia x 5 msg). Aun lejos del threshold de partition (>1M rows),
# retention via DELETE es suficiente.
#
# Rationale 365d:
# - Compliance: 12 meses cubre lookbacks de marketing y reportes anuales
# - GDPR: si lead solicito borrado, F3 lo procesa antes (cross-system)
# - audit_log preserva (en otra tabla) las acciones tomadas sobre los mensajes
#
# Cron sugerido (/etc/cron.d/livskin-erp):
#   30 3 * * * livskin /srv/livskin-revops/infra/scripts/maintenance/retention-wa-messages.sh >> /var/log/livskin-cron/wa-messages-retention.log 2>&1

set -euo pipefail

ERP_BASE="${ERP_BASE:-https://erp.livskin.site}"
AUDIT_TOKEN="${AUDIT_INTERNAL_TOKEN:-$(sudo cat /srv/livskin-revops/keys/.audit-internal-token 2>/dev/null || echo "")}"
RETENTION_DAYS="${RETENTION_DAYS:-365}"

if [ -z "$AUDIT_TOKEN" ]; then
  echo "ERROR: AUDIT_INTERNAL_TOKEN no disponible" >&2
  exit 1
fi

DELETED_COUNT=$(sudo docker exec postgres-data psql -U postgres -d livskin_erp -tA -c \
  "WITH deleted AS (DELETE FROM wa_messages WHERE sent_at < NOW() - INTERVAL '${RETENTION_DAYS} days' RETURNING id) SELECT COUNT(*) FROM deleted;")

sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "VACUUM ANALYZE wa_messages;" > /dev/null 2>&1

curl -sS -X POST "$ERP_BASE/api/internal/audit-event" \
  -H "X-Internal-Token: $AUDIT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"action\":\"wa.messages_retention_executed\",\"entity_type\":\"wa_messages\",\"entity_id\":\"retention_${RETENTION_DAYS}d\",\"metadata\":{\"deleted_count\":${DELETED_COUNT:-0},\"retention_days\":${RETENTION_DAYS},\"executed_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}}" > /dev/null

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Retention wa_messages: deleted=${DELETED_COUNT:-0} rows older than ${RETENTION_DAYS}d"
