---
title: Setup email institucional Livskin (info@livskin.site)
category: integration
estimated_minutes: 35
last_validated: 2026-05-13
owner: Dario + Claude Code
prerequisites:
  - Cloudflare account con livskin.site como zona activa
  - Cuenta destino Gmail (daizurma2@gmail.com) accesible para verificación
  - Acceso a Bitwarden (para guardar credenciales nuevas)
---

# Runbook — Setup email institucional Livskin

> **Cuándo usar este runbook:**
> - Setup inicial de un buzón `@livskin.site` corporativo (este caso: `info@`).
> - Re-setup después de DR (DNS corrupto, cuenta CF migrada, etc.).
> - Migrar un buzón existente a esta arquitectura.
>
> **Cuándo NO usar:**
> - Agregar un buzón adicional **al mismo destino** que el actual → usar sólo § 4 (sólo create rule).
> - Migrar a Google Workspace pago → runbook separado (no existe aún).

---

## Arquitectura objetivo (3 piezas)

```
Cloudflare Email Routing  →  recibe  →  forward a daizurma2@gmail.com
Brevo SMTP                →  envía   →  Gmail "Send Mail As" usa Brevo como relay
```

Costo total: $0/mes. Free tier de ambos servicios.

---

## § 1. Pre-checks

```bash
# Confirmar que livskin.site no tiene MX/SPF/DKIM legacy que conflicten
source keys/.env.integrations
ZONE_ID=89ebefbde6dc2b1234a7da7872a9ab64

# Listar records actuales de email
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=MX" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python -m json.tool
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=TXT" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python -m json.tool | grep -E "spf|dkim|dmarc"
```

Si hay records previos no relacionados a Email Routing → decidir si borrarlos o reutilizarlos. **Nunca borrar sin documentar el motivo.**

---

## § 2. Cloudflare API token — scopes requeridos

El token debe tener (revisar en dash.cloudflare.com/profile/api-tokens):

- ✅ `Account:Email Routing Addresses:Edit`
- ✅ `Zone:Email Routing Rules:Edit`
- ✅ `Zone:DNS:Edit`

Si falta alguno: editar token, agregar permission, **NO regenerar** (mantener mismo valor).

---

## § 3. Habilitar Email Routing en la zona

**Vía UI (1 click — más simple):**
- dash.cloudflare.com → livskin.site → Email → Email Routing → toggle "Enable Email Routing" ON

**Vía API (opcional, si el token tiene `Zone:Zone Settings:Edit`):**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/enable" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

**Verificar status:**
```bash
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python -c "import sys,json; r=json.load(sys.stdin)['result']; print(f'enabled={r[\"enabled\"]} status={r[\"status\"]}')"
# Esperado: enabled=True status=ready
```

---

## § 4. DNS records para Cloudflare Email Routing

5 records (3 MX + 1 SPF + 1 DKIM). Cloudflare los sugiere desde el wizard, **pero acá los crearemos vía API** para que quede trazado en code:

```bash
# MX 1
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"MX","name":"livskin.site","content":"route1.mx.cloudflare.net","priority":37,"ttl":1,"comment":"Cloudflare Email Routing"}'

# MX 2
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"MX","name":"livskin.site","content":"route2.mx.cloudflare.net","priority":44,"ttl":1,"comment":"Cloudflare Email Routing"}'

# MX 3
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"MX","name":"livskin.site","content":"route3.mx.cloudflare.net","priority":27,"ttl":1,"comment":"Cloudflare Email Routing"}'

# SPF (NO permanente — se EXTIENDE en § 8 con Brevo)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"TXT","name":"livskin.site","content":"v=spf1 include:_spf.mx.cloudflare.net ~all","ttl":1,"comment":"SPF inicial - extender con Brevo en § 8"}'

# DKIM Cloudflare (selector cf2024-1)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"TXT","name":"cf2024-1._domainkey.livskin.site","content":"v=DKIM1; h=sha256; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiweykoi+o48IOGuP7GR3X0MOExCUDY/BCRHoWBnh3rChl7WhdyCxW3jgq1daEjPPqoi7sJvdg5hEQVsgVRQP4DcnQDVjGMbASQtrY4WmB1VebF+RPJB2ECPsEDTpeiI5ZyUAwJaVX7r6bznU67g7LvFq35yIo4sdlmtZGV+i0H4cpYH9+3JJ78km4KXwaf9xUJCWF6nxeD+qG6Fyruw1Qlbds2r85U9dkNDVAS3gioCvELryh1TxKGiVTkg4wqHTyHfWsp7KD3WQHYJn0RyfJJu6YEmL77zonn7p2SRMvTMP3ZEXibnC9gz3nnhR6wcYL8Q7zXypKTMD58bTixDSJwIDAQAB","ttl":1,"comment":"DKIM Cloudflare Email Routing"}'
```

