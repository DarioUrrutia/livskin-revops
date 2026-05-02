# [E1] ERP Leads + Clientes + Ventas + Pagos → Analytics Warehouse

**Categoría:** etl
**Fase:** 3 (Mini-bloque 3.5)
**Criticidad:** medium
**Estado:** staging (en construcción al 2026-05-02)
**Schedule:** every 5 min
**ADR:** [ADR-0032](../../../../docs/decisiones/0032-metabase-warehouse-architecture-y-etl-strategy.md)

---

## Qué hace

Pull incremental cada 5 min desde el ERP via REST endpoint `/api/internal/sync/<resource>`,
y UPSERT en `analytics` warehouse (postgres-analytics en VPS2).

**4 sub-syncs en serie**:
1. `livskin_erp.leads` → `analytics.leads` (con merge de Vtiger fields preservados)
2. `livskin_erp.clientes` → join data para `analytics.leads.fecha_cliente` + populate cliente refs
3. `livskin_erp.ventas` → `analytics.opportunities`
4. `livskin_erp.pagos` → rollup en `analytics.opportunities` (monto_pagado, saldo_pendiente, estado_pago)

Idempotente: el cron usa `analytics.etl_runs` para guardar último `since` exitoso. Si un run
falla, el siguiente cron retoma desde el last known good.

Audit: cada run agrega fila a `analytics.etl_runs` con status + counts.

---

## Trigger

Schedule node: every 5 min (cron `*/5 * * * *`).

---

## Flujo (10 nodos)

```
[1] Schedule Every 5min
        ↓
[2] Get Last Sync Cursor (Postgres SELECT)
    -> SELECT MAX(finished_at) FROM etl_runs WHERE etl_name='E1' AND status='success'
        ↓
[3] HTTP GET ERP /api/internal/sync/leads?since=<cursor>&limit=500
        ↓
[4] HTTP GET ERP /api/internal/sync/clientes?since=<cursor>&limit=500
        ↓
[5] HTTP GET ERP /api/internal/sync/ventas?since=<cursor>&limit=500
        ↓
[6] HTTP GET ERP /api/internal/sync/pagos?since=<cursor>&limit=500
        ↓
[7] Code: Map ERP -> Analytics schemas (leads + opportunities)
   -> Construye 2 arrays: leads_to_upsert + opps_to_upsert
   -> Calcula rollups de pagos por venta_id (monto_pagado, saldo_pendiente)
        ↓
[8] Postgres UPSERT analytics.leads (per item, ON CONFLICT vtiger_id DO UPDATE)
        ↓
[9] Postgres UPSERT analytics.opportunities (per item, ON CONFLICT venta_id DO UPDATE)
        ↓
[10] Postgres INSERT analytics.etl_runs (audit del run)
```

---

## Mapping ERP → analytics.leads

| Source ERP | Target analytics.leads |
|---|---|
| `id` | `erp_lead_id` |
| `cod_lead` | `cod_lead` |
| `vtiger_id` | `vtiger_id` (UNIQUE — primary correlation key) |
| `nombre` | `nombre` |
| `phone_e164` | `phone_e164` |
| `email_lower` | `email_lower` |
| `fuente` | `fuente` |
| `canal_adquisicion` | `canal_adquisicion` |
| `utm_source_at_capture` | `utm_source_at_capture` |
| `utm_medium_at_capture` | `utm_medium_at_capture` |
| `utm_campaign_at_capture` | `utm_campaign_at_capture` |
| `utm_content_at_capture` | `utm_content_at_capture` |
| `utm_term_at_capture` | `utm_term_at_capture` |
| `fbclid_at_capture` | `fbclid_at_capture` |
| `gclid_at_capture` | `gclid_at_capture` |
| `fbc_at_capture` | `fbc_at_capture` |
| `ga_at_capture` | `ga_at_capture` |
| `event_id_at_capture` | `event_id_meta` |
| `tratamiento_interes` | `tratamiento_interes` |
| `consent_marketing` | `consent_marketing` |
| `estado_lead` | `estado_lead` |
| `fecha_captura` | `fecha_captura` |
| (cliente: cod_lead → fecha_primera_visita) | `fecha_cliente` |
| (cliente: cod_lead → primera venta.fecha_venta) | `fecha_primera_venta` |
| `created_at`, `updated_at` | `created_at`, `updated_at` |
| (constante) | `sync_source = 'erp'` |
| (constante) | `last_synced_at = NOW()` |

Vtiger-only fields (`leadsource_vtiger`, `leadstatus_vtiger`) quedan NULL en este ETL —
los popula `[E2]` desde Vtiger directamente.

## Mapping ERP → analytics.opportunities

| Source ERP | Target analytics.opportunities |
|---|---|
| `ventas.id` | `venta_id` (UNIQUE) |
| `ventas.cliente_id` | `cliente_id` |
| `ventas.cod_venta` | `cod_venta` |
| `ventas.fecha_venta` | `fecha_venta` |
| `ventas.tratamiento` | `tratamiento` |
| `ventas.cantidad_sesiones` | `cantidad_sesiones` |
| `ventas.monto_*` | `monto_*` |
| `ventas.estado_*` | `estado_*` |
| `ventas.vendedor` | `vendedor` |
| (lookup: clientes.cod_lead_origen → leads.id) | `lead_id` |
| (lookup: clientes.vtiger_lead_id_origen) | `vtiger_lead_id` |
| (lookup: leads.event_id_at_capture) | `event_id_meta` |
| `created_at`, `updated_at` | `created_at`, `updated_at` |

---

## Credenciales necesarias

- n8n credentials `Postgres Analytics ETL Writer` (postgres-analytics en VPS2)
- env var `ERP_SYNC_BASE_URL = https://erp.livskin.site`
- env var `AUDIT_INTERNAL_TOKEN` (X-Internal-Token para auth ERP)

---

## Idempotencia

- ERP endpoint devuelve filas ASC por `updated_at`. n8n procesa en order.
- UPSERT por `vtiger_id` (leads) y `venta_id` (opportunities) — re-procesar mismo lote es no-op.
- `etl_runs` registra last `since` usado y `next_since_hint` recibido.

## Failure modes + retries

- HTTP timeout/5xx → retry 3 veces (max). Si falla, etl_runs status='error'. Próximo cron retry.
- Postgres UPSERT failure → log error en etl_runs, abort batch (no avanza cursor).
- Empty response → status='success' rows=0, cursor avanza a `now()`.

## Output esperado

`etl_runs` row al fin de cada cron:
```json
{
  "etl_name": "E1",
  "status": "success",
  "rows_processed": 12,
  "rows_inserted": 3,
  "rows_updated": 9,
  "duration_ms": 1240
}
```

---

## Verificación post-deploy

```bash
# Check last 5 runs
docker exec postgres-analytics psql -U analytics_user -d analytics \
  -c "SELECT etl_name, status, rows_processed, finished_at FROM etl_runs WHERE etl_name='E1' ORDER BY started_at DESC LIMIT 5;"

# Compare counts ERP vs warehouse
echo "ERP leads:"
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT count(*) FROM leads;"'

echo "Analytics leads:"
ssh livskin-ops 'docker exec postgres-analytics psql -U analytics_user -d analytics -c "SELECT count(*) FROM leads;"'
```

Esperado: counts match dentro de un delta de 1-2 (lag del cron).
