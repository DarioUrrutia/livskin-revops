---
runbook: arranque-sesion
severity: high
auto_executable: false
trigger:
  - "Inicio de cualquier sesión nueva con Claude Code en este repo"
  - "Reanudar sesión tras pausa larga (>1h o cambio de máquina)"
required_secrets: []
commands_diagnose:
  - "git log --oneline -10"
  - "git status --short"
related_skills:
  - livskin-ops
related_memories:
  - feedback_session_warmup_obligatorio.md (memoria 🔥 CRÍTICA)
  - feedback_must_re_read_adrs_before_coding.md
  - preflight-cross-system.md (runbook)
---

# 🚦 Runbook — Arranque estandarizado de sesión

> **Propósito:** convertir el ritual de arranque en hard guard determinístico, no soft. Resuelve el meta-bug de la sesión 2026-05-05 (7 falsos positivos por inspeccionar infra sin leer system-map).
>
> **Cuándo se ejecuta:** **TODA sesión nueva** antes de procesar cualquier tarea no-trivial. Sin excepciones.
>
> **Cuánto tarda:** 5-7 min según volumen de cambios desde la última sesión.

---

## Filosofía

El sistema Livskin invirtió deliberadamente en herramientas anti-alucinación (system-map autoritativo, brain pgvector, runbook preflight, memorias 🔥 CRÍTICAS, MEMORY.md como index). Esas herramientas funcionan **solo si se usan al inicio**. Saltarlas = inventar `datos.livskin.site`, contar leads sin filtrar, marcar críticos a falsos positivos.

Memoria 🔥 CRÍTICA `feedback_session_warmup_obligatorio.md` codifica el principio. Este runbook lo ejecuta paso a paso.

---

## Protocolo paso a paso

### Paso 1 — Verificar estado git + filesystem (~30s)

```bash
git log --oneline -10
git status --short
```

**Lo que extraes:**
- ¿Qué se commiteó en la sesión anterior? (último 1-3 commits)
- ¿Working tree clean o hay drift?
- ¿Branch local sincronizada con `origin/main`?
- ¿Hay archivos huérfanos sin commit?

**Si NO está clean** → entender por qué antes de proceder. NO hacer commit ni revertir sin OK explícito de Dario (memoria `feedback_commit_approval_explicit.md`).

### Paso 2 — Lectura del system-map autoritativo (~3 min)

Leer mínimo de `docs/sistema-mapa.md`:
- **§1** — Inventario VPS (alias, IPs, hostnames, recursos)
- **§2** — Catálogo containers (qué corre dónde, dependencias)
- **§6** — URLs públicas (los hostnames REALES, no inventados)

**Reglas duras post-lectura:**
- NO citar hostname/path/IP/container que no aparezca en system-map
- Si el sistema cambió desde la última versión del system-map → el system-map gana hasta que se actualice formal

**Si la tarea va a tocar §3 (cross-VPS connections), §4 (matriz dependencias), §7 (backups), §8 (secretos)** → leer también esas secciones.

### Paso 3 — Lectura del MEMORY.md index (~2 min)

Leer `~/.claude/projects/c--Users-daizu-Claude-Code-Union-VPS---Maestro---Livskin/memory/MEMORY.md` completo.

**Identificar y procesar:**

1. **🔥 CRÍTICAS aplicables** — releer literal las del bloque "Doctrina rectora" siempre. Las del bloque "Arquitectura del flujo de datos" si la tarea es cross-system.

2. **🔔 Episodios efímeros** — ¿hay `project_session_handoff_*` con plan acordado de sesión previa? Si sí, **leer literal y aplicar**. Es el "te recuerdo al iniciar" que el usuario pidió.

3. **🚦 Gobernanza aplicable**:
   - `feedback_commit_approval_explicit` — cada commit individual requiere "OK"
   - `feedback_session_close_user_decision` — NO proponer cierre, usuario decide
   - `feedback_no_paid_services` — preguntar antes de costos
   - `feedback_production_preservation` — Render + Sheets intocables

### Paso 4 — Identificar modo de la sesión (#12 + #13)

Pregunta clave: **¿qué va a tocar la tarea?**

```
¿Toca docs/master-plan, ADRs, memorias críticas, infra core, brand/?
   → Modo PROYECTO

¿Toca docs/campaigns/<actual>/, infra/landing-pages/<slug>/, ad-creatives/?
   → Modo CAMPAÑA (brand SOLO LECTURA)

¿Ambos?
   → DIVIDIR en bloques explícitos con commit de barrera entre ellos
   (ver runbook sesion-modo-proyecto-vs-campana.md)

¿Bootstrap (#13) activo? — sí, hasta post-mortem 1ª campaña ~2026-05-12/13
   → Permite Bloque BOOTSTRAP-feedback al final de sesión campaña
```

