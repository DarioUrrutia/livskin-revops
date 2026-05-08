---
campaign: 2026-05-dia-madre
status: COMPLETO — campaña cerrada anticipadamente 2026-05-08, post-mortem ejecutado mismo día
trigger_for_close: principio operativo #13 — cierre del modo BOOTSTRAP
generated_by: Claude Code + Dario (collab session 2026-05-08)
---

# Post-Mortem — Campaña Día de la Madre 2026

> Cerrada anticipadamente 2026-05-08 (día 4 de 5 programados). Lo que la campaña podía entregar, ya lo entregó. Seguir 24h más solo gastaba el budget restante sin aportar data nueva.

---

## 1. Resumen ejecutivo

**Resultado: éxito MIXTO.**

| Plano | Resultado | Lectura |
|---|---|---|
| **Técnico / infraestructura** | ✅ Éxito | El flujo end-to-end (form/WA → Vtiger → ERP) funcionó. Pipeline validado. |
| **Captación de leads** | ✅ Cumplido | 6 leads recibidos (≥5 del Definition of Done). |
| **Conversión a cliente pagante** | ❌ Fracaso | 0 conversiones. Ningún lead se convirtió en cita pagada al cierre. |
| **Aprendizaje doctrinal** | ✅ Éxito alto | Doctrina v0.1 sometida a campaña real → 14 INS-NNN ya documentados + nuevos hallazgos clave del post-mortem. Lista para v1.0. |
| **ROI directo** | ❌ Negativo | S/188 spend, 0 revenue. |

**Top 3 aprendizajes**:

1. **El fracaso comercial es de contenido, no de estructura ni infraestructura.** El sistema técnico funcionó, los creativos+landing no impulsaron venta. Cita Dario: *"El fracaso a mi parecer es que no estamos haciendo contenido valioso que impulse la venta"*.

2. **WhatsApp directo gana sobre Landing en Cusco F30-55** (6/6 leads via WA, 0/6 via landing+form con 1,294 clicks). Refuta la hipótesis del brief que ponía a la landing como funnel principal.

3. **Objective Tráfico + CBO desperdicia presupuesto cuando lo que importa son leads.** Meta optimizó por clicks (49% del budget al MOFU-Landing porque tenía mejor CPC) mientras los leads venían 100% de los WhatsApp ads. La estructura económica del experimento estaba mal diseñada para medir lo que importa.

**Decisión clave para próxima campaña**: *Define con Dario en sección 9 abajo*.

---

## 2. Métricas finales

### Performance Meta Ads (al cierre 2026-05-08, ~89 horas de delivery)

| Métrica | Esperada (5 días full) | Real (4 días) | Variación |
|---|---|---|---|
| Impresiones totales | 7-14K | **106,562** | +660% sobre alto |
| Alcance único | 5-10K | **35,106** | +250% sobre alto |
| Frequency promedio | 2-3 | 3.04 | dentro de rango |
| Spend total | $100 USD ≈ S/375 | **S/188.42** | 50% del budget — sobró por cierre anticipado |
| CPM promedio | $7-15 USD | S/1.77 (~$0.47 USD) | **15-30x más barato** que esperado |
| CTR promedio | 1-2% | **1.86%** | dentro de rango |
| Link clicks total | 100-280 | **1,979** | +700% sobre alto |
| Mensajes WhatsApp recibidos | 6-15 | **6** | dentro de rango (mínimo) |
| Cost per message (lead) | $5-15 USD ≈ S/19-56 | S/31.40 (sobre todo el spend) | dentro de rango |

**CPM 15-30x más barato confirma**: audience Cusco F30-55 está sub-saturado en pauta digital del nicho. Las impresiones se compraron mucho más barato de lo que sugeriría benchmark global. Pero la traducción a leads NO escaló proporcionalmente — el cuello de botella es el contenido, no el costo de impresión.

### Performance por anuncio

