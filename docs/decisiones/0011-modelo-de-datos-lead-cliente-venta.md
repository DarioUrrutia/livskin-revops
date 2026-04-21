# ADR-0011 — Modelo de datos Lead / Cliente / Venta / Pago / Gasto

**Estado:** ✅ Aprobada (MVP v1.1)
**Fecha:** 2026-04-21 (v1.1)
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos

---

## 1. Contexto

Fase 2 requiere un modelo de datos que:
- Reemplace Google Sheets (DB actual del ERP Flask en Render) por Postgres en VPS 3
- Preserve la UX actual del formulario (comerciales ya saben usarlo — ADR-0023)
- Agregue capacidad de atribución digital (UTMs, consent, fuente) — hoy inexistente porque los 135 clientes existentes vinieron 100% por word-of-mouth
- Escale a flujos de adquisición digital vía Vtiger CRM + Conversation Agent (Fases 3-5)
- No sobre-ingeniería: profesional de RevOps pero no complejo innecesariamente

**Data real analizada** (2026-04-21):
- 5 hojas operativas en Google Sheets: Ventas (77 filas), Pagos (73), Clientes (135), Gastos (vacía), Listas (catálogos)
- Entidades actuales: Cliente, Venta (aplanada 1-fila = 1-item), Pago (4 tipos), Gasto
- Flujos de negocio densos: 6 fases de guardado de venta, distribución proporcional de pagos, manejo de créditos/deudas/abonos

Referencias:
- Plan maestro § 6.2 (arquitectura de datos), § 11.4 (Fase 2)
- ADR-0002 (3 VPS + VPC)
- ADR-0015 (Source of Truth por dominio — ya aprobada)
- ADR-0023 (ERP refactor Flask — dependiente de este dossier)
- Memory `project_erp_migration` (principios establecidos 2026-04-21)

---

## 2. Opciones consideradas

### Opción A — Replicar estructura actual del Flask 1:1 en Postgres, agregar columnas de atribución

Cada hoja de Sheets = una tabla en Postgres con mismo nombre de columnas (normalizado a snake_case). Las entidades se preservan tal cual las maneja el Flask hoy, incluyendo "Venta aplanada" (1 fila = 1 item). Se agregan columnas nuevas (fuente, UTMs, consent, timestamps) con default NULL para registros históricos.

### Opción B — Rediseñar a modelo normalizado (Venta header + ItemVenta líneas)

Separar la venta en header (info de transacción, cliente, fecha, totales) y líneas (items individuales). Modelo más limpio y flexible.

### Opción C — Modelo híbrido con vistas

Tabla física aplanada (como A) + vistas SQL que presentan estructura normalizada (como B) para queries analíticas.

---

## 3. Análisis de tradeoffs

| Dimensión | A (replicar + extender) | B (normalizar) | C (híbrido con vistas) |
|---|---|---|---|
| Costo | — | — | — |
| Complejidad implementación | Baja | Alta (refactor lógica Flask 6 fases) | Media (migrations + vistas + mantener ambas) |
| Complejidad mantenimiento | Baja | Media | Alta (dos representaciones a mantener sincronizadas) |
| Tiempo | 2-3 días | 1-2 semanas | 1 semana |
| Riesgo de romper producción | Bajo | Alto (rewrite de lógica de negocio) | Medio |
| Reversibilidad | Alta | Baja | Media |
| Escalabilidad futura | Media (refactor a normalizado siempre posible) | Alta | Alta |
| Alineación principios operativos | **Alta** (1, 5, 9) — ejecutable > ideal | Baja (viola principio 1 en MVP) | Media |

---

## 4. Recomendación

**Opción A — Replicar 1:1 y extender.**

Razones:
1. **Preserva el frontend y la lógica de negocio del Flask** — el refactor es de storage engine, no de producto. Alinea con principio 6 (respeto al equipo humano) y el mandato explícito de Dario (2026-04-21).
2. **MVP-speed** — llegamos a flujo end-to-end con data sintética en semanas, no meses. Alinea con principio 1.
3. **Reversibilidad** — si en Fase 5+ aprendemos que necesitamos ItemVenta normalizado, es un refactor de backend puro (no toca el form HTML). Alinea con principio 5.
4. **Postgres + FKs + índices compensan "aplanado"** — queries analíticas seguirán siendo rápidas con índices apropiados y vistas SQL materializadas si hacen falta.

