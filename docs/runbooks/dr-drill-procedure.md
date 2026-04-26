---
type: dr-drill-procedure
severity: high
authoritative: true
version: 1.0
last_updated: 2026-04-26
description: Procedure para ejecutar disaster recovery drills periódicamente. Valida que los runbooks DR realmente funcionan antes de necesitarlos en una emergencia.
---

# 🎯 DR Drill — Procedure y cadencia

## Por qué hacer drills

Un runbook DR sin probar es teoría. Cuando ocurra el incidente real bajo
presión, vamos a descubrir que el procedure tiene gaps. **Los drills
periódicos descubren esos gaps cuando NO hay urgencia.**

**Principio:** "Si no ejercitas el plan B, no tienes plan B."

## Cadencia recomendada

| Drill | Frecuencia | Razón |
|---|---|---|
| Restore de un backup a temp DB | Mensual | Detecta backups corruptos antes de necesitarlos |
| DR completo de VPS 1 (WP) | Cada 6 meses | Validar install.sh + restore + DNS |
| DR completo de VPS 2 (ops) | Cada 6 meses | El más complejo (4 services) |
| DR completo de VPS 3 (ERP) | Cada 6 meses | El más crítico (data PII) |
| Rollback DO snapshot | Cada 3 meses | Validar workflow CI/CD rollback |
| Credential rotation drill | Cada 3 meses | Practicar runbook credential-leaked |

## Procedure DR drill (genérico)

### Fase 1 — Setup (~10 min)

```bash
# 1.1 Anunciar drill (no production traffic)
echo "DRILL DR — VPS X — $(date -u +%Y-%m-%dT%H:%M)"

# 1.2 Crear droplet temporal de prueba
doctl compute droplet create dr-test-vpsX \
  --region fra1 \
  --image ubuntu-24-04-x64 \
  --size <same-as-prod> \
  --vpc-uuid <vpc-id> \
  --ssh-keys <key-id> \
  --tag livskin,dr-test,disposable \
  --wait

# 1.3 Anotar tiempo inicio
DRILL_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

### Fase 2 — Ejecución del runbook (sin asistencia)

Ejecutar el runbook DR correspondiente AL PIE DE LA LETRA, sin atajos
mentales. Anotar:
- ⏱️ Tiempo de cada paso
- ⚠️ Pasos donde surge confusión / falta info
- 🐛 Bugs en scripts (install.sh, restore commands)
- 📝 Comandos que el runbook asumió pero no documentó

### Fase 3 — Validación

```bash
# 3.1 Smoke tests del servicio recuperado
curl -sI http://<dr-test-ip>/...

# 3.2 Cuenta de filas en DB matchea backup
docker exec dr-postgres psql -c "SELECT COUNT(*) FROM ventas;"  # debe ser X
```

### Fase 4 — Cleanup (~5 min)

```bash
# 4.1 Snapshot DO del droplet de prueba (en caso de querer
# investigar después)
doctl compute droplet-action snapshot <dr-test-id> --snapshot-name "dr-test-snapshot-$DRILL_START"

# 4.2 Borrar droplet (cobra por hora, no acumular)
doctl compute droplet delete <dr-test-id> -f
```

### Fase 5 — Post-mortem

Documentar en `docs/audits/dr-drill-vpsX-<fecha>.md`:

```markdown
# DR Drill VPS X — <fecha>

## Tiempo total: <minutos>
## Target: <minutos del runbook>
## Diff: <+/- minutos>

## Pasos que tomaron más tiempo
- Paso N: causa

## Gaps encontrados
- El runbook no documenta X
- El comando Y falló porque Z
- Falta secret W en .env.example

## Acciones derivadas
- [ ] Update runbook con paso faltante
- [ ] Fix script install.sh línea N
- [ ] Agregar W a .env.example

