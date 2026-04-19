# Sesión 2026-04-19 — Fase 1: VPS 3 creado, hardened y data layer deployed

**Duración:** ~5-6 horas (con pausas)  
**Tipo:** ejecución guiada + Claude Code directo (segunda mitad en adelante)  
**Participantes:** Dario (decisora + operadora) + Claude Code  
**Fase del roadmap:** Fase 1 (Semana 2)

---

## Objetivos de la sesión

1. Crear VPS 3 ($12/mo DigitalOcean Frankfurt, 2GB RAM / 50GB SSD)
2. Configurar acceso SSH controlado (Dario primero, Claude Code después)
3. Hardening base: SSH endurecido, UFW, Fail2Ban, unattended-upgrades
4. Instalar Docker + Docker Compose
5. Swap 2GB
6. Verificar VPC connectivity entre los 3 VPS
7. Lynis audit baseline
8. Documentar todo

---

## Lo que se logró

### VPS 3 operativo

| Atributo | Valor |
|---|---|
| Nombre | `livskin-vps-erp` |
| Proyecto DO | Livskin Project |
| Región | Frankfurt FRA1 |
| OS | Ubuntu 22.04.5 LTS |
| Kernel | 5.15.0-171-generic |
| Recursos | 1 vCPU · 2 GB RAM · 50 GB SSD · 2 TB transfer · IPv6 · Monitoring |
| Costo | $12/mes ($0.018/hora) |
| **Public IPv4** | **139.59.214.7** |
| **Private IP VPC** | **10.114.0.4** (en subnet 10.114.0.0/20) |
| IPv6 | 2a03:b0c0:3:f0:0:2:4e1e:c000 |
| Tags | `livskin`, `erp`, `prod` |

### Acceso SSH

| Vía | Key | Uso |
|---|---|---|
| PuTTY (Dario) | `keys/livskin-vps-erp.ppk` (RSA 4096, sin passphrase*) | Acceso primario/soberano |
| Claude Code (yo) | `keys/claude-livskin` (Ed25519) | Operaciones automatizadas |

*Decisión: sin passphrase durante Fase 1-2 por frecuencia alta de conexiones. **Agregar passphrase al cerrar Fase 2** (entrada en backlog 🟡).

**Usuarios en VPS 3:**
- `root`: existe pero SSH login bloqueado (solo acceso indirecto vía `sudo -i`)
- `livskin`: UID 1000, grupo `sudo` + `docker`, sudo NOPASSWD

### Hardening aplicado

| Control | Configuración |
|---|---|
| **SSH** | PermitRootLogin no · PasswordAuth no · PubkeyAuth yes · MaxAuthTries 3 · ClientAlive 300/2 |
| Archivo config | `/etc/ssh/sshd_config.d/99-livskin-hardening.conf` (override, resistente a updates) |
| **UFW** | Default deny incoming, allow outgoing. Permitidos: 22, 80, 443 (TCP) |
| **Fail2Ban** | Jail `sshd`, 3 intentos/10min → ban 2h via UFW banaction |
| Whitelist Fail2Ban | 127.0.0.1/8, ::1, 10.114.0.0/20, 78.208.67.189 (Dario Milan) |
| **unattended-upgrades** | Activo, diario, solo security updates |
| **Swap** | 2GB /swapfile, swappiness=10, persistido en fstab |
| **Timezone** | UTC |

### Docker instalado

| Componente | Versión |
|---|---|
| Docker CE | 29.4.0 (repo oficial Docker) |
| Docker Compose | v5.1.3 (plugin) |
| containerd | instalado |
| buildx | instalado |

### VPC connectivity confirmada

| Origen → Destino | IP privada | Latencia promedio |
|---|---|---|
| VPS 3 → VPS 1 (WP) | 10.114.0.4 → 10.114.0.3 | **1.98ms** |
| VPS 3 → VPS 2 (Ops) | 10.114.0.4 → 10.114.0.2 | **1.90ms** |

