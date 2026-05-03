# Campaign Config Draft — Livskin Día de la Madre 2026

> **Estado:** 📝 **BORRADOR — pendiente aprobación Dario**
> **NO se publica nada hasta que vos apruebes este documento sección por sección.**
>
> **Brief estratégico:** [`brief.md`](brief.md) (gate de las 4 preguntas)
> **Plan operativo:** [`plan.md`](plan.md)
> **Checklist UI manual:** [`ads-manager-checklist.md`](ads-manager-checklist.md)

---

## 1. Identificación de cuentas (verificado contra sistema 2026-05-04)

```yaml
business_manager:
  name: "Livskin Perú"
  id: 444099014574638
  status: activo

ad_account:
  id: "2885433191763149"
  name: "Livskin Perú"
  status: activo (11 campañas históricas)
  url: https://www.facebook.com/adsmanager/manage/campaigns?act=2885433191763149

pixel:
  id: 4410809639201712
  name: "Livskin 2026"
  status: healthy (verificado smoke E2E 2026-05-03)
  capi_token: configurado en n8n G3 workflow (Events Manager)

facebook_page:
  id: <pendiente confirmar — Dario abrir BM Settings>
  name: Livskin
  status: requerida para Click-to-WhatsApp ads

instagram_account:
  status: vinculado a la FB page (verificar)

operator:
  user: Dario Urrutia Martinez
  role: admin del BM Livskin Perú
  method: UI manual (NO Marketing API token esta vez)

system_user_existente:
  name: "Claude Audit"
  id: 61560721390798
  status: creado 2026-04-27, sin token utilizable todavía
  note: para futura App Review formal post-Bridge Episode

confirmar_dario:
  - [ ] Verificar que ad account 2885433191763149 está activa (no suspendida)
  - [ ] Verificar Pixel 4410809639201712 tiene events recibiendo
  - [ ] Confirmar FB Page ID que se va a usar para Click-to-WhatsApp
  - [ ] Confirmar IG account vinculada a esa FB Page
  - [ ] Verificar método de pago activo en ad account
  - [ ] Verificar que NO hay restricciones / warnings activos en Account Quality
```

---

## 2.0 Jerarquía Campaign / Ad Set / Ad — diagrama explícito

**Antes de leer la configuración técnica, entender la jerarquía estándar de Meta:**

```
🟦 CAMPAIGN (1) — el nivel más alto
   • Define: objetivo, budget total, schedule
   • "Livskin — Día de la Madre 2026"
   • Objective: Engagement → Maximize messages
   • Budget: $100 USD lifetime CBO
   • Schedule: 2026-05-05 → 2026-05-09
   │
   ├─🟨 AD SET 1 — agrupa ads que comparten audience + placement
   │  • Define: audiencia, placements, schedule, frequency cap, budget allocation
   │  • "Botox - Cusco F30-55"
   │  • Audience: Cusco radio 8km, F 30-55, intereses skincare/beauty
   │  • Budget: $60 (60% del campaign)
   │  • Placements: Advantage+ (Meta auto-distribuye Feed/Stories/Reels)
   │  │
   │  ├─🟩 AD 1.1 — Botox TOFU
   │  │   • Define: creative + copy + destino
   │  │   • Asset variants (3 aspect ratios servidos según placement Meta):
   │  │       tofu-1x1.png   → FB Feed, IG Feed
   │  │       tofu-4x5.png   → FB Feed mobile, IG Feed mobile
   │  │       tofu-9x16.png  → FB Stories, IG Stories, Reels
   │  │   • Primary text + Headline + Description + CTA "Send Message"
   │  │   • Customize message: "Hola... [BTX-MAY-FB]"
   │  │
   │  ├─🟩 AD 1.2 — Botox MOFU
   │  │   Idem con creatives MOFU
   │  │
   │  └─🟩 AD 1.3 — Botox BOFU
   │      Idem con creatives BOFU
   │
   └─🟨 AD SET 2 — misma audiencia, distinto tratamiento
      • "Acido Hialurónico - Cusco F30-55"
      • Audience: idéntica a Ad Set 1
      • Budget: $40 (40% del campaign)
      │
      ├─🟩 AD 2.1 — AH TOFU (assets AH + [AH-MAY-FB])
      ├─🟩 AD 2.2 — AH MOFU
      └─🟩 AD 2.3 — AH BOFU
```

