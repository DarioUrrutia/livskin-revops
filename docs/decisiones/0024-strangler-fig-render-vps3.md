# ADR-0024 — Estrategia de migración: Strangler Fig (clone + parallel standby + cutover on-demand)

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-25
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2 (preparación) + Fase 6 (ejecución del cutover)
**Workstream:** Datos + Infra

---

## 1. Contexto

El sistema actual (`formulario-livskin.onrender.com`) es producción real usado por Dario y la doctora todos los días para registrar ventas, pagos y gastos. Cualquier interrupción de servicio o pérdida de funcionalidad rompe la operativa de la clínica → revenue real perdido + frustración del equipo.

El sistema nuevo (`erp.livskin.site` en VPS 3) está siendo construido en paralelo con el refactor descrito en ADR-0023.

La pregunta crítica de este ADR es: **¿cómo migramos del viejo al nuevo sin romper producción?**

**Constraints duros**:
- Render NO se puede modificar durante toda la migración (memoria `feedback_production_preservation`)
- Comerciales (Dario + doctora) NO deben sufrir interrupciones largas (>1h sería disruptivo)
- Datos NO se pueden perder en la transición
- Si algo falla post-cutover, debe haber camino de regreso (rollback) sin data corruption

Referencias:
- ADR-0023 (qué se refactoriza)
- ADR-0025 (cómo se carga la data — siguiente)
- Memorias `project_cutover_strategy`, `feedback_production_preservation`, `project_real_data_source`
- Master plan § 11.8 (Fase 6 hito de cutover)

---

## 2. Opciones consideradas

### Opción A — Strangler Fig: clone + parallel standby + cutover on-demand (RECOMENDADA)
Sistemas viejo y nuevo conviven en paralelo durante Fases 2-5. Render mantiene producción real, VPS 3 está dormant (testeado pero sin tráfico). En Fase 6, cuando Dario apruebe explícitamente, se ejecuta cutover controlado en ventana de ~15 minutos. Render queda 60 días en cold standby como rollback path. No hay sync bidireccional durante el período de coexistencia (riesgo de conflicts).

### Opción B — Big bang switch
Apagar Render un día específico, prender VPS 3 mismo día, comerciales migran inmediatamente. Sin overlap.

### Opción C — Strangler con dual-write
Durante coexistencia, cada operación de comerciales se escribe a AMBOS sistemas (Render Sheets + VPS 3 Postgres). Cutover trivial (ya están sincronizados).

### Opción D — Migración progresiva por módulos
Migrar una funcionalidad a la vez. Por ejemplo: primero solo "Gasto" → testear → después "Pagos" → etc. Comerciales usan partes en cada sistema según la función.

---

## 3. Análisis de tradeoffs

| Dimensión | A (clone + standby) | B (big bang) | C (dual-write) | D (progresivo) |
|---|---|---|---|---|
| Riesgo de pérdida de servicio | **Bajo** | Alto | Bajo | Medio (cambios de UX gradual) |
| Riesgo de data corruption | **Bajo** | Medio | Alto (conflicts en dual-write) | Medio |
| Complejidad implementación | Baja-media | Baja | **Alta** (modificar Render = NO permitido) | Alta (router que decide) |
| Tiempo de "ventana de bloqueo" | ~15 min | 0 min (sincrónico) | 0 min | 0 min |
| Capacidad de rollback | **Alta** (Render intacto 60 días) | Baja (sin sistema viejo activo) | Media | Baja (estado mixto) |
| Modificación a Render requerida | Ninguna ✅ | Apagarlo | **Sí** ❌ (viola `feedback_production_preservation`) | No |
| UX comerciales | **Sin cambios hasta cutover** | Cambio brusco | Sin cambios | Confusión gradual |
| Adecuación a Livskin (clínica chica, 2 usuarios) | **Excelente** | Riesgoso | Sobre-engineered | Sobre-engineered |
| Alineación memoria `feedback_production_preservation` | ✅ | ✅ | ❌ | ✅ |

---

## 4. Recomendación

**Opción A — Strangler Fig: clone + parallel standby + cutover on-demand.**

Razones:
1. **Cero modificaciones a Render** durante toda la migración → respeta `feedback_production_preservation` integralmente
2. **Riesgo de data corruption mínimo** → no hay sync bidireccional que pueda generar conflicts
3. **Rollback robusto** → Render sigue corriendo intacto 60 días, listo para usarse si algo falla en VPS 3
4. **Ventana de bloqueo aceptable** (~15 min) → comerciales reciben aviso 48h antes y aceptan el corto inconveniente
5. **Implementación simple** → no requiere routers complejos, ni dual-write, ni triggers especiales en Render

**Tradeoff aceptado**: durante el período de coexistencia (Fases 2-5), VPS 3 trabaja con un snapshot de data que va envejeciendo respecto a Render. Eso lo aceptamos porque al cutover hacemos un export fresco del Sheets (ADR-0025) y la data se actualiza al instante. La drift durante desarrollo es irrelevante (no es producción).

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-25 por Dario.