**Si el usuario aún NO declaró modo** → preguntar antes de tocar nada. Sin modo declarado → la sesión deriva (memoria `principio operativo #12`).

### Paso 5 — Si la tarea es cross-system (≥2 sistemas) → preflight

Sistemas: WordPress · Vtiger · ERP Postgres · n8n · Brain pgvector · Metabase · WhatsApp Cloud API · GTM · Meta · Google.

Si lista ≥2 → **aplicar `runbook/preflight-cross-system.md` antes de codear**:
- Identificar sistemas (lista explícita)
- Query semántica al brain (`bash infra/scripts/brain-query.sh "..."`)
- Citar ADRs + memorias específicas en el plan inicial
- Esperar OK del usuario al plan citado antes de tocar código

**Si NO se aplica** → riesgo del 2026-04-29 mini-bloque 3.3 reescrito (4h perdidas) o del 2026-05-05 audit con falsos positivos (sesión completa quemada).

---

## Hard guard — qué hacer si falló el warmup

Si me doy cuenta a mitad de tarea que salté el warmup:

1. **STOP**. No procesar más la tarea actual.
2. Reportar al usuario:
   > "Detecté que arranqué sin warmup. Voy a aplicar los pasos 1-5 antes de continuar."
3. Ejecutar warmup en orden.
4. Recién después abordar la tarea.

**NUNCA** racionalizar "ya estoy avanzado, sigo y veré". Eso es exactamente cómo se generaron los 7 falsos positivos del 2026-05-05.

---

## Cuándo NO ejecutar el warmup completo

Excepciones acotadas:

| Caso | Pasos requeridos |
|---|---|
| Tarea conversacional ("¿qué es X?") sin tocar sistema | Solo paso 3 (MEMORY.md) si requiere contexto del proyecto |
| Cierre de sesión inmediato sin trabajo nuevo | Solo paso 1 (git status) para session log |
| Continuación de turno previo en la misma sesión activa | No re-ejecutar, pero los pasos siguen vigentes desde el primer turno |
| Bug fix trivial (typo, comentario) | Solo pasos 1 + 4 (modo) |

---

## Output esperado pre-tarea

Antes de la primera acción no-trivial, presentar al usuario:

```markdown
## Warmup completo

**Estado git**: branch <main|otro> @ <commit-corto> · working tree <clean|dirty>
**Sistema**: <hallazgos relevantes del system-map para esta tarea>
**Memorias aplicables**: <lista de 🔥 CRÍTICAS + episodios efímeros relevantes>
**Modo declarado**: <PROYECTO|CAMPAÑA|BOOTSTRAP>
**Sistemas a tocar**: <lista> (preflight cross-system: <sí|no aplica>)

**Plan propuesto**:
1. ...
2. ...

¿Apruebas?
```

Solo si Dario aprueba → arranco a codear/modificar.

---

## Endurecimiento técnico (Bloque B 2026-05-06)

Este runbook es la **codificación** del protocolo. El **enforcement** viene del hook `UserPromptSubmit` configurado en `.claude/settings.json`:

```
Hook detecta:
- ¿En este session se invocó Read sobre system-map.md? — telemetría tool-use
- ¿En este session se invocó Read sobre MEMORY.md?
- ¿La tarea actual es no-trivial? (heurística: tools edit/write, comandos bash que tocan VPS, decisiones cross-system)

Si NO leyó system-map/MEMORY + tarea no-trivial → inserta system-reminder bloqueante
```

Sin el hook, este runbook es soft (depende de mi disciplina). Con el hook, es hard guard real.

---

## Cross-link

- Memoria 🔥 CRÍTICA: `feedback_session_warmup_obligatorio.md` (la doctrina)
- Hook técnico: `.claude/settings.json` `UserPromptSubmit` (Bloque B paso 4)
- Runbook complementario al inicio: `preflight-cross-system.md` (cuando ≥2 sistemas)
- Runbook complementario al cierre: `cierre-sesion.md`
- Modos sesión: `sesion-modo-proyecto-vs-campana.md`
- Falla precedente que motivó esto: sesión 2026-05-05 movimiento 2

---

## Changelog

- **v1.0** (2026-05-06): runbook creado en Bloque B endurecimiento de proceso. Tras falla 2026-05-05 con 7 falsos positivos al inspeccionar sin warmup.
