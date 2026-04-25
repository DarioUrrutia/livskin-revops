# ADR-0027 — Audit log inmutable (tabla append-only para trazabilidad)

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-25
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos + Seguridad

---

## 1. Contexto

El ERP actual del Render no tiene **trazabilidad**: no se sabe quién registró cada venta, quién modificó qué cliente, quién intentó loguearse y falló. Esto es:

- Riesgo de seguridad (no se puede investigar incidentes)
- Riesgo de compliance (Ley 29733 Perú requiere control de acceso a PII demostrable)
- Riesgo operativo (si algo sale mal, no hay forma de "rebobinar" la historia)
- Bloqueo para futuro Agente Infra+Security (memoria `project_infra_security_agent`) que necesita esta data para detectar anomalías

ADR-0026 estableció auth con users diferenciados; este ADR establece cómo se **traza cada acción** que esos users realizan.

Referencias:
- ADR-0011 v1.1 (modelo de datos — define tabla `audit_log`)
- ADR-0023 (refactor ERP — define middleware/audit como capa)
- ADR-0026 (auth — define eventos de auth a auditar)
- Memoria `project_infra_security_agent` (futuro consumidor del audit log)

---

## 2. Opciones consideradas

### Opción A — Tabla append-only en Postgres + middleware automático (RECOMENDADA)
Tabla `audit_log` en Postgres con permisos restringidos (INSERT only desde app, SELECT solo para admin). Middleware del ERP escribe automáticamente en cada operación CRUD significativa. Schema rico (before/after/context). Dashboard admin para consultar con filtros y búsqueda.

### Opción B — Logs estructurados a archivo + agregador externo (Loki, Elasticsearch)
Logs a stdout/file, recolectados por agregador (Loki, Elasticsearch), consultables vía Grafana/Kibana.

### Opción C — Triggers de Postgres directos (sin middleware app)
Triggers `AFTER INSERT/UPDATE/DELETE` en cada tabla operativa que escriben a `audit_log` automáticamente.

### Opción D — Logging mínimo (solo eventos críticos)
Solo logear auth events + delete events. Resto sin auditoría.

---

## 3. Análisis de tradeoffs

| Dimensión | A (tabla + middleware) | B (logs externos) | C (Postgres triggers) | D (mínimo) |
|---|---|---|---|---|
| Complejidad implementación | Media | Alta (setup agregador) | Baja | Muy baja |
| Cero infrastructure adicional | **Sí** | No (Loki/Grafana = +1 servicio) | Sí | Sí |
| Captura "user_id" del request | **Sí** (middleware tiene contexto) | Sí (si se pasa al log) | **Difícil** (Postgres no sabe quién hace request) | Limitado |
| Captura "before/after" semántico | **Sí** | Sí | **Limitado** (delta crudo, no semántico) | No |
| Inmutabilidad | **Sí** (permisos DB) | Depende de retention | Sí | No |
| Queryable con SQL estándar | **Sí** | Vía API agregador | Sí | No estándar |
| Adecuado para forense rápida | **Sí** | Sí | Limitado | No |
| Costo | $0 | $0-30/mes (Loki self-hosted) o más | $0 | $0 |
| Alineación con stack existente | **Excelente** (Postgres ya está) | Distinto stack adicional | Bueno | Insuficiente |
| Útil para Agente Infra+Security futuro | **Excelente** (queryable directamente) | Bueno (vía API) | Limitado | No |

---

## 4. Recomendación

**Opción A — Tabla append-only en Postgres + middleware automático.**

Razones:
1. **Cero infraestructura adicional**: usa el Postgres que ya tenemos
2. **Captura contexto rico**: middleware sabe quién, qué, cuándo, antes/después; triggers de Postgres no
3. **Queryable con SQL**: vos o el futuro Agente Infra pueden hacer queries complejas sin aprender otra herramienta
4. **Inmutable de verdad**: permisos DB garantizan que ni vos podés borrar entradas
5. **Adecuado a tu volumen**: con tu volumen actual (~88 ventas/2 meses), el log crece ~10MB/año → trivial para Postgres décadas

**Tradeoff aceptado**: el middleware tiene que recordar escribir el audit en cada operación. Mitigación: tests verifican que cada operación CRUD genere su entrada esperada (coverage ≥75%, ADR-0023). Si una operación olvida auditar, los tests fallan.

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-25 por Dario con todas mis 6 recomendaciones.

**Razonamiento de la decisora:**
> "Tomaré tus recomendaciones, teniendo en cuenta que estas eliminarán fricciones en la implementación. Recuerda que estas cosas forman parte de mi agente, al menos las capacidades de ayudarme con estos temas."

(Las 6 decisiones se desglosan en § 6.)

---

## 6. Diseño técnico