**Tradeoff aceptado:** mantenemos el "1-venta-1-item aplanado" que no es óptimo académicamente. Lo aceptamos porque la lógica de negocio del Flask (crédito aplicado, distribución proporcional de pagos, abono deuda anterior) asume esta estructura y refactorizarla rompería productividad comercial en el cutover.

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-21 por Dario.

**Razonamiento de la decisora:**
> "El frontend se preserva estricto porque los comerciales ya saben usarlo. Backend tiene que acoplarse a nuestras necesidades sin sobre-complicar. Esto debe escalar con el tiempo pero no ser algo ultra-complejo ahora."

---

## 6. Modelo de datos MVP — esquema lógico

### Entidades core (7 — revisado v1.1)

```
┌──────────────────┐            ┌──────────────────┐
│      Lead        │            │     Cliente      │
│  SoT: Vtiger     │──convert──►│  SoT: ERP Postgres│
│  (replica en     │            │  (master de TODOS │
│   Postgres leads)│            │   los humanos que │
└────┬─────────────┘            │   compraron —     │
     │                          │   walk-ins, ref., │
     │                          │   digitales, +135 │
     │                          │   históricos)     │
     │                          └──────────┬───────┘
     │ touchpoints (N por lead)             │ cod_cliente (FK)
     ▼                           ┌──────────┼──────────┐
┌────────────────┐               ▼          ▼          ▼
│ lead_touch-    │         ┌──────────┐┌─────────┐┌────────┐
│   points       │         │  Venta   ││  Pago   ││ Gasto  │
│ (cada captura) │         │  (flat)  │◄┤(4 tipos)││(sin FK │
└────────────────┘         │          │ │         ││cliente)│
                           └──────────┘ └─────────┘└────────┘
┌────────────────┐
│form_submissions│ ──► alimenta leads + lead_touchpoints
│ (raw form data)│
└────────────────┘
```

**Correción v1.1**: Cliente SoT = ERP Postgres (NO Vtiger como decía v1.0). Vtiger solo conoce clientes que vinieron vía funnel digital — los 135 históricos word-of-mouth NUNCA entran a Vtiger. Ver memoria `project_vtiger_erp_sot` + ADR-0015.

### Tablas en Postgres `livskin_erp`

Convenciones (ADR-0014):
- Nombres de tabla en `snake_case` plural
- Columnas en `snake_case`
- PKs autogeneradas (`id bigserial`) + código natural `cod_xxx` con índice único
- `created_at`, `updated_at` (timestamptz) en todas
- `created_by`, `updated_by` (FK users) una vez exista auth (ADR-0026)

