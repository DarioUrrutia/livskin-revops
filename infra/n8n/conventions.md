# Convenciones n8n — autoritativas

Este doc codifica el sistema de organización de workflows n8n. Aplica a cualquier workflow nuevo a partir del 2026-04-29 (Mini-bloque 3.3 REWRITE).

---

## 1. Categorías canónicas (8)

Cada workflow pertenece a UNA categoría. La categoría define propósito + fase típica del roadmap + dirección del flujo de datos.

| Letra | Nombre | Propósito | Sistemas tocados típicos | Fase |
|---|---|---|---|---|
| **A** | **Acquisition** | Captura de leads desde canales externos hacia Vtiger | WP form / WA inbound → n8n → Vtiger | F3+ |
| **B** | **Bridge** | Sync read-mostly entre Vtiger ↔ ERP | Vtiger → n8n → ERP / ERP → n8n → Vtiger | F3+ |
| **C** | **Conversion** | Lifecycle lead → cliente (transición digital→físico) | ERP venta → n8n → Vtiger lead status update | F6+ |
| **D** | **Dialogue** | Conversation Agent flow (WA in/out + Claude API) | WA → n8n → Claude API → WA | F4+ |
| **E** | **Engagement** | Nurture drip + handoff doctora | n8n cron → WA template + WhatsApp notification doctora | F4+ |
| **F** | **Feed** | ETL analytics (ERP/Vtiger → Metabase) | ERP → n8n → Metabase analytics views | F3.5 / F5 |
| **G** | **Growth** | Audiences sync + outbound a plataformas ads | ERP → n8n → Meta/Google APIs | F5 |
| **H** | **Health** | Monitoring + alertas (disk, RAM, costos, downtime) | n8n cron → check VPS → WA alert si excede umbral | F6 |

---

## 2. Naming de workflow (en n8n UI)

```
[<Letra><Numero>] <Verbo en infinitivo> <Objeto> → <Destino>
```

**Componentes:**
- **`[A1]`** — letra de categoría + número secuencial dentro de la categoría (zero-padded NO, naturales: A1, A2, A10, A11)
- **Verbo** — qué hace el workflow (Capturar / Espejar / Sync / Procesar / Despachar / Marcar / Monitor)
- **Objeto** — qué dato/evento se procesa
- **Destino** — sistema o estado final

**Ejemplos correctos:**
- `[A1] Capturar Form Submit → Vtiger Lead`
- `[B1] Espejar Vtiger Lead Changed → ERP Mirror`
- `[B2] Marcar ERP Cliente Created → Vtiger Lead Converted`
- `[D1] Procesar WhatsApp Inbound → Conversation Agent`
- `[E2] Notificar Score ≥70 → Doctora WhatsApp`
- `[F1] Sync ERP Daily → Metabase Cube`
- `[G3] Despachar ERP Conversion → Meta CAPI`
- `[H1] Monitor Disk + RAM → WhatsApp Alert`

**Ejemplos incorrectos:**
- ❌ `Workflow 1` (sin categoría, sin propósito)
- ❌ `[A] Form to Vtiger` (sin número)
- ❌ `[A1] form-submit-vtiger` (kebab-case en n8n UI; el kebab-case va en filename, NO en el label de UI)
- ❌ `[A1] Form Submit and create Vtiger Lead` (sin → flecha que separa input de output)

---

## 3. Numeración

- Números **secuenciales por categoría**, no globales
- **Inmutables una vez creados** — si un workflow se descarta, su número NO se reutiliza (deja gap)
- **Sin zero-padding** — `A1` no `A01` (consistente con n8n práctica común)
- Cuando el workflow se rediseña significantemente: subimos a `A1.v2` en label UI (mismo número, sufijo). El JSON file se mantiene como `A1-...` con changelog interno.

---

## 4. Webhook URLs

Para workflows con trigger Webhook:

```
https://flow.livskin.site/webhook/<categoria-en-ingles>/<nombre-kebab>
```

**Categoría en URL = en inglés** (estandar internacional + alineado con la letra):
- `acquisition`, `bridge`, `conversion`, `dialogue`, `engagement`, `feed`, `growth`, `health`

**Nombre = kebab-case del propósito**

**Ejemplos:**
- `[A1]` → `/webhook/acquisition/form-submit`
- `[A2]` → `/webhook/acquisition/whatsapp-inbound`
- `[B1]` → `/webhook/bridge/vtiger-lead-changed` (recibe webhook de Vtiger)
- `[B2]` → `/webhook/bridge/erp-cliente-converted`
- `[D1]` → `/webhook/dialogue/whatsapp-inbound` (puede coincidir con A2 si comparten endpoint — caso real, evaluar)
- `[G3]` → (no expone webhook — se dispara desde ERP via internal n8n trigger)

**Reglas:**
- URLs **inmutables** una vez expuestas (rompe integraciones externas si cambian)
- Si necesitás reemplazar un workflow, mantén la misma URL del workflow viejo y deshabilita el viejo

---

## 5. Folder structure del repo

