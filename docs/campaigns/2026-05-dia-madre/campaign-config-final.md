---
type: campaign-config-final
version: 1.0
status: APROBADO 2026-05-04
campaign: 2026-05-dia-madre
---

# 🎯 Campaign Config Final — Livskin Día de la Madre 2026 (Armonización Facial)

> **Doc maestro listo para copiar y pegar en Ads Manager.**
> Aprobado 2026-05-04 con estructura 3 ad sets · 6 ads · 3 banners.
> Copies validados contra `docs/brand/copy-principles.md` v0.1 + checklist 4 preguntas.

---

## 1. Setup global de la campaña

| Campo | Valor para copiar |
|---|---|
| **Ad account** | `2885433191763149` (Livskin Perú) |
| **Pixel** | `4410809639201712` (Livksin Pixel 2026) |
| **FB Page** | Livskin |
| **WhatsApp number** | `+51 980 727 888` |
| **Nombre campaña** | `Livskin — Día de la Madre 2026 — Armonización Facial` |
| **Buying type** | Auction |
| **Special Ad Category** | Declarar que NO es categoría especial |
| **Objective** | Tráfico (Maximize Link Clicks) |
| **Budget** | **S/ 296** lifetime |
| **CBO** | ON ✅ |
| **Bid strategy** | Mayor volumen (default) |
| **A/B test** | NO |
| **Schedule** | Inicio: 2026-05-05 06:00 (Lima) · Fin: 2026-05-09 23:59 |

---

## 2. AD SET 1 — COLD-LANDING (S/ 148, 50%)

```
Nombre: Cold-Landing - Cusco F30-55 - Armonización Facial
Conversion location: Sitio web
Performance goal: Maximizar clics en el enlace
Pixel: Livksin Pixel 2026 (4410809639201712)

Spend limits:
   Mínimo: S/ 100
   Máximo: S/ 175

Schedule: 2026-05-05 06:00 → 2026-05-09 23:59 (mismo que campaña)

UBICACIÓN
   Cusco, Perú · radio 8 km · "Personas que viven en este lugar"

EDAD: 30 – 55
GÉNERO: Mujeres
IDIOMA: Spanish (todos)

INTERESES (Include - Detailed targeting):
   • Skincare
   • Beauty
   • Aesthetic medicine
   • Cosmetic procedures
   • Anti-aging
   • Mother's Day (si aparece para Perú)

CUSTOM AUDIENCES — INCLUDE:
   (ninguno — esta corrida sin LAL, recolectamos data para siguiente campaña)

CUSTOM AUDIENCES — EXCLUDE (clave):
   • TODO COMPLETO FB
   • personas que hicieron clic en llamada de accion
   • Interaccion con la pagina 365 dias
   • PERSONA QUE INTERACTUARON 28 DIAS

Detailed targeting expansion: ON ✅
Placements: Advantage+
```

### 🟩 Ad COLD-1 — TOFU → Landing

```
Nombre del anuncio: TOFU-Landing-DM2026

Identidad: FB Page Livskin + Instagram vinculada (auto)
Formato: Imagen única
Imagen: docs/campaigns/2026-05-dia-madre/armonizacion-facial/banners/tofu.png

────── COPY ──────
Texto principal:
Tu rostro, a tu manera. Una pausa para verte como te ves cuando nadie te mira. Sin permisos, sin explicaciones.

Título:
Decide por ti

Descripción:
Livskin Cusco

────── DESTINO ──────
CTA Meta: Más información (Learn More)

URL del sitio web (pegar exacto):
https://campanas.livskin.site/dia-madre-armonizacion-2026/?src=tofu&utm_source=facebook&utm_medium=paid&utm_campaign=arm-may-2026&utm_content=tofu&utm_term=cold-landing
```

### 🟧 Ad COLD-2 — MOFU → Landing

