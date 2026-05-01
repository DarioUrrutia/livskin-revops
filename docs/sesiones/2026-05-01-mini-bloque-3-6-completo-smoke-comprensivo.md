# 2026-05-01 — Mini-bloque 3.6 completo + smoke comprehensivo + arquitectura atribución end-to-end

## Contexto inicial

Sesión continuada del cierre 2026-05-01 mañana (Mini-bloque 3.4 ✅ + ADR-0031 cerrado). Plan: ejecutar Mini-bloque 3.6 — Landings dedicadas Cloudflare Pages + sistema convenciones reutilizable.

## Qué se hizo

### Fase 1 — Mini-bloque 3.6 (sub-pasos 3.6.1 al 3.6.10)

Construcción del sistema completo de landings dedicadas:

- `_shared/conventions.md` v1.0 — contrato HTML markup que toda landing debe seguir
- `_shared/livskin-tracking.js` — script standalone que lee DOM via convenciones, intercepta forms + WA clicks, dispara Pixel + POST a n8n [A1]
- `_shared/livskin-config-schema.json` — JSON Schema Draft-07 validador
- `_template/` — landing minimal funcional (HTML + config) como referencia
- `botox-mvp/` — primera landing real migrada al sistema (rename `landing.html`→`index.html` + meta livskin-* + LIVSKIN_CONFIG)
- `.github/workflows/deploy-landings.yml` — pipeline build + validate JSON + deploy a `livskin-campanas` (CF Pages) + audit event ERP
- `docs/runbooks/landing-pages-deploy.md` — runbook ejecutable

Commit `ef431a7` consolida 3.6.1-3.6.9. CF Pages project + DNS `campanas.livskin.site` ya creados via API antes de la sesión (3.6.4) + CORS n8n configurado (3.6.6).

### Fase 2 — Smoke browser-side (3.6.10) + iteración del banner consent

Smoke 1 con Dario:
- Cookies UTM persistence ✅
- Pixel gated antes de consent ✅
- Pixel dispara post-consent ✅ (PageView 200, fbevents.js cargado, initiated by livskin-tracking.js:196)

Hallazgo: banner consent original era una franja inferior delgada poco visible. Dario comparó con el modal centrado de livskin.site WordPress (Complianz-like) y pidió rediseño.

Iteraciones:
- v1: banner inferior reforzado (rechazado — sigue siendo "barra abajo")
- v2: **modal centrado** con backdrop oscurecido, logo Livskin, 3 botones (Aceptar/Rechazar/Preferencias), ✕ cierre, animación scale-in. Aprobado.

Bug WhatsApp click: links del botox-mvp NO tenían `data-livskin-wa="true"` ni `target="_blank"`. Fix:
- `PinkCTA` componente JSX modificado para auto-detectar `wa.me|api.whatsapp.com` y agregar `data-livskin-wa="true"` + `target="_blank"` automáticamente
- 3 links WA directos (nav desktop, menu mobile, WAFloat) marcados explícitamente
- `livskin-tracking.js` también fuerza `target="_blank"` defensivamente en el handler

### Fase 3 — Bug 400 en POST WA click → HOTFIX live al workflow [A1]

Smoke browser-side reveló que POST a webhook devolvía 400 `phone_invalid` para WA clicks (phone vacío by design).

Diagnóstico: workflow [A1] nodo `Validate Phone` rechaza payloads con phone empty. Necesita rama condicional para `_source: "wa-click"`.

Fix WA_CLICK_PATCH_v1.1 aplicado live:
- `Validate Phone`: acepta phone vacío si `_source==='wa-click'`
- `Decide Create or Existing`: short-circuit ANTES de validar query Vtiger (la query con phone='' devuelve INTERNAL_SERVER_ERROR de Vtiger; ignorar para wa-click)
- `Build CREATE payload`: `phone=''`, `leadsource='WA Direct Click'`, descripción distintiva. Attribution UTMs (cf_853-cf_875) preservada intacta.

Aprendizaje técnico crítico (memoria nueva): **n8n 2.x carga workflows desde `workflow_history.nodes`, NO desde `workflow_entity.nodes`**. Patches via SQL deben actualizar AMBAS tablas. La primera tentativa solo modificó `workflow_entity` y no surtió efecto. También hubo corrupción accidental de la DB SQLite por copiar fuera del volumen — recuperamos desde backup pre-patch.

Validación E2E: Lead test `10x9` creado en Vtiger correctamente con todos los UTMs persistidos. Después borrado.

### Fase 4 — Auto-deploy CI rotura + reparación