```
infra/n8n/
├── README.md          ← overview + index
├── conventions.md     ← este doc
└── workflows/
    ├── A-acquisition/
    │   ├── A1-form-submit-to-vtiger-lead.json
    │   ├── A1-form-submit-to-vtiger-lead.md
    │   ├── A2-whatsapp-inbound-to-vtiger-lead.json    (futuro)
    │   └── A2-whatsapp-inbound-to-vtiger-lead.md
    ├── B-bridge/
    │   ├── B1-vtiger-lead-changed-to-erp-mirror.json
    │   ├── B1-vtiger-lead-changed-to-erp-mirror.md
    │   ├── B2-erp-cliente-converted-to-vtiger.json
    │   └── B2-erp-cliente-converted-to-vtiger.md
    ├── C-conversion/
    ├── D-dialogue/
    ├── E-engagement/
    ├── F-feed/
    ├── G-growth/
    └── H-health/
```

**Naming de archivos:**
- `<id-minusculas>-<descripcion-kebab>.<json|md>`
- IDs en minúsculas (`a1` no `A1`) en filenames para evitar problemas con file systems case-insensitive
- `.json` = workflow exportable (importable a n8n)
- `.md` = doc humana (propósito + IO + errores + changelog)

---

## 6. Tags en n8n UI

Cada workflow se taggea con (mínimo):

| Tag | Valores posibles | Propósito |
|---|---|---|
| `categoria` | acquisition / bridge / conversion / dialogue / engagement / feed / growth / health | Filtro por tipo |
| `fase` | fase-3 / fase-4 / fase-5 / fase-6 | Filtro por roadmap |
| `criticidad` | critical / non-critical | Critical = si falla, rompe negocio. Non-critical = degrada función pero no la rompe |
| `estado` | production / staging / experimental | Production = vivo. Staging = en validación. Experimental = work in progress |

**Ejemplo combinado para [A1]:**
```
acquisition + fase-3 + critical + production
```

---

## 7. Doc por workflow (`.md`)

Cada workflow tiene un `.md` con esta estructura **mínima**:

```markdown
# [<ID>] <Nombre>

**Categoría:** <categoria>
**Fase:** <N>
**Criticidad:** <critical|non-critical>
**Estado:** <production|staging|experimental>
**Webhook URL:** <URL si aplica, o "no — trigger interno">

## Qué hace
<2-3 oraciones describiendo el flujo>

## Trigger
<webhook | cron <cuando> | trigger interno desde otro workflow>

## Input expected
<JSON schema o descripción>

## Output
<JSON schema o descripción>

## Sistemas tocados
- <sistema 1> (read|write)
- <sistema 2> (read|write)

## Errores conocidos
- <code> → <causa> → <fix>

## Cambios
- <fecha> v<X.Y> — <qué cambió>
```

---

## 8. Versionado de workflows

Cuando se modifica un workflow:

1. **Cambio menor (bugfix, optimización sin cambio de schema):** edit JSON + bump changelog en `.md`
2. **Cambio significativo (cambio de input/output, cambio de lógica):** crear `.v2.json` + nuevo `.md`. Activar v2, deshabilitar v1, eventualmente borrar v1.
3. **Reemplazo total:** mismo número + sufijo `.v2`, `.v3`, etc.

---

## 9. Convenciones de credenciales

Para credenciales sensibles (API keys, DB passwords, etc.):

**NO** hardcodear en el JSON del workflow. Opciones (en orden de preferencia):

1. **Env vars en n8n docker-compose** — exportar `VTIGER_API_ACCESSKEY`, `ERP_API_TOKEN`, etc. al container de n8n. Workflows referencían como `{{ $env.VTIGER_API_ACCESSKEY }}`.
2. **n8n Credentials feature** — UI permite crear "credenciales" reutilizables. n8n las encripta con la `encryptionKey` del config.
3. **Secrets de Cloudflare/Vault** — fuera de scope hoy, evaluable en F6.

**Convención adoptada hoy: Opción 1 (env vars).** Razón: simple, audit clear (env vars visibles via `docker inspect`), reproducible (env vars vienen de `keys/.env.integrations` gitignored).

---

## 10. Cómo desarrollar (flujo recomendado)

1. **Diseñar localmente:** escribir el `.md` PRIMERO con propósito + IO + sistemas + errores
2. **Construir JSON:** ya sea
   a. Manual en n8n UI → exportar con `n8n export:workflow --id=N --output=...`
   b. Escribir JSON desde plantilla en este repo
3. **Documentar el JSON exportado en `.md`** con el schema visible
4. **Smoke test:** importar a n8n staging-tagged → curl manual al webhook → verificar execution log
5. **Promover a production:** cambiar tag `staging` → `production` en n8n UI
6. **Actualizar `infra/n8n/README.md`** moviendo el workflow al estado correcto

---

## 11. Cuándo reabrir esta convención

- Si surge categoría nueva no cubierta por las 8 letras → agregar (mantener orden alfabético, no reasignar letras existentes)
- Si llegamos a >50 workflows totales → posible refactor a sub-categorías (`B.1`, `B.2`)
- Si n8n upgrade cambia el formato de export → actualizar instrucciones del paso 10.2.a

---

## Cross-references

- `infra/n8n/README.md` — index vivo de todos los workflows
- Memoria `project_n8n_orchestration_layer.md` — manifiesto operativo
- ADR-0030 — file naming conventions del repo (alinea con convenciones acá)
