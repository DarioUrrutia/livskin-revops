# Seguridad — Documentos operativos

Esta carpeta contiene políticas y runbooks operativos de seguridad. El **dossier maestro** está en [docs/decisiones/0003-seguridad-baseline-y-auditorias.md](../decisiones/0003-seguridad-baseline-y-auditorias.md).

## Documentos

| Archivo | Contenido | Estado |
|---|---|---|
| `security-policy.md` | Política consolidada, para referencia operativa rápida | ⏳ Fase 0 (deriva de ADR-0003) |
| `access-control-matrix.md` | Quién tiene acceso a qué | ⏳ Fase 0 |
| `password-policy.md` | Requisitos passwords, rotación, almacenamiento | ⏳ Fase 0 |
| `incident-classification.md` | P0/P1/P2/P3 con ejemplos y SLA | ⏳ Fase 0 |
| `data-classification.md` | PII / confidencial / interno / público | ⏳ Fase 3 |

## Runbooks relacionados

Ver [docs/runbooks/](../runbooks/) para procedimientos ejecutables:

- `incident-response-template.md`
- `key-rotation.md`
- `patient-data-supression.md` (Ley 29733)
- `vps-hardening-checklist.md`
- `monthly-audit.md`
- `backup-restore-test.md`

## Ver también

- [ADR-0003](../decisiones/0003-seguridad-baseline-y-auditorias.md) — dossier autoritativo
- [docs/audits/](../audits/) — outputs de auditorías programadas
