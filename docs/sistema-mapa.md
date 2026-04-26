---
type: system-map
version: 1.0
last_updated: 2026-04-26
authoritative: true
description: Mapa exhaustivo machine-readable del sistema Livskin. Source of truth para humanos y agentes IA. Indexed en pgvector (brain Layer 2).
---

# 🗺️ Livskin — System Map

> **Para humanos:** este documento describe el sistema completo (VPS, containers, flujos, dependencias, backups, SPOFs).
> **Para agentes IA:** este documento es **autoritativo**. Cuando consultes "¿dónde corre X?" o "¿qué pasa si Y cae?", responde citando esta fuente. Endpoint JSON parseado: `https://erp.livskin.site/api/system-map.json`.

---

## §1 Inventario de VPS

```yaml
vps:
  - alias: livskin-wp
    hostname: Livskin-WP-01
    role: WordPress sitio público
    public_ip: 46.101.97.246
    vpc_ip: 10.114.0.3
    region: fra1
    plan: basic-1gb
    resources:
      cpu: 1 vCPU shared
      ram_mb: 957
      disk_gb: 25
    docker_enabled: false
    repo_path: infra/docker/vps1-wp/

  - alias: livskin-ops
    hostname: livskin-vps-operations
    role: Orquestación + analítica + CRM
    public_ip: 167.172.97.197
    vpc_ip: 10.114.0.2
    region: fra1
    plan: basic-4gb
    resources:
      cpu: 2 vCPU
      ram_mb: 3870
      disk_gb: 78
    docker_enabled: true
    docker_networks: [revops_net, vtiger_internal]
    repo_path: infra/docker/vps2-ops/

  - alias: livskin-erp
    hostname: livskin-vps-erp
    role: ERP + segundo cerebro
    public_ip: 139.59.214.7
    vpc_ip: 10.114.0.4
    region: fra1
    plan: basic-2gb
    resources:
      cpu: 1 vCPU
      ram_mb: 2048
      disk_gb: 50
    docker_enabled: true
    docker_networks: [data_net]
    repo_path: infra/docker/  # paths legacy — ver infra/docker/README.md
```

**Red privada:** DigitalOcean VPC `10.114.0.0/20` (Frankfurt). Latencia inter-VPS <2ms.

---

## §2 Catálogo de containers