**Resumen numérico:**

| Nivel | Cantidad | Descripción |
|---|---|---|
| Campaigns | **1** | "Livskin — Día de la Madre 2026" |
| Ad Sets | **2** | uno por tratamiento (Botox + AH) |
| Ads (creatives) | **6** | 3 ads por ad set (TOFU/MOFU/BOFU) |
| Asset variants (aspect ratios) | **18** | 3 variants por ad — los archivos `.png` que produce Dario en Canva |

**Decisión clave sobre aspect ratios** — usamos **Asset customization** (1 ad con 3 variantes), NO 3 ads separados:

| Opción | Total ads en Ads Manager | Ventaja | Desventaja |
|---|---|---|---|
| **Asset customization** ⭐ (elegida) | 6 ads | Meta optimiza budget mejor, learning más rápido | Menos control fino por placement |
| 3 ads separados por aspect ratio | 18 ads | Control fino | Dilute budget, learning lento — no funciona con $100 budget |

Por eso producís 18 banners pero los configurás como **3 variantes dentro de cada uno de los 6 ads**.

---

## 2. Estructura de campaña (configuración detallada)

```yaml
campaign:
  name: "Livskin — Día de la Madre 2026"
  objective: ENGAGEMENT
  performance_goal: "Maximize number of conversations"
  budget_optimization: CBO (Campaign Budget Optimization)
  budget_amount: 100 USD
  budget_type: lifetime
  schedule:
    start: "2026-05-05 06:00 (hora Lima/Cusco UTC-5)"
    end: "2026-05-09 23:59 (hora Lima/Cusco)"
  status_at_launch: ACTIVE
  special_ad_categories: <verificar al crear — Meta puede flag "Health">

ad_sets:
  - name: "Botox - Día de la Madre 2026 - Cusco F30-55"
    budget_percentage: 60
    estimated_budget_lifetime: 60 USD
    audience_id: <generar al crear>
    optimization_goal: "CONVERSATIONS" (Click-to-WhatsApp)
    billing_event: IMPRESSIONS
    bid_strategy: LOWEST_COST_WITHOUT_CAP (Meta optimiza)
    placement_type: ADVANTAGE_PLUS (Meta auto-optimiza placements)
    frequency_cap:
      cap: 4
      window_days: 7
    schedule_type: ALL_DAY (sin dayparting esta vez)
    targeting:
      countries: ["PE"]
      cities:
        - {name: "Cusco", radius_km: 8, key: <pendiente, Meta lo asigna>}
      age_min: 30
      age_max: 55
      gender: 2  # 1=men, 2=women
      locales: ["es_LA"]  # Spanish LATAM
      detailed_targeting:
        interests:
          - "Skincare"
          - "Beauty"
          - "Aesthetic medicine"
          - "Cosmetic procedures"
          - "Anti-aging"
          - "Mother's Day" (si aparece)
        behaviors:
          - "Engaged shoppers"
      custom_audiences:
        include:
          - <CA_clientes_livskin>  # 131 clientes hasheados
          - <LAL_2_3_pct_cusco>    # Lookalike sobre CA
        exclude: []  # ninguna por ahora
    ads_count: 9 (3 ideas × 3 aspect ratios)

  - name: "Acido Hialuronico - Día de la Madre 2026 - Cusco F30-55"
    budget_percentage: 40
    estimated_budget_lifetime: 40 USD
    # resto idéntico al ad set Botox excepto creatives
    ads_count: 9
```

**Plan B si Meta marca "Special Ad Category — Health":**

```yaml
plan_b_if_health_flag:
  reason: "Meta restringe targeting fino para health category"
  ajustes:
    age_min: 18
    age_max: 65
    gender: 0  # ambos (Meta optimiza)
    radius_km: 10  # ampliar ligeramente
  expected_impact: -10% efficiency, +20% audience size, -5% CTR estimado
```

---

## 3. Custom Audience — proceso completo

### 3.1 Generación del CSV (Claude, ~5 min)

