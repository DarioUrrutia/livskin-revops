# ADR-0013 — Reglas de deduplicación y cross-channel identity stitching

**Estado:** ✅ Aprobada (MVP — v2, reemplaza v1)
**Fecha:** 2026-04-21 (v2)
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos

---

## 1. Contexto

Livskin captura leads por **exactamente 2 canales**:
1. **Form en landing pages** (phone required, email opcional, UTMs/fbclid desde hidden fields)
2. **WhatsApp Business Cloud API** (phone automático, profile name, fbclid/UTMs si vino por deep link estructurado)

Los 135 clientes existentes son 100% word-of-mouth y viven solo en ERP (NO en Vtiger).

Ver `project_acquisition_flow` memory para el flujo completo y `project_vtiger_erp_sot` para la asignación de SoT corregida (ERP = master cliente, Vtiger = master lead).

La versión v1 de este ADR proponía jerarquía de señales única con 3 tiers (teléfono > email > nombre+fecha_nac). Análisis más profundo reveló:
- Teléfono es el **único identificador universal** presente en ambos canales de captura
- Email solo aparece en forms (no en WA)
- Necesitamos **cross-channel stitching**: misma persona puede llegar por form Y luego por WA (o viceversa, o múltiples veces)
- Necesitamos **cross-system dedup**: al entrar lead nuevo en Vtiger, verificar si ya es Cliente en ERP (reactivación digital)

Referencias:
- ADR-0011 (modelo de datos — define las tablas `leads` y `clientes`)
- ADR-0015 (SoT por dominio — ERP = cliente, Vtiger = lead)
- ADR-0021 (UTM persistence en localStorage)
- `project_acquisition_flow` (memoria con flujo end-to-end)

---

## 2. Opciones consideradas

### Opción A — Phone-anchor con stitching via `lead_touchpoints`
Phone E.164 es el identificador universal. Lookup cross-system (leads en Vtiger + clientes en ERP) al entrar cualquier captura nueva. Tabla auxiliar `lead_touchpoints` registra cada encuentro individual (un lead puede tener N touchpoints en el tiempo). No se introduce tabla polimórfica `contact_identifiers`.

### Opción B — Tabla polimórfica `contact_identifiers` con 10+ tipos
Modelo identity-graph más sofisticado: cada identificador es fila separada (phone, email, Instagram ID, Meta user ID, WhatsApp ID, fbclid, gclid, cookie ID, external_id, etc.). Matching via joins sobre esta tabla.

### Opción C — Jerarquía simple sin stitching (la v1 original)
Solo matcheamos uno-a-uno: nuevo lead vs existente por phone, email, o nombre+fecha_nac. No se trackean múltiples encuentros.

---

## 3. Análisis de tradeoffs

| Dimensión | A (phone-anchor + touchpoints) | B (polimórfica 10+ tipos) | C (jerarquía simple) |
|---|---|---|---|
| Adecuación a 2 canales reales | **Excelente** | Over-engineered | Limitada (pierde multi-touch) |
| Complejidad implementación | Baja-media | Alta | Baja |
| Consultas para dedup | 2 simples | Múltiples joins | 1 simple |
| Captura multi-touch | **Sí** via touchpoints | Sí | No |
| Cross-system (Vtiger ↔ ERP) | **Sí** explícito | Sí | Parcial |
| Escalabilidad a futuros canales | Media (agregar columna/tipo) | Alta | Baja |
| Portfolio value | Medio-alto | Alto (pero excesivo) | Bajo |
| Alineación con scale Livskin | **Correcta** | Sobredimensionada | Sub-dimensionada |

---

## 4. Recomendación

**Opción A — phone-anchor + `lead_touchpoints`.**

Razones:
1. Refleja la realidad de 2 canales de captura donde **phone es universal**
2. Soporta multi-touch (mismo lead captado por form hoy y por WA en 3 días) sin tabla polimórfica compleja
3. Cross-system dedup (leads Vtiger ↔ clientes ERP) es directo: dos queries por phone, una en cada tabla
4. Fácil de implementar en el Flask refactorizado sin agregar conceptos que los comerciales no necesitan ver
5. Escalable: agregar un tercer canal futuro (ej: email inbound) se resuelve con columna `source='email_inbound'` en touchpoints, no rediseño

