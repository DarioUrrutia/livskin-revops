# Ads Manager Checklist — Día de la Madre 2026 (UI manual paso a paso)

> **Para Dario** — vos ejecutás click por click siguiendo este orden estricto. Cada paso tiene "qué clickear", "qué pegar/escribir", "qué deberías ver". Si algo se desvía → parás y me decís.
>
> **NO ejecutar este checklist hasta que `campaign-config-draft.md` esté aprobado.**
>
> **Tiempo estimado total**: 60-90 minutos de UI ininterrumpida.

---

## Pre-flight checklist (Día -1, antes de configurar)

### A. Verificar Account Quality (5 min)

1. Abrir https://business.facebook.com/accountquality
2. Account selector → "Livskin Perú · 2885433191763149"
3. Verificar status:
   - ✅ "Excellent" o "Good" → seguir
   - ❌ "Limited" o "Restricted" → **PARAR**, resolver primero (escribime y vemos)

### B. Verificar Pixel + Custom Conversion (10 min)

1. Abrir https://business.facebook.com/events_manager2/list/pixel
2. Account selector → "Livskin Perú · 2885433191763149"
3. Verificar Pixel "Livskin 2026" (`4410809639201712`):
   - Status: Active
   - Last received event: <24h
   - Si no hay events recientes → smoke test: navegá a https://campanas.livskin.site/botox-mvp/ → verificar event "PageView" en Test Events
4. **Crear Custom Conversion para WhatsApp Lead** (si no existe):
   - Events Manager → Custom Conversions → Create
   - Name: "WhatsApp Lead Día de la Madre"
   - Source: Pixel Livskin 2026
   - Rule: Event = "Click" AND URL contains "wa.me"
   - Category: Lead
   - Value: dejar vacío (no asignamos $)
   - Save

### C. Verificar FB Page + WhatsApp conectado (5 min)

1. Abrir https://business.facebook.com/settings/pages
2. Account selector → "Livskin Perú"
3. Verificar que Livskin page está listada
4. Click en la page → Settings → "Apps and integrations"
5. Verificar que **WhatsApp Business** está conectado a `+51980727888`
   - ✅ Si está conectado → seguir
   - ❌ Si no → **PARAR**, conectar primero (Settings → WhatsApp → Add)

### D. Verificar Custom Audience procesada (verificar día antes de lanzamiento)

1. Abrir https://business.facebook.com/asset_library/audiences
2. Account selector → "Livskin Perú · 2885433191763149"
3. Buscar "Livskin Clientes Activos 2026-05"
4. Verificar status:
   - ✅ "Ready" → seguir
   - ⏳ "Building" → esperar (Meta tarda 24-48h)
   - ❌ "Failed" → me decís, regeneramos CSV
5. Verificar Lookalike "Livskin LAL 2-3% Peru":
   - ✅ "Ready" → seguir
   - ⏳ "Building" → esperar (Meta tarda 12-24h post-CA ready)

### E. Método de pago + Spending limit (3 min)

1. Abrir https://business.facebook.com/billing
2. Verificar payment method activo (tarjeta)
3. Verificar account spending limit ≥ $100 (para que la campaña corra los 5 días)

---

## Crear la campaña — Step by step

### Paso 1: Abrir Ads Manager + nueva campaña (1 min)

1. Abrir https://www.facebook.com/adsmanager/manage/campaigns?act=2885433191763149
2. **Verificar arriba a la izquierda dice "Livskin Perú · 2885433191763149"**
   - ❌ Si dice otro nombre → click selector → cambiar a "Livskin Perú"
3. Click verde "**+ Crear**" (esquina superior izquierda de la tabla)

### Paso 2: Buying type + objective (2 min)

1. Buying type: **Auction** (default, dejar)
2. Campaign objective: scroll y seleccionar **"Engagement"**
3. Click "**Continue**"

### Paso 3: Special Ad Categories (1 min) — VERIFICAR CON CUIDADO

1. Pantalla pregunta "Does this campaign promote credit, employment, housing, or social/political issues?"
2. **Health no aparece como Special Ad Category obligatoria normalmente** para medicina estética en LATAM. PERO Meta puede preguntarte después si la cuenta está flag-eada.
3. Seleccionar **"Declare no special ad category"** (default)
4. ⚠️ Si Meta te muestra alerta amarilla "Esta cuenta está categorizada como Health" → **PARAR**, escribime, ajustamos plan B

