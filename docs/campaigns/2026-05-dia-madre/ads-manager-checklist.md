# Ads Manager Checklist — Día de la Madre 2026 (UI manual paso a paso)

> **Versión final 2026-05-04** — alineada a decisiones del 2026-05-04:
> - Objetivo: **Tráfico** (link clicks)
> - Estructura: **1 campaña, 2 ad sets con CBO**, destinos mixtos (Landing + WhatsApp)
> - 3 ads totales: TOFU + MOFU → landing; BOFU → WA directo
> - Banners: solo 9:16 (Meta hace crop automático)
> - Pixel `4410809639201712` (Livksin Pixel 2026) confirmado activo
> - Ad account `2885433191763149` (Livskin Perú) confirmada
>
> **Para Dario** — ejecutás click por click siguiendo este orden estricto. Cada paso dice qué clickear, qué pegar, qué deberías ver. Si algo se desvía → parás y me decís.
>
> **Tiempo estimado total**: 30-45 min (campaña + 2 ad sets + 3 ads).

---

## 1. Estructura objetivo de la campaña

```
📦 Campaña: "Livskin — Día de la Madre 2026 — Armonización Facial"
   Objective: Tráfico (Traffic)
   Optimización: Link Clicks
   Budget: $100 lifetime CBO
   Schedule: 2026-05-05 06:00 → 2026-05-09 23:59 (Lima)
   Pixel: 4410809639201712 (para tracking, no optimización)
   Ad account: 2885433191763149 (Livskin Perú)
   │
   ├─🟦 Ad Set 1: "Landing"
   │   Audience: misma que Ad Set 2 (compartida)
   │   Optimization location: Website
   │   ├─ Ad TOFU → https://campanas.livskin.site/dia-madre-armonizacion-2026/?src=tofu
   │   └─ Ad MOFU → https://campanas.livskin.site/dia-madre-armonizacion-2026/?src=mofu
   │
   └─🟩 Ad Set 2: "WhatsApp directo"
       Audience: misma que Ad Set 1
       Optimization location: Messaging Apps (WhatsApp)
       └─ Ad BOFU → wa.me/51980727888 con pre-text [ARM-MAY-FB-BOFU]

Total: 1 campaign · 2 ad sets · 3 ads
```

**Hipótesis a validar**: ¿landing convierte mejor que WA directo? Meta CBO redistribuye budget según performance → respuesta natural en 2-3 días.

---

## 2. Pre-flight (Día -1, antes de configurar)

### A. Account Quality (3 min)

1. Abrir https://business.facebook.com/accountquality
2. Account selector → seleccionar **"Livskin Perú · 2885433191763149"**
3. Verificar status:
   - ✅ "Excellent" o "Good" → seguir
   - ❌ "Limited" o "Restricted" → **PARAR**, escribime

### B. Pixel funcionando (3 min)

1. Abrir https://business.facebook.com/events_manager2/list/datasets
2. Seleccionar **Livksin Pixel 2026** (`4410809639201712`)
3. Verificar:
   - Status: Active
   - Eventos recientes: PageView debe estar disparando (ya validamos: 154 PV en últimas 14h ✅)
4. **Smoke test rápido**: abrir https://campanas.livskin.site/dia-madre-armonizacion-2026/?src=tofu en otra pestaña → aceptar consent modal → en Events Manager → "Probar eventos" debe registrar el PageView en 1-2 min

### C. FB Page + WhatsApp conectado (3 min)

1. Abrir https://business.facebook.com/settings/pages
2. Seleccionar la Page de Livskin
3. Settings → "Apps and integrations" → confirmar **WhatsApp Business** está conectado a `+51980727888`
4. Si NO está → **PARAR**, conectar primero (Settings → WhatsApp → Add)

### D. Método de pago + spending limit (2 min)

1. https://business.facebook.com/billing
2. Verificar:
   - Payment method activo (tarjeta no vencida)
   - Account spending limit ≥ $100

---

## 3. Crear la campaña

### Paso 1: Abrir Ads Manager (1 min)

1. Abrir https://www.facebook.com/adsmanager/manage/campaigns?act=2885433191763149
2. **Verificar arriba a la izquierda dice "Livskin Perú · 2885433191763149"**
   - ❌ Si dice otro → click selector → cambiar a Livskin Perú
3. Click verde **"+ Crear"** (esquina superior izquierda)

### Paso 2: Buying type + objective (2 min)

