---
campaign: 2026-05-dia-madre
type: bootstrap-feedback
mode: BOOTSTRAP (principio operativo #13)
purpose: capturar insights durante producción + ejecución de campaña que deben refinar la doctrina
processed_at_close: post-mortem 2026-05-12/13
---

# Doctrine Feedback — Campaña Día de la Madre 2026

> **Solo aplica mientras estamos en modo BOOTSTRAP** (principio operativo #13). Cada insight relevante para refinar `docs/brand/` se anota acá durante la campaña. Al cierre del bootstrap (post-mortem), se procesan en bloque BOOTSTRAP-feedback dedicado y se promueven a doctrina v0.X.

---

## Cómo se llena este archivo

Durante:
- **Producción** (Dario crea banners en Canva, Claude redacta copies, etc.)
- **Configuración** (setup Ads Manager, Custom Audience, etc.)
- **Lanzamiento** (primeras impresiones, ajustes)
- **Monitoring** (daily reports identifican patrones)

Cualquier insight del tipo *"esto debería ir en la doctrina porque..."* se anota aquí con:
- Insight concreto
- Archivo de doctrina afectado
- Por qué (razón)
- Quién lo detectó (Dario / Claude)
- Fecha
- Estado (pendiente / promovido / descartado)

---

## Insights acumulados

### Tipo de cambio: aclaraciones a la doctrina

#### [INS-001] (2026-05-04, Claude) — Aclaración: BOFU/landing puede mencionar tratamiento

**Contexto**: brief.md acepta que las landings core (botox-mvp, AH futura) mencionan tratamiento en hero, mientras que el doc de Guidelines decía estricto "NO listamos tratamientos en TOFU". Decisión Dario: 2 landings por tratamiento (no umbrella) acepta este trade-off.

**Razón**: el funnel TOFU/MOFU/BOFU del Guidelines aplica a los **ads** (que llevan al usuario en un journey identitario), pero la **landing** generalmente es BOFU (donde el doc sí permite mencionar evaluación/procedimiento). Si la landing es punto de aterrizaje post-ad, ya viene contextualizada.

**Archivo afectado**: `docs/brand/brand-system.md` § 3.3 BOFU + posible nota en § 3.1 TOFU

**Refinamiento propuesto a v0.2**: agregar aclaración en § 3.1 TOFU (sobre ads) y § 3.3 BOFU (sobre landings) explicitando que:
> "El funnel TOFU/MOFU/BOFU se aplica al **journey de ads** (cómo se pasa al lead de cold a warm a hot). La **landing** suele ser BOFU del journey: aceptable mencionar tratamiento + evaluación si el ad fue identitario. La landing es donde se 'aterriza' la decisión, no donde se activa."

**Estado**: 🟡 pendiente promoción a v0.2 al cierre del bootstrap

---

#### [INS-002] (2026-05-04, Claude) — Estructura de carpetas por campaña/tratamiento

**Contexto**: Dario propuso estructura `docs/campaigns/<camp>/<trat>/{banners,fotos,landing-source}/` para que él tenga UN solo lugar centralizado donde dejar assets. Esto NO está en la doctrina — debería formalizarse.

**Razón**: estructura replicable obligatoria para todas las campañas futuras. Reduce fricción operativa significativamente.

**Archivo afectado**: nuevo `docs/brand/campaign-folder-structure.md` (archivo modular como los otros 5 de doctrina)

**Refinamiento propuesto a v0.2**: crear archivo nuevo + actualizar `docs/brand/README.md` (índice de 5 → 6 archivos).

**Estado**: 🟡 pendiente promoción a v0.2 al cierre del bootstrap

---

#### [INS-003] (2026-05-04, Claude) — Alcance honesto de capacidades Claude vs Dario

**Contexto**: Dario forzó honestidad técnica radical sobre qué hace bien Claude (texto + sistema + integración) vs qué NO (diseño visual, edición fotos, banners). El alcance real:
- Claude: copies, briefs, integración técnica, tracking, sistema, post-mortem
- Dario: diseño visual de banners + landings + edición fotos
- Foto: drag-drop o `_pending-uploads/` o batches via carpeta de tratamiento

**Razón**: sin esto explícito, expectativas se desalinean. El sistema de carpetas funciona porque cada uno sabe qué produce.

**Archivo afectado**: `docs/brand/image-guidelines.md` § "Mecánica de upload" (ya tiene parte de esto, pero falta la separación clara de roles humano vs Claude vs Brand Orchestrator futuro)

**Refinamiento propuesto a v0.2**: sección nueva "Roles y responsabilidades visuales" en image-guidelines.md.

**Estado**: 🟡 pendiente promoción a v0.2 al cierre del bootstrap

---

#### [INS-004] (2026-05-04, Claude) — Review gate explícito antes de inyección técnica

**Contexto**: Dario exigió que ANTES de cualquier inyección técnica de tracking/Pixel/conventions, Claude pregunte "¿esta versión está lista para producción o necesita cambios?". Iteraciones de cambios viven en `landing-source/` (NO en `infra/`) hasta que esté lista. Doble review gate.

**Razón**: prevenir que landings no aprobadas lleguen a producción por inyección automática.

**Archivo afectado**: `docs/brand/campaign-folder-structure.md` (si se crea — INS-002) o nueva sección en `image-guidelines.md`

**Refinamiento propuesto a v0.2**: protocolo formal "Doble review gate de landings" como sección dedicada.

**Estado**: 🟡 pendiente promoción a v0.2 al cierre del bootstrap

---

### Tipo de cambio: aspect ratios + producción de banners

#### [INS-005] (2026-05-04, Claude) — Cantidad real de banners por campaña

**Contexto**: la doctrina inicial sugería 3 banners (TOFU/MOFU/BOFU). En realidad, una campaña FB Ads profesional requiere **3 ideas creativas × 3 aspect ratios = 9 banners por tratamiento**. El número real es **18 banners para 2 tratamientos**.

**Aspect ratios obligatorios**:
- 1:1 (1080×1080) — FB Feed, IG Feed, Marketplace, Carousel
- 4:5 (1080×1350) — FB Feed mobile, IG Feed mobile (mejor performance)
- 9:16 (1080×1920) — FB Stories, IG Stories, Reels

**Razón**: cada placement Meta tiene aspect ratio óptimo. Sin variantes, el ad se serve mal en placements no-cuadrados. Esto baja CTR significativamente.

**Archivo afectado**: `docs/brand/design-principles.md` (agregar sección de aspect ratios) + `docs/brand/campaign-brief-template.md` (sección "Activos a producir" especificar)

**Refinamiento propuesto a v0.2**: tabla canónica de aspect ratios + checklist de producción por banner.

**Estado**: 🟡 pendiente promoción a v0.2 al cierre del bootstrap

---

### Tipo de cambio: configuración técnica de campaña

#### [INS-008] (2026-05-04, Claude — corregido contexto post-feedback Dario) — Captura inconsistente de phone en walk-ins

**Contexto correcto**: TODOS los 131 clientes activos son walk-ins (Livskin ha sido 100% word-of-mouth pre-Mini-bloque 3.6). De estos:
- **36 dejaron su número** (la doctora lo capturó al atenderlos)
- **95 NO** tienen phone capturado (la doctora no siempre lo anotó — gap de proceso humano, NO diferencia de origen del cliente)

**Mi error inicial**: dije "95 son walk-ins históricos sin phone" — implicando otra fuente. Corrigo: TODOS son walk-ins. El gap es la captura inconsistente del número de teléfono.

**Razón del gap**: hasta antes del Mini-bloque 3.6 (landings + form digital), Livskin no tenía proceso sistemático de captura. La doctora apuntaba phone si le parecía relevante; muchas veces no lo registró.

**Implicación para Custom Audience + LAL Meta**:
- Meta recomienda mínimo ~100 personas en source audience para Lookalike Audience útil
- Con 36 phones: LAL puede ser rechazada por Meta o tener confidence muy baja
- **No podemos depender de LAL** como audiencia principal de esta campaña

**Refinamiento al plan operativo**:
- Ajustar campaña a depender 100% de **interest-based targeting + behavior** como audiencia primary
- CA + LAL como targeting secundario (intentamos subirla pero NO confiamos en ella)
- Si Meta rechaza LAL → seguimos con interest-based puro, no afecta lanzamiento

**Implicación de proceso para futuras campañas**:
- Necesitamos un **proceso de captura de phone para walk-ins** post-Bridge Episode
- Idea: doctora anota phone al atender nuevo cliente walk-in (campo `clientes.phone_e164` ya existe desde ADR-0011 v1.1)
- Cada campaña → más phones acumulados → LAL crece en quality progresivamente

**Archivo afectado en doctrina**: `docs/brand/campaign-brief-template.md` § restricciones operativas

**Refinamiento propuesto a v0.2**:
- Agregar al template: "verificar tamaño de Custom Audience disponible vs Meta requirements (~100 personas para LAL)"
- Decisión consciente: si <100 personas, NO depender de LAL
- Plan de crecimiento progresivo de CA campaña a campaña

**Archivo nuevo eventual (post-bootstrap)**: `docs/brand/audience-strategy.md` con guideline de cuándo usar CA/LAL/interest-based según tamaño disponible.

**Estado**: 🔴 **CRÍTICO PARA ESTA CAMPAÑA** — ajusta el config inmediatamente. Promoción a v0.2 al cierre del bootstrap.

---

#### [INS-006] (2026-05-04, Claude) — Marketing API token: lecciones del intento previo

**Contexto**: el intento de generar Marketing API token (sesión 2026-04-27) falló iterativamente. Decisión esta vez: **NO repetir ese camino**, ir 100% UI manual con checklist exhaustivo paso-a-paso. App Review formal queda en backlog post-Bridge.

**Razón**: honestidad sobre limitaciones técnicas de Meta + tiempo limitado (7 días hasta DM) + experiencia previa documentada.

**Archivo afectado**: ninguno de doctrina directamente — es decisión operacional. Pero **patrón replicable** para campañas futuras: si no tenemos Marketing API, decidir manual UI desde el inicio, no perder tiempo intentando.

**Refinamiento propuesto a v0.2**: nota en `docs/brand/campaign-brief-template.md` § restricciones operativas: "Verificar disponibilidad de Marketing API token al inicio. Si no, planear setup UI manual desde día 0 — no intentar generación de token mid-campaign."

**Estado**: 🟡 pendiente promoción a v0.2 al cierre del bootstrap

---

#### [INS-007] (2026-05-04, Claude) — Ad account confusion: Business Manager vs personal

**Contexto**: Dario tenía 3 contenedores Meta (2 BMs + cuenta personal) y se confundía entre cuál estaba usando. La verdad: única ad account operativa es `2885433191763149` (BM Livskin Perú). La "cuenta personal" `2130672884136872` está vacía y nunca se usó realmente.

**Razón**: confusion entre "user que opera" (Dario logueado) vs "ad account donde viven las campañas" (`2885433191763149`).

**Archivo afectado**: posible nuevo `docs/brand/meta-account-architecture.md` (estructura clara de IDs + assets)

**Refinamiento propuesto a v0.2**: documento de referencia de IDs Meta (BM ID, ad account ID, Pixel ID, app IDs) con diagrama de relaciones. Para que cualquier sesión nueva tenga claridad inmediata sobre qué cuenta es qué.

**Estado**: 🟡 pendiente promoción a v0.2 al cierre del bootstrap

---

## Insights post-monitoring (a llenar durante días 1-5 de campaña)

> Esta sección se llena conforme corre la campaña.

### Patrones de performance

- (a llenar)

### Sorpresas en audience

- (a llenar)

### Creatives que rompen la doctrina pero performean (paradojas)

- (a llenar)

### Refinamientos a copy-principles.md sugeridos por data real

- (a llenar)

---

## Procesamiento al cierre (post-mortem)

Al cierre del modo bootstrap (post-mortem 2026-05-12/13):

1. Cada [INS-NNN] se evalúa: ¿promueve a doctrina o se descarta?
2. Si promueve: commit `docs(brand): refinamiento v0.X → v0.X+1 — [razón breve]` con cambio aplicado
3. Si se descarta: marcar 🔴 con razón
4. Estados finales se documentan en `post-mortem.md` § 7

---

## Notas operativas

- **Fecha de creación**: 2026-05-04 (modo bootstrap apertura)
- **Fecha estimada de cierre**: 2026-05-13 (post-mortem)
- **Cierre formal**: trigger del cierre del modo bootstrap (principio #13)
- **Archivado**: post-cierre, este archivo se mueve a `docs/campaigns/_archive/2026-05-dia-madre/_doctrine-feedback.md` como histórico