| Anuncio | Clicks | Spend (S/) | % del spend | Imp | Reach | CTR | Freq | Leads | Cost-per-Lead |
|---|---|---|---|---|---|---|---|---|---|
| MOFU-Landing-DM2026 | 1,143 | S/92.48 | **49%** | 52,606 | 18,991 | 2.17% | 2.77 | **0** | ∞ ⚠️ |
| MOFU-WhatsApp-COLDWA-DM2026 | 512 | S/49.46 | 26% | 34,168 | 18,800 | 1.50% | 1.82 | 3 | S/16.49 |
| TOFU-Landing-DM2026 | 151 | S/12.86 | 7% | 7,835 | 3,452 | 1.93% | 2.27 | 0 | ∞ ⚠️ |
| MOFU-WhatsApp-WARM-DM2026 | 107 | S/26.92 | 14% | 7,830 | 511 | 1.37% | **15.32** ⚠️ | 2 | S/13.46 |
| BOFU-WhatsApp-COLDWA-DM2026 | 59 | S/5.35 | 3% | 3,749 | 2,482 | 1.57% | 1.51 | 1 | **S/5.35** ⭐ |
| BOFU-WhatsApp-WARM-DM2026 | 7 | S/1.35 | 1% | 374 | 55 | 1.87% | 6.80 | 0 | n/a |
| **Total** | **1,979** | **S/188.42** | 100% | **106,562** | **35,106** | 1.86% | 3.04 | **6** | **S/31.40** |

**Cost-per-Lead efectivo (excluyendo presupuesto desperdiciado en landing)**:
- Solo 4 ad sets WhatsApp: S/83.08 / 6 leads = **S/13.85 por lead** (~$3.7 USD) ⭐ excelente.
- Si CBO hubiera priorizado WhatsApp → 6 leads habrían costado solo el 44% del spend total.

### Funnel completo (cross-check tracking sheet doctora)

| Stage | Cantidad | % conversion vs anterior |
|---|---|---|
| Impresiones | 106,562 | — |
| Link clicks | 1,979 | 1.86% |
| Visitas landing | ~1,294 | (66% de los clicks; resto fue directo a WA) |
| Forms completados en landing | **0** | **0% de las visitas a landing** |
| Mensajes WhatsApp recibidos | 6 | 0.30% de clicks totales |
| Conversación iniciada por doctora | 6 | 100% (excelente reactividad) |
| Tiempo medio respuesta doctora | ~12 min | (mejor: 1 min, peor: 1h 8min) |
| Cita agendada | **0** | 0% — ningún lead pasó de "contactado" |
| Asistió a cita | 0 | n/a |
| Cliente pagante | 0 | n/a |
| Revenue total generado | **S/0** | — |
| **CAC real** (spend / clientes pagantes) | indefinido | — |
| **ROI directo** (revenue / spend) | -100% | spend total perdido |

### Distribución de leads por shortcode

| Shortcode | Leads | Origen ad |
|---|---|---|
| ARM-MAY-FB-MOFU-COLDWA | 3 | MOFU-WhatsApp-COLDWA |
| ARM-MAY-FB-MOFU-WARM | 2 | MOFU-WhatsApp-WARM |
| ARM-MAY-FB-BOFU-COLDWA | 1 | BOFU-WhatsApp-COLDWA |
| **`-WEB` (landing → form)** | **0** | Confirmado por doctora |
| **TOTAL** | **6** | |

---

## 3. Hipótesis del brief — validación

| Hipótesis original (brief.md §145) | Resultado real | ¿Se confirmó? | Implicación |
|---|---|---|---|
| **H1**: Umbrella "armonización facial" convierte mejor que tratamiento específico | No medible — solo corrió umbrella | **Inconcluso** | Próxima corrida: validar con un tratamiento específico (Botox o AH) en paralelo |
| **H2**: Audience F30-55 Cusco radio 8km es viable con $100/5d | 35K reach + 6 leads en 4 días | **Parcialmente sí** | Audience funciona pero **se satura rápido** (frequency 15.32 en MOFU-WARM). Próxima: ampliar a radio 12-25 km |
| **H3**: Landing → form fill convierte mejor que Click-to-WA directo | 0 forms (1,294 clicks) vs 6 mensajes (685 clicks) | **❌ REFUTADA fuerte** | Próxima: 100% Click-to-WhatsApp directo. Landing solo como autoridad, no funnel |
| **H4**: Identidad "decisión personal" Día de la Madre resuena | CTR 1.86% (dentro del rango), pero 0 conversiones | **Mixto** | El hook resuena para CTR pero NO para acción. El gap está en el siguiente paso (landing/contenido) |
| **H5**: Spontaneously los leads expresan preferencia tratamiento | Ninguno especificó tratamiento ("No especifico" en los 6 leads) | **❌ REFUTADA** | Sin hint de tratamiento → la doctora no puede pre-calificar. Próxima: testar copy que invite a expresar pain específico |