Los 3 VPS están en el mismo VPC Frankfurt (10.114.0.0/20). DO VPC verificada operativa.

### Lynis audit inicial

- **Hardening index:** 65/100
- Tests performed: 259
- Baseline aceptable para Fase 1. Recomendaciones específicas se accionan en Fase 6 (estabilización).

---

## Incidentes y aprendizajes

### Incidente 1: Auto-ban de Claude Code por Fail2Ban

**Qué pasó:** al aplicar Paso E (enable UFW), mi conexión SSH se dropeó momentáneamente. Mi cliente SSH retry automático fue visto por Fail2Ban como "3 intentos fallidos en 10 min" → mi IP `78.208.67.189` quedó baneada por 2h.

**Diagnóstico:** ping a 139.59.214.7 funcionaba (ICMP allowed), pero TCP 22 timeout → clásica signature de Fail2Ban banaction=ufw.

**Resolución:** desde PuTTY de Dario (conexión pre-establecida, no afectada por ban):
```bash
sudo fail2ban-client set sshd unbanip 78.208.67.189
# + creación de /etc/fail2ban/jail.d/ignoreip.local con whitelist permanente
sudo fail2ban-client reload
```

**Lección aprendida:** al enable UFW en un VPS donde hay sesión SSH activa con auto-retry, agregar whitelist a Fail2Ban ANTES del UFW enable. Para futuras sesiones con VPS nuevos, agregar ignoreip como paso previo al activate de Fail2Ban. Queda documentado.

### Incidente 2: Tags no se aplicaron al crear el droplet

Dario siguió el checklist pero los tags `livskin`, `erp`, `prod` no quedaron registrados al Create. Resuelto manualmente con "Edit tags" en el panel DO post-creación. Tampoco crítico.

---

## Decisiones derivadas

1. **ADR-0004 (DO VPC)** → pasa de aprobada conceptual a **implementada y verificada**
2. **Nombre final VPS 3:** `livskin-vps-erp` (hostname) + alias SSH `livskin-erp`
3. **Subnet VPC confirmada:** 10.114.0.0/20 (10.114.0.2-3-4 asignadas a los 3 VPS)
4. **Fail2Ban ignoreip list** documentada como parte del baseline de seguridad (ADR-0003 debería actualizarse)
5. **Claude Code puede operar directamente** en VPS 3 tras validación manual inicial por Dario

---

## Pendiente (queda para próxima sesión o fases siguientes)

### Fase 1 (lo que falta antes de Fase 2)

- [ ] Instalar Postgres 16 + pgvector extension
- [ ] Crear DBs `livskin_erp` y `livskin_brain` con usuarios app
- [ ] Desplegar container `embeddings-service` (multilingual-e5-small)
- [ ] Nginx + Cloudflare DNS para `erp.livskin.site` + `erp-staging.livskin.site`
- [ ] Cloudflare Origin Cert wildcard para VPS 3
- [ ] GitHub Actions CI/CD (push → deploy automático a VPS 3)
- [ ] Alembic configurado (esqueleto)
- [ ] Staging environment (docker-compose-staging.yml + subdomain)
- [ ] Agregar IP de la laptop de Dario (oficina) al whitelist de Fail2Ban

### Pendientes de la usuaria

- [ ] Cargar crédito en Anthropic console + generar API key
- [ ] API key fal.ai
- [ ] Instalar Bitwarden + guardar `keys/.env.integrations`
- [ ] Crear Meta App + WhatsApp test number (sigue pendiente, no bloqueante para Fase 1-2)
- [ ] Iniciar trámite WhatsApp Business API producción

---

---

## Parte 2 — Data layer (Postgres + pgvector + embeddings service)

Continuación en la misma sesión, tras snapshot baseline del VPS 3.

### Snapshot baseline tomado

Snapshot manual `livskin-vps-erp-baseline-post-hardening-2026-04-19` tomado en DO panel antes de iniciar deploys. Punto de retorno limpio si algo sale mal en las próximas 1-2 semanas. Programado para borrar cuando Fase 1 esté estable (backlog entry).

