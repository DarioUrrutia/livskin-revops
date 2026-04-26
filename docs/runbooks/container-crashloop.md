---
runbook: container-crashloop
severity: high
auto_executable: false
trigger:
  - "container restart count >= 3 en 1 hora"
  - "evento infra.container_unhealthy del sensor"
required_secrets: []
commands_diagnose:
  - "ssh <vps> 'docker ps -a --format \"table {{.Names}}\\t{{.Status}}\\t{{.RestartCount}}\"'"
  - "ssh <vps> 'docker logs --tail=200 <container_name>'"
  - "ssh <vps> 'docker inspect <container_name> | jq .State'"
commands_fix:
  - "ssh <vps> 'docker compose -f <path>/docker-compose.yml up -d --force-recreate <service>'"
  - "(si OOM) ssh <vps> 'docker compose -f <path> down; docker compose up -d' con limites de memoria"
commands_verify:
  - "ssh <vps> 'docker ps --format \"{{.Names}} {{.Status}}\"' | grep <container>"
escalation:
  if_fail: "git log → identificar último deploy → considerar rollback DO snapshot"
related_skills:
  - livskin-ops
---

# Container en crashloop

## Síntomas
- Sensor reporta `container.restart_count >= 3` en 1 hora
- Container marcado "Restarting" en `docker ps`
- Endpoints público devuelven 502/503

## Diagnóstico

```bash
# 1. Identificar el container
ssh livskin-erp 'docker ps -a --format "table {{.Names}}\t{{.Status}}"'

# 2. Ver últimos logs
ssh livskin-erp 'docker logs --tail=200 erp-flask 2>&1'

# 3. Ver estado detallado (exit code, OOM, etc.)
ssh livskin-erp 'docker inspect erp-flask | jq .State'

# 4. Ver eventos recientes de docker
ssh livskin-erp 'docker events --since 1h --until now --filter container=erp-flask'
```

## Causas comunes y fixes

### A. OOM (Out Of Memory)
Síntoma: `OOMKilled: true` en `docker inspect .State`

```bash
# 1. Ver memoria actual del VPS
ssh livskin-erp 'free -h'

# 2. Si hay margen → agregar límite de memoria al compose
# Editar el docker-compose.yml del servicio:
#   deploy:
#     resources:
#       limits:
#         memory: 512M
# Y restart:
ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/erp-flask && docker compose up -d'

# 3. Si el VPS no tiene margen → resize en DO panel
```

### B. App crash al startup (ej: env var faltante)
Síntoma: logs muestran traceback Python o "missing variable"

```bash
# 1. Identificar la variable faltante en logs
ssh livskin-erp 'docker logs erp-flask 2>&1 | tail -50'

# 2. Verificar .env del servicio
ssh livskin-erp 'cat /srv/livskin-revops/infra/docker/erp-flask/.env'

# 3. Si falta → agregar y restart
ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/erp-flask && docker compose up -d --force-recreate'
```

### C. Dependencia caída (ej: erp-flask depende de postgres-data)
Síntoma: app log muestra "could not connect to server"

```bash
# 1. Verificar que el dependency está up
ssh livskin-erp 'docker ps | grep postgres-data'

# 2. Si no está → levantar primero
ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/postgres-data && docker compose up -d'

# 3. Esperar healthcheck y restart el dependiente
ssh livskin-erp 'docker compose -f /srv/livskin-revops/infra/docker/erp-flask/docker-compose.yml restart'
```

### D. Cambio reciente en código rompió algo
Síntoma: crashloop empezó después de un deploy

```bash
# 1. Identificar último deploy
ssh livskin-erp 'cd /srv/livskin-revops && git log --oneline -5'

# 2. Si es seguro rollback → revert + redeploy
ssh livskin-erp 'cd /srv/livskin-revops && git revert HEAD --no-edit && git push'

# 3. O si fue un deploy con snapshot DO → restore
# (ejecutar desde GHA o manualmente con doctl)
```

## Verificación

```bash
# Container está running >5 min sin restart
ssh livskin-erp 'docker ps --format "{{.Names}} {{.Status}}"' | grep erp-flask

# Endpoint público responde
curl -sI https://erp.livskin.site/ping
```

## Escalación

Si después de 30 min no se identifica la causa raíz:
- Considerar rollback DO snapshot (workflow GHA `deploy-vps3.yml` con
  `workflow_dispatch` y `skip_snapshot: false` puede triggerearlo)
- Pingear a Dario via WhatsApp con resumen