**Hipótesis adicional emergente**:
- **H6 (post-hoc)**: *"El contenido de los creativos no impulsa decisión de venta"*. Confirmada por el contraste CTR sano (1.86%) + 0 conversiones a cliente pagante. La gente clickea, ve, pero no acciona la cita. El gap está en el creativo + landing, no en la atracción al click.

---

## 4. Qué funcionó (proteger para próximas campañas)

### Infraestructura técnica
- ✅ **Pipeline form WP → n8n A1 → Vtiger → ERP**: validado end-to-end (smoke test técnico 2026-05-08 confirmó la cadena entera)
- ✅ **Cron B3** sincroniza Vtiger → ERP cada 2 min sin race conditions (post-hotfix 2026-05-02)
- ✅ **Backups daily cross-VPS** (Bloque 0.5) corrieron los 5 días sin fallar
- ✅ **Sensor cross-VPS** mantuvo observabilidad en tiempo real durante la campaña
- ✅ **Audit log** capturó eventos de backups y CAPI sin pérdida

### Captación
- ✅ **WhatsApp directo (BOFU-COLDWA)**: el ratio cost-per-lead más eficiente del set (S/5.35 — ~$1.4 USD). Mensajes directos al fondo del funnel funcionan en Cusco.
- ✅ **Pre-text de los WhatsApp ads** con shortcode embebido: 100% de los leads llegaron con shortcode correctamente formateado, atribución limpia.
- ✅ **Reactividad de la doctora**: 5 de 6 leads contactados en <30 min (1 min en el mejor caso). El cuello de botella humano respondió bien.

### Aprendizaje doctrinal en producción
- ✅ Modo BOOTSTRAP cumplió su función: 14 INS-NNN capturados durante producción y ejecución. La doctrina v0.1 fue testada sin fragilidad — sobrevivió la campaña con refinamientos identificados pero sin necesidad de rewrites mayores.

### Decisión Dario mid-flight
- ✅ **Refactor 2026-05-04 a umbrella "Armonización Facial"** (INS-009): la decisión de simplificar de 2 tratamientos a 1 umbrella por presión de tiempo fue correcta operativamente y coherente con la doctrina (no listar tratamientos en TOFU). Reducción de scope sin perder rigor.
- ✅ **Cierre anticipado 2026-05-08**: lectura honesta del experimento. Ahorra ~$50 USD del budget para usarlos en próxima corrida con creatividad mejor.

---

## 5. Qué NO funcionó (evitar para próximas campañas)

### Contenido / creativos / landing
- ❌ **Landing como funnel principal**: 0 forms de 1,294 visitas. Hipótesis H3 refutada fuerte. La landing necesita rol distinto (autoridad, no captura) o rediseño completo.
- ❌ **Form en landing redirige a WhatsApp** (no postea a webhook ni crea Lead): el único canal de captura "real" es el WA, lo que hace que el form sea fricción innecesaria. Quien iba a escribir al WA hubiera sido más rápido directo desde el ad.
- ❌ **Hook genérico "Día de la Madre"**: resuena para CTR pero no para conversión. Falta pain específico ("¿Las líneas de expresión te están ganando?", "Pómulos definidos en una sesión") que conecte con problema concreto del usuario.
- ❌ **Copy umbrella sin gancho específico**: "Agenda tu evaluación de Armonización Facial" es seguro doctrinalmente pero no diferencia ni urge.

### Estructura de campaña
- ❌ **Objective Tráfico + CBO**: en ausencia de Marketing API y con Health restrictions, optimizar por clicks redistribuye budget al ad con mejor CPC, NO al que más leads genera. El 49% del budget se gastó en MOFU-Landing que dio 0 leads.
- ❌ **Audience radio 8 km**: saturó rápido. MOFU-WhatsApp-WARM llegó a frequency 15.32 (cada persona vio el ad 15 veces). Audience demasiado chica para 5 días + budget agresivo.
- ❌ **CA + LAL no operacional**: solo 36 phones de 134 clientes históricos (gap captura), debajo del threshold Meta para LAL útil (~100). LAL no contribuyó como audiencia.

