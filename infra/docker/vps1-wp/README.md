# VPS 1 — WordPress (livskin-wp)

**IP pública:** 46.101.97.246
**IP privada VPC:** 10.114.0.3
**Hostname:** `Livskin-WP-01`

## Rol

Hosting de **livskin.site** — sitio público con Elementor + SureForms + Complianz.
Stack tradicional **NO dockerizado** (a diferencia de VPS 2 y VPS 3) por:
- Compatibilidad con plugins WP que esperan filesystem real
- Performance de PHP-FPM directo
- Simplicidad operacional para WP (CMS común)

## Stack actual

| Componente | Versión | Cómo verificarlo |
|---|---|---|
| OS | Ubuntu 22.04 | `lsb_release -a` |
| Web server | nginx host | `nginx -v` |
| PHP | 8.1-fpm | `php-fpm -v` |
| DB | MariaDB 10.6 (host) | `mariadb --version` |
| WordPress | 6.9.4 | `head -20 /var/www/livskin/wp-includes/version.php` |
| TLS | Let's Encrypt (certbot) | `certbot certificates` |

## Plugins WordPress activos

| Plugin | Propósito | Fase |
|---|---|---|
| **pixelyoursite** | Meta Pixel + GA4 + GTM client-side | 3 |
| **sureforms** | Formularios con webhook a n8n | 3 |
| **complianz-gdpr** | Consent management (reject-or-accept) | 3 |
| **elementor** + **header-footer-elementor** | Page builder | (ya en uso) |
| **updraftplus** | Backups WP | (ya en uso) |
| **duplicate-page** | Utilitario edición | (ya en uso) |
| ⚠️ **latepoint** | Booking — **NO está en blueprint** — pendiente decisión: mantener / desactivar / desinstalar | TBD |

## Theme activo

**astra** (paid versión) con personalizaciones via Elementor.

## Estructura de directorios versionada

```
vps1-wp/
├── README.md                    # este archivo
├── nginx/
│   └── livskin.conf             # /etc/nginx/sites-available/livskin
├── wp-mu-plugins/               # must-use plugins (custom code)
│   ├── README.md
│   └── (vacío hoy — Fase 3 mete el UTM persistence script aquí)
├── install.sh                   # bootstrap idempotente desde Ubuntu fresca
└── deploy-wp-config.sh          # rsync de configs sin downtime
```

## Configs gestionados por el repo

✅ **Versionado:**
- `/etc/nginx/sites-available/livskin` → `vps1-wp/nginx/livskin.conf`
- `/var/www/livskin/wp-content/mu-plugins/*` → `vps1-wp/wp-mu-plugins/`

⏳ **No versionado (deuda técnica conocida):**
- WordPress core en `/var/www/livskin/` (releases de WP, gestionados por el plugin updater)
- Plugins en `/var/www/livskin/wp-content/plugins/` (instalados por UI, no por código)
- DB MariaDB (backups daily — ver §backups)
- `/etc/letsencrypt/` (certbot maneja él solo, backup en cross-VPS)

## Volumes y backups

| Componente | Backup | Retención | Verificación |
|---|---|---|---|
| Filesystem `/var/www/livskin/` | tarball daily 02:00 | 30 días cross-VPS a VPS 2 | `restore-test` weekly |
| MariaDB `livskin_wp` DB | `mariadb-dump` daily | 30 días cross-VPS | `pg_restore` a temp DB |
| Certbot certs | (auto-renew + cross-VPS) | 90 días renew | `certbot renew --dry-run` cron |

## TLS

Let's Encrypt managed by certbot. Renew cron en `/etc/cron.d/certbot`.
Certs en `/etc/letsencrypt/live/livskin.site/`.

## Setup desde cero (DR)

Ver `docs/runbooks/disaster-recovery-vps1.md`.

Resumen: bootstrap script `install.sh` instala nginx + php-fpm + MariaDB + WP, luego restore de backups.

## Acceso

```bash
ssh -F keys/ssh_config livskin-wp
```

Usuario: `livskin` (sudo NOPASSWD). Root deshabilitado.

## Recursos

- 1GB RAM (apretado para WP — monitorear)
- 25GB disk
- 1 CPU shared