```
Nombre del anuncio: MOFU-Landing-DM2026

Identidad: FB Page Livskin + Instagram vinculada
Formato: Imagen única
Imagen: docs/campaigns/2026-05-dia-madre/armonizacion-facial/banners/mofu.png

────── COPY ──────
Texto principal:
Sin perder naturalidad. Cada rostro tiene su propia forma de armonizar. Conoce el tuyo, sin presión.

Título:
Conoce tu enfoque

Descripción:
Livskin Cusco

────── DESTINO ──────
CTA Meta: Más información

URL del sitio web (pegar exacto):
https://campanas.livskin.site/dia-madre-armonizacion-2026/?src=mofu&utm_source=facebook&utm_medium=paid&utm_campaign=arm-may-2026&utm_content=mofu&utm_term=cold-landing
```

---

## 3. AD SET 2 — COLD-WA (S/ 74, 25%)

```
Nombre: Cold-WA - Cusco F30-55 - Armonización Facial
Conversion location: Aplicaciones de mensajería
   App: ✅ WhatsApp
   ❌ Messenger
   ❌ Instagram
Performance goal: Maximizar clics en el enlace
   (Nota: "Conversaciones" no se puede seleccionar cuando el objetivo
    de campaña es Tráfico. Optimizamos por Link Clicks; la atribución
    de mensajes reales se hace manual via shortcode.)

Page: Livskin
WhatsApp: +51 980 727 888

Spend limits:
   Mínimo: S/ 50
   Máximo: S/ 90

Schedule: igual que la campaña

────── AUDIENCE ──────
EXACTAMENTE LA MISMA QUE COLD-LANDING:
   • Cusco · 8km · F 30-55 · Spanish
   • Intereses: Skincare, Beauty, Aesthetic medicine,
                Cosmetic procedures, Anti-aging, Mother's Day
   • EXCLUDE las 4 CAs históricas
   • Sin LAL (esta corrida la recolecta para la próxima)

Tip: en Ad Set 1 antes de salir → "Save audience" → reusar acá.

Placements: Advantage+
```

### 🟧 Ad COLDWA-1 — MOFU → WhatsApp

```
Nombre del anuncio: MOFU-WhatsApp-COLDWA-DM2026

Identidad: FB Page Livskin + Instagram vinculada
Formato: Imagen única
Imagen: docs/campaigns/2026-05-dia-madre/armonizacion-facial/banners/mofu.png

────── COPY ──────
Texto principal:
Sin perder naturalidad. Conversemos sobre tu rostro cuando quieras — sin presión, sin compromiso.

Título:
Conversemos

Descripción:
Livskin Cusco

────── DESTINO ──────
CTA Meta: Enviar mensaje

Toggle "Personalizar mensaje" ON
Mensaje pre-poblado (pegar exacto):
Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB-MOFU-COLDWA]
```

### 🟥 Ad COLDWA-2 — BOFU → WhatsApp

```
Nombre del anuncio: BOFU-WhatsApp-COLDWA-DM2026

Identidad: FB Page Livskin + Instagram vinculada
Formato: Imagen única
Imagen: docs/campaigns/2026-05-dia-madre/armonizacion-facial/banners/bofu.png

────── COPY ──────
Texto principal:
Inicia tu Armonización Facial este Día de la Madre. Definimos la combinación ideal para ti, con criterio profesional.

Título:
Agenda tu evaluación

Descripción:
Livskin Cusco

────── DESTINO ──────
CTA Meta: Enviar mensaje

Toggle "Personalizar mensaje" ON
Mensaje pre-poblado (pegar exacto):
Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB-BOFU-COLDWA]
```

---

## 4. AD SET 3 — WARM (S/ 74, 25%)

