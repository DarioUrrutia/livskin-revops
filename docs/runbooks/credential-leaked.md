---
runbook: credential-leaked
severity: critical
auto_executable: false
trigger:
  - "API token visible en log público (GitHub Actions, Loki, etc.)"
  - "Password en un commit (incluso post-commit)"
  - "SSH key en un repo público"
  - "Acceso no autorizado detectado en audit_log"
required_secrets:
  - DO_API_TOKEN
  - Bitwarden master password
time_target: "<30 minutos para rotar (mínimo) — bloqueo inmediato"
related_skills:
  - livskin-ops
---

# Credencial filtrada

## Severidad

🔴 **CRITICAL** — actuar en minutos, no horas. Cada minuto extra es ventana
para abuso.

## Síntomas

- API token visible en:
  - Log de GitHub Actions público
  - Commit history (incluso si fue revertido — git history persiste)
  - Bitbucket, GitLab, Stack Overflow, paste sites
  - Captura de pantalla compartida
- Password en plain text en algún archivo
- Audit log muestra accesos desde IP desconocida
- CloudFlare WAF triggers desde IP sospechosa

## Triage por tipo

### Tipo 1: DO_API_TOKEN

**Impacto:** atacante puede crear/destruir droplets, snapshots, etc.

```bash
# 1. INMEDIATO: revocar el token comprometido
# https://cloud.digitalocean.com/account/api/tokens → Delete token

# 2. Generar token nuevo con scope mínimo:
# - read+write droplet
# - read+write snapshot
# (NO admin, NO billing)

# 3. Update GitHub Secrets:
gh secret set DO_API_TOKEN --body "<new-token>"

# 4. Validar workflows siguen funcionando:
gh workflow run deploy-vps3.yml -f skip_snapshot=true -f skip_tests=true
```

### Tipo 2: SSH key (claude-livskin)

**Impacto:** atacante puede SSH a los 3 VPS.

```bash
# 1. INMEDIATO: remover key comprometida de los 3 VPS
for vps in livskin-wp livskin-ops livskin-erp; do
  ssh -F keys/ssh_config $vps 'sudo sed -i "/<comment-de-la-key>/d" /home/livskin/.ssh/authorized_keys'
done

# 2. Generar par nuevo
ssh-keygen -t ed25519 -f keys/claude-livskin-new -N "" -C "claude-code 2026-04-26"

# 3. Copiar pública a los 3 VPS (via consola DO o key vieja antes de revocar)
# Ya estaría hecho si la nueva ya fue distribuida.

# 4. Update GitHub Secrets:
gh secret set VPS1_SSH_KEY --body "$(cat keys/claude-livskin-new)"
gh secret set VPS2_SSH_KEY --body "$(cat keys/claude-livskin-new)"
gh secret set VPS3_SSH_KEY --body "$(cat keys/claude-livskin-new)"

# 5. Verificar SSH con key nueva funciona, key vieja no
ssh -F keys/ssh_config -i keys/claude-livskin-new livskin-erp 'echo OK new'
ssh -F keys/ssh_config -i keys/claude-livskin livskin-erp 'echo OK old' 2>&1 | grep -i denied

# 6. Backup key vieja en Bitwarden con tag "REVOKED <fecha>"
```

### Tipo 3: Password de DB (postgres-data, vtiger-db, etc.)

**Impacto:** dump completo de la DB, modificación de datos.

```bash
# 1. Conectar al postgres como superuser y rotar
ssh livskin-erp 'docker exec postgres-data psql -U postgres -c "ALTER USER postgres WITH PASSWORD \"<new-password>\";"'

# 2. Update .env del erp-flask (y otros containers que la usen)
ssh livskin-erp 'sudo sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=<new>/" /srv/livskin-revops/infra/docker/postgres-data/.env'

# 3. Restart containers que usen la DB
ssh livskin-erp 'cd /srv/livskin-revops/infra/docker/erp-flask && docker compose restart'

# 4. Verificar erp-flask sigue funcional
curl -sI https://erp.livskin.site/ping

# 5. Update Bitwarden con nueva password
```

### Tipo 4: Password de usuario ERP (Dario o Claudia)

**Impacto:** acceso a datos PII de 134 clientes (riesgo Ley 29733).

```bash
# 1. Force logout de TODAS las sesiones del usuario afectado
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  UPDATE user_sessions
  SET revoked = TRUE, revoked_at = NOW(), revoked_reason = \"security-credential-leaked\"
  WHERE user_id = (SELECT id FROM users WHERE username = \"dario\");
"'

# 2. Force reset de password (próximo login redirige a /change-password)
ssh livskin-erp 'docker exec erp-flask python /app/scripts/seed_users.py --reset'
# Captura las passwords nuevas en stdout (UNA VEZ)

# 3. Comunicar password nueva a Dario/Claudia por canal seguro (Signal, presencial)

# 4. Audit log entry:
curl -X POST https://erp.livskin.site/api/internal/audit-event \
  -H "X-Internal-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"infra.credential_rotated","metadata":{"reason":"leaked","scope":"user-passwords"}}'
```

### Tipo 5: Anthropic API key (post-Fase 4)

**Impacto:** atacante usa nuestra cuenta para hacer llamadas (costo).

```bash
# 1. Revocar en https://console.anthropic.com/settings/keys
# 2. Generar nueva key
# 3. Update Bitwarden + .env de containers que la usen
# 4. Restart containers
# 5. Verificar próxima llamada Claude API funciona (audit_log)
```

## Pasos comunes a TODOS los tipos

### A. Determinar exposure window

```bash
# ¿Cuándo se filtró? Buscar en:
git log --all --pretty=format:"%H %s" -p | grep -E "<token-prefix>"
gh run list --limit 50 --json databaseId,status,createdAt
# Audit log: accesos desde IP desconocida
```

### B. Revisar acceso no autorizado

```bash
# IPs de los últimos accesos exitosos
ssh livskin-erp 'docker exec postgres-data psql -U postgres -d livskin_erp -c "
  SELECT user_username, ip, count(*), max(occurred_at)
  FROM audit_log
  WHERE action = \"auth.login_success\"
    AND occurred_at > NOW() - INTERVAL \"7 days\"
  GROUP BY user_username, ip
  ORDER BY 4 DESC;
"'

# Buscar IPs no familiares (no Italia, no Cusco)
```

### C. Documentar incidente

`docs/audits/security-incident-<fecha>.md`:
- Timeline (cuándo se filtró, cuándo se detectó, cuándo se rotó)
- Scope (qué credencial, qué servicios afectados)
- Indicators of compromise (IPs, queries sospechosas)
- Acciones tomadas
- Lecciones aprendidas

### D. Audit event en audit_log

```bash
curl -X POST https://erp.livskin.site/api/internal/audit-event \
  -H "X-Internal-Token: $NEW_TOKEN" \
  -d '{"action":"infra.credential_rotated","metadata":{"reason":"leaked","scope":"<descriptor>"}}'
```

## Post-incidente

- Review por qué se filtró (CI logs públicos, commit, screenshot, etc.)
- Implementar prevención (gitleaks pre-commit hook, secrets scanning en GHA)
- Considerar si IP de atacante hay que bloquear en Cloudflare WAF

## Por qué este runbook NO es auto_executable

Rotaciones de credenciales requieren coordinación humana:
- Comunicar a usuarios afectados
- Update Bitwarden manualmente
- Regenerar tokens en consolas externas

Pero el agente PUEDE diagnosticar y proponer plan de rotación.
