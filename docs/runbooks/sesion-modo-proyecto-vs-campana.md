---
runbook: sesion-modo-proyecto-vs-campana
version: 1.0
last_updated: 2026-05-04
authoritative: true
applies_to: cualquier sesión de trabajo (humana o futuro Brand Orchestrator)
references:
  - principle: 12 (modo declarado)
  - principle: 13 (modo bootstrap)
  - doctrine: docs/brand/
---

# 🚦 Runbook — Modo de trabajo declarado por sesión

**Por qué este runbook existe:** las sesiones largas mezclan tactical de campaña con doctrina durable por defecto. Sin disciplina de modo, las decisiones efímeras contaminan memorias críticas y los aprendizajes durables no quedan capturados.

**Quién lo usa:** Claude Code en cada sesión. Futuro Brand Orchestrator hereda esta disciplina.

---

## Los 3 modos

### 🟢 Modo PROYECTO

**Qué toca:**
- ✅ `CLAUDE.md`
- ✅ `docs/master-plan-mvp-livskin.md`
- ✅ `docs/decisiones/` (ADRs)
- ✅ `docs/audits/`
- ✅ `docs/runbooks/`
- ✅ `docs/sesiones/` (session log)
- ✅ `docs/brand/` (modificación de doctrina — solo en modo proyecto)
- ✅ Memorias 🔥 CRÍTICAS en `~/.claude/projects/.../memory/`
- ✅ Infra core: `infra/docker/`, `infra/n8n/workflows/`, `infra/scripts/`

**Qué NO toca:**
- ❌ `docs/campaigns/<actual>/` (excepto leer brief / post-mortem)
- ❌ `infra/landing-pages/<slug>/` (excepto bug crítico operativo)
- ❌ `infra/ad-creatives/<actual>/`

**Pre-flight:**
1. Releer memorias 🔥 CRÍTICAS aplicables
2. Releer ADRs relevantes (memoria `feedback_must_re_read_adrs_before_coding`)
3. Citar referencias en plan inicial

**Cierre:**
- Session log en `docs/sesiones/YYYY-MM-DD-<slug>.md`
- Update memorias críticas si hay aprendizajes durables
- Commit prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, etc. (estándar)

### 🟡 Modo CAMPAÑA

**Qué toca:**
- ✅ `docs/campaigns/<actual>/` (escritura libre)
- ✅ `infra/landing-pages/<slug>/` (escritura libre)
- ✅ `infra/ad-creatives/<actual>/` (escritura libre)
- ✅ `docs/brand/` (SOLO LECTURA)
- ✅ `_pending-uploads/` (lectura para procesar fotos)

**Qué NO toca:**
- ❌ `CLAUDE.md`
- ❌ `master-plan-mvp-livskin.md`
- ❌ ADRs (cambios o creaciones)
- ❌ Memorias 🔥 CRÍTICAS
- ❌ Infra core (`infra/docker/`, `infra/n8n/workflows/` core)
- ❌ `docs/brand/` (modificación — está prohibido aquí, va a modo PROYECTO o BOOTSTRAP-feedback)

**Pre-flight:**
1. Lectura obligatoria de `docs/brand/brand-system.md`
2. Lectura del archivo principle relevante a la tarea (`copy-principles.md` para texto, `design-principles.md` para layout, `image-guidelines.md` para fotos)
3. Llenar `docs/campaigns/<actual>/brief.md` ANTES de tocar cualquier asset (gate de aprobación)
4. Las 4 preguntas del checklist deben estar respondidas