```
Nombre: Warm - Reactivación Histórica - Armonización Facial
Conversion location: Aplicaciones de mensajería → WhatsApp
Performance goal: Maximizar clics en el enlace
   (Nota: "Conversaciones" no se puede seleccionar cuando el objetivo
    de campaña es Tráfico. Optimizamos por Link Clicks; la atribución
    de mensajes reales se hace manual via shortcode.)

Page: Livskin
WhatsApp: +51 980 727 888

Spend limits:
   Mínimo: S/ 50
   Máximo: S/ 90

Schedule: igual que la campaña

────── AUDIENCE ──────
SOLO Custom Audiences (sin restricciones encima):
   ✅ TODO COMPLETO FB
   ✅ personas que hicieron clic en llamada de accion
   ✅ Interaccion con la pagina 365 dias
   ✅ PERSONA QUE INTERACTUARON 28 DIAS

NO tocar geo, edad, género, idioma — las CAs ya son listas filtradas.

Placements: Advantage+
```

### 🟧 Ad WARM-1 — MOFU → WhatsApp

```
Nombre del anuncio: MOFU-WhatsApp-WARM-DM2026

Identidad: FB Page Livskin + Instagram vinculada
Formato: Imagen única
Imagen: docs/campaigns/2026-05-dia-madre/armonizacion-facial/banners/mofu.png

────── COPY ──────
Texto principal:
Volvemos a aparecer este Día de la Madre. Sin perder naturalidad, conversemos cuando quieras.

Título:
Conversemos

Descripción:
Livskin Cusco

────── DESTINO ──────
CTA Meta: Enviar mensaje

Toggle "Personalizar mensaje" ON
Mensaje pre-poblado (pegar exacto):
Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB-MOFU-WARM]
```

### 🟥 Ad WARM-2 — BOFU → WhatsApp

```
Nombre del anuncio: BOFU-WhatsApp-WARM-DM2026

Identidad: FB Page Livskin + Instagram vinculada
Formato: Imagen única
Imagen: docs/campaigns/2026-05-dia-madre/armonizacion-facial/banners/bofu.png

────── COPY ──────
Texto principal:
Inicia tu Armonización Facial este Día de la Madre. La combinación ideal para ti, con criterio profesional.

Título:
Agenda tu evaluación

Descripción:
Livskin Cusco

────── DESTINO ──────
CTA Meta: Enviar mensaje

Toggle "Personalizar mensaje" ON
Mensaje pre-poblado (pegar exacto):
Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB-BOFU-WARM]
```

---

## 5. Tracking shortcodes consolidados

| Shortcode que recibe la doctora | Origen del lead | Calidad |
|---|---|---|
| `[ARM-MAY-FB-TOFU-WEB]` | Cold TOFU → landing → click WA | 🟩 Caliente (leyó info) |
| `[ARM-MAY-FB-MOFU-WEB]` | Cold MOFU → landing → click WA | 🟧 Tibio (leyó info) |
| `[ARM-MAY-FB-MOFU-COLDWA]` | Cold MOFU directo a WA (no vio web) | 🟧 Tibio (sin contexto) |
| `[ARM-MAY-FB-BOFU-COLDWA]` | Cold BOFU directo a WA (no vio web) | 🟥 Frío educado |
| `[ARM-MAY-FB-MOFU-WARM]` | Warm MOFU directo a WA (audiencia histórica) | 🟧 Reactivación tibia |
| `[ARM-MAY-FB-BOFU-WARM]` | Warm BOFU directo a WA (audiencia histórica) | 🟥 Reactivación cierre |
| `[ARM-MAY-FB]` (sin sufijo) | Tráfico orgánico desde landing | ⚪ Mixto |

---

## 6. Validación contra `copy-principles.md` v0.1

### Palabras prohibidas — verificación
- ❌ "Botox" / "ácido hialurónico" en TOFU/MOFU → ✅ NO aparecen en los copies de texto (solo "Armonización Facial" en BOFU, que SÍ permite mencionar tratamiento)
- ❌ "arruga" / "envejecimiento" / "líneas" → ✅ NO aparecen
- ❌ "promoción" / "descuento" / "antes del" → ✅ NO aparecen
- ❌ verbos de empuje ("compra", "aprovecha", "reserva ya") → ✅ NO aparecen

