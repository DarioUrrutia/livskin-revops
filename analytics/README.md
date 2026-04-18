# Analytics — Warehouse + Dashboards

Capa analítica del sistema. Fuente de todas las métricas de negocio y observabilidad.

## Contenido

```
analytics/
├── schemas/              # DDL (SQL files) del warehouse
│   ├── leads.sql
│   ├── opportunities.sql
│   ├── events.sql
│   ├── ads_metrics.sql
│   └── llm_costs.sql
├── migrations/           # Alembic migrations (versionadas)
│   └── versions/
│       └── 0001_initial.py
├── dashboards/           # exports JSON de Metabase
│   ├── leads-por-fuente.json
│   ├── conversion-por-etapa.json
│   └── sistema-completo.json
└── queries/              # queries comunes documentados
    ├── cac_por_canal.sql
    ├── ltv_por_cohorte.sql
    └── funnel_conversion.sql
```

## Warehouse — tablas principales

| Tabla | Contenido | Se popula por |
|---|---|---|
| `leads` | leads extraídos de Vtiger, con fuente/UTMs/fbclid | n8n ETL cada 5 min |
| `crm_stages` | historial cambios etapa del lead | n8n ETL + event trigger |
| `opportunities` | conversiones (ventas) con revenue y atribución | n8n ETL al cerrar venta |
| `events` | todos eventos tracking (PageView, Lead, Purchase, etc.) | SureForms webhook + server-side |
| `ads_metrics` | métricas Meta Ads por creativo/día | Meta Ads API pull horario |
| `llm_costs` | costos Claude API por agente/ejecución | Langfuse integration |
| `conversation_summary` | métricas agregadas de conversaciones (no contenido) | n8n daily ETL desde brain |

## Motor y ubicación

- **DB:** `analytics` en container `postgres-analytics` (VPS 2)
- **Motor:** PostgreSQL 16
- **Schema management:** Alembic migrations (ADR-0010)

## Consumidor principal

**Metabase** (VPS 2, subdominio `dash.livskin.site`) consulta `analytics` con usuario `metabase_reader` (solo SELECT).

## Dashboards planeados

| Dashboard | Fase | Contenido |
|---|---|---|
| Infra Health | Fase 1 | CPU/RAM/disco por VPS, uptime subdominios |
| Leads por Fuente | Fase 2 | Top canales, tendencias, conversión por canal |
| Conversión por Etapa | Fase 3 | Funnel Vtiger stages, drop-off points |
| Tracking Health | Fase 3 | Match quality Meta CAPI, eventos recibidos |
| Conversation Agent | Fase 4 | Volumen conversaciones, tiempo respuesta, escalaciones |
| Creative Performance | Fase 5 | Top creativos, CPL por creativo, format winners |
| Sistema Completo | Fase 6 | Vista ejecutiva end-to-end con semáforos |

## Referencias

- ADR-0002 — Arquitectura de datos (define dónde vive `analytics`)
- ADR-0010 — Alembic migrations
- ADR-0019 — Tracking architecture (poblador principal de `events`)
- ADR-0040 — Cost tracking (poblador de `llm_costs`)
