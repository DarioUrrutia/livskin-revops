# Sesión 2026-04-25 — Fase 2: ADRs huérfanos del refactor + nuevo agente Infra+Security

**Duración:** ~6-8 horas
**Tipo:** definición intensa (5 ADRs MVP-speed) + clarificaciones operativas + visión nueva del 5to agente
**Participantes:** Dario + Claude Code
**Fase del roadmap:** Fase 2 (definición conceptual completa)

---

## Objetivo de la sesión

Cerrar los **5 ADRs huérfanos** marcados ✅ en el índice pero sin archivo (0023-0027) que faltaban para tener definición completa de Fase 2 antes de implementación.

## Estado al cierre

**Definición conceptual de Fase 2 = 100% completa.** Todos los ADRs necesarios están escritos:

**Gobierno de datos** (sesión 2026-04-21):
- ✅ ADR-0011 v1.1 — Modelo Lead/Cliente/Venta/Pago/Gasto (9 tablas)
- ✅ ADR-0012 — Pipeline stages Vtiger (5 stages)
- ✅ ADR-0013 v2 — Dedup phone-anchor + lead_touchpoints
- ✅ ADR-0014 — Naming conventions
- ✅ ADR-0015 — SoT por dominio

**Refactor + migración** (sesión 2026-04-25 — HOY):
- ✅ ADR-0023 — ERP refactor Flask (estrategia de modernización)
- ✅ ADR-0024 — Strangler fig (clone + parallel standby + cutover on-demand)
- ✅ ADR-0025 — Backfill script re-ejecutable
- ✅ ADR-0026 — Auth bcrypt + 2 cuentas con roles
- ✅ ADR-0027 — Audit log inmutable

## Trabajo realizado hoy

### 1. Verificación de estado al inicio
- Repo intacto desde el 21 (último commit `94e21f5`)
- 5 ADRs pendientes identificados como bloqueador
- Decisión: arrancar con ADR-0023 (estrategia) y avanzar 1 por 1 con validación

### 2. ADR-0023 — ERP refactor strategy
Tras mostrar a Dario las 4 decisiones core, ella aprobó:
- Estructura modular (carpetas separadas: models/services/routes/middleware)
- Eliminación de caché 90s del Flask actual
- **Coverage tests ≥75%** (ajuste de Dario vs mi 70% propuesto)
- Sin módulos olvidados del Flask actual

**Stack** decidido: Flask + SQLAlchemy 2.0 + Pydantic v2 + structlog + pytest + mypy + Docker.

**Estructura de archivos**: `erp-flask/` con models/ schemas/ services/ repositories/ routes/ middleware/ tests/ + alembic/.

**Endpoints nuevos críticos**: `/api/client-lookup`, `/webhook/form-submit`, `/webhook/whatsapp`, `/login`, `/logout`.

**Preservación**: `formulario.html` 100% intacto + las 6 fases de venta + endpoints existentes con mismo contract.

### 3. Clarificación crítica de Dario sobre preservación de producción

Dario emphasized (en mayúsculas): "**ESTAS COSAS DEBEN SER SOLO LECTURA**, NUNCA TOCAR Render ni Sheets ni el repo formulario-livskin".

Acciones tomadas:
- Memoria nueva `feedback_production_preservation.md` — regla absoluta inmutable
- CLAUDE.md actualizada: regla #2 "NUNCA tocar el sistema actual en producción" con detalle exhaustivo
- Repo `formulario-livskin` confirmado como SOLO LECTURA

### 4. Cambio de fuente de data: Excel viejo → export fresco del Sheets

Dario aclaró que el `docs/Datos Livskin.xlsx` (del 18 de abril) era una muestra vieja, no la verdad. La fuente real es el Sheets conectado a Render.

Decidimos:
- **Opción 1** (export manual): más simple para principiante, suficiente para MVP
- Dario hizo el export hoy → `docs/Datos_Livskin_2026-04-25.xlsx` (88 ventas, 84 pagos, 135 clientes)
- Archivo gitignored como PII (`.gitignore` actualizada)
- Memoria nueva `project_real_data_source.md` documenta el mecanismo

### 5. Confirmación crítica sobre Dario como principiante en implementación

Dario explícitamente solicitó: "explicame paso a paso, sin asumir que conozco términos técnicos".

Acción tomada:
- Memoria nueva `feedback_explain_to_beginner.md` — guidelines para explicar siempre, paso-a-paso UI, analogías cotidianas, glosarios cuando hay >3 términos técnicos

