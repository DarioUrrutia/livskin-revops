# Tracking — Campaña Día de la Madre 2026

> **Cheat sheet consolidado** — para Dario al monitorear + para la doctora al recibir mensajes WhatsApp.

---

## Shortcodes manuales (para la doctora)

Cuando alguien clickea el ad de Facebook/Instagram, WhatsApp se abre con un mensaje pre-poblado que contiene un código entre corchetes. La doctora ve ese código en el primer mensaje del lead.

| Código | Significado | Qué tratamiento promociona el ad |
|---|---|---|
| `[BTX-MAY-FB]` | Lead vino del ad de **Botox** Día de la Madre 2026 | Botox |
| `[AH-MAY-FB]` | Lead vino del ad de **Ácido Hialurónico** Día de la Madre 2026 | Ácido Hialurónico |

**Si el mensaje no tiene código entre corchetes**: lead orgánico (no de campaña). Anotar igualmente con código `[ORGANIC]`.

---

## Mensajes WhatsApp pre-poblados (lo que el lead manda)

### Botox

```
Hola, vengo del aviso de Livskin Día de la Madre [BTX-MAY-FB]
```

URL de href para los ads:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BBTX-MAY-FB%5D
```

### Ácido Hialurónico

```
Hola, vengo del aviso de Livskin Día de la Madre [AH-MAY-FB]
```

URL de href para los ads:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BAH-MAY-FB%5D
```

---

## UTMs estandarizadas (a nivel ad creative)

Aunque esta campaña va a WhatsApp directo (no a landings), las UTMs se incluyen en los ads para tracking en Pixel + CAPI events.

**Estructura estándar:**

```
utm_source=facebook | instagram (según placement Meta auto-detecte)
utm_medium=paid
utm_campaign=dia-madre-2026
utm_content=<treatment>-<funnel>-<aspect_ratio>
utm_term=<adset_id_meta>
```

**Ejemplos por banner:**

| Treatment | Funnel | Aspect ratio | utm_content |
|---|---|---|---|
| Botox | TOFU | 1:1 | `botox-tofu-1x1` |
| Botox | TOFU | 4:5 | `botox-tofu-4x5` |
| Botox | TOFU | 9:16 | `botox-tofu-9x16` |
| Botox | MOFU | 1:1 | `botox-mofu-1x1` |
| Botox | MOFU | 4:5 | `botox-mofu-4x5` |
| Botox | MOFU | 9:16 | `botox-mofu-9x16` |
| Botox | BOFU | 1:1 | `botox-bofu-1x1` |
| Botox | BOFU | 4:5 | `botox-bofu-4x5` |
| Botox | BOFU | 9:16 | `botox-bofu-9x16` |
| AH | TOFU | 1:1 | `ah-tofu-1x1` |
| ... | ... | ... | ... |

**Total**: 18 combinaciones únicas (9 por tratamiento × 2 tratamientos).

---

## Google Sheet de tracking manual (para la doctora)

**Ubicación**: Google Drive → "Livskin Tracking 2026-05 Día de la Madre"

**Compartido con**: Dario + doctora (edit)

**Columnas**:

| # | Columna | Descripción |
|---|---|---|
| A | Fecha | YYYY-MM-DD del primer mensaje |
| B | Hora | HH:MM cuándo llegó |
| C | Phone | Número del lead (con +51) |
| D | Shortcode visto | `[BTX-MAY-FB]` / `[AH-MAY-FB]` / `[ORGANIC]` |
| E | Tratamiento de interés expresado | Lo que dijo el lead en la conversación (puede no coincidir con shortcode) |
| F | Status | Nuevo / Contactado / Agendado / Asistió / Cliente / No-show / Descartado |
| G | Notas | Comentarios libres de la doctora |

**Status flow**:
- Nuevo → Contactado (la doctora respondió) → Agendado (cita confirmada) → Asistió (vino) → Cliente (compró)
- O: Nuevo → Contactado → No-show / Descartado

**Update frequency**: la doctora actualiza al final de cada día de campaña.

---

## Métricas a monitorear (daily, sin Marketing API)

Dario abre Ads Manager cada mañana → screenshot + paso a Claude:

**Daily key metrics:**

| Métrica | Dónde la encuentro en Ads Manager | Target / alarma |
|---|---|---|
| Impresiones (total + por ad set) | Vista de campaña | Debería crecer linealmente |
| Frequency | Vista de ad set | Cap a 3-4 (audience chica) — alarma si >4 |
| CTR (click-through-rate) | Por ad creative | Target 1-2%, alarma <0.5% (creative malo, swap) |
| CPM (cost per mille) | Por ad set | Target $7-15 USD para Cusco |
| Costo por mensaje | Por ad set | Target $5-15 USD, alarma >$20 |
| Mensajes recibidos | Reportado por Meta + cross-check con tracking sheet | Target 6-15 totales en 5 días |
| Spend total (vs budget $100) | Vista de campaña | Debe gastarse uniformemente |

**Acciones de Claude post-screenshot diario:**
1. Update `daily-reports/YYYY-MM-DD.md`
2. Identificar creatives con CTR <0.5% → recomendar pause
3. Identificar audience saturado (frequency >4 sin más leads) → recomendar pause o ampliar
4. Comparar Botox vs AH: si uno está dominando, recomendar reasignar budget

---

## Audit events (capturados automáticamente)

Si configuramos un Custom Conversion en Meta para "Click-to-WhatsApp Lead":
- Cada click dispara Pixel `Lead` event
- CAPI server-side via n8n G3 también dispara (deduplicado por event_id)
- ERP audit log captura `tracking.capi_event_emitted`

NOTA: para esta campaña sin landings, el Pixel solo firea en el momento del click del ad (no hay landing PageView). El "Lead" event llega a Meta directamente desde el botón Click-to-WhatsApp si Meta lo soporta como conversion automática.

---

## Cleanup post-campaña (al cerrar carpeta)

- [ ] Exportar Google Sheet a CSV
- [ ] Importar CSV a tabla `campaign_manual_tracking` en ERP (modelo a crear post-Bridge si hay valor recurrente)
- [ ] Cruzar con métricas Ads Manager exportadas
- [ ] Generar análisis CAC real en `post-mortem.md`
- [ ] Archivar `2026-05-dia-madre/` a `docs/campaigns/_archive/`