**Razonamiento de la decisora:**
> "Decidido por mí cuándo hacer el cutover, secuencia de 7 pasos OK, 60 días de cold standby, plan de rollback OK, solo la doctora y yo usamos el sistema."

---

## 6. Diseño de la migración

### 6.1 Período de coexistencia (Fases 2-5, semanas 3-8)

**Render** (producción real):
- Sigue corriendo sin cambios
- Comerciales lo usan diariamente
- Sheets DB sigue acumulando ventas/pagos reales
- Cero modificaciones de código, deploys, env vars (memoria `feedback_production_preservation`)

**VPS 3 — `erp.livskin.site`** (dormant standby):
- ERP refactorizado corriendo (ADR-0023)
- Postgres con copia de data (snapshot del Sheets, ADR-0025)
- Solo accesible para Dario via auth (ADR-0026)
- NO recibe tráfico de comerciales
- Se puede actualizar la copia de data las veces que sea necesario (Dario hace export fresco, corre backfill)

**No hay sync entre los sistemas** — son independientes durante este período.

### 6.2 Pre-requisitos para que Dario apruebe el cutover

Antes de que Dario apruebe el "go" del cutover, deben cumplirse:

- ✅ Sistema completo end-to-end funcionando con data sintética (Fases 2-5 cerradas)
- ✅ Vos personalmente has probado: registrar venta, registrar pago, registrar gasto, ver dashboard, ver historial cliente, exportar libro
- ✅ Tests automatizados pasando (coverage ≥75% per ADR-0023)
- ✅ Backfill script ejecutado en dry-run al menos 2-3 veces sin errores
- ✅ Smoke tests pasan contra el ERP en VPS 3
- ✅ Auth funcionando (login con tu user + login con doctora)
- ✅ Audit log capturando movimientos
- ✅ Conversation Agent + Vtiger funcionando (para que el bridge digital→físico esté completo)
- ✅ Backups daily de Postgres VPS 3 verificados

**El trigger del cutover es decisión 100% de Dario** — no hay timeline forzado, no hay automatic deadline.

### 6.3 Secuencia operativa del cutover (día D)

Tabla de los 7 pasos:

| Tiempo | Acción | Quién la hace |
|---|---|---|
| **T-48h (2 días antes)** | Aviso a la doctora vía WhatsApp: "El [día] a las [hora] hacemos el cambio al sistema nuevo. Va a haber una ventana corta (15 min) donde no podrás registrar nada. Te aviso cuando esté listo." | Dario |
| **T-2h** | Export fresco del Sheets a Excel (.xlsx) | Dario (5 min, mismo proceso del 2026-04-25) |
| **T-1h** | Subir el Excel a `docs/Datos_Livskin_<fecha>.xlsx` y ejecutar backfill script en modo `--apply` (ADR-0025) contra Postgres VPS 3 | Claude Code (con Dario supervisando) |
| **T-30min** | Smoke tests automáticos: 10-15 verificaciones rápidas (login funciona, dashboard carga, totales coinciden con Excel, etc.) | Claude Code |
| **T-15min** | Aviso final a la doctora: "Estamos arrancando el cutover. NO registres ventas en los próximos 15 minutos. Te aviso cuando puedas usar el nuevo URL." | Dario |
| **T-0 (cutover)** | Comerciales empiezan a usar `erp.livskin.site` (login con sus credenciales nuevas). Render sigue corriendo pero ya nadie le entra | Dario + doctora |
| **T+0 a T+72h** | Monitoreo intensivo. Cualquier problema se atiende inmediato | Dario + Claude Code |

**Ventana total de bloqueo de operación**: ~15 minutos (T-15min a T-0).

### 6.4 Cold standby de Render (60 días post-cutover)

Durante 60 días después del cutover, **Render sigue corriendo** sin modificaciones:
- No deploys
- No cambios
- No queries a su Sheets
- Disponible 100% como rollback path

**Por qué 60 días** (no 30, no 90):
- 30 días puede ser corto si bugs aparecen tarde por uso de funcionalidad poco frecuente (ej: cierre de mes)
- 90 días es overhead innecesario una vez confirmada estabilidad
- 60 días captura ciclos típicos de uso mensual + buffer de seguridad

**Costo del cold standby**:
- Render free tier: $0/mes (no hay costo)
- Si tuviera plan pago: ~$7-25/mes según plan — aceptable como seguro

### 6.5 Plan de rollback (qué hacer si algo se rompe)

**Triggers de rollback**:
- Bug crítico que impide registrar ventas (>30 min sin solución)
- Pérdida de datos detectada
- Performance grave (queries >5s consistentemente)
- Cualquier issue que la doctora reporte como blocker

