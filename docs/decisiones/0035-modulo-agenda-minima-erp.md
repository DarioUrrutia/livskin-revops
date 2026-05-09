# ADR-0035 — Módulo Agenda Mínima en ERP

**Estado:** ✅ Aprobada · ✅ **IMPLEMENTADA 2026-05-09 (Fase 4A.1)**
**Fecha:** 2026-05-05
**Fecha de aprobación:** 2026-05-05 por Dario (cita: "OK APROBADO")
**Fecha de implementación:** 2026-05-09 (sesión Fase 4A.1, branch `feat/agenda-module-4a1`)
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 4A — Bloque puente backbone determinístico (post-Bridge Episode)
**Workstream:** Datos · ERP · Adquisición operativa

> **Histórico de implementación:**
> - **2026-05-05 (1er intento)**: 12 archivos escritos sin preflight-cross-system → ELIMINADOS por D1 de Dario.
> - **2026-05-09 (rebuild correcto)**: implementación completa con preflight estricto + protocolo de precisión quirúrgica + 50 tests passing + feature flag default OFF. Migration 0007 aplicada en producción. Runbook `docs/runbooks/agenda-mantenimiento.md` creado.

---

## 1. Contexto

**Problema.** Hoy el ERP tiene un agujero en el funnel operativo entre `lead capturado` y `venta registrada`. La doctora lleva las citas en su cabeza y las anota cuando la persona viene físicamente. Esto rompe varias cosas:

1. **Métricas reales del embudo imposibles** — no podemos calcular `lead → cita → asistencia → cliente` porque las dos columnas del medio no existen como data.
2. **Server-side CAPI no puede emitir `Schedule` ni `CompleteRegistration`** — eventos clave de Meta Ads para optimización de campaña.
3. **Match automático de ADR-0033 funciona solo en el momento de cobrar** — no sabe si la cita ocurrió, si fue no-show, si se reagendó.
4. **UI confunde lead vs cliente** (hallazgo smoke E2E 2026-05-02 PM): un lead que tiene cita pero todavía no asistió aparece como "cliente" o no aparece en ningún lado. La doctora no tiene una pantalla "próximas citas" para mañana.
5. **Doctora no puede simular el flujo via UI**: durante el smoke E2E se descubrió que la única forma de mover un lead → cita → asistencia → venta era inyectando SQL. Esto bloquea la doctora cuando quiere cerrar manualmente una operación.

**Decisión arquitectónica previa (memoria `project_agenda_module_erp.md`, 2026-04-26).** Se evaluaron 3 opciones y se eligió Opción B — Agenda en ERP. Este ADR formaliza esa decisión + define schema y endpoints concretos.

**Modelo operacional REAL (sin cambios respecto a ADR-0033):**
- Vtiger gestiona el lead lifecycle de marketing (Dario opera Vtiger)
- ERP gestiona cliente operacional + ventas (la doctora opera ERP)
- El lead llega a Vtiger via form/WhatsApp; la doctora contacta por su WhatsApp/llamada
- **NUEVO con este ADR**: cuando el lead acepta venir, se crea una `appointment` en ERP. Cuando la doctora atiende, se marca asistencia → trigger automático crea cliente + dispara matching ADR-0033.

**Referencias:**
- Memoria `project_agenda_module_erp.md` — decisión Opción B (2026-04-26)
- Memoria `feedback_surgical_precision_erp.md` — protocolo 8 pasos
- Memoria `project_acquisition_flow.md` — flujo end-to-end con event_id
- Memoria `project_attribution_chain_event_id.md` — event_id como hilo conductor
- Memoria `project_vtiger_erp_sot.md` — Vtiger=lead, ERP=cliente+operativo
- ADR-0011 v1.1 — modelo de datos lead-cliente-venta
- ADR-0033 — match automático lead↔cliente al crear cliente
- Backlog `docs/backlog.md` — sección "Bloque puente Agenda Mínima ERP"

---

## 2. Opciones consideradas

### Opción A — Agenda vive en Vtiger (rechazada en 2026-04-26)

Vtiger tiene módulo "Calendar" nativo. Se podrían crear `Vtiger Activity` con tipo "Meeting" para cada cita.

**Por qué rechazada:**
- La doctora NO abre Vtiger diariamente (solo Dario lo opera)
- Vtiger no es accesible desde el móvil de la doctora vía la UI de ERP
- Crear sync ERP↔Vtiger calendar agrega fragilidad innecesaria
- Vtiger 8.2 community tiene limitaciones en su Calendar API

### Opción B — Agenda vive en ERP (elegida en 2026-04-26, formalizada en este ADR)

Tabla `appointments` en Postgres ERP. Nueva pestaña "AGENDA" en formulario.html. Endpoints CRUD aislados. Workflow `mark-attended` dispara creación automática de cliente + match ADR-0033.

