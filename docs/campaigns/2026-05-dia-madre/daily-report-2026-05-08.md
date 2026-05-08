---
campaign: 2026-05-dia-madre
report_date: 2026-05-08
report_type: daily-report-final (cierre anticipado)
day_of_campaign: 4 de 5 — CERRADA el día 4
schedule_original: 2026-05-05 06:00 → 2026-05-09 23:59 (Lima)
status_final: ✅ Cerrada anticipadamente 2026-05-08 por decisión de Dario
framing: "campaña de calibración" — scope mínimo (validar flujo) cumplido; comercialmente fracaso
---

# Daily Report — Día de la Madre 2026 · 2026-05-08 (CIERRE ANTICIPADO)

## 🎯 Resumen ejecutivo

**Decisión de cierre 2026-05-08 (Dario):** la campaña ya entregó todo lo que podía entregar. Seguir 24h más solo gasta el ~50% restante del budget sin aportar data nueva ni validar más del sistema. Mejor preservar el budget y avanzar a otras prioridades del proyecto.

**Resultado de la calibración:**

| Dimensión | Resultado |
|---|---|
| Scope mínimo (validar flujo end-to-end) | ✅ Cumplido — pipeline form/WA → Vtiger → ERP funcional |
| Definition of Done leads (≥5) | ✅ Cumplido — 6 leads recibidos |
| Conversión leads → cliente pagante | ❌ 0 conversiones |
| ROI directo | ❌ Negativo (S/188 spend, 0 revenue) |
| Aprendizaje doctrinal | ✅ Fuerte — patrón Click-to-WhatsApp domina sobre Landing |

**Lectura honesta de Dario:**

> *"El fracaso a mi parecer es que no estamos haciendo contenido valioso que impulse la venta. Al menos hemos recolectado eventos en nuestro pixel para poder enviar una nueva campaña de remarketing probando otro ángulo."*

El problema raíz NO fue estructura ni infraestructura — fue **calidad del contenido / creativos / narrativa**. El sistema técnico funcionó; los creativos no impulsaron venta.

> **Asimetría de canales:** WhatsApp directo capturó 6/6 leads. Landing capturó 0/6 con 1,294 clicks gastados.

---

## 1. Leads recibidos (tracking sheet actualizado 2026-05-08)

| # | Fecha | Hora | Nombre | Teléfono | Shortcode | Origen ad | Tiempo respuesta doctora |
|---|---|---|---|---|---|---|---|
| 1 | 2026-05-04 | 09:41 | (sin nombre) | +51 968 322 731 | ARM-MAY-FB-BOFU-COLDWA | BOFU-WhatsApp-COLDWA | 7 min ✅ |
| 2 | 2026-05-04 | 19:14 | Alicia | +51 900 929 060 | ARM-MAY-FB-MOFU-COLDWA | MOFU-WhatsApp-COLDWA | 1h 8min ⚠️ |
| 3 | 2026-05-04 | 20:51 | (sin nombre) | +51 967 499 371 | ARM-MAY-FB-MOFU-WARM | MOFU-WhatsApp-WARM | 26 min ✅ |
| 4 | 2026-05-07 | 22:28 | Roxana Costilla | +51 957 366 444 | ARM-MAY-FB-MOFU-COLDWA | MOFU-WhatsApp-COLDWA | 1 min ✅ |
| 5 | 2026-05-07 | 18:29 | Alicia García | +51 967 478 335 | ARM-MAY-FB-MOFU-WARM | MOFU-WhatsApp-WARM | 20 min ✅ |
| 6 | 2026-05-07 | 21:33 | (sin nombre) | +51 972 588 486 | (borrado) | indeterminado | día siguiente 8:43 AM ⚠️ |

**Distribución por origen ad:**
- MOFU-WhatsApp-COLDWA: 3 leads (más eficiente en captura)
- MOFU-WhatsApp-WARM: 2 leads
- BOFU-WhatsApp-COLDWA: 1 lead
- Landing (TOFU + MOFU): **0 leads identificables**