### Postgres 16 + pgvector desplegado

- Container `postgres-data` (imagen oficial `pgvector/pgvector:pg16`)
- Volumen persistente `postgres-data-vol`
- Puerto 5432 **NO expuesto al host ni internet** — solo accesible dentro de `data_net`
- Init scripts aplicados en primera creación:
  - `01-roles.sh`: 4 roles con least privilege (erp_user, analytics_etl_reader, brain_user, brain_reader)
  - `02-databases.sh`: DBs `livskin_erp` y `livskin_brain` con owners y grants correctos
  - `03-brain-schema.sh`: pgvector + pgcrypto extensiones + 6 tablas del cerebro (clinic_knowledge, project_knowledge, conversations, creative_memory, learnings, embedding_runs) con 5 índices HNSW para búsqueda semántica
- Passwords generadas con `openssl rand -hex 24` (192 bits de entropía), guardadas en `/srv/livskin/postgres-data/.env` (perms 600, owner livskin, nunca commitear)

Verificaciones pasadas:
- 5 DBs listadas (postgres, template0, template1, livskin_erp, livskin_brain)
- 3 extensiones en livskin_brain: plpgsql, vector 0.8.2, pgcrypto 1.3
- 6 tablas del cerebro con brain_user como owner
- 5 índices HNSW creados
- 4 roles app con login=t

### Embeddings service desplegado

- Container `embeddings-service` (imagen propia `livskin/embeddings-service:multilingual-e5-small`)
- FastAPI + sentence-transformers
- Modelo `intfloat/multilingual-e5-small` (384 dims, multilingüe)
- Modelo bakeado en build time → runtime rápido
- En red `data_net`, NO expuesto al host

Endpoints:
- `GET /health` → estado
- `POST /embed` → genera embedding(s) con prefijo `query` o `passage`

### Nginx reverse proxy + TLS público

**Paralelo al data layer**, se desplegó también el reverse proxy público del VPS 3.

**DNS agregado en Cloudflare:**
- `erp.livskin.site` → 139.59.214.7 (Proxied) ✅
- `erp-staging.livskin.site` → 139.59.214.7 (Proxied) ✅

**Nginx container `nginx-vps3` (imagen nginx:stable) desplegado:**
- Ports 80 + 443 expuestos al host
- TLS terminación con Cloudflare Origin Cert wildcard (reutilizado de VPS 2, válido hasta 2041)
- HTTP → HTTPS redirect
- Security headers: HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- Staging con `X-Robots-Tag: noindex,nofollow`
- Catch-all 444 para hosts desconocidos (bloquea bots de escaneo)
- Log format incluye `CF-Connecting-IP` (IP real cliente tras Cloudflare, no la de CF)

**Maintenance pages** en `/var/www/prod` y `/var/www/staging`. Cuando se despliegue ERP Flask en Fase 2, se cambia el bloque `location /` por `proxy_pass http://erp-flask:5000`.

**Verificación end-to-end desde internet:**

```
curl -sI https://erp.livskin.site
→ HTTP/1.1 200 OK
→ Server: cloudflare
→ + todos los security headers

curl -sI https://erp-staging.livskin.site
→ HTTP/1.1 200 OK
→ + X-Robots-Tag: noindex, nofollow, noarchive

curl -sI http://erp.livskin.site
→ HTTP/1.1 301 Moved Permanently → https://erp.livskin.site/
```

La usuaria puede abrir `https://erp.livskin.site` en navegador y ver la página de maintenance con branding Livskin.

---

### Test end-to-end verificado ✅

**Pipeline completo funcionando:**

```
Python client → embeddings-service:8000/embed
                  (genera vector 384-dim multilingual-e5-small)
              → psycopg2 INSERT en clinic_knowledge con pgvector
              → SELECT con operador <=> (cosine distance)
                  + índice HNSW para ordenamiento semántico
```