**Tradeoff aceptado**: si algún día Livskin agrega canales con identificadores no-phone (ej: Instagram DMs directamente al CRM, o integración con apps de terceros con user IDs propios), Opción A requerirá agregar columnas al schema. Aceptable: low-frequency event, alternativa menos compleja que polimórfica preventiva.

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-21 por Dario.

**Razonamiento de la decisora:**
> "Usaré Meta y Google Ads, en su mayoría las campañas enviarán a landing pages que tendrán dos opciones: llenar formulario o botones que te lleven a WhatsApp. Esas dos serán mis fuentes. Todas las campañas tendrán esas posibilidades, mis landings también."

---

## 6. Modelo de identity resolution MVP

### 6.1 Identificadores principales (columnas directas en `leads` y `clientes`)

| Identificador | Normalización | Presencia en Form | Presencia en WA |
|---|---|---|---|
| **phone_e164** | formato E.164 (`+51987654321`) | ✅ siempre | ✅ siempre |
| **email_lower** + **email_hash_sha256** | lowercase + trim | ✅ usualmente | ❌ no |
| **nombre** | lowercase + trim + colapsar espacios, SIN remover acentos | ✅ input usuario | ~ WA display_name (baja calidad) |
| **fecha_nacimiento** | date, solo en clientes/leads que la conocen | ✅ si form lo pide | ❌ no captured via WA |
| **fbclid_at_capture** | string from URL | ✅ hidden field | ~ solo si click-to-WA deep link |
| **gclid_at_capture** | string from URL | ✅ hidden field | ~ solo si click-to-WA deep link |
| **utm_source/medium/campaign/content/term_at_capture** | lowercase | ✅ hidden fields | ~ solo si click-to-WA deep link |

**`at_capture` vs `latest`**: guardamos el **first-touch** (at_capture, inmutable) para attribution histórica. Para nuevos encuentros de la misma persona, los identificadores de cada touch se guardan en `lead_touchpoints` (ver § 6.3).

### 6.2 Normalización de identificadores (reglas canónicas)

**Phone → E.164**:
```
Input: "987 654 321" / "51987654321" / "+51-987-654-321" / "(987) 654-321"
Normalizado: "+51987654321"

Reglas:
- Strip espacios, guiones, paréntesis
- Si empieza con "00", reemplazar por "+"
- Si no empieza con "+" y son 9 dígitos empezando por 9/8/7/6 → asumir "+51" (Perú)
- Si < 7 dígitos o > 15 → INVÁLIDO (guarda NULL + flag review)
```

**Email**:
```
"Dario@GMAIL.com " → "dario@gmail.com"
email_hash_sha256 = SHA256(email_lower) para Meta CAPI / Google Enhanced Conversions
```

**Nombre**:
```
"  Carmen   López " → "carmen lópez" (preservar acentos)
```

### 6.3 Tabla `lead_touchpoints` (multi-touch tracking)

Un lead puede tener **múltiples touchpoints** en el tiempo. Cada captura vía form o WA es un touchpoint.

| Columna | Tipo | Notas |
|---|---|---|
| id | bigserial PK | |
| lead_id | bigint FK leads NOT NULL | |
| canal | text NOT NULL | `form_web`, `whatsapp_cloud_api` |
| landing_url | text | URL de la landing si vino de form |
| fecha_contacto | timestamptz NOT NULL | |
| utm_source/medium/campaign/content/term | text | snapshot de ese touch específico |
| fbclid | text | |
| gclid | text | |
| primer_mensaje | text | solo WA: texto del primer msg (intent signal) |
| form_data_json | jsonb | solo form: snapshot completo de respuestas |
| ip | inet | server-side |
| user_agent | text | server-side |
| session_id | text | cookie first-party de UTM persistence (ADR-0021) |
| created_at | timestamptz | |

