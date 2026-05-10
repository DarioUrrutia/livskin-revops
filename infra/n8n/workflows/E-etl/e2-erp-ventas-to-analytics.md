# [E2] ERP Ventas → Analytics Opportunities

**Categoría:** etl
**Fase:** 3 (Mini-bloque 3.5)
**Criticidad:** medium
**Estado:** staging (en validación)
**Schedule:** every 10 min
**ADR:** [ADR-0032](../../../../docs/decisiones/0032-metabase-warehouse-architecture-y-etl-strategy.md)

---

## Qué hace

Pull incremental cada 10 min de `livskin_erp.ventas` via REST endpoint `/api/internal/sync/ventas` (read-only) y UPSERT en `analytics.opportunities` warehouse (postgres-analytics en VPS2).

**Workflow complementario al [E1]** — E1 sincroniza la chain completa (leads + clientes + ventas + pagos en serie cada 5 min); E2 es enfoque más rápido específico solo a ventas (y pagos rollup) para dashboards de revenue near-realtime.

Diferencia con E1:
- **E1**: comprehensive — 4 syncs en serie, every 5 min, latency aceptable 5-10 min, dashboards completos
- **E2**: focused — solo opportunities + revenue rollup, every 10 min, latency 10-15 min, dashboards revenue-focused

---

## Trigger

**Schedule Trigger** — cron `*/10 * * * *` (cada 10 minutos UTC).

---

## Cursor

n8n persiste `last_synced_venta_at` en `analytics.etl_runs.last_synced_at` para tracking. Cursor avanza al `MAX(updated_at)` del response exitoso.

---

## Filtros del endpoint ERP

`GET /api/internal/sync/ventas?since=<ISO8601>&limit=500`:
- `ventas.updated_at > since`
- ORDER BY `updated_at` ASC
- LIMIT 500 (default, max 5000)

Auth: `X-Internal-Token` header.

---

## Idempotencia

UPSERT en `analytics.opportunities` por `cod_item` (PK natural):
- INSERT si no existe
- UPDATE si existe (campos modificados se sobrescriben)

Re-run del mismo cron es seguro — los datos quedan en último estado del ERP.

---

## Cross-references

- ADR-0032 — Metabase warehouse + ETL strategy
- Workflow [E1] — sync comprehensive cada 5 min (alternativa)
- `infra/docker/erp-flask/routes/api_internal_sync.py` — endpoint ERP
- `analytics.opportunities` schema — tabla destino en VPS2 postgres-analytics