Push del commit grande disparó workflow `deploy-landings.yml` que falló en step 8 (`wrangler pages deploy`). Investigación cascada:

1. Hipótesis 1: secret `CLOUDFLARE_ACCOUNT_ID` mal configurado → hardcoded en yml (account_id es identificador público no sensible)
2. Re-run falla. Hipótesis 2: token. Verificación local: token de `keys/.env.integrations` SÍ funciona vía CF API directa. Falla específica en GH Actions runner.
3. Re-run falla con error real (vía screenshot logs Dario): `Wrangler requires at least Node.js v22.0.0. You are using v20.20.2`. Causa raíz: `wrangler@latest` bumpeó Node requirement. Fix: `node-version: "22"` + pin `wrangler@4.87.0`.
4. Re-run falla otra vez: `ERROR: Not logged in`. Token no llega al runner. Diagnostic step temporal agregado al yml: detectó token de **38 chars** (debería ser 53) — Dario pegó solo parte del token al copiar del editor (line wrap).
5. Dario re-pegó token completo via PowerShell (53 chars). Re-run final → **SUCCESS**. Diagnostic step removido.

5 commits del cierre 3.6: `ef431a7` (build inicial), `cff7a0a` (modal v2 + WA + A1 patch), `a5419c8` (hardcode account_id), `3138577` (Node 22 + wrangler pin), `98f4327` (cleanup diagnostic).

### Fase 5 — Smoke comprehensivo del journey "anuncio → paga"

Dario pidió tests más diversos en lugar de cerrar con bugs documentados en backlog. Plan: arreglar primero los 2 hallazgos del smoke previo, después correr 16 tests con condiciones explícitas.

**FASE A — arreglos previos:**

A.1. **Hallazgo 1 (WA-click → ERP gap)**: decisión arquitectónica Op B. Workflow [B3] modificado vía SQL UPDATE (script `scripts/patch_b3_skip_wa_click.py`): `Map Vtiger to ERP Schema` retorna `[]` cuando `leadsource === "WA Direct Click"`. Patch B3_SKIP_WA_CLICK_v1 aplicado a `workflow_entity` Y `workflow_history` (lección aprendida del A1). Verificado live.

A.2. **Hallazgo 2 (sensor cron no instalado)**: cron `*/5 * * * *` collect + `23 3 * * *` cleanup instalado en VPS3 ejecutando `docker exec erp-flask python -m services.infra_snapshot_service collect`. Verificación: 3 VPS reportando samples fresh (`livskin-wp`, `livskin-ops`, `livskin-erp` con timestamp 21:32:50).

**FASE B — 16 tests smoke con condiciones explícitas:**

| # | Cobertura | Resultado |
|---|---|---|
| 1-4 | Landing carga (Meta+Google+orgánico+JS asset) | ✅ |
| 5 | CORS preflight n8n desde campanas.livskin.site | ✅ |
| 6-7 | POST form happy path (Meta + Google attribution) | ✅ leads 10x12+10x13 |
| 8 | Phone normalization local→E.164 | ✅ `987654300` → `+51987654300` |
| 9 | Phone inválido rechazado | ✅ HTTP 400 |
| 10 | Dedup mismo phone 2x | ✅ `is_new:false`, mismo lead_id |
| 11 | WA-click sin phone (post-patch v1.1) | ✅ lead 10x15 con `leadsource="WA Direct Click"` |
| 12 | JSON malformado | ✅ HTTP 422, no crash |
| 13 | Attribution preservada Vtiger (10 campos) | ✅ 10/10 OK |
| 14 | Phone normalization en Vtiger storage | ✅ |
| 15 | Consent flag persistido | ⚠️ gap diseñado para 3.7+ |
| 16 | ERP sync E2E + Op B filter | ⚠️ race condition (1 de 3 form leads sincronizó por ciclo cron) |

**Cleanup**: leads test `10x9, 10x10, 10x11, 10x12, 10x13, 10x14, 10x15` borrados de Vtiger + ERP.

### Fase 6 — Decisión arquitectónica clave: cómo el chatbot Fase 4 cierra el círculo de atribución

Dario identificó (preguntando) que el "gap" de Op B (WA click leads sin phone no son operacionales en ERP) **se cierra automáticamente cuando llegue Fase 4 — Conversation Agent**. Razón:

WhatsApp Cloud API expone `from: <phone E.164>` en el primer mensaje del visitante. Cuando el chatbot recibe ese mensaje, hace tool call `vtiger_search_lead_by_event_id(event_id)` (extraído del mensaje pre-poblado que appendea livskin-tracking.js a la URL WA), y enriquece ese Vtiger Lead con phone real.