```yaml
containers:
  # ===== VPS 1 (no docker, host services) =====
  - name: nginx-host
    vps: livskin-wp
    type: host_service
    binary: /usr/sbin/nginx
    config: /etc/nginx/sites-available/livskin
    repo_path: infra/docker/vps1-wp/nginx/livskin.conf
    listen: [80, 443]
    public_url: https://livskin.site

  - name: php8.1-fpm
    vps: livskin-wp
    type: host_service
    socket: /var/run/php/php8.1-fpm.sock
    document_root: /var/www/livskin
    backup: filesystem-tarball-daily

  - name: mariadb-host
    vps: livskin-wp
    type: host_service
    db: livskin_wp
    user: livskin_user
    backup: mariadb-dump-daily

  # ===== VPS 2 (docker compose) =====
  - name: n8n
    vps: livskin-ops
    image: n8nio/n8n:latest
    network: revops_net
    port_internal: 5678
    public_url: https://flow.livskin.site
    nginx_proxy: vps2-ops/nginx/sites/n8n.conf
    volumes:
      - host: ./n8n/data
        container: /home/node/.n8n
        contents: workflows + sqlite db + credentials
    backup: tarball-daily-cross-vps
    repo_compose: infra/docker/vps2-ops/n8n/docker-compose.yml
    role: orquestador workflows + webhook receiver
    depends_on: []
    impacted_by_failure_of: [nginx-vps2]

  - name: vtiger
    vps: livskin-ops
    image: vtigercrm/vtigercrm-8.2.0:latest
    networks: [revops_net, vtiger_internal]
    port_internal: 80
    public_url: https://crm.livskin.site
    nginx_proxy: vps2-ops/nginx/sites/crm.conf
    volumes:
      - host: ./vtiger/data
        container: /var/www/html
    role: CRM master del lead digital (ADR-0015)
    depends_on: [vtiger-db]
    impacted_by_failure_of: [vtiger-db, nginx-vps2]

  - name: vtiger-db
    vps: livskin-ops
    image: mariadb:10.6
    network: vtiger_internal  # AISLADO — defensa-en-profundidad
    port_internal: 3306
    db: livskin_db
    volumes:
      - host: ./vtiger/db
        container: /var/lib/mysql
    backup: mariadb-dump-daily-cross-vps
    role: DB de Vtiger
    depends_on: []
    impacted_by_failure_of: []

  - name: metabase
    vps: livskin-ops
    image: metabase/metabase:latest
    network: revops_net
    port_internal: 3000
    port_host: 127.0.0.1:3000  # solo loopback
    public_url: https://dash.livskin.site
    nginx_proxy: vps2-ops/nginx/sites/dash.conf
    role: dashboards analítica
    depends_on: [postgres-analytics]
    backend_db: postgres-analytics:metabase
    impacted_by_failure_of: [postgres-analytics, nginx-vps2]

  - name: postgres-analytics
    vps: livskin-ops
    image: postgres:16
    network: revops_net
    port_internal: 5432
    port_host: null  # solo via VPC para metabase + n8n + cross-VPS
    databases:
      - name: analytics
        owner: analytics_user
        purpose: warehouse OLAP (events, leads, opportunities, llm_costs, ads_metrics)
      - name: metabase
        owner: analytics_user
        purpose: backend interno de metabase
    volumes:
      - host: ./postgres-analytics/data
        container: /var/lib/postgresql/data
    backup: pg_dump-daily-cross-vps
    role: warehouse OLAP de Livskin
    depends_on: []
    impacted_by_failure_of: []

  - name: nginx-vps2
    vps: livskin-ops
    image: nginx:stable
    network: revops_net
    listen: [80, 443]
    sites:
      - flow.livskin.site → n8n:5678
      - crm.livskin.site → vtiger:80
      - dash.livskin.site → metabase:3000
    cert_source: cloudflare-origin-cert wildcard *.livskin.site
    role: reverse proxy + TLS termination VPS 2
    depends_on: []
    impacted_by_failure_of: []

  # ===== VPS 3 (docker compose) =====
  - name: postgres-data
    vps: livskin-erp
    image: pgvector/pgvector:pg16
    network: data_net
    port_internal: 5432
    port_host: null  # solo via VPC
    databases:
      - name: livskin_erp
        owner: postgres
        purpose: ERP refactorizado (clientes, ventas, pagos, gastos, audit_log, users, leads, lead_touchpoints)
        critical_invariant: "trigger DEBE dinamico (recompute_venta_debe) recalcula ventas.pagado y ventas.debe automaticamente"
      - name: livskin_brain
        owner: postgres
        purpose: pgvector embeddings (Layer 1-6 del segundo cerebro)
      - name: livskin_erp_test
        owner: postgres
        purpose: tests pytest CI (ephemeral, TRUNCATE between tests)
      tables_critical:
        # Bloque 0.10 — agent resource tracking
        - agent_api_calls (raw events de cada call Claude API, retención 90d)
        - agent_budgets (límites por agente, hard_block_at_limit default true)
        - agent_budget_alerts (dedup state de alertas)
        # Bloque 0.4
        - infra_snapshots (sensors snapshots, retención 30d)
        # ERP core
        - audit_log (49 eventos canónicos, INMUTABLE via trigger PL/pgSQL)
        - clientes, ventas, pagos, gastos (data productiva)
        - users, user_sessions (auth ADR-0026)
      sql_functions:
        - daily_budget_consumed(agent_name) — Bloque 0.10
        - monthly_budget_consumed(agent_name) — Bloque 0.10
        - recompute_venta_debe(cod_item) — trigger DEBE dinámico
        - audit_log_immutable() — trigger anti UPDATE/DELETE
    volumes:
      - host: ./data
        container: /var/lib/postgresql/data
    backup: pg_dump-daily-cross-vps
    role: master de cliente + transacciones (ADR-0015)
    depends_on: []

  - name: erp-flask
    vps: livskin-erp
    image: livskin/erp-flask:latest (built locally)
    network: data_net
    port_internal: 8000
    port_host: 127.0.0.1:8000  # solo loopback
    public_url: https://erp.livskin.site (vía nginx-vps3)
    role: ERP refactorizado Flask + SQLAlchemy + Pydantic + auth + audit
    routes:
      - path: /login, /logout, /change-password (allowlist auth)
      - path: /admin/audit-log (admin only — ADR-0027)
      - path: /admin/system-health (admin only — Bloque 0.4)
      - path: /admin/agent-costs (admin only — Bloque 0.10)
      - path: /api/* (JSON, requires auth)
      - path: /webhook/form-submit (Fase 4)
      - path: /api/internal/audit-event (cross-VPS audit ingest)
      - path: /api/internal/system-state (Bloque 0.4)
      - path: /api/internal/agent-api-call (Bloque 0.10 — wrappers de agentes POSTean acá)
      - path: /api/internal/agent-budget-check (Bloque 0.10 — pre-check budget)
      - path: /api/system-map.json (Bloque 0.3)
      - path: /api/internal/health (Bloque 0.4)
    depends_on: [postgres-data]

  - name: embeddings-service
    vps: livskin-erp
    image: ghcr.io/UKPLab/sentence-transformers (multilingual-e5-small)
    network: data_net
    port_internal: 8001
    role: embeddings server self-hosted ($0)
    depends_on: []

  - name: nginx-vps3
    vps: livskin-erp
    image: nginx:stable
    network: data_net
    listen: [80, 443]
    sites:
      - erp.livskin.site → erp-flask:8000
    cert_source: cloudflare-origin-cert wildcard *.livskin.site
    role: reverse proxy + TLS termination VPS 3

  - name: alembic-erp
    vps: livskin-erp
    type: on-demand
    image: livskin/alembic-erp (built)
    network: data_net
    role: migrations del schema livskin_erp
    invocation: docker compose run --rm alembic-erp upgrade head

  - name: alembic-brain
    vps: livskin-erp
    type: on-demand
    image: livskin/alembic-brain
    network: data_net
    role: migrations del schema livskin_brain (pgvector)

  - name: brain-tools
    vps: livskin-erp
    type: on-demand
    image: livskin/brain-tools
    network: data_net
    role: indexer + query CLI del segundo cerebro
    commands: [index, query]
```

