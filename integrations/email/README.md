# Email institucional — Livskin

> **Estado:** ✅ operacional (2026-05-13)
> **Buzón principal:** `info@livskin.site`
> **Forward destino:** `daizurma@gmail.com` (Gmail principal de Dario)
> **Send Mail As:** configurado en Gmail Web cuenta `daizurma@gmail.com`
> **Arquitectura:** Cloudflare Email Routing (RX) + Brevo SMTP (TX) + Gmail "Send Mail As" (UX)
> **ADR:** pendiente (se crea al cierre del setup)

---

## Propósito

Email oficial del negocio Livskin para:
- Email oficial registrado en Facebook Business Manager (ahora mismo está `daizurma@gmail.com` personal — riesgo de exposición).
- Campañas de email marketing (Fase 4A.5 del roadmap).
- Comunicación operativa con leads/clientes que escriban a contacto público.
- Address From en notificaciones automáticas del sistema (ERP, n8n, etc.) cuando aplique.

**Restricciones:**
- Free tier estricto (principio operativo #8 — cero servicios pagos sin aprobación).
- Durable: setup debe sobrevivir 12+ meses sin migración.
- Forward a `daizurma@gmail.com` (Gmail principal de Dario, donde lee diariamente).
- Send Mail As configurado en `daizurma@gmail.com` para componer/responder como `info@livskin.site`.
- `daizurma2@gmail.com` queda como destination address secundario (verified, disponible para forwards futuros — ej. doctora@livskin.site).
- Mobile-first: Dario revisa email principalmente desde Gmail Android.

---

## Arquitectura (3 piezas)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   ┌─ INBOUND (recibir) ────────────────────────────────────────────────┐     │
│   │                                                                    │     │
│   │   sender@externo.com                                                │     │
│   │         ↓                                                           │     │
│   │   info@livskin.site                                                 │     │
│   │         ↓ MX → Cloudflare Email Routing (3 MX route1/2/3)           │     │
│   │         ↓ rule literal "info@livskin.site" forward                  │     │
│   │         ↓                                                           │     │
│   │   daizurma@gmail.com  (inbox Gmail principal de Dario)              │     │
│   │                                                                    │     │
│   └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│   ┌─ OUTBOUND (enviar) ───────────────────────────────────────────────┐      │
│   │                                                                   │      │
│   │   Gmail Web/Android (cuenta daizurma@gmail.com)                    │      │
│   │         ↓ "Send Mail As" feature → from = info@livskin.site        │      │
│   │         ↓ SMTP credentials = Brevo (ab370e001@smtp-brevo.com)      │      │
│   │   smtp-relay.brevo.com:587 (STARTTLS, SMTP AUTH)                   │      │
│   │         ↓ Brevo firma con DKIM brevo1/2._domainkey.livskin.site    │      │
│   │         ↓ SPF check pass (include:spf.brevo.com)                   │      │
│   │         ↓ DMARC=pass por DKIM alignment d=livskin.site             │      │
│   │   recipient@externo.com  (inbox, después reputación domain)        │      │
│   │                                                                   │      │
│   └───────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Por qué 3 piezas y no una sola SaaS:**
- Zoho Mail Free **fue eliminado** (2026-05). Google Workspace Free no existe.
- Cloudflare Email Routing es free para **recibir** pero NO permite enviar.
- Brevo Free permite enviar (300 emails/día) pero NO da buzón.
- Combinándolos: $0/mes + buzón profesional con UX nativa de Gmail.

---

## Configuración actual (2026-05-13)

### Cloudflare Email Routing — INBOUND

| Item | Valor |
|---|---|
| Zone | `livskin.site` |
| Zone ID | `89ebefbde6dc2b1234a7da7872a9ab64` |
| Account ID | `5c8c8d42417a0c5c0ae4640a392ebc8f` |
| Status | `enabled` (status `ready`) |
| Destination address principal | `daizurma@gmail.com` (verified 2026-05-13 via Gmail link) |
| Destination ID principal | `024aee8d4f6d4f37a5464e05409b19b5` |
| Destination address secundario | `daizurma2@gmail.com` (verified, sin rule activa — disponible para forwards futuros) |
| Destination ID secundario | `d4a8293a73c0483d8b3daa8b8b86bf9b` |
| Routing rule | `info@livskin.site → daizurma@gmail.com` (enabled, priority 0) |
| Rule ID | `5c093602644245d5b9cdf0831d1d372c` |
| Catch-all | `Drop` (disabled) — emails a otras direcciones `@livskin.site` se descartan silenciosamente |

**DNS records (Cloudflare-managed, agregados vía API):**

| Tipo | Nombre | Contenido | Prioridad | Propósito |
|---|---|---|---|---|
| MX | `livskin.site` | `route1.mx.cloudflare.net` | 37 | Email Routing receiver #1 |
| MX | `livskin.site` | `route2.mx.cloudflare.net` | 44 | Email Routing receiver #2 |
| MX | `livskin.site` | `route3.mx.cloudflare.net` | 27 | Email Routing receiver #3 |
| TXT | `livskin.site` | `v=spf1 include:_spf.mx.cloudflare.net include:spf.brevo.com ~all` | — | SPF: autoriza Cloudflare Email Routing + Brevo SMTP |
| TXT | `cf2024-1._domainkey.livskin.site` | `v=DKIM1; ... p=MII...` | — | DKIM Cloudflare (firma forwards) |
| CNAME | `brevo1._domainkey.livskin.site` | `b1.livskin-site.dkim.brevo.com` | — | DKIM Brevo signature 1 |
| CNAME | `brevo2._domainkey.livskin.site` | `b2.livskin-site.dkim.brevo.com` | — | DKIM Brevo signature 2 |
| TXT | `livskin.site` | `brevo-code:b8d08510ae530dde9941d3b77332ef5f` | — | Brevo domain ownership verification |
| TXT | `_dmarc.livskin.site` | `v=DMARC1; p=none; rua=mailto:rua@dmarc.brevo.com,mailto:daizurma2@gmail.com` | — | DMARC monitor-only (reports a Brevo + daizurma2) |

### Brevo Free — OUTBOUND

| Item | Valor |
|---|---|
| Cuenta owner | `daizurma2@gmail.com` (Bitwarden label "Brevo SMTP Livskin") |
| Plan | Free (300 emails/día, hard limit) |
| Status | ✅ activo (signed up 2026-05-13) |
| Dominio firmado | ✅ `livskin.site` autenticado (2026-05-13) |
| SMTP host | `smtp-relay.brevo.com` |
| SMTP port | `587` (STARTTLS) |
| SMTP user | `ab370e001@smtp-brevo.com` (asignado por Brevo) |
| SMTP key | Generada 2026-05-13 label "Livskin Gmail SendAs" — valor en `keys/.env.integrations` BREVO_SMTP_KEY + Bitwarden |
| Sender | `Livskin <daizurma2@gmail.com>` verificado (no se usa en outbound real — Send Mail As reescribe From a info@livskin.site) |

**DNS records Brevo (✅ ya aplicados en sección anterior arriba):**

Brevo no usa el selector `brevo._domainkey` como mencionaba la doc legacy — en el flujo "Autentica il dominio da solo" Brevo da 2 CNAME (`brevo1._domainkey` + `brevo2._domainkey`) que apuntan a su DKIM signing infrastructure. Validación end-to-end confirmada con header `firmado por: livskin.site` en email recibido por Gmail.

**Por qué DKIM CF + DKIM Brevo coexisten:** selectors diferentes (`cf2024-1` para Cloudflare Email Routing forwards, `brevo1`/`brevo2` para Brevo SMTP outbound). Cada uno firma sus propios mensajes. No conflictan.

**Por qué DMARC en modo `p=none`:** monitor-only para diagnosticar antes de enforcement. Después de 30+ días sin issues, escalable a `p=quarantine`. Reports llegan a `rua@dmarc.brevo.com` (Brevo analytics) + `daizurma2@gmail.com` (visibilidad propia).

### Gmail "Send Mail As" — UX

✅ Configurado 2026-05-13 en **Gmail Web cuenta `daizurma@gmail.com`** (Gmail principal de Dario):

- Settings → Accounts and Import → Send mail as → Add another email
- Email: `info@livskin.site`
- Name: `Livskin`
- "Treat as alias": **DESMARCADO** (para reply correcto)
- SMTP server: `smtp-relay.brevo.com`
- Port: `587`
- Username: `ab370e001@smtp-brevo.com`
- Password: SMTP key Brevo (de `keys/.env.integrations` BREVO_SMTP_KEY + Bitwarden)
- TLS: enabled
- Verification: código mandado a info@livskin.site → reenvió a daizurma@ → clickeado link

Al componer en Gmail Web/Android (cuenta daizurma@gmail.com), dropdown "From" permite elegir `Livskin <info@livskin.site>`. Reply automático mantiene el From cuando responde a un email recibido en esa dirección.

---

## Smoke tests

### Test inbound (recibir)

```bash
# Desde cualquier email externo:
# To: info@livskin.site
# Subject: smoke test inbound
# Esperado: llega a daizurma2@gmail.com en <60 seg
```

Validar:
- ✅ Email aparece en Gmail inbox
- ✅ Header `Delivered-To: daizurma2@gmail.com` (forward)
- ✅ Header `X-Forwarded-For: info@livskin.site` (CF reescribe)

### Test outbound (enviar desde Gmail como info@)

```
# Desde Gmail (Web o Android), cuenta daizurma2@gmail.com:
# Compose new
# From dropdown: elegir info@livskin.site
# To: <cualquier externo que tengas acceso>
# Subject: smoke test outbound
# Body: cualquier
# Send
```

Validar en inbox destinatario:
- ✅ From muestra `info@livskin.site` (no daizurma2@gmail.com)
- ✅ Inspeccionar headers: `dkim=pass` para `brevo._domainkey.livskin.site`
- ✅ `spf=pass smtp.mailfrom=spf.brevo.com`
- ✅ NO aparece en Spam folder (Gmail/Outlook common destinatarios)

### Test reply

```
# Desde Gmail recibí un test inbound. Click Reply.
# El From auto-completa a info@livskin.site
# Send
```

Validar: comportamiento idéntico a outbound + threading preservado.

---

## Operación

### Agregar un buzón nuevo (ej. `doctora@livskin.site`)

1. **Decisión:** ¿forward a otra cuenta personal o nuevo destination?
2. **Si forward a destino existente** (ej. también daizurma2@gmail.com):
   - 1 línea via API: `POST /zones/$ZONE_ID/email/routing/rules` con matcher `literal to doctora@livskin.site`
3. **Si forward a NUEVO destino** (ej. doctora-personal@gmail.com):
   - Primero `POST /accounts/$ACCOUNT_ID/email/routing/addresses` con email destino
   - Dueño del email destino debe clickear link de verificación que llega de Cloudflare
   - Después create rule como arriba

Templates listos en `integrations/email/scripts/add-mailbox.sh` (pendiente — TODO si agregamos más buzones).

### Cambiar destino de un forward

```bash
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/rules/$RULE_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -d '{"actions":[{"type":"forward","value":["nuevo@destino.com"]}]}'
```

### Rotar SMTP key de Brevo

1. Brevo dashboard → SMTP & API → SMTP keys → revoke key actual
2. Generate new SMTP key
3. Gmail → Settings → Accounts → "Send mail as" → edit info@livskin.site → cambiar password
4. Update `keys/.env.integrations` si la usa otro sistema (ERP/n8n)
5. Smoke test outbound

### Migrar a Workspace pago (futuro)

Cuando Livskin tenga ingresos >$200/mes y justifique:
- Crear cuenta Google Workspace Business Starter ($6 USD/mes/usuario)
- Migrar DNS: cambiar 3 MX de Cloudflare por MX de Google
- Migrar Brevo SMTP a Workspace SMTP (o seguir con Brevo si volumen marketing > 300/día Gmail límite)
- Actualizar este README

---

## Troubleshooting

| Síntoma | Probable causa | Diagnóstico |
|---|---|---|
| Email a `info@` llega a **Spam folder** de Gmail | Normal en setups nuevos de forwarding — Gmail desconfía hasta entrenar | Marcar "Not spam" + **crear filtro Gmail permanente** `Has the words: deliveredto:info@livskin.site` con acción "Never send it to Spam". Mejora con tiempo + agregar DMARC (Brevo paso § 8). |
| Email a `info@` no llega a Gmail (ni Spam) | Rule disabled o destination unverified | `GET /zones/$ZONE_ID/email/routing/rules` → check `enabled:true`. `GET /accounts/$ACCOUNT_ID/email/routing/addresses` → check `status:verified` |
| Enviado desde Gmail como `info@` cae en Spam | Falta DKIM o SPF | Inspeccionar headers email recibido. Si `dkim=neutral` → revisar TXT brevo._domainkey en CF DNS. Si `spf=softfail` → revisar TXT SPF tiene `include:spf.brevo.com` |
| Gmail "Send Mail As" rechaza credenciales | SMTP key rotada/revoked | Regenerar SMTP key en Brevo + actualizar password en Gmail |
| Bounce "550 5.7.1 message rejected" | DMARC strict en destinatario, alguno de SPF/DKIM falla | Activar DMARC reports (rua=) para diagnosticar. Si Brevo agregó hostname propio en headers, esperar 24h propagación DKIM |
| MX records perdidos en CF | DNS purge accidental | Re-aplicar vía API (scripts en `infra/scripts/email/` — TODO) |

---

## Seguridad

- **Tokens y credenciales en `keys/.env.integrations`** (gitignored). Respaldo cifrado en Bitwarden.
- **SMTP key Brevo** NO se commitea. Está en `.env` con prefix `BREVO_SMTP_*`.
- **DKIM private keys** las maneja Cloudflare y Brevo internamente — nunca los vemos ni respaldamos.
- **Email forwarding NO es e2e encrypted** — Cloudflare lee headers para hacer routing. OK para uso comercial; NO usar para info legal/médica confidencial (eso va por canal cifrado aparte).
- **Phishing risk:** cualquier rule mal configurada (ej. catch-all forward) puede convertir el dominio en open relay de spam. **Mantener catch-all en `Drop`** salvo necesidad explícita.

---

## Cleanup Meta/Facebook ejecutado en este setup (2026-05-13)

Mientras configuramos el email institucional, sanamos también la identidad de Dario en Meta:

**Antes:**
- Cuenta personal FB tenía registrado `durrutia@livskinperu.com` como email primary (dominio extinto, mail zombi → riesgo de seguridad).
- BM Livskin Perú People mostraba `durrutia@livskinperu.com` como "Correo electrónico del negocio" del único admin.

**Después:**
- Meta Accounts Center contactos: `info@livskin.site` (agregado) + `daizurma2@gmail.com` + 2 teléfonos (+51 + +39).
- `durrutia@livskinperu.com` ELIMINADO del Accounts Center (cerró agujero de recovery zombi).
- BM People "Correo electrónico del negocio": `durrutia@livskinperu.com` → `daizurma2@gmail.com`.

**Doctrina actual de identidad Meta:**
- Una sola cuenta personal FB (Dario Urrutia Martinez) — Meta política, no se pueden tener 2 cuentas misma persona.
- 4 recovery options: 2 emails (info@livskin.site + daizurma2@gmail.com) + 2 teléfonos.
- Co-admin del BM requiere otra persona física (futuro: invitar a la doctora cuando aplique).

## Cross-references

- **Cloudflare Email Routing docs:** https://developers.cloudflare.com/email-routing/
- **Brevo SMTP docs:** https://help.brevo.com/hc/en-us/articles/7924908994450
- **Gmail Send Mail As:** https://support.google.com/mail/answer/22370
- **Runbook setup paso a paso:** [`docs/runbooks/email-institucional-setup.md`](../../docs/runbooks/email-institucional-setup.md)
- **CLAUDE.md principio #8** — cero servicios pagos sin aprobación.
- **Backlog Sprint A** — email institucional (este setup cierra ese sprint).
- **Roadmap Fase 4A.5** — email marketing tool (consume este setup como cimiento).
