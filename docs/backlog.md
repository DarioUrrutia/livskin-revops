# Backlog del proyecto Livskin

**Propósito:** artefacto vivo para capturar ideas, cambios, dudas y observaciones que no son acción inmediata pero **no deben perderse**.

**Uso:**
- Cualquier de los dos (Dario o Claude Code) agrega entradas cuando surjan ideas
- Al inicio de cada sesión, yo reviso el backlog y te propongo qué retomar
- Al cierre de cada sesión, movemos a "Hecho" o reordenamos prioridades
- Priorización por **impacto al proyecto**, no por orden cronológico

---

## Leyenda

- 🔴 Alta prioridad (bloquea algo o es riesgo activo)
- 🟡 Media prioridad (mejora importante, no bloquea)
- 🟢 Baja prioridad (nice to have)
- 💡 Idea/brainstorm (todavía sin decisión, a discutir)
- ❓ Duda abierta (requiere respuesta de usuaria)
- ✅ Hecho (se mantiene como historial)

---

## Prioritario

<!-- Cosas que hay que hacer pronto -->

### 🟡 Sesión estratégica — Estructura organizacional de agentes IA
**Antes de Fase 5 (Brand Orchestrator).** Dario pidió pensar el sistema como organización empresarial: él CEO, agentes con rangos + funciones + subagentes + skills.

**Output esperado:**
- ADR-0030 — Brand Orchestrator multi-agent architecture
- `docs/agents/organization-chart.md` — organigrama + roles + rangos + cadencias reporting
- Subdirs `docs/agents/<agent-name>/` con SKILL.md + prompts/ + tools.json + evals/ + cadence.md
- Brand voice consolidado en `docs/brand/voice.md`
- Approval flows + métricas de éxito por agente

**Visión clave registrada en memoria `project_agent_org_design.md`:**
- Brand Orchestrator (era Content Agent) expandido a director creativo end-to-end (ads + landings + copies + email + implementación)
- Patrón: orquestador + subagentes especializados (Research, Concept, Copywriter, Visual, Implementation)
- Skills compartidas cross-agent (research-competition usado por Brand + Acquisition + Growth)
- Aprobación bloqueante de anuncios (NUNCA publica sin OK Dario)

**Combinable con:** Interludio Estratégico (entre Fase 3 y Fase 4) — mismo bloque ~4-8h porque consume arquetipos del interludio.

**Fase sugerida:** post-Fase 3, pre-Fase 4 (interludio + sesión organizacional juntos).
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 Dashboards admin secundarios — `/admin/users`, `/admin/sessions`, `/admin/system-health`
ADR-0026 + ADR-0027 mencionan estos dashboards. Hoy solo está `/admin/audit-log`. Pendiente:
- `/admin/users` — lista usuarios + status + last_login + reset password de otro
- `/admin/sessions` — sesiones activas + ability to revoke
- `/admin/system-health` — status de containers + backups + cert expiry

**Por qué baja prioridad:** la Ley 29733 ya está cubierta con `/admin/audit-log`. Estos dashboards mejoran capacidad operativa pero no son bloqueadores.
**Fase sugerida:** post-Fase 3 si Dario los necesita
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 CI/CD: tests pre-deploy en lugar de post-deploy
Hoy el workflow `deploy-vps3.yml` corre pytest DESPUÉS del deploy. Eso significa que código broken puede llegar a producción antes de que los tests lo detengan.

**Mejora:** build el container en el runner GHA, levantar Postgres temporal, correr pytest contra el build. Si pasa → deploy. Si falla → no deploy.

**Mitigación actual:** el ERP refactorizado está en validación interna (no producción real, Render sigue siendo prod hasta Fase 6). El riesgo es bajo.
**Fase sugerida:** Fase 6 antes del cutover Render→VPS 3
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 Limpiar gaps diferidos del Flask original
Dos gaps documentados en `docs/erp-flask-original-deep-analysis.md` no se cerraron por ser cosméticos / no críticos:
1. Métodos de pago primera fila — el HTML original tenía pre-fill heurístico de la primera fila de pagos según fecha; no replicado.
2. Multi-currency por item — el original soporta moneda por línea de venta; el refactor unifica moneda a nivel venta.
3. Categoría `__otro__` libre — el HTML acepta categoría arbitraria via `__otro__`, el refactor solo lista presets.