```
Source: livskin_erp.clientes (VPS 3 postgres)
Query: SELECT phone_e164, email_lower
       FROM clientes
       WHERE activo = TRUE
         AND phone_e164 IS NOT NULL

Procesamiento por Claude:
  1. SSH livskin-erp + psql query
  2. Para cada fila:
     - phone: strip "+", strip espacios, lowercase
     - email: lowercase + trim
     - hash SHA-256 hex de phone y email separados
  3. Output CSV con columnas:
     phone (sha256 hex)
     email (sha256 hex, si existe)

Path output: _pending-uploads/livskin-clientes-CA-20260504.csv
Estado: gitignored (PII hasheada, mejor mantener fuera del repo igual)
```

### 3.2 Upload a Meta Business Manager (Dario, ~10 min UI)

```
1. https://business.facebook.com/asset_library/audiences
2. Account selector → "Livskin Perú · 2885433191763149"
3. Create Audience → Custom Audience → Customer file
4. Source: "Direct from customers"
5. Upload: livskin-clientes-CA-20260504.csv
6. Map columns:
   - phone (hashed) → phone
   - email (hashed) → email
7. Audience name: "Livskin Clientes Activos 2026-05"
8. Audience description: "131 clientes activos del ERP, hasheado SHA-256, source: ventas históricas + word-of-mouth"
9. Submit
10. Esperar 24-48h Meta procesa (status changes from "Building" → "Ready")
```

### 3.3 Crear Lookalike Audience (Dario, ~5 min UI, post-procesamiento de CA)

```
1. Audiences → Create → Lookalike Audience
2. Source: "Livskin Clientes Activos 2026-05"
3. Location: Peru (Meta no permite ciudad-level para LAL)
4. Audience size: 2-3% (custom slider)
5. Name: "Livskin LAL 2-3% Peru sobre Clientes 2026-05"
6. Submit
7. Esperar 12-24h Meta procesa
```

**Nota**: el LAL es a nivel país (Peru completo), NO Cusco. Pero el ad set restringe geográficamente a Cusco radio 8km, entonces la intersección efectiva = personas similares a tus clientes QUE ADEMÁS están en Cusco.

---

## 4. Creatives — especificación detallada

### 4.1 Cantidad total

- **2 tratamientos** (Botox, AH)
- **3 ideas creativas por tratamiento** (TOFU declaración / MOFU consideración / BOFU acción)
- **3 aspect ratios por idea** (1:1, 4:5, 9:16)
- **TOTAL: 18 banners**

### 4.2 Aspect ratios obligatorios

| Ratio | Pixels | Placement Meta | Prioridad |
|---|---|---|---|
| **1:1** | 1080×1080 | FB Feed, IG Feed, Marketplace, Carousel | Alta (se serve en muchos lugares) |
| **4:5** | 1080×1350 | FB Feed mobile (mejor performance), IG Feed mobile | **Crítica** (mobile = mayoría tráfico) |
| **9:16** | 1080×1920 | FB Stories, IG Stories, Reels | Alta (Reels growing fast) |

### 4.3 Por idea creativa — qué debe transmitir

#### Idea 1 — TOFU (Declaración de identidad)

**Mensaje principal**: "Este Día de la Madre, decide por ti"

**Imagen**: mujer 35-50 años, mirada con intención (NO sonrisa exagerada), expresión tranquila, fondo natural. Comunica autonomía + control + naturalidad ANTES del texto.

**Texto sobre imagen** (mínimo, máximo 8 palabras):
- Hero: "Este Día de la Madre,\ndecide por ti."
- Sub-mínimo (opcional): "Una hora para ti."

**CTA del banner**: "Descubre más →" (suave, editorial)

**Botón del ad (Meta)**: "Send Message" / "Enviar mensaje" → abre WhatsApp

**Copy del ad (texto principal Meta, no el banner)**:
> Tu rostro, tus reglas. Aplicación médica con criterio en Livskin Cusco.

**Por qué funciona** (checklist 4 preguntas):
- ✅ Identidad: madre que decide por ella misma
- ✅ Emoción: permiso interno + tranquilidad
- ✅ Decisión: dedicarse tiempo, conversar con la doctora
- ✅ NO dice: producto específico, precio, urgencia, "rejuvenecer"

#### Idea 2 — MOFU (Consideración / explicativo emocional)

**Mensaje principal**: "La armonía que tú decides"

**Imagen**: mismo universo estético que TOFU. Puede ser la misma persona o foto similar. Coherencia visual obligatoria. Puede mostrar la doctora si tenés foto profesional aprobada.