**Test ejecutado:**
1. Embebió 2 passages clínicos (botox frente, hialurónico ojeras)
2. Insertó en `livskin_brain.clinic_knowledge` con embeddings 384-dim
3. Query semántica: "¿cuánto dura el botox en frente?"
4. Resultados por similitud coseno:

| Passage | Similitud | ¿Match correcto? |
|---|---|---|
| botox_frente ("Botox frente/entrecejo, 4-6 meses, S/.550") | **0.8943** | ✅ Sí — match semántico |
| hialuronico_ojeras ("Ác. hialurónico para ojeras, S/.1600") | 0.8070 | correctamente menor |

**Diferencia de 9 puntos** entre el match correcto y el incorrecto — retrieval quality sólido. El modelo `multilingual-e5-small` entiende español técnico (botox, tratamiento, precio, frente) sin problema.

**Cleanup:** test data eliminada post-verificación, `clinic_knowledge` de vuelta vacía.

Este es el momento donde el **segundo cerebro de Livskin empezó a existir operativamente**. Desde aquí escalamos a poblar L1 (catálogo completo), L2 (indexación del repo), MCP server, y eventualmente L4 (conversaciones WhatsApp) en Fase 4.

### Estructura en VPS 3 al cierre de Fase 1 parte 2

```
/srv/livskin/
├── postgres-data/
│   ├── docker-compose.yml
│   ├── .env              [gitignored, perms 600]
│   └── init/
│       ├── 01-roles.sh
│       ├── 02-databases.sh
│       └── 03-brain-schema.sh
├── embeddings-service/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── docker-compose.yml
└── nginx/
    ├── docker-compose.yml
    ├── nginx.conf
    ├── sites/
    │   ├── 00-default.conf
    │   ├── erp.livskin.site.conf
    │   └── erp-staging.livskin.site.conf
    ├── html/
    │   ├── prod/index.html
    │   └── staging/index.html
    └── certs/
        ├── livskin-origin.crt
        └── livskin-origin.key  (perms 600)

Containers running:
- postgres-data       (pgvector/pgvector:pg16)       healthy
- embeddings-service  (livskin/embeddings-service)   healthy
- nginx-vps3          (nginx:stable, ports 80+443)   healthy

Networks:
- data_net (bridge, external)

Volumes:
- postgres-data-vol
```

### Decisiones importantes de esta parte

- **Passwords aleatorios hex 48 chars en lugar de base64** — evita caracteres `/=+` que pueden complicar connection strings/escaping.
- **Init scripts como `.sh` no `.sql`** — bash permite expansión de env vars para passwords sin hardcodear en SQL.
- **Puertos DB no expuestos al host** — aislamiento por Docker network; acceso cross-VPS pendiente configurar reglas UFW VPC cuando se conecte n8n (VPS 2 → VPS 3).
- **Modelo de embeddings bakeado en imagen** — reproducibilidad total; re-build si se cambia de modelo.

---

## Commits derivados de esta sesión

1. `feat(vps3): provisioning + hardening VPS 3 livskin-vps-erp` (commit 6961f61)
2. `feat(vps3): data layer — Postgres 16 + pgvector + embeddings service`  
   Incluye: infra/docker/postgres-data/, infra/docker/embeddings-service/, actualización backlog, session log, audit follow-up.

---

## Referencias

- [docs/master-plan-mvp-livskin.md](../master-plan-mvp-livskin.md)
- [docs/decisiones/0002-arquitectura-de-datos-y-3-vps.md](../decisiones/0002-arquitectura-de-datos-y-3-vps.md)
- [docs/decisiones/0003-seguridad-baseline-y-auditorias.md](../decisiones/0003-seguridad-baseline-y-auditorias.md)
- [docs/audits/2026-04-19-vps3-baseline.md](../audits/2026-04-19-vps3-baseline.md)

---

**Firma del log:** Claude Code + Dario · 2026-04-19
