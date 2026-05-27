---
campaign: 2026-05-click-to-wa-wanchaq
type: post-mortem
status: closed
held_on: 2026-05-27
duration_min: 60
campaign_id_meta: 120243361185770678
campaign_name_meta: "Livskin — May 2026 v3 — Click-to-WA Cusco metro (TRAFFIC + LIFETIME)"
ad_account_currency: PEN
---

# Post-Mortem — 2da campaña paga Livskin (Click-to-WA Wanchaq+6km)

> Sesión de cierre + análisis. 2da campaña paga del proyecto (la 1ra fue `2026-05-dia-madre`).
> Pausada manualmente el 2026-05-27 ~05:20 Lima por bajo performance, con 38.5% del cap consumido.

---

## 1. Resumen ejecutivo

| Métrica | Plan | Real | Var |
|---|---|---|---|
| Budget | S/ 350.00 | S/ 134.58 | -61.5% (pausada antes del cap) |
| Duración | 25/05 → 30/05 (6 días) | 25/05 04:00 → 27/05 ~05:20 (~49h) | -67% |
| Impresiones | — (no estimadas) | 111,264 | — |
| Alcance único | — | 36,972 personas | — |
| Frequency | 1.5-2.0 target | 2.62 (saturado) | +30-75% |
| Clicks | — | 1,424 (unique 1,154) | — |
| CTR | 1.0% target | 1.27% | +27% ✓ |
| CPC | S/0.15 target | S/0.09 | -40% ✓ (barato) |
| CPM | S/2.00 target | S/1.21 | -40% ✓ |
| **Messaging started (Meta)** | 15-25 target | **8** | -47% a -68% |
| **Leads en DB** | — | **8 conversaciones** | — |
| **Leads cualificables (escapan q1)** | — | **3** (Maritza q2_unparseable, Emilia escalada, Jean test) | — |
| **Leads útiles (contacto real con doctora)** | 5-10 target | **1** (Emilia → soft commit) | -80% a -90% |
| **CPL útil** | < S/50 target | **S/134.58** | **+169%** ⚠️ |
| Conversiones a cliente real | — | **0 todavía** (Emilia "probable próxima semana") | — |
| Revenue confirmado | — | S/ 0 | — |
| Revenue proyectado (si Emilia convierte) | — | ~S/ 409 (ticket promedio histórico) | — |
| **ROAS proyectado optimista** | 2.0x target | ~3.0x (409/134.58) si Emilia convierte | — |
| **ROAS actual** | — | **0x** (sin revenue todavía) | — |

**Verdict**: campaña **subperforming** pero con costos unitarios sanos (CPC/CPM/CTR mejor que target). El problema NO fue Meta delivery — fue **conversión click→message** (0.56% vs 1-2% típico industria) y **funnel post-q1** del bot.

---

## 2. Hipótesis vs realidad

### Hipótesis principal (del setup)
> "Mujeres 18-65 en Wanchaq+6km harán click en banners de Botox/AH/PRP/Limpieza y escribirán al WA del bot para info → bot cualifica → escala a doctora vía handoff humano → cita".

**Resultado:** 🔴 **rechazada parcialmente**

**Evidencia:**
- ✅ Click rate sano (1.27% CTR — la gente sí click)
- ❌ Solo 0.56% de quienes click escribieron al WA (debería ser 1-2%)
- ❌ De quienes escribieron (8), solo 12.5% llegó a contacto humano real con la doctora (Emilia)
- ❌ Botox (top categoría histórica) tuvo 0 conversaciones — hipótesis "Botox es la mejor punta de lanza" rechazada

### Hipótesis secundarias

| Hipótesis | Resultado | Evidencia |
|---|---|---|
| "Botox convierte mejor (50% revenue histórico)" | 🔴 rechazada | 0 conv en S/22.30 — peor ad set |
| "Distribución 35/35/15/15 (Botox/AH/PRP/Limpieza) es óptima" | 🔴 rechazada | PRP+Limpieza (30% allocation original) generaron 7 de 8 conv |
| "Wanchaq+6km tiene pool suficiente" | 🟡 inconclusiva | Reach 36,972 con frequency 2.62 sugiere saturación cercana al pool real |
| "Bot rule-based maneja el funnel sin fricción" | 🔴 rechazada | 62.5% drop-off post-q1 (5 de 8 leads se evaporan tras 1 inbound) |
| "18-65 femenino captura el mercado" | 🔴 rechazada parcial | 25-34 consumió S/43.42 con 0 conv; 45-64 generó 6 de 8 conv |
| "Click-to-WA es mejor que landing page" | 🟡 inconclusiva | Solo 5 landing_page_view registrados → mayoría fue directo a WA, no se puede comparar |

