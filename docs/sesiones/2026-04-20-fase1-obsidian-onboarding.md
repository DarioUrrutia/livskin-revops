# Sesión 2026-04-20 (parte 4) — Obsidian onboarding + pregunta estratégica diferida

**Duración:** ~30 min
**Tipo:** onboarding + consulta estratégica
**Participantes:** Dario + Claude Code
**Fase del roadmap:** Fase 1 (cierre real — capa humana del cerebro)

---

## Contexto

Tras cerrar Fase 1 en parte 3 (brain L2 indexado), quedaba el setup de la **capa humana del segundo cerebro**: Obsidian como interfaz visual sobre los mismos `.md` que brain-tools indexa en pgvector.

## Lo que se hizo

### 1. Instalación Obsidian

Dario instaló Obsidian en laptop (Milán, Windows, idioma italiano) y seleccionó la raíz del repo como vault. Confirmación visual: vault "Union VPS - Maestro - Livskin" abierto con estructura completa visible (agents, analytics, backups, docs, infra, integrations, keys, notes, CLAUDE, README).

### 2. Configuración mínima

- Editor default mode: **Anteprima dinamica** (Live Preview) — se conservó el default, decisión correcta para usuaria no-técnica. Source mode se descartó tras reflexión (demasiado crudo para uso diario).
- File and links: auto-update internal links ON, relative path para nuevos links.

### 3. Graph View explorado

Dario ejecutó `Ctrl+G`. Observación de Claude sobre el grafo visible:

- **Cluster central denso** (~40 nodos interconectados) = master plan + ADRs + session logs + backlog
- **Nodos satélite aislados** = READMEs de servicios aún no referenciados desde docs principales (señal de documentos "huérfanos" en términos de links)
- Total: ~70 nodos = corresponde a los 43 archivos indexados por brain-tools + READMEs de carpetas + otros `.md` sueltos

Esto valida la arquitectura dual-consumer del conocimiento (ADR-0001 § 9.2): mismos `.md` sirven a la interfaz humana (grafo visual Obsidian) y a la interfaz máquina (retrieval semántico pgvector).

### 4. Búsqueda demo: "pgvector"

Dario ejecutó `Ctrl+Shift+F` con query "pgvector". Resultado: **70 matches en 11 archivos**, distribución:

| Archivo | Matches |
|---|---|
| `0001-segundo-cerebro-filosofia-y-alcance.md` | 19 |
| `0002-arquitectura-de-datos-y-3-vps.md` | 13 |
| `2026-04-19-fase1-vps3-creado.md` | 10 |
| `master-plan-mvp-livskin.md` | 7 |
| (otros incluyendo READMEs y session logs) | resto |

Demostró que la búsqueda full-text cross-vault da intuición inmediata de "cuán profunda" está una decisión en el proyecto.

## Dudas y decisiones emergentes

### Pregunta 1 — "¿tantos READMEs es necesario?"

Dario observó que aparecen 4 READMEs indistinguibles en resultados de búsqueda. Claude explicó la convención de GitHub (auto-render). Consenso: **no cambiar ahora**, se puede reorganizar después. Dario usa `Ctrl+O` (Quick Switcher) que sí muestra path completo para distinguirlos.

### Pregunta 2 (ESTRATÉGICA) — "¿Obsidian sirve para memoria de clientes / campañas?"

Dario preguntó si Obsidian podría tener un "apartado por cliente" con historial e interacciones, para que el cerebro "sepa cómo tratarlos".

**Respuesta de Claude:** Obsidian es la herramienta INCORRECTA para data operativa de clientes. Lo correcto es la arquitectura ya diseñada:

- **Vtiger CRM** → identidad master de cada cliente (Fase 2)
- **Postgres `livskin_erp`** → transacciones, tratamientos, pagos (Fase 2)
- **`livskin_brain.conversations`** + pgvector → historial WhatsApp embebido para retrieval (Fase 4)
- **Conversation Agent** → query a los 3 en <1s para responder contextualmente (Fase 4)

