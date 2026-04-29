---
runbook: preflight-cross-system
severity: critical
auto_executable: true
trigger:
  - "Antes de empezar mini-bloque que toca ≥2 sistemas (WP/Vtiger/ERP/n8n/Brain/Metabase/WA/GTM/Meta/Google)"
  - "Antes de ejecutar Sub-paso 'a' (Plan + ADR) de cualquier mini-bloque"
required_secrets: []
commands_diagnose:
  - "bash /srv/livskin-revops/infra/scripts/brain-query.sh '<keyword>'"
commands_fix: []
commands_verify: []
escalation:
  if_fail: "Si el plan no cita ADRs/memorias específicas → PARAR, no codear, escribir mini-ADR primero"
related_skills:
  - livskin-ops
---

# Runbook — Pre-flight para mini-bloques cross-system

> **Propósito:** evitar repetir el error del 2026-04-29 (mini-bloque 3.3 inventado, 4 horas perdidas, commits revertidos) — implementar arquitectura sin antes verificar lo ya documentado.
>
> **Cuándo aplica:** TODA tarea/mini-bloque que toque ≥2 sistemas del stack:
> WordPress · Vtiger · ERP Postgres · n8n · Brain pgvector · Metabase · WhatsApp Cloud API · GTM · Meta · Google
>
> **Cuándo NO aplica:** bugfixes 1-sistema, refactors sin cambio de comportamiento, ajustes UI/copy, cambios solo en docs/memorias, tareas con plan citado ya aprobado en sesión actual.
>
> **Tiempo:** 5-10 minutos / ~5K tokens. ROI vs no aplicarlo: 30-50x.

---

## Origen del runbook

Sesión 2026-04-29 mini-bloque 3.3:
- Implementé Form → ERP `/api/leads/intake` directo, saltándome n8n y Vtiger
- Ignorando ADR-0011 v1.1, ADR-0015, memoria `project_acquisition_flow`, memoria `project_vtiger_erp_sot`
- Resultado: cleanup completo, revert de commits, sesión perdida

La memoria `feedback_surgical_precision_erp` (precisión quirúrgica al ampliar ERP) NO fue suficiente — solo cubría cambios al ERP, no flows cross-system completos. Este runbook llena ese gap.

---

## Protocolo (5 pasos)

### Paso 1 — Identificar sistemas involucrados

Listar EXPLÍCITAMENTE qué sistemas toca el mini-bloque. Si la lista incluye ≥2 sistemas → este runbook es obligatorio.

**Ejemplo (correcto) — Mini-bloque 3.3 form → leads:**
- WordPress (form 1569)
- n8n (orquestador)
- Vtiger (lead lifecycle)
- ERP (espejo `leads`)
- → 4 sistemas → **protocolo OBLIGATORIO**

**Ejemplo (no aplica) — Bugfix en cliente_service del ERP:**
- ERP solamente
- → 1 sistema → protocolo NO obligatorio (pero aplicar `feedback_surgical_precision_erp` sí)

### Paso 2 — Query semántica al brain pgvector

En vez de releer 5 ADRs completos, usar el brain como motor de búsqueda semántica. **El brain está re-indexado y vivo** (verificable: `livskin_brain.project_knowledge` tiene 1.765+ chunks).

**Comando:**
```bash
bash /srv/livskin-revops/infra/scripts/brain-query.sh "<keyword o pregunta>" [limit]
```

**Queries típicas (ejemplos):**
- `"flujo lead form vtiger n8n erp"` → devuelve flujo end-to-end
- `"source of truth lead vs cliente"` → SoT por dominio
- `"n8n workflows orquestador cross-system"` → mapping de workflows
- `"tracking event_id deduplicacion CAPI"` → dedup chain
- `"agenda module appointments erp"` → módulo agenda

**Output esperado:** top 5-10 chunks más relevantes (~2K tokens).

**Si el brain está stale o caído:** PARAR. Re-indexar primero (`bash /srv/livskin-revops/infra/scripts/brain-index.sh`). Tarda ~9 min.

### Paso 3 — Citar ADRs + memorias específicas en el plan inicial

