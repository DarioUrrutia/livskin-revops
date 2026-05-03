---
campaign: Livskin — Día de la Madre 2026
slug: 2026-05-dia-madre
status: BORRADOR — pendiente aprobación Dario
created: 2026-05-04
launches: 2026-05-05 (target)
ends: 2026-05-09 (target)
mothers_day_peru: 2026-05-11 (Domingo)
---

# Campaign Brief — Livskin Día de la Madre 2026

> **Plantilla aplicada**: `docs/brand/campaign-brief-template.md` v0.1 BORRADOR (modo bootstrap principio #13)
>
> **Gate de aprobación**: las 4 preguntas DEBEN estar respondidas con claridad ANTES de tocar cualquier asset (banners, fotos, landings). Sin claridad → no se construye.

---

## Identificación

| Campo | Valor |
|---|---|
| Nombre | Livskin Día de la Madre 2026 |
| Slug técnico | `2026-05-dia-madre` |
| Frame contextual | Día de la Madre Perú = Domingo 11 de mayo 2026 |
| Fecha lanzamiento | 2026-05-05 (lunes) |
| Fecha cierre | 2026-05-09 (viernes) — 4 días pre-DM + viernes para conversiones tardías |
| Budget | $100 USD lifetime |
| Plataforma | Meta (Facebook + Instagram) — solo |
| Ad account | `2885433191763149` (Business Manager Livskin Perú) |
| Pixel | `4410809639201712` (Livskin 2026) |
| Operador | Dario (UI manual Ads Manager — sin Marketing API token esta vez) |
| Doctora aprueba copy | [ ] Pendiente |
| Brief aprobado por Dario | [ ] **PENDIENTE — gate de aprobación** |

---

## Las 4 preguntas (gate obligatorio)

### 1. ¿Qué identidad activa?

**Madre que decide cuidarse a sí misma — recibir tiempo en vez de solo darlo.**

El Día de la Madre tradicionalmente activa el código de "darle algo a mamá". Livskin invierte el frame: **la mamá decide darse algo a sí misma**. No es "recibir un regalo de los hijos" — es "recibir tiempo de sí misma".

Arquetipo: mujer 35-55, con hijos, vive en Cusco. Económicamente estable, ha cuidado a otros toda su vida, y este día específicamente se permite priorizarse. NO espera permiso de la familia — decide.

### 2. ¿Qué emoción genera?

**Permiso interno + tranquilidad.** No urgencia, no ansiedad, no comparación.

NO buscamos: FOMO, "última oportunidad", urgencia barata.

SÍ buscamos: la sensación de pausa, de "para mí también", de control sobre lo propio.

### 3. ¿Qué decisión sugiere?

**Dedicarse una hora a sí misma — evaluación con criterio médico en Livskin.**

NO sugerimos: "agendar tratamiento de Botox/AH" (ese es el siguiente paso, decisión de la doctora en consulta).

SÍ sugerimos: **conversación con la doctora vía WhatsApp** para empezar a explorar — la decisión sobre qué tratamiento (si alguno) la toma la doctora con ella en consulta presencial.

### 4. ¿Qué NO está diciendo?

**Lista explícita de frames evitados** (aplicación rigurosa de `docs/brand/copy-principles.md`):

- ❌ NO promete rejuvenecer / "eliminar arrugas" / "quitar años"
- ❌ NO dice "tu hijo te lo regala" (frame regalo de tercero)
- ❌ NO menciona precios / descuentos / promociones
- ❌ NO crea urgencia barata ("antes del 11", "última oportunidad")
- ❌ NO usa "envejecimiento" / "problema" / "defecto"
- ❌ NO menciona Botox o Ácido Hialurónico en TOFU/MOFU del ad (sí en el banner BOFU del que ya identificó tratamiento)
- ❌ NO promete "resultados inmediatos" / "garantizados"
- ❌ NO usa modelos artificiales / sonrisas exageradas / piel digital

---

## Aplicación del funnel a esta campaña

**Decisión arquitectónica**: Opción A — todos los ads optimizan para **Click-to-WhatsApp** (Engagement → Maximize messages).

| Etapa | Aplica en esta campaña |
|---|---|
| **TOFU** | Banners de declaración de identidad — abren WhatsApp con shortcode |
| **MOFU** | Banners explicativos emocionales — abren WhatsApp con shortcode (mismo destino que TOFU) |
| **BOFU** | Banners más directos — abren WhatsApp con shortcode |

**Nota importante**: aunque los banners siguen TOFU/MOFU/BOFU como código creativo (declaración → consideración → acción), **TODOS terminan en WhatsApp directo**. No hay landing pages de Día de la Madre en esta campaña — la audiencia chica de Cusco + objetivo simple "máximo contacto WhatsApp" no justifica el costo de producir landings dedicadas.

Las landings core (`botox-mvp` evergreen) siguen vivas para tráfico orgánico, pero no se promocionan en esta campaña.

---

## Destinos y atribución

| Destino | Tipo | Tracking |
|---|---|---|
| WhatsApp Botox | `wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20Día%20de%20la%20Madre%20%5BBTX-MAY-FB%5D` | Shortcode `[BTX-MAY-FB]` manual + Pixel "Lead" event vía Custom Conversion |
| WhatsApp Ácido Hialurónico | `wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20Día%20de%20la%20Madre%20%5BAH-MAY-FB%5D` | Shortcode `[AH-MAY-FB]` manual + Pixel "Lead" event |

Tracking flow:
1. Usuario clickea ad → WhatsApp se abre con mensaje pre-poblado con shortcode
2. Usuario manda mensaje (la mayoría sin editar texto)
3. Doctora ve shortcode → anota en Google Sheet manual
4. Al final de la campaña, cruzamos sheet con métricas de Ads Manager

---

## Activos a producir (operacional)

### Por Dario en Canva (banners visuales)

Por cada tratamiento (Botox + AH = 2 tratamientos):
- **3 ideas creativas** (TOFU declaración / MOFU consideración / BOFU acción)
- **3 aspect ratios cada una** (1:1 1080x1080 + 4:5 1080x1350 + 9:16 1080x1920)
- Total: **9 banners por tratamiento × 2 tratamientos = 18 banners**

Lugar: `docs/campaigns/2026-05-dia-madre/<tratamiento>/banners/`

### Por Claude (sistema + texto)

- ✅ Este `brief.md` (gate aprobación)
- ⏳ `campaign-config-draft.md` (configuración técnica exhaustiva)
- ⏳ `ads-manager-checklist.md` (paso a paso UI manual)
- ⏳ `copies.md` por tratamiento (textos para banners bajo doctrina)
- ⏳ `tracking.md` por tratamiento (UTMs específicas)
- ⏳ CSV de Custom Audience (131 clientes hasheados)

---

## Hipótesis a validar (qué aprendemos de esta campaña)

| Hipótesis | Cómo se mide | Decisión que informa |
|---|---|---|
| Click-to-WhatsApp directo convierte mejor que landing→form para Cusco | Cost-per-message (Meta) + leads anotados en sheet manual | Si CPL <$10 USD: scale en próximas campañas. Si >$15: revisar segmentación |
| Botox vs AH: cuál convierte mejor en Cusco | Mensajes WhatsApp por shortcode | Próxima campaña: ajustar budget allocation |
| Audience F30-55 Cusco radio 5-8km es viable | Frequency + impresiones + CTR | Refinar audience post-mortem |
| LAL 1-3% sobre 131 clientes mejora performance | Comparar ad set con LAL vs solo interest-based | Si funciona: subir CA es práctica estándar |
| Identidad "decisión personal" del Día de la Madre resuena | CTR por banner (TOFU declaración vs alternativa) | Refinar doctrina v0.2 |
| Ads sin mencionar tratamiento específico convierten | Tasa de mensaje por banner | Validar principio "no producto en TOFU" |

---

## Restricciones operativas

- [x] Doctrina de marca v0.1 BORRADOR cargada (`docs/brand/`)
- [ ] Custom Audience subida a ad account `2885433191763149` (Dario, ~30 min UI)
- [ ] Lookalike Audience 2-3% creada en Cusco (Meta tarda 24-48h en preparar)
- [ ] Pixel + CAPI verificados con flujo end-to-end (ya validado 2026-05-03 Tarea 1)
- [ ] Compliance Meta health category — verificar al crear ad (puede aplicar "Special Ad Category")
- [ ] Banners 18 producidos por Dario en Canva
- [ ] Pre-aprobación copy por Dario (línea por línea de `copies.md`)
- [ ] Doctora informada del shortcode tracking + cheat sheet imprimible

---

## Aprendizajes para doctrina (modo BOOTSTRAP)

> Sección obligatoria mientras estamos en bootstrap (principio #13). Cada insight relevante para refinar `docs/brand/` se anota acá durante la campaña + se procesa al cierre del Bloque BOOTSTRAP-feedback.

| Insight | Archivo doctrina afectado | Promovido a v0.X | Commit |
|---|---|---|---|
| (a llenar durante producción y campaña) | | | |

Archivo dedicado: `_doctrine-feedback.md` en raíz de la campaña.

---

## Post-mortem (completar al cerrar)

→ `post-mortem.md` (template vacío — se llena 2026-05-12/13).

---

## Cross-link

- Doctrina: `docs/brand/` v0.1 BORRADOR
- Plan operativo: `plan.md` en esta carpeta
- Configuración técnica detallada: `campaign-config-draft.md`
- Checklist Ads Manager UI: `ads-manager-checklist.md`
- Copies por tratamiento: `botox/copies.md`, `acido-hialuronico/copies.md`
- Tracking sheet doctora: `tracking.md` (raíz de campaña, consolidado)

---

## Estado del brief

**APROBACIÓN PENDIENTE DE DARIO.** Cuando vos aprobés explícitamente este brief, procedemos con `campaign-config-draft.md` técnico + `ads-manager-checklist.md`.

Acción de Dario:
- [ ] Leer las 4 preguntas (§ "Las 4 preguntas")
- [ ] Aprobar respuesta de cada una (o pedir ajuste)
- [ ] Confirmar approach Opción A (todo Click-to-WhatsApp, no landings de campaña)
- [ ] Confirmar fechas de lanzamiento (5-9 may)
- [ ] Confirmar budget $100 lifetime
- [ ] Confirmar shortcode `[BTX-MAY-FB]` y `[AH-MAY-FB]`
