# Auditorías

Carpeta con outputs de auditorías programadas del sistema.

## Cadencia y naming

| Cadencia | Formato de archivo | Ejemplo |
|---|---|---|
| Mensual (automática) | `YYYY-MM-DD-monthly.md` | `2026-05-18-monthly.md` |
| Trimestral | `YYYY-Qn-security.md` | `2026-Q2-security.md` |
| Anual | `YYYY-annual.md` | `2026-annual.md` |
| Ad-hoc / pre-cambio | `YYYY-MM-DD-<descripción>.md` | `2026-04-18-pre-fase0-baseline.md` |
| Tools específicos | `YYYY-MM-DD-<tool>.md` | `2026-05-18-lynis.md`, `2026-05-18-owasp-zap.md` |

## Subcarpetas

```
docs/audits/
├── supressions/              # solicitudes Ley 29733
│   └── YYYY-MM-DD-<id>.md
├── rotations.md              # log agregado de rotaciones de keys
└── README.md (este)
```

## Ejecución del audit mensual

Desde Claude Code (a implementar en Fase 1):

```bash
# Comando único que audita los 3 VPS y genera el report
bash infra/scripts/monthly-audit.sh
```

Genera archivo en esta carpeta y muestra deltas vs mes anterior.

## Ver también

- [ADR-0003 § 10](../decisiones/0003-seguridad-baseline-y-auditorias.md#10-programa-de-auditorías)
- [docs/seguridad/](../seguridad/)
- [docs/runbooks/monthly-audit.md](../runbooks/) — procedimiento detallado
