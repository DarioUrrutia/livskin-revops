---
runbook: migration-failed-mid-deploy
severity: critical
auto_executable: false
trigger:
  - "alembic upgrade fail mid-execution"
  - "DB en estado inconsistente (parte de la migration aplicada, parte no)"
required_secrets:
  - DO_API_TOKEN
commands_diagnose:
  - "ssh livskin-erp 'docker compose -f /srv/livskin-revops/infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp current'"
  - "ssh livskin-erp 'docker compose -f /srv/livskin-revops/infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp history --verbose | head -40'"
  - "ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c \"\\\\d+\"'"
commands_fix:
  - "# Opción A: rollback DO snapshot (más seguro si snapshot reciente)"
  - "doctl compute droplet-action restore livskin-vps-erp --image-id <snapshot-id>"
  - "# Opción B: alembic downgrade a revision previa"
  - "ssh livskin-erp 'docker compose run --rm alembic-erp downgrade <prev_revision>'"
commands_verify:
  - "ssh livskin-erp 'docker compose run --rm alembic-erp current'  # debe mostrar versión coherente"
  - "ssh livskin-erp 'docker exec erp-flask pytest /app/tests/ --tb=short --no-cov -x'"
escalation:
  if_fail: "rebuild VPS 3 desde DR runbook (último recurso)"
related_skills:
  - livskin-ops
  - livskin-deploy
---

# Migration Alembic falló mid-deploy

## Síntomas
- Deploy CI/CD reporta error en step `alembic upgrade`
- DB en estado inconsistente (algunas tablas/columnas creadas, otras no)
- erp-flask falla al iniciar con SQLAlchemy errors sobre schema

**Esto es CRITICAL — la DB puede tener integridad rota.**

## Diagnóstico

```bash
# 1. Ver versión Alembic actual
ssh livskin-erp 'cd /srv/livskin-revops && docker compose -f infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp current'

# 2. Histórico de migrations
ssh livskin-erp 'cd /srv/livskin-revops && docker compose -f infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp history --verbose | head -40'

# 3. Schema actual de DB (¿coincide con migration?)
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "\\d"'

# 4. Logs del step que falló
gh run list --workflow=deploy-vps3.yml --limit 5
gh run view <run-id> --log
```

## Decision tree

```
¿Hay snapshot DO pre-deploy (<24h)?
├── SÍ → opción A (rollback DO snapshot) — RECOMENDADO
└── NO → opción B (alembic downgrade) — MÁS RIESGO
```

## Fix Opción A — Rollback DO snapshot

```bash
# 1. Listar snapshots recientes
doctl compute snapshot list --format ID,Name,CreatedAt | grep livskin-vps-erp-pre-deploy

# 2. Restore (DESTRUCTIVO, requiere autorización Dario)
doctl compute droplet-action restore <droplet-id> --image-id <snapshot-id> --wait
```

Esto deja el VPS exactamente como antes del deploy fallido.

## Fix Opción B — Alembic downgrade

```bash
# 1. Identificar revision previa (la que SÍ funcionaba)
ssh livskin-erp 'cd /srv/livskin-revops && docker compose -f infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp history --verbose | head -10'

# 2. Downgrade
ssh livskin-erp 'cd /srv/livskin-revops && docker compose -f infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp downgrade <prev_revision>'

# 3. Si downgrade está incompleto (a veces happen) → restaurar desde backup pg_dump
ssh livskin-erp 'gunzip -c /srv/backups/local/livskin_erp-<fecha>.sql.gz | docker exec -i postgres-data psql -U postgres livskin_erp'
```

## Verificación

```bash
# 1. Versión Alembic coherente
ssh livskin-erp 'docker compose -f /srv/livskin-revops/infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp current'

# 2. Tests pasan (verifica que el schema funciona)
ssh livskin-erp 'docker exec erp-flask pytest /app/tests/ --no-cov -x --tb=short'

# 3. Endpoint público responde
curl -sI https://erp.livskin.site/ping
```

## Escalación

Si NI rollback NI downgrade NI restore funcionan:
- Activar runbook [disaster-recovery-vps3](disaster-recovery-vps3.md)
- WhatsApp a Dario con context completo
- Mantener Render como fallback (sigue siendo prod hasta Fase 6)

## Por qué este runbook NO es auto_executable

`doctl compute droplet-action restore` es DESTRUCTIVO — pierde TODO lo
escrito al VPS desde el snapshot. Si entre el snapshot y ahora hubo
ventas reales, se pierden. **Siempre autorización Dario.**
