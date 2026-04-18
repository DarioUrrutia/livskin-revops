# notes/

Carpeta para notas personales y colaborativas del proyecto Livskin. Pensada para usar con Obsidian.

## Subcarpetas

### `compartido/`
**Versionado en git** (visible en GitHub).

Notas colaborativas entre Dario y Claude Code. Ejemplos:
- Drafts de documentos antes de pasarlos a `docs/decisiones/`
- Brainstorms estructurados que vale la pena preservar
- Outlines de features antes de escribir ADR formal
- Insights de sesiones que no entran en session log

### `privado/`
**Gitignored** (no se sube a GitHub).

Espacio personal de Dario. Para:
- Pensamientos libres, preocupaciones, dudas
- Ideas a medio cocinar
- Referencias externas personales
- Notas que no están listas para compartir

Este espacio **NO se sincroniza entre máquinas** (por diseño — cada laptop tiene sus notas privadas).

## Uso con Obsidian

1. Abre Obsidian
2. "Open folder as vault" → selecciona la raíz del proyecto (`Union VPS - Maestro - Livskin/`)
3. Todos los `.md` del repo + estas carpetas aparecen en el grafo
4. Backlinks `[[path/archivo]]` funcionan automáticamente
5. Búsqueda full-text cubre todo

## Integración con segundo cerebro

- `notes/compartido/` se indexa semanalmente en Layer 2 del cerebro (project_knowledge) junto con el resto del repo
- `notes/privado/` **NO** se indexa (es privado, queda local)

Ver [ADR-0001 sección 9.2](../docs/decisiones/0001-segundo-cerebro-filosofia-y-alcance.md) para la arquitectura completa.

## Plantilla para nota nueva

```markdown
---
title: <Título>
tags: [idea, brainstorm, duda, referencia]
created: YYYY-MM-DD
status: draft | review | integrated
---

# <Título>

## Contexto

## Contenido

## Próximos pasos
```

Si quieres automatizar esto, el plugin **Templater** de Obsidian (gratis) permite crear notas nuevas con un atajo de teclado aplicando esta plantilla.
