# Sesión 2026-04-18 — Arranque Fase 0

**Duración estimada:** ~6-7 horas de trabajo acumulado (conversación estratégica + ejecución)  
**Tipo:** estratégica + ejecución (primera sesión en esta máquina personal)  
**Participantes:** Dario (decisora) + Claude Code (ejecutor)

---

## Contexto de arranque

Primera sesión en la laptop personal de Dario (ella usa 2 computadoras, esta y la del trabajo). El repo ya estaba en GitHub (`DarioUrrutia/livskin-revops`) desde la sesión anterior (2026-04-16), pero este folder estaba vacío y sin accesos a VPS desde esta máquina.

---

## Objetivos de la sesión

1. Conectar este folder al repo GitHub y cerrar el entorno a esta carpeta
2. Establecer acceso SSH a los 2 VPS existentes desde esta máquina
3. Auditoría en vivo para verificar estado vs audit previo del 2026-04-16
4. Asimilar el blueprint estratégico (docx) + datos reales del Excel + ERP en Render
5. Consolidar estrategia, tomar 39+ decisiones estructurales y dejar el plan listo
6. Reorganizar el repo, crear dossiers fundacionales, CLAUDE.md, master plan
7. Commitear baseline de Fase 0 a GitHub

---

## Hitos de la sesión

### Parte 1 — Acceso y auditoría en vivo

- Repo clonado desde `DarioUrrutia/livskin-revops`
- `.claude/settings.json` configurado con permisos cerrados a esta carpeta
- Clave SSH nueva generada (`keys/claude-livskin`, ed25519, sin passphrase)
- Llave pública instalada en `~/.ssh/authorized_keys` del usuario `livskin` en ambos VPS (mediante PuTTY manual)
- SSH config local creado en `keys/ssh_config` con aliases `livskin-wp` y `livskin-ops`
- Conexión verificada a ambos VPS + sudo NOPASSWD confirmado
- **Auditoría en vivo** contra `docs/system-audit-2026-04-16.md`:
  - Estado general consistente
  - Metabase y postgres-analytics restartearon 2026-04-16 (coincide con deployment ese día)
  - Disco ops 7.9GB → 12GB (crecimiento por nuevos containers, normal)
  - RAM ops 53% → 58%
  - Fail2Ban ops: 369 fallos SSH acumulados, 46 bans históricos, 1 activo
  - Nginx warning deprecated `http2` en n8n.conf (cosmético)
  - WP root real: `/var/www/livskin` (no `/var/www/livskin.site`)
  - `wp-cli` NO instalado en WP VPS
  - Último backup UpdraftPlus: 2026-03-30 (19 días)
  - Repo NO clonado en los VPS (compose files en `~/apps/` como copias)

### Parte 2 — Contexto estratégico

- Leído blueprint completo (`docs/livskin_pensamientos...docx` → extraído a `pensamientos.txt`)
- Excel de datos reales procesado: 74 ventas, 135 clientes, S/.29,995 revenue, 7 semanas
  - Ticket promedio S/.405 (blueprint asumía S/.280-1,200)
  - Botox = 34% del volumen (top categoría)
  - 47% pagos en efectivo (crítico: mitad no trazable digital)
  - **Gap crítico:** no existe campo "fuente del lead" en data actual
- ERP Livskin en Render (formulario-livskin.onrender.com) revisado — Flask + Google Sheets, 5 módulos (Venta, Gasto, Pagos, Cliente Dashboard, Libro)
- Claude Design evaluado via WebSearch:
  - Herramienta Anthropic lanzada 2026-04-17 (2 días antes de esta sesión)
  - Powered by Opus 4.7
  - Research preview para Claude Max (ya pagado)
  - Export directo a Canva (fully editable)
  - Export a Claude Code (yo)
  - Perfecto fit para landing pages + banners

### Parte 3 — Toma de decisiones (39+ ADRs)

Trabajo de definición estratégica intensivo. La decisora explícitamente pidió varias veces **pensamiento estratégico completo, no respuestas reactivas**. Feedback crítico recibido y corregido:

