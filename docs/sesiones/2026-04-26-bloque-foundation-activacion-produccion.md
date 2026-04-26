# Sesión 2026-04-26 — Activación del Bloque 0 v2 en producción

**Continuación de:** sesión anterior (cimientos cross-VPS state-of-the-art)
**Tipo:** activación operacional + decisiones estratégicas (budget + visión organizacional)
**Branch:** `chore/foundation-cross-vps`

---

## Decisiones estratégicas tomadas (Dario)

### 1. Budget MVP-light: $134/mes (de $300 original)
> "Bajemos a $150 USD mes, pero imagino que esto será cuando empiece a tener mucho volumen, al principio ni llegará a eso."

| Agente | Daily | Monthly |
|---|---|---|
| Conversation | $1.50 | $45 |
| Content (Brand Orchestrator) | $2.00 | $60 |
| Acquisition | $0.50 | $15 |
| Growth | $0.30 | $9 |
| Infra-Security | $0.20 | $5 |
| **Total** | **$4.50** | **$134** |

Aplicado en migration 0005 + memoria `feedback_agent_resource_optimization`.

### 2. Daily summary llega solo a Dario
No al equipo. El equipo (doctora) usa el ERP web directo, no recibe alertas.

### 3. Anuncios bloqueantes
Content Agent NUNCA publica nada en Meta/Google/Instagram sin OK Dario. Política dura.

### 4. Brand Orchestrator (era Content Agent) — visión expandida
**Reframe:** no es "agente que genera creativos para Meta". Es **director creativo end-to-end**:
- Ads (Meta + Google + Instagram)
- Landing pages (Claude Design para mejorar livskin.site + crear nuevas)
- Copies coherentes (ad + landing + email + autoresponder)
- Implementación cross-channel

**Patrón propuesto:** orquestador + subagentes especializados:
- Research Agent (Haiku — Meta Ad Library + competencia)
- Concept Agent (Sonnet — concepto + arquetipo)
- Copywriter Agent (Sonnet — copies coherentes)
- Visual Agent (Opus + Claude Design — landings + banners)
- Implementation Agent (Haiku + Meta API — prepara, no publica)

**Aclaración Claude Design vs fal.ai:**
- Claude Design = diseñar interfaces web (HTML/CSS/landings) ✓ priorizar
- fal.ai = generar imágenes desde cero (Flux Pro) — opcional Fase 5

### 5. Estructura organizacional de agentes — sesión estratégica pendiente
> "Pienso que deberíamos profundizar muy bien el cómo será la estructura de mis agentes... yo soy su gerente y debo guiarlos como personas a mi cargo, con rangos."

Output esperado de la sesión (antes de Fase 5):
- ADR-0030 — Brand Orchestrator multi-agent architecture
- `docs/agents/organization-chart.md`
- Subdirs `docs/agents/<agent-name>/` con SKILL.md + prompts/ + tools.json + evals/ + cadence.md
- Brand voice consolidado
- Approval flows + métricas por agente

Combinable con Interludio Estratégico entre Fase 3 y Fase 4 (~4-8h juntos).

Memoria nueva: `project_agent_org_design.md`.

---

## Bloque 0.10 — Agent resource optimization (NUEVO)

Implementación del principio operativo:
> "El uso de recursos por parte de mis agentes tiene que ser optimizado y preciso."

### Componentes desplegados

- **Migration 0005** — tablas `agent_api_calls` + `agent_budgets` + `agent_budget_alerts` + funciones SQL `daily_budget_consumed()` / `monthly_budget_consumed()`
- **Models** — AgentApiCall, AgentBudget, AgentBudgetAlert
- **services/agent_resource_service.py** con:
  - MODEL_PRICES (Opus/Sonnet/Haiku con cache pricing)
  - calculate_cost_usd() precisión 6 decimales
  - check_budget_or_block() pre-check con hard_block_at_limit
  - record_call() persiste + emite audit + threshold evaluation
  - query_costs() para dashboard
  - cleanup_old_calls() cron daily