A partir de ahí: chatbot conversa → agenda cita → ERP crea cliente con phone match → ERP dispara CAPI Purchase con MISMO `event_id` → Meta dedup → atribución full-funnel cerrada **sin intervención humana**.

Esto refuerza Op B como decisión correcta. El "gap" es temporary by design — chatbot lo cierra en Fase 4.

Memoria nueva con el modelo completo creada (`project_attribution_chain_event_id.md`).

## Decisiones tomadas

1. **Op B (WA-click leads viven solo en Vtiger)** — decisión arquitectónica final. ERP solo recibe leads operacionales (con phone). Vtiger es source of truth marketing journey. Workflow [B3] filtra `leadsource="WA Direct Click"` del sync.

2. **Banner consent = modal centrado** (no banner inferior). Compliance-first sobre UX agresiva. Validado browser-side.

3. **Hardcode account_id en deploy-landings.yml** — identificador público, evita dependencia de secret frágil.

4. **Pin wrangler version en CI** — `wrangler@4.87.0` (no `@latest`) para evitar breaks por bumps de Node-version requirement.

5. **El `event_id` UUID es el hilo conductor end-to-end de atribución** — anuncio → click → Pixel Lead → POST n8n → Vtiger Lead cf_871 → (Fase 4) chatbot lee → ERP cliente → CAPI Purchase con mismo event_id → Meta dedup full-funnel.

## Hallazgos relevantes

1. **n8n 2.x workflow_history vs workflow_entity** — n8n carga desde `workflow_history.nodes` para ejecutar webhooks; `workflow_entity.nodes` es solo snapshot. Patches via SQL DEBEN tocar ambas tablas.

2. **n8n DB modification safety** — copiar `database.sqlite` fuera del volumen del container y modificar con sqlite3 desde el host CORROMPE la DB (perdimos n8n DB por esto, recuperamos desde `/tmp/dbcopy.sqlite` pre-corrupción). El método correcto es alpine sidecar con `--volumes-from n8n` que monta el volumen y modifica in-place.

3. **B3 race condition** — cron cada 2 min con lookback 3 min procesó solo 1 de 3 form leads creados en mismo ventana. Causa raíz pendiente investigar (posible: n8n batch processing serial detenido en error silencioso, o split items con race en Vtiger query response). HOTFIX bajo investigación para próxima sesión.

4. **CF token GitHub secret frágil** — pegado parcial (38 chars de 53) por wrap visual del editor. Diagnostic step en CI agregando length+prefix check capturó el bug sin exponer el token. Patrón reusable para futuros secrets.

5. **wrangler@latest es inestable en CI** — bump silencioso de Node requirement rompe builds. Pin obligatorio en pipelines.

## Lo que queda pendiente

1. **HOTFIX B3 race condition** — investigar por qué solo 1 de N leads se sincroniza por ciclo. Puede ser `continueOnFail` no seteado, o split items con race. Severidad media (en producción sin smoke, leads quedan sin attribution en ERP por algunos minutos hasta próximo cron).

2. **WhatsApp Business API approve** — pendiente trámite Meta (5-10 días). Bloqueante para Fase 4 Conversation Agent.

3. **Consent flag persist a Vtiger** — gap diseñado, push a Mini-bloque 3.7+ cuando se decida exponerlo (compliance audit posibles).

4. **Backlog limpio** — entradas antiguas a re-priorizar.

## Próxima sesión propuesta

**Mini-bloque 3.5 — Observabilidad + Metabase dashboards** (cierra Fase 3).

Objetivos:
- Dashboards Metabase básicos: leads/day por canal, attribution waterfall (anuncio→lead→cliente→venta), CAPI match quality scores, Vtiger lead source distribution.
- Conexión Metabase ↔ Postgres ERP + analytics.
- Alertas básicas (zero leads en 24h, CAPI failures).
- Validación que infra_snapshots sensor data sirva para dashboards de health (ahora que el cron está instalado).
- Pre-flight obligatorio (preflight-cross-system.md).

**Tiempo estimado**: 4-6h.

**Pre-requisito**: HOTFIX B3 race condition resuelto (15-30 min al arrancar la sesión, antes del 3.5).

Con 3.5 cerrado, **Fase 3 al 100%**. El siguiente bloque es el Bloque puente Agenda Mínima ERP (módulo `appointments`) entre Fase 3 y Fase 4.
