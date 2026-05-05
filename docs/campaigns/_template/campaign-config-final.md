---
type: campaign-config-final
version: 1.0
status: planning
campaign: {{CAMPAIGN_SLUG}}
---

# 🎯 Campaign Config Final — {{CAMPAIGN_NAME}}

> **Doc maestro listo para copiar y pegar en Ads Manager.**
> Status: `planning` → marcar `approved` antes de pegar en Ads Manager.

---

## 1. Setup global de la campaña

| Campo | Valor |
|---|---|
| **Ad account** | `{{AD_ACCOUNT}}` |
| **Pixel** | `{{PIXEL_ID}}` |
| **FB Page** | (a llenar) |
| **WhatsApp number** | `{{WA_PHONE_E164}}` |
| **Nombre campaña** | `{{CAMPAIGN_NAME}}` |
| **Buying type** | Auction |
| **Special Ad Category** | (declarar — Health requires careful flag) |
| **Objective** | (a llenar — Tráfico / Engagement / Leads / Conversiones) |
| **Budget** | **S/ {{BUDGET_PEN}}** lifetime |
| **CBO** | (decidir ON/OFF) |
| **Bid strategy** | Mayor volumen (default) |
| **A/B test** | NO |
| **Schedule** | Inicio: {{START_DATE}} hora · Fin: {{END_DATE}} hora |

---

## 2. AD SET 1 — (a llenar — nombre)

```
Nombre: (a llenar)
Conversion location: (a llenar)
Performance goal: (a llenar)
Pixel: {{PIXEL_ID}}

Spend limits:
   Mínimo: S/ X
   Máximo: S/ Y

Schedule: {{START_DATE}} → {{END_DATE}}

UBICACIÓN
   (a llenar — geo + radio)

EDAD: X – Y
GÉNERO: (a llenar)
IDIOMA: Spanish (todos)

INTERESES (Include - Detailed targeting):
   • (a llenar)

CUSTOM AUDIENCES — INCLUDE:
   • (a llenar o "ninguno")

CUSTOM AUDIENCES — EXCLUDE:
   • (a llenar — para evitar canibalización con otros ad sets)

Detailed targeting expansion: ON ✅
Placements: Advantage+
```

### 🟩 Ad N — (nombre del ad)

```
Nombre del anuncio: (a llenar)

Identidad: FB Page + Instagram vinculada
Formato: Imagen única
Imagen: (a llenar — path al banner)

────── COPY ──────
Texto principal:
(a llenar)

Título:
(a llenar)

Descripción:
Livskin Cusco

────── DESTINO ──────
CTA Meta: (a llenar — "Más información" / "Enviar mensaje" / etc.)

URL del sitio web (si aplica):
(a llenar con UTMs)

Mensaje pre-poblado WhatsApp (si aplica):
Hola, vengo del aviso de Livskin (a llenar) [{{SHORTCODE_PREFIX}}-X]
```

(repetir bloques para más ads del ad set)

---

## 3. AD SET 2 — (si aplica)

(repetir estructura)

---

## 4. AD SET 3 — (si aplica)

(repetir estructura)

---

## 5. Tracking shortcodes consolidados

| Shortcode que recibe la doctora | Origen del lead | Calidad |
|---|---|---|
| `[{{SHORTCODE_PREFIX}}-...]` | (a llenar) | (a llenar) |

---

## 6. Validación contra `copy-principles.md`

### Palabras prohibidas — verificación
- ❌ Botox / ácido hialurónico en TOFU/MOFU → ✅ verificar en copies
- ❌ arruga / envejecimiento / líneas → ✅ verificar
- ❌ promoción / descuento / antes del → ✅ verificar
- ❌ verbos de empuje (compra, aprovecha, reserva ya) → ✅ verificar

### Verbos de poder — verificación
- ✅ Decide / Conoce / Conversemos / Inicia / Agenda — al menos 1 por copy

### Checklist 4 preguntas (`brand-system.md` § 6)

| Ad | ¿Qué identidad activa? | ¿Qué emoción? | ¿Qué decisión sugiere? | ¿Qué NO dice? |
|---|---|---|---|---|
| (a llenar para cada ad) |  |  |  |  |

---

## 7. Pre-requisitos antes de configurar (Día -1)

- [ ] Pixel verificado funcionando
- [ ] Banners disponibles
- [ ] Landing live (si aplica)
- [ ] Cheat sheet doctora impreso
- [ ] Pre-flight checklist completado (ver `ads-manager-checklist.md` § 2)

---

**Cualquier desvío del checklist → parar, screenshot, escribir al chat. Cero improvisación.**
