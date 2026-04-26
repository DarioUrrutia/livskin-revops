# Backups — sistema cross-VPS de Livskin (Bloque 0.5)

Estrategia de backups daily verificados, diseñada para que el agente IA pueda
operarla autónomamente y para soportar disaster recovery (DR) sin pérdida
de data crítica.

## Componentes a respaldar

| Componente | VPS origen | Método | Destino | Retención | Verificación |
|---|---|---|---|---|---|
| `livskin_wp` (MariaDB) | livskin-wp | mariadb-dump | livskin-ops `/srv/backups/vps1/` | 30 días | restore a temp DB + count check |
| `/var/www/livskin/` (filesystem) | livskin-wp | tarball | livskin-ops `/srv/backups/vps1/` | 30 días | tar -tf integridad |
| `livskin_db` (Vtiger MariaDB) | livskin-ops | mariadb-dump | livskin-erp `/srv/backups/vps2/` | 30 días | restore a temp DB |
| `analytics + metabase` (Postgres) | livskin-ops | pg_dump | livskin-erp `/srv/backups/vps2/` | 30 días | pg_restore --schema-only |
| `livskin_erp + livskin_brain` (Postgres) | livskin-erp | pg_dump | livskin-ops `/srv/backups/vps3/` | 30 días | pg_restore + count |
| `n8n workflows + sqlite` | livskin-ops | tarball | livskin-erp `/srv/backups/vps2/` | 30 días | tar -tf |

## Estructura de directorios destino

```
/srv/backups/
├── vps1/
│   ├── livskin_wp-2026-04-26.sql.gz
│   ├── livskin_wp-2026-04-25.sql.gz
│   └── wordpress-files-2026-04-26.tar.gz
├── vps2/
│   ├── livskin_db-2026-04-26.sql.gz
│   ├── analytics-2026-04-26.sql.gz
│   └── n8n-data-2026-04-26.tar.gz
└── vps3/
    ├── livskin_erp-2026-04-26.sql.gz
    └── livskin_brain-2026-04-26.sql.gz
```

## Cadencia

- **Daily 02:00 UTC**: `backup-all.sh` (incluye dump + transfer cross-VPS)
- **Daily 04:00 UTC**: `verify-all.sh` (restore a temp + count + reporte)
- **Daily 05:00 UTC**: `cleanup-old.sh` (borra >30 días)

## Verificación automática

Cada backup se verifica restaurándolo a una DB temporal y comparando counts
con la original. Si:
- ✅ counts coinciden → evento `infra.backup_verified` en audit_log
- ⚠️ diff <1% → evento `infra.backup_verified` con metadata.warning
- ❌ diff >1% o restore falla → evento `infra.backup_failed` + alerta

## Cross-VPS transfer

Cada VPS tiene una clave SSH específica para hacer rsync hacia el otro.
Las claves están en `/root/.ssh/backup-target` (privilegiado, no checked
in al repo).

Setup:
```bash
# En VPS de origen, generar key:
ssh-keygen -t ed25519 -f /root/.ssh/backup-target -N ""
# Copiar pública al VPS destino:
ssh-copy-id -i /root/.ssh/backup-target.pub backup@<vps-destino>
```

## Scripts

| Script | Corre en | Función |
|---|---|---|
| `backup-vps1.sh` | livskin-wp | dump WP + tar → rsync VPS 2 |
| `backup-vps2.sh` | livskin-ops | dump vtiger-db + analytics + n8n → rsync VPS 3 |
| `backup-vps3.sh` | livskin-erp | dump livskin_erp + livskin_brain → rsync VPS 2 |
| `verify-vps1.sh` | livskin-ops | verifica backups recibidos de VPS 1 |
| `verify-vps2.sh` | livskin-erp | verifica backups recibidos de VPS 2 |
| `verify-vps3.sh` | livskin-ops | verifica backups recibidos de VPS 3 |
| `cleanup-old.sh` | cada VPS | borra `/srv/backups/*/<archivo>` con mtime >30 días |
| `restore.sh` | DR | menu interactivo de restore |

## Audit log integration

Cada operación reporta a `/api/internal/audit-event` en VPS 3:
- `infra.backup_started`
- `infra.backup_completed`
- `infra.backup_verified`
- `infra.backup_failed`
- `infra.backup_cleanup_completed`

Esto permite consultas como:
- "¿Cuándo fue el último backup verificado de livskin_erp?"
- "¿Hubo backups fallidos esta semana?"

## Recovery (DR)

Ver `docs/runbooks/disaster-recovery-vps[1|2|3].md` para procedure detallado.

Resumen:
1. Crear droplet nuevo en DO
2. `bash install.sh` (idempotente)
3. `bash restore.sh --backup=<file>` o automated
4. Verificar smoke tests
5. DNS cutover en Cloudflare si aplica