1. **Buying type**: Auction (default)
2. **Campaign objective**: seleccionar **"Tráfico"** (Traffic)
3. Click **"Continuar"**

### Paso 3: Special Ad Categories (1 min) — atención

1. Pantalla pregunta sobre Crédito / Empleo / Vivienda / Política / Salud
2. Seleccionar **"Declarar que no es categoría especial de anuncios"** (default)
3. ⚠️ Si Meta muestra alerta amarilla "Esta cuenta está categorizada como Salud" → **PARAR**, me avisás. Plan B = ampliar audiencia 18-65 ambos géneros.

### Paso 4: Campaign details (3 min)

1. **Nombre de la campaña** (pegar exacto):
   ```
   Livskin — Día de la Madre 2026 — Armonización Facial
   ```
2. **Optimización del presupuesto de la campaña (CBO)**: TOGGLE **ON** ✅
3. **Presupuesto de la campaña**:
   - Tipo: **Presupuesto total** (Lifetime)
   - Cantidad: **100** USD
4. **Estrategia de puja**: dejar default "Mayor volumen" (Highest volume)
5. **A/B test**: NO marcar
6. Click **"Siguiente"**

---

### Paso 5: Crear Ad Set 1 — "Landing"

#### 5.1 Nombre del conjunto de anuncios
```
Landing - Cusco F30-55 - Armonización Facial
```

#### 5.2 Conversion Location
- Seleccionar: **"Sitio web"** (Website)

#### 5.3 Performance goal
- "Maximizar el número de clics en el enlace" (Maximize link clicks)

#### 5.4 Pixel (opcional, para tracking)
- Si Meta lo pregunta: seleccionar **Livksin Pixel 2026 (`4410809639201712`)**

#### 5.5 Budget & schedule

- **Spend limits del ad set** (forzar split):
  - Toggle "Establecer límites de gasto del conjunto de anuncios" → ON
  - Mínimo: **50** USD
  - Máximo: **70** USD
  - (Asegura que Landing recibe entre 50-70%, dejando 30-50% para WhatsApp)

- **Schedule**:
  - Fecha de inicio: **2026-05-05**, hora: **06:00** (hora local Lima)
  - Fecha de finalización: **2026-05-09**, hora: **23:59**

#### 5.6 Audience

- **Ubicaciones**:
  - Click "Editar" → buscar **"Cusco"** → seleccionar **Cusco, Perú** (ciudad)
  - Cambiar tipo a **"Personas que viven en este lugar"** (no "personas en este lugar recientemente")
  - Radio: **8 km**
  - Verificar que NO aparece Lima ni provincias lejanas; eliminar si aparecen

- **Custom Audiences (Include)** — click en "Públicos personalizados" → buscar y agregar las 4:
  - ✅ TODO COMPLETO FB
  - ✅ personas que hicieron clic en llamada de accion
  - ✅ Interaccion con la pagina 365 dias
  - ✅ PERSONA QUE INTERACTUARON 28 DIAS

- **Edad**: 30 - 55
- **Género**: Mujeres
- **Idiomas**: Spanish (todos)

- **Detailed targeting** (intereses) — agregar:
  - Skincare
  - Beauty
  - Aesthetic medicine
  - Cosmetic procedures
  - Anti-aging
  - Mother's Day (si aparece para Perú)

- **Detailed targeting expansion**: ON ✅

- **Estimated audience size**: anota lo que muestra
  - <2K → audience demasiado chica, ampliar intereses
  - >50K → demasiado amplia, considera quitar 1-2 intereses

#### 5.7 Placements

- Seleccionar **Advantage+ placements** (Meta auto-optimiza)
- Si pregunta sobre Audience Network → leave default

#### 5.8 Click "Siguiente" → vamos a crear los 2 ads del Ad Set "Landing"

---

### Paso 6: Crear Ads del Ad Set "Landing" (2 ads)

#### 6.1 Ad TOFU → Landing

##### Nombre del anuncio
```
TOFU-Landing-DM2026
```

##### Identidad
- Página de Facebook: **Livskin**
- Cuenta de Instagram: vinculada (auto)

##### Formato
- **Imagen única** (Single image)

##### Medio (imagen)
- Subir: `tofu.png` (de docs/campaigns/2026-05-dia-madre/armonizacion-facial/banners/tofu.png)
- Si Meta sugiere "Customize media for placement": dejar la 9:16 para todos los placements (Meta hace crop automático)

##### Texto principal (sobre la imagen)
```
Tu rostro, a tu manera. Una pausa para verte como te ves cuando nadie te mira. Sin permisos, sin explicaciones.
```