**Texto sobre imagen**:
- Hero: "La armonía que\ntú decides."
- Sub: "Aplicación médica con criterio."

**CTA**: "Conoce tu enfoque"

**Copy del ad**:
> Cada rostro tiene su propia forma de armonizar. Conoce el tuyo con criterio médico, sin presión.

**Por qué funciona**:
- ✅ Introduce el concepto de "armonización" (consideración) sin nombrar Botox/AH
- ✅ Mantiene tono identitario del TOFU
- ✅ NO dice: "tratamiento", "rellenar", "suavizar arrugas"

#### Idea 3 — BOFU (Acción concreta)

**Mensaje principal**: "Agenda tu evaluación"

**Imagen**: más cercana, más directa. Puede mostrar la doctora en consultorio (humanización del servicio) o resultado sutil natural (NO antes/después comparativo).

**Texto sobre imagen**:
- Hero: "Tu hora.\nTu decisión."
- Sub: "Evaluación médica con la doctora."

**CTA**: "Agenda tu evaluación"

**Copy del ad**:
> Una hora, una conversación, una evaluación con criterio. La doctora te escucha y propone con criterio médico.

**Por qué funciona**:
- ✅ Directo pero elegante (BOFU permitido)
- ✅ Acción concreta ("agenda")
- ✅ NO dice: "promoción", "descuento", "antes del 11 de mayo"

### 4.4 Adaptación por aspect ratio

Cada idea creativa se produce en 3 aspect ratios. Recomendaciones de adaptación:

| Aspect ratio | Tip de composición |
|---|---|
| **1:1** (1080×1080) | Hero text en parte superior 1/3, imagen ocupa 2/3 inferior. Centro de mensaje al 50% Y |
| **4:5** (1080×1350) | Más espacio vertical. Imagen full-bleed con overlay gradient + texto en franja inferior. Optimizar para Feed mobile |
| **9:16** (1080×1920) | Stories/Reels. Texto en parte superior, imagen central, CTA visual abajo. Full-bleed obligatorio. |

### 4.5 Texto sobre imagen — restricciones Meta

Meta tiene reglas (no estricta hoy, pero recomendable):
- **Texto en imagen ≤20%** del área total → mejor delivery
- Si tu banner tiene mucho texto, Meta puede limitarte alcance (no rechaza, pero serve menos)
- Recomendación: en aspect 1:1 y 4:5, texto en una franja (10-20% del área) + resto imagen pura

---

## 5. Copy del ad (lo que Meta llama "Primary text" / "Headline" / "Description")

Por cada ad creative, Meta pide:

| Campo Meta | Caracter limit | Prop. Botox TOFU | Prop. AH TOFU |
|---|---|---|---|
| **Primary text** (above image) | 125 chars ideal | "Tu rostro, tus reglas. Una hora para ti este Día de la Madre. Aplicación médica con criterio." | "La armonía que tú decides. Una hora para ti este Día de la Madre. Aplicación médica con criterio." |
| **Headline** (under image) | 27 chars | "Decide por ti" | "Decide por ti" |
| **Description** (smaller, optional) | 27 chars | "Livskin Cusco" | "Livskin Cusco" |
| **Display Link** (optional) | — | (no aplica para Click-to-WhatsApp) | — |
| **Call to action** | preset | "Send Message" | "Send Message" |

Variantes para MOFU + BOFU se detallan en `botox/copies.md` y `acido-hialuronico/copies.md`.

---

## 6. Click-to-WhatsApp setup

### 6.1 Requirements Meta

- ✅ FB Page conectada a WhatsApp Business account
- ⚠️ La doctora tiene WhatsApp Business app instalada en su número `+51980727888`
- ⚠️ El número debe estar verificado en Meta Business Manager → WhatsApp accounts

**Verificar Dario antes de lanzar**:
- [ ] FB Page Livskin tiene WhatsApp number conectado en Settings → Apps and integrations → WhatsApp
- [ ] Número activo y respondible (la doctora atiende)

### 6.2 Mensaje pre-poblado por ad

Cada ad tiene su propio mensaje pre-poblado dependiendo de tratamiento:

**Botox ads:**
```
Hola, vengo del aviso de Livskin Día de la Madre [BTX-MAY-FB]
```
URL encoded:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BBTX-MAY-FB%5D
```

**AH ads:**
```
Hola, vengo del aviso de Livskin Día de la Madre [AH-MAY-FB]
```
URL encoded:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BAH-MAY-FB%5D
```

### 6.3 En Ads Manager UI

Al crear el ad:
1. Destination: "WhatsApp" (no "Website")
2. WhatsApp number: seleccionar `+51980727888` (debe aparecer si la FB Page tiene WhatsApp conectado)
3. Welcome message / pre-filled text: pegar el mensaje correspondiente con shortcode

---

## 7. UTM scheme estandarizado

Aunque la conversión va a WhatsApp directo (no a landing), las UTMs se incluyen en los ads para tracking en Pixel + CAPI events si Meta los dispara.

```
?utm_source=facebook | instagram (Meta auto-detecta placement)
&utm_medium=paid
&utm_campaign=dia-madre-2026
&utm_content=<treatment>-<funnel>-<aspect_ratio>
&utm_term=<adset_id>
```

**Tabla completa de UTMs (18 banners):**

| # | Treatment | Funnel | Aspect | utm_content |
|---|---|---|---|---|
| 1 | Botox | TOFU | 1:1 | botox-tofu-1x1 |
| 2 | Botox | TOFU | 4:5 | botox-tofu-4x5 |
| 3 | Botox | TOFU | 9:16 | botox-tofu-9x16 |
| 4 | Botox | MOFU | 1:1 | botox-mofu-1x1 |
| 5 | Botox | MOFU | 4:5 | botox-mofu-4x5 |
| 6 | Botox | MOFU | 9:16 | botox-mofu-9x16 |
| 7 | Botox | BOFU | 1:1 | botox-bofu-1x1 |
| 8 | Botox | BOFU | 4:5 | botox-bofu-4x5 |
| 9 | Botox | BOFU | 9:16 | botox-bofu-9x16 |
| 10 | AH | TOFU | 1:1 | ah-tofu-1x1 |
| 11 | AH | TOFU | 4:5 | ah-tofu-4x5 |
| 12 | AH | TOFU | 9:16 | ah-tofu-9x16 |
| 13 | AH | MOFU | 1:1 | ah-mofu-1x1 |
| 14 | AH | MOFU | 4:5 | ah-mofu-4x5 |
| 15 | AH | MOFU | 9:16 | ah-mofu-9x16 |
| 16 | AH | BOFU | 1:1 | ah-bofu-1x1 |
| 17 | AH | BOFU | 4:5 | ah-bofu-4x5 |
| 18 | AH | BOFU | 9:16 | ah-bofu-9x16 |

---

## 8. Compliance + Risk + Meta policies

### 8.1 Special Ad Category — Health

Meta puede flagear esta cuenta como "Special Ad Category — Health" porque:
- Cuenta promociona servicios médicos
- Pixel events de "medical" related interests

Cómo verificar AL CREAR EL AD:
- En el step de "campaign objective", Meta puede pedir auto-categorizar
- Si pide → seleccionar "None" si tu cuenta no la marca; "Health" si lo exige

**Si flag aplica:**
- Audience NO se puede targeting fino (gender/age/zip code)
- Aplicar Plan B (§ 2 plan_b_if_health_flag)
- Lead generation funciona igual, solo audience más amplia

### 8.2 Compliance copy — review pre-submit

Cada texto se valida contra:
- ❌ NO claims absolutas: "garantizado", "100% efectivo", "sin riesgo"
- ❌ NO antes/después en imagen sin disclaimer (mejor evitar)
- ❌ NO targeting por enfermedad/condición ("¿tienes arrugas?")
- ❌ NO precios ni "desde S/."
- ✅ Disclaimers sutiles si aplica ("Resultados varían según cada persona")

**Yo (Claude) reviso ANTES de submit cada copy y banner del checklist**. Si algo es dudoso → pre-flag.

### 8.3 Account Quality — verificar status

Antes de lanzar, Dario verifica en Business Manager:
- https://business.facebook.com/accountquality
- Seleccionar ad account `2885433191763149`
- Status debe ser "Excellent" o "Good"
- Si "Limited" o "Restricted" → resolver ANTES de lanzar (evita rejection automática)

### 8.4 Budget kill switch trigger