**Índices**:
- `(lead_id, fecha_contacto DESC)` — historial del lead
- `(fecha_contacto)` — analytics temporal
- `(utm_campaign)` — attribution per campaña

### 6.4 Algoritmo de dedup — flujo canónico

Cuando llega captura nueva (form submit o WA inbound):

```
INPUT: {phone_raw, email_raw (opt), nombre (opt), utm_*, fbclid, gclid, canal}

PASO 1 — Normalizar
  phone_e164 = normalize_phone(phone_raw)
  email_lower = normalize_email(email_raw) if email_raw
  if phone_e164 == NULL:
      return ERROR("phone inválido o ausente")  ← phone es required

PASO 2 — Cross-system lookup
  match_cliente = SELECT * FROM clientes WHERE phone_e164 = $1
  match_lead    = SELECT * FROM leads WHERE phone_e164 = $1 
                  AND estado NOT IN ('convertido', 'descartado')

PASO 3 — Resolver
  
  CASO A: match_cliente existe (→ reactivación digital)
    - Este humano YA ES Cliente en ERP
    - INSERT en leads con flag `es_reactivacion=true`, `cod_cliente_vinculado=LIVCLIENTxxxx`
    - INSERT en lead_touchpoints (canal, UTMs, etc.)
    - UPDATE clientes SET nuevos campos vacíos con data fresca si procede
    - Action: Conversation Agent trata como "cliente existente regresa"
  
  CASO B: match_lead existe (→ re-engagement del lead)
    - Este lead YA ESTÁ en funnel, este es un touch adicional
    - INSERT en lead_touchpoints (nueva fila con este encuentro)
    - UPDATE leads con data fresca donde las columnas estaban NULL
    - Re-scoring: el agent considera si este touch mejora el score
    - Action: continuar funnel con contexto acumulado
  
  CASO C: ni match_cliente ni match_lead (→ lead realmente nuevo)
    - INSERT en leads (nueva persona)
    - INSERT en lead_touchpoints (primer touch)
    - Action: Conversation Agent inicia nurture/qualification

PASO 4 — Enriquecimiento secundario (si email disponible)
  si email_lower presente y matcheable:
    - Buscar clientes con email_lower = $1 (otro canal de match)
    - Si match → igual que CASO A pero matched-by-email
    - Esto cubre: persona dio phone por WA y luego llena form con email + phone diferente (cambió celular)
```

### 6.5 Casos especiales

**Nombre + fecha_nacimiento sin phone** (ej: doctora registra walk-in manualmente sin tener phone):
- No aplica a leads (leads siempre tienen phone por canales digitales)
- Aplica solo a clientes creados manualmente en ERP
- Para estos: si nombre_normalizado + fecha_nacimiento coincide con cliente existente → NO merge automático, flag en `dedup_candidates`
- Si solo coincide nombre → NO merge, crea nuevo cliente

**Email inconsistente con phone** (persona A da su email + phone de persona B):
- Caso raro, aceptamos falso negativo (crea nuevo cliente)
- Si se detecta manualmente → merge con audit log

**Phone compartido** (dos personas usan mismo WA, ej: madre e hija):
- Sistema los trata como un solo lead hasta que se detecte semánticamente en conversación
- Action: Conversation Agent puede preguntar "¿con quién hablo?" y crear leads separados manualmente

### 6.6 Tabla `dedup_candidates` (revisión manual)

Igual que v1 de este ADR, preserva la tabla auxiliar para casos ambiguos:

| Columna | Tipo |
|---|---|
| id | bigserial PK |
| nuevo_id | bigint (el que acaba de entrar) |
| nuevo_tipo | text (`lead` o `cliente`) |
| existente_id | bigint |
| existente_tipo | text |
| razon | text (`mismo_nombre_sin_phone`, `email_coincide_phone_no`, ...) |
| score_similitud | numeric |
| resuelto | boolean default false |
| resolucion | text (`merge`, `mantener_separado`) |
| resuelto_por | bigint FK users |
| resuelto_at | timestamptz |
| created_at | timestamptz |