- No estaba tomando la profundidad del proyecto → rediseño completo del plan
- Segundo cerebro no estaba como workstream estratégico → se elevó
- Seguridad no tenía apartado propio → se elevó a workstream dedicado
- Plan tenía solo 3 dossiers cuando requiere ~45 → expansión del mapa

**Principales decisiones aprobadas:**

| # | Decisión | Resolución |
|---|---|---|
| - | 3er VPS dedicado | Sí, $12/mes, 2GB/50GB Frankfurt (VPS 3 Data) |
| - | Comunicación entre VPS | **DO VPC** (no Tailscale) — decisora corrigió mi propuesta inicial |
| - | ERP: refactor vs rewrite | **Refactor Flask** (Opción A), no rewrite |
| - | Migración ERP | Strangler fig, Render → VPS 3, paralelo luego cutover |
| - | Agenda | Sin LatePoint. Flujo WhatsApp → Vtiger Calendar directo |
| - | ERP usuarios | 2 cuentas fijas (tú + doctora), sin concurrencia |
| - | Historial paciente | Diferido, campo `historial_json` reservado en schema |
| - | SUNAT / IGV | Deferidos |
| - | Inventario | Fuera MVP, máximo registro de compras en `gastos` |
| - | WhatsApp | Test number de Meta para desarrollo, prod cuando Meta apruebe |
| - | Embeddings | Self-hosted `multilingual-e5-small` ($0) |
| - | Claude Design | Sumada al workstream creativo |
| - | Atribución | Last-touch para MVP |
| - | Backups | Escalonados por fase, activar cron al primer lead real (Fase 2) |

**Roadmap consolidado:** 10 semanas, 6 workstreams paralelos (infra · datos · tracking · agentes · cerebro · seguridad).

### Parte 4 — Construcción del baseline (ejecución)

Reorganización completa del repo:

```
DE:                          A:
/docker/                     /infra/docker/
/nginx/                      /infra/nginx/
/scripts/                    /infra/scripts/
/sql/                        /infra/sql/
(no existían)                /integrations/{meta, google, whatsapp, cloudflare, canva, anthropic, fal-ai, claude-design}/
                             /agents/{conversation, content, acquisition, growth}/
                             /analytics/{schemas, migrations, dashboards}/
                             /backups/
                             /docs/{decisiones, sesiones, audits, seguridad, runbooks, diagramas}/
```

Documentos creados en esta sesión:

1. **CLAUDE.md** (raíz) — contexto maestro para cada sesión de Claude Code
2. **README.md** (raíz, reemplazando anterior) — documentación pública del repo
3. **docs/master-plan-mvp-livskin.md** — PLAN AUTORITATIVO del proyecto (15+ secciones, ~8000 palabras)
4. **docs/decisiones/README.md** — index de 40+ ADRs con estado
5. **docs/decisiones/_template.md** — plantilla ADR
6. **docs/decisiones/0001-segundo-cerebro-filosofia-y-alcance.md** — filosofía del segundo cerebro + 6 capas + tecnologías + schemas + cronograma
7. **docs/decisiones/0002-arquitectura-de-datos-y-3-vps.md** — topología 3 VPS + 5 DBs + flujo end-to-end
8. **docs/decisiones/0003-seguridad-baseline-y-auditorias.md** — 10 dimensiones + baseline + cronograma + auditorías programadas
9. **README placeholders** en integrations/, agents/, analytics/, docs/seguridad/, docs/audits/, docs/runbooks/

Configuración:
- `.gitignore` robustecido (keys/, erp/, backups/, .env*, extracciones temporales, etc.)
- `.claude/settings.json` con deny explícito en `erp/` + rm -rf + git push --force bloqueados

Memoria persistente Claude Code actualizada con:
- `user_profile.md` — perfil de la usuaria
- `project_livskin_overview.md` — contexto de negocio
- `project_stack.md` — stack consolidado
- `project_roadmap.md` — roadmap 10 semanas
- `feedback_operating_principles.md` — 10 principios
- `feedback_no_paid_services.md` — regla cero costos
- `vps_access.md` — acceso SSH
- `reference_docs.md` — dónde buscar qué

