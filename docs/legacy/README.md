# `docs/legacy/` — Archivos histórico-pero-no-borrar

Documentos de fases tempranas o pre-roadmap que se conservan por valor histórico/auditoría pero **no son referencia operativa actual**.

## ⚠️ Para Claude Code y futuras sesiones

**NO leer estos docs como fuente autoritativa.** La info que sigue siendo válida está consolidada en:
- `CLAUDE.md` — contexto vivo
- `docs/master-plan-mvp-livskin.md` — plan autoritativo
- `docs/decisiones/` — ADRs físicas (20 reales al 2026-05-03)
- Memorias 🔥 CRÍTICAS en el `.claude/memory/` del proyecto

Si necesitás citar uno de estos docs, **acompañar con disclaimer** "(legacy, ver X para versión actual)".

---

## Contenido y razón de archivado

| Archivo | Razón de archivado | Fecha movido |
|---|---|---|
| `fase-2-reverse-proxy-n8n.md` | Doc de "FASE 2" del proyecto VIEJO (pre-roadmap 10 semanas). Confunde namespace con Fase 2 del roadmap actual (ERP refactor) | 2026-05-03 |
| `fase-3-tls-vtiger.md` | Idem — "FASE 3" legacy (TLS + Vtiger setup) vs Fase 3 actual (Tracking + atribución) | 2026-05-03 |
| `consultas-y-decisiones.md` | Dump de la primera sesión 2026-04-16. Info ya consolidada en master plan + memorias | 2026-05-03 |
| `erp-flask-original-deep-analysis.md` | Análisis profundo del Flask original (pre-refactor). Info ya en ADRs 0023-0027 + sesión `2026-04-26-fase2-implementacion-completa.md` | 2026-05-03 |

---

## Política

- **No editar** estos archivos (son snapshots históricos)
- **No borrar** sin discusión explícita (valor de auditoría retroactiva)
- Si un doc nuevo vuelve a `docs/` raíz por error de organización, considerar moverlo aquí o reorganizarlo apropiadamente

---

**Mantenido por:** auditoría integral 2026-05-03
