# Runbooks — Procedimientos operativos

Procedimientos ejecutables paso-a-paso para operaciones rutinarias y de emergencia.

## Runbooks planeados

### Operaciones rutinarias

| Runbook | Cuándo se ejecuta | Estado |
|---|---|---|
| `monthly-audit.md` | 1 del mes | ⏳ Fase 1 |
| `key-rotation.md` | Trimestral por key, o tras incidente | ⏳ Fase 0 |
| `backup-restore-test.md` | Trimestral | ⏳ Fase 2 |
| `ssl-cert-renewal-check.md` | Pre-expiración | ⏳ Fase 1 |
| `adr-new-decision.md` | Al tomar decisión arquitectónica | ⏳ Fase 0 |
| `session-log-writing.md` | Al cerrar sesión de trabajo | ⏳ Fase 0 |

### Deploys y migraciones

| Runbook | Cuándo | Estado |
|---|---|---|
| `deploy-to-vps.md` | Cada cambio en infra | ⏳ Fase 1 |
| `erp-migration-cutover.md` | Fase 2 única vez | ⏳ Fase 2 |
| `erp-rollback-to-render.md` | Si cutover falla | ⏳ Fase 2 |
| `database-migration-alembic.md` | Cada cambio schema | ⏳ Fase 1 |

### Respuesta a incidentes

| Runbook | Cuándo | Estado |
|---|---|---|
| `incident-response-template.md` | Plantilla para cualquier P0/P1 | ⏳ Fase 0 |
| `vps-down.md` | VPS no responde | ⏳ Fase 1 |
| `database-corruption.md` | Data corrupta detectada | ⏳ Fase 2 |
| `api-key-leaked.md` | Fuga confirmada de credencial | ⏳ Fase 0 |
| `ddos-mitigation.md` | Ataque sostenido detectado | ⏳ Fase 3 |
| `conversation-agent-wrong-response.md` | Agente da respuesta dañina | ⏳ Fase 4 |

### Compliance

| Runbook | Cuándo | Estado |
|---|---|---|
| `patient-data-supression.md` | Paciente pide supresión (Ley 29733) | ⏳ Fase 6 |
| `data-access-request.md` | Paciente pide copia de sus datos | ⏳ Fase 6 |

## Formato de runbook

Cada runbook sigue esta estructura:

```markdown
# Runbook: <Título>

**Cuándo ejecutar:** ...
**Tiempo estimado:** ...
**Pre-requisitos:** ...
**Quién ejecuta:** ...

## Pasos

1. Paso 1 con comando exacto
2. Paso 2
...

## Validación

Cómo verificar que funcionó.

## Si falla

Plan B.

## Registro

Dónde queda evidencia (docs/audits/, docs/sesiones/, etc.)
```

## Ver también

- [docs/decisiones/](../decisiones/) — ADRs que motivan estos runbooks
- [docs/seguridad/](../seguridad/) — políticas marco
- [docs/audits/](../audits/) — outputs de ejecuciones