**Kill switch automático** (Meta lo provee): si CTR cae <0.3% o frequency >5 → el ad se vuelve ineficiente. Yo recomendaré pause.

**Kill switch manual** (vos podés activar):
- En Ads Manager: pause campaña entera
- O pause específico ad set / ad

**Cuándo activar kill switch:**
- Costo por mensaje >$25 USD (target era $5-15)
- 0 mensajes después de día 2 con $20 gastados → audience equivocada o creative malo
- Algún error grave (ad mal aprobado, link roto)

---

## 9. Tracking + KPIs

### 9.1 Pixel events esperados

Esta campaña va a Click-to-WhatsApp. Pixel events que pueden dispararse:
- `Click` (custom — cuando alguien clickea botón "Send Message")
- `Lead` (custom — si configuramos Custom Conversion para click WhatsApp)
- (NO PageView porque no hay landing)

**Custom Conversion sugerida (Dario en Events Manager):**
```
Name: "WhatsApp Lead Día de la Madre"
Event: Click
Rule: URL contains "wa.me" OR action_type = "send_message"
Category: Lead
```

### 9.2 KPIs y targets

| KPI | Target | Alarma |
|---|---|---|
| Spend | $100 lifetime distribuido en 5 días | Si >$25/día desde día 2 → revisar |
| CPM | $7-15 USD | >$20 = audience demasiado chica o baja relevance |
| CTR | 1-2% | <0.5% = creative malo, swap |
| Frequency | 2-3 promedio | >4 = audience saturada, ampliar o pause |
| Mensajes WhatsApp | 6-15 totales en 5 días | <5 al día 4 = revisar fundamentalmente |
| Cost per message | $5-15 USD | >$20 = problemas |
| Pixel "Lead" events | match con # mensajes WhatsApp ±10% | divergencia >20% = tracking issue |

### 9.3 Daily monitoring (sin Marketing API)

Workflow ya descrito en `tracking.md` § "Métricas a monitorear (daily)".

Resumen:
1. Dario abre Ads Manager 1× por día (mañana)
2. Screenshot/exporta métricas
3. Pasa a Claude
4. Claude actualiza `daily-reports/YYYY-MM-DD.md` con análisis + recomendaciones

---

## 10. Timeline operativo día por día

```
Domingo 2026-05-04 (HOY) — modo BOOTSTRAP
  • Brief aprobado (gate)
  • Config-draft aprobado (gate)
  • CSV CA generado por Claude → entregado a Dario
  • Dario sube CA a Meta (espera 24-48h)

Lunes 2026-05-05 (Día 1) — LAUNCH
  • LAL ya disponible (procesado)
  • Banners 18 entregados por Dario en Canva
  • Claude ejecuta: review copy + checklist UI step-by-step
  • Dario: configurar campaña en Ads Manager (con Claude guía)
  • Submit a Meta review (4-24h)
  • Lanzamiento target: 18:00-21:00 hora Cusco (peak engagement)

Martes 2026-05-06 (Día 2)
  • Daily check 1 (mañana)
  • Verificar primeras 12-18h de delivery
  • Si CTR <0.5% en algún creative → swap

Miércoles 2026-05-07 (Día 3) — MID
  • Daily check 2
  • Análisis Botox vs AH a la fecha
  • Posible reasignación budget si uno domina mucho

Jueves 2026-05-08 (Día 4)
  • Daily check 3
  • Verificar frequency cap
  • Pause creatives saturados

Viernes 2026-05-09 (Día 5) — FINAL DAY
  • Daily check 4
  • Push final budget
  • Preparar checklist de cierre

Sábado 2026-05-10
  • Verificar last-day spend
  • Tracking sheet doctora consolidado

Domingo 2026-05-11 (DÍA DE LA MADRE)
  • Doctora atiende citas presenciales
  • Anota en sheet quiénes vinieron por la campaña

Lunes 2026-05-12 (Día +1) — POST-MORTEM PREP
  • Cross-check Ads Manager vs tracking sheet
  • Calcular CAC real, ROI directo

Martes 2026-05-13 (Día +2) — POST-MORTEM SESSION
  • Session 2-3h con Dario
  • Llenar post-mortem.md completo
  • Procesar _doctrine-feedback.md
  • Cierre formal del modo BOOTSTRAP (principio #13)
  • Commit ascendiendo doctrina v0.1 → v1.0
```

