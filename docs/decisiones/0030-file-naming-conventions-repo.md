# ADR-0030 — File naming conventions del repo

**Estado:** ✅ Aprobada
**Fecha:** 2026-04-29
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 3 (organización post-cleanup mini-bloque 3.3)
**Workstream:** Infra / Docs

---

## 1. Contexto

ADR-0014 codificó naming de **entidades de data** (`LIVCLIENT####`, UTMs, fuentes). Pero la **nomenclatura de archivos del repo** (docs, scripts, configs) **emergió orgánicamente sin codificación explícita** — es bastante consistente pero hay inconsistencias detectadas en audit del 2026-04-29:

- `docs/audits/` mezcla 3 patrones (algunos con prefijo `audit-`, otros con fecha al inicio, otros con `mini-bloque-`)
- 2 archivos legacy con espacios + typo: `Datos Livskin.xlsx`, `livskin_pensamientos para una implemetacion profesional...docx`
- 2 archivos canvas vacíos (`Senza nome*.canvas`) sin gitignore

Para evitar que sigan apareciendo inconsistencias y que un nuevo colaborador (humano o Claude futuro) sepa qué convención seguir, esta ADR codifica los patrones que ya existen **+ corrige las inconsistencias detectadas**.

Referencias:
- ADR-0014 (naming de entidades data — códigos LIVXXXX, UTMs)
- Audit 2026-04-29 `audit-organizacion-integridad-seguridad-2026-04-29.md`

---

## 2. Opciones consideradas

### Opción A — Codificar lo que ya emergió + corregir 4 inconsistencias detectadas
Documentar las convenciones actuales (kebab-case docs, snake_case Python, fecha-prefix sesiones, NNNN-prefix ADRs) + agregar reglas para casos no cubiertos (canvas, archivos data legacy).

### Opción B — Reescribir convenciones from scratch (más rigurosa)
Por ejemplo migrar TODO a snake_case, o TODO a kebab-case. Más limpio pero costoso (renombrar 100+ archivos + actualizar todas las referencias).

### Opción C — No codificar, mantener flexibilidad
Dejar la convención implícita. Riesgo: sigue habiendo inconsistencias futuras.

---

## 3. Análisis de tradeoffs

| Dimensión | A (codificar lo emergido) | B (reescribir from scratch) | C (no codificar) |
|---|---|---|---|
| Costo implementación | Bajo (~1 hora) | Alto (renombrar 100+ archivos) | Cero |
| Continuidad histórica | Alta (preserva nombres existentes) | Rompe links + brain index | Alta |
| Robustez futura | Alta (regla escrita) | Alta | Baja (sigue dependiendo de criterio) |
| Risk de romper algo | Bajo (solo 4 inconsistencias menores) | Alto (renombres masivos) | Cero |
| Onboarding nuevo colaborador | Claro | Claro | Confuso |

---

## 4. Recomendación

**Opción A** — codificar las convenciones emergidas + corregir solo lo necesario.

Razones:
1. Las convenciones actuales son **buenas** (consistentes en 90% de archivos)
2. Cambios masivos riesgan romper referencias en docs + brain pgvector + Obsidian wikilinks
3. Las 4 inconsistencias detectadas son aisladas y se pueden corregir quirúrgicamente

---

## 5. Decisión

**Aprobada:** 2026-04-29 por Dario.

---

## 6. Convenciones canónicas

### Por tipo de directorio

| Directorio | Patrón | Ejemplo |
|---|---|---|
| `docs/sesiones/` | `YYYY-MM-DD-titulo-kebab.md` | `2026-04-29-error-arquitectonico-mini-bloque-3-3-y-cleanup.md` |
| `docs/decisiones/` | `NNNN-titulo-kebab.md` (4 dígitos padding) | `0030-file-naming-conventions-repo.md` |
| `docs/audits/` | `YYYY-MM-DD-titulo-kebab.md` (mismo patrón que sesiones) | `2026-04-29-audit-organizacion-integridad-seguridad.md` |
| `docs/runbooks/` | `titulo-kebab.md` (sin fecha — son evergreen) | `cierre-sesion.md`, `disk-full.md`, `preflight-cross-system.md` |
| `docs/seguridad/` | `titulo-kebab.md` | `gestion-de-secretos.md` |
| `docs/diagramas/` | `titulo-kebab.{png,svg,md}` | (vacío hoy, reservado) |