##### Título (debajo de la imagen)
```
Decide por ti
```

##### Descripción (texto pequeño, opcional)
```
Livskin Cusco
```

##### Llamada a la acción
- Seleccionar **"Más información"** (Learn More)

##### URL del sitio web
```
https://campanas.livskin.site/dia-madre-armonizacion-2026/?src=tofu&utm_source=facebook&utm_medium=paid&utm_campaign=arm-may-2026&utm_content=tofu
```

##### Click "Guardar borrador" → seguir con Ad MOFU

---

#### 6.2 Ad MOFU → Landing

##### Nombre del anuncio
```
MOFU-Landing-DM2026
```

##### Mismo Identity, formato, página

##### Medio
- Subir: `mofu.png`

##### Texto principal
```
Sin perder naturalidad. Cada rostro tiene su propia forma de armonizar. Conoce el tuyo, sin presión.
```

##### Título
```
Conoce tu enfoque
```

##### Descripción
```
Livskin Cusco
```

##### Llamada a la acción
- **"Más información"**

##### URL del sitio web
```
https://campanas.livskin.site/dia-madre-armonizacion-2026/?src=mofu&utm_source=facebook&utm_medium=paid&utm_campaign=arm-may-2026&utm_content=mofu
```

##### Click "Guardar borrador" → vamos al Ad Set 2

---

### Paso 7: Volver al nivel campaña + crear Ad Set 2 — "WhatsApp directo"

1. Click "← Volver a la campaña" o navegar arriba al nivel campaña
2. Click **"+ Crear"** → **"Conjunto de anuncios"**

#### 7.1 Nombre
```
WhatsApp directo - Cusco F30-55 - Armonización Facial
```

#### 7.2 Conversion Location
- Seleccionar: **"Aplicaciones de mensajería"** (Messaging apps)
- App: ✅ **WhatsApp**
- ❌ Messenger (no marcar)
- ❌ Instagram (no marcar)

#### 7.3 Performance goal
- "Maximizar el número de conversaciones" (Maximize conversations)

#### 7.4 Facebook Page + WhatsApp number
- Page: Livskin
- WhatsApp: `+51980727888`

#### 7.5 Budget & schedule
- Spend limits del ad set:
  - Mínimo: **30** USD
  - Máximo: **50** USD
- Schedule: idéntico al Ad Set 1 (5/5 06:00 → 9/5 23:59)

#### 7.6 Audience
- **EXACTAMENTE LA MISMA AUDIENCE QUE EL AD SET 1**
- Tip: en el Ad Set 1 (Landing) puedes hacer "Save audience" con un nombre antes de salir, y luego en este ad set "Use saved audience"
- O re-introduce manualmente: ubicaciones, edad, género, idiomas, las 4 CAs, los 6 intereses

#### 7.7 Placements
- Advantage+ placements

#### 7.8 Click "Siguiente"

---

### Paso 8: Crear Ad del Ad Set "WhatsApp" (1 ad)

#### 8.1 Ad BOFU → WhatsApp

##### Nombre del anuncio
```
BOFU-WhatsApp-DM2026
```

##### Identidad
- Page Livskin + Instagram

##### Formato
- Imagen única

##### Medio
- Subir: `bofu.png`

##### Texto principal
```
Inicia tu Armonización Facial. Definimos la combinación ideal para ti, con criterio profesional.
```

##### Título
```
Agenda tu evaluación
```

##### Descripción
```
Livskin Cusco
```

##### Llamada a la acción
- **"Enviar mensaje"** (Send Message)

##### Customize message (mensaje pre-poblado)
- Toggle **"Personalizar mensaje"** ON
- Pegar exacto:
  ```
  Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB-BOFU]
  ```

##### Click "Guardar borrador"

---

### Paso 9: Review + publish (5 min)

1. Click **"Revisar"** (arriba a la derecha)
2. Verificar pantalla "Resumen de la campaña":
   - Campaign: "Livskin — Día de la Madre 2026 — Armonización Facial" ✅
   - Budget: $100 lifetime CBO ✅
   - Ad sets: 2 ✅
   - Ads: 3 ✅
   - Schedule: 5/5 06:00 → 9/5 23:59 ✅
   - Spend limits: AS1 50-70, AS2 30-50 ✅
3. Si todo OK: click **"Publicar"**
4. Meta envía a review (4-24h)
5. Status: cambiará de "En revisión" → "Activo" cuando aprueben

---