### 6.1 Las 6 decisiones técnicas validadas

| # | Decisión | Aprobada |
|---|---|---|
| 1 | **Eventos a registrar**: ~30 tipos (auth + venta + pago + gasto + cliente + lead + admin + webhooks) | ✅ |
| 2 | **Información por entrada**: who/when/what/before/after/context/result | ✅ |
| 3 | **Inmutabilidad absoluta**: nadie (ni admin) puede UPDATE o DELETE entradas | ✅ |
| 4 | **Retención**: para siempre (storage no es problema con volumen Livskin) | ✅ |
| 5 | **Visibilidad**: solo admins (vos), operadoras NO ven el log | ✅ |
| 6 | **Dashboard admin**: `/admin/audit-log` con filtros + búsqueda + export CSV | ✅ |

### 6.2 Schema de la tabla `audit_log`

```sql
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Quién
    user_id         BIGINT REFERENCES users(id),     -- NULL si fue webhook externo o sistema
    user_username   TEXT,                             -- desnormalizado (snapshot — user puede renombrarse)
    user_role       TEXT,                             -- snapshot del rol al momento del evento
    
    -- Qué
    action          TEXT NOT NULL,                    -- 'venta.created', 'auth.login_success', etc.
    category        TEXT NOT NULL,                    -- 'auth', 'venta', 'pago', 'gasto', 'cliente', 'lead', 'admin', 'webhook'
    entity_type     TEXT,                             -- 'venta', 'cliente', etc. (NULL si auth)
    entity_id       TEXT,                             -- 'LIVVENTA0089' o similar
    
    -- Cambio (cuando aplica)
    before_state    JSONB,                            -- estado antes del cambio (NULL si es create)
    after_state     JSONB,                            -- estado después del cambio (NULL si es delete)
    
    -- Contexto del request
    ip              INET,
    user_agent      TEXT,
    session_id      BIGINT REFERENCES user_sessions(id),
    request_id      TEXT,                             -- correlation ID del request (para tracing)
    
    -- Resultado
    result          TEXT NOT NULL DEFAULT 'success',  -- 'success' o 'failure'
    error_detail    TEXT,                             -- descripción si result=failure
    
    -- Metadata adicional flexible
    metadata        JSONB                              -- campo libre para info extra (ej: {affected_rows: 3})
);

-- Índices
CREATE INDEX idx_audit_occurred ON audit_log(occurred_at DESC);
CREATE INDEX idx_audit_user ON audit_log(user_id, occurred_at DESC);
CREATE INDEX idx_audit_action ON audit_log(action, occurred_at DESC);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id, occurred_at DESC);
CREATE INDEX idx_audit_category ON audit_log(category, occurred_at DESC);

-- GIN index para búsqueda en JSON (queries complejas tipo "todas las ventas con total > 1000")
CREATE INDEX idx_audit_after_state_gin ON audit_log USING gin(after_state);
CREATE INDEX idx_audit_before_state_gin ON audit_log USING gin(before_state);
```

### 6.3 Inmutabilidad — implementación

**Capa 1: Permisos a nivel DB**

```sql
-- El usuario que la app usa para conectar (erp_user) tiene:
GRANT SELECT, INSERT ON audit_log TO erp_user;
-- NO se otorga UPDATE ni DELETE.

-- Solo el usuario admin de DB (postgres_superuser) podría modificar,
-- pero ese usuario NO se usa desde el ERP — solo para mantenimiento manual.
```

**Capa 2: Trigger defensivo (extra seguridad)**

```sql
CREATE OR REPLACE FUNCTION audit_log_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log es inmutable — UPDATE/DELETE no permitidos';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_audit_modification
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW
    EXECUTE FUNCTION audit_log_immutable();
```

Doble protección: aunque alguien manipule permisos por error, el trigger los rechaza.

### 6.4 Lista canónica de eventos auditables (~30 tipos)

#### Auth (7 eventos)
| Action | Cuando |
|---|---|
| `auth.login_success` | Login exitoso |
| `auth.login_failed` | Username/password incorrectos |
| `auth.lockout_triggered` | 8mo intento fallido |
| `auth.logout_voluntary` | Click en "logout" |
| `auth.logout_inactivity` | Auto-logout por 2h sin actividad |
| `auth.password_changed` | Usuario cambió su password |
| `auth.password_reset_by_admin` | Admin reseteó password de otro user |

#### Venta (3 eventos)
| Action | Cuando |
|---|---|
| `venta.created` | POST /venta exitoso (las 6 fases) |
| `venta.updated` | UPDATE de venta existente (rare en MVP) |
| `venta.deleted` | DELETE (sin endpoint expuesto en MVP, solo via SQL admin) |

#### Pago (3 eventos)
- `pago.created`, `pago.updated`, `pago.deleted`

