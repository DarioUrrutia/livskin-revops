# Plan Operativo — {{CAMPAIGN_NAME}}

> **Brief estratégico:** [`brief.md`](brief.md)
> **Configuración técnica:** [`campaign-config-final.md`](campaign-config-final.md)
> **Checklist UI manual:** [`ads-manager-checklist.md`](ads-manager-checklist.md)

---

## 1. Objetivo

(a llenar — extender el `purpose` del brief con detalle operativo)

---

## 2. Estructura de la campaña

```
📦 Campaign: "{{CAMPAIGN_NAME}}"
   Objective: (a llenar — Tráfico / Engagement / Leads / Conversiones)
   Budget: S/ {{BUDGET_PEN}} lifetime con CBO
   Schedule: {{START_DATE}} → {{END_DATE}}
   Ad account: {{AD_ACCOUNT}}
   Pixel: {{PIXEL_ID}}
   │
   └─ (a llenar — ad sets + ads)
```

**Total:** (a llenar)

---

## 3. Audiencia detallada

(referenciar `brief.md` § 4 + extender con operativa de Meta Ads)

---

## 4. Métricas esperadas y targets

| Métrica | Target |
|---|---|
| CPM | (a llenar) |
| CTR | (a llenar) |
| Cost per lead | (a llenar) |
| Conversion rate lead→cliente | (a llenar) |
| Revenue esperado | (a llenar) |

---

## 5. Cronograma operativo

| Día | Fecha | Acciones |
|---|---|---|
| Día -1 (prep) |  | • Brief aprobado<br>• Banners producidos<br>• Landing aprobada<br>• Smoke E2E pre-launch |
| Día 0 (configuración) |  | • Configurar campaña en Ads Manager<br>• Submit a Meta review |
| Día 1 (launch) | {{START_DATE}} | • Meta aprueba ads<br>• Monitor primeras 6h |
| Día 2-N |  | • Daily check Ads Manager<br>• Doctora llena tracking sheet |
| Día final | {{END_DATE}} | • Cierre + análisis preliminar |
| Post-mortem |  | • Sesión de cierre + procesamiento `_doctrine-feedback.md` |

---

## 6. Tracking + monitoring

### Daily checklist (5 min cada mañana)

1. Abrir Ads Manager → seleccionar la campaña
2. Screenshot de métricas clave
3. Pasar al chat
4. Análisis + recomendaciones
5. Actualizar `tracking-sheet.csv` con leads nuevos

### Tracking manual de la doctora

- Cheat sheet impreso con shortcodes de esta campaña
- Anotar cada mensaje WA en Google Sheet
- Status flow: Nuevo → Contactado → Agendado → Asistio → Cliente

### Tracking automático

- Pixel client-side: PageView + clicks WA del landing
- (otros eventos según configuración del ad set)

---

## 7. Risk + mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| (a llenar) |  |  |  |

---

## 8. Lo que NO se hace en esta campaña

(declarar explícitamente lo descartado para preservar foco)

❌ (a llenar)

---

## 9. Definition of Done

- [ ] Campaña corrió X días + Ads Manager muestra impresiones + clicks reales
- [ ] Mínimo X leads recibidos
- [ ] Doctora llenó tracking sheet
- [ ] Daily reports generados
- [ ] Post-mortem ejecutado con data real
- [ ] Carpeta `docs/campaigns/{{CAMPAIGN_SLUG}}/` lista para archivar

---

## 10. Cross-link

- Brief: [`brief.md`](brief.md)
- Tracking: [`tracking-sheet.csv`](tracking-sheet.csv) + [`tracking-sheet-template.md`](tracking-sheet-template.md)
- Config técnico: [`campaign-config-final.md`](campaign-config-final.md)
- Checklist UI: [`ads-manager-checklist.md`](ads-manager-checklist.md)
- Doctrine feedback: [`_doctrine-feedback.md`](_doctrine-feedback.md)
- Post-mortem: [`post-mortem.md`](post-mortem.md)

---

**Plan vivo.** Refinable hasta lanzamiento. Una vez en producción, NO se modifica estructura/budget/audience sin OK explícito del operador.