### Verbos de poder — verificación
- ✅ "Decide", "Conoce", "Conversemos", "Inicia", "Agenda" — todos presentes según funnel

### Checklist 4 preguntas (`brand-system.md` § 6) aplicado a la campaña

| Ad | ¿Qué identidad activa? | ¿Qué emoción? | ¿Qué decisión sugiere? | ¿Qué NO dice? |
|---|---|---|---|---|
| **COLD-1 TOFU** | Mujer que tiene derecho a una pausa para sí misma | Calma, autoría, no-permiso | Ver tu rostro como tú quieres | Producto, precio, urgencia |
| **COLD-2 MOFU** | Mujer con criterio que reconoce que cada rostro es único | Curiosidad sin presión | Conocer tu propio enfoque | Producto, comparación, fórmula estándar |
| **COLDWA-1 MOFU** | Mujer que prefiere conversar antes de leer | Tranquilidad, conversación | Iniciar conversación sin compromiso | Producto, cierre, urgencia |
| **COLDWA-2 BOFU** | Mujer decidida que sabe lo que busca | Acción tranquila | Iniciar Armonización Facial | Precio, descuento, "antes del 11" |
| **WARM-1 MOFU** | Cliente conocida revisitada | Reconocimiento, retorno | Reactivar conversación | Reproches, agresividad |
| **WARM-2 BOFU** | Cliente lista para cerrar | Decisión cómoda | Agendar evaluación | Precio, urgencia barata |

---

## 7. Resumen visual

```
S/ 296 lifetime CBO

╔═════════════════════════╦═════════════╦═══════╗
║         AD SET          ║   BUDGET    ║  ADS  ║
╠═════════════════════════╬═════════════╬═══════╣
║ COLD-LANDING            ║ S/ 148 (50%)║   2   ║
║   → Sitio web           ║             ║       ║
║   intereses + LAL       ║             ║       ║
╠═════════════════════════╬═════════════╬═══════╣
║ COLD-WA                 ║ S/  74 (25%)║   2   ║
║   → WhatsApp            ║             ║       ║
║   misma audience        ║             ║       ║
╠═════════════════════════╬═════════════╬═══════╣
║ WARM                    ║ S/  74 (25%)║   2   ║
║   → WhatsApp            ║             ║       ║
║   4 CAs históricas      ║             ║       ║
╚═════════════════════════╩═════════════╩═══════╝

TOTAL: 1 campaign · 3 ad sets · 6 ads · 3 banners únicos
```

---

## 8. Pre-requisitos antes de configurar (Día -1)

- [x] Pixel `4410809639201712` activo (validado: 154 PV últimas 14h)
- [x] Banners disponibles en `armonizacion-facial/banners/`
- [x] Landing live con consent modal funcionando (validado en incógnito)
- [x] Shortcode injection funcionando (parámetro `?src=tofu|mofu` reescribe WA links)
- [x] **DESCARTADO**: LAL — decisión 2026-05-04: esta corrida recolecta seed para LAL futura (objetivo 100+ leads). Cuando tengamos esa seed, LAL en la siguiente campaña.
- [ ] **PENDIENTE**: verificar WhatsApp Business app conectado a FB Page (al crear ad set 2 y 3 confirmamos)
- [ ] **PENDIENTE**: cheat sheet doctora impreso

### 🎯 Objetivo secundario de esta corrida (post-mortem)

Recolectar **mínimo 100 leads/contactos** para tener seed sólida de LAL en la siguiente campaña. Cada lead que entre por:
- Form del landing → guardado en sistema
- WhatsApp con shortcode → guardado en cheat sheet doctora

→ alimenta la base. Post-campaña esos 100+ se convierten en una nueva Custom Audience por phone hash + las CAs Pixel filtradas por UTM. Esa será la seed limpia que falta hoy.

---

**Cualquier desvío del checklist → parar, screenshot, escribirme. Cero improvisación.**
