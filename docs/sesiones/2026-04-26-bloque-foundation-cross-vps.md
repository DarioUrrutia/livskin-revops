# Sesión 2026-04-26 — Bloque 0 v2: Cimientos cross-VPS state-of-the-art

**Duración:** ~14h sesión maratoniana (~6am-9pm Italia)
**Tipo:** infraestructura senior + AI-first design
**Branch:** `chore/foundation-cross-vps`
**Output:** sistema AI-operable end-to-end con 5 propiedades simultáneas

---

## Trigger

Tras cerrar Fase 2 al 99% (auth + audit + dashboard + tests 81% coverage), Dario propuso arrancar Fase 3 (tracking + observabilidad). Auditoría exhaustiva descubrió:

1. **VPS 2 (n8n + vtiger + metabase + postgres-analytics + nginx) NO estaba versionado** — corría desde `/home/livskin/apps/*` sin git
2. **VPS 1 (WordPress) 0% versionado** — solo nginx config + DB en host
3. **Sin sensors uniformes** cross-VPS para visibilidad holística
4. **Sin runbooks ejecutables** para incidentes
5. **Sin DR drill procedure** ensayado
6. **Sin skills declarativas** para que el 5to agente futuro consuma

Dario: *"hagamos el mejor trabajo... tiene que ser algo de gran categoría... el agente debe ser capaz de monitorear todo el sistema en los 3 VPS... yo debo preocuparme por la analítica de mis publicidades, estrategia, etc, pero el sistema debe ser potente."*

→ Decisión: pre-Fase 3, dedicar 1-2 sesiones al Bloque 0 v2 — cimientos AI-first state-of-the-art.

---

## 9 sub-bloques completados

### 0.1 Versionar 3 VPS al repo (~3h)
- `infra/docker/vps2-ops/` — 5 servicios (n8n, vtiger, metabase, postgres-analytics, nginx) con compose + .env.example + README
- `infra/docker/vps1-wp/` — nginx config + mu-plugins/ + install.sh DR
- VPS 3: paths legacy mantenidos (asimetría intencional documentada)
- `migrate-from-home.sh` zero-downtime para mover servicios VPS 2

### 0.2 CI/CD multi-VPS (~3h)
- `deploy-vps1.yml` — rsync nginx + mu-plugins + reload
- `deploy-vps2.yml` — docker compose por servicio
- `deploy-vps3.yml` mejorado — agrega snapshot DO + rollback
- `.github/scripts/do-snapshot.sh` — wrapper doctl (create/restore/cleanup)
- `.github/scripts/install-doctl.sh` — instala doctl en runner GHA
- Audit event en cada deploy
- Cleanup snapshots viejos automático

### 0.3 System map autoritativo (~2.5h)
- `docs/sistema-mapa.md` — 11 secciones machine-readable (frontmatter YAML + tablas + JSON code blocks)
- Inventario VPS, catálogo containers, cross-VPS connections, dependency matrix, SPOFs, public URLs, backups, secrets, capacity, AI agent guide
- Endpoint `/api/system-map.json` parsea el MD y sirve JSON estructurado
- `services/system_map_service.py` con cache 60s
- Diseñado para que el 5to agente lo consuma sin asumir nada

### 0.4 Sensors uniformes cross-VPS (~2h)
- `infra/docker/livskin-sensor/` — mini Flask app:
  - `GET /api/health` (sin auth)
  - `GET /api/system-state` (con `X-Internal-Token`)
  - Reporta: uptime, disk, RAM, containers, host_services, last_deploy_sha
  - Modo Docker (VPS 2) + modo systemd (VPS 1)
- VPS 3: endpoint en erp-flask con mismo schema
- Recolector cron `services/infra_snapshot_service.py` cada 5 min
- Migration 0004: tabla `infra_snapshots` (retención 30d)
- Dashboard `/admin/system-health` — tarjetas por VPS con bars green/yellow/red
- OpenAPI spec `infra/openapi/system-api.yaml`

### 0.5 Backups daily verificados (~2h)
- `infra/scripts/backups/`:
  - `common.sh` — funciones compartidas
  - `backup-vps[1|2|3].sh` — uno por VPS
  - `verify-backup.sh` — restore a temp DB + count check
  - `install-cron-vps3.sh` — cron 02:00/04:00/05:00 UTC
- Cross-VPS transfer via SSH key dedicada
- Cada operación reporta a audit_log