---

## 3. Performance por ad set

| Ad Set | Spend (S/) | Clicks | CTR | Conv | CPL (S/) | Veredicto |
|---|---|---|---|---|---|---|
| **PRP** | 49.42 | 521 | 1.30% | 4 | 12.36 | 🏆 Ganador inesperado |
| **Limpieza Facial** | 39.62 | 397 | 1.18% | 3 | 13.21 | 🥈 Sólido |
| **Ácido Hialurónico** | 23.19 | 274 | 1.47% | 1 | 23.19 | 🥉 Aceptable |
| **Botox** | 22.30 | 232 | 1.23% | 0 | ∞ | ☠️ Fail completo |

**Insight crítico**: el creative + copy de Botox NO conecta. Históricamente es el 50% del revenue; en este canal frío con bot, NO arranca. Hipótesis: precio percibido alto + barrera mental ("es para más viejas / es invasivo").

---

## 4. Performance por edad (todas femenino ✓)

| Edad | Spend (S/) | Clicks | CTR | Conv | CPL (S/) |
|---|---|---|---|---|---|
| **55-64** | 13.54 | 148 | 1.50% | 3 | **4.51** ⭐ |
| **45-54** | 28.36 | 310 | 1.35% | 3 | 9.45 |
| **35-44** | 39.16 | 382 | 1.14% | 2 | 19.58 |
| **25-34** | 43.42 | 480 | 1.30% | **0** | ∞ ☠️ |
| **18-24** | 10.05 | 104 | 1.31% | 0 | ∞ |

**Insight**: sweet spot es **45-64**. 25-34 fue **dinero perdido** (38% del spend, 0 conversaciones). Hipótesis: gen Y/Z hace scroll y click pero NO inicia conversación con clínica (espera info en feed).

---

## 5. Performance por placement

| Placement | Spend (S/) | CTR | Conv | CPL (S/) | Veredicto |
|---|---|---|---|---|---|
| **Facebook Feed** | 47.57 | 1.74% | 5 | **9.51** | 🏆 Campeón |
| **Facebook Stories** | 6.55 | 2.59% | 1 | 6.55 | 🥈 Eficiente, baja escala |
| **FB Instream Video** | 51.10 | 0.91% | 2 | 25.55 | ⚠️ Caro |
| **FB Reels** | 29.17 | 1.72% | 0 | ∞ | ☠️ Cero conversión |
| Instagram (todos) | 0.13 | 0% | 0 | — | No probado |

**Insight**: **Reels gastó S/29 sin generar 1 conversación**. CTR alto (1.72%) pero quien click NO escribe — comportamiento "swipe & forget". Feed es el único placement con consistencia ROI.

---

## 6. Funnel detallado

```
1,424 clicks
    ↓ (0.56% conversión click→message)
8 messaging conversations started
    ↓ (87.5% drop-off post-q1)
1 conversación que llegó a contacto humano real
    ↓ (en evaluación, "probable próxima semana")
0 ventas confirmadas (todavía)
```

**Drop-off severo en 2 puntos:**
1. **Click → Message**: 99.44% del tráfico click pero no escribe — quizás creative no comunica "es para escribir AHORA", o Meta envía bots/curiosos
2. **Q1 → Q2**: 5 de 8 leads (62.5%) se evaporaron tras la respuesta inicial del bot — el bot pregunta `q2` (¿primera vez?) y NO responden

---

## 7. Aprendizajes durables

### Lo que funcionó
- **Costos unitarios sanos** — CPC S/0.09 y CTR 1.27% mejor que target. Meta delivery está fino, no es Meta el problema.
- **Audiencia 45-64 femenino** — perfecto match con cliente real Livskin (boca a boca también es 40-60). CPL S/4-9.
- **FB Feed** como placement primario — 5 de 8 conversaciones, mejor CPL.
- **PRP+Limpieza** como angles inesperados — generan más conversaciones que Botox (contra-intuitivo pero data clara).
- **Fast pause capability** — pausamos en <30 segundos vía Meta API, ahorrando S/215 (61.5% del cap).
- **Pipeline determinístico end-to-end funcionó** — webhook WA → bot → wa_conversation_state → escalación → notificación Dario. Sin caídas.

