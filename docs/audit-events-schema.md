---
type: audit-events-schema
version: 1.0
last_updated: 2026-04-26
authoritative: true
description: Schema completo de eventos auditables del sistema Livskin. Source of truth para audit_log queries por humanos y agentes IA.
---

# 📋 Audit Events Schema

## Filosofía

Cada evento que importa al negocio o a la operación queda persistido en
`postgres-data.audit_log` con schema estructurado. Esto permite:
- Auditoría legal (Ley 29733 PE)
- Forense de incidentes
- Detección de anomalías por agentes IA
- Reportes operacionales

## Estructura común de evento

```yaml
audit_log:
  id: BIGSERIAL PK
  occurred_at: TIMESTAMPTZ DEFAULT NOW()
  user_id: BIGINT FK → users.id (NULL para eventos sistema)
  user_username: TEXT (snapshot — sobrevive si el user se borra)
  user_role: TEXT
  action: TEXT NOT NULL              # <category>.<verb>
  category: TEXT NOT NULL            # auto-derivado de action
  entity_type: TEXT                  # ej: 'venta', 'user_session'
  entity_id: TEXT                    # ej: 'LIVTRAT0042'
  before_state: JSONB                # data antes (para updates)
  after_state: JSONB                 # data después
  ip: INET
  user_agent: TEXT
  session_id: BIGINT FK → user_sessions
  request_id: TEXT
  result: TEXT NOT NULL DEFAULT 'success'  # 'success' | 'failure'
  error_detail: TEXT
  metadata: JSONB                    # contexto extra específico del evento
```

**Inmutable:** trigger PL/pgSQL `audit_log_immutable()` rechaza UPDATE/DELETE
a nivel DB (migration 0003). Ni `postgres` superuser puede modificar entries.

## Categorías

| Category | # eventos | Origen |
|---|---|---|
| `auth.*` | 8 | erp-flask routes/auth.py + middleware |
| `venta.*` | 3 | erp-flask routes/legacy_forms.py + api_venta.py |
| `pago.*` | 3 | idem + api_pagos.py |
| `gasto.*` | 3 | idem + api_gasto.py |
| `cliente.*` | 3 | api_cliente.py |
| `lead.*` | 5 | n8n workflows (Fase 4+) |
| `admin.*` | 5 | admin actions (incluye `admin.budget_changed` Bloque 0.10) |
| `webhook.*` | 2 | n8n SureForms + WhatsApp |
| `infra.*` | 20 | CI/CD + crons + sensors (Bloque 0) — incluye `infra.budget_warning/exceeded` |
| `agent.*` | 2 | wrappers de agentes IA (Bloque 0.10) |

**Total: 54 eventos canónicos.**

## Catálogo completo por categoría

### auth.* (8) — Autenticación y sesiones

| Action | Cuándo | Metadata típica |
|---|---|---|
| `auth.login_success` | Login con credenciales válidas | `{first_login: bool}` |
| `auth.login_failed` | Username/password incorrecto | `{}` |
| `auth.lockout_triggered` | 8º intento fallido (lock 15 min) | `{}` |
| `auth.logout_voluntary` | Click en logout | `{}` |
| `auth.logout_inactivity` | >2h sin actividad | `{}` |
| `auth.logout_expired` | Sesión >48h | `{}` |
| `auth.password_changed` | Usuario cambió su password | `{}` |
| `auth.password_reset_by_admin` | Admin reseteó password de otro user | `{target_user_id: int}` |

### venta.* (3)

| Action | Cuándo | Metadata |
|---|---|---|
| `venta.created` | POST /venta exitoso | `{cliente, cod_items, items_count, credito_generado, abonos_deudas}` |
| `venta.updated` | UPDATE rare en MVP | `{}` (con before/after_state) |
| `venta.deleted` | Solo SQL admin | `{reason}` |

### pago.* (3)

| Action | Cuándo | Metadata |
|---|---|---|
| `pago.created` | POST /pagos | `{cliente, cod_items, fecha}` |
| `pago.updated` | Rare | `{}` |
| `pago.deleted` | Solo SQL admin | `{}` |

### gasto.* (3)

| Action | Cuándo | Metadata |
|---|---|---|
| `gasto.created` | POST /gasto | `{tipo, destinatario, monto}` |
| `gasto.updated` | Rare | `{}` |
| `gasto.deleted` | Rare | `{}` |

### cliente.* (3)

| Action | Cuándo | Metadata |
|---|---|---|
| `cliente.created` | Nuevo cliente registrado | `{}` |
| `cliente.updated` | Modificación datos | `{fields_changed}` (con before/after) |
| `cliente.merged` | Merge dedup (ADR-0013) | `{merged_into, merged_from}` |

### lead.* (5) — Fase 4+ (Conversation Agent)

| Action | Metadata |
|---|---|
| `lead.created` | `{fuente, utm_source, fbclid_present}` |
| `lead.score_updated` | `{old_score, new_score, factors}` |
| `lead.handoff_to_doctora` | `{score, reason}` |
| `lead.converted` | `{cliente_id, venta_id}` |
| `lead.discarded` | `{reason}` |

### admin.* (4)

| Action | Metadata |
|---|---|
| `admin.user_created` | `{username, rol}` |
| `admin.user_deactivated` | `{target_user_id, reason}` |
| `admin.config_changed` | `{config_key, before, after}` |
| `admin.dedup_resolved` | `{candidate_id, action}` |

### webhook.* (2)

| Action | Metadata |
|---|---|
| `webhook.form_submit_received` | `{source, has_consent, has_utm}` |
| `webhook.whatsapp_received` | `{from_phone, message_type}` |

### infra.* (18) — Bloque 0 nuevos