### 6. ADR-0024 — Strangler fig (migración Render → VPS 3)

Aprobado con 5 parámetros explícitos:
1. Cutover decidido por Dario (sin timeline forzado)
2. Secuencia de 7 pasos (T-48h aviso → T-2h export → T-1h backfill → T-30min smoke → T-15min lockout → T-0 cutover → T+72h monitoreo)
3. **60 días de cold standby** (Dario ajustó vs mis 30 propuestos)
4. Plan de rollback ("vuelvan a Render mientras arreglamos")
5. Solo Dario + doctora reciben avisos vía WhatsApp

Master plan § 11.8 actualizado con "60 días" en lugar de "30".

### 7. ADR-0025 — Backfill script re-ejecutable

Aprobado con 11 decisiones (5 validadas explícitamente por Dario + 6 técnicas que yo decidí con su luz verde):

| # | Tema | Decisión |
|---|---|---|
| 1 | Idempotencia | Sí (UPSERT por código único) |
| 2 | Modos | dry-run, apply, verify |
| 3 | Modo escritura | INSERT en dev, UPSERT en cutover |
| 4 | Logs | Detallados por ejecución |
| 5 | Datos raros | Importar tal cual |
| 6 | Container | Docker en VPS 3 |
| 7 | Errores en filas | Log + continuar |
| 8 | Orden carga | Catálogos → clientes → ventas → pagos |
| 9 | Tablas vacías | leads, touchpoints, audit_log, etc. |
| 10 | Code reuse | Reusa models del ERP |
| 11 | Modo verify | Conteos + sumas + sample 5 random |

Memoria nueva `project_backfill_decisions.md` plasma las 11 decisiones para referencia futura.

### 8. Visión nueva: 5to Agente — Infra + Security

Durante ADR-0025, Dario propuso una visión estratégica importante:

> "Estoy pensando que deberemos tener un agente especializado en el mantenimiento de toda nuestra infraestructura, que se encargue de estos detalles, o que sea mi asistente personal para llevar por mí, y yo solo autorizar, además debe también ser especializado en seguridad."

Acciones tomadas:
- Memoria nueva `project_infra_security_agent.md` — visión completa del 5to agente
- Master plan § 10.1 actualizado: agrega 5to agente como "fin de Fase 6 / extensión inmediata" (no post-MVP vago)
- **Timing corregido por Dario**: construir "pronto, en el mejor momento que aproveche los setups que ya estamos haciendo" → en cierre de Fase 6 cuando ya estamos setup-eando Watchtower + UptimeRobot + n8n alertas + monthly audit + backups (esos son los sensors/tools del agente)

### 9. ADR-0026 — Auth bcrypt + 2 cuentas

Aprobado con 6 parámetros explícitos:
1. 2 cuentas (Dario admin + doctora operadora)
2. Bcrypt
3. **Sesión 48h** (Dario eligió vs 8h propuesta)
4. Roles diferenciados
5. **8 intentos + 15 min lockout** (Dario eligió vs 5 propuesto)
6. **2 horas inactividad → auto-logout** (Dario eligió vs 30 min propuesto)

**Patrón consistente en preferencias de Dario**: sesgo hacia comodidad sobre seguridad estricta — apropiado para sistema interno trusted-team de 2 usuarios.

Schema completo de tabla `users` + `user_sessions` + procedimiento de password recovery + middleware con decorators `@authenticated` y `@require_role('admin')`.

### 10. ADR-0027 — Audit log inmutable

Aprobado con 6 recomendaciones mías ("tomaré tus recomendaciones, eliminarán fricciones en la implementación"):
1. ~30 tipos de eventos canónicos (auth + venta + pago + gasto + cliente + lead + admin + webhooks)
2. Schema rico (who/when/what/before/after/context/result + JSONs antes/después)
3. Inmutabilidad absoluta (permisos DB + trigger defensivo)
4. Retención para siempre
5. Solo admins ven el log
6. Dashboard `/admin/audit-log` con filtros + búsqueda + export CSV

### 11. Acumulación de capacidades del Agente Infra+Security

Por instrucción explícita de Dario ("estas cosas forman parte de mi agente, ya iremos desglosando capacidades, toma nota"), expandí `project_infra_security_agent.md` con secciones específicas:

**Capacidades de auth (ADR-0026)**:
- Detectar clusters de login fallidos
- Alertar lockouts
- Detectar logins fuera de horario
- Sugerir password rotation
- Asistir password resets