### Opción C — Agenda inferida de mensajes WhatsApp (rechazada en 2026-04-26)

Un parser de mensajes de la doctora detectaría cuando agenda algo ("nos vemos mañana 4pm") y crea `appointments` automáticamente.

**Por qué rechazada:**
- Frágil (NLP no determinístico en producción)
- Viola Principio Operativo #11 (deterministic backbone first)
- Requiere integración WhatsApp Business API + chatbot — ambas en Fase 4

---

## 3. Análisis de tradeoffs

| Dimensión | Opción A (Vtiger) | Opción B (ERP) ✅ | Opción C (NLP WA) |
|---|---|---|---|
| UX doctora | Cero (no usa Vtiger) | Alta (ya usa ERP) | Cero (transparente) |
| Determinismo | Alto | Alto | Bajo |
| Implementación | Medio (Vtiger API) | Medio (FastAPI/Flask) | Alto (NLP + chatbot) |
| Mantenimiento | Frágil sync | Mantenible | Difícil de debuggear |
| Tiempo | 4-6h | 4-6h | 12-20h |
| Reversibilidad | Difícil | Fácil (Alembic downgrade) | N/A |
| Portfolio value | Bajo | Alto (módulo completo) | Medio |
| Alineación principios | Mediano | Alto (deterministic + observable + simple) | Bajo (#11 violado) |

---

## 4. Recomendación

**Opción B — Agenda en ERP** porque:

1. **Doctora ya opera ERP** diariamente (es su SoT operativo). Cero adopción adicional.
2. **Determinístico** (Principio #11): cita es row de DB, no inferencia de modelo IA.
3. **Cierra el agujero del funnel** end-to-end: lead → appointment → cliente → venta → pago.
4. **Habilita CAPI Schedule + CompleteRegistration** server-side automáticamente al crear/marcar appointments.
5. **Pre-requisito explícito de Fase 4** (Conversation Agent): el bot tendrá tool `erp_create_appointment`. Sin Agenda construida, el bot no puede operar.

**Tradeoff principal que aceptamos:** dejamos pasar la oportunidad de "Agenda transparente vía NLP" (Opción C). Esa optimización vendría con grandes costos de complejidad y no determinismo. Mejor: empezar con UI explícita determinística, y si en un futuro queremos agregar NLP-assist, va sobre la base ya construida.

---

## 5. Decisión

**Elección:** Opción B — Tabla `appointments` en ERP + UI dedicada + endpoints aislados.

**Fecha de aprobación:** _(pendiente — Dario revisa este ADR)_

---

## 6. Schema de la tabla `appointments`

```sql
-- Migration Alembic 0007 (próximo número disponible)

CREATE TABLE appointments (
    id              BIGSERIAL PRIMARY KEY,
    cod_appointment TEXT       NOT NULL UNIQUE,           -- LIVAPT0001 (formato LIVAPT####, generado en backend)

    -- Referencias (al menos una requerida)
    lead_id         BIGINT     REFERENCES leads(id),     -- NULL si la cita se crea directo en ERP sin lead origen (walk-in)
    cod_cliente     TEXT       REFERENCES clientes(cod_cliente),  -- NULL hasta que se marque asistida (entonces se crea cliente)
    vtiger_lead_id  TEXT,                                -- redundante con leads.vtiger_id pero útil para auditing

    -- Datos de la cita
    treatment       TEXT       NOT NULL,                 -- valor del catálogo de tratamientos
    scheduled_for   TIMESTAMPTZ NOT NULL,                -- fecha + hora de la cita
    duration_min    INTEGER    NOT NULL DEFAULT 60,      -- duración estimada
    status          TEXT       NOT NULL DEFAULT 'scheduled',  -- enum (ver más abajo)
    channel         TEXT,                                -- canal donde se acordó: 'whatsapp', 'phone', 'walk_in', 'form_web'
    notes           TEXT,                                -- texto libre, observaciones operativas

    -- Lifecycle timestamps
    confirmed_at    TIMESTAMPTZ,                         -- cuándo el lead confirmó
    attended_at     TIMESTAMPTZ,                         -- cuándo se marcó "asistió"
    no_show_at      TIMESTAMPTZ,                         -- cuándo se marcó "no_show"
    cancelled_at    TIMESTAMPTZ,                         -- cuándo se canceló
    rescheduled_to  BIGINT     REFERENCES appointments(id),  -- si rescheduled, apunta al nuevo appointment

    -- Auditoría estándar
    created_by      BIGINT     REFERENCES users(id),
    updated_by      BIGINT     REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraint: al menos lead_id O cod_cliente debe existir
    CONSTRAINT appointments_has_subject CHECK (lead_id IS NOT NULL OR cod_cliente IS NOT NULL)
);

-- Índices
CREATE INDEX appointments_scheduled_for_idx     ON appointments (scheduled_for);
CREATE INDEX appointments_status_idx            ON appointments (status);
CREATE INDEX appointments_lead_id_idx           ON appointments (lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX appointments_cod_cliente_idx       ON appointments (cod_cliente) WHERE cod_cliente IS NOT NULL;
CREATE INDEX appointments_status_scheduled_idx  ON appointments (status, scheduled_for);  -- listing "próximas citas"

-- Trigger updated_at
CREATE TRIGGER appointments_updated_at_trigger
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();
```

### Status enum (validado a nivel aplicación, no DB)

```
scheduled    → cita creada, sin confirmar
confirmed    → lead confirmó (vía WA, llamada, o doctora marcó manualmente)
attended     → la persona vino → trigger automático: crea cliente con cod_lead_origen
no_show     → no vino el día acordado
cancelled   → cancelada antes del día
rescheduled → reagendada (rescheduled_to apunta a la nueva)
```

### Reglas de transición de estados

```
[creada]
    │
    ├─→ scheduled (estado inicial)
    │
scheduled
    ├─→ confirmed   (lead confirmó)
    ├─→ cancelled   (cancela antes del día)
    └─→ rescheduled (cambia fecha → crea nueva appointment, apunta rescheduled_to)

confirmed
    ├─→ attended    (✨ asistió → trigger creación cliente)
    ├─→ no_show     (no vino)
    ├─→ cancelled   (canceló a último momento)
    └─→ rescheduled (reagendó tarde)

attended | no_show | cancelled | rescheduled
    └─→ (estados terminales, no más transiciones)
```

---

## 7. Endpoints API

Nuevo blueprint `app/blueprints/appointments.py` (aislado, NO toca rutas existentes):

```
GET    /api/appointments                         Lista paginada con filtros
GET    /api/appointments?status=scheduled        Filtro por status
GET    /api/appointments?from=2026-05-10&to=...  Filtro por rango de fecha
GET    /api/appointments/<cod_appointment>        Detalle
POST   /api/appointments                         Crear (status=scheduled por default)
PATCH  /api/appointments/<cod>                   Update fields (notes, scheduled_for, duration_min)

POST   /api/appointments/<cod>/confirm           Marca confirmed_at + status=confirmed
POST   /api/appointments/<cod>/mark-attended     Trigger crítico (ver workflow abajo)
POST   /api/appointments/<cod>/mark-no-show      Marca no_show_at + status=no_show
POST   /api/appointments/<cod>/cancel            Marca cancelled_at + status=cancelled
POST   /api/appointments/<cod>/reschedule        Crea nueva, apunta rescheduled_to
```

### Workflow del endpoint `/mark-attended`

Es el endpoint con más lógica:

```python
def mark_attended(cod_appointment):
    apt = Appointment.find_by_cod(cod_appointment)

    # 1. Validar transición permitida
    if apt.status not in ('scheduled', 'confirmed'):
        return error("Solo citas scheduled/confirmed se pueden marcar attended")

    # 2. Si el appointment tiene lead_id pero NO cod_cliente → crear cliente
    if apt.lead_id and not apt.cod_cliente:
        lead = Lead.get(apt.lead_id)
        cliente = Cliente.create_from_lead(
            lead=lead,
            attribution_passthrough=True,  # hereda UTMs, fbclid, gclid, vtiger_lead_id, cod_lead_origen
        )
        apt.cod_cliente = cliente.cod_cliente

    # 3. Marcar asistida
    apt.attended_at = now()
    apt.status = 'attended'
    apt.save()

    # 4. Audit log
    audit_log.append(action='appointment.marked_attended', metadata={...})

    # 5. (Futuro Fase 4B) Disparar CAPI CompleteRegistration server-side
    # capi_emitter.fire('CompleteRegistration', cliente=cliente, appointment=apt)

    return apt
```

---

## 8. UI — pestaña "AGENDA" en formulario.html

### Layout propuesto (no implementación final, sketch)

```
┌─────────────────────────────────────────────────────────┐
│ Pestañas: [CLIENTE] [VENTA] [PAGO] [LIBRO] [▸AGENDA◂]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Filtros: [Próximas 7 días ▾] [Todos los status ▾]     │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Mañana 10:00 · Sofia López · Botox  [Confirmar]  │ │
│  │ Mañana 14:30 · Carla Pérez · Hilos  [Confirmar]  │ │
│  │ Pasado 09:00 · Juan Torres · Limpieza · 🟢confirmada [Asistió] [No vino]  │
│  │ ...                                                │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  [+ Nueva cita]                                         │
└─────────────────────────────────────────────────────────┘
```

### Modal "+ Nueva cita"

```
[Buscar lead por nombre/phone/cod_lead]  ← typeahead a /api/leads?search=
   o
[Walk-in directo (sin lead)] ← marcar checkbox

Tratamiento: [dropdown con catálogo]
Fecha: [date picker]
Hora: [time picker]
Duración: [60 min default]
Canal acordado: [whatsapp / phone / walk_in / form_web]
Notas: [textarea]

[Cancelar] [Crear cita]
```

### Botones de acción por appointment row

| Status actual | Botones visibles |
|---|---|
| `scheduled` | [Confirmar] [Reagendar] [Cancelar] |
| `confirmed` | [Asistió] [No vino] [Reagendar] [Cancelar] |
| `attended` | (solo lectura) |
| `no_show` | (solo lectura) [Reagendar nueva fecha] |
| `cancelled` | (solo lectura) |
| `rescheduled` | (link al nuevo appointment) |

---

## 9. Feature flag

```python
# settings.py
AGENDA_FEATURE_ENABLED = bool(int(os.getenv("AGENDA_FEATURE_ENABLED", "0")))
```

- Si `False` → la pestaña AGENDA NO se muestra en formulario.html, endpoints retornan 404
- Si `True` → todo activo
- Default `False` hasta validación con doctora completada (sub-bloque 3.4)

---

## 10. Implementación derivada (sub-bloques 3.2, 3.3, 3.4)

### Sub-bloque 3.2 — Backend (~2h)
- [ ] Migration Alembic 0007 con tabla `appointments` (upgrade + downgrade simétricos)
- [ ] Modelo SQLAlchemy `Appointment`
- [ ] Schemas Pydantic (`AppointmentCreate`, `AppointmentUpdate`, `AppointmentRead`)
- [ ] Service `appointment_service.py` con lógica de transiciones
- [ ] Blueprint `appointments.py` con todos los endpoints
- [ ] Tests pytest TDD (mínimo 15 tests cubriendo: creación, filtros, mark-attended workflow, transiciones inválidas, audit log)
- [ ] Audit log emit en cada acción (`appointment.created`, `appointment.confirmed`, etc.)

### Sub-bloque 3.3 — UI (~1-2h)
- [ ] Pestaña AGENDA en formulario.html (HTML + JS vanilla, alineado con Flask actual)
- [ ] Lista con filtros + auto-refresh cada 60s (opcional)
- [ ] Modal "Nueva cita" con typeahead leads
- [ ] Botones acción por row con confirmación
- [ ] Smoke test manual con datos productivos

### Sub-bloque 3.4 — Validación + cierre (~30-60min)
- [ ] Demo con la doctora: 5 escenarios reales
- [ ] Audit log cubierto + visible en `/admin/audit-log`
- [ ] Feature flag → ON en producción
- [ ] Runbook `docs/runbooks/agenda-mantenimiento.md` con casos comunes + rollback
- [ ] (Futuro Fase 4B) Hook a CAPI Schedule/CompleteRegistration

---

## 11. Consecuencias

### Desbloqueado por esta decisión
- Conversation Agent Fase 4 puede agendar citas vía tool `erp_create_appointment`
- CAPI server-side puede emitir `Schedule` y `CompleteRegistration`
- Métricas reales del funnel `lead → appointment → attended → client → sale`
- Doctora puede manejar todo el flujo desde ERP UI sin SQL manual

### Bloqueado / descartado
- NLP-inferred appointments (Opción C) NO se construye ahora — reabrir solo si volumen lo justifica
- Sync con Vtiger Calendar — descartado, ERP es SoT

### Cuándo reabrir esta decisión
- Si la doctora reporta que la UI de Agenda es ineficiente para su flujo real
- Si Conversation Agent (Fase 4) necesita campos adicionales no contemplados
- Si volumen de citas/día crece y necesitamos vistas tipo calendar (semanal/mensual)

---

## 12. Cambios a ADRs/memoria existentes

- ✅ Memoria `project_agenda_module_erp.md` se mantiene válida (decisión Opción B confirmada en este ADR formal)
- ✅ ADR-0011 v1.1 sigue válida (cliente.cod_lead_origen ya existe — no requiere modificación de schema)
- ✅ ADR-0033 sigue válida (match automático lead↔cliente al cobrar — ahora también se activa al `mark-attended`)

Sin cambios a otros ADRs.

---

## 13. Changelog de esta ADR

- 2026-05-05 — v1.0 — Borrador creado tras pre-flight + lectura de memorias y ADRs relacionados (ADR-0011, ADR-0033, memorias de agenda + acquisition flow + surgical precision)
- 2026-05-05 — Aprobada por Dario ("OK APROBADO"). Implementación arranca con sub-bloque 3.2 una vez resuelta la autorización para tocar `erp/`.