### Lo que NO funcionó
- **Botox como punta de lanza** (cero conversaciones, S/22 wasted) — históricamente es el 50% del revenue, pero en canal frío con tráfico cold no convierte.
- **Audiencia 25-34** — S/43.42 (38% del spend) con 0 conv. Money sink.
- **Reels + InStream Video** — alto CTR/clicks pero 0 mensajes (Reels) y 2 mensajes caros (InStream).
- **Bot q2 (¿primera vez?)** — drop-off 62.5%. La pregunta percibida como interrogatorio innecesario. El lead esperaba precio/respuesta directa.
- **Templates Meta "RETURNANTE"** — `doctor_lead_returning_v1` quedó PENDING toda la campaña (Meta no aprobó en 48h). Jean (test) fue manejado solo con response in-thread.
- **Logging de wa_messages** — tabla `wa_messages` está vacía (0 rows) aunque hubo 8 conversaciones con 11+ mensajes. **Bug crítico**: no estamos persistiendo bodies de mensajes para análisis post-campaña.

### Sorpresas
- **PRP fue el ganador**, no Botox (4 conv vs 0). Inesperado dado histórico.
- **55-64 fue mejor que 45-54** en CPL (S/4.51 vs S/9.45). Pensábamos 40-50 era el target.
- **Stories fue muy eficiente** pese a su baja escala (CPL S/6.55, mejor que Feed). Vale explorar más en próxima campaña.
- **Conversión click→message de 0.56%** — esperábamos 1-2% (benchmark industria salud Perú). Hay friction oculta o tráfico de baja calidad.
- **Frequency 2.62 en 2 días** sugiere pool real de Wanchaq+6km femenino interesado es **~30-40k personas** (no las 100k+ que Meta dice como "potential reach").

---

## 8. Bugs/gaps técnicos detectados

| Item | Severidad | Backlog destination | Notas |
|---|---|---|---|
| **wa_messages table vacía** | 🔴 P0 | `docs/backlog.md` | 8 conv en wa_conversation_state pero 0 mensajes en wa_messages. Probable bug en workflow D1v2 (no persiste msg body). Sin esto NO podemos analizar copy quality. |
| **q2 parser falla con "No"** | 🟡 P1 | `docs/backlog.md` | Maritza dijo "No" → bot marcó `q2_unparseable` y escaló. "No" es respuesta válida negative para "¿primera vez?". Fix regex parser q2. |
| **Template `doctor_lead_returning_v1` PENDING 48h** | 🟡 P2 | (monitoreo) | Meta MARKETING templates demoran. Para próxima campaña: pre-aprobar templates ≥7 días antes. |
| **Bot funnel q2 con 62.5% drop-off** | 🔴 P0 | `docs/brand/` post Interludio | Considerar skip q2 → ir directo a derivar a doctora tras q1. Validar en Interludio Discovery con doctora. |
| **No tenemos conv rate creative-level** | 🟡 P2 | analytics | API no devuelve breakdown por banner individual fácilmente. Considerar tagging UTM creative-level. |

---

## 9. Decisiones para próxima campaña (3ra)

| Cambio | Razón | Esperado |
|---|---|---|
| **Eliminar Ad Set Botox** | 0 conv, S/22 wasted | Reasignar S/22 a PRP+Limpieza |
| **Restricción edad 35-64** (no 18-34) | 25-34 gastó 38% con 0 conv | Ahorrar S/40+ del budget |
| **Solo placements Feed + Stories** (no Reels, no InStream) | Reels=0 conv S/29; InStream caro S/25.55/conv | Concentrar en placement que convierte |
| **Distribución budget**: PRP 40%, Limpieza 35%, AH 25% | PRP campeón, Limpieza sólida, AH aceptable | Esperar 12-15 leads con mismo S/350 |
| **Rework copy bot — eliminar q2** | Drop-off 62.5% post-q1 | Lead manda 1 inbound → bot responde "Por supuesto, le paso tu interés a la doctora" → handoff directo |
| **Pre-aprobar templates Meta ≥7 días antes** | `doctor_lead_returning_v1` quedó PENDING | Todos los templates APPROVED al lanzar |
| **Fix wa_messages logging ANTES de lanzar 3ra** | Sin esto no hay análisis post-campaña | P0 backlog |
| **Geo: probar ampliar a 10km** O **probar otra zona Cusco** | Frequency 2.62 saturó pool Wanchaq+6km en 2 días | Reach fresco |
| **Pre-pausar Reels + InStream desde el setup** | No esperar a ver wasted spend | S/30+ ahorrados |
| **Budget cap menor para próxima**: S/200 en lugar de S/350 | 2da campaña gastó S/134 antes de pausar; S/200 da margen sin sobre-exponer | Test más controlado |