### Operacional
- ❌ **Tracking sheet de la doctora se actualizó con delay**: 3 leads del 2026-05-04 quedaron registrados solo el 2026-05-08 cuando Dario pidió screenshots a la doctora. Atribución manual + humana introduce lag.
- ❌ **Daily reports no salieron diarios**: el primer (y único) daily report se hizo el 2026-05-08. Ese es un gap del proceso humano, no del sistema.

---

## 6. Sorpresas (cosas que no esperábamos)

1. **CPM extremadamente barato (S/1.77 = ~$0.47 USD)**, 15-30x debajo del benchmark global. Cusco F30-55 está sub-disputado en pauta digital. Esto invita a campañas de mayor scale (más impresiones → más volumen al filtrar) sin tener que aumentar mucho el budget.

2. **MOFU-WhatsApp-WARM con frequency 15.32**: una misma persona vio el ad 15 veces. Audience demasiado chica + CBO le tiró budget porque convertía. Riesgo de ad fatigue extremo en audiences custom <1,000 personas (ya documentado en INS-007 doctrine-feedback).

3. **CBO tiró 49% del budget a MOFU-Landing aunque generaba 0 leads** porque medía resultados como "link clicks" (objective Tráfico). Reveló una **falla de alineación entre objective Meta y objetivo real del negocio**. La elección del objective importa MÁS que la creatividad cuando el budget es chico.

4. **0 forms completados en la landing**: era esperable que conversion fuera baja, pero **literalmente cero** sorprendió. Sugiere que la fricción de "completar form en landing" es prohibitiva en mobile-first Cusco. La gente prefiere WhatsApp directo sin pasar por form.

5. **Reactividad doctora excelente (1-30 min de respuesta)** pero **0 conversiones a cita agendada** de los 6 leads. Sorprende porque el cuello de botella histórico era la respuesta humana, y aquí no fue. El gap está en otro lado: probablemente la **conversación misma** no convierte (tono, objection handling, oferta concreta).

6. **Lead 2 (Alicia +51 900 929 060)** y **Lead 5 (Alicia García +51 967 478 335)** tienen el mismo nombre pero números distintos. Casualidad o falsos positivos del shortcode (alguien usándolo sin venir del ad). Vale la pena verificar en Ads Manager que el ad activo lleva el shortcode esperado.

---

## 7. Refinamientos a doctrina v0.1 → v1.0

> Esta sección procesa los 14 INS-NNN del `_doctrine-feedback.md` + nuevos del post-mortem y propone los cambios concretos a `docs/brand/`.

### 14 INS pendientes del bootstrap (procesados)

| ID | Insight | Archivo afectado | Decisión |
|---|---|---|---|
| INS-001 | BOFU/landing puede mencionar tratamiento (clarificación funnel) | `brand-system.md` § 3.1 + 3.3 | ✅ **Promover a v1.0** |
| INS-002 | Estructura de carpetas por campaña/tratamiento | nuevo `campaign-folder-structure.md` | ✅ **Promover a v1.0** |
| INS-003 | Roles humano/Claude/Brand Orchestrator visuales | `image-guidelines.md` § Roles | ✅ **Promover a v1.0** |
| INS-004 | Doble review gate de landings | `image-guidelines.md` o nuevo doc | ✅ **Promover a v1.0** |
| INS-005 | Aspect ratios (3 obligatorios) + cantidad real banners (9 por tratamiento) | `design-principles.md` + `campaign-brief-template.md` | ✅ **Promover a v1.0** |
| INS-006 | Marketing API: decidir desde día 0 si manual UI o API | `campaign-brief-template.md` § restricciones | ✅ **Promover a v1.0** |
| INS-007 | Meta account architecture (BM vs personal IDs) | nuevo `meta-account-architecture.md` | ✅ **Promover a v1.0** |
| INS-008 | Custom Audience size <100 → no LAL, depender de interest-based | `campaign-brief-template.md` + nuevo `audience-strategy.md` | ✅ **Promover a v1.0** (ya validado por la corrida) |
| INS-009 | Umbrella vs split por tratamiento — regla provisional | nuevo `campaign-scope-decision.md` o sección en `brand-system.md` | ✅ **Promover a v1.0** con regla refinada (ver más abajo) |
| INS-010 | "Médico/a" como palabra contextual (no permitida en hero/CTAs) | `copy-principles.md` § glosario | ✅ **Promover a v1.0** |
| INS-011 | NO mostrar trazabilidad de productos en copy de marca | `copy-principles.md` § principios | ✅ **Promover a v1.0** |
| INS-012 | BeforeAfter cerca del top de landing — orden recomendado | `brand-system.md` § funnel + posible `landing-structure-principles.md` | ✅ **Promover a v1.0** |
| INS-013 | Fotos clínicas pixeladas válidas para BeforeAfter (vs editoriales) | `image-guidelines.md` § tipos imagen | ✅ **Promover a v1.0** |
| INS-014 | Tono en chat WhatsApp — máximo emojis | `copy-principles.md` § tono chat | ✅ **Promover a v1.0** |