---

## Decisiones pendientes que quedan en tu cancha

1. **Iniciar trámite WhatsApp Business API** en Meta (para número producción, 5-10 días hábiles)
2. **Crear Meta App + habilitar WhatsApp test number** (ver `integrations/whatsapp/README.md` — 15 min)
3. **Cargar créditos en Anthropic console** y generar API key
4. **Generar API key fal.ai**
5. **Instalar Bitwarden** + crear vault para este proyecto, guardar `keys/.env.integrations`
6. **Confirmar disponibilidad real semanal** (12-15 h asumidas del blueprint)

Ninguno de estos bloquea hoy — los encaramos al inicio de Fase 1.

---

## Observaciones sobre la sesión

**Lo que funcionó:**
- Decisora me corrigió múltiples veces con razón (segundo cerebro como workstream, seguridad explícita, DO VPC mejor que Tailscale, no LatePoint, rewrite mal planteado)
- Cada corrección mejoró el plan final
- El proceso iterativo de crear 39+ decisiones expansión 3 → 40 dossiers dio visibilidad completa al proyecto
- Claude Design salió 2 días antes de esta sesión y encajó perfecto al stack

**Lo que aprendí sobre cómo trabajar con Dario:**
- Respuestas reactivas a preguntas puntuales no alcanzan; necesita visión holística
- Leer TODO el contexto que comparte (docs, Excel, links) antes de responder
- Usar MAYÚSCULAS o mensajes largos es señal de que necesita profundidad
- Explicar términos técnicos al aterrizar (CLAUDE.md, MCP, Alembic, strangler fig)
- Dar opciones con tradeoffs en tabla, no jerga
- Cuando ella dice "decide tú", transparencia TOTAL sobre el porqué
- Evitar proponer implementación antes de definición estructural aprobada

**Lo que quedó reforzado como principio:**
- **Lo ejecutable supera a lo ideal**, pero defender el equilibrio — no sobre-simplificar
- **Antes de implementar, definir** — evita 10x fricción en despliegue después
- **Memoria persistente** carga contexto a futuras sesiones (cross-máquina)

---

## Estado al cierre

✅ **Fase 0 completada en lo estratégico y documental.**  
⏳ **Fase 0 pendiente en lo operativo** (5 items tuyos arriba).

**Exit criteria Fase 0 logrados:**
- Puedes cerrar esta laptop, abrir otra, `git clone`, bajar `.env.integrations` de Bitwarden (cuando lo tengas), y retomar sin pérdida de contexto
- CLAUDE.md + master plan + memoria persistente garantizan continuidad en futuras sesiones
- 3 dossiers fundacionales aprobados dan las bases para Fase 1

**Próximo paso:** Fase 1 (Semana 2) — provisionar VPS 3, configurar DO VPC, Postgres+pgvector, embeddings service, CI/CD GitHub Actions, Alembic, staging env.

---

## Commits derivados de esta sesión

1. `docs: fase 0 - baseline plan maestro + dossiers 0001-0003 + reorganizacion repo`

---

## Referencias

- Audit previo: [docs/system-audit-2026-04-16.md](../system-audit-2026-04-16.md)
- Bitácora previa: [docs/consultas-y-decisiones.md](../consultas-y-decisiones.md)
- Blueprint: [docs/livskin_pensamientos...docx](../livskin_pensamientos%20para%20una%20implemetacion%20profesional%20basica%20pero%20basada%20en%20ia.docx)
- Data: [docs/Datos Livskin.xlsx](../Datos%20Livskin.xlsx)
- Plan maestro: [docs/master-plan-mvp-livskin.md](../master-plan-mvp-livskin.md)
- Index decisiones: [docs/decisiones/README.md](../decisiones/README.md)

---

**Firma del log:** Claude Code (Opus 4.7, 1M context) + Dario · 2026-04-18
