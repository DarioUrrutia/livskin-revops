# Tracking — Ácido Hialurónico — Día de la Madre 2026

> Específico para los ads de AH de esta campaña. Cheat sheet consolidado: [`../tracking.md`](../tracking.md).

---

## Shortcode manual

```
[AH-MAY-FB]
```

Significado: lead vino del ad de **Ácido Hialurónico Día de la Madre 2026 — Facebook/Instagram**.

---

## Mensaje WhatsApp pre-poblado

**Texto**:
```
Hola, vengo del aviso de Livskin Día de la Madre [AH-MAY-FB]
```

**URL completa para los 3 ads (TOFU/MOFU/BOFU) de AH**:
```
https://wa.me/51980727888?text=Hola%2C%20vengo%20del%20aviso%20de%20Livskin%20D%C3%ADa%20de%20la%20Madre%20%5BAH-MAY-FB%5D
```

**Donde se usa**: campo "Customize message" al configurar cada Ad de AH en Ads Manager.

---

## UTMs por banner (3 banners AH)

### Banner TOFU

```
utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=ah-tofu&utm_term={{adset.id}}
```

### Banner MOFU

```
utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=ah-mofu&utm_term={{adset.id}}
```

### Banner BOFU

```
utm_source=facebook&utm_medium=paid&utm_campaign=dia-madre-2026&utm_content=ah-bofu&utm_term={{adset.id}}
```

---

## Pixel events esperados

(Idénticos a Botox — ver `../botox/tracking.md` § "Pixel events esperados")

---

## Reportes de performance AH (post-launch)

| Métrica | Target AH |
|---|---|
| Spend AH ad set | ~$40 lifetime (40% del total) |
| Impresiones AH | ~3-6K |
| CTR AH | 1-2% |
| Mensajes WhatsApp con `[AH-MAY-FB]` | 2-6 totales en 5 días |
| Cost per message AH | $7-20 USD (puede ser ligeramente más alto que Botox por menos historial) |
| Mensajes por banner (TOFU vs MOFU vs BOFU) | distribución informa qué creative resuena |

---

## Cross-check con tracking sheet doctora

Cada vez que la doctora reciba un mensaje con `[AH-MAY-FB]` en su WhatsApp:

1. Doctora anota en Google Sheet:
   - Phone, Shortcode `AH-MAY-FB`, Tratamiento_interés, Status

2. Al final de campaña: count de leads `[AH-MAY-FB]` en sheet vs reportados por Meta para ad set AH.

---

## Comparativa Botox vs AH esperada

Hipótesis del brief: Botox tendrá más leads que AH (60/40 budget split refleja history 25 vs 4 ventas históricas).

Si los datos reales muestran:
- **AH supera a Botox proporcionalmente** → insight para próxima campaña: subir AH a 50/50 o más
- **Botox dominante 70%+ leads** → confirma Botox como caballo de batalla, AH es complemento
- **Ambos con CPM/CTR similar** → la audiencia es la misma F30-55 Cusco, los tratamientos varían en intent

---

## Cross-link

- Tracking consolidado: [`../tracking.md`](../tracking.md)
- Plan operativo: [`../plan.md`](../plan.md)
- Checklist UI: [`../ads-manager-checklist.md`](../ads-manager-checklist.md)
- Copies aprobados: [`copies.md`](copies.md)
- Tracking Botox: [`../botox/tracking.md`](../botox/tracking.md)