---

## §3 Cross-VPS connections (DO VPC `10.114.0.0/20`)

```yaml
cross_vps_connections:
  - origin: livskin-wp
    target: livskin-ops:n8n
    via: public_internet  # Cloudflare → flow.livskin.site
    port: 443
    protocol: HTTPS
    purpose: SureForms webhook → n8n
    used_in: Fase 3+

  - origin: livskin-ops:n8n
    target: livskin-erp:erp-flask
    via: public_internet  # erp.livskin.site
    port: 443
    protocol: HTTPS
    purpose: Cross-VPS sync (lead → cliente)
    used_in: Fase 3+

  - origin: livskin-ops:metabase
    target: livskin-erp:postgres-data
    via: vpc
    port: 5432
    protocol: postgres
    purpose: queries cross-VPS desde dashboards (read-only)
    used_in: Fase 3+
    requires: pg_hba.conf en livskin-erp acepta conexiones desde 10.114.0.0/20

  - origin: livskin-erp:cron-recolector
    target: livskin-wp:9100
    via: vpc
    port: 9100
    protocol: HTTP
    purpose: pull /api/system-state cada 5 min
    used_in: Bloque 0.4+

  - origin: livskin-erp:cron-recolector
    target: livskin-ops:9100
    via: vpc
    port: 9100
    protocol: HTTP
    purpose: pull /api/system-state cada 5 min

  - origin: github-actions-runner
    target: livskin-erp:22
    via: public_internet
    port: 22
    protocol: SSH
    purpose: deploy CI/CD
    auth: SSH key (secret VPS3_SSH_KEY)

  - origin: github-actions-runner
    target: livskin-ops:22
    via: public_internet
    port: 22
    protocol: SSH
    purpose: deploy CI/CD

  - origin: github-actions-runner
    target: livskin-wp:22
    via: public_internet
    port: 22
    protocol: SSH
    purpose: deploy CI/CD (rsync nginx + mu-plugins)
```

