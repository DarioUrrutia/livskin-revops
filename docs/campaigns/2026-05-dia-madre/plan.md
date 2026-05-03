# Plan Operativo — Campaña Día de la Madre 2026

> **Status:** 🚀 EN PREPARACIÓN — pendiente aprobación brief.md
> **Frame contextual:** Día de la Madre Perú (Domingo 11 de mayo 2026)
> **Tipo:** Bridge Episode entre Fase 3 (cerrada) y Fase 4 (reescrita post-audit)
> **Doctrina rectora:** principio operativo #11 (deterministic backbone first) + #13 (modo bootstrap)
> **Brief:** ver [`brief.md`](brief.md) — gate de aprobación
> **Configuración técnica detallada:** ver [`campaign-config-draft.md`](campaign-config-draft.md)
> **Checklist Ads Manager UI:** ver [`ads-manager-checklist.md`](ads-manager-checklist.md)

---

## 1. Objetivo REAL

**Maximizar contactos directos a WhatsApp de la doctora durante la ventana del Día de la Madre.**

NO es solo generar data (eso era el Bridge Episode genérico). Esta campaña tiene un objetivo comercial directo:
- Aprovechar el momento contextual (DM peruano)
- Activar identidad de "madre que decide cuidarse"
- Llegar a WhatsApp directo donde la doctora cierra la conversación

Data secundaria que aprendemos (hipótesis del brief):
- ¿Cost-per-message viable en Cusco?
- ¿Botox vs AH cuál mueve más?
- ¿Audience F30-55 Cusco radio 5-8km es suficiente?
- ¿LAL 2-3% mejora performance vs interest-based puro?

---

## 2. Decisión arquitectónica — Opción A (todo Click-to-WhatsApp)

```
Campaign: Livskin — Día de la Madre 2026
   Objective: Engagement → Maximize messages (Click-to-WhatsApp)
   Budget: $100 USD lifetime CBO
   Schedule: 2026-05-05 → 2026-05-09 (5 días corridos)
   Ad account: 2885433191763149 (Business Manager Livskin Perú)
   Pixel: 4410809639201712 (Livskin 2026)

   ├─ Ad Set 1: BOTOX
   │  Budget allocation: 60% (~$60 lifetime)
   │  Audience: ver § 3
   │  Optimization: Lead conversation (WhatsApp)
   │  Placements: Advantage+ (Meta auto-optimiza)
   │  Frequency cap: 3-4 (audience chica de Cusco)
   │  Banners: 9 (3 ideas × 3 aspect ratios)
   │  Destination: WhatsApp con shortcode [BTX-MAY-FB]
   │
   └─ Ad Set 2: ÁCIDO HIALURÓNICO
      Budget allocation: 40% (~$40 lifetime)
      Audience: idéntica a Botox
      Banners: 9 (idem)
      Destination: WhatsApp con shortcode [AH-MAY-FB]
```

**Por qué 60/40 Botox/AH:**
Datos históricos del Excel productivo (`Datos_Livskin_2026-04-25.xlsx`):
- Botox: 25 ventas históricas
- Ácido Hialurónico: 4 ventas históricas
- Botox tiene 6× más historial → mayor probabilidad de conversión → más budget

Ratio 60/40 da a AH suficiente budget para validar (~$40 / 5 días = $8/día → 4-8 messages esperados, suficiente para learning).

---

## 3. Audience

**Geografía (Cusco-only, radio 5-8 km desde Wanchaq):**

```
Ubicación principal: Wanchaq (donde está la clínica)
Radio: 5-8 km
   ├─ Wanchaq ✅
   ├─ Cercado de Cusco ✅
   ├─ San Sebastián ✅
   └─ Santiago ✅

Excluido:
   ❌ San Jerónimo (10-15 km, lejos)
   ❌ Saylla (12-18 km, lejos)
   ❌ Provincias lejanas (Quillabamba, Espinar)
```

**Demografía:**
- Mujeres
- 30-55 años
- Idioma: Spanish

⚠️ **Plan B si Meta marca "Special Ad Category — Health"**: ampliar a 18-65, ambos géneros (Meta optimiza por Pixel events).

