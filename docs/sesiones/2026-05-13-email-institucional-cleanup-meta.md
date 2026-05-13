---
fecha: 2026-05-13
duracion: ~4-5h
modo: PROYECTO (#12)
participantes: Dario + Claude Code
fase: Sprint A — Email institucional + cleanup identidad Meta
estado: setup E2E completo + 1 commit pendiente
---

# Sesión 2026-05-13 — Email institucional info@livskin.site + cleanup Meta

## Resumen ejecutivo

Sprint A completado: email institucional `info@livskin.site` operacional end-to-end ($0/mes, free tier) + cleanup de identidad Meta (eliminación email legacy zombi del dominio extinto livskinperu.com). Documentación durable creada (README + runbook + .env.example + actualizaciones en 2 índices).

## Logros

### Email institucional E2E

| Capa | Componente | Estado |
|---|---|---|
| Inbound | Cloudflare Email Routing — rule `info@livskin.site → daizurma@gmail.com` | ✅ verified |
| Outbound | Gmail "Send Mail As" desde `daizurma@gmail.com` → Brevo SMTP | ✅ verified |
| DKIM | 2 selectors: `brevo1`/`brevo2._domainkey` (Brevo) + `cf2024-1._domainkey` (CF) | ✅ pass `d=livskin.site` |
| SPF | `v=spf1 include:_spf.mx.cloudflare.net include:spf.brevo.com ~all` | ✅ extendido |
| DMARC | `p=none; rua=mailto:rua@dmarc.brevo.com,mailto:daizurma2@gmail.com` | ✅ monitor-only |
| TLS | STARTTLS end-to-end | ✅ |
| Filtro Gmail anti-spam | `deliveredto:info@livskin.site` → Never send to Spam | ✅ creado |

**Componentes técnicos:**
- 3 MX records `route1/2/3.mx.cloudflare.net` aplicados vía Cloudflare API.
- Destination addresses: `daizurma@gmail.com` (primary, verified via email link) + `daizurma2@gmail.com` (secondary, disponible para futuros).
- Brevo Free plan: dominio `livskin.site` autenticado, SMTP user `ab370e001@smtp-brevo.com`, key Standard 64-char label "Livskin Gmail SendAs".
- Gmail Send Mail As configurado en cuenta `daizurma@gmail.com` (principal de Dario).

### Cleanup identidad Meta

**Hallazgos:**
- BM People mostraba `durrutia@livskinperu.com` como business email del único admin (Dario).
- `livskinperu.com` dominio EXTINTO — mail zombi → recovery imposible → riesgo de seguridad.
- Meta Accounts Center tenía registrado durrutia@livskinperu.com como recovery legítimo.

**Acciones ejecutadas:**
1. Agregado `info@livskin.site` al Meta Accounts Center (verificado via email forward → daizurma@).
2. Eliminado `durrutia@livskinperu.com` del Accounts Center.
3. BM People "Correo electrónico del negocio": cambiado a `daizurma2@gmail.com`.

**Estado final identidad Meta:**
- 4 recovery options en Accounts Center: `info@livskin.site` + `daizurma2@gmail.com` + `+51982732978` + `+393519466979`.
- BM Livskin Perú: 1 admin (Dario, business email = daizurma2@gmail.com).

## Doctrinas validadas

- **Principio #8 (zero pago sin aprobación)**: setup $0/mes (Cloudflare free + Brevo free + Gmail free).
- **Single user multi-email**: en FB no se pueden tener "2 entidades admin = vos" — una sola cuenta personal por persona física, pero múltiples emails recovery.
- **Email legacy ≠ borrar inmediato**: antes de eliminar un recovery email, agregar reemplazo + verificar para no romper acceso.

## Hallazgos no obvios

1. **Cloudflare Email Routing tiene 2 toggles separados** que UI etiqueta inconsistente: "Routing status: Enabled" (DNS records configurados) vs `enabled=true` real del servicio. El servicio se activa en UI nueva `cloudflare.com/email-routing` con botón "+ Onboard Domain" + Done. Los DNS records solos NO bastan.
2. **DigitalOcean bloquea TODOS los SMTP ports outbound** (25 + 587 + 465) por anti-spam. No se pueden hacer smoke tests SMTP desde VPS. Validación outbound requiere Gmail Send Mail As o API HTTPS de relay.
3. **Gmail con `deliveredto:` operator filtra emails forwardeados** independiente del sender original. Único filtro robusto contra spam-folder en setups de forwarding nuevo (sin reputación de dominio acumulada).
4. **Meta Accounts Center NO tiene "email primary" del perfil personal FB** (Meta unificó UI, eliminó esa noción). El "displayed email" en BM People es un campo INDEPENDIENTE editable ("Correo electrónico del negocio") por persona dentro de cada BM — separable del email FB account.
5. **Instagram + Threads permiten solo 1 email por cuenta** (advertencia roja en Meta Accounts Center si intentás agregar otro). Facebook sí permite múltiples emails. Por eso al agregar info@livskin.site a IG/Threads habría REEMPLAZADO daizurma2 — desmarcamos IG/Threads.

## Files creados/modificados

**Nuevos:**
- `integrations/email/README.md` — fuente de verdad del setup
- `integrations/email/.env.example` — vars template
- `docs/runbooks/email-institucional-setup.md` — runbook ejecutable 35 min, 12 secciones
- `docs/sesiones/2026-05-13-email-institucional-cleanup-meta.md` — este file

**Modificados:**
- `keys/.env.integrations` — bloque BREVO_SMTP_* agregado (gitignored)
- `integrations/README.md` — entry email/ agregado
- `docs/runbooks/README.md` — runbook #22 agregado, version bump 2.1 → 2.2

## Métricas

- **Tiempo total**: ~4-5h (incluyendo loops UI + troubleshooting Cloudflare enable + clarificaciones doctrinales)
- **API calls Cloudflare**: ~30 (DNS records + Email Routing setup + verificaciones)
- **Servicios SaaS nuevos**: 1 (Brevo Free)
- **Costo recurrente nuevo**: $0/mes
- **Recovery options Meta nuevas**: +1 email (info@livskin.site)
- **Recovery options Meta eliminadas (riesgo)**: -1 email zombi (durrutia@livskinperu.com)

## Próxima sesión propuesta

- Watchpoint pasivo Meta BM restricción (post Domain Verification 2026-05-10).
- Si Meta destraba → Sprint B: Fase 4A.2 + 4A.3 (bot-broker WhatsApp).
- Si Meta sigue trabado + docs RUC disponibles → submit Business Verification.

## Commits

(pendiente — Dario aprueba en chat al cierre)

Proyectado:
```
feat(email): setup email institucional info@livskin.site + cleanup Meta legacy

Arquitectura $0/mes: Cloudflare Email Routing (inbound) + Brevo SMTP (outbound)
+ Gmail "Send Mail As" en daizurma@gmail.com (UX).

Componentes:
- 3 MX + SPF extendido CF+Brevo + DKIM CF + 2 DKIM Brevo + DMARC monitor
- Destination address daizurma@gmail.com (primary verified)
- Rule literal info@livskin.site -> daizurma@
- Brevo Free + dominio livskin.site autenticado + SMTP key generada
- Gmail Send Mail As verificado en cuenta daizurma@

Cleanup identidad Meta:
- info@livskin.site agregado a Accounts Center
- durrutia@livskinperu.com eliminado (dominio extinto)
- BM People business email actualizado a daizurma2@gmail.com

Smoke E2E validado: outbound DKIM d=livskin.site, TLS, inbox limpio.

Documentación durable:
- integrations/email/README.md (fuente de verdad)
- integrations/email/.env.example (template vars)
- docs/runbooks/email-institucional-setup.md (35 min, 12 secciones)
- Index actualizados en integrations/README.md + docs/runbooks/README.md
```
