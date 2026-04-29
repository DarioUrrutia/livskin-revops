# Audit minucioso — organización, seguridad, integridad (2026-04-29)

> **Solicitado por Dario:** "revisa organización del folder, nombres, categorización, seguridad e integridad. Sin romper lo que hicimos. Minuciosamente."
> **Modo:** read-only diagnóstico. Cero cambios.
> **Output:** este documento + recomendaciones priorizadas. Dario aprueba qué se ejecuta.

---

## 🔴 CRÍTICO (1 hallazgo)

### 1. Backups daily NO están corriendo en producción

**Verificado:**
```
ssh livskin-erp ls /srv/backups/local/  → 0 archivos
ssh livskin-erp ls /srv/backups/vps2/   → 0 archivos
ssh livskin-erp ls /srv/backups/        → solo "VPS3" placeholder de 9 bytes (Apr 26)
```

**Esperado:** Bloque 0.5 dice "Backups daily verificados ✅" en CLAUDE.md.

**Causa probable:** el cron nunca se instaló. CLAUDE.md menciona explícitamente como **pendiente**: "Instalar crons backup + sensor-collect (`install-cron.sh`)".

**Riesgo concreto:**
- Si VPS 3 cae **HOY**, se pierden:
  - 134 clientes productivos
  - 88 ventas + 84 pagos (data financiera real)
  - audit_log inmutable
  - brain pgvector con 1.765 chunks indexados
- Recovery time potencial: indefinido (sin backup external)
- DigitalOcean snapshots automáticos NO sustituyen backups daily — tienen latencia + son point-in-time arbitrarios

**Recomendación:** instalar crons HOY. El script `install-cron.sh` ya existe en `infra/scripts/`, solo hay que ejecutarlo en VPS 3 + verificar primer run mañana.

**Severidad:** 🔴 CRÍTICA porque hay data productiva insustituible.

---

## 🟡 MEJORAS DE ORGANIZACIÓN (3 hallazgos)

### 2. Archivos canvas vacíos en root

Archivos huérfanos:
```
./Senza nome 1.canvas    (2 bytes, contenido: "{}")
./Senza nome.canvas      (2 bytes, contenido: "{}")
```

Son artefactos de Obsidian (canvas vacíos creados por accidente).

**No están en .gitignore** — pero NO se han commiteado todavía (siguen en untracked).

**Recomendación:**
- Borrar los 2 archivos
- Agregar `*.canvas` (o más específico `Senza nome*.canvas`) a `.gitignore` para prevenir commits futuros accidentales

**Severidad:** 🟡 menor (cero impacto operativo, solo "ruido visual" en repo).

### 3. Duplicación de docker-compose folders (legacy + nuevo Bloque 0 v2)

5 folders legacy con `docker-compose.yml` que quedan superseded por equivalentes en `vps2-ops/`:

| Legacy (Fase 1) | Reemplazado por (Bloque 0 v2) |
|---|---|
| `infra/docker/n8n/docker-compose.yml` (408 bytes) | `infra/docker/vps2-ops/n8n/docker-compose.yml` (899 bytes — más completo) |
| `infra/docker/metabase/docker-compose.yml` | `infra/docker/vps2-ops/metabase/docker-compose.yml` |
| `infra/docker/vtiger/docker-compose.yml` | `infra/docker/vps2-ops/vtiger/docker-compose.yml` |
| `infra/docker/nginx/docker-compose.yml` | `infra/docker/vps2-ops/nginx/docker-compose.yml` (con conf/ + sites/) |
| `infra/docker/postgres/docker-compose.yml` | `infra/docker/vps2-ops/postgres-analytics/docker-compose.yml` |

**Verificación de seguridad antes de borrar:**
- ✅ Ningún workflow GitHub Actions referencia los paths legacy (`grep -r infra/docker/(n8n|metabase|...)/ .github/` → 0 matches)
- ✅ Los containers en VPS 2 actualmente corren desde `/home/livskin/apps/` (path legacy NO en repo) — no desde el repo. La migración (`migrate-from-home.sh`) está pendiente.
- ✅ Borrar las legacy NO afecta producción

**Recomendación:** borrar los 5 folders legacy. La fuente de verdad para deploy futuro es `infra/docker/vps2-ops/<service>/`.

**Severidad:** 🟡 menor (causan confusión cognitiva pero no daño operativo).

### 4. Diferencia entre `scripts/` (root) y `infra/scripts/` no documentada

**Estado actual:**
- `scripts/` (root) — 5 archivos Python: `google_audit.py`, `google_oauth_setup.py`, `gtm_*.py` (3 archivos GTM)
- `infra/scripts/` — 7 archivos shell: `alembic-*.sh`, `backup.sh`, `restore.sh`, `brain-*.sh`