---

## 11. Mis acciones pendientes (Claude — antes de lanzar)

- [x] Brief.md ✅
- [x] plan.md ✅
- [x] tracking.md ✅
- [x] post-mortem.md template ✅
- [x] _doctrine-feedback.md ✅
- [x] campaign-config-draft.md (este archivo) ✅
- [ ] **ads-manager-checklist.md exhaustivo paso a paso** (siguiente)
- [ ] Por tratamiento: README.md + copies.md + tracking.md
- [ ] CSV Custom Audience generado y dejado en `_pending-uploads/`
- [ ] Validate copy compliance contra Meta policies (al recibir banners + copies finales)
- [ ] Pre-flight smoke E2E (verificar Pixel + UTMs el día -1)
- [ ] Daily reports durante campaña

## 12. Tus acciones pendientes (Dario)

### Pre-aprobación del brief y config (gate de aprobación)

- [ ] Leer `brief.md` § "Las 4 preguntas" — aprobar respuesta de cada una
- [ ] Leer este config-draft sección por sección — aprobar cada bloque
- [ ] Confirmar fechas de lanzamiento (5-9 may)
- [ ] Confirmar budget split 60/40 Botox/AH

### Verificaciones técnicas pre-launch

- [ ] Verificar Account Quality del ad account 2885433191763149 (Excellent/Good)
- [ ] Verificar FB Page ID + IG account vinculados
- [ ] Verificar WhatsApp Business conectado a la FB Page
- [ ] Verificar método de pago activo en ad account
- [ ] Confirmar Pixel firea correctamente (test event con FB Pixel Helper)

### Custom Audience workflow

- [ ] Recibir CSV de Claude (en `_pending-uploads/`)
- [ ] Subir CA a Meta Business Manager (ver § 3.2)
- [ ] Esperar 24-48h procesamiento
- [ ] Crear LAL 2-3% (ver § 3.3)
- [ ] Esperar 12-24h procesamiento

### Producción de banners (en Canva)

- [ ] 9 banners Botox (3 ideas × 3 aspect ratios)
- [ ] 9 banners Acido Hialurónico (idem)
- [ ] Dejar en `docs/campaigns/2026-05-dia-madre/<treatment>/banners/`
- [ ] Naming convencional: `<funnel>-<aspect>.png` (ej: `tofu-1x1.png`, `mofu-4x5.png`)

### Configuración Ads Manager (siguiendo checklist)

- [ ] Abrir checklist ads-manager-checklist.md
- [ ] Ejecutar cada paso confirmando con Claude
- [ ] Submit a Meta review

### Doctora coordination

- [ ] Imprimir cheat sheet de shortcodes
- [ ] Crear Google Sheet de tracking
- [ ] Coordinar disponibilidad doctora días 5-11 (especialmente DM)
- [ ] Asegurar que la doctora puede responder rápido WhatsApp (target <2h)

---

## 13. Definition of Done (config aprobado)

Este config-draft se considera "aprobado y listo para implementar" cuando:

- [ ] Dario marcó OK explícito a las 13 secciones
- [ ] Dario verificó las acciones técnicas pre-launch (§ 12)
- [ ] CA está procesando en Meta
- [ ] Banners 18 están en sus carpetas
- [ ] Copies refinados bajo doctrina (Claude)
- [ ] Compliance review de copy hecho (Claude)
- [ ] ads-manager-checklist.md generado (Claude — pendiente siguiente paso)

Cuando los 7 estén ✅ → ejecutamos el lanzamiento siguiendo el checklist UI manual.

---

## 14. Cross-link

- Brief estratégico: [`brief.md`](brief.md)
- Plan operativo: [`plan.md`](plan.md)
- Tracking consolidado: [`tracking.md`](tracking.md)
- Post-mortem template: [`post-mortem.md`](post-mortem.md)
- Doctrine feedback (bootstrap): [`_doctrine-feedback.md`](_doctrine-feedback.md)
- Doctrina de marca v0.1: `docs/brand/`
- Checklist UI manual: [`ads-manager-checklist.md`](ads-manager-checklist.md) (siguiente)

---

**Estado del config-draft**: pendiente aprobación Dario. Léelo sección por sección y decime qué ajustar.
