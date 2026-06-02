---
title: Restore Postgres backup (livskin_erp / livskin_brain / analytics / metabase / n8n)
type: runbook
severity: critical
auto_executable: false
last_validated: 2026-06-02 (writing — pending real DR test)
estimated_time: 15-30 min per DB
prerequisites:
  - backup .sql.gz disponible en /srv/backups/local/ o /srv/backups/vps3/ o vps2/
  - postgres-data (VPS3) o postgres-analytics (VPS2) operacional
  - Acceso SSH livskin-erp / livskin-ops
---

# Runbook — Restore Postgres backup

> Procedimiento formal para restore de un PG dump (cualquier DB). Cubre los
> 5 databases backed up daily (livskin_erp + livskin_brain en VPS3, analytics
> + metabase + n8n en VPS2). Path crítico para DR scenarios.

---

## 1. Decidir scope

| DB | VPS | Container | Backup location |
|---|---|---|---|
| livskin_erp | VPS3 | postgres-data | /srv/backups/local/ + /srv/backups/vps2/vps3/ |
| livskin_brain | VPS3 | postgres-data | /srv/backups/local/ + /srv/backups/vps2/vps3/ |
| analytics | VPS2 | postgres-analytics | /srv/backups/local/ + /srv/backups/vps3/vps2/ |
| metabase | VPS2 | postgres-analytics | /srv/backups/local/ + /srv/backups/vps3/vps2/ |
| n8n | VPS2 | postgres-analytics | /srv/backups/local/ + /srv/backups/vps3/vps2/ |

---

## 2. Diagnóstico pre-restore

```bash
# A) Confirmar último backup integro
ssh livskin-erp 'ls -la /srv/backups/local/livskin_erp-*.sql.gz | tail -3'
# Verifica fecha, tamaño razonable (>500KB para livskin_erp típico)

# B) Verificar integridad del archivo (gzip OK + dump válido)
ssh livskin-erp 'gunzip -t /srv/backups/local/livskin_erp-YYYY-MM-DD.sql.gz && echo OK'

# C) Verificar PG container target activo
ssh livskin-erp 'sudo docker ps --filter name=postgres-data --format "table {{.Names}}\t{{.Status}}"'

# D) Identificar consumers activos que pueden bloquear restore
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -c "SELECT pid, usename, application_name, state FROM pg_stat_activity WHERE datname IN (\"livskin_erp\",\"livskin_brain\");"'
```

---

## 3. Restore — DB completa (in-place)

⚠️ **ATENCIÓN: esto SOBREESCRIBE la DB actual.** Si dudas, hacer dump del estado actual ANTES:

```bash
# Pre-restore backup del estado actual (safety net)
ssh livskin-erp 'sudo docker exec postgres-data pg_dump -U postgres livskin_erp | gzip > /srv/backups/local/livskin_erp-PRERESTORE-$(date +%Y%m%d-%H%M).sql.gz'
```

### Restore procedure (livskin_erp ejemplo)

```bash
# 1. Stop consumers (erp-flask + n8n que escriben a la DB)
ssh livskin-erp 'sudo docker stop erp-flask'
# Si tarda demasiado, n8n también puede pausarse:
ssh livskin-ops 'sudo docker stop n8n'

# 2. Drop + recreate DB (idempotency)
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -c "DROP DATABASE IF EXISTS livskin_erp;"'
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -c "CREATE DATABASE livskin_erp OWNER postgres ENCODING UTF8;"'

# 3. Restore desde dump
ssh livskin-erp 'gunzip -c /srv/backups/local/livskin_erp-YYYY-MM-DD.sql.gz | sudo docker exec -i postgres-data psql -U postgres -d livskin_erp'

# 4. Restart consumers
ssh livskin-erp 'sudo docker start erp-flask'
ssh livskin-ops 'sudo docker start n8n'  # si stopped
```

### Verificación post-restore

```bash
# A) Row counts en tablas principales
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -t -A -c "
SELECT \"clientes\" AS t, COUNT(*) FROM clientes
UNION ALL SELECT \"ventas\", COUNT(*) FROM ventas
UNION ALL SELECT \"pagos\", COUNT(*) FROM pagos
UNION ALL SELECT \"leads\", COUNT(*) FROM leads
UNION ALL SELECT \"audit_log\", COUNT(*) FROM audit_log;
"'
# Comparar contra el último estado conocido (CLAUDE.md o sistema-mapa)

# B) FK constraints válidas
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "
SELECT conname FROM pg_constraint WHERE contype = \"f\" AND NOT convalidated;
"'  # debe ser 0 rows

# C) Application smoke
curl -s -o /dev/null -w "ERP login %{http_code}\n" https://erp.livskin.site/login

# D) Audit log entry restore
TOKEN=$(ssh livskin-erp 'sudo cat /srv/livskin-revops/keys/.audit-internal-token')
curl -X POST https://erp.livskin.site/api/internal/audit-event \
  -H "X-Internal-Token: $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"action":"infra.restore_executed","entity_type":"livskin_erp","metadata":{"backup_date":"YYYY-MM-DD","operator":"dario","reason":"DR_test"}}'
```

