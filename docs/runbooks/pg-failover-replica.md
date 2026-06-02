---
title: PG failover replica VPS2 (cuando VPS3 cae)
type: runbook
last_validated: 2026-05-28 (Sprint 1.5 DR drill)
cadence: trimestral (re-validar replica está streaming)
estimated_time: 15-30 min
prerequisites:
  - VPS3 inaccesible o postgres-data crashed
  - VPS2 + postgres-replica operacional
---

# Runbook — Failover Postgres VPS3 → VPS2 replica

> Replica streaming desde Sprint 1.4 (2026-05-28). Failover MANUAL — requiere
> intervención humana para promote. NO hay auto-failover (intencional: evita
> split-brain en transient network issues VPC).

---

## Pre-flight check (siempre antes de touch)

```bash
# 1. Confirmar primary realmente down (no es solo network glitch)
ssh livskin-erp 'sudo docker ps -a --filter name=postgres-data'
ssh livskin-erp 'curl -s -o /dev/null -w "%{http_code}\n" https://erp.livskin.site/login'  # debería fallar

# 2. Confirmar replica está streaming hasta donde podía
ssh livskin-ops 'sudo docker exec postgres-replica psql -U postgres -t -A -c "SELECT pg_last_wal_replay_lsn(), pg_last_xact_replay_timestamp();"'

# 3. Tomar nota del último LSN del replica — es el punto de truncamiento
```

---

## Failover (promote replica como nuevo primary)

### Paso 1: Promote replica

```bash
ssh livskin-ops 'sudo docker exec postgres-replica psql -U postgres -c "SELECT pg_promote();"'
# Returns: t (boolean true) si exito

# Verificar que ya no está en recovery:
ssh livskin-ops 'sudo docker exec postgres-replica psql -U postgres -t -A -c "SELECT pg_is_in_recovery();"'
# Debe retornar: f (false)
```

### Paso 2: Reconfigurar erp-flask para apuntar al nuevo primary (VPS2:5433)

```bash
# Edit /srv/livskin-revops/infra/docker/erp-flask/docker-compose.yml en VPS3:
#   environment:
#     ERP_DB_HOST: 10.114.0.2  # (era: postgres-data)
#     ERP_DB_PORT: 5433        # (era default 5432)

ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/erp-flask && sudo docker compose up -d --force-recreate'

# Verificar:
curl -s -o /dev/null -w "%{http_code}\n" https://erp.livskin.site/login  # debe ser 200
```

### Paso 3: Reconfigurar consumers internos (n8n, embeddings-service)

n8n credentials Postgres apuntan via revops_net `postgres-data:5432`. Cambiar host
a 10.114.0.2:5433 desde n8n UI o via export/import:credentials con --decrypted.

embeddings-service usa misma DB — actualizar env via compose.

### Paso 4: Notificar audit_log

```bash
ssh livskin-erp 'TOKEN=$(sudo cat /srv/livskin-revops/keys/.audit-internal-token) && curl -X POST https://erp.livskin.site/api/internal/audit-event \
  -H "X-Internal-Token: $TOKEN" \
  -d "{\"action\":\"infra.failover_executed\",\"entity_type\":\"postgres\",\"entity_id\":\"vps3_to_vps2\",\"metadata\":{\"reason\":\"vps3_down\",\"new_primary\":\"vps2:5433\"}}"'
```

---

## Restoring primary (post-incident, cuando VPS3 vuelve)

**ATENCIÓN**: NO simplemente reiniciar postgres-data en VPS3 — eso dispara
split-brain (2 primaries con divergent writes). Hay que:

1. Decidir si volver a topology original (VPS3 primary + VPS2 replica) o promote
   replica como permanent primary
2. Si volver al original: re-sync VPS3 desde VPS2 (treat VPS3 as new replica)
3. Re-create replication slot + basebackup
4. Switch back consumers

Procedimiento detallado pendiente — escribir cuando ocurra primer incidente real.

---

## Re-validación trimestral (cadencia)

Sin downtime real:
```bash
# 1. Write marker en primary
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "CREATE TABLE IF NOT EXISTS dr_drill_test (id SERIAL PRIMARY KEY, marker TEXT, captured_at TIMESTAMPTZ DEFAULT NOW()); INSERT INTO dr_drill_test (marker) VALUES (CONCAT(\"drill_\", NOW()));"'

# 2. Wait 5 sec for replication

# 3. Read in replica
ssh livskin-ops 'sudo docker exec postgres-replica psql -U postgres -d livskin_erp -t -A -c "SELECT marker FROM dr_drill_test ORDER BY id DESC LIMIT 1;"'

# 4. Cleanup
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "DROP TABLE dr_drill_test;"'

# 5. Verify replication lag
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -t -A -c "SELECT application_name, client_addr, state, replay_lag FROM pg_stat_replication;"'
```

Update `last_validated` en el frontmatter de este runbook + commit.
