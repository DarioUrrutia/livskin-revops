# `infra/n8n/` — workflows + convenciones de la capa orquestadora

n8n es la **capa visual orquestadora** de TODAS las automatizaciones cross-system de Livskin. Toda integración entre WordPress, Vtiger, ERP Postgres, Brain pgvector, Metabase, WhatsApp Cloud API, Meta Ads y Google Ads pasa por aquí.

**URL UI:** https://flow.livskin.site
**Container:** `n8n` en VPS 2 (`livskin-ops`)
**Setup:** Bloque 0 v2 (2026-04-26) — workflows agregados a partir de Mini-bloque 3.3 REWRITE (2026-04-29)

Ver memoria `project_n8n_orchestration_layer.md` para el manifiesto completo de "n8n = capa visible".

---

## Convenciones (autoritativas)

Ver [`conventions.md`](conventions.md) para el sistema completo de naming, folder structure, tags y URLs.

**TL;DR:**
- Workflows nombrados `[<Letra><Numero>] <Verbo> <Objeto> → <Destino>`
- Categorías: A (Acquisition), B (Bridge), C (Conversion), D (Dialogue), E (Engagement), F (Feed), G (Growth), H (Health)
- Webhook URLs namespaced por categoría: `/webhook/<categoria>/<nombre>`
- Cada workflow tiene `.json` (importable) + `.md` (doc humana)

---

## Index de workflows

### Estado actual: 0 workflows en producción (n8n virgen al 2026-04-29 antes de 3.3)

### A — Acquisition (captura de leads)

| Workflow | Estado | Fase |
|---|---|---|
| [A1] Capturar Form Submit → Vtiger Lead | 🚧 en desarrollo (3.3 REWRITE) | F3 |
| [A2] Capturar WhatsApp Inbound → Vtiger Lead | ⏳ pendiente | F4 |

### B — Bridge (sync Vtiger ↔ ERP)

| Workflow | Estado | Fase |
|---|---|---|
| [B1] Espejar Vtiger Lead Changed → ERP Mirror | 🚧 en desarrollo (3.3 REWRITE) | F3 |
| [B2] Marcar ERP Cliente Created → Vtiger Lead Converted | ⏳ pendiente | F6 |

### C — Conversion (lead → cliente lifecycle)

| Workflow | Estado | Fase |
|---|---|---|
| (vacío hoy) | — | F6 |

### D — Dialogue (Conversation Agent)

| Workflow | Estado | Fase |
|---|---|---|
| [D1] Procesar WhatsApp Inbound → Conversation Agent | ⏳ pendiente | F4 |
| [D2] Despachar Agent Response → WhatsApp Outbound | ⏳ pendiente | F4 |

### E — Engagement (nurture + handoff)

| Workflow | Estado | Fase |
|---|---|---|
| [E1] Nurture Drip → WhatsApp Template | ⏳ pendiente | F4 |
| [E2] Handoff Score ≥70 → Notificar Doctora | ⏳ pendiente | F4 |

### F — Feed (analytics ETL)

| Workflow | Estado | Fase |
|---|---|---|
| [F1] Sync ERP Daily → Metabase Cube | ⏳ pendiente | F3.5 / F5 |

### G — Growth (audiences sync)

| Workflow | Estado | Fase |
|---|---|---|
| [G1] Sync Customers → Meta Custom Audience | ⏳ pendiente | F5 |
| [G2] Sync Customers → Google Customer Match | ⏳ pendiente | F5 |
| [G3] Sync ERP Conversions → Meta CAPI | ⏳ pendiente | F3.4 |

### H — Health (monitoring + alertas)

| Workflow | Estado | Fase |
|---|---|---|
| [H1] Monitor Disk + RAM → WhatsApp Alert | ⏳ pendiente | F6 |
| [H2] Monitor Agent Costs → WhatsApp Alert si excede | ⏳ pendiente | F6 |
| [H3] Monitor Vtiger/ERP Health → WhatsApp Alert si down | ⏳ pendiente | F6 |

---

## Cómo desarrollar un workflow nuevo

1. **Identificar categoría correcta** (ver `conventions.md`)
2. **Reservar siguiente número** dentro de la categoría
3. **Crear archivo** `infra/n8n/workflows/<categoria>/<id>-<nombre-kebab>.json` (lo escribe Claude o exportás de n8n UI)
4. **Crear doc complementaria** `infra/n8n/workflows/<categoria>/<id>-<nombre-kebab>.md`
5. **Importar a n8n** vía `docker exec n8n n8n import:workflow --input=<path>` o UI Import
6. **Agregar tags** apropiados en n8n UI (categoria + fase + criticidad + estado)
7. **Smoke test** con curl manual al webhook (si trigger es webhook)
8. **Activar workflow** vía CLI o UI
9. **Actualizar este README** moviendo el workflow a su tabla con estado actualizado

---

## Cómo extraer el JSON de un workflow ya creado en n8n UI

```bash
# Export workflow ID 5 a archivo
ssh -F keys/ssh_config livskin-ops 'docker exec n8n n8n export:workflow --id=5 --output=/tmp/workflow.json'
ssh -F keys/ssh_config livskin-ops 'docker cp n8n:/tmp/workflow.json -' > infra/n8n/workflows/A-acquisition/A1-form-submit-to-vtiger-lead.json
```

---

## Cross-references

- Memoria `project_n8n_orchestration_layer.md` — manifiesto de n8n como capa orquestadora
- Memoria `project_acquisition_flow.md` — flujo end-to-end de adquisición digital
- ADR-0011 v1.1 — modelo de datos (consume Workflows A + B)
- ADR-0015 — Source of Truth (define qué workflow escribe a qué sistema)
- `integrations/vtiger/fields-mapping.md` — mapeo cf_NNN ↔ ERP (consumido por Workflows A + B)
- Runbook `n8n-workflow-failing.md` — troubleshooting cuando un workflow falla
