# Sesión 2026-04-29 → 2026-05-01 — Mini-bloque 3.3 REWRITE completo end-to-end

**Duración:** sesión multi-día (3 días, ~12-15 horas reales).
**Fase:** 3 (Tracking + leads).
**Resultado:** **Pipeline form WP → Vtiger → ERP 100% operacional con first-touch attribution preservado.**

---

## Contexto inicial

Sesión arranca tras cleanup completo de Mini-bloque 3.3 fallido (sesión 2026-04-29). El intento previo había implementado Form → ERP webhook directo, ignorando ADR-0011 v1.1 + ADR-0015 + memoria `project_acquisition_flow` que documentaban el flujo correcto Form → n8n → Vtiger → ERP espejo.

Esta sesión REWRITE comienza aplicando rigurosamente el runbook `preflight-cross-system.md` recién escrito.

---

## Qué se hizo

### Pre-flight cross-system completo

Antes de tocar código, ejecuté las 5 etapas del protocolo:
1. ✅ Releí 6 memorias críticas literal (vtiger_erp_sot, acquisition_flow, n8n_orchestration_layer, must_re_read_adrs_before_coding, surgical_precision_erp, capi_match_quality)
2. ✅ Query brain pgvector con keyword "flujo lead form vtiger n8n erp espejo phone anchor" — top 8 chunks relevantes
3. ✅ Leí ADR-0011 v1.1 + ADR-0015 completos
4. ✅ Identifiqué los 4 sistemas involucrados (WordPress + n8n + Vtiger + ERP)
5. ✅ Plan citado aprobado por Dario antes del primer commit

### Construcción granular paso por paso

**Migration Alembic 0006** (commits `00d7a60` + `1741fdc` fix revision ID limit):
- 9 columnas nuevas (3 por tabla × 3 tablas: leads, lead_touchpoints, form_submissions)
- `fbc_at_capture`, `ga_at_capture`, `event_id_at_capture` (ADR-0011 v1.1 no anticipó estas 3 cookies/IDs)
- 3 índices btree
- Migration 100% reversible
- Aplicada en VPS 3 producción + verificada

**Vtiger setup** (commit `69a2d01`):
- 12 custom fields creados via UI admin (Dario manualmente, ~10 min)
- Picklist `cf_875` con 9 opciones de tratamiento
- REST API verified end-to-end (login + describe + create + delete)
- Documentación: `integrations/vtiger/README.md` + `fields-mapping.md` (cf_NNN ↔ ERP)
- Runbook `docs/runbooks/vtiger-custom-fields.md` evergreen

**Sistema organizacional n8n** (mismo commit):
- 8 categorías canónicas (A-H) documentadas en `infra/n8n/conventions.md`
- Naming pattern `[<Letra><Numero>] <Verbo> <Objeto> → <Destino>`
- Webhook URLs namespaced `/webhook/<categoria>/<nombre-kebab>`
- Folder structure `infra/n8n/workflows/A-acquisition/` etc.
- Index vivo en `infra/n8n/README.md` (16 workflows mapeados)

**n8n Workflow [A1] form→Vtiger** (mismo commit):
- 16 nodes, 14 connections
- Validate phone E.164 + Vtiger auth (getchallenge + md5 + login) + dedup query + create/skip + respond
- 4 smoke tests pasados (mínimo + dedup + full payload con 12 cf_NNN + phone inválido)
- Aprendizajes registrados:
  - n8n requiere `id` field a nivel workflow para import
  - `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` necesario para `$env.*` en nodos
  - `NODE_FUNCTION_ALLOW_BUILTIN=crypto` necesario para md5

**Endpoint Flask `/api/leads/sync-from-vtiger`** (commit `2918bb7`):
- 4 archivos nuevos: schema (Pydantic), service, route, tests
- 18 tests TDD escritos primero (fallaron correctamente) → implementación → 18 pasaron
- Coverage global 79.25% (target ADR-0023: ≥75%)
- 0 regresiones en 220 tests existentes (total 238 pasan)
- Idempotencia por `vtiger_id`: CREATE si nuevo, UPDATE preservando at_capture (first-touch immutable)
- Mapeo Vtiger leadstatus → ERP estado_lead (12 valores)
- Mapeo Vtiger leadsource → ERP fuente (7 valores)
- Audit log entry `lead.synced_from_vtiger`
- Smoke test E2E productivo: CREATE + UPDATE + at_capture immutability verificada