---

## § 5. Destination address + routing rule

```bash
# Crear destination (verified automáticamente si es el email owner de la cuenta CF)
ACCOUNT_ID=5c8c8d42417a0c5c0ae4640a392ebc8f

curl -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/email/routing/addresses" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"email":"daizurma2@gmail.com"}'

# Si destino NO es owner: Cloudflare manda email de verificación, dueño clickea link

# Crear rule literal info@ -> daizurma2
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/rules" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "info@livskin.site forward to Gmail",
    "enabled": true,
    "priority": 0,
    "matchers": [{"type":"literal","field":"to","value":"info@livskin.site"}],
    "actions": [{"type":"forward","value":["daizurma2@gmail.com"]}]
  }'
```

**Test inbound:** desde tu Gmail personal mandate un email a `info@livskin.site`. Debe llegar a `daizurma2@gmail.com` en <60 seg.

> ⚠️ **Gmail puede mandarlo a Spam folder la primera vez** — comportamiento normal en forwarding nuevo. Solución:
> 1. Marcar "Not spam" en el email.
> 2. Crear filtro permanente en Gmail: Settings → Filters → "Has the words: `deliveredto:info@livskin.site`" → Create filter → marcar "Never send it to Spam".
> 3. DMARC (que agregaremos en § 8 con Brevo) ayuda a que Gmail confíe más rápido.

---

## § 6. Brevo Free signup (manual — Dario)

1. https://www.brevo.com → **Sign up free**
2. Email: `daizurma2@gmail.com` (centralizar acceso)
3. Password: generar y guardar en Bitwarden con label "Brevo SMTP Livskin"
4. Verificar email + teléfono (Perú o Italia)
5. En el onboarding cuando pregunta "qué emails vas a mandar": elegir **Transactional + Marketing**
6. Quedarte en el dashboard.

---

## § 7. Brevo — agregar dominio + obtener DNS records

En Brevo dashboard:

1. **Senders, Domains & Dedicated IPs** (menú izquierdo, bajo settings o senders).
2. **Domains** tab → **Add a domain**.
3. Domain: `livskin.site` → **Save & Authenticate**.
4. Brevo te muestra 2 (o 3) records DNS que tenés que agregar:
   - **DKIM TXT** — selector `brevo._domainkey` o similar (Brevo te da el valor exacto)
   - **SPF TXT** — usualmente te dice "agregar include:spf.brevo.com al SPF existente"
   - **DMARC TXT** (opcional pero recomendado): `_dmarc.livskin.site` con `v=DMARC1; p=none;`

Anotá esos valores. **NO clickees "Verify" todavía** — primero agregamos los records vía API en § 8.

---

## § 8. Aplicar DNS records de Brevo vía API

```bash
# 8.1 — Eliminar SPF inicial (vamos a reemplazarlo por el extendido)
# Listar TXT records para encontrar el ID del SPF
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=TXT&name=livskin.site" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | python -m json.tool

# Identificar el record con content "v=spf1 include:_spf.mx.cloudflare.net ~all" y guardar su id
SPF_ID="<id-del-spf-actual>"

# 8.2 — Reemplazar SPF (PUT/PATCH) con versión extendida que incluya Brevo
curl -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$SPF_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"TXT","name":"livskin.site","content":"v=spf1 include:_spf.mx.cloudflare.net include:spf.brevo.com ~all","ttl":1,"comment":"SPF para CF Email Routing + Brevo SMTP"}'

# 8.3 — Agregar DKIM Brevo (usar el valor exacto que Brevo te dio en § 7)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"TXT","name":"brevo._domainkey.livskin.site","content":"<DKIM-VALUE-FROM-BREVO>","ttl":1,"comment":"DKIM Brevo SMTP"}'

# 8.4 — Agregar DMARC (recomendado, modo monitor)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"TXT","name":"_dmarc.livskin.site","content":"v=DMARC1; p=none; rua=mailto:daizurma2@gmail.com","ttl":1,"comment":"DMARC monitor-only - escalar a quarantine despues de 30d sin issues"}'
```

**Volver a Brevo dashboard → Domains → click Verify Domain.** Brevo lee TXT y confirma. Puede tardar 5-15 min por propagación DNS.

---

## § 9. Generar SMTP key Brevo

En Brevo dashboard:

1. **SMTP & API** (menú izquierdo, settings).
2. **SMTP** tab.
3. **Generate a new SMTP key** → label: "Livskin Gmail SendAs"
4. Brevo te muestra **una sola vez** las credenciales:
   - **Login:** suele ser `daizurma2@gmail.com`
   - **SMTP key:** string aleatorio largo

Copiar AMBOS valores ahora a Bitwarden (label "Brevo SMTP Livskin — credentials").

Guardar también en `keys/.env.integrations`:
```
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
BREVO_SMTP_USER=daizurma2@gmail.com
BREVO_SMTP_KEY=<la-key-recien-generada>
```

---

## § 10. Gmail "Send Mail As"

**En Gmail Web (más fácil que Android para esta config inicial):**

1. mail.google.com con cuenta `daizurma2@gmail.com`.
2. **Settings (rueda dentada)** → **See all settings** → tab **Accounts and Import**.
3. Sección **Send mail as** → **Add another email address**.
4. Modal:
   - Name: `Livskin` (o "Livskin Estética" cuando esté la doctrina de marca)
   - Email address: `info@livskin.site`
   - **DESMARCAR** "Treat as an alias" (queremos que Gmail trate los outbound como cuenta separada para reply-as)
   - Next Step
5. SMTP config:
   - SMTP Server: `smtp-relay.brevo.com`
   - Port: `587`
   - Username: `daizurma2@gmail.com` (o el login que Brevo asignó)
   - Password: SMTP key Brevo
   - Secured connection using: **TLS** (recomendado)
   - Add Account
6. Gmail manda un email de verificación a `info@livskin.site` con un código.
7. Como `info@livskin.site` reenvía a daizurma2@gmail.com, el código LLEGA al inbox de Gmail mismo. Abrir, copiar código (o clickear link), pegar en modal, **Verify**.

**Test outbound:** compose new → from `info@livskin.site` → enviar a un email externo (otra cuenta tuya) → verificar que llegue con From `Livskin <info@livskin.site>` y NO en spam.

**Gmail Android:** una vez configurado en Web, Android lo hereda. Al componer email en Android, dropdown "From" permite elegir info@.

---

## § 11. Smoke tests obligatorios

### Inbound
- [ ] Email externo → `info@livskin.site` → llega a Gmail daizurma2@ en <60s
- [ ] Catch-all sigue en `Drop` (mandar email a `random@livskin.site` debe descartarse silenciosamente)

### Outbound
- [ ] Enviar desde Gmail como `info@` a Gmail externo → llega a Inbox (NO Spam)
- [ ] Headers muestran `dkim=pass` y `spf=pass`
- [ ] Reply a un email inbound preserva el From `info@livskin.site`
- [ ] Enviar desde Gmail Android como `info@` funciona igual

### Volumen (verificar después de 1 semana de uso)
- [ ] Brevo dashboard → Statistics → emails enviados <300/día consistentemente
- [ ] No bounces sostenidos (>5% bounce rate = revisar reputación)

---

## § 12. Documentar credenciales generadas

Actualizar:
- `keys/.env.integrations` (gitignored) con vars del § 9
- Bitwarden con labels "Brevo SMTP Livskin" + "Brevo dashboard login"
- `integrations/email/README.md` § "Configuración actual" — anotar fecha de signup Brevo, plan vigente, primer SMTP key id (sin el valor)

---

## Rollback / troubleshooting

**Si el setup falla a mitad de camino:**

1. **Desactivar rule** en CF Email Routing (en lugar de borrar) — `enabled: false` por API. Preserva config para diagnóstico.
2. **Si DNS está roto:** los records originales se listan en `integrations/email/README.md` § "Configuración actual" — re-aplicar via API.
3. **Si Brevo SMTP no autentica:** revocar SMTP key en Brevo + generar nueva + re-config Gmail.

**Errores comunes:**
| Error | Fix |
|---|---|
| `dkim=neutral` en headers outbound | DKIM record Brevo no propagado todavía. Esperar 15-30 min, retry. |
| Gmail "Send Mail As" rechaza credenciales | Verificar Brevo cuenta no está suspendida (free tier requiere verificar identity dentro de 7 días). |
| Catch-all forward accidental crea spam loop | Borrar rule catch-all inmediatamente. Mantener catch-all en `Drop`. |

---

## Cross-references

- `integrations/email/README.md` — fuente de verdad de configuración actual
- `integrations/email/.env.example` — vars de entorno
- `integrations/cloudflare/` — token API + scopes
- CLAUDE.md § "Principios operativos" #8 — cero servicios pagos sin aprobación (este setup es free, OK)
- Backlog Sprint A — email institucional (este runbook cierra ese sprint)