**Cuándo:** si la doctora reporta fricción específica al usar el sistema.
**Fase sugerida:** Fase 6 o reactiva.
**Agregado por:** Claude Code · 2026-04-26

---

### 🟢 Subir coverage de tests más allá del 81% actual
Actualmente 81.31% (target ADR-0023 era ≥75%, superado). Áreas con coverage bajo:
- `routes/api_venta.py` — 25%
- `routes/api_cliente.py` — 39%
- `services/dashboard_service.py` — 75% (falta cubrir cálculo aging + comparativas)
- `services/normalize_service.py` — 86% (edge cases de phone/email)

Subir a 90%+ daría más confianza para refactors futuros, pero no es bloqueador.
**Fase sugerida:** opcional, post-Fase 3
**Agregado por:** Claude Code · 2026-04-26

---

### 🟡 Capa de auto-mantenimiento — implementar al cierre de Fase 6
Para que Dario NO dependa de intervenir manualmente en el sistema cuando esté dirigiendo la empresa (target: 3-5 h/mes total incluyendo mantenimiento).

**Componentes a implementar en Fase 6:**
- **Watchtower** (gratis, self-hosted) — monitorea containers y aplica security updates de imágenes Docker automáticamente. Reduce el riesgo de CVEs sin intervención manual.
- **UptimeRobot free tier** (50 monitors gratis) — monitorea cada subdominio público cada 5 min. Si cae algo, email/SMS a Dario.
- **n8n workflows de alertas internas** — vigilan disco, RAM, costos Claude API; alertan vía WhatsApp cuando crucen umbrales (definidos en ADR-0003 § 15.2).
- **Monthly audit auto-ejecutado** — cron job del día 1-5 de cada mes corre audit completo (Lynis + docker state + cert expiry + disk + etc.) y commitea el report a `docs/audits/`.
- **Runbooks operativos completos** — en `docs/runbooks/` documentar procedimientos paso a paso para los 5-10 incidentes más probables (SSL expirado, disco lleno, container crash, API key comprometida, etc.). Así cualquier persona puede resolver sin experticia.

**Objetivo cuantitativo:** reducir mantenimiento a <5h/mes rutinario + incidentes que alerten automáticamente.

**Decisión a futuro (Año 1-2):** según volumen real de incidentes, evaluar Ruta A (tú + Claude Code), Ruta B (fractional DevOps $300-800/mo) o Ruta C (managed services DO Managed Postgres +$15/mo).

**Referencia:** esta decisión fue formalizada tras consulta de Dario el 2026-04-20 sobre "cómo se mantiene esto cuando yo esté dirigiendo la empresa". Documentado en master plan § "Operación post-MVP y mantenimiento".

**Fase sugerida:** Fase 6 (Semana 10) + ajustes post-lanzamiento según data real.  
**Agregado por:** Claude Code · 2026-04-20

---


### 🟡 Agregar passphrase a `livskin-vps-erp.ppk` al cerrar Fase 2
Durante Fase 1-2 la `.ppk` no tiene passphrase (decisión consciente por fricción de setup). Al terminar Fase 2 (cutover ERP completo), agregarle passphrase y guardar en Bitwarden.

**Cómo:** PuTTYgen → Load → tipear nueva passphrase + confirm → Save private key.  
**Fase sugerida:** cierre de Fase 2 (semana 4)  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Agregar IP de laptop de trabajo de Dario al whitelist Fail2Ban
La IP pública actual (`78.208.67.189`) es solo de la laptop personal en Milán. Cuando Dario conecte desde la laptop de trabajo por primera vez, si Fail2Ban la banea automáticamente, lo arreglamos y agregamos esa IP al `ignoreip` en `/etc/fail2ban/jail.d/ignoreip.local` en los 3 VPS.