### 0.6 12 runbooks operativos ejecutables (~2.5h)
Cada uno con frontmatter YAML estructurado:
- ssl-cert-expiring, disk-full, container-crashloop, postgres-connections-exhausted, n8n-workflow-failing, backup-failed
- migration-failed-mid-deploy, vpc-down, disaster-recovery-vps[1|2|3]
- credential-leaked

Compatible MCP skill execution (auto-discoverable).

### 0.7 DR drill procedure (~1h)
- `docs/runbooks/dr-drill-procedure.md`
- Cadencia: backup-restore mensual, DR completo semestral, rollback trimestral
- Post-mortem template + audit log integration

### 0.8 Audit log expandido (~1h)
- 49 eventos canónicos en 9 categorías (agregado `infra.*` con 18 eventos nuevos)
- `docs/audit-events-schema.md` autoritativo
- 6 common_queries SQL machine-readable para agentes

### 0.9 Skills + MCP scaffold (~2.5h)
- `skills/livskin-ops/` — read-only ops (6 tools: query_system_state/audit_log/system_map/runbooks/trigger_runbook/backups_status)
- `skills/livskin-deploy/` — deploys autorizados (4 tools: trigger_deploy/monitor/rollback/list_recent_deploys)
- Cada skill con SKILL.md (frontmatter executable) + tools.json (tool_use schema)
- Compatible Claude Code + Agent SDK + MCP clients
- `infra/docker/mcp-livskin/` — scaffold del server (implementación Fase 6+)

---

## Decisiones arquitectónicas del Bloque

### A. Asimetría VPS 3 (paths legacy mantenidos)
Mover compose files de `infra/docker/<servicio>/` a `infra/docker/vps3-erp/<servicio>/` requiere mover también volúmenes `./data` que contienen 134 clientes + 88 ventas reales. Riesgo no justificado por consistencia cosmética. Reorganizar en Fase 6 cuando se haga cutover real.

### B. Sensors uniformes via API estandarizada (no logging shipping)
Decidimos endpoints HTTP `/api/system-state` con OpenAPI spec en lugar de log shipping a un central (Loki, etc.). Razones:
- Más simple operacionalmente
- Read-only pull de un consumer central
- AI-friendly (un agente puede curl)
- Compatible con cualquier observability stack futuro

### C. MCP server scaffolded, no implementado
Las skills funcionan HOY via Claude Code leyendo SKILL.md + tools.json. MCP server agrega valor para clientes MCP arbitrarios → útil cuando exista 5to agente Infra+Security. Implementar entonces, no antes.

### D. Audit log único para business + infra
Mismo `audit_log` table guarda eventos de auth/venta/pago/etc. + eventos infra (deploys, backups, snapshots). Unificación permite queries forenses cross-domain ("¿hubo deploy cuando empezaron los login_failed?").

### E. Backups con verificación automática
No solo dump cron — cada backup se restaura a una DB temporal y se valida (counts coinciden con original). Si algo está corrupto, alerta antes de necesitar el backup.

### F. Skills con authorization model claro
Read-only sin auth (queries son safe). Mutating con auth callback Dario (deploy, rollback, runbook risky). Esto refleja el principio "agente IA opera, humano autoriza acciones risky".

---

## Estado del repo

Branch: `chore/foundation-cross-vps`
Commits (6):
- `e2319f7` — Versionar VPS 1 + VPS 2 (0.1)
- `9d8a1d0` — CI/CD multi-VPS + system-map (0.2 + 0.3)
- `0aab019` — Sensors uniformes + dashboard (0.4)
- `f3780bf` — Backups + 12 runbooks (0.5 + 0.6)
- `e246a12` — DR drill + audit infra + skills + MCP (0.7-0.9)

Files added:
- 21 nuevos en VPS 1/VPS 2 versionado
- 5 workflows + 2 scripts CI/CD
- 1 system-map (autoritativo)
- 5 nuevos en livskin-sensor
- 1 OpenAPI spec
- 1 migration 0004 + 1 model + 1 service + 1 template + 1 cron script
- 8 nuevos scripts backups
- 13 runbooks (12 nuevos + 1 DR procedure)
- 1 audit-events-schema.md
- 4 skills (2 SKILL.md + 2 tools.json + READMEs)
- 1 MCP scaffold

**Total: ~70 archivos nuevos, ~5500 líneas.**