---

## 2. Performance Meta Ads (4 días, screenshot 2026-05-08 11:30 AM)

### Por anuncio

| Anuncio | Clicks | Spend (S/) | Imp | Reach | CTR | Freq | Leads | Cost-per-Lead |
|---|---|---|---|---|---|---|---|---|
| **MOFU-Landing** 🥇 | **1,143** | **S/92.48** (49%) | 52,606 | 18,991 | 2.17% | 2.77 | **0** | ∞ ⚠️ |
| MOFU-WhatsApp-COLDWA | 512 | S/49.46 | 34,168 | 18,800 | 1.50% | 1.82 | 3 | S/16.5 |
| TOFU-Landing | 151 | S/12.86 | 7,835 | 3,452 | 1.93% | 2.27 | 0 | ∞ ⚠️ |
| MOFU-WhatsApp-WARM | 107 | S/26.92 | 7,830 | 511 | 1.37% | **15.32** ⚠️ | 2 | S/13.5 |
| BOFU-WhatsApp-COLDWA | 59 | S/5.35 | 3,749 | 2,482 | 1.57% | 1.51 | 1 | S/5.4 ⭐ |
| BOFU-WhatsApp-WARM | 7 | S/1.35 | 374 | 55 | 1.87% | 6.80 | 0 | n/a |
| **TOTAL** | **1,979** | **S/188.42** | **106,562** | **35,106** | 1.86% | 3.04 | **6** | **S/31.4** |

### Cost-per-Lead recalculado (sin contar el dinero "perdido" en landing):

- Solo WhatsApp ads: S/(5.35 + 49.46 + 26.92 + 1.35) = **S/83.08 → 6 leads = S/13.85 por lead** (~$3.7 USD)
- Vs benchmark del brief: $5-15 USD ✅ EXCELENTE

### Frecuencia anómala — MOFU-WhatsApp-WARM = 15.32

Significa que en promedio cada persona del audience vio el ad **15 veces**. Audience es chica (511 reach) y el ad sigue corriendo → ad fatigue inminente. Ya rinde 2 leads, pero seguir invirtiendo aquí es desperdicio.

---

## 3. Hallazgos doctrinales

### 🔥 CRÍTICO #1 — CBO bajo objective Tráfico optimiza por clicks, NO por leads

Meta CBO redistribuyó budget priorizando **MOFU-Landing (1,143 clicks, CPC S/0.08)** porque es el que más "Resultados" produce — pero el "Resultado" definido es **Link clicks**, no leads. Ese ad recibió **49% del budget total** y generó **0 conversiones reales**.

**Implicación práctica:**
- Cuando el objetivo real son leads y NO se puede usar Pixel Lead optimization (Health restrictions / no Marketing API), CBO con objective Tráfico **NO sirve para optimizar leads**.
- Mejor: presupuesto fijo por ad set + **manual budget allocation** basado en performance manual.

### 🔥 CRÍTICO #2 — En Cusco F30-55, WhatsApp directo > Landing para captura de lead inicial

**6 leads via WhatsApp directo** (685 clicks combinados) vs **0 leads via Landing** (1,294 clicks combinados).

Conversion rate:
- WhatsApp ads → mensaje: 6/685 = **0.88%**
- Landing → mensaje con shortcode `-WEB`: 0/1,294 = **0.00%**

**Posibles razones (en orden de probabilidad):**
1. **Fricción extra**: 1 paso más (visitar landing → entender → click WA) vs 1 paso (click ad WA → ya estás en WA con texto pre-poblado).
2. **Contexto desktop vs mobile**: Meta puede mostrar Landing ads en Reels (que son mobile-first), pero el landing requiere lectura. Mensaje WA directo funciona en cualquier contexto.
3. **Falta de form en landing**: el visitante que *quería* dejar contacto pero NO usar WhatsApp no tenía forma de hacerlo.
4. **Audience chica saturada**: 35K reach total → el Cusco F30-55 ya vio el ad y los curiosos genuinos ya hicieron click WA directo.