---

## 10. Métricas para benchmark futuro

```
Campaña: 2026-05-click-to-wa-wanchaq
Currency: PEN
Pausada: 27/05 ~05:20 Lima (49h de corrida real)

Top-line:
  Spend:          S/ 134.58 (de S/350 cap)
  Impresiones:    111,264
  Reach único:    36,972
  Frequency:      2.62
  Clicks:         1,424 (unique 1,154)
  CPM:            S/ 1.21
  CTR:            1.27%
  CPC:            S/ 0.09

Funnel:
  Click→Message:  0.56% (8 de 1,424)
  Q1→Q2 retain:   37.5% (3 de 8)
  Lead→Cita:      12.5% (1 de 8 — Emilia soft commit)
  Lead→Cliente:   0% (todavía)

Por ad set ganador (PRP):
  CPL útil:       S/ 12.36
  CTR:            1.30%

Por audiencia ganadora (45-64 femenino):
  CPL útil:       S/ 6.98 (combined 45-64)
  6 de 8 conv

Por placement ganador (FB Feed):
  CPL útil:       S/ 9.51
  5 de 8 conv

Benchmarks para próxima:
  Target CTR:        ≥1.5%
  Target click→msg:  ≥1.0%
  Target q1→q2:      ≥70%
  Target CPL útil:   ≤S/50
```

---

## 11. Status del modo bootstrap

- ☐ Bootstrap **se cierra** con esta campaña
- ☑ Bootstrap **continúa** → próxima campaña sigue capturando feedback

**Razón**: principio #13 dice "trigger formal cierre = post-mortem 2da campaña paga". Pero esta 2da campaña:
1. NO produjo cita confirmada todavía (Emilia es soft commit "próxima semana")
2. NO validó la hipótesis principal (subperformed -47% a -68% en mensajes)
3. Identificó 5+ bugs/gaps críticos del backbone que NO conocíamos (q2 parser, wa_messages logging, drop-off q2)

**Decisión**: bootstrap se mantiene ABIERTO hasta:
- Cierre del lead Emilia (sea venta confirmada o no-show)
- Fix de los 2 bugs P0 (wa_messages + bot q2)
- Corrida de la **3ra campaña paga** con los cambios de §9 → ahí cierra bootstrap.

---

## 12. Archivado

- [x] Esta carpeta `docs/campaigns/2026-05-click-to-wa-wanchaq/` queda en activo (no a `_archive/`) hasta que Emilia se resuelva (próxima semana)
- [ ] Aprendizajes durables a migrar a memorias permanentes:
  - `project_paid_campaign_2_learnings_2026_05_27.md` — qué funcionó/no funcionó (creative angles, audiencia, placement)
  - `feedback_q2_drop_off_pattern.md` — drop-off masivo en pregunta secundaria del bot
  - `project_currency_meta_account_PEN.md` — todas las métricas de spend están en soles, no USD
- [x] Backlog actualizado con items P0/P1 (al cerrar esta sesión)
- [ ] Próxima campaña planificada cuando se cierren los 2 bugs P0

---

## 13. Decisiones inmediatas (next 7 días)

1. **Esperar resolución Emilia** (probable visita próxima semana — si convierte, ROAS 3.04x; si no, ROAS 0x)
2. **Fix bug wa_messages logging** (P0, sin esto no podemos analizar copy)
3. **Fix bug q2 parser "No"** (P1, cierra Maritza)
4. **Revisar funnel bot post-q1 con doctora en Interludio Discovery** (decidir si skip q2 o mantenerlo)
5. **Capturar 7 conversaciones cold (qualifying)** que F2 cerrará en 28-30/05 — sus `last_inbound_text` son data útil pre-cleanup

---

**Status del post-mortem:** `closed` ✓ — análisis completado el 2026-05-27 con data parcial (49h de corrida, 38.5% del cap consumido).