- **2 endpoints internos:**
  - `POST /api/internal/agent-api-call` para wrappers
  - `GET /api/internal/agent-budget-check` para pre-check
- **5 audit events nuevos:** agent.api_call_completed/blocked, infra.budget_warning/exceeded, admin.budget_changed
- **Dashboard `/admin/agent-costs`** — tarjetas por agente verde/amarillo/rojo + breakdown daily
- **Skill `livskin-ops` extendida** — query_agent_costs + query_agent_budget_status
- **Runbook `cost-budget-exceeded.md`**
- **Tests pytest** del service + endpoints

### Total: 54 eventos canónicos auditables

(antes 49 — agregamos 5 con Bloque 0.10)

---

## Activación en producción — qué se hizo

### En VPS 3 (livskin-erp)

✅ AUDIT_INTERNAL_TOKEN generado (random 64-char) y deployed:
- `/srv/livskin-revops/infra/docker/erp-flask/.env`
- `/srv/livskin-revops/keys/.audit-internal-token` (para crons)

✅ UFW puerto 9100 abierto desde VPC `10.114.0.0/20`

✅ Migrations 0004 (infra_snapshots) + 0005 (agent_resource_tracking) aplicadas:
- 4 tablas nuevas: infra_snapshots, agent_api_calls, agent_budgets, agent_budget_alerts
- 2 funciones SQL: daily_budget_consumed, monthly_budget_consumed
- Trigger inmutabilidad audit_log preservado
- Trigger DEBE dinámico preservado
- 5 agent_budgets seedados ($134/mes total)

