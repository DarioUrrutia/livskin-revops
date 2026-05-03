---
type: brand-doctrine-index
version: 0.1
status: BORRADOR — sujeto a refinamiento por aprendizajes de la primera campaña
ascends_to_v1: post-mortem campaña 2026-05-dia-madre (estimado 2026-05-12/13)
authoritative_when: v1.0 firmada
---

# 🎨 Doctrina de Marca Livskin — Sistema de creación de contenido

> **⚠️ ESTADO BORRADOR (v0.1)** — vivimos en **modo BOOTSTRAP** (principio operativo #13). Esta doctrina nació del documento de Guidelines pasado por Dario el 2026-05-04, y será **refinada con aprendizajes de la primera campaña paga (Día de la Madre 2026-05)** antes de ascender a v1.0 firmada. Hasta entonces, no es referencia inmutable.

---

## Filosofía final

**Livskin NO vende tratamientos. Livskin vende decisiones sobre identidad.**

El tratamiento NO es el protagonista. **La persona lo es.**

4 códigos rectores de toda comunicación:
- **Decisión** (no imposición)
- **Control** (de la persona sobre su rostro)
- **Naturalidad** (no exageración)
- **Seguridad** (criterio médico)

---

## Estructura de la doctrina (5 archivos)

| Archivo | Propósito | Consume quién |
|---|---|---|
| [brand-system.md](brand-system.md) | Base teórica + funnel TOFU/MOFU/BOFU + filosofía + checklist 4 preguntas | Brand Orchestrator (system prompt) + cualquier sesión modo CAMPAÑA |
| [copy-principles.md](copy-principles.md) | 4 principios de copy + glosario palabras permitidas/prohibidas | Subagente Copywriter futuro |
| [design-principles.md](design-principles.md) | Espacio + jerarquía + color + tipografía | Subagente Visual futuro + landings |
| [image-guidelines.md](image-guidelines.md) | Qué SÍ y qué NO en fotos + convención de upload + naming | Subagente Visual + Dario al subir fotos |
| [campaign-brief-template.md](campaign-brief-template.md) | Plantilla a llenar al inicio de cada campaña (las 4 preguntas) | Brand Orchestrator + cada sesión nueva campaña |

---

## Cómo se usa

### Modo CAMPAÑA (sesiones humanas o futuras del agente)

1. Pre-flight: lectura obligatoria de `brand-system.md` + el archivo principle relevante a la tarea
2. Llenar `campaign-brief-template.md` ANTES de tocar cualquier asset (gate de aprobación)
3. Cada output (ad, landing, banner) debe pasar el **checklist de 4 preguntas** del brand-system
4. Modificaciones a esta doctrina están **prohibidas en modo campaña** (excepto en bloque BOOTSTRAP-feedback explícito hasta cierre del bootstrap)

### Modo PROYECTO (sesiones de evolución de doctrina)

1. Solo en sesiones declaradas modo PROYECTO se modifican estos archivos
2. Cambios de doctrina ascienden versión: `v0.1 → v0.2 → v0.3 → v1.0` al cierre del bootstrap
3. Cada bump de versión registra qué insight lo causó (commit message + changelog interno)

### Brand Orchestrator futuro (Fase 4B)

El system prompt del agente referencia esta carpeta como ground truth:

```
Eres el Director Creativo de Livskin. Tu doctrina vive en docs/brand/.
Lectura obligatoria como primer step de cada task: brand-system.md.
Cada output debe pasar el checklist de 4 preguntas antes de presentarse a Dario.
NUNCA publica sin OK explícito de Dario (memoria feedback_agent_governance punto 3).
```

---

## Versión y trazabilidad

- **v0.1** (2026-05-04, BORRADOR): destilado desde el documento Guidelines de Dario + estructurado en 5 archivos modulares.
- **v0.2+** (a venir): refinamientos por aprendizajes de campaña Día de la Madre.
- **v1.0** (estimado 2026-05-12/13): firmada al cierre del modo bootstrap, post-post-mortem.

---

## Referencias cruzadas

- Principio operativo **#11** (deterministic backbone first) — la doctrina existe sin agente IA
- Principio operativo **#12** (modo declarado) — esta doctrina solo se modifica en modo PROYECTO
- Principio operativo **#13** (modo bootstrap) — régimen actual permite feedback bidireccional con disciplina
- Audit `docs/audits/agent-scope-audit-2026-05-03.md` — Brand Orchestrator es el único agente IA real V1
- Memoria `feedback_deterministic_backbone_first.md` — IA es capa aditiva, esta doctrina es la base