#### Gasto (3 eventos)
- `gasto.created`, `gasto.updated`, `gasto.deleted`

#### Cliente (3 eventos)
| Action | Cuando |
|---|---|
| `cliente.created` | Nuevo cliente registrado |
| `cliente.updated` | Modificación de datos cliente |
| `cliente.merged` | Merge tras dedup (ADR-0013 v2) |

#### Lead (5 eventos)
| Action | Cuando |
|---|---|
| `lead.created` | Lead nuevo (form o WA) |
| `lead.score_updated` | Conversation Agent ajustó score |
| `lead.handoff_to_doctora` | Score ≥70, escalado a doctora |
| `lead.converted` | Lead → Cliente al primera venta |
| `lead.discarded` | Marcado como `perdido` |

#### Admin (4 eventos)
| Action | Cuando |
|---|---|
| `admin.user_created` | Nuevo usuario del sistema |
| `admin.user_deactivated` | Desactivación de usuario |
| `admin.config_changed` | Modificación de configs sensibles |
| `admin.dedup_resolved` | Admin resolvió un dedup_candidate |

#### Webhooks externos (2 eventos)
| Action | Cuando |
|---|---|
| `webhook.form_submit_received` | Form de landing page recibido |
| `webhook.whatsapp_received` | Mensaje WA Cloud API recibido |

**Total: 30 tipos de eventos canónicos.** Lista extensible (cuando aparezca evento nuevo, se agrega aquí + se documenta en cambio de ADR).

### 6.5 Eventos que NO se auditan

Para evitar ruido excesivo:

- ❌ `GET /` (carga del formulario)
- ❌ `GET /api/dashboard`, `/api/libro`, `/api/config` (consultas read-only)
- ❌ `GET /cliente?cod=X` (lookup, no modifica)
- ❌ `GET /api/client-lookup` (es lookup AJAX, alta frecuencia)
- ❌ `/ping`, `/static/*`
- ❌ Health checks

**Trade-off**: si en el futuro queremos saber "quién consultó el historial de Carmen", no tenemos esa info. Aceptable porque:
1. Volume sería 100x mayor sin valor proporcional
2. Compliance Ley 29733 se enfoca en mutaciones, no consultas (en general)
3. Si necesitamos auditar consultas en futuro, agregamos categoria `query.*` selectivamente

### 6.6 Implementación del middleware

**Decorator `@audit`**:

```python
@audit(action='venta.created', entity_type='venta')
def create_venta(data):
    # ... lógica del service
    return new_venta
```

El decorator:
1. Captura `before_state` si es update (lee el registro antes)
2. Ejecuta la función
3. Captura `after_state` (resultado)
4. Toma user_id, role, ip, user_agent, session_id del request context
5. INSERT en `audit_log` (en la misma transacción que la operación)
6. Si la operación falla → registra con `result='failure'` y `error_detail`

**Para auth events** (que no encajan en CRUD):

```python
def login(username, password):
    # ... lógica
    audit_log.write(
        action='auth.login_success',
        user_id=user.id,
        category='auth',
        result='success',
        metadata={'session_id': session.id}
    )
```

### 6.7 Dashboard `/admin/audit-log`

**Pantalla con filtros**:

```
┌─────────────────────────────────────────────────────────┐
│ Audit Log                                               │
├─────────────────────────────────────────────────────────┤
│ Usuario: [Todos ▼]  [Dario]  [Doctora]  [Sistema]       │
│ Categoría: [Todas ▼] [Auth] [Venta] [Pago] [Cliente]    │
│ Fecha: [Desde] _____ [Hasta] _____  [Aplicar]           │
│ Buscar: [_______________________]                       │
│                                              [Export CSV]│
├─────────────────────────────────────────────────────────┤
│ 2026-05-15 14:32:11  Dario   venta.updated   LIVVENTA0089│
│   total: 700 → 650, descuento: 0 → 50                   │
│   IP: 78.208.67.189                          [Ver más]  │
├─────────────────────────────────────────────────────────┤
│ 2026-05-15 14:30:00  Doctora venta.created   LIVVENTA0089│
│   {cliente: "Carmen", total: 700, ...}                  │
│   IP: 167.99.X.X                              [Ver más] │
├─────────────────────────────────────────────────────────┤
│ ... (paginated, 50 entries por página)                  │
└─────────────────────────────────────────────────────────┘
```

**Búsqueda full-text** sobre `before_state` y `after_state` JSONs:

Ej: query SQL para "todas las ventas modificadas con total > 1000":

```sql
SELECT * FROM audit_log
WHERE action = 'venta.updated'
  AND (before_state->>'total')::numeric > 1000
ORDER BY occurred_at DESC;
```

### 6.8 Performance considerations