---

## §4 Matriz de dependencias (qué cae si X cae)

```yaml
dependency_matrix:
  - if_down: postgres-data (VPS 3)
    affects:
      - erp-flask (no funciona)
      - tests CI (no corren)
      - cross-VPS queries desde metabase
    severity: critical
    runbook: docs/runbooks/postgres-data-down.md

  - if_down: erp-flask
    affects:
      - https://erp.livskin.site
      - audit log de deploys (no se persiste)
      - sync de leads a clientes
    severity: high
    runbook: docs/runbooks/erp-flask-down.md

  - if_down: postgres-analytics (VPS 2)
    affects:
      - metabase (no carga dashboards)
      - n8n workflows que escriben a analytics.events
      - llm_costs no se persiste
    severity: high
    runbook: docs/runbooks/postgres-analytics-down.md

  - if_down: n8n
    affects:
      - SureForms webhooks no llegan a Vtiger ni a Meta CAPI ni a GA4 MP
      - Meta Pixel client-side sigue funcionando (resilience parcial)
    severity: high
    runbook: docs/runbooks/n8n-down.md

  - if_down: vtiger
    affects:
      - CRM no accesible
      - n8n workflows que crean Lead fallan
      - dependientes en Fase 4 (Conversation Agent escala leads a doctora)
    severity: high
    runbook: docs/runbooks/vtiger-down.md

  - if_down: nginx-vps2 (VPS 2)
    affects: [flow.livskin.site, crm.livskin.site, dash.livskin.site]
    severity: critical
    runbook: docs/runbooks/nginx-down.md

  - if_down: nginx-vps3 (VPS 3)
    affects: [erp.livskin.site]
    severity: critical
    runbook: docs/runbooks/nginx-down.md

  - if_down: nginx-host (VPS 1)
    affects: [livskin.site]
    severity: critical
    runbook: docs/runbooks/nginx-down.md

  - if_down: VPS 1 completo
    affects: [livskin.site, livskin_wp DB, plugins activos]
    severity: critical
    recovery: DR drill — install.sh + restore backups
    runbook: docs/runbooks/disaster-recovery-vps1.md

  - if_down: VPS 2 completo
    affects: [n8n, vtiger, metabase, postgres-analytics — paraliza tracking]
    severity: critical
    recovery: DO snapshot restore O install.sh + restore backups
    runbook: docs/runbooks/disaster-recovery-vps2.md

  - if_down: VPS 3 completo
    affects: [ERP completo, brain, cliente data — paraliza operación interna]
    severity: critical
    recovery: DO snapshot restore O install.sh + restore backups
    runbook: docs/runbooks/disaster-recovery-vps3.md

  - if_down: DigitalOcean VPC
    affects: [cross-VPS queries metabase→erp, sensors recolección]
    severity: medium
    mitigation: VPS 1 sigue público; VPS 2/3 tienen IPs públicas → Cloudflare proxy puede ser fallback
```

---

## §5 SPOFs (Single Points of Failure)