**Detailed targeting (intereses):**
- Skincare, Beauty
- Cosmetic procedures
- Anti-aging
- Aesthetic medicine
- Mother's Day (si Meta lo expone para Perú)

**Behavior:** Engaged shoppers (proxy de poder adquisitivo).

**Custom Audiences:**
- 131 clientes activos del ERP → CSV hasheado en `_pending-uploads/livskin-clientes-CA-20260504.csv`
- Subir a Meta Business Manager → Audiences → Customer file
- Meta tarda 24-48h en procesar
- Después: crear Lookalike Audience 2-3% en Cusco → ~10-15K personas similares en el radio

**Audience size esperado** (post-filtros):
- Cusco metro radio 5-8 km: ~280-300K personas
- Mujeres 30-55: ~45-55K
- Tras intereses + behavior: ~10-18K alcanzables
- Con LAL 2-3% adicional: ~25-30K efectivos

---

## 4. Métricas esperadas y targets

| Métrica | Target / Benchmark | Notas |
|---|---|---|
| **CPM** (cost per mille) | $7-15 USD | Audience chica → más caro que mercados grandes |
| **Impresiones totales** | 7-14K con $100 lifetime | Función de CPM |
| **Frequency** | 2-3 promedio (cap 3-4) | Audience chica → frequency sube rápido |
| **CTR** | 1-2% | Benchmark medicina estética LATAM |
| **Cost per message** | $5-15 USD | Si <$10 → muy bueno; si >$15 → revisar segmentación |
| **Mensajes WhatsApp totales esperados** | 6-15 | Realista para $100/5 días en Cusco |
| **Conversion mensaje → consulta agendada** | 30-50% | Depende de qué tan rápido responde la doctora |
| **Conversion consulta → cliente pagante** | 20-40% | Depende de cierre comercial doctora |
| **Clientes pagantes esperados (post-DM)** | 1-4 | Es validación, no growth |
| **Revenue esperado** | S/. 800-3.200 PEN | Si tratamiento promedio S/. 800 |

**ROI mínimo aceptable**: $100 USD ≈ S/. 380. Con 1 cliente que pague S/. 600+ ya es break-even directo. Con 2+ es campaña ganadora.

⚠️ **Pero el ROI directo NO es el único output**: aprendizajes de tracking + audience + creative son input crítico para próxima campaña.

---

## 5. Cronograma operativo día por día