### Por tipo de archivo

| Tipo | Convención | Razón |
|---|---|---|
| Markdown (`.md`) | kebab-case | Consistencia + URL-friendly |
| Python (`.py`) | snake_case (PEP 8) | Estándar Python |
| Shell (`.sh`) | kebab-case | Consistencia con resto del repo |
| YAML CI (`.yml` `.yaml`) | kebab-case (`deploy-vps3.yml`) | Consistencia |
| JSON config (`.json`) | kebab-case | Consistencia |
| `Dockerfile` | exacto (sin extensión) | Estándar Docker |
| `docker-compose.yml` | exacto | Estándar Docker |
| `README.md` | exacto (mayúscula) | Convención GitHub |

### Reglas duras

1. **NO espacios en nombres de archivos** (ni siquiera en data files). Excepción única: archivos legacy que ya están commiteados (ver "Excepciones" abajo).
2. **NO caracteres especiales** (acentos, ñ, símbolos no-ASCII) en nombres — usar transliteración (`piropo` no `piropó`).
3. **NO mayúsculas en nombres de docs** salvo `README.md` (convención GitHub) y `CLAUDE.md` (config Claude Code).
4. **Sí mayúsculas en `Dockerfile`** (estándar Docker).
5. **Fechas siempre en formato ISO 8601**: `YYYY-MM-DD`.
6. **Padding numérico**: ADRs usan 4 dígitos (`0001`, `0030`), versiones de migrations Alembic usan 4 dígitos (`0001_initial`).

### Sufijos canónicos (cuando aplica)

| Sufijo | Significado |
|---|---|
| `-template.md` | Plantilla para crear nuevos | 
| `-example` (ej. `.env.example`) | Template config con valores ficticios |
| `_legacy/` (folder) | Código deprecated en período de gracia (no eliminado todavía) |
| `-disabled` | Archivo desactivado pero no borrado (típico mu-plugins) |

### Lo que va a `.gitignore` automáticamente

- `Senza nome*.canvas`, `Untitled*.canvas` — Obsidian artifacts vacíos (creados por accidente con New > Canvas)
- Cualquier archivo con espacios creado por accidente (`*  *.md`, etc.)
- `.DS_Store`, `Thumbs.db`, `desktop.ini` — OS artifacts

---

## 7. Excepciones permitidas

Archivos legacy ya commiteados con nombres no-conformantes — **NO renombrar** porque romperían referencias massivas:

1. `docs/Datos Livskin.xlsx` (espacios) — base de datos histórica anonimizada por paso del tiempo. Se mantiene como referencia. Si se renombra, hay que actualizar +20 referencias en docs.
2. `docs/livskin_pensamientos para una implemetacion profesional basica pero basada en ia.docx` (espacios + typo "implemetacion") — blueprint original. Múltiples referencias. Renombrar requiere 30-45 min de cuidadoso grep + update.

**Cuándo reabrir el rename de los legacy:**
- Cuando se haga una sesión dedicada exclusivamente a refactor de organización (no en conjunto con feature work)
- Si se identifica que el nombre rompe alguna integración nueva (improbable)

Para futuras adiciones de archivos data tipo Excel/Word, **aplicar las reglas duras** (sin espacios, kebab-case, sin caracteres especiales).

---

## 8. Consecuencias

### Desbloqueado por esta decisión

- Onboarding más claro para nuevos colaboradores (humanos o Claude)
- Reducción de inconsistencias en próximos archivos (regla escrita = aplicable)
- Base para automatización futura (ej. linter de naming en pre-commit hook)

### Implementación derivada (post-aprobación)

- [x] `.gitignore` actualizado con `Senza nome*.canvas` + `Untitled*.canvas` (2026-04-29)
- [x] 2 archivos canvas vacíos borrados (2026-04-29)
- [ ] (Opcional, sesión futura) Rename de `docs/audits/` a patrón uniforme (5 archivos)
- [ ] (Opcional, sesión dedicada) Rename de archivos legacy con espacios

### Cuándo reabrir esta decisión

- Si surge un caso de uso que no encaja en las convenciones actuales (ej. soporte para múltiples idiomas en docs → puede requerir sufijo `-en.md`/`-es.md`)
- Si la migración mass-rename de legacy se decide hacer

---

## 9. Changelog

- 2026-04-29 — v1.0 — Creada y aprobada
