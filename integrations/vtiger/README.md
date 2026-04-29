# integrations/vtiger/ — config + docs Vtiger CRM 8.2

Vtiger es el master del **lead lifecycle** (marketing automation) en la arquitectura Livskin. Ver ADR-0015 (Source of Truth por dominio) y memoria `project_n8n_orchestration_layer`.

## Contenido

- [`fields-mapping.md`](fields-mapping.md) — diccionario `cf_NNN ↔ ERP columns` (los 12 custom fields del módulo Leads)

## URL + acceso

- **UI:** https://crm.livskin.site
- **Container:** `vtiger` (VPS 2 — `livskin-ops`)
- **DB:** `vtiger-db` MariaDB 10.6 — DB `livskin_db`, user `livskin`
- **Admin user:** `admin` (id 1)
- **REST API user:** `admin` con accesskey almacenado en `keys/.env.integrations` (gitignored)

## Setup ejecutado

| Fecha | Cambio | Origen |
|---|---|---|
| 2026-04-29 | Creados 12 custom fields en módulo Leads (atribución digital + tracking) | Mini-bloque 3.3 REWRITE |

## Cómo extender

Para agregar más custom fields o modificar el módulo Leads, seguir runbook [`docs/runbooks/vtiger-custom-fields.md`](../../docs/runbooks/vtiger-custom-fields.md). Después de cualquier cambio, actualizar [`fields-mapping.md`](fields-mapping.md).

## Cross-references

- ADR-0011 v1.1 — modelo de datos
- ADR-0015 — SoT por dominio
- Memoria `project_n8n_orchestration_layer` — n8n como capa orquestadora cross-system
- Memoria `project_capi_match_quality` — orden de identifiers para attribution
