# Tracking — Armonización Facial — Día de la Madre 2026

> Tracking unificado de la campaña umbrella. Cheat sheet consolidado para la doctora: [`../tracking.md`](../tracking.md).

---

## Shortcode manual unificado

```
[ARM-MAY-FB]
```

Significado: lead vino del ad de **Armonización Facial Día de la Madre 2026 — Facebook/Instagram**.

**1 solo shortcode para toda la campaña** (vs 2 que teníamos antes con tratamientos separados). La doctora tiene UN código a recordar.

Cuando alguien clickea el ad → llega a la landing → tiene CTA WhatsApp con mensaje pre-poblado:
```
Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB]
```

URL completa del WA href en la landing:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BARM-MAY-FB%5D
```

---

## UTMs por banner (3 banners)

Cada ad de Meta tiene URL parameters que se setean al configurar el ad en Ads Manager. La landing recibe el lead con UTMs preservadas.

### Banner TOFU

```
utm_source=facebook
utm_medium=paid
utm_campaign=dia-madre-2026
utm_content=arm-tofu
utm_term={{adset.id}}
```

URL completa al destination:
```
https://campanas.livskin.site/dia-madre-armonizacion-2026/?utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=arm-tofu&utm_term={{adset.id}}
```

### Banner MOFU

```
utm_content=arm-mofu
```

URL completa:
```
https://campanas.livskin.site/dia-madre-armonizacion-2026/?utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=arm-mofu&utm_term={{adset.id}}
```

### Banner BOFU

```
utm_content=arm-bofu
```

URL completa:
```
https://campanas.livskin.site/dia-madre-armonizacion-2026/?utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=arm-bofu&utm_term={{adset.id}}
```

**Tabla resumen de utm_content** (3 valores únicos vs 18 que teníamos antes):

| Banner | utm_content |
|---|---|
| TOFU | `arm-tofu` |
| MOFU | `arm-mofu` |
| BOFU | `arm-bofu` |

Notar: las **variantes de aspect ratio** (1:1, 4:5, 9:16) usan el MISMO `utm_content` del banner principal — no las diferenciamos en URL porque Meta las serve según placement automáticamente.

---

## Pixel events esperados

Cuando el lead navega:

1. **Click en ad** → Meta marca el click
2. **Llegada a landing** → Pixel `PageView` event
3. **Submit form** → Pixel `Lead` event (vía evento custom + script `livskin-tracking.js`)
4. **Click CTA WhatsApp** → Pixel custom event (via tracking.js auto-detect)
5. **Server-side**: CAPI emit via n8n G3 cuando se crea el lead en ERP (post-form submit)

---

## Reportes de performance esperados

| Métrica | Target |
|---|---|
| Spend total | $100 lifetime distribuido en 5 días |
| Impresiones | 7-14K |
| CTR landing | 1-2% |
| Cost per click landing | $1-3 USD |
| Conversion rate landing → form lead | 2-5% (target: 5-15 leads totales) |
| Click WA CTA en landing → mensaje | 30-50% (la mayoría que dan click sí mandan) |
| Mensajes con `[ARM-MAY-FB]` totales | 5-15 |

---

## Cross-check con tracking sheet doctora

Cada vez que la doctora reciba mensaje con `[ARM-MAY-FB]`:

1. Anota en Google Sheet:
   - Phone, Shortcode `ARM-MAY-FB`, Tratamiento_interés que la persona expresa, Status
   - **Importante**: si la persona en chat dice "quiero Botox" o "quiero rellenos" → la doctora anota qué dijo (dato valioso para entender qué decisión espontánea hace la audiencia)
2. Al final de campaña:
   - Cross-check leads con `[ARM-MAY-FB]` en sheet vs reportados por Pixel + Meta Ads Manager
   - Análisis: ¿qué tratamiento expresaron mayoritariamente los leads? Botox vs AH vs ambos vs no especificó

---

## Insight valioso — captura indirecta de preferencia tratamiento

Aunque la campaña no menciona Botox/AH específico, **los leads naturalmente expresan en chat qué quieren**. La doctora captura esto en Google Sheet.

Post-campaña tendremos data como:
- 60% de los leads dijeron "Botox" inicialmente
- 25% dijeron "armonización" sin especificar
- 10% dijeron "rellenos" / "ácido hialurónico"
- 5% otros (limpieza, etc.)

Esto INFORMA la próxima campaña: validar el split 60/40 Botox/AH original con data orgánica de la conversación.

---

## Cross-link

- Tracking consolidado de campaña: [`../tracking.md`](../tracking.md)
- Plan operativo: [`../plan.md`](../plan.md)
- Checklist UI: [`../ads-manager-checklist.md`](../ads-manager-checklist.md)
- Copies aprobados: [`copies.md`](copies.md)
- Landing: [`landing.md`](landing.md)