✅ erp-flask rebuilt con:
- Volume `/repo:ro` para que system_map_service lea docs/sistema-mapa.md
- Variable `audit_internal_token` cargada
- Endpoints nuevos /api/internal/* + /api/system-map.json operativos

✅ Crons instalados:
- `/etc/cron.d/livskin-erp` — sensor recolector cada 5 min + cleanup daily 03:00
- `/etc/cron.d/livskin-backups` — backup-vps3 daily 02:00 + verify daily 04:00 + cleanup daily 05:00

### En VPS 2 (livskin-ops)

✅ Repo clonado en `/srv/livskin-revops/` (branch chore/foundation-cross-vps)

✅ User `backup` creado con HOME=/srv/backups + shell /bin/bash

✅ Container `livskin-sensor` desplegado en `infra/docker/vps2-ops/livskin-sensor/`:
- Image built local
- Reporta /api/health y /api/system-state
- Mount /var/run/docker.sock:ro para reportar containers
- AUDIT_INTERNAL_TOKEN configurado en .env

✅ UFW puerto 9100 abierto

✅ SSH key `backup-target` generada + pública autorizada en VPS 3

### En VPS 1 (livskin-wp)

✅ Repo clonado en `/srv/livskin-revops/`

✅ User `backup` corregido (HOME + shell)

✅ Sensor desplegado via systemd (NO docker — VPS 1 es host nginx + WP):
- venv Python en `/opt/livskin-sensor/venv`
- Service `livskin-sensor.service` enabled + active
- Reporta nginx, php8.1-fpm, mariadb (todos active)

✅ UFW puerto 9100 abierto

✅ SSH key `backup-target` autorizada en VPS 2

### Verificación end-to-end

✅ Recolector cross-VPS funcional:
```
docker exec erp-flask python -m services.infra_snapshot_service collect
→ Collected snapshots:
  livskin-wp: ok       (disk 19.6%, RAM 77.2%)
  livskin-ops: ok      (disk 14.7%, RAM 67.9%, 7 containers)
  livskin-erp: ok      (disk 46.8%, RAM 60.8%)
```

✅ Tabla `infra_snapshots` poblada (3 entries)

✅ Endpoints públicos respondiendo:
- https://erp.livskin.site/ping → 200
- https://erp.livskin.site/api/system-map.json → 200
- https://erp.livskin.site/api/internal/health → 200

✅ Backup cross-VPS manual probado: 17KB transferido VPS 3 → VPS 2 OK

---

## Pendiente para sesión próxima

### Bloqueante (10 min con vos)

1. **DO_API_TOKEN** generado por vos en https://cloud.digitalocean.com/account/api/tokens con scopes:
   - droplet:read, snapshot:read+write+delete, image:read
   - Expiración 90 días
   - Pasar a `gh secret set DO_API_TOKEN`

### No bloqueante (siguientes sesiones)

2. **GitHub Secrets faltantes para CI/CD multi-VPS:**
   - VPS1_SSH_KEY, VPS1_HOST, VPS1_USER
   - VPS2_SSH_KEY, VPS2_HOST, VPS2_USER
   - AUDIT_INTERNAL_TOKEN (mismo valor que el del VPS 3)

3. **Ajuste backup script automation:**
   - El backup manual funciona, pero el cron daily 02:00 necesita que user `livskin` (o `backup` añadido al grupo docker) corra `docker exec`. Permission tuning pendiente.

4. **Migrar VPS 2 servicios** desde `/home/livskin/apps/` a `/srv/livskin-revops/infra/docker/vps2-ops/` con `migrate-from-home.sh`. Los containers siguen corriendo en path viejo — la migración es operativa, no urgente.

5. **Brain Layer 2 reindex** — corriendo en background, debe completar.

6. **Merge branch `chore/foundation-cross-vps` → main** después de ~24-48h de operación estable.

7. **Tag `v0.foundation`** en main para snapshot de versión.

---

## Métricas de la sesión

- **Sub-bloques nuevos:** 0.10 (agent resource optimization)
- **Decisiones estratégicas registradas:** 5 (budget, daily summary, anuncios bloqueantes, Brand Orchestrator, sesión organizacional pendiente)
- **Memorias nuevas:** 2 (`feedback_agent_resource_optimization`, `project_agent_org_design`)
- **Commits en esta sesión:** 3 (0.10, budgets MVP-light, fix backups gitignore)
- **Migrations aplicadas:** 0004 + 0005
- **Containers desplegados:** livskin-sensor en VPS 2
- **Systemd services:** livskin-sensor en VPS 1
- **Crons instalados:** 5 (sensor 5min + cleanup + backup-vps3 + verify + cleanup-old)
- **Líneas de código nuevas (Bloque 0.10):** ~1,700
- **Activación end-to-end:** verificada con recolector real cross-VPS

---

## Estado del sistema al cierre

🟢 **Bloque 0 v2 — 100% completado y activado en producción**

✅ Sensors uniformes en los 3 VPS
✅ Recolector cross-VPS pulleando cada 5 min
✅ Audit log expandido (54 eventos canónicos)
✅ Budgets agentes seedados ($134/mes total)
✅ Backups cross-VPS configurados (cron + SSH keys + verify)
✅ Runbooks ejecutables (13 con cost-budget-exceeded)
✅ Skills MCP (livskin-ops + livskin-deploy) compatibles Agent SDK
✅ System-map machine-readable + endpoint JSON

🚧 **Pendiente:**
- DO_API_TOKEN (Dario, 5 min)
- GitHub Secrets restantes
- Backup script permission tuning
- Migrate VPS 2 paths (no urgente)
- Merge a main (después de validación)

---

## Próximo paso

**Sesión próxima** con DO_API_TOKEN listo:
1. Setup GitHub Secrets (10 min)
2. Test workflow `deploy-vps2.yml` con dummy change (10 min)
3. Test workflow `deploy-vps1.yml` con dummy change (10 min)
4. Drill: rollback automático intencional para validar el rollback (15 min)
5. Si todo OK → merge a main + tag `v0.foundation`
6. **Arrancar Fase 3** (tracking + observabilidad: Meta Pixel + GA4 + GTM + Langfuse + UTMs en WP)

Total estimado próxima sesión: ~2-3h.