### 6.7 Merge semántico (cuando se decide unificar)

Reglas idénticas a v1:
1. **Preserva el de fecha_registro más antigua** (histórico gana)
2. **Datos consolidados**: campos NULL se llenan con valores del descartado
3. **FK redirect**: `ventas.cod_cliente`, `pagos.cod_cliente`, `lead_touchpoints.lead_id` se redireccionan
4. **Descartado NO se borra**: `merged_to = <id_preservado>`, `activo = false`
5. **Audit log obligatorio** (ADR-0027)

---

## 7. Qué se difiere explícitamente

- **Fuzzy matching con Levenshtein/soundex**: agregar si volumen de `dedup_candidates` pendientes >20/mes
- **Tabla polimórfica `contact_identifiers` con 10+ tipos**: overkill para 2 canales; reabrir si llegan canales con identificadores exclusivos no-phone (ej: Instagram DMs directo al sistema)
- **Identity graph con ML / probabilistic matching**: Año 2
- **Cross-device cookie stitching**: requiere tracking server-side maduro (parte de Fase 3)
- **Phone portability / segundos teléfonos**: persona con 2 números → agregar tabla `phone_aliases` cuando aparezca el caso

---

## 8. Consecuencias

### Desbloqueado
- Flujo form→WA (dispara template Meta al phone del form) tiene resolución clara: crea lead si no existe, agrega touchpoint si existe
- WhatsApp Cloud API inbound → mismo lookup consistente con forms
- Cross-system dedup (Vtiger lead vs ERP cliente) estandarizado
- Conversation Agent tiene contexto completo: "¿este phone ya me escribió? ¿es cliente histórico? ¿cuántos touchpoints lleva?"
- Meta CAPI Purchase con external_id hash garantiza attribution a phone del primer touch

### Bloqueado / descartado
- NO se crean leads sin phone (phone es NOT NULL required)
- NO hay fuzzy matching en MVP
- NO hay polimorphic identifiers table
- NO se permite merge automático por solo nombre

### Implementación derivada
- [ ] Funciones `normalize_phone(raw)`, `normalize_email(raw)`, `normalize_nombre(raw)` en Python + equivalentes SQL (idempotentes)
- [ ] Migración Alembic: crear `lead_touchpoints` + `dedup_candidates` con índices
- [ ] Endpoint `/api/client-lookup?phone=X` en ERP Flask (devuelve match_cliente + match_lead si existen)
- [ ] Endpoint `/webhook/form-submit` en n8n (valida, normaliza, dispara algoritmo § 6.4)
- [ ] Webhook WhatsApp Cloud API → n8n → mismo algoritmo
- [ ] UI de revisión de `dedup_candidates` en dashboard ERP
- [ ] Test cases (15+) cubriendo: nuevo lead, re-engagement, reactivación digital, nombre sin phone, email match, merge, dedup_candidate
- [ ] Documentar en `integrations/whatsapp/README.md` y `integrations/meta/README.md` la contract de identifiers

### Cuándo reabrir
- Volumen `dedup_candidates` pendientes >20/mes (agregar fuzzy)
- Nuevo canal de captura que no comparte phone (agregar tipo en touchpoints)
- Falsos positivos de merge detectados frecuentes (>2% de merges manuales revertidos)
- Integración con CDP externo (Segment, mParticle) — reabrir arquitectura completa
- Revisión trimestral obligatoria: 2026-07-21

---

## 9. Changelog

- 2026-04-21 — v1.0 — Creada y aprobada (MVP Fase 2) — jerarquía simple
- 2026-04-21 — v2.0 — **Reescrita completamente** tras clarificación de Dario: 2 canales reales (form + WA), phone como anchor universal, multi-touch via `lead_touchpoints`, cross-system dedup Vtiger ↔ ERP explícito. v1 NO tuvo vida productiva — misma sesión.
