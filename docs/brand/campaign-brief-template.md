---
type: brand-doctrine-template
version: 0.1
status: BORRADOR
parent: brand-system.md
purpose: plantilla a duplicar al inicio de cada nueva campaña — gate de aprobación obligatorio antes de tocar assets
---

# Campaign Brief Template — Livskin

> **Cómo se usa:** copiá este archivo a `docs/campaigns/<YYYY-MM-name>/brief.md` y completá las 4 preguntas + secciones operativas. Si las 4 preguntas NO están respondidas con claridad, **no se construye nada** todavía.

---

## Identificación de la campaña

| Campo | Valor |
|---|---|
| Nombre | <ej: Día de la Madre 2026> |
| Slug técnico | <ej: 2026-05-dia-madre> |
| Frame contextual | <fecha / ocasión / por qué AHORA> |
| Fecha lanzamiento | YYYY-MM-DD |
| Fecha cierre | YYYY-MM-DD |
| Budget | $XXX USD lifetime |
| Plataformas | <FB Ads / Google Ads / orgánico> |
| Doctora aprueba copy | [ ] Sí / [ ] Pendiente |
| Brief aprobado por Dario | [ ] Sí / [ ] Pendiente |

---

## Las 4 preguntas (gate obligatorio)

### 1. ¿Qué identidad activa?

> Describí explícitamente el arquetipo de persona que la campaña le habla. NO el demográfico — la identidad. *(Ejemplo: "Madre que decide cuidarse a sí misma — recibir tiempo en vez de solo darlo".)*

**Respuesta:**

[texto]

---

### 2. ¿Qué emoción genera?

> 1-2 emociones específicas. NO "felicidad genérica". *(Ejemplo: "Permiso interno + tranquilidad — no urgencia, no ansiedad".)*

**Respuesta:**

[texto]

---

### 3. ¿Qué decisión sugiere?

> La acción interna que activa antes que la externa. *(Ejemplo: "Dedicarse una hora — evaluación con criterio médico". NO "agendar botox".)*

**Respuesta:**

[texto]

---

### 4. ¿Qué NO está diciendo?

> Lista explícita de palabras / frames / promesas que la campaña EVITA. Esto previene el deslizamiento al copy clínico. *(Ejemplo: "NO promete rejuvenecer, NO 'tu hijo te lo regala', NO precios, NO descuentos, NO urgencia barata".)*

**Respuesta:**

[texto]

---

## Aplicación del funnel

### TOFU (atracción)

| Componente | Decisión |
|---|---|
| Headline | <declaración de identidad, máx 6-8 palabras> |
| Sub-headline | <refuerza decisión, máx 12 palabras> |
| Imagen tipo | <descripción de qué comunica antes del texto> |
| CTA | "Descubre más →" |

### MOFU (consideración)

| Componente | Decisión |
|---|---|
| Mensaje principal | <explicativo emocional, sin nombrar producto> |
| Imagen | <coherencia visual con TOFU obligatoria> |
| CTA | <evolución, no repetición — "Conoce tu enfoque" / "Explora tu armonía"> |

### BOFU (conversión)

| Componente | Decisión |
|---|---|
| Mensaje | <directo pero elegante> |
| Imagen | <más cercana, puede mostrar consultorio/doctora> |
| CTA | "Agenda tu evaluación" |

---

## Destinos y atribución

| Destino | URL | Shortcode tracking |
|---|---|---|
| Landing | https://campanas.livskin.site/<slug>/ | n/a (UTM automático) |
| WhatsApp directo | wa.me/<num>?text=<msg-con-shortcode> | `[<COD>-<MES>-<PLATAFORMA>]` |
| Site genérico | https://livskin.site/?utm_... | n/a |

---

## Activos a producir

- [ ] Landing principal (path: `infra/landing-pages/<slug>/`)
- [ ] Landings secundarias si aplica
- [ ] Ads creatives (path: `creatives/` dentro de la campaña)
  - [ ] Ad TOFU x N
  - [ ] Ad MOFU x N (si aplica)
  - [ ] Ad BOFU x N
- [ ] Tracking sheet para doctora (template en `docs/campaigns/_shared/tracking-sheet-template.md` o local)
- [ ] Cheat sheet shortcodes

---

## Hipótesis a validar

> Qué queremos APRENDER de esta campaña (no solo qué queremos vender).

| Hipótesis | Cómo se mide | Decisión que informa |
|---|---|---|
| <hipótesis 1> | <métrica> | <qué se cambia post-mortem> |
| <hipótesis 2> | <métrica> | <qué se cambia> |

---

## Restricciones operativas

- Plugin notas + foto de doctora aprobada: [ ] Sí / [ ] No
- Compliance Meta health category verificado: [ ] Sí / [ ] No
- Privacy policy + terms updated: [ ] Sí / [ ] No
- Pixel + CAPI verificados con flujo end-to-end: [ ] Sí / [ ] No
- Brand voice de la doctora alineado con copy: [ ] Sí / [ ] Pendiente

---

## Aprendizajes para doctrina (modo BOOTSTRAP — completar durante)

> Solo aplica mientras estamos en modo bootstrap (principio #13). Al ascender a v1.0 esta sección desaparece del template.

| Insight | Archivo doctrina afectado | Promovido a v0.X | Commit |
|---|---|---|---|
| <ej: "el rosa hot pink se ve barato en mobile, ajustar a más desaturado"> | design-principles.md | sí/no | <hash> |

---

## Post-mortem (completar al cerrar)

### Qué funcionó
- [a llenar]

### Qué no funcionó
- [a llenar]

### Métricas finales

| Métrica | Esperada | Real |
|---|---|---|
| Impresiones | | |
| CTR | | |
| Leads landing | | |
| Leads WA | | |
| Costo por lead | | |
| Conversion lead → cliente | | |

### Decisiones para próxima campaña
- [a llenar]

---

## Changelog del template

- **v0.1** (2026-05-04): destilado de Guidelines + estructura derivada del checklist 4 preguntas.