#### Tabla `leads` (SoT: Vtiger; replica en Postgres para lookups cross-system y analytics)
| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| cod_lead | text unique | formato `LIVLEAD####`, generado por Vtiger |
| vtiger_id | text | ID del lead en Vtiger (para sync bidireccional) |
| nombre | text not null | |
| phone_e164 | text not null | **required** — identifier anchor universal (ADR-0013 v2); normalizado a E.164 |
| email_lower | text | lowercase + trim |
| email_hash_sha256 | text | para Meta CAPI / Google Enhanced Conversions |
| fuente | text | valores ADR-0014: `meta_ad`, `instagram_organic`, `facebook_organic`, `google_search`, `google_ad`, `form_web`, `whatsapp_directo`, `referido`, `walk_in`, `otro`, `organico` |
| canal_adquisicion | text | `paid`, `organic`, `referral`, `walk_in`, `direct`, `legacy` |
| utm_source_at_capture | text | first-touch, inmutable |
| utm_medium_at_capture | text | |
| utm_campaign_at_capture | text | |
| utm_content_at_capture | text | |
| utm_term_at_capture | text | |
| fbclid_at_capture | text | |
| gclid_at_capture | text | |
| tratamiento_interes | text | picklist (botox, prp, ácido_hialurónico, ...) |
| consent_marketing | boolean | default false |
| consent_date | timestamptz | |
| fecha_nacimiento | date | opcional — solo si form lo pide |
| **estado_lead** | text | `nuevo`, `contactado`, `agendado`, `asistio`, `cliente`, `perdido` (ver ADR-0012) |
| fecha_captura | timestamptz | |
| **score** | integer default 0 | 0-100, rules-based v1 (ADR-0029 Conversation Agent) |
| **score_updated_at** | timestamptz | |
| **scoring_signals_json** | jsonb | señales detectadas (para auditar decisiones de score) |
| **intent_level** | text | `investigando`, `evaluando`, `listo_comprar`, `cold` |
| **nurture_state** | text | `inactivo`, `activo`, `pausado`, `handed_off` |
| **nurture_stream** | text | qué secuencia de drip está consumiendo |
| **handoff_to_doctora_at** | timestamptz | NULL si nunca hubo handoff |
| **handoff_status** | text | `pendiente`, `tomado`, `completado` |
| **handoff_notified_via** | text | `whatsapp`, `email`, `dashboard` |
| **es_reactivacion** | boolean default false | true si phone matcheó un Cliente existente (cliente histórico vuelve por digital) |
| cod_cliente_vinculado | text FK clientes | set cuando convierte (o al entrar si es reactivación) |
| created_at / updated_at | timestamptz | |

**Columnas nuevas en v1.1** (negritas): `score`, `score_updated_at`, `scoring_signals_json`, `intent_level`, `nurture_state`, `nurture_stream`, `handoff_to_doctora_at`, `handoff_status`, `handoff_notified_via`, `es_reactivacion`. Además renombrado `telefono` → `phone_e164` (ADR-0013) y `utm_*` → `utm_*_at_capture` (first-touch inmutable; per-touch se guarda en `lead_touchpoints`).

#### Tabla `clientes` (SoT: ERP Postgres — master de TODOS los humanos que compraron)
| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| cod_cliente | text unique not null | formato `LIVCLIENT####` (preservado del Flask) |
| nombre | text not null | |
| phone_e164 | text | normalizado (ADR-0013 v2) |
| email_lower | text | |
| email_hash_sha256 | text | para CAPI / Enhanced Conversions |
| fecha_nacimiento | date | |
| fecha_registro | date | preservada del Excel |
| fuente | text | default `organico` para los 135 existentes (word-of-mouth, ADR-0014) |
| canal_adquisicion | text | default `legacy` para históricos |
| utm_*_at_capture, fbclid_at_capture, gclid_at_capture | text | NULL para históricos; llenados desde Fase 3 para nuevos clientes digital-origin |
| tratamiento_interes | text | |
| consent_marketing | boolean | default false |
| consent_date | timestamptz | |
| notas | text | free text |
| cod_lead_origen | text FK leads | NULL para clientes pre-digital, se llena al convertir Lead→Cliente |
| vtiger_lead_id_origen | text | ID del Lead original en Vtiger (para debugging) |
| activo | boolean default true | soft-delete (ADR-0013 merge) |
| merged_to | bigint FK clientes | set cuando este cliente se mergea a otro (ADR-0013) |
| created_at / updated_at | timestamptz | |
| created_by / updated_by | bigint FK users | cuando exista auth |

