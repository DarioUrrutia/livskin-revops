# Tracking — Botox — Día de la Madre 2026

> Específico para los ads de Botox de esta campaña. Para el cheat sheet consolidado de la doctora ver [`../tracking.md`](../tracking.md).

---

## Shortcode manual

```
[BTX-MAY-FB]
```

Significado: lead vino del ad de **Botox Día de la Madre 2026 — Facebook/Instagram**.

---

## Mensaje WhatsApp pre-poblado

**Texto**:
```
Hola, vengo del aviso de Livskin Día de la Madre [BTX-MAY-FB]
```

**URL completa para los 3 ads (TOFU/MOFU/BOFU) de Botox**:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BBTX-MAY-FB%5D
```

**Donde se usa**: en el campo "Customize message" al configurar cada Ad de Botox en Ads Manager (ver `../ads-manager-checklist.md` § 6).

---

## UTMs por banner (3 banners Botox)

Tracking URL parameters que se setean al crear cada Ad en Meta Ads Manager:

### Banner TOFU (3 aspect ratios = 1 ad en Ads Manager)

```
utm_source=facebook
utm_medium=paid
utm_campaign=dia-madre-2026
utm_content=botox-tofu
utm_term={{adset.id}}
```

URL parameter compacto (lo que se pega en Ads Manager):
```
utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=botox-tofu&utm_term={{adset.id}}
```

### Banner MOFU

```
utm_content=botox-mofu
```

URL parameter compacto:
```
utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=botox-mofu&utm_term={{adset.id}}
```

### Banner BOFU

```
utm_content=botox-bofu
```

URL parameter compacto:
```
utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=botox-bofu&utm_term={{adset.id}}
```

---

## Pixel events esperados (al click del usuario)

Cuando un usuario clickea "Send Message" en cualquier banner Botox:

1. **Pixel `Click` event** firea (default behavior de Meta)
2. **Custom Conversion "WhatsApp Lead Día de la Madre"** firea (si está configurada en Events Manager) — tracking categorizado como "Lead" event
3. **CAPI server-side** NO firea desde click directo (CAPI dispara en eventos posteriores como Purchase). Para esta campaña, CAPI no es crítico — el Pixel front-end es suficiente.

---

## Reportes de performance Botox (post-launch)

Métricas a trackear específicamente para Botox:

| Métrica | Target Botox |
|---|---|
| Spend Botox ad set | ~$60 lifetime (60% del total) |
| Impresiones Botox | ~5-9K |
| CTR Botox | 1-2% |
| Mensajes WhatsApp con `[BTX-MAY-FB]` | 4-10 totales en 5 días |
| Cost per message Botox | $6-15 USD |
| Mensajes por banner (TOFU vs MOFU vs BOFU) | distribución informa qué creative resuena |

---

## Cross-check con tracking sheet doctora

Cada vez que la doctora reciba un mensaje con `[BTX-MAY-FB]` en su WhatsApp:

1. Doctora lo anota en Google Sheet:
   - Phone: del lead
   - Shortcode: `BTX-MAY-FB`
   - Tratamiento_interés expresado en conversación: lo que diga el lead
   - Status: nuevo → contactado → agendado → asistió → cliente

2. Al final de campaña: count de leads con `[BTX-MAY-FB]` en sheet vs count de mensajes reportados por Meta Ads Manager para el ad set Botox.
   - Si match ±10% → tracking funciona
   - Si divergencia >20% → investigar (algunos leads pueden editar el texto antes de enviar)

---

## Cross-link

- Tracking consolidado: [`../tracking.md`](../tracking.md)
- Plan operativo: [`../plan.md`](../plan.md)
- Checklist UI: [`../ads-manager-checklist.md`](../ads-manager-checklist.md)
- Copies aprobados: [`copies.md`](copies.md)