**n8n Workflow [B1] Vtiger→ERP receiver** (commit `86073c0`):
- 13 nodes — webhook receiver para futuro Custom PHP Hook Vtiger
- Smoke test: lead Vtiger 10x4 → ERP `leads` propagado con 12 attribution fields

**n8n Workflow [B3] cron pull** (commit `53fe70f`):
- 12 nodes, schedule cron `*/2 * * * *`
- Query Vtiger leads modificados últimos 3 min (1 min buffer)
- Loop por modified leads: retrieve + map cf_NNN → ERP + POST sync-from-vtiger
- Reemplaza necesidad de webhook on-change (Vtiger 8.2 community no tiene "Send To URL" task nativo)
- Migración a realtime diferida (Custom PHP Hook) para F4+ si Conversation Agent requiere <30s
- Smoke test E2E: lead creado via [A1] aparece en ERP automáticamente <2.5 min sin trigger manual

**mu-plugin WordPress** (pendiente commit final):
- Archivo: `infra/wordpress/mu-plugins/livskin-form-to-n8n.php` (~470 líneas)
- **Form-id agnostic** — funciona con cualquier SureForms form via post_meta `_livskin_n8n_sync`
- Modo `prod` (POST a [A1]) | `test` (solo log) | `off` (no hace nada)
- Hardcoded fallback config para forms canónicos
- Mapeo defensivo SureForms slug → n8n payload (Pass 1 exact, Pass 2 fuzzy)
- JS injection extendido v1.1: populates 11 hidden inputs desde URL params + cookies + UUID al submit
- Persistencia 90 días en cookies `lvk_*` para multi-session attribution
- Fire-and-forget POST (non-blocking — UX form no se afecta)
- Try/catch para nunca fallar la submission del form

**Validación E2E final productiva:**
- Lead real submit en https://livskin.site con URL `?utm_source=instagram&utm_campaign=prod-final-test&fbclid=...`
- mu-plugin captura 17 fields (4 user + 11 hidden + 3 server)
- POST a [A1] → Vtiger Lead 10x8 con 12 cf_NNN poblados
- Cron [B3] propaga a ERP en <2 min con first-touch attribution preservado
- Audit log entry registrada inmutable

### Vtiger UI walkthrough con Dario

Dario aprendió a usar Vtiger UI:
- Login + navegación a Leads module
- Lista filtrada por attribution
- Custom view "Leads de Meta Ads" (UTM Source = facebook OR instagram) creada
- Detail view con 2 bloques nuevos (Atribución Digital + Tracking Avanzado)
- Bulk actions + export CSV

Validado en producción: lead con UTM Source = `facebook` aparece en custom view; lead con UTM Source = `demo` correctamente excluido.

### Documentación + sistema organizacional

**Memoria nueva crítica:** `project_agent_skills_inventory.md` — tracker continuo de capacidades por agente. Tabla retroactiva de TODO lo construido desde Bloque 0 v2 hasta hoy + qué agente futuro lo usará. Input pre-mapeado para sesión estratégica organizacional pre-Fase 5.

**Memoria nueva:** `feedback_commit_approval_explicit.md` — cada commit/push requiere aprobación explícita en ese momento (Dario corrigió esto durante la sesión).

**Runbook nuevo:** `docs/runbooks/wordpress-form-livskin-integration.md` — cómo activar/desactivar/debuggear forms WP nuevos con el mu-plugin.

**Runbook actualizado:** `docs/runbooks/cierre-sesion.md` § 8 — check explícito al inventory de skills (OBLIGATORIO si hubo build).

**Backlog (3 items nuevos + 1 movido a Hecho):**
- 🔴 Metabase dashboards de leads (Mini-bloque 3.5)
- 🟡 ERP `/admin/leads` page (Fase 4-5)
- 🟡 Alinear picklist Vtiger `cf_875` con dropdown form WP 1569
- ✅ Mini-bloque 3.3 REWRITE movido a Hecho con full historial

---

## Decisiones tomadas

### 1. n8n control vars en `.env` (no hardcoded en compose)

`N8N_BLOCK_ENV_ACCESS_IN_NODE=false`, `NODE_FUNCTION_ALLOW_BUILTIN=crypto`, `EXECUTIONS_DATA_SAVE_*=all` se setean en `.env` del VPS (gitignored). `.env.example` documenta el pattern.

**Razón:** secretos + control flags en mismo lugar; reproducible cross-VPS; visible en `docker inspect`.