**Propósito real:**
- `scripts/` (root) = **scripts de operación local** que corren desde mi laptop usando OAuth/credentials para auditar Google/Meta/etc.
- `infra/scripts/` = **scripts de operación VPS** que corren dentro de los servidores (alembic migrations, backups, brain re-indexing)

Son propósitos distintos pero el naming no lo deja claro. Alguien nuevo podría confundirse.

**Recomendación:**
- Crear `scripts/README.md` explicando que son scripts de operación local + listing de cada uno
- Crear `infra/scripts/README.md` similar para VPS-side scripts
- (Opcional, más invasivo) Renombrar `scripts/` → `scripts-local/` para claridad — NO recomendable porque rompe paths conocidos

**Severidad:** 🟡 menor (nice-to-have).

---

## 🟢 SEGURIDAD — todo OK (verificado)

### 5. .gitignore completo y robusto

```
✅ .env, .env.* (excepto .env.example)
✅ *.pem, *.key, *.crt
✅ *.ppk (PuTTY private keys)
✅ keys/* con whitelist (ssh_config, README, .gitkeep)
✅ erp/ (repo separado)
✅ data/, db/, /backups/ (gitignored at root)
✅ docs/Datos_Livskin_*.xlsx (PII real)
✅ notes/privado/* (local-only)
✅ logs, .pyc, __pycache__, node_modules, etc.
```

### 6. 0 secretos reales en historial git

Búsqueda exhaustiva en `git log -p` por keywords PASSWORD, SECRET_KEY, API_KEY, TOKEN, EAAg (Meta), fbq init:
- 0 tokens reales encontrados
- Todas las matches son **placeholders**: `"change-me-in-production"`, `"dev-only-change-in-production"`, `"test-internal-token"` — son default values del código, no secretos
- Las únicas referencias a "secret" en código son `cf_turnstile_secret_key: str = ""` (vacío por default)

### 7. 7 archivos `.env.example` versionados (correcto — son templates)

```
.env.example
infra/docker/erp-flask/.env.example
infra/docker/postgres-data/.env.example
infra/docker/vps2-ops/{metabase,n8n,postgres-analytics,vtiger}/.env.example
```

Ningún `.env` real commiteado (verificado `git ls-files '.env*'` → solo .example). ✅

### 8. keys/ folder bien protegido

```
keys/
  README.md              ✅ tracked (sin secrets)
  ssh_config             ✅ tracked (IPs + paths, sin claves)
  .gitkeep               ✅ tracked
  claude-livskin (priv)  ❌ NO tracked (gitignored por keys/*)
  claude-livskin.pub     ❌ NO tracked
  google-claude.json     ❌ NO tracked (service account)
  google-oauth-client.json ❌ NO tracked (OAuth client secret)
  google-oauth-token.json  ❌ NO tracked (refresh token)
  livskin-*.ppk          ❌ NO tracked (PuTTY keys)
  known_hosts            ❌ NO tracked
```

Estructura correcta. Si alguien clona el repo, NO obtiene credenciales.

---

## 🟢 INTEGRIDAD GIT — todo OK

### 9. git fsck limpio

```
dangling blob 3f7eae...   ← normal (residuo del revert, no es problema)
```

Sin objetos corruptos, sin commits huérfanos relevantes.

### 10. Historial git coherente

```
Últimos 11 commits trazables: cierres de sesión, mini-bloques, cleanup.
2 commits de revert correctos (1c4e977, f62775e).
0 force-pushes a main detectados.
0 commits sin co-authorship correcta.
```

---

## 🟢 PRODUCCIÓN — todos los servicios healthy

| URL | Status | Servicio |
|---|---|---|
| https://livskin.site/ | 301 (redirect www, normal) | WordPress |
| https://flow.livskin.site/ | 200 | n8n |
| https://crm.livskin.site/ | 200 | Vtiger |
| https://dash.livskin.site/ | 200 | Metabase |
| https://erp.livskin.site/api/internal/health | 200 JSON | ERP Flask |

VPS 3 containers (`docker ps`):
- erp-flask: Up 41 min (healthy)
- nginx-vps3: Up 9 days (healthy)
- embeddings-service: Up 9 days (healthy)
- postgres-data: Up 9 days (healthy)

ERP DB state (post-cleanup):
- leads: 0 (limpio tras revert)
- lead_touchpoints: 0
- **clientes: 134** (productivos intactos)
- **ventas: 88** (productivas intactas)
- **pagos: 84** (productivos intactos)
- audit_log: 11 entries (incluye 2 inmutables del experimento fallido — esto es por design, audit log no se borra)

---

## 🟢 ESTRUCTURA DE FOLDERS — bien organizada

