---
campaign: Livskin — Día de la Madre 2026
slug: 2026-05-dia-madre
treatment_frame: armonizacion-facial (umbrella Botox + Ácido Hialurónico)
status: BORRADOR — pendiente aprobación Dario
created: 2026-05-04
refactored: 2026-05-04 (de 2 tratamientos separados → 1 umbrella por presión de tiempo)
launches: 2026-05-05 (target)
ends: 2026-05-09 (target)
mothers_day_peru: 2026-05-11 (Domingo)
---

# Campaign Brief — Livskin Día de la Madre 2026 — Armonización Facial

> **Plantilla aplicada**: `docs/brand/campaign-brief-template.md` v0.1 BORRADOR (modo bootstrap principio #13)
>
> **Refactor 2026-05-04**: la campaña pasa de 2 tratamientos separados (Botox + AH) a **1 umbrella "Armonización Facial"** por presión de tiempo + alineación con doctrina del doc Guidelines (no listar tratamientos en TOFU). La doctora decide en consulta presencial qué tratamiento aplicar.
>
> **Gate de aprobación**: las 4 preguntas DEBEN estar respondidas con claridad ANTES de tocar cualquier asset.

---

## Identificación

| Campo | Valor |
|---|---|
| Nombre | Livskin Día de la Madre 2026 — Armonización Facial |
| Slug técnico | `2026-05-dia-madre` |
| Frame umbrella | Armonización Facial (cubre Botox + Ácido Hialurónico) |
| Fecha lanzamiento | 2026-05-05 (lunes) |
| Fecha cierre | 2026-05-09 (viernes) |
| Budget | $100 USD lifetime |
| Plataforma | Meta (Facebook + Instagram) |
| Ad account | `2885433191763149` (Business Manager Livskin Perú) |
| Pixel | `4410809639201712` (Livskin 2026) |
| Operador | Dario (UI manual Ads Manager) |
| Doctora aprueba copy | [ ] Pendiente |
| Brief aprobado por Dario | [ ] **PENDIENTE — gate de aprobación** |

---

## Las 4 preguntas (gate obligatorio)

### 1. ¿Qué identidad activa?

**Madre que decide cuidarse a sí misma — recibir tiempo en vez de solo darlo.**

El Día de la Madre tradicionalmente activa el código de "darle algo a mamá". Livskin invierte el frame: la mamá decide darse algo a sí misma. Bajo umbrella "armonización facial" — porque la armonización es sobre **decidir cómo se ve tu rostro**, no sobre un tratamiento específico.

Arquetipo: mujer 35-55 en Cusco, con hijos, económicamente estable, ha cuidado a otros toda su vida, este día específicamente se permite priorizarse.

### 2. ¿Qué emoción genera?

**Permiso interno + tranquilidad.** No urgencia, no ansiedad, no comparación.

Sí buscamos: pausa, "para mí también", control sobre lo propio.

### 3. ¿Qué decisión sugiere?

**Dedicarse una hora a evaluación con la doctora — para conocer su armonía facial.**

NO sugerimos: "agendar Botox" o "agendar relleno". La decisión sobre qué tratamiento se aplica es médica, la toma la doctora con la paciente en consulta presencial. **Por eso umbrella "armonización facial" es coherente** — el ad invita a la conversación, no a un producto.

### 4. ¿Qué NO está diciendo?

- ❌ NO menciona "Botox", "ácido hialurónico", "rellenos", "toxina"
- ❌ NO promete rejuvenecer / "eliminar arrugas" / "quitar años"
- ❌ NO dice "tu hijo te lo regala"
- ❌ NO menciona precios / descuentos / promociones
- ❌ NO crea urgencia barata ("antes del 11", "última oportunidad")
- ❌ NO usa "envejecimiento" / "problema" / "defecto"
- ❌ NO promete "resultados inmediatos" / "garantizados"
- ❌ NO usa modelos artificiales / sonrisas exageradas

---

## Aplicación del funnel a esta campaña

**Decisión arquitectónica**: 1 campaña umbrella → todos los ads van a **1 landing page "Armonización Facial"**.

| Etapa | Aplica |
|---|---|
| **TOFU** | Banner declaración de identidad → click → landing |
| **MOFU** | Banner explicativo emocional → click → landing |
| **BOFU** | Banner directo evaluación → click → landing |

La landing tiene CTA principal a WhatsApp con shortcode `[ARM-MAY-FB]` + form (Pixel Lead optimization).

---

## Destinos y atribución

**1 landing umbrella**:
- URL: `https://campanas.livskin.site/dia-madre-armonizacion-2026/`
- Slug técnico: `dia-madre-armonizacion-2026`
- Path repo: `infra/landing-pages/dia-madre-armonizacion-2026/` (a crear cuando reciba la versión casi-final de Dario)

**WhatsApp tracking shortcode** (en CTA dentro de landing):
- `[ARM-MAY-FB]` — único shortcode

Tracking flow:
1. Usuario clickea ad → Pixel `Click` event
2. Llega a landing → Pixel `PageView`
3. Llena form O clickea CTA WhatsApp → Pixel `Lead` event
4. Si WhatsApp directo: doctora ve shortcode `[ARM-MAY-FB]` en mensaje → anota en Google Sheet
5. Cross-check al final: form leads (Pixel) + WA leads (manual sheet) = leads totales

---

## Activos a producir

### Por Dario en Canva (banners)

- **3 banners principales** (TOFU/MOFU/BOFU) ← drag-drop a Claude o `armonizacion-facial/banners/`
- **Aspect ratio variants** (1:1, 4:5, 9:16) por cada banner — Dario los hace en Canva y **sube directo a FB Ads Manager** (no archiva en repo)

### Por Dario en claude.ai/design u otra herramienta (landing)

- 1 landing casi-final basada en estructura de la botox-mvp existente
- Adaptar texto a frame "Armonización Facial" (Botox + AH simultáneamente)
- Pegar a Claude para review gate + adaptación técnica + deploy

### Por Dario incrementalmente (fotos)

- Fotos para la landing pasadas "poco a poco" después de tener todo organizado
- Claude integra cada foto cuando llegue (mover a `infra/uploads/` + actualizar HTML)

### Por Claude (sistema + texto)

- ✅ Este `brief.md` (gate aprobación)
- ✅ `plan.md` operativo
- ✅ `tracking.md` consolidado
- ✅ `campaign-config-draft.md` técnico
- ✅ `ads-manager-checklist.md` UI manual
- ✅ `armonizacion-facial/` con README + copies + landing.md + tracking.md
- ⏳ Adaptación landing al sistema (10 pasos cuando llegue)
- ⏳ Compliance review banners (al recibir)
- ⏳ Daily reports durante campaña
- ⏳ Post-mortem

---

## Hipótesis a validar (qué aprendemos)

| Hipótesis | Cómo se mide | Decisión que informa |
|---|---|---|
| Umbrella "armonización facial" convierte mejor que tratamiento específico | CTR + form lead rate vs benchmark interno | Próxima campaña: validar umbrella vs split por tratamiento |
| Audience F30-55 Cusco radio 8km es viable con $100/5 días | Frequency + impresiones + cost per lead | Refinar audience post-mortem |
| Landing → form fill convierte mejor que Click-to-WhatsApp directo | Pixel Lead events vs mensajes manuales WA | Decide próxima inversión: optimizar landing o ir directo a WA |
| Identidad "decisión personal" Día de la Madre resuena | CTR por banner (TOFU declaración) | Refinar doctrina v0.2 |
| Spontaneously los leads expresan preferencia tratamiento (Botox vs AH) | Doctora anota en sheet qué dice cada lead | Validar split 60/40 histórico vs preferencia orgánica |

---

## Restricciones operativas

- [x] Doctrina de marca v0.1 BORRADOR cargada (`docs/brand/`)
- [ ] Custom Audience subida a ad account (Dario, ~10 min)
- [ ] LAL creada (Meta procesa 24-48h) — opcional, no bloquea
- [ ] Pixel + CAPI verificados (ya validado 2026-05-03)
- [ ] Compliance Meta health category — verificar al crear ad
- [ ] 3 banners principales producidos por Dario en Canva
- [ ] Aspect ratio variants generadas por Dario
- [ ] Landing casi-final entregada por Dario
- [ ] Pre-aprobación copy por Dario
- [ ] Doctora informada del shortcode + cheat sheet impreso

---

## Aprendizajes para doctrina (modo BOOTSTRAP)

Ver [`_doctrine-feedback.md`](_doctrine-feedback.md) para insights acumulados durante producción + ejecución.

Insight relevante de este refactor: `INS-009` (cambio de scope mid-prep — de 2 tratamientos a 1 umbrella por presión de tiempo).

---

## Estado del brief

**APROBACIÓN PENDIENTE DE DARIO.** Cuando vos aprobés explícitamente, procedemos con producción de banners + landing + checklist UI.

Acción de Dario:
- [ ] Leer las 4 preguntas (§ "Las 4 preguntas")
- [ ] Aprobar respuesta de cada una (o pedir ajuste)
- [ ] Confirmar approach: 1 campaña umbrella + 1 landing
- [ ] Confirmar fechas (5-9 may)
- [ ] Confirmar budget $100 lifetime
- [ ] Confirmar shortcode `[ARM-MAY-FB]`