PERO Obsidian SÍ sirve para lo **narrativo/estratégico**:
- **Arquetipos de cliente** (`notes/compartido/arquetipos/*.md`) — alimentan prompts del Conversation/Content Agent
- **Post-mortems de campañas** (narrativa, no structured data)
- **Notas personales de pacientes VIP** (en `notes/privado/`, gitignored)

Dario decidió **diferir** la definición de arquetipos y segmentación a **sesión estratégica dedicada** (antes de Fase 4). Lo enmarcó en su pensamiento natural: "al momento de definir nuestra estrategia, nuestros segmentos, nuestro negocio y ver su plan estratégico".

### Limpieza: Canvas file accidental

Dario creó sin querer un `Senza nome.canvas` al explorar Obsidian. Se borró. Canvas queda documentado como feature para uso futuro (flujos visuales, planificación de campañas).

## Cambios al repo

- **Nuevo ítem en `docs/backlog.md` → Mediano plazo:** *"Sesión estratégica — definir estrategia, segmentos y plan de negocio"* con scope completo (arquetipos, posicionamiento, plan 6-12-24 meses), output esperado (`notes/compartido/arquetipos/` + `docs/estrategia/`), y link a su relevancia para Fase 4-5 (los arquetipos son input literal a los prompts de agentes).
- **Archivo borrado:** `Senza nome.canvas` (basura accidental).
- **Sin cambios de código**, sin nuevos ADRs, sin migraciones.

## Cierre real de Fase 1

Con Obsidian funcionando, la capa humana del segundo cerebro queda viva:

```
✅ Layer 2 (project_knowledge) indexado en pgvector — 679 chunks (máquina)
✅ Obsidian abre el vault — grafo navegable (humano)
✅ Ambos consumen los mismos .md — sin duplicación, sin sync
```

**Fase 1 = 100% completa, todas las piezas operativas.**

## Próxima sesión

**Fase 2 — ERP refactor + gobierno de datos**, sin alternativa.

Arranca con los 4 dossiers de gobierno de datos (ADRs 0011-0014: modelo Lead/Cliente/Venta, stages Vtiger, dedup, naming conventions) antes de tocar código del ERP.

**Por qué sin alternativa** (corrección de framing inicial):
Al cerrar esta sesión inicialmente presenté dos opciones: "Fase 2" o "adelantar sesión estratégica". Dario observó correctamente que la opción B viola el principio de *plumbing-first* y rompe el desarrollo del proyecto. Las sesiones estratégicas son **slots programados del roadmap**, no alternativas ad-hoc al trabajo táctico.

**Dónde vive la sesión estratégica ahora:**
Formalizada como **§ 11.5b del master plan** — Interludio estratégico entre Fase 3 y Fase 4. Es el único slot correcto porque:
- Plumbing validado con data sintética (Fases 1-3 completas) → discusión aterrizable
- Antes de Fase 4-5 (agentes que consumen arquetipos como input de prompt)
- No desplaza fechas si se hace con foco (1-2 sesiones, ~4-8h)

Adelantarlo violaría plumbing-first; retrasarlo bloquearía Fase 4. Hay un slot y solo uno.

**Correcciones aplicadas al cierre:**
1. Master plan → agregado § 11.5b "Interludio estratégico" + nota en § 11.1 Vista consolidada + changelog v1.1
2. Memoria `project_roadmap` → reescrita con principios explícitos + slot del interludio + regla "no hay opción B al proponer próxima sesión"
3. Backlog → removido el ítem floating de "sesión estratégica" (ahora vive en master plan, no en backlog)
4. Memoria nueva `feedback_roadmap_order` → regla para Claude Code: respetar orden del roadmap al proponer siguiente sesión, no ofrecer sesiones estratégicas como alternativas paralelas
5. Este session log → corregido el framing inicial de "dos opciones"

---

## Estadísticas del día completo 2026-04-20

- **4 session logs**: cicd + alembic + brain-l2 + obsidian-onboarding
- **Duración total**: ~7 horas acumuladas
- **Commits del día**: 8
- **Fase 1 cerrada**: todas las piezas (plumbing máquina + interfaz humana)

---

**Firma del log:** Claude Code + Dario · 2026-04-20 (parte 4, cierre definitivo Fase 1)