**Fase sugerida:** cuando aparezca por primera vez (reactivo)  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Limpiar `/srv/livskin/` en VPS 3 (carpeta vieja pre-migración)
El 2026-04-20 se migraron los containers de `/srv/livskin/<svc>/` a `/srv/livskin-revops/infra/docker/<svc>/` como parte del setup de CI/CD. La carpeta vieja `/srv/livskin/` (postgres-data, embeddings-service, nginx) quedó como backup temporal.

**Cuándo borrarla:** después de 24-48h de operación estable desde la nueva ubicación (probable: 2026-04-22).  
**Cómo:** SSH a VPS 3 → `sudo rm -rf /srv/livskin/postgres-data /srv/livskin/embeddings-service /srv/livskin/nginx` (preservando `/srv/livskin/` mismo por si se necesita para algo futuro, o borrar todo si ya no tiene uso).  
**Agregado por:** Claude Code · 2026-04-20

---

### 🔴 Borrar snapshot VPS 3 cuando Fase 1 esté estable
Snapshot `livskin-vps-erp-baseline-post-hardening-2026-04-19` cuesta ~$3/mes si se mantiene permanente. Debe borrarse cuando la Fase 1 esté operativamente estable (típicamente 1-2 semanas post-deploy sin incidentes). Mientras tanto es cobertura por si algo falla y necesitamos rollback al estado pre-Postgres.

**Cuándo borrarlo:** ~2 semanas después de que Postgres + embeddings service estén corriendo sin incidentes (probable fecha: semana del 2026-05-03).  
**Dónde:** DO panel → droplet livskin-vps-erp → Backups & Snapshots → Delete.  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟢 Configurar email para `livskin.site` (MX + SPF + DKIM + DMARC)
Cloudflare alerta sobre falta de MX records. No bloquea nada operativo, pero:
- Sin MX: nadie puede mandar email a info@livskin.site, doctora@livskin.site, etc.
- Sin SPF/DKIM/DMARC: spammers pueden suplantar @livskin.site (afecta deliverability de marketing)

**Decisiones pendientes:**
- ¿Email propio en livskin.site? ¿O solo usan Gmail/Yahoo personales?
- Si sí: ¿qué proveedor? Google Workspace ($6/user/mes), Zoho Mail ($1/user/mes), ProtonMail (más caro), o self-hosted (descartado — dolor de cabeza para PYME)
- Dario confirma si necesita este canal de comunicación formal

**Fase sugerida:** no crítico hasta lanzamiento comercial formal. Si se decide email propio, 30 min de setup.  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Crear Dossier ADR-0019 (tracking architecture) en versión full
Actualmente es stub en el index. Al llegar a Fase 3 debe escribirse completo. Incluye server-side tracking, eventos, consent, match quality targets.

**Referencia:** docs/decisiones/README.md línea 0019  
**Fase sugerida:** Fase 3 (Semana 5)  
**Agregado por:** Claude Code · 2026-04-18

---

### ❓ Confirmar nombre del repo GitHub del ERP Livskin
La usuaria mencionó que el ERP tiene su propio repo GitHub. Necesario al llegar a Fase 2 para clonarlo en `erp/` local.

**Referencia:** ADR-0023 (ERP refactor)  
**Acción:** preguntar a Dario en próxima sesión  
**Agregado por:** Claude Code · 2026-04-18

---

### 🟡 Definir las 5-10 FAQs típicas de pacientes para Layer 1 del cerebro
Para poblar `clinic_knowledge` con las preguntas que más hacen los pacientes + respuesta autoritativa validada por la doctora.

**Referencia:** ADR-0001 sección 7.1  
**Fase sugerida:** Fase 2 (Semana 3-4)  
**Necesita input de:** la doctora  
**Agregado por:** Claude Code · 2026-04-18

---

## Mediano plazo

### 🟡 Plugin de WordPress para tracking server-side
Evaluar si hay plugin WP open-source que nos ayude con UTM persistence + server-side event forwarding, o si construimos script custom mínimo.