**Capacidades de audit log (ADR-0027)**:
- Detección de anomalías (cambios masivos, montos altos, borrados raros)
- Reportes periódicos (daily summary WhatsApp, weekly compliance, monthly forensic)
- Forense bajo demanda
- Compliance support (Ley 29733)
- Correlación cross-source (audit + UptimeRobot + Watchtower + alerts)

## Decisiones cerradas en sesión

1. **75% test coverage** (vs mi 70% propuesto)
2. **60 días cold standby** Render post-cutover (vs 30 propuestos)
3. **Sesión auth 48h** (vs 8h propuesta)
4. **8 intentos fallidos** antes de lockout (vs 5)
5. **2 horas inactividad** auto-logout (vs 30 min)
6. **Backfill desde Excel manual** (no Sheets API en MVP) — Opción 1 simple
7. **Datos importados tal cual** (sin limpieza al backfill)
8. **5to agente Infra+Security** programado para cierre Fase 6 (no post-MVP)
9. **Audit log retención forever** (volumen permite)
10. **Render + Sheets + repo formulario-livskin = SOLO LECTURA** absoluto

## Estado del repo al cierre

### ADRs nuevos (5 archivos)
- `docs/decisiones/0023-erp-refactor-flask-strategy.md`
- `docs/decisiones/0024-strangler-fig-render-vps3.md`
- `docs/decisiones/0025-backfill-script-rerunable.md`
- `docs/decisiones/0026-auth-bcrypt-2-cuentas.md`
- `docs/decisiones/0027-audit-log-inmutable.md`

### Archivos modificados
- `.gitignore` (PII protection: `Datos_Livskin_*.xlsx` excluido)
- `CLAUDE.md` (NUNCA TOCAR producción + referencias a memorias)
- `docs/decisiones/README.md` (0023-0027 marked ✅ con descripciones actualizadas)
- `docs/master-plan-mvp-livskin.md` (5to agente + 60 días cold standby + cutover detail)

### Memorias Claude Code nuevas (en `~/.claude/projects/.../memory/`)
- `feedback_production_preservation.md` — regla absoluta de SOLO LECTURA
- `project_real_data_source.md` — exports manuales del Sheets
- `feedback_explain_to_beginner.md` — Dario principiante en implementación
- `project_backfill_decisions.md` — 11 decisiones técnicas del backfill
- `project_infra_security_agent.md` — visión completa del 5to agente (timing actualizado)

### Archivo de data real (gitignored, vive solo local)
- `docs/Datos_Livskin_2026-04-25.xlsx` (88 ventas, 84 pagos, 135 clientes, 55 catálogos)

## Lo que sigue para mañana / próximas sesiones

### Fase 2 — Implementación (ya con 100% definición conceptual)

1. **Crear `infra/docker/erp-flask/`** con estructura modular (ADR-0023)
2. **Migration Alembic `0001_initial_schema.py`** con las 9+ tablas (ADR-0011 v1.1, 0026, 0027)
3. **Implementar models SQLAlchemy** (1 archivo por entidad)
4. **Implementar schemas Pydantic** (request/response validation)
5. **Implementar services** empezando por VentaService (las 6 fases preservadas)
6. **Implementar middleware de auth** (bcrypt + sesiones, ADR-0026)
7. **Implementar middleware de audit** (decorator `@audit`, ADR-0027)
8. **Implementar routes** preservando contract HTTP del Flask actual
9. **Implementar endpoints nuevos** (`/api/client-lookup`, webhooks)
10. **Tests** con coverage ≥75%
11. **Crear `infra/docker/erp-backfill/`** (ADR-0025)
12. **Smoke tests** end-to-end
13. **Deploy a VPS 3 en dormant standby**

### Estimación

Per ADR-0023, refactor estimado en 2-3 semanas. Conservador con principiante en implementación: 3-4 semanas.

## Estadísticas de la sesión

- **5 ADRs MVP escritos** (~50KB total de documentación técnica)
- **5 memorias nuevas** persistentes
- **3 archivos raíz actualizados** (.gitignore, CLAUDE.md, master-plan)
- **10 decisiones estructurales cerradas**
- **1 visión nueva incorporada** (5to agente Infra+Security)
- **0 líneas de código** (esta fue sesión 100% de definición)
- **8/9 ADRs de Fase 2 completos** (solo falta ADR-0018 schema cerebro detallado, no bloquea Fase 2 implementación)

---

**Firma del log:** Claude Code + Dario · 2026-04-25

**Estado cierre**: Definición conceptual de Fase 2 al **100%**. Listo para arrancar implementación en próxima sesión sin necesidad de más decisiones de gobierno.