NO empezar a implementar sin un plan que cite literalmente:
- "Según **ADR-XXXX** sección X, el flujo correcto es..."
- "Según memoria **`project_xyz.md`**, debo..."

Si no puedes citar una decisión documentada → **NO existe** en el sistema → escribir **mini-ADR** ANTES de codear.

### Paso 4 — Verificar contra las 5 memorias 🔥 CRÍTICAS

Antes de empezar, repasar mentalmente que el plan respeta:

1. **`project_vtiger_erp_sot.md`** — ¿qué sistema es SoT del dato que toco?
2. **`project_acquisition_flow.md`** — ¿el flujo que propongo coincide con el end-to-end documentado?
3. **`project_n8n_orchestration_layer.md`** — ¿n8n está en el medio de cualquier sync cross-system?
4. **`feedback_must_re_read_adrs_before_coding.md`** — ¿este protocolo se está aplicando?
5. **`feedback_surgical_precision_erp.md`** — ¿estoy aplicando los 8 pasos para cambios al ERP?

Si la respuesta a cualquiera es "no" → **PARAR** y replantear.

### Paso 5 — Plan citado pre-implementación

El plan que doy a Dario antes de empezar a codear DEBE incluir:
- ✅ Sistemas involucrados (lista explícita)
- ✅ ADRs citados (números + secciones)
- ✅ Memorias citadas (filenames)
- ✅ Si hay conflicto entre ADRs/memorias y mi propuesta: explicarlo explícitamente, no asumir

Solo si Dario aprueba el plan citado, empezar a codear.

---

## Anti-patrones que disparan este runbook

🚫 **"Recuerdo que esto va así"** sin verificar memoria/ADR específico
🚫 **"Lo voy haciendo y vemos"** en arquitectura cross-system
🚫 **"El otro día decidimos X"** sin citar el documento
🚫 **"Es obvio que debe ir así"** — la obviedad para Claude ≠ la decisión documentada
🚫 **Inventar nuevo flujo cuando ya hay uno cerrado en ADR**
🚫 **"El ADR es viejo, hagámoslo distinto"** sin escribir nuevo ADR que supersede

---

## Output esperado del pre-flight

Antes de tocar código, presentar a Dario:

```markdown
## Plan mini-bloque X.Y (preflight cross-system aplicado)

**Sistemas involucrados:** [lista]
**ADRs consultados:**
- ADR-XXXX sección Y → cita específica
- ADR-ZZZZ sección W → cita específica
**Memorias consultadas:**
- `project_xxx.md` → cita
- `feedback_yyy.md` → cita
**Brain queries ejecutadas:**
- `query "..."` → top 3 chunks relevantes resumidos

**Plan derivado (respeta arquitectura documentada):**
1. Step 1...
2. Step 2...

**Conflictos potenciales con docs:** [si hay] / "ninguno detectado"

¿Apruebas?
```

---

## Cuánto cuesta vs cuánto ahorra

| | Aplicar protocolo | NO aplicarlo (caso 2026-04-29) |
|---|---|---|
| **Tiempo** | 5-10 min preflight | 4 horas codear + 30 min cleanup |
| **Tokens** | ~5-10K extra | 0 extra... + 80K en commits revertidos |
| **Frustración Dario** | mínima | máxima |
| **Daño al stack** | 0 | "huevada completa" + 2 leads test + mu-plugin innecesario + commits invertidos |

ROI: **aplicar siempre que el flag de "cross-system" se prenda.**

---

## Cross-references

- Memoria 🔥 `feedback_must_re_read_adrs_before_coding.md` — versión memoria del mismo protocolo
- Memoria 🔥 `project_vtiger_erp_sot.md` — la decisión más violada hoy
- Memoria 🔥 `project_n8n_orchestration_layer.md` — la pieza que faltaba en mi modelo mental
- Memoria 🔥 `project_acquisition_flow.md` — flujo end-to-end documentado
- ADR-0011 v1.1 — modelo datos lead/cliente/venta + webhooks n8n
- ADR-0015 — source of truth por dominio
- Sesión 2026-04-29 session log — ejemplo concreto del error

---

**Última revisión:** 2026-04-29 (creación, post-error mini-bloque 3.3)
