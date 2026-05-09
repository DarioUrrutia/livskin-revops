---
runbook: agenda-mantenimiento
severity: low
auto_executable: false
trigger:
  - "Doctora reporta problema con pestaña AGENDA"
  - "Endpoint /api/appointments retorna 404 o 5xx"
  - "Cita marcada attended NO creó cliente automaticamente"
required_secrets: []
commands_diagnose:
  - "ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c \"SELECT cod_appointment, status, scheduled_for FROM appointments ORDER BY scheduled_for DESC LIMIT 10;\"'"
  - "ssh livskin-erp 'sudo docker exec erp-flask python -c \"from config import settings; print(settings.agenda_feature_enabled)\"'"
commands_fix: []
commands_verify:
  - "curl -sS -o /dev/null -w '%{http_code}' https://erp.livskin.site/api/appointments"
escalation:
  if_fail: "Si rollback necesario: alembic downgrade -1 + AGENDA_FEATURE_ENABLED=0. La migration 0007 es 100% reversible (DROP TABLE simple)."
related_skills:
  - livskin-ops
---

# Runbook — Mantenimiento del módulo Agenda Mínima (ADR-0035)

> **Propósito:** referencia operacional para diagnosticar y resolver problemas comunes del módulo Agenda en ERP. Implementado en Fase 4A.1 (2026-05-09).

> **Cuándo se ejecuta:** cuando la doctora reporta problemas con la pestaña AGENDA, cuando hay errores 4xx/5xx en `/api/appointments`, o cuando el workflow `mark-attended` no crea cliente automáticamente.

---

## Arquitectura del módulo

```
[UI formulario.html — pestaña AGENDA] (gated por agenda_feature_enabled)
    ↓ fetch
[/api/appointments — Blueprint Flask]
    ↓
[appointment_service.py]
    ↓
[Postgres livskin_erp.appointments]
    ↓
[audit_log eventos appointment.* — inmutable]
```

**Componentes (todos en VPS3):**
- Modelo: `infra/docker/erp-flask/models/appointment.py`
- Service: `infra/docker/erp-flask/services/appointment_service.py`
- Routes: `infra/docker/erp-flask/routes/api_appointments.py`
- Schemas: `infra/docker/erp-flask/schemas/appointment.py`
- Migration: `infra/docker/alembic-erp/migrations/versions/2026_05_09_1200-0007_appointments.py`
- UI: `infra/docker/erp-flask/templates/formulario.html` (sección `tab-agenda`)
- Feature flag: `AGENDA_FEATURE_ENABLED` env var (lee `config.settings.agenda_feature_enabled`)

---

## Estados válidos de una cita

```
[creada]
    │
    ├─→ scheduled (estado inicial al crear)
    │
scheduled
    ├─→ confirmed   (lead/cliente confirmó)
    ├─→ cancelled   (cancela antes del día)
    └─→ rescheduled (cambia fecha → crea nueva, apunta rescheduled_to)

confirmed
    ├─→ attended    (✨ asistió → trigger creación cliente automática)
    ├─→ no_show     (no vino)
    ├─→ cancelled   (canceló a último momento)
    └─→ rescheduled (reagendó tarde)

attended | no_show | cancelled | rescheduled
    └─→ (estados terminales, no más transiciones)
```

---

## Diagnóstico rápido

### 1. ¿Está activo el feature flag?

```bash
ssh livskin-erp 'sudo docker exec erp-flask python -c "from config import settings; print(settings.agenda_feature_enabled)"'
```

- `True` → flag activo, módulo visible.
- `False` → flag apagado, todo el módulo retorna 404. Activar con env var `AGENDA_FEATURE_ENABLED=1` en `infra/docker/postgres-data/.env`.

### 2. ¿Está aplicada la migration 0007?

```bash
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT version_num FROM alembic_version;"'
```

- `0007_appointments` → migration aplicada.
- Cualquier otro valor → aplicar con `bash /srv/livskin-revops/infra/scripts/alembic-erp.sh upgrade head`.

### 3. ¿Existe la tabla appointments?

```bash
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "\d appointments"'
```

Si no existe → migration no aplicada. Aplicar paso 2.

### 4. ¿Hay errores recientes en logs?

```bash
ssh livskin-erp 'sudo docker logs erp-flask --tail 100 | grep -iE "appointment|error|traceback"'
```

### 5. ¿El audit log captura los eventos?

```bash
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT action, COUNT(*) FROM audit_log WHERE action LIKE 'appointment.%' GROUP BY action;"'
```

Las 7 acciones esperadas: `appointment.created`, `appointment.updated`, `appointment.confirmed`, `appointment.marked_attended`, `appointment.marked_no_show`, `appointment.cancelled`, `appointment.rescheduled`.

---

## Casos comunes

### Caso 1 — La doctora marcó "Asistió" pero no se creó cliente

**Diagnóstico:**

```bash
# Ver el appointment
ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT cod_appointment, status, lead_id, cod_cliente, attended_at FROM appointments WHERE cod_appointment='\''LIVAPT0001'\'';"'
```

**Posibles causas:**