**Referencia:** ADR-0021 (UTMs persistence)  
**Fase sugerida:** Fase 3  
**Agregado por:** Claude Code · 2026-04-18

---

### 🟢 Explorar Dataview plugin de Obsidian para dashboards de proyecto
Dataview permite escribir queries SQL-like sobre frontmatter YAML de los .md. Podríamos generar "estado actual de todos los ADRs" en una tabla viva dentro de Obsidian.

**Fase sugerida:** Fase 0-1 (cuando Obsidian esté instalado)  
**Agregado por:** Claude Code · 2026-04-18

---

## Ideas (brainstorm, sin decisión aún)

### 💡 Integrar Pipedream o similar como redundancia de n8n
Si n8n cae, Pipedream podría actuar como failover para webhooks críticos (form submit). No urgente pero vale la pena evaluar.

**Agregado por:** Claude Code · 2026-04-18

---

### 💡 Caso de estudio público para LinkedIn
Al terminar Fase 6 (mes 2-3 de operación estable), publicar case study técnico: "Cómo construí un sistema RevOps multi-agente en 10 semanas solo con Claude Code". Material excelente para portfolio RevOps.

**Agregado por:** Claude Code · 2026-04-18

---

## Dudas abiertas

### ❓ ¿Livskin emite comprobantes electrónicos a SUNAT hoy?
Si ya factura electrónicamente, necesitamos integración con PSE (Nubefact, Efact, etc.). Si no, decisión de negocio diferida.

**Trigger para responder:** cuando Dario decida estrategia fiscal  
**Relacionado:** ADR-0099 (SUNAT — diferido)  
**Agregado por:** Claude Code · 2026-04-18

---

### ❓ ¿La clínica imprime recibos físicos a pacientes?
Condiciona si necesitamos módulo PDF/impresión en ERP.

**Relacionado:** ADR-0103 (PDFs — diferido)  
**Agregado por:** Claude Code · 2026-04-18

---

## Hecho (historial)

<!-- Los items completados se mueven aquí para mantener historial. No se borran. -->

### ✅ Fase 0 — Repo reorganizado + 3 dossiers + master plan
Completada 2026-04-18. Ver session log correspondiente.

### ✅ ADR-0005 simplificada a "n8n único orquestador"
Originalmente aprobada como híbrido; revisada por Dario en misma sesión. Agent SDK diferido.
2026-04-18.

### ✅ Obsidian integrado al plan como capa humana del segundo cerebro
Dario propuso, se aprobó, se actualizó ADR-0001 con sección 9.2.
2026-04-18.

### ✅ VPS 3 provisionado y hardened
`livskin-vps-erp` @ 139.59.214.7 (VPC 10.114.0.4). Ubuntu 22.04.5, Docker 29.4.0, swap 2GB, UFW+Fail2Ban+unattended-upgrades activos. Lynis score 65/100. VPC connectivity a VPS 1 y 2 verificada (<2ms).
2026-04-19. Ver `docs/sesiones/2026-04-19-fase1-vps3-creado.md`.

### ✅ Whitelist Fail2Ban con ignoreip
Tras incidente de auto-ban en instalación de UFW: whitelist permanente creada en `/etc/fail2ban/jail.d/ignoreip.local` con 127.0.0.1/8, ::1, 10.114.0.0/20 (VPC), 78.208.67.189 (Dario Milan). 2026-04-19.

### ✅ CI/CD workflow extendido a stack ERP completo
Commit `7eb2d63` (2026-04-26). Workflow `.github/workflows/deploy-vps3.yml` ahora cubre: erp-flask con `--build`, alembic-erp + brain-tools `build only`, nginx `-s reload` tras cambios de config, retry verify de URLs públicas (3 intentos × 5s, sleep inicial 20s). Resuelve además el item original "Workflow CI/CD: agregar nginx reload" (2026-04-20).