#### Tabla `ventas` (flat, preservando estructura del Flask 1-fila-1-item)
| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| num_secuencial | integer | columna `#` del Excel (sequence per year si quieres) |
| fecha | date not null | |
| cod_cliente | text FK clientes not null | |
| cliente_nombre | text | desnormalizado por velocidad — validar contra clientes.nombre |
| cliente_telefono | text | idem |
| tipo | text not null | `Tratamiento`, `Producto`, `Certificado`, `Promocion` |
| cod_item | text not null | `LIVTRAT####` o `LIVPROD####` o `LIVCERT####` |
| categoria | text | valor de catálogo (`Botox`, `PRP`, etc.) |
| zona_cantidad_envase | text | multi-uso: zona para tratamientos, envase para productos |
| proxima_cita | date | |
| fecha_nac_cliente | date | desnormalizado (se llena desde clientes) |
| moneda | text default 'PEN' | |
| total | numeric(10,2) not null | |
| efectivo | numeric(10,2) | |
| yape | numeric(10,2) | |
| plin | numeric(10,2) | |
| giro | numeric(10,2) | |
| debe | numeric(10,2) | CALCULADO (ver abajo) — puede guardarse como denormalizado con cron semanal, pero SoT es `total - sum(pagos)` |
| pagado | numeric(10,2) | sum de los pagos aplicados |
| tc | numeric(10,4) | tipo de cambio si moneda != PEN |
| precio_lista | numeric(10,2) | |
| descuento | numeric(10,2) | default 0 |
| notas | text | |
| created_at / updated_at / created_by / updated_by | | |

**Nota importante sobre `debe`:** el valor canónico es calculado `total - sum(pagos.monto WHERE pago.tipo != 'credito_aplicado' AND pago.cod_item = ventas.cod_item)`. Puede materializarse en la tabla para queries rápidas en dashboards, pero la fuente de verdad son los pagos. Decidimos materializar con trigger AFTER INSERT/UPDATE en pagos (más simple que cron).

#### Tabla `pagos`
| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| num_secuencial | integer | |
| cod_pago | text unique not null | `LIVPAGO####` |
| fecha | date not null | |
| cod_cliente | text FK clientes not null | |
| cliente_nombre | text | desnormalizado |
| cod_item | text | FK lógico a ventas.cod_item (no FK duro porque podría ser abono de deuda sin venta asociada actual) |
| categoria | text | |
| monto | numeric(10,2) not null | |
| efectivo | numeric(10,2) | |
| yape | numeric(10,2) | |
| plin | numeric(10,2) | |
| giro | numeric(10,2) | |
| tipo_pago | text not null | `normal`, `credito_generado`, `credito_aplicado`, `abono_deuda` (preservado del Flask) |
| notas | text | |
| created_at / ... | | |

#### Tabla `gastos`
| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| num_secuencial | integer | |
| fecha | date not null | |
| tipo | text | |
| descripcion | text | |
| destinatario | text | |
| monto | numeric(10,2) not null | |
| metodo_pago | text | |
| notas | text | |
| created_at / ... | | |

#### Tabla `lead_touchpoints` (nueva v1.1 — multi-touch tracking, ADR-0013 v2)

Un lead puede tener N encuentros en el tiempo. Cada captura (form o WA) es un touchpoint. Permite first-touch vs last-touch attribution + reconstrucción del customer journey.

| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| lead_id | bigint FK leads NOT NULL | |
| canal | text NOT NULL | `form_web`, `whatsapp_cloud_api` |
| landing_url | text | URL de landing si vino de form |
| fecha_contacto | timestamptz NOT NULL | |
| utm_source | text | snapshot de ese touch específico (no at_capture) |
| utm_medium | text | |
| utm_campaign | text | |
| utm_content | text | |
| utm_term | text | |
| fbclid | text | |
| gclid | text | |
| primer_mensaje | text | solo WA: texto del primer msg (intent signal) |
| form_data_json | jsonb | solo form: snapshot completo de respuestas |
| ip | inet | server-side |
| user_agent | text | server-side |
| session_id | text | cookie first-party de UTM persistence (ADR-0021) |
| created_at | timestamptz | |

Índices: `(lead_id, fecha_contacto DESC)`, `(fecha_contacto)`, `(utm_campaign)`.

#### Tabla `form_submissions` (nueva v1.1 — raw audit trail de forms)

Almacena cada form submit ANTES de procesarlo (sirve como audit y permite reprocesar si falla el flujo lead+touchpoint).

| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| landing_slug | text | ej: `botox`, `prp` (nombre del landing) |
| landing_url_completa | text | URL con query string completa |
| phone_raw | text | crudo del form (pre-normalización) |
| phone_e164 | text | normalizado (puede ser NULL si inválido) |
| email_raw | text | |
| nombre_raw | text | |
| tratamiento_interes | text | |
| utm_source/medium/campaign/content/term | text | desde URL |
| fbclid | text | |
| gclid | text | |
| consent_marketing | boolean | |
| ip | inet | |
| user_agent | text | |
| referer | text | página anterior |
| fecha | timestamptz | |
| status | text | `received`, `processed`, `rejected_invalid_phone`, `rejected_spam` |
| lead_id | bigint FK leads | si se creó/vinculó lead |
| lead_touchpoint_id | bigint FK lead_touchpoints | si se creó touchpoint |
| error | text | si status=rejected o falló processing |
| created_at | timestamptz | |

Este audit trail es valioso para debugging y para reprocesar conversiones perdidas si n8n tiene downtime.

#### Tabla `dedup_candidates` (nueva v1.1 — casos ambiguos manuales, ADR-0013 v2 § 6.6)

Ver ADR-0013 v2 § 6.6 para estructura completa.

#### Tabla `catalogos` (reemplaza hoja Listas)
| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| lista | text not null | `tipo`, `cat_Tratamiento`, `cat_Producto`, `cat_Certificado`, `area`, `fuente`, `canal_adquisicion`, `metodo_pago` |
| valor | text not null | |
| orden | integer | display order |
| activo | boolean default true | para soft-delete de categorías descontinuadas |
| created_at / updated_at | | |

Índice único: `(lista, valor) WHERE activo = true`.

### Índices MVP mínimos

- `clientes(cod_cliente)` unique — existe por constraint
- `clientes(phone_e164)` — dedup cross-system (ADR-0013 v2)
- `clientes(email_lower)` — dedup secundario
- `clientes(lower(nombre))` — dedup case-insensitive fallback
- `leads(phone_e164)` — dedup cross-system (ADR-0013 v2)
- `leads(email_lower)` — dedup secundario
- `leads(estado_lead, score DESC)` — queries de handoff "próximos leads calientes"
- `leads(vtiger_id)` — sync bidireccional con Vtiger
- `lead_touchpoints(lead_id, fecha_contacto DESC)` — historial del lead
- `lead_touchpoints(utm_campaign)` — attribution per campaña
- `form_submissions(fecha, status)` — audit y retry
- `ventas(cod_cliente, fecha)` — dashboard queries
- `ventas(fecha)` — rango de fechas
- `pagos(cod_item)` — join con ventas para calcular debe
- `pagos(cod_cliente, fecha)` — historial por cliente
- `pagos(tipo_pago)` — filtros

### Qué se difiere explícitamente

- **ItemVenta normalizado** — reevaluar si surge necesidad de >5 items por "transacción" o si queries de ticket-promedio-por-visita se vuelven complejas
- **Inventario de productos** — diferido (plan maestro)
- **Historial clínico estructurado** — diferido (plan maestro)
- **Tabla `campanas`** — llega en Fase 5 con Acquisition Agent
- **Tabla `citas`** — vive en Vtiger Calendar (ADR separado si se decide replicar en Postgres)
- **Loyalty/puntos, referral rewards** — diferidos hasta evidencia de necesidad
- **Segmentación de clientes en tabla** — vienen como markdown notes (interludio estratégico entre Fase 3 y 4)

---

## 7. Consecuencias

### Desbloqueado
- ADR-0012 (Vtiger stages) puede definir mapeo `Lead → Cliente` con estados claros
- ADR-0013 (dedup) tiene columnas canónicas sobre las cuales operar
- ADR-0014 (naming) se escribe consolidando las convenciones ya plasmadas aquí
- ADR-0023 (ERP refactor) tiene modelo destino claro
- ADR-0025 (backfill) sabe qué tablas poblar y con qué datos del Excel
- Primera migration real en `alembic-erp/versions/0001_initial_schema.py`
- Layer 3 del cerebro puede crear vistas analíticas sobre este modelo