**Durante la sesión:**
- Cada output debe pasar el checklist de 4 preguntas (`brand-system.md` § 6)
- Si emerge insight "esto debería refinar la doctrina":
  - **Modo bootstrap activo (principio #13):** anotar en `docs/campaigns/<actual>/_doctrine-feedback.md`. Procesar en bloque BOOTSTRAP-feedback al final.
  - **Modo bootstrap cerrado:** anotar en `_overflow-for-project-mode.md`. Procesar en sesión PROYECTO separada.

**Cierre:**
- Post-mortem en `docs/campaigns/<actual>/post-mortem.md` (si la campaña terminó)
- Commit prefix obligatorio: `feat(campaign):`, `fix(campaign):`, `docs(campaign):`
- NO toca master plan, NO modifica ADRs, NO crea memorias 🔥 CRÍTICAS

### 🟠 Modo BOOTSTRAP — régimen único transitorio

**Cuándo aplica:** desde el 2026-05-04 hasta el cierre del post-mortem de la primera campaña paga (estimado 2026-05-12/13). **Es modo único, no se repite.**

**Qué permite que los otros modos NO permiten:**
- Feedback bidireccional explícito doctrina ↔ campaña
- Bloque dedicado al final de cada sesión campaña para procesar refinamientos a doctrina
- Doctrina vive en estado borrador versionado (`v0.1, v0.2,...`)

**Reglas duras:**
1. Doctrina en `docs/brand/` está marcada `BORRADOR` con header explícito
2. Refinamientos a doctrina por aprendizaje de campaña requieren:
   - Anotación previa en `docs/campaigns/<actual>/_doctrine-feedback.md`
   - Procesamiento en **bloque BOOTSTRAP-feedback** dedicado al final de la sesión
   - Commit separado con prefix `docs(brand):` y comentario explícito del insight original
3. Memorias 🔥 CRÍTICAS de marca NO se crean durante bootstrap. Se crean al cierre.
4. Cada sesión durante bootstrap declara cuáles son sus bloques (A/B/C como mínimo si toca ambos modos)

**Cierre formal del bootstrap:**

Trigger: post-mortem completo de la primera campaña paga.

Acciones al cerrar:
1. Decisión consciente de Dario: *"doctrina ya validada con data, ascenso a v1.0"*
2. Eliminar header `BORRADOR` de cada archivo `docs/brand/`
3. Bumpear versión `v0.X → v1.0` en frontmatter de cada archivo
4. Crear memorias 🔥 CRÍTICAS de marca:
   - `project_brand_methodology_v1.md` — referencia autoritativa al brand-system
   - `feedback_brand_voice_consolidated.md` (si aplica) — tone of voice cerrado
5. Update CLAUDE.md: principio #13 marca el bootstrap como cerrado, mover su descripción a "histórico"
6. Commit: `docs(brand): cierre bootstrap — doctrina ascendida a v1.0 post-mortem campaña <slug>`

**A partir del cierre:** modos PROYECTO/CAMPAÑA son separados estrictos. Sin excepciones. Si una sesión necesita feedback bidireccional, requiere división explícita en bloques con commits separados (sin ser bootstrap — el bootstrap fue único).

---

## Workflow de sesión por modo

### Sesión modo PROYECTO

```
┌─────────────────────────────────────────────────┐
│ 1. Declaración inicial                          │
│    "Esta sesión es modo PROYECTO: <objetivo>"   │
├─────────────────────────────────────────────────┤
│ 2. Pre-flight                                   │
│    - Memorias 🔥 CRÍTICAS aplicables           │
│    - ADRs relevantes citados                    │
│    - Plan presentado para aprobación            │
├─────────────────────────────────────────────────┤
│ 3. Ejecución                                    │
│    - Toca solo zonas durables                   │
│    - NO toca docs/campaigns/<actual>/           │
├─────────────────────────────────────────────────┤
│ 4. Cierre                                       │
│    - Session log                                │
│    - Memorias actualizadas si aplica            │
│    - Commit + push                              │
└─────────────────────────────────────────────────┘
```

### Sesión modo CAMPAÑA

```
┌─────────────────────────────────────────────────┐
│ 1. Declaración inicial                          │
│    "Esta sesión es modo CAMPAÑA: <slug>"        │
├─────────────────────────────────────────────────┤
│ 2. Pre-flight                                   │
│    - Lectura obligatoria docs/brand/            │
│    - Brief llenado o existente                  │
│    - Checklist 4 preguntas verificado           │
├─────────────────────────────────────────────────┤
│ 3. Ejecución                                    │
│    - Toca solo docs/campaigns/<actual>/         │
│    - + infra/landing-pages/<slug>/              │
│    - + infra/ad-creatives/<actual>/             │
│    - Cada output pasa checklist 4 preguntas     │
├─────────────────────────────────────────────────┤
│ 4. Cierre                                       │
│    - Post-mortem si campaña cerró               │
│    - Commit prefix: feat(campaign):             │
│    - NO toca durables                           │
└─────────────────────────────────────────────────┘
```

### Sesión modo BOOTSTRAP (mientras aplica)

```
┌─────────────────────────────────────────────────┐
│ Bloque A — modo PROYECTO                        │
│   (si la sesión necesita modificar doctrina)    │
│   Commit + push como barrera                    │
├─────────────────────────────────────────────────┤
│ Bloque B — modo CAMPAÑA                         │
│   Trabajo de campaña aplicando doctrina v0.X    │
│   Insights → _doctrine-feedback.md              │
│   Commit + push                                 │
├─────────────────────────────────────────────────┤
│ Bloque C — BOOTSTRAP-feedback                   │
│   Procesar _doctrine-feedback.md                │
│   Promover insights califican a doctrina v0.X+1 │
│   Commit + push                                 │
└─────────────────────────────────────────────────┘
```

---

## Anti-patrones (qué nunca hacer)

| ❌ Anti-patrón | Por qué rompe |
|---|---|
| Sesión sin modo declarado | Deriva, contamina contextos |
| Modo CAMPAÑA modifica master plan | Decisiones efímeras ascienden a doctrina del proyecto |
| Modo CAMPAÑA crea memorias 🔥 CRÍTICAS | Memorias críticas son durables — no nacen de tactical |
| Modo PROYECTO modifica landings live de campaña activa | Riesgo operativo durante campaña corriendo |
| Cambio de modo sin commit de barrera | Pierde el checkpoint, mezcla bloques |
| Modo BOOTSTRAP extendido más allá de post-mortem | Bootstrap es único — extenderlo es soft mode permanente |

---

## Cómo identificar el modo correcto al iniciar

```
¿La sesión va a tocar...?
├─ master plan, ADRs, memorias críticas, infra core ──→ MODO PROYECTO
├─ landing de campaña activa, ads, brief de campaña ──→ MODO CAMPAÑA
├─ docs/brand/ — modificar ────────────────────────────→ MODO PROYECTO
├─ docs/brand/ — solo leer ────────────────────────────→ cualquier modo
└─ ambos zonas ────────────────────────────────────────→ DIVIDIR EN BLOQUES con barrera explícita

¿Estamos en bootstrap (principio #13 activo)?
└─ sí → permite Bloque BOOTSTRAP-feedback al final
    no → división estricta, insights van a _overflow-for-project-mode.md
```

---

## Cross-link

- Principio operativo **#12** en CLAUDE.md
- Principio operativo **#13** en CLAUDE.md
- Doctrina de marca: `docs/brand/`
- Memoria sugerida (post-bootstrap): `feedback_session_mode_declared.md` (NO crear todavía si estamos en bootstrap)

---

## Changelog

- **v1.0** (2026-05-04): runbook creado al activar modos declarados + bootstrap.