## Costo
- Droplet temporal: $X (Y horas)
- Total drill: ~$Z
```

## Drill mensual: restore de backup a temp DB

Más liviano que un DR completo, pero crítico para validar que los
backups SIRVEN.

```bash
# 1. Identificar backup más reciente de cada componente
ssh livskin-erp 'ls -t /srv/backups/local/livskin_erp-*.sql.gz | head -1'
# → /srv/backups/local/livskin_erp-2026-04-25.sql.gz

# 2. Restore a DB temporal
ssh livskin-erp 'docker exec postgres-data psql -U postgres -c "CREATE DATABASE drill_$(date +%s);"'
ssh livskin-erp 'gunzip -c /srv/backups/local/livskin_erp-*.sql.gz | head -1 | docker exec -i postgres-data psql -U postgres drill_*'

# 3. Verificar invariantes
docker exec postgres-data psql -d drill_* -c "
  SELECT
    (SELECT count(*) FROM clientes) as c,
    (SELECT count(*) FROM ventas) as v,
    (SELECT count(*) FROM pagos) as p;
"

# 4. Cleanup
docker exec postgres-data psql -U postgres -c "DROP DATABASE drill_*;"
```

## Drill: credential rotation (trimestral)

Ejecutar [credential-leaked](credential-leaked.md) en modo "drill":
- Rotar SSH key (con backup de la vieja en Bitwarden)
- Confirmar todos los workflows GHA siguen funcionando con key nueva
- Tiempo total: <30 min

## Drill: rollback DO snapshot (trimestral)

```bash
# 1. Asegurar snapshot reciente existe
doctl compute snapshot list | grep livskin-vps-erp-pre-deploy

# 2. Hacer un cambio bobo en main (ej: comment en docs)
git commit --allow-empty -m "drill: trigger CI/CD"
git push

# 3. Esperar workflow correr → snapshot creado

# 4. Trigger workflow_dispatch con flag para forzar fallo:
gh workflow run deploy-vps3.yml -f skip_tests=false -f skip_snapshot=false

# 5. (DESTRUCTIVE) tirar el deploy via SSH para forzar rollback:
ssh livskin-erp 'docker stop erp-flask'
# CI/CD verify falla → rollback automático debe activarse

# 6. Verificar:
# - Snapshot DO restaurado (droplet vuelve a estado pre-deploy)
# - URL pública responde nuevamente
# - audit_log tiene infra.deploy_rolled_back

# 7. Si NO se rolleó: bug en workflow → fix
```

⚠️ Esto es un drill destructivo en producción — solo hacer en horarios
de bajo tráfico (madrugada Italia / siesta Cusco).

## Schedule de drills (calendar)

```yaml
drills:
  - name: backup-restore-monthly
    frequency: monthly
    day: 1
    time: 03:00 UTC
    auto: true  # cron lo ejecuta solo
    notify: dario@whatsapp

  - name: dr-vps3-semestral
    frequency: 6-months
    next: 2026-10-26
    auto: false  # requiere humano + autorización
    duration_estimated: 90min

  - name: dr-vps2-semestral
    frequency: 6-months
    next: 2026-10-26
    auto: false
    duration_estimated: 90min

  - name: dr-vps1-semestral
    frequency: 6-months
    next: 2026-10-26
    auto: false
    duration_estimated: 45min

  - name: rollback-trimestral
    frequency: 3-months
    next: 2026-07-26
    auto: true  # workflow GHA lo orquesta

  - name: credential-rotation-trimestral
    frequency: 3-months
    next: 2026-07-26
    auto: false  # requiere humano
```

## Métricas a trackear

- **MTTR (Mean Time To Recovery)** observado en drills vs target del runbook
- **Tasa de drills exitosos** vs fallidos (target: >95%)
- **Acciones derivadas por drill** (target: <3 — más significa runbook frágil)

## Reportes

Cada drill genera evento `infra.dr_drill_completed` en audit_log con:
- runbook_executed
- duration_minutes
- success: true/false
- gaps_found: list[str]
- audit_link: link al post-mortem

Esto permite al 5to agente preguntar:
- "¿Cuándo fue el último DR drill exitoso de VPS 3?"
- "¿Qué runbooks DR nunca se han ejercitado?"