### Paso 4: Campaign details (3 min)

1. **Campaign name**: pegar exacto
   ```
   Livskin — Día de la Madre 2026
   ```

2. **Campaign budget optimization (CBO)**: TOGGLE ON ✅
3. **Campaign budget**:
   - Tipo: **Lifetime budget**
   - Amount: **100 USD**
4. **Bid strategy**: dejar default "Highest volume" (= LOWEST_COST)
5. **A/B test**: NO marcar
6. Click "**Next**"

### Paso 5: Crear Ad Set 1 — Botox (10 min)

#### 5.1 Ad set name

```
Botox - Día de la Madre 2026 - Cusco F30-55
```

#### 5.2 Conversion location

- Seleccionar: **"Messaging apps"**
- App: ✅ **WhatsApp**
- ❌ Messenger (NO marcar)
- ❌ Instagram (NO marcar — solo WhatsApp directo)

#### 5.3 Performance goal

- "Maximize number of conversations"

#### 5.4 Facebook Page

- Seleccionar la **FB Page Livskin** (la que tiene WhatsApp conectado)

#### 5.5 WhatsApp number

- Seleccionar `+51980727888` (debe aparecer disponible si la FB Page tiene WhatsApp conectado)
- Si no aparece → **PARAR**, problema de conexión FB Page ↔ WhatsApp Business

#### 5.6 Budget & schedule

- Esta sección está deshabilitada porque CBO está ON a nivel campaign — Meta distribuirá.
- **Budget allocation por ad set NO se setea acá.** Lo veremos al final cuando tengamos los 2 ad sets, vamos a balancear 60/40 manualmente con "Bid amount" o "Spend cap" por ad set.
- **Schedule**:
  - Start date: **2026-05-05**, time: **06:00** (hora local Lima/Cusco)
  - End date: **2026-05-09**, time: **23:59**

#### 5.7 Audience

- **Locations**:
  - Click "Edit" → buscar "Cusco" → seleccionar **Cusco, Perú** (ciudad)
  - Cambiar a "Address" (no "current city")
  - Radio: **8 km** (drag slider o type)
  - Eliminar cualquier otra ubicación que aparezca por default

- **Custom Audiences (Include)**:
  - Click "Custom Audiences" → buscar
    - "Livskin Clientes Activos 2026-05" → seleccionar
    - "Livskin LAL 2-3% Peru sobre Clientes 2026-05" → seleccionar
  - Total CA en include: 2

- **Age**: 30 - 55
- **Gender**: Women
- **Languages**: agregar "Spanish (all)"
- **Detailed targeting** (interests):
  - Buscar y agregar:
    - Skincare
    - Beauty
    - Aesthetic medicine
    - Cosmetic procedures
    - Anti-aging
    - Mother's Day (si aparece para Perú)
- **Detailed targeting expansion**: ON ✅ (Meta puede ampliar si encuentra mejor audiencia)
- **Estimated daily reach**: anota lo que muestra (debería estar entre 5-15K alcance estimado)
  - Si <2K → audience demasiado chica, ampliar interests
  - Si >50K → demasiado amplia para budget chico

#### 5.8 Placements

- Seleccionar **Advantage+ placements** (Meta auto-optimiza)
- Si Meta pregunta sobre Audience Network → leave default (incluido)

#### 5.9 Frequency cap

Si Meta lo expone (no siempre):
- Cap: **4 impressions**
- Window: **7 days**

#### 5.10 Optimization & delivery

- Optimization for delivery: "Conversations" (default)
- Cost per result goal: dejar vacío (LOWEST_COST sin cap)

#### 5.11 Click "Next" → vamos a crear los ads de este ad set

### Paso 6: Crear Ads del Ad Set 1 — Botox

Crearemos **3 ads** (TOFU + MOFU + BOFU). Cada ad va a usar 3 aspect ratios (1:1, 4:5, 9:16) — Meta los serve según placement.

#### 6.1 Ad 1 — Botox TOFU

##### Ad name
```
Botox-TOFU-DM2026
```

##### Identity
- Facebook Page: Livskin
- Instagram account: vinculada (auto)

##### Format
- **Single image or video** (no carousel)

##### Media
- Click "Add media" → "Add image"
- Upload los 3 banners de TOFU Botox:
  - `tofu-1x1.png` (de docs/campaigns/2026-05-dia-madre/botox/banners/)
  - `tofu-4x5.png`
  - `tofu-9x16.png`