### Bloqueado / descartado
- Opción B (normalización venta/item) descartada para MVP — reabrir solo si Opción A demuestra fricción evidente
- No se crean tablas para dimensiones analíticas (star schema) — eso es Metabase-layer con views, no tablas físicas

### Implementación derivada
- [ ] Crear `alembic-erp/versions/0001_initial_schema.py` con todas estas tablas (Fase 2 semana 3): leads, clientes, ventas, pagos, gastos, catalogos, lead_touchpoints, form_submissions, dedup_candidates
- [ ] Refactor del `app.py` del Flask para usar SQLAlchemy sobre estas tablas (ADR-0023)
- [ ] Script de backfill sintético (ADR-0025) — mode=test poblando con 77 ventas + 135 clientes sintéticos; mode=real pullea Google Sheets live en cutover
- [ ] Configurar Vtiger: picklists (fuente, canal_adquisicion, tratamiento_interes, estado_lead), stages de ADR-0012, campos custom de ADR-0012 § 6
- [ ] Endpoint `/api/client-lookup?phone=X` en ERP Flask (ADR-0013 v2 § 6.4) — CRÍTICO para bridge digital→físico
- [ ] Webhook `/webhook/form-submit` en n8n con algoritmo de dedup v2 (ADR-0013)
- [ ] Webhook WhatsApp Cloud API → n8n con mismo algoritmo
- [ ] Normalizadores `normalize_phone`, `normalize_email`, `normalize_nombre` (Python + SQL)
- [ ] UI de revisión `dedup_candidates` en dashboard ERP
- [ ] Agregar vistas SQL analíticas en Fase 3 (revenue por fuente, cohort por mes, funnel conversion rate, no-show rate)
- [ ] Trigger AFTER INSERT/UPDATE en pagos para materializar `ventas.debe`

### Cuándo reabrir

- **Fricción evidente por Venta aplanada**: si tickets promedio tienen >3 items frecuentemente y los comerciales se quejan de duplicar cliente en cada fila
- **Volumen >5,000 ventas/año**: evaluar performance de queries; posible movida a ItemVenta normalizado
- **Nuevo canal de venta** (e-commerce, paquetes, suscripciones): requiere revisión del modelo
- **Compliance Ley 29733 / SUNAT facturación electrónica**: puede forzar campos nuevos o estructura diferente
- **Revisión trimestral obligatoria**: 2026-07-21

---

## 8. Changelog

- 2026-04-21 — v1.0 — Creada y aprobada (MVP Fase 2) — 5 entidades + SoT Vtiger=cliente (incorrecto)
- 2026-04-21 — v1.1 — **Actualizada en la misma sesión** tras clarificación estructural de Dario:
  - **SoT corregido**: Cliente master = ERP Postgres (no Vtiger). Vtiger tiene solo leads digitales. Los 135 históricos nunca entran a Vtiger. Ver memoria `project_vtiger_erp_sot`.
  - **2 tablas nuevas**: `lead_touchpoints` (multi-touch tracking, ADR-0013 v2) y `form_submissions` (raw audit de forms).
  - **Columnas nuevas en `leads`**: scoring (score, score_updated_at, scoring_signals_json), intent (intent_level), nurture (nurture_state, nurture_stream), handoff (handoff_to_doctora_at, handoff_status, handoff_notified_via), reactivación (es_reactivacion, cod_cliente_vinculado).
  - **Campos renombrados**: `telefono` → `phone_e164` (ADR-0013 v2), `utm_*` → `utm_*_at_capture` (first-touch inmutable).
  - **`clientes` actualizada**: agregado phone_e164, email_lower + email_hash_sha256, vtiger_lead_id_origen, activo, merged_to.
  - **Índices**: agregados para lead_touchpoints, form_submissions, queries de handoff.
  - **Implementación derivada expandida**: endpoint `/api/client-lookup`, webhooks n8n, normalizadores, trigger para `debe`.
  - Razón: simplificación tras realizar que Livskin tiene solo 2 canales de captura (form + WA) con phone como identifier universal + clarificación de Vtiger scope (marketing automation, no master de clientes).