### ✅ ERP refactorizado deployed funcional con data real
Commits del 2026-04-26 (`815cb0b` → `7eb2d63`). Stack: Flask + SQLAlchemy 2.0 + Pydantic v2 + structlog + gunicorn. Migration 0001 (12 tablas) + 0002 (trigger DEBE) aplicadas. Backfill ejecutado: 134 clientes + 88 ventas + 84 pagos del Excel productivo. URL `https://erp.livskin.site` responde con formulario funcional. Auditoría profunda Flask original cerró 11 de 13 gaps. Capa compat form-data preserva HTML legacy. 2026-04-26.

### ✅ erp-staging.livskin.site eliminado (decisión Opción A)
Durante Fases 2-5 el ERP nuevo está en validación interna (Render sigue siendo producción). Tener un staging del que ya está en validación era redundante. Staging real con DB separada se reabrirá en Fase 6 al hacer cutover real (ADR-0024 strangler fig). Commit `59e37c2`. DNS Cloudflare borrado por Dario. 2026-04-26.

### ✅ Auth bcrypt + login/logout + sesiones (ADR-0026)
Commit `87c07b5`. Stack: bcrypt 12 rounds, sesión 48h con auto-revoke por 2h inactividad, lockout 8 intentos / 15 min. 2 cuentas seedadas: Dario (admin) + Claudia Delgado (operadora). Templates login.html + change_password.html. Middleware Flask before_request protege todas las rutas excepto allowlist (login, logout, ping, static). CurrentUser dataclass desacoplado de SQLAlchemy session. Decorator @require_role para granularidad por rol. Passwords iniciales generadas + entregadas + cambiadas (Dario hizo su primer cambio). 2026-04-26.

### ✅ Audit log middleware + 30 eventos canónicos (ADR-0027)
Commit `75683c6` + migration 0003 (`0003_audit_immutable`). Trigger PL/pgSQL `audit_log_immutable()` rechaza UPDATE/DELETE a nivel DB (verificado: ni superuser puede modificar). AuditService.log() escribe entry atómicamente con la business logic dentro del session_scope. AuditService.log_isolated() para flujos donde el principal ya falló. 30 KNOWN_ACTIONS canónicos en 7 categorías (auth, venta, pago, gasto, cliente, lead, admin, webhook). Hooks instalados en auth (login_success/failed/lockout/logout/expired/inactivity/password_changed) + legacy_forms (venta/pago/gasto created con before/after states). Captura automática de IP, user-agent, user_id, user_role via flask.g + request. 2026-04-26.

### ✅ Dashboard /admin/audit-log con filtros + export CSV
Commit `9d72a60`. Tabla paginada (50/pag, max 500). Filtros: rango fechas, action, category, user, result, entity_id (búsqueda parcial). Export CSV respeta filtros, max 10000 filas, incluye before/after/metadata como JSON. UI minimalista con tags por categoría. @require_role("admin") protege endpoints (403 para Claudia). Header del formulario.html muestra link "audit log" solo para admin. Dropdowns muestran TODAS las categorías canónicas (no solo las que ya tienen entries) — fix `0dc52f5`. 2026-04-26.

### ✅ Test coverage 81.31% (target ADR-0023: ≥75%)
Commits `b7acedb` → `6450ae0`. 186 tests pasan en 76s. Cubre: auth_service (99%), audit_service (88%), cliente_service (87%), venta_service (93%), pago_service (93%), catalogo_service (100%), libro_service (100%), codgen_service (100%), middleware (100%), schemas (100%). Tests routes para auth + admin + legacy_forms + API JSON. CI/CD workflow ahora corre pytest post-deploy automáticamente (commit `6450ae0`). Conftest pattern: TRUNCATE-based cleanup, fixtures admin_user/operadora_user committeadas para que session_scope() las vea, db_session separada. DB livskin_erp_test creada en Postgres VPS 3. 2026-04-26.

---

## Cómo agregar una entrada nueva

Copia esta plantilla:

```markdown
### <icono> <título>
<Descripción breve — qué, por qué, qué falta>

**Referencia:** ADR-XXXX o doc relevante  
**Fase sugerida:** Fase N  
**Necesita input de:** <persona o "ninguno">  
**Agregado por:** <Dario | Claude Code> · YYYY-MM-DD
```

Y ubícala en la sección correcta según prioridad.