1. **El appointment ya tenía `cod_cliente` al crearlo** (era walk-in directo) → comportamiento esperado, no se crea cliente nuevo.
2. **El lead origen tenía phone duplicado en `clientes`** → el service detecta `ClienteDuplicadoError` y vincula al cliente existente (no crea uno nuevo). Verificar:
   ```bash
   ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT id, vtiger_id, phone_e164 FROM leads WHERE id=<lead_id>;"'
   ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT cod_cliente FROM clientes WHERE phone_e164=<phone>;"'
   ```
3. **Lead no encontrado** (FK rota) → revisar logs de erp-flask para `LeadNotFoundError`.

### Caso 2 — Endpoint /api/appointments retorna 404

**Causas:**

1. **Feature flag apagado** → `agenda_feature_enabled=False`. Activar.
2. **Sin sesión** → 404 NO es esperado sin sesión (debería ser 302). Si pasa, hay bug en middleware. Ver logs.

### Caso 3 — UI no muestra pestaña AGENDA

**Causa:** template renderiza `{% if agenda_feature_enabled %}` como False.

**Verificar:**

```bash
ssh livskin-erp 'sudo docker exec erp-flask grep -A1 "agenda_feature_enabled" /app/routes/views.py'
```

Si la variable se pasa al template pero el HTML no la renderiza → posible cache de browser. Hard refresh.

### Caso 4 — Status enum rechazado al insertar

**Síntoma**: `ck_appointments_status_valido` fallando.

Solo permitidos: `scheduled, confirmed, attended, no_show, cancelled, rescheduled`. Si necesita un estado nuevo, agregar a:
1. `models/appointment.py` (`APPOINTMENT_STATUS_VALUES`)
2. Migration nueva con `ALTER TABLE` para extender el CHECK constraint
3. `schemas/appointment.py` (`AppointmentStatus` Literal)
4. UI labels en `formulario.html`

### Caso 5 — Validation 400 al crear cita

**Síntoma**: POST /api/appointments retorna 400 con `validacion fallida`.

**Causas comunes:**
- Falta `cod_lead` Y `cod_cliente` (al menos uno requerido)
- `treatment` vacío
- `scheduled_for` no es ISO8601 timezone-aware
- `duration_min` fuera de [15, 480]

---

## Rollback completo (emergencia)

Si necesitamos quitar el módulo Agenda completo (ej: bug crítico):

```bash
# 1. Apagar feature flag (efecto inmediato — UI desaparece, endpoints 404)
ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/erp-flask && sudo sed -i "s/AGENDA_FEATURE_ENABLED=1/AGENDA_FEATURE_ENABLED=0/" ../postgres-data/.env && sudo docker compose restart erp-flask'

# 2. Si necesitamos rollback DB (solo si migration trajo problemas):
ssh livskin-erp 'bash /srv/livskin-revops/infra/scripts/alembic-erp.sh downgrade -1'
# Esto hace DROP TABLE appointments + DROP indices (operación 100% reversible).

# 3. Si necesitamos volver a una versión anterior del codigo:
ssh livskin-erp 'cd /srv/livskin-revops && git checkout <commit-anterior> && cd infra/docker/erp-flask && sudo docker compose build && sudo docker compose up -d erp-flask'
```

**Importante:** apagar feature flag es preferible a rollback DB. El flag es atómico (~5 segundos), rollback DB requiere downtime.

---

## Tests

### Tests automatizados (CI/local)

```bash
ssh livskin-erp 'sudo docker exec erp-flask pytest tests/services/test_appointment_service.py tests/routes/test_api_appointments.py -v'
```

Esperado: 50 tests passing.

### Smoke test manual

1. Login en `https://erp.livskin.site/`
2. Click pestaña "Agenda"
3. Click "+ Nueva cita"
4. Llenar:
   - Cliente o lead: pegar un `LIVCLIENT####` real existente (o `LIVLEAD####`)
   - Tratamiento: "Test"
   - Fecha: mañana
   - Hora: cualquiera
5. Click "Crear cita" → debería aparecer en la lista
6. Click "Confirmar" → status pasa a "Confirmada"
7. Click "Asistió" → status pasa a "Asistió"
8. Si fue creada con un `cod_lead`, verificar que se creó el cliente:
   ```bash
   ssh livskin-erp 'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "SELECT cod_cliente, nombre, cod_lead_origen FROM clientes ORDER BY id DESC LIMIT 5;"'
   ```

---

## Referencias

- ADR-0035 — Módulo Agenda Mínima en ERP (decisión arquitectónica)
- ADR-0011 v1.1 — Modelo de datos lead-cliente-venta
- ADR-0033 — Match automático lead↔cliente al crear cliente
- ADR-0027 — Audit log inmutable
- Memoria `feedback_surgical_precision_erp.md` — protocolo 8 pasos aplicado
- Memoria `project_agenda_module_erp.md` — decisión Opción B (ERP, no Vtiger)
- Sesión 2026-05-09 — implementación completa Fase 4A.1

---

**Última revisión:** 2026-05-09 (creación tras implementación Fase 4A.1)