```yaml
spofs:
  - component: postgres-data (VPS 3)
    impact: ERP entero + tests + cross-VPS queries
    severity: critical
    mitigation_now:
      - Backup pg_dump daily verificado
      - DO snapshot pre-deploy
      - Rollback automático CI/CD
    mitigation_planned:
      - Postgres replica read-only en VPS 2 (Fase 6+)

  - component: VPS 1 (1GB RAM apretado para WP)
    impact: WP puede OOM bajo carga
    severity: medium
    mitigation_now:
      - Monitoring de RAM
      - Plugin updates controlados
    mitigation_planned:
      - Resize a 2GB en Fase 6

  - component: Cloudflare Origin Cert (compartido entre VPS 2 y 3)
    impact: Si se compromete, ambos VPS expuestos
    severity: medium
    mitigation_now:
      - Cert separados en filesystem de cada VPS (no shared volume)
    mitigation_planned:
      - Cert por VPS (Fase 6 hardening)

  - component: GitHub Actions (CI/CD)
    impact: si GHA cae, no podemos deployar
    severity: low (raro + temporal)
    mitigation_now:
      - SSH directo al VPS sigue siendo posible
      - install.sh idempotente

  - component: doctl token (DO_API_TOKEN)
    impact: si se compromete, atacante puede destruir VPS
    severity: high
    mitigation_now:
      - Token solo en GitHub Secrets (encrypted)
      - Bitwarden backup del token
    mitigation_planned:
      - Rotación trimestral
      - Token con scope mínimo (no admin)
```

---

## §6 URLs públicas (todas vía Cloudflare)

```yaml
public_urls:
  - url: https://livskin.site
    backend: VPS 1 nginx-host → /var/www/livskin (WordPress)
    cert: Let's Encrypt
    cdn: cloudflare
    public: yes

  - url: https://flow.livskin.site
    backend: VPS 2 nginx → n8n:5678
    cert: cloudflare-origin
    public: yes (con auth interno)
    purpose: webhooks SureForms + workflows

  - url: https://crm.livskin.site
    backend: VPS 2 nginx → vtiger:80
    cert: cloudflare-origin
    public: yes (con auth Vtiger)
    purpose: CRM access

  - url: https://dash.livskin.site
    backend: VPS 2 nginx → metabase:3000
    cert: cloudflare-origin
    public: yes (con auth Metabase)
    purpose: dashboards

  - url: https://erp.livskin.site
    backend: VPS 3 nginx-vps3 → erp-flask:8000
    cert: cloudflare-origin
    public: yes (con auth bcrypt — ADR-0026)
    purpose: ERP

  # Eliminadas (decisión 2026-04-26):
  # - erp-staging.livskin.site (eliminada — staging real en Fase 6)
```

---

## §7 Backups (estado al 2026-04-26)

```yaml
backups:
  - component: WordPress files (/var/www/livskin/)
    vps: livskin-wp
    method: tarball
    frequency: pendiente Bloque 0.5
    retention: 30 dias planeado
    destination: cross-VPS livskin-ops /backups/vps1/
    verification: pendiente
    runbook: docs/runbooks/backup-wp.md

  - component: livskin_wp (MariaDB)
    vps: livskin-wp
    method: mariadb-dump
    frequency: pendiente Bloque 0.5
    retention: 30 dias planeado
    verification: restore a temp DB + count check

  - component: livskin_erp + livskin_brain (Postgres)
    vps: livskin-erp
    method: pg_dump
    frequency: pendiente Bloque 0.5
    retention: 30 dias planeado
    destination: cross-VPS livskin-ops /backups/vps3/

  - component: analytics + metabase (Postgres)
    vps: livskin-ops
    method: pg_dump
    frequency: pendiente Bloque 0.5

  - component: livskin_db (MariaDB Vtiger)
    vps: livskin-ops
    method: mariadb-dump
    frequency: pendiente Bloque 0.5

  - component: n8n workflows (sqlite + filesystem)
    vps: livskin-ops
    method: tarball ./n8n/data/
    frequency: pendiente Bloque 0.5
    critical: yes  # workflows perdidos = recreación manual

  - component: DO Snapshots (pre-deploy)
    method: doctl snapshot
    frequency: cada deploy
    retention: 7 dias (cleanup automático en workflow)
    purpose: rollback rápido en CI/CD failures
```

---

## §8 Credenciales y secretos