---

## 4. Restore — point-in-time (con WAL streaming)

⚠️ Solo aplica si necesitas restore a un timestamp ENTRE backups. Requiere replica VPS2 (Sprint 1.4):

```bash
# Usar pg_promote() en replica para failover (ver pg-failover-replica.md)
# La replica ya tiene WAL streaming hasta el último LSN del primary
ssh livskin-ops 'sudo docker exec postgres-replica psql -U postgres -c "SELECT pg_promote();"'

# Verificar:
ssh livskin-ops 'sudo docker exec postgres-replica psql -U postgres -c "SELECT pg_is_in_recovery();"'  # → f (false)

# Reconfigurar erp-flask para apuntar a 10.114.0.2:5433
# Ver docs/runbooks/pg-failover-replica.md § Paso 2
```

---

## 5. Rollback si restore falla

```bash
# Si restore corrompe DB o queda en estado inconsistente:
# 1. Usar pre-restore backup (safety net del paso 3)
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -c "DROP DATABASE IF EXISTS livskin_erp;"'
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -c "CREATE DATABASE livskin_erp OWNER postgres ENCODING UTF8;"'
ssh livskin-erp 'gunzip -c /srv/backups/local/livskin_erp-PRERESTORE-*.sql.gz | sudo docker exec -i postgres-data psql -U postgres -d livskin_erp'

# 2. Restart consumers
ssh livskin-erp 'sudo docker start erp-flask'
```

---

## 6. Restore desde cross-VPS backup

Si /srv/backups/local/ en VPS origen no tiene el backup pero está en cross-VPS:

```bash
# Backup VPS3 (livskin_erp) → almacenado también en VPS2 /srv/backups/vps3/
# Backup VPS2 (analytics/n8n) → almacenado también en VPS3 /srv/backups/vps2/

# Si VPS3 down y necesitas restore desde VPS2:
ssh livskin-ops 'ls /srv/backups/vps3/livskin_erp-*.sql.gz | tail -3'

# Copiar a VPS3 (cuando esté UP) o usar VPS2 si VPS3 destroyed:
scp -F keys/ssh_config livskin-ops:/srv/backups/vps3/livskin_erp-YYYY-MM-DD.sql.gz /tmp/
scp -F keys/ssh_config /tmp/livskin_erp-YYYY-MM-DD.sql.gz livskin-erp:/tmp/
```

---

## 7. Cadencia validación (sin downtime real)

Cada 3 meses ejecutar DR drill:

```bash
# 1. Restore en DB de TEST (no producción)
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -c "CREATE DATABASE livskin_erp_drill_$(date +%Y%m%d);"'
ssh livskin-erp 'gunzip -c /srv/backups/local/livskin_erp-latest.sql.gz | sudo docker exec -i postgres-data psql -U postgres -d livskin_erp_drill_YYYYMMDD'

# 2. Validar counts coinciden con producción
# (queries del paso 4 verificación, comparar)

# 3. Drop DB drill
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -c "DROP DATABASE livskin_erp_drill_YYYYMMDD;"'

# 4. Update last_validated en este runbook
```

---

## 8. Casos especiales

### Caso: restore livskin_brain (segundo cerebro pgvector)

Mismo procedimiento que livskin_erp, pero después de restore ejecutar:
```bash
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_brain -c "CREATE EXTENSION IF NOT EXISTS vector;"'
```
Verificar `SELECT COUNT(*) FROM project_knowledge;` matches expectation.

### Caso: restore n8n DB

Stop n8n PRIMERO (encryption key conflicts si workflows mid-execution):
```bash
ssh livskin-ops 'sudo docker stop n8n'
# Restore...
ssh livskin-ops 'sudo docker start n8n'
# Verificar: docker exec n8n n8n list:workflow | wc -l (debe ser >0)
```

### Caso: restore después de migration

Si la DB tiene migraciones más nuevas que el backup, después de restore correr:
```bash
ssh livskin-erp 'sudo docker compose -f /srv/livskin-revops/infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp upgrade head'
```

---

## 9. Métricas + alerting (futuro)

**Backup health metrics actualmente disponibles:**
- audit_log entries `infra.backup_started` + `infra.backup_completed`
- `/srv/backups/local/` daily files (ls -la)

**Pendiente Sprint futuro:**
- Alerting Slack si backup_completed NO emitido en 26h (cron diaria espera <2h jitter)
- Dashboard Metabase con backup health (audit_log query)
- Cron weekly: ejecutar este runbook §7 DR drill automático sobre DB de test

---

**Status del runbook:** `draft` — pendiente primera ejecución real para validar.
