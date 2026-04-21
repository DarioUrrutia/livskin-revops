# ADR-0014 — Naming conventions (códigos, fuentes, campañas, UTMs)

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-21
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos

---

## 1. Contexto

Sistema con múltiples canales (WhatsApp, Meta Ads, forms, referencias) y múltiples sistemas (Vtiger, ERP, n8n, brain, Metabase) necesita vocabulario consistente. Sin convención, cada superficie inventa sus nombres → análisis imposible.

Livskin ya tiene convenciones parciales del Flask/Excel actual: `LIVCLIENT####`, `LIVTRAT####`, `LIVPRODxxxx`, `LIVPAGO####`. Las preservamos y extendemos.

Referencias:
- Plan maestro § 12.3 (Naming conventions — base)
- ADR-0011 (modelo de datos usa estos códigos)
- ADR-0012 (pipeline stages)

---

## 2. Opciones consideradas

### Opción A — Extender convención existente Livskin (`LIVXXXX####`)
Preservar patrón del Flask. Agregar nuevos: `LIVLEAD####`, `LIVCERT####`, `LIVCAMP####`, etc. Consistente con histórico.

### Opción B — Migrar a UUIDs en todas las entidades
PKs y códigos externos en UUID v4. Más robusto globalmente, no hay conflictos de secuencia en sistemas distribuidos.

### Opción C — Híbrido: UUIDs internos + códigos legibles `LIVXXXX####` para display
Mejor de ambos: UUID como PK técnico, `LIVCLIENT####` como código de negocio visible.

---

## 3. Análisis de tradeoffs

| Dimensión | A (`LIVXXXX####`) | B (UUIDs) | C (híbrido) |
|---|---|---|---|
| Continuidad histórica | **Alta** | Baja (reassign) | Alta |
| Legibilidad humana (form, tickets) | Alta | Baja | Alta |
| Complejidad backfill histórico | Muy baja | Alta | Media |
| Compatibilidad Flask actual | Total | Rompe | Compatible |
| Robustez ante sistema distribuido | Media (secuencia central) | Alta | Alta |
| Complejidad implementación | Baja | Media | Media |
| Overhead storage | Mínimo | +16 bytes por row | +16 bytes + extra columna |

---

## 4. Recomendación

**Opción A (extender `LIVXXXX####`) para MVP.**

Razones:
1. No rompe la data histórica del Excel ni el Flask actual
2. Comerciales ya están familiarizados (LIVCLIENT0099 en ticket = reconocible)
3. Livskin es single-site, single-DB — no hay problema de colisiones distribuidas que UUIDs resuelven
4. Si algún día se expande a multi-sede o sistemas distribuidos, se puede agregar UUID como columna adicional sin romper códigos existentes

**Tradeoff aceptado**: secuencia depende de lectura del max actual antes de insert (patrón ya usado por el Flask). Bajo concurrencia (2 usuarios simultáneos) podría haber race condition — mitigado por locks a nivel DB (`SELECT FOR UPDATE`) en Fase 2. Aceptable porque Vtiger y ERP tienen 2 cuentas únicamente (ADR-0026).

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-21 por Dario.

---

## 6. Convenciones canónicas MVP

### Códigos de entidades (preservados del Flask + nuevos)

| Entidad | Patrón | Ejemplo | Generador |
|---|---|---|---|
| Cliente | `LIVCLIENT####` | `LIVCLIENT0135` | ERP Flask (secuencia en Postgres) |
| Lead | `LIVLEAD####` | `LIVLEAD0001` | Vtiger (custom field sequence) |
| Tratamiento (item) | `LIVTRAT####` | `LIVTRAT0125` | ERP Flask |
| Producto (item) | `LIVPROD####` | `LIVPROD0014` | ERP Flask |
| Certificado (item) | `LIVCERT####` | `LIVCERT0002` | ERP Flask (nuevo patrón) |
| Promoción (item) | `LIVPROM####` | `LIVPROM0001` | ERP Flask (nuevo patrón) |
| Pago | `LIVPAGO####` | `LIVPAGO0073` | ERP Flask |
| Gasto | `LIVGASTO####` | `LIVGASTO0001` | ERP Flask (nuevo patrón) |
| Campaña | `LIVCAMP####` | `LIVCAMP0003` | Acquisition Engine (Fase 5) |
| Creativo | `LIVCREA####` | `LIVCREA0027` | Content Agent (Fase 5) |
| Usuario ERP | `LIVUSR####` | `LIVUSR0001` | ERP Flask (ADR-0026, solo 2 valores previsibles) |

**Regla de formato**:
- Prefijo en MAYÚSCULAS + 4 dígitos con padding zero
- Cuando la secuencia supere 9999 → 5 dígitos (`LIVCLIENT10000`)
- NO se reutilizan códigos de registros borrados/mergeados (preserva historial)

### Fuentes (`fuente` en Lead/Cliente)

Valores canónicos (picklist en Vtiger + enum en Postgres):

| Valor | Descripción |
|---|---|
| `meta_ad` | Click en anuncio Meta (Facebook + Instagram ads) |
| `instagram_organic` | Post orgánico Instagram (no pagado) |
| `facebook_organic` | Post orgánico Facebook (no pagado) |
| `google_search` | Búsqueda orgánica Google |
| `google_ad` | Anuncio Google Ads |
| `tiktok_organic` | Post orgánico TikTok (diferido hasta presencia real) |
| `form_web` | Formulario livskin.site |
| `whatsapp_directo` | Primer contacto vía WhatsApp sin canal previo identificado |
| `referido` | Referido por cliente existente (si se identifica quién) |
| `walk_in` | Llegó a la clínica sin contacto previo |
| `otro` | Default cuando no se puede clasificar |
| `organico` | Default para históricos (pre-digital acquisition) |

