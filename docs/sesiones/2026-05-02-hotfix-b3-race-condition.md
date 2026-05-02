# 2026-05-02 — HOTFIX n8n [B3] race condition resuelto

## Contexto inicial

Sesión cerrada el 2026-05-02 dejó el HOTFIX B3 documentado en backlog (severidad media, bloqueante para campañas con tráfico múltiple). Esta mini-sesión tomó el HOTFIX como tarea única.

## Qué se hizo

Preflight cross-system aplicado (3 sistemas: n8n + Vtiger + ERP). Brain query + memorias 🔥 CRÍTICAS revisadas. Plan citado aprobado por Dario.

### Diagnóstico

**Reproducción:** 3 form leads creados consecutivos en ventana de 7 segundos (10x16, 10x17, 10x18). Cron B3 (08:14:37) procesó SOLO 10x16. Los otros 2 quedaron orphan permanentemente (modifiedtime salió del window de futuros crons).

**Causa raíz identificada vía static analysis del JSON exportado** (sin necesidad de inspeccionar execution_data interno):
- Nodo `Prepare Retrieve` (Code, post-Split) usaba `$input.first().json` → tomaba 1 de N items
- Nodo `Map Vtiger to ERP Schema` (Code, post-HTTP-Retrieve) mismo bug
- Resultado: N-1 leads silently dropped por cada batch

### Fixes aplicados

**B3_BATCH_FIX_v1** (2 patches):
- `Prepare Retrieve`: `$input.all().map(it => ({ json: { vtiger_id: it.json.id, _vtiger_session: session }}))` para procesar TODOS los items
- `Map Vtiger to ERP Schema`: loop `for (const it of $input.all())` con graceful handling de Vtiger retrieve failures + Op B preservada (skip wa-click)

Smoke parcial post-batch-fix con 10x19/10x20/10x21 (3 leads concurrent) reveló **bug adicional** en ERP: `psycopg2.errors.UniqueViolation: Key (cod_lead)=(LIVLEAD0002) already exists`. Cod_lead generation no es atómica → race entre INSERTs concurrentes → segundo INSERT falla y aborta el workflow B3 entero.

**B3_CONTINUE_ON_FAIL_v1**:
- `continueOnFail: true` + `retryOnFail: true` (maxTries=3, waitBetweenTries=1000ms) en nodo POST ERP
- Bandaid: errores individuales no abortan el batch; retries resuelven transient failures como cod_lead race

### Validación E2E

Smoke final con 10x22/10x23/10x24 (3 leads en <1s span):
- Cron 785 status `success` (no más `error`)
- Los 3 leads llegaron a ERP con cod_leads LIVLEAD0005/6/7
- cod_lead asignado out-of-order (10x22→0007, 10x23→0005, 10x24→0006) confirmando que el race del ERP existe pero retry lo resuelve transparente

### Cleanup

9 leads test (10x16-10x24) borrados de Vtiger + ERP.

## Decisiones tomadas

1. **Bandaid retry sobre fix proper**: aplicado `continueOnFail+retry` en B3 en lugar de fixear la generación atómica de cod_lead en ERP. Razón: scope único (n8n B3), evitar tocar Alembic + tests ERP en mini-sesión. Fix proper en backlog con severidad baja.

2. **Op B preservada en Map node**: el rewrite del Code node mantiene `if (v.leadsource === 'WA Direct Click') continue` para no romper la decisión arquitectónica del cierre 2026-05-02.

## Hallazgos relevantes

- **ERP cod_lead race condition**: revelado por el batch fix. Bug pre-existente que solo se manifestaba cuando había concurrent INSERTs. Antes del batch fix, B3 procesaba 1 lead a la vez por accidente, escondiendo este bug.
- **Leads orphan permanentes**: cuando un cron falla mid-batch SIN continueOnFail, los leads que no llegan a procesarse quedan permanentemente orphan en Vtiger (modifiedtime sale del lookback window de 3 min). Reprocessing manual requeriría tocar modifiedtime para forzar re-pickup.

## Lo que queda pendiente

- **HOTFIX ERP cod_lead atomic generation** (severidad baja, retry transparente lo resuelve hoy). Backlog item separado para próxima sesión ERP.
- **Mini-bloque 3.5 Observabilidad + Metabase** (4-6h) — próxima sesión grande.

## Próxima sesión propuesta

**Mini-bloque 3.5 — Observabilidad + Metabase** (4-6h con preflight obligatorio).
