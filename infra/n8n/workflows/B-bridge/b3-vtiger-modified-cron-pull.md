# [B3] Sync Vtiger Modified Leads → ERP Mirror (cron pull)

**Categoría:** bridge
**Fase:** 3 (Mini-bloque 3.3 REWRITE)
**Criticidad:** critical
**Estado:** staging (en validación al 2026-05-01)
**Trigger:** cron (NO webhook)
**Schedule:** cada 2 minutos

---

## Qué hace

Cada 2 minutos, query Vtiger por leads modificados en los últimos 3 minutos (buffer de 1 min para clock skew + workflow runtime). Para cada lead modificado: `retrieve()` + map cf_NNN → ERP + POST `/api/leads/sync-from-vtiger`.

**Reemplaza la necesidad de webhook on-change Vtiger.** Razones (ver memoria + Paso 6.5):
- Vtiger 8.2 community no tiene "Send To URL" task nativo
- Cron pull es independiente de config Vtiger (robusto a upgrades)
- Latencia 0-3 min es aceptable para MVP (la doctora contacta en min/horas)
- En F4+ podemos pasar a realtime via Custom PHP Hook (Opción D) si Conversation Agent lo requiere

**Idempotente:** `/api/leads/sync-from-vtiger` por diseño — reprocesar un lead 2 veces (overlap de ventana) no causa duplicados ni inconsistencia.

---

## Trigger

**Schedule Trigger** — cron `*/2 * * * *` (cada 2 minutos UTC).

---

## Input

Ninguno (cron). El workflow internamente:
1. Calcula `since = now() - 3 minutes` en UTC
2. Query Vtiger: `SELECT id, modifiedtime FROM Leads WHERE modifiedtime > '<since>';`

---

## Output

No hay response (cron). Cada execution loguea en n8n:
- Cuántos leads modificados encontró
- Cuántos POSTeó exitosamente al ERP
- Errores per lead (si los hubo)

---

## Sistemas tocados

| Sistema | Acceso |
|---|---|
| Vtiger via REST API | read (login + query + retrieve N veces) |
| ERP `/api/leads/sync-from-vtiger` | write (POST por cada lead modificado) |
| n8n SQLite (execution log) | write automático |

---

## Flujo (10 nodos)

```
[1] Schedule Trigger (cron */2 * * * *)
       ↓
[2] Build query window (Code) — calcula 'since' UTC
       ↓
[3] Vtiger getchallenge (HTTP GET)
       ↓
[4] Compute MD5 Hash (Code)
       ↓
[5] Vtiger Login (HTTP POST → sessionName)
       ↓
[6] Vtiger Query Modified Leads (HTTP GET — SELECT WHERE modifiedtime > since)
       ↓
[7] Split into individual items (n8n Split Out node)
       ↓ (por cada lead modificado)
[8] Vtiger Retrieve Lead (HTTP GET retrieve(id))
       ↓
[9] Map cf_NNN → ERP Schema (Code)
       ↓
[10] POST ERP /api/leads/sync-from-vtiger (HTTP POST)
       ↓
(Done — no response needed)
```

---

## Credenciales necesarias (env vars en n8n container — ya seteadas)

```bash
VTIGER_URL=https://crm.livskin.site
VTIGER_API_USER=admin
VTIGER_API_ACCESSKEY=<keys/.env.integrations>
ERP_SYNC_URL=https://erp.livskin.site/api/leads/sync-from-vtiger
AUDIT_INTERNAL_TOKEN=<keys/.audit-internal-token VPS 3>
```

---

## Errores conocidos / edge cases

| Caso | Comportamiento |
|---|---|
| Vtiger query devuelve 0 leads modificados | Workflow corre 0 iteraciones del loop, completa OK |
| Vtiger session expira mid-loop | n8n no re-autentica automatic — falla este run, próximo cron arranca limpio |
| ERP responde 4xx para 1 lead | Loguea error, continúa con próximo lead |
| ERP responde 5xx para 1 lead | Loguea error, próximo cron lo reintenta (idempotente) |
| Vtiger query timeout | Falla este run, próximo cron reintenta |
| Lead nuevo creado por [A1] | Aparece en query del cron siguiente con modifiedtime reciente — sync OK |
| Lead modificado >3 min antes del cron | NO se procesa hasta que vuelva a modificarse — diseño aceptado (window de catch-up es próximo modify) |
| Múltiples crons solapados (lento) | n8n maneja isolation por execution — OK |

---

## Tags n8n (post-import)

```
bridge · fase-3 · critical · staging  (cambia a production tras 24h sin issues)
```

---

## Cómo testar manualmente

```bash
# 1. Crear/modificar un lead en Vtiger UI o via [A1]
curl -X POST https://flow.livskin.site/webhook/acquisition/form-submit \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Test B3 Cron", "phone": "+51999000B30", "consent_marketing": true}'

# 2. Esperar 2-3 minutos (siguiente ejecución del cron)

# 3. Verificar en ERP DB
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp \
  -c "SELECT vtiger_id, nombre, fuente FROM leads ORDER BY id DESC LIMIT 3;"'

# 4. Verificar execution log en n8n UI
# https://flow.livskin.site → Workflows → [B3] → Executions
# Cada execution debe mostrar: query devuelve N items → split → POST por cada uno
```

---

## Cuándo migrar a realtime (Opción D — Custom PHP Hook)

**Trigger para reabrir esta decisión:**
- Conversation Agent (F4) requiere reaccionar a cambios en <30s
- Volumen de leads > 100/día (cron de 2 min se queda corto si hay backlog grande)
- Doctora pide "ver leads en ERP en tiempo real al cambiarlos en Vtiger"

**Plan de migración:**
1. Escribir custom PHP module `modules/CRMEntity/CustomHooks.php` en Vtiger que dispara `[B1]` webhook on-change
2. Activar [B1] webhook trigger (ya existe)
3. Bajar frecuencia de [B3] cron a cada 15 min (catch-up backup en caso webhook falle)
4. Después de 1 semana sin issues, desactivar [B3] completo

---

## Cambios

- 2026-05-01 v1.0 — diseño inicial Mini-bloque 3.3 REWRITE