### 2. SureForms se queda (no migración a Gravity Forms)

Considerado migración a Gravity Forms ($59/año, Hidden block nativo, 15 años de track record). Decisión: stick con SureForms + mu-plugin generic. Razones:
- Free vs $59/año (CLAUDE.md principio 8)
- mu-plugin abstraction layer mitiga fragility
- Migración reversible si SureForms falla en F4-F5

**Reabrir:** ≥5 forms simultaneously, conditional logic complejo, multi-step forms, bug SureForms persistente.

### 3. Cron pull en lugar de webhook on-change Vtiger (MVP)

Vtiger 8.2 community no tiene "Send To URL" workflow task nativo. 4 opciones evaluadas:
- A: Vtiger Workflows UI (no soportado en community)
- B: Custom PHP Hook (frágil al upgrade)
- C: **Cron pull en n8n (elegido)** — robusto + sin tocar Vtiger core
- D: Workflow Tasks Custom Function (requiere PHP custom)

Latencia 0-3 min aceptable para MVP. Migración a realtime (D) diferida para F4+ si Conversation Agent requiere.

### 4. mu-plugin self-sufficient (vs depender de GTM Tracking Engine)

Hallazgo durante validación: GTM Tracking Engine (Mini-bloque 3.2) NO populates los hidden inputs `lvk_*`. Estaba diseñado para fire events Pixel/GA4, no para escribir a inputs.

Decisión: ampliar JS del mu-plugin para que él mismo populates inputs (URL params + cookies + UUID al submit). Independiente de GTM. Single source of truth.

**Trade-off:** ~40 líneas más de JS en mu-plugin. Beneficio: cero coupling con GTM, más resiliente.

### 5. Test mode opt-in via post_meta

Forms en estado `test` loguean payload pero NO postean a n8n. Permite iterar/validar nuevos forms sin contaminar Vtiger/ERP. Switch a `prod` con un `wp post meta delete` o update.

---

## Hallazgos relevantes

### Vtiger 8.2 community — fieldnames numéricos para custom fields

Esperaba `cf_utm_source`, recibí `cf_853` (sequential numeric). Es comportamiento default. Aceptado (Opción A) — documentado en `integrations/vtiger/fields-mapping.md` con dictionary cf_NNN ↔ ERP.

### SureForms — sin block "Hidden" nativo

Confirmado revisando plugin source. Workaround: mu-plugin inyecta hidden inputs via JS al renderear (defense-in-depth pattern, estándar). Cero modificación al form 1569.

### SureForms `srfm_before_submission` payload format

Pasa array `['form_id' => N, 'data' => [<slug> => <value>]]` con keys = SLUGS (`text-field`, `email`, `phone-number`, `dropdown`). Mapping defensivo Pass 1 (exact) + Pass 2 (fuzzy) cubre 100% de casos validados.

### mu-plugin sin tracker JS poblando inputs requería ampliación

Primer test (URL limpia) reveló UTMs vacíos correctamente, pero `event_id` + `landing_url` también vacíos — eso indicó que GTM no toca los inputs. Fix: JS inline en mu-plugin puebla todos los inputs autonomously.

### Picklist Vtiger vs dropdown WP form — gap a alinear

Form 1569 tiene "Plasma Rico en Plaquetas" (full name); Vtiger picklist tiene "PRP" (abbreviation). Si un usuario submitea "Plasma Rico en Plaquetas" → Vtiger lo guarda raw → queries por "PRP" canónico no matchean. Backlog item agregado.

### Auto-cleanup Vtiger soft-delete

Vtiger DELETE via REST API marca `vtiger_crmentity.deleted = 1` (soft delete). Lead no aparece en UI lists pero sigue en DB. Para hard delete habría que tocar tabla directamente (no recomendado — perdés audit trail Vtiger).

### Inventory de skills/agentes era cabo suelto explícito

Dario detectó que yo no estaba tracking sistemáticamente "lo que construyo → qué agente lo usa". Falla de coherencia con el plan organizacional documentado meses atrás. Fix: memoria `project_agent_skills_inventory.md` + check explícito en runbook cierre-sesion § 8 (OBLIGATORIO).

---

## Lo que queda pendiente

### Mini-bloque 3.4 — CAPI server-side desde ERP (próxima sesión)