| Action | Origen | Metadata |
|---|---|---|
| `infra.deploy_started` | GHA workflow | `{vps, sha, actor}` |
| `infra.deploy_completed` | GHA workflow | `{vps, sha, actor, outcome, duration_s}` |
| `infra.deploy_failed` | GHA workflow | `{vps, sha, step_failed, error}` |
| `infra.deploy_rolled_back` | GHA workflow rollback | `{vps, snapshot_id, original_sha}` |
| `infra.snapshot_created` | doctl pre-deploy | `{vps, snapshot_id}` |
| `infra.snapshot_restored` | DR rollback | `{vps, snapshot_id}` |
| `infra.backup_started` | cron backup-vpsX.sh | `{vps, source}` |
| `infra.backup_completed` | cron backup-vpsX.sh | `{vps, files: [str]}` |
| `infra.backup_verified` | cron verify-backup.sh | `{engine, db, summary: {tables: int}}` |
| `infra.backup_failed` | backup script error | `{vps, reason}` |
| `infra.cert_renewed` | certbot renew (VPS 1) | `{domain, valid_until}` |
| `infra.cert_warning` | sensor detect <14d expiry | `{domain, days_until_expiry}` |
| `infra.healthcheck_red` | sensor monitor | `{vps, container, reason}` |
| `infra.disk_warning` | sensor disk_pct >= 85 | `{vps, disk_pct, used_gb, total_gb}` |
| `infra.ram_warning` | sensor ram_pct >= 90 | `{vps, ram_pct}` |
| `infra.container_unhealthy` | sensor restart_count >= 3 | `{vps, container, restart_count}` |
| `infra.dr_drill_completed` | DR drill post-mortem | `{runbook, duration_min, success: bool, gaps_found: [str]}` |
| `infra.credential_rotated` | post credential-leaked | `{credential_type, reason}` |
| `infra.budget_warning` | agente alcanzó alert_threshold (default 80%) | `{scope: 'daily'\|'monthly', usd_consumed, usd_limit, pct}` |
| `infra.budget_exceeded` | agente superó hard limit | `{scope, usd_consumed, usd_limit, pct}` |

### agent.* (2) — Bloque 0.10 uso de recursos LLM API

| Action | Cuándo | Metadata |
|---|---|---|
| `agent.api_call_completed` | call individual a Claude API persistido | `{agent, model, tokens, cost_usd, outcome}` |
| `agent.api_call_blocked` | llamada bloqueada por budget hard-limit | `{agent, reason, would_have_cost}` |

## Queries comunes (machine-readable para agentes IA)

```yaml
common_queries:
  - description: "¿Cuándo fue el último deploy exitoso a VPS 3?"
    sql: |
      SELECT occurred_at, user_username, audit_metadata
      FROM audit_log
      WHERE action = 'infra.deploy_completed'
        AND audit_metadata->>'vps' = 'vps3'
        AND result = 'success'
      ORDER BY occurred_at DESC LIMIT 1;

  - description: "¿Hay deploys fallidos esta semana?"
    sql: |
      SELECT occurred_at, audit_metadata->>'vps' as vps, error_detail
      FROM audit_log
      WHERE action IN ('infra.deploy_failed', 'infra.deploy_rolled_back')
        AND occurred_at > NOW() - INTERVAL '7 days'
      ORDER BY occurred_at DESC;

  - description: "¿Backups verificados en las últimas 24h por VPS?"
    sql: |
      SELECT
        audit_metadata->>'engine' as engine,
        audit_metadata->>'db' as db,
        max(occurred_at) as last_verified
      FROM audit_log
      WHERE action = 'infra.backup_verified'
        AND occurred_at > NOW() - INTERVAL '24 hours'
      GROUP BY 1, 2;

  - description: "¿Quién logueó hoy?"
    sql: |
      SELECT user_username, ip, count(*) as logins, max(occurred_at) as last_login
      FROM audit_log
      WHERE action = 'auth.login_success'
        AND occurred_at::date = CURRENT_DATE
      GROUP BY 1, 2
      ORDER BY 4 DESC;

  - description: "¿Hubo intentos de acceso fallidos sospechosos?"
    sql: |
      SELECT user_username, ip, count(*) as fails, max(occurred_at) as last
      FROM audit_log
      WHERE action IN ('auth.login_failed', 'auth.lockout_triggered')
        AND occurred_at > NOW() - INTERVAL '24 hours'
      GROUP BY 1, 2
      HAVING count(*) >= 3
      ORDER BY 3 DESC;

  - description: "¿Qué snapshots DO tenemos disponibles?"
    sql: |
      SELECT audit_metadata->>'vps' as vps,
             audit_metadata->>'snapshot_id' as snapshot_id,
             occurred_at
      FROM audit_log
      WHERE action = 'infra.snapshot_created'
        AND occurred_at > NOW() - INTERVAL '7 days'
      ORDER BY 1, 3 DESC;
```

## Cómo agregar un nuevo tipo de evento

1. Decidir nombre `<category>.<verb_past_participle>` (ej: `lead.scored`)
2. Agregar a `KNOWN_ACTIONS` en `services/audit_service.py`
3. Agregar entry en este documento
4. Agregar query útil al catálogo "common_queries" si aplica
5. Si es para infra: actualizar el script/workflow que lo dispara
6. Bumpear `version` de este doc

## Retention policy

`audit_log` es **permanente** (no se autolimpia). Tradeoff:
- ✅ Histórico completo para forense + compliance
- ⚠️ Crecimiento DB ~ 1MB/100 eventos. A 10/min = 14k/día = 5M/año. Manejable.

Política de archivado (cuando volume sea problema en años):
- >2 años → mover a tabla `audit_log_archive` (mismo schema, sin trigger
  inmutabilidad)
- Comprimido + indexado solo por timestamp
- Restaurable bajo demanda