**Nota sobre históricos**: todos los 135 clientes del Excel se taggean como `fuente='organico'` en backfill (ADR-0025). Son casos de word-of-mouth que no encajan en taxonomía digital.

### Canales de adquisición (`canal_adquisicion`)

Agrupación analítica sobre fuentes:

| Valor | Fuentes que incluye |
|---|---|
| `paid` | `meta_ad`, `google_ad` (y futuros TikTok ad, etc.) |
| `organic` | `instagram_organic`, `facebook_organic`, `google_search`, `form_web` |
| `referral` | `referido` |
| `walk_in` | `walk_in` |
| `direct` | `whatsapp_directo` cuando no hay UTM identificable |
| `legacy` | `organico` (todos los históricos pre-MVP) |

### UTM parameters (convenciones)

Todos lowercase, separados por `_`. **Nunca mezclar mayúsculas y minúsculas** (Meta/Google distinguen).

**utm_source** (plataforma de origen):
- `facebook`, `instagram`, `google`, `tiktok`, `email`, `whatsapp`, `referral`

**utm_medium** (tipo de tráfico):
- `cpc` (paid click), `social` (orgánico social), `email`, `referral`, `direct`, `organic`

**utm_campaign** (nombre de campaña):
- Formato: `<objetivo>_<producto>_<mes>_<año>`
- Ejemplo: `awareness_botox_mayo_2026`, `retargeting_prp_agosto_2026`
- Sin espacios, sin tildes, minúsculas

**utm_content** (variante de creativo):
- Formato: `<tipo>_<variante>`
- Ejemplo: `video_a`, `carousel_b`, `single_image_c`

**utm_term** (keyword si es search):
- Solo aplica a Google Ads
- Lowercase, espacios como `+` o `-`
- Ejemplo: `botox+cusco`

### Nombres de campañas internas (Meta Ads Manager)

Mismo formato que `utm_campaign` + sufijo de cuenta/objetivo:
```
<objetivo>_<producto>_<mes>_<año>_<tipo_campaña>
awareness_botox_mayo_2026_alcance
conversion_prp_julio_2026_conversiones
```

### Nombres de archivos (docs, media)

| Tipo | Convención | Ejemplo |
|---|---|---|
| ADR | `NNNN-kebab-case-titulo.md` | `0011-modelo-de-datos.md` |
| Session log | `YYYY-MM-DD-fase-tema.md` | `2026-04-21-fase2-adrs-gobierno.md` |
| Arquetipo | `<nombre-arquetipo>.md` | `mama-antiaging.md` |
| Runbook | `<topic>.md` | `disaster-recovery.md` |
| Media (creativos) | `<LIVCREA####>_<formato>.<ext>` | `LIVCREA0027_story.mp4` |

### Convenciones en código (recordatorio de master plan § 12.3)

- **Nombres Python** (variables, funciones, clases): inglés, snake_case/PascalCase
- **Columnas DB**: español, snake_case (`monto_total`, `cod_cliente`)
- **Tablas DB**: español, snake_case plural (`ventas`, `clientes`, `dedup_candidates`)
- **Endpoints HTTP**: inglés kebab-case (`/api/dashboard`, `/venta`)
- **Templates HTML**: español kebab-case (`formulario.html`)

### Qué se difiere explícitamente

- **Nombres de archivos en S3/CDN** — no usamos cloud storage externo en MVP
- **Slugs de URLs de landings** — se decide al diseñar landing pages (Fase 5)
- **Nombres de colecciones Metabase** — se decide al diseñar dashboards (Fase 3)
- **Convención de tags en brain (Layer 1-6)** — se decide al poblar (Fase 2+)

---

## 7. Consecuencias

### Desbloqueado
- ADR-0011 tiene formatos validados para todos sus códigos
- ADR-0025 (backfill) sabe cómo generar secuencias
- Vtiger se configura con picklists canónicos
- Plantillas de campañas tienen formato uniforme desde día 1
- Metabase puede agrupar por `canal_adquisicion` sin limpieza previa

### Bloqueado / descartado
- NO se crean nuevos prefijos `LIVXXXX` sin actualizar este ADR
- NO se usan UUIDs en MVP
- NO se permite mezcla mayúsculas/minúsculas en UTMs

### Implementación derivada
- [ ] Función `generar_codigo(entidad, secuencia)` en ERP (una por tipo)
- [ ] Validación Pydantic de formato UTM en endpoint `/venta` y forms
- [ ] Constraint CHECK en Postgres: `cod_cliente ~ '^LIVCLIENT[0-9]{4,}$'`
- [ ] Config de Vtiger: picklist `fuente` con los 12 valores definidos
- [ ] Config Meta Business: naming template de campañas
- [ ] Documentar en `integrations/meta/README.md` y `integrations/google/README.md` las convenciones UTM

### Cuándo reabrir
- Multi-sede (2+ clínicas): podría requerir prefijo de sede (`LIVCUSCO-CLIENT0001`)
- Integración con sistema externo que asigna sus propios IDs (ej: pasarela de pagos)
- Cambio de idioma principal del negocio (si Livskin opera en inglés en el futuro)
- Revisión trimestral obligatoria: 2026-07-21

---

## 8. Changelog

- 2026-04-21 — v1.0 — Creada y aprobada (MVP Fase 2)
