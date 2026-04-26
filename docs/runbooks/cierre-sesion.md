---
runbook: cierre-sesion
severity: low
auto_executable: false
trigger:
  - "Dario dice 'cerrar sesion' o 'cierra el dia'"
  - "Fin de sesión de trabajo natural (sin más tareas pendientes)"
required_secrets: []
commands_diagnose: []
commands_fix: []
commands_verify:
  - "git status"
  - "git log --oneline -5"
escalation:
  if_fail: "Si git push falla, no abandonar — investigar (network, auth, conflicto). Nunca dejar trabajo sin commitear."
related_skills:
  - livskin-ops
---

# Runbook — Cierre de sesión estandarizado

> **Propósito:** convertir el cierre de día en un protocolo determinístico que ni Dario ni Claude tengan que re-pensar cada vez. Garantiza que **nada del trabajo se pierde**, que el **arranque de la próxima sesión es zero-friction**, y que la **memoria/segundo cerebro/repo** quedan coherentes entre sesiones.

> **Cuándo se ejecuta:** al final de cada sesión de trabajo, sea breve (15 min) o larga (varias horas), gatillado por Dario diciendo "cerrar sesión", "cierra el día", o por Claude proponiéndolo cuando detecta fin de tareas.

> **Cuánto tarda:** 5-15 min según volumen de cambios. Si la sesión fue solo de discusión sin código nuevo, puede ser 3 min. Si hubo decisiones arquitectónicas + código + ADRs, hasta 20 min.

---

## Filosofía

El cierre de sesión NO es paperwork. Es la operación que convierte trabajo individual en **organización persistente**. Cada cierre debe dejar al proyecto en un estado donde:

1. **Cualquier humano** (Dario, otro colaborador futuro) puede leer la última sesión y entender qué pasó.
2. **Cualquier instancia futura de Claude Code** puede arrancar con contexto completo sin re-explicarle nada.
3. **El árbol git** refleja el estado real del trabajo (nada en working directory sin commitear, nada perdido).
4. **El backlog** está actualizado: nuevos items capturados, completados movidos a "Hecho".
5. **La memoria persistente** captura los aprendizajes y decisiones nuevas (no solo qué se hizo, sino qué se decidió y por qué).

---

## Protocolo paso a paso

### 1. Estado inicial — Claude verifica
```bash
git status
git log --oneline -5
```
Si hay archivos sin trackear o cambios no commiteados, los identifica antes de proceder.

### 2. Session log — escribe la narrativa de hoy
**Archivo:** `docs/sesiones/YYYY-MM-DD-titulo-corto.md`

Estructura mínima:
- **Contexto inicial** — dónde quedamos en sesión anterior
- **Qué se hizo hoy** — narrativa, no bullet list, ordenada cronológicamente
- **Decisiones tomadas** — destacadas, con el "por qué"
- **Hallazgos relevantes** — lo que descubrimos (audits, mediciones, contradicciones)
- **Lo que queda pendiente** — bullets con próximo paso concreto
- **Próxima sesión propuesta** — UNA opción (per memoria `feedback_roadmap_order`), no múltiples

### 3. ADRs nuevos — si hubo decisiones arquitectónicas
Si en la sesión se tomó alguna decisión irreversible o de impacto cross-fase:
- Crear dossier en `docs/decisiones/00XX-titulo.md` usando `_template.md`
- Actualizar `docs/decisiones/README.md` (index)

### 4. CLAUDE.md — refresco de estado
Actualizar la sección **"📝 Estado al YYYY-MM-DD"** con:
- Nuevos sub-bloques completados / en progreso
- Cambios estructurales del proyecto (no detalles de implementación)
- Pendientes de la próxima sesión a alto nivel

NO duplicar información que vive en master plan o session log. CLAUDE.md es el **mapa rápido**, no el detalle.

### 5. Master plan — si cambió la trayectoria
Solo actualizar `docs/master-plan-mvp-livskin.md` si:
- Hubo cambio de fase (completada, retrasada, reordenada)
- Hubo decisión arquitectónica que afecta roadmap
- Apareció un nuevo bloque/sub-bloque que merece ser parte del plan

### 6. Backlog — captura y limpieza
Editar `docs/backlog.md`:
- **Agregar** items nuevos que surgieron en la sesión (ideas, dudas, mejoras detectadas pero no ejecutadas)
- **Mover a "Hecho"** items completados, con commit hash de referencia
- **Re-priorizar** si la sesión cambió importancia de algo (escalar 🟢→🟡 o viceversa)