```yaml
secrets_inventory:
  - name: VPS1_SSH_KEY / VPS2_SSH_KEY / VPS3_SSH_KEY
    location: GitHub Secrets
    backup: keys/claude-livskin (gitignored, Bitwarden)
    purpose: SSH desde GHA + máquina dev a VPS
    rotation_target: anual

  - name: VPS1_HOST, VPS2_HOST, VPS3_HOST, VPS{N}_USER
    location: GitHub Secrets
    purpose: connection strings para SSH

  - name: DO_API_TOKEN
    location: GitHub Secrets + Bitwarden
    purpose: snapshots + rollbacks en CI/CD
    scope: read+write snapshots, droplets read
    rotation_target: trimestral

  - name: AUDIT_INTERNAL_TOKEN
    location: GitHub Secrets + .env de erp-flask
    purpose: shared secret para POST /api/internal/audit-event desde workflows
    rotation_target: trimestral

  - name: postgres-data password (livskin_erp)
    location: VPS 3 .env file (gitignored) + Bitwarden
    rotation_target: anual

  - name: postgres-analytics password
    location: VPS 2 .env file + Bitwarden
    current_value: "livskin" literal (DEUDA TÉCNICA — rotar en Bloque 0.7)

  - name: vtiger-db root + user passwords
    location: VPS 2 .env + Bitwarden
    current_value: "livskin" literal (DEUDA TÉCNICA — rotar en Bloque 0.7)

  - name: ERP user passwords (Dario, Claudia)
    location: bcrypt hash en livskin_erp.users
    backup: Bitwarden (passwords elegidas por usuarias)
    rotation_target: 90 dias recomendado

  - name: Cloudflare API token
    location: Bitwarden
    purpose: DNS management (manual hoy, automatizable)

  - name: Anthropic API key
    location: Bitwarden + keys/.env.integrations (gitignored)
    purpose: Claude API calls (Fase 4+)
    rotation_target: cuando Fase 4 lo use
```

---

## §9 Capacity planning

```yaml
capacity:
  - vps: livskin-wp
    cpu_avg_pct: 1
    ram_used_mb: 880
    ram_total_mb: 957
    ram_pct: 92  # APRETADO
    disk_used_gb: 4.4
    disk_total_gb: 25
    disk_pct: 19
    headroom: low (RAM)
    next_action_at: ram_pct > 95% por 24h sostenido

  - vps: livskin-ops
    cpu_avg_pct: 5
    ram_used_mb: 2253
    ram_total_mb: 3870
    ram_pct: 58
    disk_used_gb: 12
    disk_total_gb: 78
    disk_pct: 15
    headroom: comfortable

  - vps: livskin-erp
    cpu_avg_pct: 3
    ram_used_mb: ~700
    ram_total_mb: 2048
    ram_pct: 35
    disk_used_gb: ~10
    disk_total_gb: 50
    disk_pct: 20
    headroom: comfortable
```

---

## §10 Cómo el agente IA usa este documento

```yaml
ai_agent_consumption:
  primary_consumer: 5to agente (Infra+Security) post-Fase 6
  secondary_consumers: [Claude Code, Claude Agent SDK, MCP clients]

  query_examples:
    - question: "¿Dónde corre Langfuse?"
      response_source: §2 catálogo containers (cuando Langfuse esté agregado)

    - question: "¿Qué pasa si cae postgres-analytics?"
      response_source: §4 dependency_matrix entry "if_down: postgres-analytics"

    - question: "¿Cuál es el último backup de livskin_erp?"
      response_source: §7 backups + audit_log "infra.backup_verified" más reciente

    - question: "¿Hay algún SPOF crítico sin mitigación?"
      response_source: §5 spofs filtered by severity + mitigation_now

  json_endpoint:
    url: https://erp.livskin.site/api/system-map.json
    auth: shared_secret_header
    purpose: agente puede curl esta URL y parsear JSON estructurado
    parser_format: yaml-frontmatter + parsed body sections
```

---

## §11 Histórico de cambios

| Fecha | Cambio | SHA |
|---|---|---|
| 2026-04-26 | v1.0 — creación inicial post-Bloque 0.3 | TBD |

---

**Próximas actualizaciones esperadas:**
- Fase 3 → agregar Langfuse + workflows n8n a §2 y §3
- Fase 4 → agregar Conversation Agent a §2 + ingesta a agent_api_calls real
- Fase 6 → reorganizar VPS 3 paths + agregar staging + agregar ETL agent_api_calls → analytics.llm_costs