- En la sección "Customize media for placement":
  - 1:1 → asignar `tofu-1x1.png` para "Feed" placements
  - 4:5 → asignar para "Mobile Feed" + "Instagram Feed" placements
  - 9:16 → asignar para "Stories" + "Reels" placements

##### Primary text (Above image)
```
Tu rostro, tus reglas. Una hora para ti este Día de la Madre. Aplicación médica con criterio.
```
(125 chars máx ideal — esta tiene 105, OK)

##### Headline (under image)
```
Decide por ti
```

##### Description (smaller text, optional)
```
Livskin Cusco
```

##### Call to action
- Seleccionar **"Send Message"** del dropdown

##### Customize message (pre-poblado)
- Toggle "**Customize message**" ON
- Pegar exacto:
  ```
  Hola, vengo del aviso de Livskin Día de la Madre [BTX-MAY-FB]
  ```

##### URL parameters (para tracking)
Sí: muchas veces "URL parameters" aparece para ads de tipo Conversation. Pegar:
```
utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=botox-tofu&utm_term={{adset.id}}
```
(Meta auto-rellena `{{adset.id}}` con el ID del ad set)

##### Click "Save and finish ad" → seguir con Ad 2 (MOFU)

#### 6.2 Ad 2 — Botox MOFU

Idéntico al Ad 1 con cambios:
- Ad name: `Botox-MOFU-DM2026`
- Media: mofu-1x1.png + mofu-4x5.png + mofu-9x16.png
- Primary text:
  ```
  Cada rostro tiene su propia forma de armonizar. Conoce el tuyo con criterio médico, sin presión.
  ```
- Headline: `La armonía que tú decides`
- Description: `Livskin Cusco`
- CTA: Send Message
- Customize message: mismo `[BTX-MAY-FB]`
- URL parameters: `utm_content=botox-mofu` (resto igual)

#### 6.3 Ad 3 — Botox BOFU

- Ad name: `Botox-BOFU-DM2026`
- Media: bofu-1x1.png + bofu-4x5.png + bofu-9x16.png
- Primary text:
  ```
  Una hora, una conversación, una evaluación con criterio. La doctora te escucha y propone con criterio médico.
  ```
- Headline: `Tu hora, tu decisión`
- Description: `Livskin Cusco`
- CTA: Send Message
- Customize message: mismo `[BTX-MAY-FB]`
- URL parameters: `utm_content=botox-bofu`

### Paso 7: Volver al nivel campaign + crear Ad Set 2 — Acido Hialurónico

1. Click "Back to Campaign" o navegar arriba
2. Click "+ Create" → "Ad set"
3. Repetir todos los pasos del Paso 5 PERO con:
   - Ad set name: `Acido Hialuronico - Día de la Madre 2026 - Cusco F30-55`
   - **Misma audience exacta** (copiar la del Ad Set 1 si Meta permite, o re-seleccionar)
   - Misma WhatsApp number
4. Crear 3 ads (TOFU + MOFU + BOFU) usando los **banners de Ácido Hialurónico**:
   - Mensaje pre-poblado: `Hola, vengo del aviso de Livskin Día de la Madre [AH-MAY-FB]`
   - utm_content: `ah-tofu` / `ah-mofu` / `ah-bofu`
   - Copies específicos (ver `acido-hialuronico/copies.md`)

### Paso 8: Budget allocation 60/40 entre ad sets (3 min)

CBO con lifetime budget reparte automáticamente PERO podemos influenciar:

**Opción A — dejar Meta decidir** (recomendado para learning):
- No tocar nada. Meta optimiza basándose en performance early.

**Opción B — forzar split 60/40**:
- Ir a Ad Set Botox → Budget → "Set ad set spend limits"
  - Min: 50 USD, Max: 70 USD
- Ir a Ad Set Acido Hialurónico → Budget → "Set ad set spend limits"
  - Min: 30 USD, Max: 50 USD

**Mi recomendación**: Opción B (forzar 60/40) para esta primera campaña. Si Meta tuviera infinita data podríamos confiar en optimización, pero $100/5 días es poco data → mejor controlar.

### Paso 9: Review + submit (5 min)

1. Click "Review" arriba a la derecha
2. Verificar pantalla "Campaign overview":
   - Campaign: "Livskin — Día de la Madre 2026" ✅
   - Budget: $100 lifetime CBO ✅
   - Ad sets: 2 ✅
   - Ads: 6 ✅
   - Schedule: 5/5 06:00 → 9/5 23:59 ✅