- ADR-0019 v1.0 (decisión definitiva: ¿desde ERP o desde n8n?)
- Decisión Meta App Review (formal) o saltar Meta del audit programático
- Endpoint en ERP que emite Lead/Schedule/Purchase a Meta CAPI con event_id deduplicado
- Decisión sobre anuncio Meta €2/día activo
- Custom Audience: subir 134 clientes existentes a Meta como Lookalike base

**Estimado:** 2-3 sesiones.

### Mini-bloque 3.5 — Observabilidad

- Metabase dashboards leads (4 dashboards: diarios + funnel + cohort + CAC)
- Fix sensor VPS 2 unhealthy flag + sensor VPS 1 Docker WARNING
- Cron recolector cross-VPS de system-map JSON (instalación pendiente desde Bloque 0.4)
- Brain re-indexing automatic (cron + webhook GitHub)
- Alertas n8n sobre disk/RAM/costos cuando exceden umbrales

**Estimado:** 2-3 sesiones.

### Bloque puente Agenda (entre F3 y F4)

- ADR cerrado para tabla `appointments` + módulo
- Migration Alembic 0007 — `appointments` table + `clientes.first_touch_attribution` JSONB
- Endpoints CRUD + UI doctora
- Integration con tracking_emitter (Schedule + CompleteRegistration → CAPI)
- Tests pytest ≥85% del módulo nuevo
- Validación con doctora real

**Estimado:** 3-4 sesiones.

### Picklist Vtiger cf_875 alignment con form WP 1569

Backlog item con detalle. Antes de F4 (Conversation Agent que dependerá de tratamiento_interes para routear).

---

## Próxima sesión propuesta

**Mini-bloque 3.4 — CAPI server-side**

Aplicar runbook `preflight-cross-system.md` (≥2 sistemas: ERP + Meta APIs + n8n).

Sub-pasos esperados:
1. Decisión Meta App Review (Opción B saltar audit, o Opción A/C iniciar review)
2. ADR-0019 v1.0 cerrado (CAPI emitter en ERP vs n8n)
3. Endpoint ERP `/api/internal/capi-emit` (interno) con schema Pydantic + auth
4. Tests pytest TDD primero
5. Hook auto-emit al crear venta (Purchase event)
6. Hook auto-emit al crear lead (Lead event vía sync-from-vtiger trigger)
7. Smoke test productivo + verificación en Meta Events Manager

Pre-requisito tuyo: revisar las opciones Meta App Review en backlog y decidir Opción A/B/C antes del primer commit.

---

## Próximo paso opcional antes del 3.4

**Test parcial manual end-to-end** (~30 min) — Opción C aprobada hoy:
1. Submit form → Vtiger Lead → ERP `leads` (✅ ya validado)
2. Manualmente: convert lead a cliente desde Vtiger UI o ERP
3. Crear venta + pago en ERP `/legacy/venta-create`
4. Verificar audit log + chain end-to-end

Esto valida 60-70% del flow completo manual sin bloquear el avance hacia 3.4.

---

## Referencias

- `infra/wordpress/mu-plugins/livskin-form-to-n8n.php` — mu-plugin completo
- `infra/n8n/workflows/A-acquisition/a1-form-submit-to-vtiger-lead.md` — workflow [A1]
- `infra/n8n/workflows/B-bridge/b1-vtiger-lead-changed-to-erp-mirror.md` — workflow [B1]
- `infra/n8n/workflows/B-bridge/b3-vtiger-modified-cron-pull.md` — workflow [B3]
- `infra/docker/erp-flask/routes/api_leads_sync.py` — endpoint Flask
- `infra/docker/alembic-erp/migrations/versions/2026_04_29_2200-0006_capi_match_quality.py` — migration 0006
- `integrations/vtiger/fields-mapping.md` — diccionario cf_NNN ↔ ERP
- `docs/runbooks/wordpress-form-livskin-integration.md` — runbook integración forms (NUEVO)
- `docs/runbooks/vtiger-custom-fields.md` — runbook custom fields Vtiger
- Memoria `project_agent_skills_inventory.md` — inventory vivo (NUEVO)
- Memoria `feedback_commit_approval_explicit.md` — protocolo commits (NUEVO)
- ADR-0011 v1.1, ADR-0015, ADR-0030 — autoritativas
- Backlog § "Hecho" — entry detallada del 3.3 REWRITE

**Commits referencia:** `00d7a60` `1741fdc` `69a2d01` `2918bb7` `86073c0` `53fe70f` + commit cierre.