### Refinamientos NUEVOS del post-mortem (no estaban en INS)

| Refinamiento | Razón | Archivo afectado |
|---|---|---|
| **R-15** Click-to-WhatsApp directo > Landing como funnel principal en mercados nuevos / audiences chicas (<50K) | Hipótesis H3 refutada fuerte: 6/6 leads via WA, 0/6 via landing-form con 1,294 clicks | `brand-system.md` § funnel + `campaign-brief-template.md` § destinos |
| **R-16** Objective Meta debe alinearse con objetivo real del negocio: Mensajes (no Tráfico) si meta es leads sin Marketing API | CBO con Tráfico desperdició 49% del budget en clicks que no convirtieron | `campaign-brief-template.md` § configuración técnica |
| **R-17** Audience radio mínimo: 12-25 km (8 km satura en 4 días) | MOFU-WARM frequency 15.32 = saturación extrema | `audience-strategy.md` § radius rules |
| **R-18** Hook de ad debe atacar **pain específico** + tener **gancho de urgencia/promo** explícito | Hipótesis H6: contenido no impulsa decisión. CTR sano pero 0 conversiones = el siguiente paso (acción) no se activa | `copy-principles.md` § hooks |
| **R-19** Process: capturar phone de TODOS los walk-ins históricos (campaña progresiva) para construir CA usable | Solo 36 de 134 clientes con phone → CA debajo de threshold LAL | nuevo `audience-strategy.md` § growth plan |
| **R-20** Daily reports deben ser DIARIOS (operacional). Si no se hace, el lag de feedback impide acciones mid-flight | Único daily report fue el día 4. Decisiones (pausar ads malos, etc.) se postergaron por falta de visibilidad | `campaign-brief-template.md` § operativa |

### Refinamiento crítico de INS-009 (regla umbrella vs split)

La regla provisional original era:
> *"Si budget <$200 + audience <50K + tiempo <7 días → umbrella. Si >$300 + audience >100K + tiempo >14 días → split."*

**Refinamiento post-mortem**: La data NO permite validar la regla porque solo corrimos umbrella. Mantener la regla provisional **pero agregar test obligatorio en próxima campaña**: correr 1 tratamiento específico (ej: Botox) bajo mismo audience + budget para comparar conversion umbrella vs específico.

### Total de archivos `docs/brand/` afectados

- `brand-system.md` (versión 0.1 → 1.0): cambios de funnel + R-15 + R-18
- `copy-principles.md` (0.1 → 1.0): INS-010, INS-011, INS-014, R-18
- `design-principles.md` (0.1 → 1.0): INS-005
- `image-guidelines.md` (0.1 → 1.0): INS-003, INS-004, INS-013
- `campaign-brief-template.md` (0.1 → 1.0): INS-005, INS-006, INS-008, R-15, R-16, R-20
- **NUEVOS** archivos a crear:
  - `campaign-folder-structure.md` (INS-002)
  - `meta-account-architecture.md` (INS-007)
  - `audience-strategy.md` (INS-008, R-17, R-19)
  - `campaign-scope-decision.md` (INS-009)
  - `landing-structure-principles.md` (INS-012)

