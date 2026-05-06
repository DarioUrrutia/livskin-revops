#!/bin/bash
# warmup-check.sh — UserPromptSubmit hook para Claude Code.
#
# Verifica si en el session actual se ha invocado tool Read sobre:
#   - docs/sistema-mapa.md (autoritativo machine-readable)
#   - MEMORY.md (index de memorias persistentes)
#
# Si NO se ha leído NINGUNO de los dos en el session → inyecta system-reminder
# bloqueante recordando el warmup obligatorio (memoria 🔥
# feedback_session_warmup_obligatorio.md + runbook arranque-sesion.md).
#
# Si ya leyó al menos uno → output silencioso (exit 0 sin stdout).
#
# Caso especial: primer turno del session (transcript no existe o vacío) →
# permitir sin bloquear. El reminder dispara en el segundo prompt si todavía
# no leyó.
#
# Comportamiento del hook:
#   - exit 0 sin stdout    → harness procesa el prompt normal
#   - exit 0 con JSON      → harness inyecta systemMessage al contexto Claude
#                            si "continue": false → Claude debe parar y atender
#
# Performance target: <200ms (grep + minimal JSON output, sin jq parsing complejo).

set -e

# Leer stdin del hook (Claude Code pipea JSON con info del session)
HOOK_INPUT=$(cat)

# Extraer transcript_path con grep robusto (no requiere jq instalado)
# Pattern: "transcript_path":"/path/to/file.jsonl"
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" \
  | grep -oE '"transcript_path"[[:space:]]*:[[:space:]]*"[^"]+"' \
  | head -1 \
  | sed -E 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')

# Caso 1: no se pudo parsear transcript_path → no bloquear (fail-open)
if [ -z "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

# Caso 2: transcript no existe (primer turno del session) → no bloquear
if [ ! -f "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

# Buscar evidencia de Read sobre los 2 archivos críticos.
# Tool use de Read en transcript JSONL típicamente luce como:
#   {"type":"tool_use","name":"Read","input":{"file_path":"/.../sistema-mapa.md"},...}
# Buscamos cualquier mención de los nombres de archivo (robustos a paths
# absolutos vs relativos, slashes vs backslashes).
FOUND_SYSMAP=$(grep -cE '"file_path"[^"]*"[^"]*sistema-mapa\.md"' "$TRANSCRIPT_PATH" 2>/dev/null) || FOUND_SYSMAP=0
FOUND_MEMORY=$(grep -cE '"file_path"[^"]*"[^"]*MEMORY\.md"' "$TRANSCRIPT_PATH" 2>/dev/null) || FOUND_MEMORY=0

# Caso 3: leyó al menos uno → silent (warmup OK)
if [ "$FOUND_SYSMAP" -gt 0 ] || [ "$FOUND_MEMORY" -gt 0 ]; then
  exit 0
fi

# Caso 4: NO leyó ninguno → inyectar system-reminder bloqueante
# El JSON output con systemMessage + continue:false hace que el harness pare
# y le inyecte el mensaje a Claude antes de procesar el prompt.
cat <<'EOF'
{
  "systemMessage": "⚠️ WARMUP OBLIGATORIO no completado.\n\nEste proyecto tiene herramientas anti-alucinación (system-map autoritativo + MEMORY.md index). Saltarse el warmup = repetir errores como los del 2026-05-05 (7 falsos positivos al inspeccionar infra sin leer system-map primero).\n\nAntes de procesar tareas no-triviales, ejecuta el warmup de 5 pasos:\n\n1. Lee `docs/sistema-mapa.md` §1 + §2 + §6 (VPS, containers, URLs públicas)\n2. Lee `MEMORY.md` index + memorias 🔥 CRÍTICAS aplicables (especialmente episodios efímeros tipo `project_session_handoff_*` con plan acordado)\n3. `git log --oneline -10` + `git status --short`\n4. Identifica modo (#12: PROYECTO/CAMPAÑA/BOOTSTRAP)\n5. Si la tarea va a tocar ≥2 sistemas (WP/Vtiger/ERP/n8n/Brain/Metabase/WA/GTM/Meta/Google) → aplica `docs/runbooks/preflight-cross-system.md`\n\nDoctrina rectora: `feedback_session_warmup_obligatorio.md` + `docs/runbooks/arranque-sesion.md`.\n\nSi la tarea es trivial (conversacional, bug fix typo, cierre rápido) → puedes proceder explicándolo al usuario brevemente. En ese caso este recordatorio no aplica.",
  "continue": false
}
EOF
exit 0