**Crecimiento estimado**:
- ~88 ventas/mes + ~84 pagos + ~10 clientes nuevos + leads cuando arranque digital
- Por evento: ~1KB promedio (JSONs son pequeños)
- Volumen mensual: ~200KB hoy, ~5MB cuando arranque digital
- 10 años: ~600MB → trivial para Postgres

**Sin necesidad de**:
- Particionamiento (por ahora)
- Archivado a storage frío (volumen es bajo)
- Compresión especial (Postgres TOAST maneja JSONB)

**Si en algún punto crece >10GB**: considerar particionamiento por año.

---

## 7. Capacidades del Agente Infra+Security relacionadas con audit log

(Per memoria `project_infra_security_agent` — capacidades acumulándose conforme aparecen)

El agente, cuando se construya en cierre de Fase 6, usará el audit log para:

### Detección de anomalías
- **Login patterns sospechosos**: múltiples failed logins en corto tiempo, logins desde IPs nuevas, logins fuera de horario habitual
- **Cambios masivos**: si en 1h hay >20 ventas modificadas (cuando el promedio es 0-2), alerta
- **Modificaciones a montos altos**: si una venta de S/.5,000 se modifica, alerta inmediata
- **Borrados inusuales**: cualquier delete (que en MVP no debería pasar via UI) → alerta crítica

### Reportes periódicos
- **Daily summary**: resumen diario por WhatsApp ("Hoy 5 ventas, 1 modificación, 2 logins, todo OK")
- **Weekly compliance**: reporte de cumplimiento Ley 29733 ("Acceso a PII de 12 clientes esta semana, todos por usuarios autorizados")
- **Monthly forensic**: tendencias mensuales, comparación vs mes anterior

### Respuesta a queries forenses de Dario
- "¿Quién modificó esta venta el mes pasado?" → query rápido
- "¿La doctora hizo algo raro la semana pasada?" → análisis de su actividad
- "Necesito reporte de TODO lo que pasó el 15 de marzo" → export filtered

### Compliance support
- Generar reportes de "acceso a PII" para Ley 29733 si auditoría externa lo pide
- Detectar y alertar PII potencialmente expuesta (logs sin sanitizar, exports de DB)

### Integration con el resto del agente
- Audit log es UNO de los inputs del agente (junto con monitoring de Watchtower, UptimeRobot, alertas de n8n)
- El agente correla eventos: "alerta de UptimeRobot + spike en login_failed = posible ataque DDoS coordinado"

---

## 8. Consecuencias

### Desbloqueado
- ERP refactorizado tiene trazabilidad completa desde día 1
- Compliance Ley 29733 con evidencia demostrable
- Forense rápida ante incidentes
- Conversation Agent (Fase 4) puede consultar audit log para context (ej: "¿hubo cambio reciente en este cliente?")
- Agente Infra+Security (Fase 6) tiene su input principal de eventos
- Dario puede investigar "qué pasó" sin conjeturas

### Bloqueado / descartado
- Opción D (logging mínimo) descartada — no soporta compliance ni forense
- Opción B (Loki/Elasticsearch) descartada — overhead de stack adicional sin beneficio claro
- Lectura del audit log para operadoras descartada (solo admin)
- Borrado del audit log descartado (inmutabilidad absoluta)

### Implementación derivada
- [ ] Migration Alembic: tabla `audit_log` con permisos restringidos + trigger de inmutabilidad
- [ ] Implementar `middleware/audit.py` con decorator `@audit`
- [ ] Aplicar decorator a todos los services de creación/modificación (ventas, pagos, gastos, clientes, leads)
- [ ] Auth events: agregar `audit_log.write(...)` en login/logout/lockout/password change
- [ ] Webhook events: registrar en cada `/webhook/*` recibido
- [ ] Dashboard `/admin/audit-log` con filtros (UI + endpoints)
- [ ] Export CSV
- [ ] Tests: verificar que cada operación CRUD genera SU entry esperada (test cover gap = bug)
- [ ] Documentar en `erp-flask/README.md`: lista canónica de eventos + cómo consultar

### Cuándo reabrir
- Si volumen crece >100GB → particionar tabla
- Si compliance externa requiere export en formato específico (XML, JSON-LD, etc.)
- Si surge necesidad de auditar también lecturas (queries) — agregar `query.*` events
- Si Agente Infra+Security demanda formato distinto de eventos (improbable, JSON es flexible)
- Revisión obligatoria: 2026-07-25

---

## 9. Changelog

- 2026-04-25 — v1.0 — Creada y aprobada (MVP Fase 2). Cierra la **5ta y última** de las ADRs huérfanas (0023-0027). Incorpora capacidades preliminares del Agente Infra+Security que consumirá el audit log como input principal.