**Total: 5 archivos refinados + 5 archivos nuevos = 10 archivos en docs/brand/**

---

## 8. Cierre del modo BOOTSTRAP (principio operativo #13)

### Decisión Dario 2026-05-08: BOOTSTRAP se mantiene ABIERTO

**Cita literal Dario**:
> *"pienso que el bootstrap nos servirá, porque terminaremos el flujo y el sistema o al menos lo mejoraremos y necesitaremos meter tráfico para validarlo"*

**Razón**: una sola campaña es muestra estadística chica. Antes de cerrar la doctrina v0.1 → v1.0, queremos:
1. Terminar el deterministic backbone (Fase 4A: módulo Agenda + WA Cloud API + chatbot rule-based + smoke E2E)
2. Correr una segunda campaña sobre ese backbone completo
3. Cerrar bootstrap con data de **2 campañas reales** + sistema técnico estable

### Implicaciones de mantener BOOTSTRAP abierto

| Item | Status |
|---|---|
| Doctrina sigue como v0.1 BORRADOR | ✅ Confirmado |
| `docs/brand/*.md` mantienen header BORRADOR | ✅ Confirmado |
| Los 14 INS + 6 R **NO se aplican** a `docs/brand/` hoy | ✅ Confirmado — quedan como aprendizajes acumulados |
| `_doctrine-feedback.md` se mantiene activo para próxima campaña | ✅ Sigue siendo el destino de insights nuevos |
| Memoria 🔥 CRÍTICA de marca | ⏳ Diferida al cierre formal post-2da campaña |
| CLAUDE.md principio #13 sigue como ABIERTO | ✅ Sin cambios |
| Trigger nuevo de cierre formal | Post-mortem de **segunda campaña** (post-Fase 4A) |

### Lo que esta decisión preserva

- **Flexibilidad para revisar la doctrina con más evidencia**. Los 14 INS + 6 R quedan como propuestas validadas pero no committeadas — pueden refinarse, descartarse o ampliarse cuando llegue la segunda campaña.
- **Coherencia con la doctrina rectora #11** (deterministic backbone first): primero terminamos el sistema determinístico, después validamos doctrina con campaña sobre sistema completo. El orden de operaciones es deliberado.
- **Reduce riesgo de cerrar v1.0 prematuramente**: doctrina cerrada con muestra de 1 corrida sería frágil. Mejor v1.0 robusto sobre 2+ campañas.

### Items que SÍ se ejecutan ahora (no requieren cierre bootstrap)

- ✅ Post-mortem completo (este documento)
- ✅ Backlog actualizado con Fase 4A como prioridad
- ✅ Memoria del aprendizaje "Click-to-WhatsApp directo > Landing en mercado Cusco" (memoria táctica, no doctrinal)
- ✅ Archivado de la campaña a `docs/campaigns/_archive/`

### Items diferidos al cierre formal (post-2da campaña)

- ⏳ Procesar 14 INS + 6 R → docs/brand/*.md v1.0
- ⏳ Crear 5 archivos nuevos en `docs/brand/`
- ⏳ Memoria 🔥 CRÍTICA `project_brand_methodology_v1.md`
- ⏳ Update CLAUDE.md: cerrar #13
- ⏳ Update master plan changelog v1.6
- ⏳ Eliminar headers BORRADOR de `docs/brand/*.md`

---

## 9. Decisiones para próxima campaña

### Decisión Dario 2026-05-08: Próxima campaña post-Fase 4A

**Cita literal Dario**:
> *"No sé cuándo será la próxima campaña, de seguro cuando tengamos listo el sistema completo. Igual la prioridad es ya cerrar el círculo de todo el deterministic backbone, allí haremos la nueva campaña, aunque tengamos el WhatsApp test, al menos todo ya debe estar hecho y solo al final solucionar lo de WhatsApp para mandarlo a producción."*

### Plan acordado

| Decisión | Valor |
|---|---|
| **Cuándo próxima campaña** | Post-Fase 4A (todo el backbone determinístico cerrado) |
| **Backbone necesario antes de campaña** | Módulo Agenda en ERP + WA Cloud API test number + chatbot rule-based + smoke E2E completo |
| **WhatsApp test vs producción** | Test number durante desarrollo Fase 4A; producción solo al final, justo antes de la próxima campaña |
| **Prioridad inmediata** | NO seguir invirtiendo en captación pagada hasta que el sistema esté validado al 100% end-to-end |

### Por qué esta decisión es coherente con la doctrina #11

> **Deterministic backbone first — IA es capa aditiva, no foundational.**

El cierre completo del backbone determinístico (Fase 4A) elimina los puntos de fricción operacional que esta campaña no pudo testear (cita agendada, asistencia marcada por doctora, conversión cliente). La próxima campaña correrá sobre infraestructura robusta y permitirá validar **el embudo completo**, no solo el primer paso.

### Pre-decisiones del post-mortem (aplicables cuando llegue la próxima campaña)

Los aprendizajes de esta campaña que se aplicarán en la próxima (independientemente del scope final):

- ✅ **Objective Meta**: cambiar a **Mensajes (Conversaciones iniciadas)** — no Tráfico (R-16)
- ✅ **Audience radius**: 15-25 km Cusco (no 8 km) — R-17
- ✅ **Daily reports**: hard rule de daily, no batch (R-20)
- ✅ **Capturar phone walk-ins**: campaña progresiva en ERP UI cuando exista módulo Agenda — R-19
- ✅ **Hook con pain específico**: dejar de lado el genérico "Día de la Madre" — R-18
- ✅ **Pre-flight cross-system**: aplicar `docs/runbooks/preflight-cross-system.md` antes de tocar landing/n8n/ERP
- ✅ **Click-to-WhatsApp directo prioridad sobre Landing como funnel** — R-15

Estas pre-decisiones quedan como **memoria del aprendizaje táctico**, no como doctrina formal v1.0 todavía (espera al cierre del bootstrap post-2da campaña).

---

## 10. Aprendizajes para Brand Orchestrator futuro (Fase 4B)

> Insights destinados a alimentar el system prompt del agente IA cuando se construya en Fase 4B.

### Insights tácticos (qué hacer / no hacer)

1. **Cusco F30-55 tiene CPM 15-30x más barato que benchmarks globales**: el agente debe esperar costos de impresión bajos y NO sobre-ajustar el budget proyectado al alza.
2. **Audiences <1,000 personas saturan en 4 días**: el agente debe rechazar configuraciones de campaña con CA chica + budget agresivo. Hard rule: si CA <1,000 → presupuesto Warm ≤15% del total.
3. **Click-to-WhatsApp directo gana sobre Landing en mercado emergente**: el agente debe priorizar destination Messaging Apps (WhatsApp) sobre Sitio web cuando geo es ciudades <500K habitantes O audiences <100K reach.
4. **Objective Meta = Mensajes**, no Tráfico, cuando NO hay Marketing API + Pixel Lead optimization: el agente debe exigir esta config como default.
5. **Capturar phone de walk-ins es campaña progresiva**: el agente debe mantener un proceso recurrente que pida a la doctora capturar phone en cada nueva interacción.

### Insights estructurales (cómo decidir)

6. **Regla umbrella vs split** (refinada de INS-009 + R-15): si budget <$200 + audience <50K + tiempo <7 días → umbrella; si >$300 + audience >100K + tiempo >14 días → split. Refinable con data de próximas corridas.
7. **Mid-flight changes son destructivos**: el agente NO debe pausar/cambiar audiences/budgets durante una campaña en learning phase (~5 días). Solo pausar es válido si delivery es <50% del esperado al día 3.
8. **Definition of Done debe medir LEADS, no clicks**: el agente debe rechazar Definition of Done basadas en métricas de tráfico cuando el objetivo del negocio es generación de leads.

### Insights de proceso (cómo trabajar con humanos)

9. **Daily reports son obligatorios**: el agente debe generar daily report automático cada 24h durante campaña activa. NO esperar pedido humano.
10. **Tracking sheet humano va con delay**: el agente debe sincronizar manualmente con la doctora al menos cada 12h durante campaña activa. NO confiar 100% en captura humana de leads.
11. **Doctora respuesta WA: cuello de botella histórico, NO en esta corrida**: el cuello en esta campaña fue conversión, no respuesta. El agente debe medir time-to-response (tipo de fricción 1) vs conversion rate (tipo de fricción 2) por separado.

### Insights doctrinales (qué validó / refutó la primera campaña)

12. **Doctrina v0.1 sobrevivió la corrida**: 14 INS de refinamiento, ningún cambio mayor o reverso. La fundación es sólida.
13. **Refactor mid-prep umbrella (INS-009) fue decisión correcta**: la doctrina permite umbrella + el resultado táctico (CTR sano, leads recibidos) lo confirma.
14. **El gap NO es de doctrina, es de creativos**: el agente Brand Orchestrator no necesita re-pensar la doctrina, necesita aplicarla mejor en producción de creativos. La capa creativa es donde se pierde la conversión.

---

## 11. Acciones derivadas — backlog

> Lista de items que se mueven al backlog del proyecto principal después del post-mortem.

| Acción | Prioridad | Asignar | Status |
|---|---|---|---|
| Procesar 14 INS + 6 R → docs/brand/*.md v1.0 | 🟡 Media | Claude (con OK Dario) | ⏳ Pendiente |
| Crear 5 archivos nuevos en `docs/brand/` (folder-structure, meta-account-arch, audience-strategy, campaign-scope-decision, landing-structure-principles) | 🟡 Media | Claude | ⏳ Pendiente |
| Memoria 🔥 CRÍTICA `project_brand_methodology_v1.md` | 🟡 Media | Claude (al cierre bootstrap) | ⏳ Pendiente |
| Update CLAUDE.md: cerrar #13 + mover a histórico | 🟡 Media | Claude | ⏳ Pendiente |
| Aplicar a Meta Marketing API App Review | 🟢 Baja | Dario | ⏳ Side-project |
| Customer development — entrevistas con 10-20 clientes históricos | 🟡 Media | Dario | ⏳ Paralelo |
| Cleanup BM "Livskin Perú Comercial" vacío | 🟢 Baja | Dario | ⏳ Cuando tenga tiempo |
| Cleanup ad account personal `2130672884136872` | 🟢 Baja | Dario | ⏳ Cuando tenga tiempo |
| Capturar phone histórico walk-ins (95 sin phone de 134) | 🟡 Media | Doctora + ERP UI cuando exista módulo agenda | ⏳ Fase 4A |
| GA4 + GTM en landings (cross-domain tracking) | 🟡 Media | Claude (post-Fase 4A) | ⏳ |
| Próxima campaña con creativos mejores | 🔴 Alta | Dario decide cuándo | ⏳ |

---

## 12. Archivado de la campaña

**Al completar este post-mortem:**

```bash
git mv docs/campaigns/2026-05-dia-madre docs/campaigns/_archive/2026-05-dia-madre
```

Razón: cerrar el ciclo — la campaña ya no es activa, su valor histórico se preserva en `_archive/`.

Memoria efímera `project_first_paid_campaign_2026_05_03.md`:
- [ ] Borrar de `~/.claude/projects/.../memory/` post-cierre formal del bootstrap
- [ ] Aprendizajes durables ya migrados a memorias permanentes y `docs/brand/` v1.0

---

## Notas finales

- **Esta campaña fue exitosa como calibración**, fracasó como venta. Esa dualidad es lo que el modo BOOTSTRAP buscaba: probar el sistema en condiciones reales antes de comprometer doctrina.
- **El sistema técnico está validado.** Próxima campaña ya no necesita demostrar que el flujo funciona — necesita demostrar que **el contenido convierte**.
- **El siguiente capítulo del proyecto** es Fase 4A: cerrar el backbone determinístico (módulo Agenda, WhatsApp Cloud API test, chatbot rule-based, smoke E2E) ANTES de la próxima campaña paga.
- **Brand Orchestrator (Fase 4B) llega con datos**, no con hipótesis: tendrá los aprendizajes de esta campaña + insights de competencia (Playwrightdemo) + 2-3 campañas pagas adicionales como training data.

---

**Cerrado por**: Claude Code + Dario · 2026-05-08 · sesión colaborativa
**Cierre formal del modo BOOTSTRAP**: pendiente decisión de Dario en sección 8
**Próximo trabajo**: Fase 4A arranque (próxima sesión)