### Paso 10: Verificación post-publish

Cuando Meta apruebe:

1. Status del Campaign = "Activo" ✅
2. Status de cada Ad = "Activo" ✅
3. Si algún Ad rechazado:
   - Ver razón en Ads Manager (columna "Estado")
   - Si es Health-related → ajustar copy + resubmit
   - Si es image issue → cambiar banner + resubmit

---

## 4. Smoke test pre-spend significativo

Cuando Meta apruebe pero ANTES de gastar mucho:

### Tu acción (Dario):
1. Desde tu celular (NO admin), navegá a Facebook/Instagram
2. Buscá manualmente alguno de los ads (puede tardar)
3. Para los Ads de Landing (TOFU/MOFU):
   - Click en "Más información"
   - Verificar que abre `campanas.livskin.site/dia-madre-armonizacion-2026/?src=tofu` (o `mofu`)
   - Aceptar consent modal
   - Click en cualquier botón WhatsApp del landing
   - Verificar que el mensaje pre-poblado contiene `[ARM-MAY-FB-TOFU-WEB]` (o `MOFU-WEB`)
4. Para el Ad de WhatsApp (BOFU):
   - Click en "Enviar mensaje"
   - Verificar que abre WhatsApp con `+51980727888`
   - Mensaje pre-poblado: `Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB-BOFU]`
5. **NO mandes el mensaje** (sería test que ensucia data). Solo verificá.

### Mi acción (Claude):
- Pixel Test Events: confirmar PageView desde el landing
- Verificar audit log ERP por si hay events fluyendo

---

## 5. Daily checks durante campaña (5 min cada mañana)

1. Abrir Ads Manager → "Livskin — Día de la Madre 2026 — Armonización Facial"
2. Sacar screenshots de:
   - Campaña: impresiones, gasto, clics, mensajes, CPM, CTR
   - Cada ad set (cómo está distribuyendo CBO)
   - Cada ad: CTR + reach
3. Pasar screenshots al chat
4. Yo armo `daily-reports/YYYY-MM-DD.md` con análisis + recomendaciones
5. Si recomiendo pause/swap → vos lo ejecutás con un click

---

## 6. Checklist consolidado

### Pre-launch (Día -1)
- [ ] Account Quality verificado (Excellent/Good)
- [ ] Pixel firea events recientes
- [ ] FB Page tiene WhatsApp `+51980727888` conectado
- [ ] Banners 9:16 disponibles (TOFU, MOFU, BOFU) en `armonizacion-facial/banners/`
- [ ] Landing PREVIEW + STABLE validados (consent modal aparece, shortcode injection funciona)
- [ ] Cheat sheet doctora impreso

### Launch (Día 1)
- [ ] Pasos 1-9 ejecutados
- [ ] Review final ✅
- [ ] Publish ✅
- [ ] (esperar aprobación Meta)

### Smoke test (post-aprobación, pre-spend significativo)
- [ ] Test desde celular: ad → URL/Send Message correcto
- [ ] Pixel events fluyendo
- [ ] Shortcodes correctos en mensajes WA
- [ ] Spend rate normal (<$5 primeras 6h)

### Durante campaña (Día 2-5)
- [ ] Daily check 1 (martes)
- [ ] Daily check 2 (miércoles)
- [ ] Daily check 3 (jueves)
- [ ] Daily check 4 (viernes)
- [ ] Doctora llena tracking sheet diariamente

### Post-campaña (Día 7-8)
- [ ] Spend final = $100 (o cercano)
- [ ] Pause campaña manualmente si quedó budget
- [ ] Export final metrics CSV de Ads Manager
- [ ] Sesión post-mortem 2-3h
- [ ] Llenar `post-mortem.md`
- [ ] Procesar `_doctrine-feedback.md`
- [ ] Cierre del modo bootstrap (principio #13)

---

## 7. Recursos rápidos

- **Ads Manager**: https://www.facebook.com/adsmanager/manage/campaigns?act=2885433191763149
- **Events Manager**: https://business.facebook.com/events_manager2/list/datasets
- **Account Quality**: https://business.facebook.com/accountquality
- **Audiences**: https://business.facebook.com/asset_library/audiences
- **Page Settings**: https://business.facebook.com/settings/pages
- **Billing**: https://business.facebook.com/billing
- **Landing PREVIEW URL**: https://campanas.livskin.site/dia-madre-armonizacion-2026/

---

**Si algo se desvía del checklist → parar, screenshot, escribirme. Cero improvisación durante el setup.**