| Día | Fecha | Acciones |
|-----|-------|----------|
| **Día -1 (prep)** | 2026-05-04 (hoy) | • Brief aprobado<br>• Custom Audience subida<br>• Lookalike creada (24-48h procesamiento Meta)<br>• Banners producidos por Dario en Canva<br>• Copies refinados bajo doctrina<br>• Pre-flight smoke E2E |
| **Día 0 (pre-launch)** | 2026-05-04 noche / 2026-05-05 mañana | • Configurar campaña en Ads Manager (siguiendo `ads-manager-checklist.md`)<br>• Verificar Pixel + UTMs<br>• Submit a Meta review |
| **Día 1 (launch)** | 2026-05-05 (lunes) | • Meta aprueba ads (puede tardar 4-24h)<br>• Monitor primeras 6h |
| **Día 2-4** | 2026-05-06 a 2026-05-08 | • Daily check Ads Manager 1× día<br>• Doctora llena tracking sheet WA<br>• Pause/swap creatives si performance baja |
| **Día 5 (cierre)** | 2026-05-09 (viernes) | • Last-day spend<br>• Pre-DM final push si budget remaining |
| **Día 6 (Día de la Madre)** | 2026-05-11 (domingo) | • Doctora atiende citas presenciales<br>• Tracking de quiénes vinieron por la campaña |
| **Día 7-8 (post-mortem)** | 2026-05-12 a 2026-05-13 | • Análisis completo en `post-mortem.md`<br>• Cierre del modo bootstrap (principio #13)<br>• Doctrina v0.X → v1.0 |

---

## 6. Tracking + monitoring (sin Marketing API token)

**Sin Marketing API token disponible** (decisión 2026-05-04 — no repetir el camino fallido del 27/4). Monitoring 100% manual:

### Daily checklist Dario (5 min cada mañana)

1. Abrir Ads Manager → ad account `2885433191763149`
2. Filtrar campaña "Livskin Día de la Madre 2026"
3. Screenshot o copia de las métricas clave:
   - Impresiones, alcance, frequency
   - CTR, CPM, costo por mensaje
   - Mensajes recibidos por ad set
4. Pasar screenshot/CSV a Claude vía chat
5. Claude genera análisis + recomendaciones en `daily-reports/YYYY-MM-DD.md`

### Tracking manual WhatsApp doctora

- Doctora con cheat sheet impreso de shortcodes
- Anota cada mensaje nuevo en Google Sheet con: fecha, hora, número, shortcode visto, tratamiento_interés, status
- Al final de la campaña, cruzar sheet con métricas Meta para CAC real

### Tracking automático (lo que sí funciona sin Marketing API)

- ✅ Pixel + CAPI ya operativos: cada click-to-WhatsApp dispara Pixel "Lead" event si configuramos Custom Conversion para detectar clicks
- ✅ Vtiger sigue capturando leads de form orgánico (NO de esta campaña, esta es solo WhatsApp directo)
- ✅ Audit log ERP: registra cada lead

---

## 7. Risk + mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Meta marca "Special Ad Category — Health" | Media | Audience más amplia (no F35-55) | Plan B: ajustar a 18-65 ambos géneros |
| Compliance ad rejection por copy | Baja-Media | Retraso de aprobación 24-48h | Pre-validar copy contra políticas Meta |
| Audience Cusco demasiado chica | Baja | CPM alto, low impresiones | Ampliar radio a 10 km en plan B |
| Doctora no llena tracking sheet | Media | Pérdida de atribución manual | Cheat sheet impreso + WhatsApp recordatorio cada mañana |
| Banners no se aprueban a tiempo | Media | Lanzamiento tardío | Submit ads el viernes 4 noche para aprobación lunes mañana |
| Budget se gasta antes de día 5 | Baja | Campaña termina antes del DM | Lifetime budget evita esto, Meta distribuye |
| Pixel no firea correctamente | Baja | Pérdida de optimization signal | Smoke E2E pre-launch (ya validado 2026-05-03) |
| Custom Audience tarda >48h en procesar | Media | LAL no disponible al lanzamiento | Subir CA hoy mismo (Meta procesa 24-48h) |

---

## 8. Lo que NO se hace en esta campaña (resistir FOMO)

❌ Landings de Día de la Madre (decisión Opción A — todo Click-to-WhatsApp)
❌ Marketing API token (queda en backlog post-Bridge Episode)
❌ Banners para 3+ tratamientos (solo Botox + AH)
❌ Targeting fuera de Cusco
❌ Promociones / descuentos / "antes del 11"
❌ Múltiples objectives en 1 campaña (solo Engagement→Messages)

Si emerge alguna tentación de estas durante la producción → al `_doctrine-feedback.md` para procesar post-mortem, no se cambia campaña corriendo.

---

## 9. Definition of Done

**La campaña se considera cerrada cuando:**

- [ ] Campaña corrió 5 días + Ads Manager muestra impresiones + clicks reales
- [ ] Mínimo 5 mensajes WhatsApp recibidos por la doctora con shortcodes anotados
- [ ] Tracking sheet manual llenado por doctora con al menos 5 entradas
- [ ] Daily reports de Claude por cada día de campaña
- [ ] Post-mortem ejecutado con data real
- [ ] Decisión consciente del cierre del modo bootstrap (doctrina v0.1 → v1.0)
- [ ] Aprendizajes durables migrados a memorias permanentes
- [ ] Carpeta `2026-05-dia-madre/` movida a `_archive/` post-cierre

---

## 10. Cross-link

- `brief.md` — gate de aprobación + las 4 preguntas
- `tracking.md` — cheat sheet shortcodes consolidado
- `campaign-config-draft.md` — config técnica exhaustiva
- `ads-manager-checklist.md` — paso a paso UI manual
- `botox/copies.md` — copies bajo doctrina
- `acido-hialuronico/copies.md` — idem
- `_doctrine-feedback.md` — bootstrap insights
- `post-mortem.md` — llenar al cerrar

---

**Plan vivo.** Refinable antes del lanzamiento. Una vez la campaña corre, NO se modifican estructura/budget/audience sin OK explícito de Dario.