### 🟡 NOTABLE — El BOFU directo es el más eficiente (S/5.4 por lead)

BOFU-WhatsApp-COLDWA: 59 clicks → 1 lead → S/5.35 spent → cost-per-lead ~S/5.4 (~$1.4 USD). Es el ratio más eficiente de todos los ads.

**Aprendizaje:** mensajes directos al BOTTOM-funnel (audience cálida que YA conocía Livskin) convierten 5-10x mejor que TOP/MIDDLE-funnel cold outreach. Pero su volumen es limitado por el tamaño del audience cálido.

---

## 4. Smoke test landing — análisis técnico completo

### Cómo funciona el form de la landing (verificado en código fuente)

La landing **SÍ tiene formulario** (componente `Booking` en `sections-2.jsx` línea 219). Pero NO funciona como un form tradicional que POSTea a un webhook:

1. **UI de captura**: 3 inputs (Nombre, Teléfono, Email) + checkbox consent + botón "Agendar evaluación"
2. **Validación client-side**: name ≥2 chars + phone formato `9XXXXXXXX` + consent checked
3. **Construcción de texto WA** con datos del usuario:
   ```
   "Hola Livskin, soy [nombre], mi número es +51 999 999 999, email: x@x.com.
   Me gustaría agendar una valoración de Armonización Facial."
   ```
4. **Inyección de shortcode** vía `getWALink()` (definido en `index.html` línea 186-190) → agrega `[ARM-MAY-FB-MOFU-WEB]` al final del texto si la URL traía `?src=mofu`
5. **Click "Agendar"** → abre WhatsApp con ese texto completo + shortcode

**El form NO crea Lead en Vtiger ni form_submission en WP.** Manda el visitante directo a WhatsApp con los datos pre-poblados + shortcode `-WEB` reconocible.

### Verificación técnica deployada (2026-05-08 19:55 UTC)

- ✅ HTTP 200 sobre la landing
- ✅ `livskin-tracking.js` carga 200
- ✅ Código de inyección de shortcode presente en HTML servido
- ✅ JSX components con form serían renderizados client-side por React

**Conclusión técnica:** la landing está bien deployada. Si alguien completaba el form y daba "Agendar evaluación", su mensaje llegaba a la doctora con:
- Patrón distintivo: `"Hola Livskin, soy [nombre], mi número es..."`
- Shortcode con sufijo `-WEB` (ej: `ARM-MAY-FB-MOFU-WEB`)
- Datos personales explícitos en el cuerpo

### ✅ Confirmación de la doctora (Dario, 2026-05-08)

> *"No le ha llegado nada más a lo que he enviado, no se llenaron forms"*

**0 mensajes con patrón landing-form recibidos durante los 4 días.**

→ **Resultado verificado:** 1,294 clicks landing → 0 forms completados → 0 leads atribuibles a landing.

**Conversion rate landing→form: 0/1,294 = 0.00%** (confirmado por doctora + ausencia de patrón en CSV).

---

## 5. Status Definition of Done

| Criterio | Status |
|---|---|
| Campaña corrió 5 días + Ads Manager muestra impresiones reales | ✅ 4/5 días, 106K imp |
| Mínimo 5 leads recibidos (form + WA combined) | ✅ **6 leads** |
| Doctora llenó tracking sheet con al menos 5 entradas | ✅ 6 entries |
| Daily reports de Claude | ⚠️ Este es el primero (atrasado) |
| Post-mortem ejecutado con data real | ⏳ Programado 2026-05-12/13 |
| Modo bootstrap cerrado (doctrina v0.X → v1.0) | ⏳ Pendiente post-mortem |
| Aprendizajes durables migrados a memorias permanentes | 🟡 1 memoria nueva agregada hoy |
| Carpeta `2026-05-dia-madre/` movida a `_archive/` | ⏳ |

---

## 6. Recomendaciones tácticas para el último día (2026-05-09)

### 🟢 NO tocar