```
.
├── CLAUDE.md                    ← contexto maestro auto-cargado
├── README.md                    ← instrucciones humanas
├── .env.example                 ← template
├── .gitignore                   ← comprehensivo
├── .github/                     ← CI/CD
├── .obsidian/                   ← gitignored (vault personal)
├── agents/                      ← Fase 4-5 (4 README placeholders)
├── analytics/                   ← Fase 3.5+ (3 subfolders empty pero esperados)
├── backups/                     ← gitignored
├── docs/
│   ├── audits/        (6 md)
│   ├── decisiones/    (16 ADRs)
│   ├── diagramas/     (vacío, reservado)
│   ├── runbooks/      (18 md)
│   ├── seguridad/     (1 md)
│   └── sesiones/      (15 md)
├── infra/
│   ├── docker/        (servicios containerizados — 🟡 5 legacy folders)
│   ├── nginx/         (configs)
│   ├── openapi/       (specs API)
│   ├── scripts/       (shell scripts VPS-side)
│   └── sql/           (legacy, 1 archivo — verificar)
├── integrations/      (8 servicios externos con README)
├── keys/              (gitignored salvo whitelist)
├── notes/
│   ├── compartido/    (versionada con .gitkeep)
│   └── privado/       (gitignored)
├── scripts/           (Python scripts operación local)
└── skills/            (Claude Code skills MCP — 2 folders)
```

**Naming convention:** kebab-case predomina, consistente. Excepciones identificadas:
- `Senza nome*.canvas` (Obsidian artifacts, a borrar)
- Algunos archivos Python en snake_case (estándar Python, correcto)

---

## 📋 EMPTY FOLDERS — todos esperados (placeholders fase futura)

```
agents/{acquisition,content,conversation,growth}/{prompts,evals,tools,...}  ← Fase 4-5
analytics/{dashboards,migrations,schemas}                                   ← Fase 3.5+
docs/diagramas/                                                              ← reservado
docs/datos_livskin_extract/                                                  ← gitignored (PII data viva)
backups/                                                                     ← gitignored (pulls locales)
infra/docker/nginx-vps3/html/                                                ← static placeholder
```

Todos OK — son estructuras pre-creadas para que cuando lleguen las fases respectivas no haya que improvisar paths.

---

## 📊 Inventario numérico

| Tipo | Cantidad |
|---|---|
| `.md` files | 102 (docs + memorias + READMEs) |
| `.py` files | 99 (ERP Flask + scripts + tests) |
| `.sh` files | 23 (ops scripts) |
| `.yml` files | 21 (docker-compose + CI workflows) |
| `.json` files | 12 (configs) |
| `.conf` files | 12 (nginx) |
| ADRs cerradas | 16 |
| Session logs | 15 |
| Runbooks ejecutables | 18 |
| Audit docs | 6 |
| Memorias persistentes | 32 |
| Brain pgvector chunks | 1.765 (94 archivos indexados) |

---

## 🎯 Plan propuesto (en orden de prioridad)

### 🔴 EJECUTAR HOY (CRÍTICO)
1. **Instalar crons backup en VPS 3** (`bash /srv/livskin-revops/infra/scripts/install-cron.sh`)
   - Verificar primer backup mañana 24h después
   - Documentar en CLAUDE.md cuando esté funcionando
   - Tiempo: 10 min

### 🟡 EJECUTAR HOY (LIMPIEZA, 5-10 min total)
2. **Borrar 2 archivos canvas** del root + agregar `*.canvas` a `.gitignore`
3. **Borrar 5 folders docker-compose legacy** (`infra/docker/{n8n,metabase,vtiger,nginx,postgres}/`)
4. **Crear 2 README pequeños**: `scripts/README.md` + `infra/scripts/README.md` (ya existe)

### 🟢 OPCIONAL (mejor para próxima sesión)
5. Verificar que `infra/sql/` no tiene basura legacy
6. Documentar `agents/` y `analytics/` empty folders con notas "reservado para Fase X"

### 🚫 NO TOCAR
- keys/ folder structure
- .gitignore (ya está perfecto, solo agregar `*.canvas`)
- Estructura `docs/decisiones/` (ADRs son inmutables)
- Estructura `infra/docker/erp-flask/` (precision quirúrgica)
- Empty folders con README (placeholders esperados)
- audit_log entries (inmutables por design)

---

## Conclusión global

**Sistema en buen estado.** Único hallazgo crítico real: **backups no corriendo**. Lo demás son mejoras de organización menores que se pueden ejecutar en 5-10 min sin riesgo.

**Resultado del audit:** ✅ Seguridad sólida + ✅ Integridad git OK + ✅ Producción healthy + 🔴 1 problema operativo + 🟡 4 mejoras menores.

---

**Generado:** Claude Code · 2026-04-29 (modo read-only, cero cambios ejecutados)