3. Si todo OK: click "**Publish**"
4. Meta envía a review (4-24h)
5. Status: cambiará de "In review" → "Active" cuando Meta apruebe

### Paso 10: Verificación post-publish (cuando Meta apruebe)

1. Status del Campaign = "Active" ✅
2. Status de cada Ad = "Active" ✅
3. Si algún Ad rechazado:
   - Ver razón en Ads Manager
   - Si es Health-related issue → ajustar copy + resubmit
   - Si es image issue → cambiar banner + resubmit

---

## Smoke test pre-launch (cuando Meta apruebe pero antes de gastar mucho)

### Acción Dario:
1. Desde tu celular (NO desde la cuenta admin), navegá a Facebook/Instagram
2. Buscá manualmente alguno de los ads (puede tardar un tiempo en mostrarse)
3. Click en "Send message"
4. Verificá:
   - WhatsApp se abre con `+51980727888`
   - Mensaje pre-poblado: "Hola, vengo del aviso de Livskin Día de la Madre [BTX-MAY-FB]" o `[AH-MAY-FB]`
5. **NO mandes el mensaje** (sería un lead test que ensucia data). Solo verificá.

### Acción Claude:
1. Pixel Test Events: confirmar que "Click" event firea cuando alguien clickea Send Message
2. Verificar Pixel "Lead" event si Custom Conversion está mapeada

---

## Daily checks durante campaña (5 min cada mañana)

1. Abrir Ads Manager → "Livskin — Día de la Madre 2026"
2. Sacar screenshot de:
   - Vista de campaña con métricas (impresiones, spend, mensajes, CPM, CTR)
   - Vista de cada ad set
   - Top 3 ads + bottom 3 ads por CTR
3. Pasar screenshots a Claude vía chat
4. Claude actualiza `daily-reports/YYYY-MM-DD.md` con análisis + recomendaciones
5. Si Claude recomienda pause/swap → ejecutás con un click

---

## Checklist consolidado

### Pre-launch (Día -1)

- [ ] Account Quality verificado (Excellent/Good)
- [ ] Pixel firea events recientes
- [ ] Custom Conversion "WhatsApp Lead" creada
- [ ] FB Page tiene WhatsApp +51980727888 conectado
- [ ] Custom Audience procesada (status Ready)
- [ ] Lookalike Audience procesada (status Ready)
- [ ] Banners 18 disponibles en docs/campaigns/2026-05-dia-madre/<treatment>/banners/
- [ ] Copies aprobados (botox/copies.md + acido-hialuronico/copies.md)
- [ ] Compliance review por Claude hecho

### Launch (Día 1)

- [ ] Paso 1-9 ejecutados
- [ ] Review final ✅
- [ ] Publish ✅
- [ ] Meta review submitted
- [ ] (esperar aprobación)

### Smoke test (post-aprobación, pre-spend significativo)

- [ ] Test desde celular: ad → Send Message → WhatsApp abre con shortcode correcto
- [ ] Pixel events fluyendo
- [ ] No spend rate anormal (>$5 primeras 6h = ok)

### Durante campaña (Día 2-5)

- [ ] Daily check 1 (martes)
- [ ] Daily check 2 (miércoles)
- [ ] Daily check 3 (jueves)
- [ ] Daily check 4 (viernes)
- [ ] Doctora llena tracking sheet diariamente

### Post-campaña (Día 7-8)

- [ ] Spend final = $100 (o cercano)
- [ ] Pause campaign manualmente si quedó budget remaining
- [ ] Export final metrics CSV de Ads Manager
- [ ] Sesión post-mortem 2-3h
- [ ] Llenar post-mortem.md
- [ ] Procesar _doctrine-feedback.md
- [ ] Cierre del modo bootstrap (principio #13)

---

## Recursos rápidos

- Ads Manager: https://www.facebook.com/adsmanager/manage/campaigns?act=2885433191763149
- Events Manager: https://business.facebook.com/events_manager2/list/pixel
- Account Quality: https://business.facebook.com/accountquality
- Audiences: https://business.facebook.com/asset_library/audiences
- Page Settings: https://business.facebook.com/settings/pages
- Billing: https://business.facebook.com/billing

---

**Si algo se desvía del checklist → parar, screenshot, escribirme. Cero improvisación durante el setup.**
