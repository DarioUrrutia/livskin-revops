# Tracking — Campaña Día de la Madre 2026 (umbrella Armonización Facial)

> **Cheat sheet consolidado** — para Dario al monitorear + para la doctora al recibir mensajes WhatsApp.

---

## Shortcode único

```
[ARM-MAY-FB]
```

Significado: lead vino de **Armonización Facial Día de la Madre 2026 — Facebook/Instagram**.

**1 solo shortcode** para toda la campaña (refactored 2026-05-04 desde 2 originales `[BTX-MAY-FB]` + `[AH-MAY-FB]` → 1 unificado `[ARM-MAY-FB]`).

---

## Mensaje WhatsApp pre-poblado (en CTA dentro de la landing)

**Texto**:
```
Hola, vengo del aviso de Livskin Día de la Madre [ARM-MAY-FB]
```

**URL completa**:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BARM-MAY-FB%5D
```

**Donde se usa**:
- Como `href` del botón "Reservar por WhatsApp" / "Conversar con la doctora" en la landing umbrella
- Yo lo configuro como parte de los 10 pasos de adaptación cuando me pases la landing casi-final

---

## UTMs estandarizadas (a nivel ad creative)

```
utm_source=facebook | instagram (Meta auto-detect según placement)
utm_medium=paid
utm_campaign=dia-madre-2026
utm_content=arm-<funnel>     # arm-tofu / arm-mofu / arm-bofu
utm_term={{adset.id}}        # Meta auto-rellena
```

**3 valores únicos de utm_content** (vs 18 que teníamos en versión 2-tratamientos):

| Banner | utm_content |
|---|---|
| TOFU | `arm-tofu` |
| MOFU | `arm-mofu` |
| BOFU | `arm-bofu` |

Las variantes de aspect ratio comparten el MISMO `utm_content` del banner principal — Meta serve según placement automático.

---

## Cheat sheet doctora (imprimir o pegar en WhatsApp Web)

**Cuando la doctora reciba un mensaje nuevo en WhatsApp**:

1. **Buscar el código entre corchetes** en el primer mensaje del lead:
   - Si dice `[ARM-MAY-FB]` → lead de la campaña Día de la Madre
   - Si NO tiene código → lead orgánico (anotar igualmente con código `[ORGANIC]`)

2. **Anotar en Google Sheet** "Livskin Tracking 2026-05 Día de la Madre" con columnas:

| # | Columna | Descripción |
|---|---|---|
| A | Fecha | YYYY-MM-DD del primer mensaje |
| B | Hora | HH:MM cuándo llegó |
| C | Phone | Número con +51 |
| D | Shortcode | `ARM-MAY-FB` o `ORGANIC` |
| E | **Tratamiento_interés expresado** | ⭐ Lo que el lead diga en chat: "Botox", "rellenos", "armonización", "no especificó", etc. |
| F | Status | Nuevo / Contactado / Agendado / Asistió / Cliente / No-show / Descartado |
| G | Notas | Comentarios libres |

**⭐ Importante**: la columna E (tratamiento expresado) es **el dato más valioso**. Aunque la campaña no menciona producto, los leads naturalmente expresan qué quieren. Esto valida la hipótesis "qué tratamiento prefiere la audiencia espontáneamente".

---

## Métricas a monitorear (daily, sin Marketing API)

Dario abre Ads Manager cada mañana → screenshot/CSV → pasa a Claude:

| Métrica | Dónde encontrar | Target / alarma |
|---|---|---|
| Spend total | Vista de campaña | Distribuido en 5 días |
| Impresiones (total + por ad) | Vista de campaña + por ad | Crecimiento lineal |
| Frequency | Vista de ad set | Cap 4, alarma >4 |
| CTR (click-through-rate) | Por ad creative | Target 1-2%, alarma <0.5% (swap) |
| CPM | Por ad set | Target $7-15 USD |
| Pixel "Lead" events | Events Manager | Target 5-15 totales |
| Cost per Lead | Calculado spend / leads | Target $7-20 USD |

**Acciones de Claude post-screenshot diario:**
1. Update `daily-reports/YYYY-MM-DD.md`
2. Identificar ads con CTR <0.5% → recomendar pause
3. Identificar audience saturado (frequency >4 sin más leads) → recomendar ampliar
4. Cross-check Pixel Lead events vs tracking sheet manual de la doctora

---

## Cross-check Pixel + sheet manual

Al final de la campaña:

```
Total leads = (form fills via Pixel Lead event) + (mensajes WhatsApp con [ARM-MAY-FB] en sheet doctora)
```

Si hay divergencia >20% entre los dos canales:
- Form leads >> WA leads → CTA WhatsApp en landing podría estar roto, investigar
- WA leads >> form leads → form de landing tiene fricción, optimizar

---

## Audit events automáticos (capturados sin esfuerzo)

- ✅ Pixel `PageView` cada vez que alguien llega a la landing
- ✅ Pixel `Lead` event al submit form (configurado en Custom Conversion)
- ✅ Pixel `Click` event al click WA CTA
- ✅ CAPI server-side via n8n G3 cuando se crea el lead en ERP
- ✅ ERP `audit_log` registra cada lead nuevo

---

## Cleanup post-campaña

- [ ] Exportar Google Sheet a CSV
- [ ] Cruzar con métricas Ads Manager exportadas
- [ ] Generar análisis CAC real en `post-mortem.md`
- [ ] Archivar `2026-05-dia-madre/` a `docs/campaigns/_archive/`
