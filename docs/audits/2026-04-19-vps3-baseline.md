# Audit — VPS 3 baseline post-hardening

**Fecha:** 2026-04-19  
**VPS auditado:** `livskin-vps-erp` (139.59.214.7)  
**Tipo:** audit manual + Lynis `--quick` tras hardening inicial (Fase 1)  
**Ejecutado por:** Claude Code  
**Trigger:** provisión + hardening inicial del VPS 3

---

## 1. Contexto

Primer audit del VPS 3 inmediatamente después de aplicar hardening baseline:
- SSH endurecido (sin root, sin password)
- UFW activo (22/80/443 solo)
- Fail2Ban activo (jail sshd + whitelist)
- unattended-upgrades activo
- Docker CE 29.4.0 instalado
- Swap 2GB
- Timezone UTC

Establece la **línea base** para comparar en audits subsiguientes.

---

## 2. Estado del sistema

| Métrica | Valor |
|---|---|
| OS | Ubuntu 22.04.5 LTS |
| Kernel | 5.15.0-171-generic |
| Uptime | 32 min (fresh) |
| RAM total | 1.9 GB (de 2 GB, reservado kernel) |
| RAM en uso | 233 MB (sin containers aún) |
| Swap | 2.0 GB, 0 bytes usados |
| Disco | 50 GB (detalles pendientes de medición) |

## 3. Seguridad (Lynis quick)

| Métrica | Valor |
|---|---|
| **Hardening index** | **65/100** |
| Tests performed | 259 |
| Plugins enabled | 1 |

Interpretación: 65 es baseline aceptable para un VPS productivo con hardening básico. Rango de referencia:
- 50-55: sin hardening
- 60-70: hardening básico (este VPS)
- 75-85: hardening avanzado (+AppArmor, auditd, restricciones adicionales)
- >85: paranoid

Las recomendaciones específicas de Lynis se accionan en Fase 6 (estabilización).

## 4. Servicios activos

| Servicio | Estado |
|---|---|
| `ssh` | active |
| `ufw` | active |
| `fail2ban` | active |
| `unattended-upgrades` | active |
| `docker` | active |

## 5. Firewall (UFW)

**Default:** deny incoming, allow outgoing.

| Rule | Port | Action | Source |
|---|---|---|---|
| 1 | 22/tcp | ALLOW | Anywhere |
| 2 | 80/tcp | ALLOW | Anywhere |
| 3 | 443/tcp | ALLOW | Anywhere |
| 4 | 22/tcp (v6) | ALLOW | Anywhere v6 |
| 5 | 80/tcp (v6) | ALLOW | Anywhere v6 |
| 6 | 443/tcp (v6) | ALLOW | Anywhere v6 |

Puertos DB (5432), embeddings service (8000), etc. **NO expuestos** — quedarán detrás de Docker networks + VPC privado.

## 6. Fail2Ban

| Jail | Bantime | Findtime | Maxretry | Status |
|---|---|---|---|---|
| sshd | 7200s (2h) | 600s (10min) | 3 | enabled |

**Whitelist (ignoreip):** `127.0.0.1/8 ::1 10.114.0.0/20 78.208.67.189`

## 7. Puertos LISTEN externos

```
tcp 0.0.0.0:22         # SSH
tcp 127.0.0.53%lo:53   # systemd-resolved (solo localhost, no expuesto)
tcp [::]:22            # SSH IPv6
```

**Ninguna exposición no-deseada.**

## 8. SSH

| Directiva | Valor |
|---|---|
| PermitRootLogin | no |
| PasswordAuthentication | no |
| PubkeyAuthentication | yes |
| MaxAuthTries | 3 |
| ClientAliveInterval | 300 |
| ClientAliveCountMax | 2 |

Config aplicada via override `/etc/ssh/sshd_config.d/99-livskin-hardening.conf`.

## 9. Usuarios

| Usuario | UID | Grupos | SSH login |
|---|---|---|---|
| root | 0 | root | **BLOQUEADO** (PermitRootLogin no) |
| livskin | 1000 | livskin, sudo, docker | ✅ via key |

`livskin` tiene sudo NOPASSWD via `/etc/sudoers.d/livskin`.

## 10. Docker

- Docker CE 29.4.0 (repo oficial)
- Docker Compose v5.1.3 (plugin)
- containerd instalado
- 0 containers running (aún no desplegamos nada)
- 0 networks custom creadas
- 0 volumes creados

## 11. Conectividad VPC

Verificada con ping a IPs privadas:

| Destino | IP privada | Latencia |
|---|---|---|
| VPS 1 (WP) | 10.114.0.3 | 1.981ms |
| VPS 2 (Ops) | 10.114.0.2 | 1.904ms |

**VPC Frankfurt operativa. Los 3 VPS alcanzables entre sí.**

## 12. Backups

Aún NO configurados (según política ADR-0041: se activan en Fase 2 cuando entre el primer lead real).

Snapshot manual baseline **NO tomado todavía** para VPS 3 — pendiente agregar a backlog.

## 13. Items a mejorar (para atacarse en fase 6)

Lynis suggestions destacadas (las más accionables):
- Instalar AppArmor profiles más estrictos
- Configurar auditd para logging de auditoría
- Restringir lista de SUID/SGID binaries
- Endurecer parámetros sysctl adicionales (ipv4/ipv6 hardening)
- Instalar debsums para verificación de integridad de paquetes

Estas **no bloquean MVP**. Se accionan cuando Hardening index <65 o trimestralmente.

## 14. Siguientes steps del workstream seguridad

- Snapshot manual baseline del VPS 3 pre-Postgres (recomendado antes de Paso siguiente de Fase 1)
- Agregar IP de laptop de trabajo al whitelist Fail2Ban cuando se conozca
- Después de Postgres instalado: reglas UFW específicas para permitir 5432 solo desde VPC privada

---

**Auditor:** Claude Code · **Próxima auditoría automática:** primera del primer día del mes 2026-05-01 (mensual según ADR-0003).