### 7. Memoria persistente — solo si hubo aprendizajes
Path: `C:/Users/daizu/.claude/projects/c--Users-daizu-Claude-Code-Union-VPS---Maestro---Livskin/memory/`

**Crear nueva memoria** cuando se cumple AL MENOS UNA de estas condiciones:
- Apareció un **principio operativo** nuevo (feedback_*)
- Se cerró una **decisión estructural** sobre el proyecto (project_*)
- Se registró un **rasgo del usuario** relevante para futuras colaboraciones (user_*)
- Se mapeó una **referencia externa** que necesitamos recordar (reference_*)

**Actualizar memoria existente** cuando:
- Una decisión previa se refinó o cambió
- Un memoria se quedó incompleta y ahora hay datos para completarla

**Cada memoria nueva** se referencia en `MEMORY.md` (1 línea, ≤150 chars).

**NO crear memoria** para:
- Detalles de implementación (van en código + commits)
- Estado temporal (en master plan)
- Cosas que ya están documentadas en CLAUDE.md o ADRs

### 8. Capacidades de agentes — actualización viva
Si en la sesión se identificó:
- Una **nueva habilidad** que el 5to agente (Infra+Security) necesitará → actualizar `project_infra_security_agent.md`
- Una **nueva tarea/subagente** emergente para cualquier agente → actualizar `project_agent_org_design.md`
- Un **patrón de gobernanza** (procesos > IA, deterministic > LLM) → memoria `feedback_agent_governance.md`

Esto evita acumular deuda en el diseño organizacional. Cuando llegue la sesión estratégica de estructura de agentes (pre-Fase 5), todo está pre-mapeado.

### 9. Segundo cerebro — Obsidian / livskin_brain
- **Obsidian local**: el repo entero ES el vault. Los nuevos .md de hoy ya están indexados al guardar.
- **livskin_brain (Postgres+pgvector en VPS 3)**: por ahora schema vacío. **No re-indexar manualmente** — eso lo hará el agente Brand Orchestrator cuando arranque Fase 5. Si en sesión hubo conocimiento clínico nuevo (FAQs, tratamientos, precios), apuntar en `notes/compartido/conocimiento-clinica.md` para futura ingesta.

### 10. Git — commit y push
```bash
git status                                           # confirmar qué se va a commitear
git add <archivos específicos>                       # NO usar git add . o -A
git commit -m "$(cat <<'EOF'
docs: cierre sesión YYYY-MM-DD — <titulo>

<1-3 bullets de qué cambió>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push origin main
```

**Reglas duras:**
- NUNCA `git add -A` o `git add .` (riesgo de incluir secrets/binarios accidentalmente)
- NUNCA `git push --force` a main
- NUNCA `--no-verify` ni `--amend` salvo autorización explícita de Dario en el momento
- Si hay archivos en `keys/`, `backups/`, `erp/` en la lista — alerta y NO commitear

### 11. Verificación final
```bash
git status              # debe decir "nothing to commit, working tree clean"
git log --oneline -3    # nuevo commit visible arriba
```

Resumen final a Dario en una frase:
> "Sesión cerrada. Commit `<hash>`. Próxima sesión: `<próximo paso>`."

---

## Checklist abreviado (versión rápida)

```
[ ] git status verificado
[ ] Session log escrito en docs/sesiones/
[ ] ADRs nuevos (si aplica) en docs/decisiones/
[ ] CLAUDE.md refrescado (si hubo cambio de estado)
[ ] Master plan actualizado (si hubo cambio de trayectoria)
[ ] Backlog: nuevos items + mover completados
[ ] Memorias: nuevas/actualizadas + MEMORY.md
[ ] Capacidades agentes: infra_security_agent / agent_org_design (si aplica)
[ ] git add específico (NO -A) + commit + push origin main
[ ] git status limpio + 1-frase de cierre a Dario
```

---

## Cuándo NO ejecutar este runbook completo

- **Sesión de solo lectura/discusión sin cambios al repo**: skip pasos 2-7, hacer solo paso 11 (frase de cierre + propuesta de próxima sesión).
- **Trabajo a medio terminar que continúa mañana**: igual ejecutar 1-11, pero el session log debe decir "EN PROGRESO" y dejar TODO list explícito.
- **Cambios solo a `notes/privado/`**: gitignored, no requiere commit. Solo session log si hubo decisiones.

---

## Evolución del runbook

Este runbook DEBE evolucionar. Cada cierre de sesión que descubra fricción nueva (algo que faltó, algo que se duplicó, algo que se perdió) gatilla actualización del runbook mismo.

**Última revisión mayor:** 2026-04-26 (creación, post-sesión audit-real-arquitectura-tracking).