- Mantener campaña corriendo como está. Mid-flight changes son destructivos.
- No pausar MOFU-Landing aunque "no convierte" — pausar mid-flight resetea learning phase y daña delivery.

### 🟡 Considerar acciones suaves

- Pegar manualmente el screenshot de tracking-sheet actualizado a la doctora para que tenga visibilidad de los 6 leads ya capturados.
- Recordatorio diario a la doctora durante el último día: cualquier mensaje con shortcode (especialmente con `-WEB`) → registrar inmediatamente en CSV.

### 🔴 Items para el post-mortem (2026-05-12/13)

1. **Decisión doctrinal sobre landing**: ¿la próxima campaña corre con landing? Si sí, agregar form (no solo botones WA). Si no, 100% Click-to-WhatsApp.
2. **Decisión sobre objective**: si seguimos sin Marketing API + Health restrictions, optar por objective **Mensajes** (no Tráfico) para que CBO optimice por mensajes WA, no por clicks.
3. **Audience expansion**: F30-55 Cusco 8km es probable que ya esté saturándose (frequency 3.04, MOFU-WARM en 15.32). Próxima campaña → ampliar geo (radio 12km) o aumentar edad (28-58).
4. **Custom Audience seed**: usar los 6 leads + el resto de clientes históricos (134) para crear LAL 1-3% en próxima campaña. Esa es la primera audience custom REAL que tenemos.

---

## 7. Cosas a registrar como aprendizaje durable (post-mortem)

> Estas líneas se trasladan al `post-mortem.md` y memorias permanentes al cierre del bootstrap (#13).

1. **Doctrina#11 confirmada**: "deterministic backbone first, IA aditiva". Aquí: Manual UI funcionó sin Marketing API. La data programática (Vtiger + ERP audit + Ads UI screenshots) fue suficiente.
2. **Objective Tráfico ≠ Optimización de leads** (memoria nueva ya guardada).
3. **Cusco mobile-first**: WhatsApp directo le gana a Landing en este perfil de audience.
4. **Tracking manual de la doctora va con delay** — no es real-time. Próxima vez: integrar daily reminder o un sistema mejor (form WA, bot de captura, etc).
5. **CBO con audience chica**: cuidado con frequency >5. Mejor presupuesto fijo por ad set.

---

## 8. Cierre operacional 2026-05-08

- ✅ **Campaña pausada** en Ads Manager por Dario (toggle off de los 6 ads)
- ✅ **Daily report final** generado (este documento)
- ✅ **Tracking sheet** actualizado con los 6 leads
- ✅ **Memoria warning** anotada en backlog: material de competitor research disponible para próximas campañas (sandbox `Playwrightdemo` externo)
- ✅ **Confirmación de la doctora**: 0 mensajes con patrón landing-form (`-WEB` shortcode)

## 9. Para el post-mortem (2026-05-12/13)

Items abiertos para discutir/decidir en post-mortem:

1. **Decisión doctrinal sobre landing**: ¿próxima campaña corre con landing? Si sí, ¿como funnel de captura o solo autoridad/credibilidad?
2. **Decisión sobre objective**: cambiar de "Tráfico" a "Mensajes" (sin Marketing API).
3. **Audience expansion**: F30-55 Cusco 8km saturó (frequency 3.04, MOFU-WARM en 15.32). Considerar radio 12-25 km y ajustar edad.
4. **Custom Audience seed**: usar los 6 leads + 134 clientes históricos para LAL 1-3% en próxima campaña.
5. **Calidad del contenido**: principal raíz del fracaso comercial. ¿Qué cambia para que los creativos impulsen venta? (ver material de Playwrightdemo en backlog).
6. **Cierre del modo BOOTSTRAP** (#13): doctrina v0.X → v1.0 + memorias 🔥 críticas de marca.

---

**Status final:** Campaña de calibración cerrada anticipadamente 2026-05-08. Sistema técnico validado. Aprendizajes doctrinales claros. Listos para avanzar a ingeniería del proyecto.