**Procedimiento de rollback** (estimado <30 min):

1. **Dario decide** (no Claude Code) si activar rollback
2. **Dario avisa a la doctora**: "Detectamos un problema, volvé a usar `formulario-livskin.onrender.com` por ahora"
3. **Comerciales vuelven a Render** (sigue corriendo, sin cambios) — empiezan a registrar ventas ahí
4. **Claude Code analiza el bug** en VPS 3, lo arregla
5. **Tests + smoke tests** validan el fix
6. **Datos registrados en VPS 3 durante la ventana de bug**:
   - Si <5 ventas: se re-registran manualmente en Render
   - Si más: script de exportación VPS 3 → re-import a Sheets (manual y cuidadoso, supervisión Dario)
7. **Repetir cutover** cuando esté listo nuevamente: nuevo export del Sheets → backfill → smoke → cutover

**Tradeoff aceptado**: rollback puede implicar pérdida de algunas ventas registradas en VPS 3 durante la ventana de bug. Mitigación: detección rápida + ventana corta. Para Livskin (volumen bajo), data fix manual es manejable.

### 6.6 Comunicación al equipo

**Equipo que usa el ERP**: solo Dario + doctora. Nadie más.

**Canal de comunicación**: **WhatsApp** (directo, lo usan ambas).

**Mensajes clave durante el cutover**:

- **T-48h**: "Hola doctora! Te aviso que este [día] a las [hora] cambiamos al sistema nuevo del ERP. Va a haber 15 min donde no vas a poder registrar ventas, así que organizate. Cuando esté listo te paso la nueva URL. Es básicamente igual al actual, no cambia nada visualmente."

- **T-15min**: "Doctora, ahora SÍ vamos a hacer el cambio. Por favor no registres ventas en los próximos 15 min. Te aviso cuando esté arriba."

- **T-0**: "Listo doctora! Ya podés usar el sistema nuevo. La URL es: erp.livskin.site. Tu usuario es [doctora_username] y la contraseña es la que te di antes. Si algo no funciona, avisame de inmediato."

- **T+24h**: "Doctora, ¿todo bien con el sistema nuevo? ¿Notaste algo raro? Cualquier cosa avísame."

### 6.7 Decisión post-60-días (apagar Render o no)

Después de 60 días limpios sin issues, Dario decide:

**Opción A — Apagar Render**:
- Pros: simplifica el stack, no hay sistema "fantasma" mantener
- Cons: si hay un disaster meses después, no hay sistema viejo para volver
- Cómo: cancel del Render service + descarga final del Sheets + archivado

**Opción B — Mantener Render indefinidamente (free tier)**:
- Pros: redundancia + acceso a Sheets viejo si se necesita lookup histórico
- Cons: ningún costo monetario en free tier; cero overhead operativo
- Cómo: dejar como está, no tocar

**Recomendación**: **Opción B** mientras siga en free tier (cero costo, cero riesgo). Decisión Dario en su momento.

---

## 7. Consecuencias

### Desbloqueado
- Estrategia clara de cómo se ejecuta el cambio
- ADR-0025 (backfill) sabe contra qué se ejecuta y cuándo
- Master plan § 11.8 ya tiene los 7 pasos del cutover (actualizar de "30 días" a "60 días")
- Comunicación al equipo tiene templates de WhatsApp listos

### Bloqueado / descartado
- NO se hace dual-write durante coexistencia (descarta Opción C)
- NO se modifica Render durante coexistencia (memoria `feedback_production_preservation`)
- NO hay automatic timeline para cutover (decisión humana, Dario)

### Implementación derivada
- [ ] Script de smoke tests post-cutover (Fase 2 implementación)
- [ ] Documentar procedimiento de cutover en `docs/runbooks/cutover-render-to-vps3.md` (Fase 6)
- [ ] Documentar procedimiento de rollback en `docs/runbooks/rollback-vps3-to-render.md` (Fase 6)
- [ ] Backups daily de Postgres VPS 3 funcionando antes del cutover
- [ ] Dry-run del cutover completo antes del real (con data sintética, en staging)
- [ ] Templates de WhatsApp pre-escritos para los 4 mensajes a la doctora
- [ ] Master plan § 11.8 update: "30 días cold standby" → "60 días cold standby"

### Cuándo reabrir
- Si se decide agregar usuarios nuevos al ERP (escalar más allá de 2): revisar capacidad
- Si Render desaparece (cierra el free tier o cancela el plan): acelerar cutover sin standby
- Si bug grave aparece post-60-días: extender standby hasta resolución
- Revisión obligatoria al T+30 días post-cutover: ¿algún issue? ¿extender standby?

---

## 8. Changelog

- 2026-04-25 — v1.0 — Creada y aprobada (MVP Fase 2). Cierra la 2da de las 5 ADRs huérfanas (0023-0027). Cold standby ajustado de 30 a 60 días por preferencia de Dario.