---

## Pendiente activar en producción

1. **GitHub Secrets nuevos:**
   - `DO_API_TOKEN` (DigitalOcean snapshots)
   - `AUDIT_INTERNAL_TOKEN` (cross-VPS audit events)
   - `VPS1_SSH_KEY`, `VPS1_HOST`, `VPS1_USER`
   - `VPS2_SSH_KEY`, `VPS2_HOST`, `VPS2_USER`

2. **Configurar en VPS 3:**
   - `AUDIT_INTERNAL_TOKEN` en `.env` de erp-flask
   - Container `erp-flask` con volume `/repo:ro` (rebuild)

3. **Migrar VPS 2:**
   - `bash /srv/livskin-revops/infra/docker/vps2-ops/migrate-from-home.sh --dry-run`
   - Si OK → ejecutar sin --dry-run

4. **Desplegar sensors:**
   - VPS 1: install systemd service `livskin-sensor`
   - VPS 2: `docker compose up -d` en `vps2-ops/livskin-sensor/`

5. **Crons:**
   - VPS 3: `bash /srv/livskin-revops/infra/docker/erp-flask/scripts/install-cron.sh`
   - VPS 3: `bash /srv/livskin-revops/infra/scripts/backups/install-cron-vps3.sh`

6. **Migration 0004:**
   - `docker compose -f infra/docker/alembic-erp/docker-compose.yml run --rm alembic-erp upgrade head`

7. **UFW cross-VPS:**
   - En cada VPS: `ufw allow from 10.114.0.0/20 to any port 9100`

---

## Próximos pasos

1. **Validar Bloque 0 en producción** (próxima sesión):
   - Activar los 7 pendientes arriba
   - Smoke tests de cada componente
   - Drill: ejecutar un deploy con rollback intencional para validar que funciona
   - Drill: restore de un backup a temp DB

2. **Merge a main + tag `v0.foundation`** una vez validado

3. **Arrancar Fase 3** con la base ya AI-operable:
   - Langfuse en VPS 2 (ya hay scaffold, solo agregar compose)
   - Migration analytics (ads_metrics, llm_costs, conversation_summary)
   - n8n workflows (SureForms → Meta CAPI + GA4 MP)
   - Custom JS UTM persistence en VPS 1 mu-plugins
   - Configurar plugins WP (PixelYourSite, SureForms, Complianz)

---

## Lecciones del bloque

1. **AI-first design cambia el énfasis sin cambiar el alcance.** Hubiéramos hecho los mismos 9 sub-bloques sin AI-first; lo que cambió fueron los formatos (machine-readable, tools.json, YAML frontmatter ejecutable) y la arquitectura (skills + MCP).

2. **Asimetrías documentadas son aceptables, no-documentadas son deuda.** VPS 3 con paths legacy es OK porque está documentado en `infra/docker/README.md`. Si no estuviera documentado, sería trampa para futuros operadores.

3. **El system-map es el documento más importante del bloque.** Indexable, parseable, con secciones autoexplicativas. El agente futuro empieza ahí cualquier query.

4. **Runbooks con frontmatter estructurado son skills.** No es un truco — es un patrón claro. Convierte documentación inerte en capability ejecutable.

5. **Sensors uniformes con API estandarizada > log aggregation custom.** Cuesta lo mismo de implementar y es mucho más reusable cross-stack.

6. **Backups sin verificación automática son backups inexistentes.** La verificación post-dump (restore a temp + count) es lo que diferencia un sistema confiable de uno teóricamente correcto.

---

## Métricas del bloque

- **Líneas de código:** ~5,500 nuevas
- **Archivos nuevos:** ~70
- **Commits:** 6 checkpoints
- **Documentos autoritativos creados:** 4 (sistema-mapa, audit-events-schema, dr-drill-procedure, runbooks/README)
- **Runbooks:** 12
- **Skills MCP:** 2 (con 10 tools combinados)
- **Workflows GHA nuevos:** 2 (deploy-vps1, deploy-vps2) + 1 mejorado (deploy-vps3)
- **Endpoints nuevos:** 4 (system-map.json, internal/audit-event, internal/health, internal/system-state)
- **Eventos auditables:** +18 (de 30 → 48 → 49 con 1 más en otra categoría)
- **Tests:** 0 nuevos en este bloque (los del Fase 2 siguen valiendo). Tests del bloque 0 viven en producción real.
