# WhatsApp Cloud API

Canal único de conversación con pacientes. Usado por el Conversation Agent.

## Estado actual

- [ ] Meta App creada
- [ ] WhatsApp Cloud API habilitada en la app
- [ ] Test number asignado (automático al habilitar la API)
- [ ] Número tuyo + doctora agregados como test recipients
- [ ] Access token + phone_number_id guardados en `keys/.env.integrations`
- [ ] Trámite de business verification iniciado (para número de producción)
- [ ] Templates de mensaje aprobadas (para número producción — opcional)

## Estrategia

**Fase 0 (ahora):** crear test number. Permite desarrollo completo sin esperar aprobación de Meta.

**Fase 4 (semana 6):** Conversation Agent usa test number. Tú y la doctora como test recipients.

**Cuando Meta aprueba producción:** cambiar variables de entorno, aprobar templates, migrar.

## Limitaciones del test number

- Solo envía a **números pre-aprobados** (hasta 5)
- 100% idéntico funcionalmente a producción
- No requiere business verification
- Gratuito

## Pasos para crear (guía)

1. Ir a https://developers.facebook.com/apps/ y crear una **App** tipo "Business"
2. Nombre: `Livskin RevOps` (u otro)
3. Agregar producto **WhatsApp** a la app
4. En WhatsApp → Getting Started: Meta asigna test phone number automáticamente
5. Copiar `Phone number ID` y `WhatsApp Business Account ID`
6. Generar **Temporary Access Token** (24h) para pruebas, luego **System User Token** permanente
7. Agregar tu número + el de la doctora como test recipients
8. Guardar en `keys/.env.integrations`:

```bash
WHATSAPP_PHONE_NUMBER_ID=123456789...
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321...
WHATSAPP_ACCESS_TOKEN=EAAxxxxxx...
WHATSAPP_TEST_RECIPIENTS=+51XXXXXXXXX,+51YYYYYYYYY
WHATSAPP_VERIFY_TOKEN=<string random generado por ti, para webhook>
```

## Webhook de mensajes entrantes

Cuando el paciente responda, Meta envía webhook HTTPS POST a:

```
https://flow.livskin.site/webhook/whatsapp-incoming
```

En n8n se configurará un webhook que valida `verify_token` y procesa el payload.

## Documentación externa

- WhatsApp Cloud API docs: https://developers.facebook.com/docs/whatsapp/cloud-api
- Test numbers: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

## Referencias

- ADR-0028 — Flujo de citas WhatsApp → Vtiger (sin LatePoint)
- ADR-0038 — WhatsApp test number Meta
- ADR-0029 — Conversation Agent (Fase 4)
