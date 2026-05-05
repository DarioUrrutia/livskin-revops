---
campaign: {{CAMPAIGN_SLUG}}
type: post-mortem
status: pending
held_on: (fecha cuando se ejecute)
duration_min: (cuánto duró la sesión)
---

# Post-Mortem — {{CAMPAIGN_NAME}}

> Sesión de cierre + análisis. Procesar `_doctrine-feedback.md` + métricas reales + decisiones para próxima campaña.

---

## 1. Resumen ejecutivo

| Métrica | Plan | Real | Var |
|---|---|---|---|
| Budget | S/ {{BUDGET_PEN}} |  |  |
| Impresiones |  |  |  |
| Clicks |  |  |  |
| Leads |  |  |  |
| CPL |  |  |  |
| Conversion rate lead→cliente |  |  |  |
| Revenue |  |  |  |
| ROI |  |  |  |

---

## 2. Hipótesis vs realidad

### Hipótesis principal (del brief)
> (citar la hipótesis declarada en `brief.md`)

**Resultado:** ✅ confirmada / ❌ rechazada / 🟡 inconclusiva

**Evidencia:**
(a llenar)

### Hipótesis secundarias

| Hipótesis | Resultado | Evidencia |
|---|---|---|
|  |  |  |

---

## 3. Performance por ad set

| Ad Set | Spend | Clicks | Leads | CPL | Conv rate |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

---

## 4. Performance por shortcode

| Shortcode | Leads | Conversiones | CPL real |
|---|---|---|---|
|  |  |  |  |

---

## 5. Procesamiento de `_doctrine-feedback.md`

Para cada [INS-NNN] del archivo:

| INS | Decisión | Razón |
|---|---|---|
|  | 🟢 Promover a doctrina v0.X+1 |  |
|  | 🟡 Mantener como observación |  |
|  | 🔴 Descartar |  |

### Commits de refinamiento de doctrina ejecutados

- `docs(brand): ...` (link al commit)

---

## 6. Aprendizajes durables (no doctrina, pero capturar)

### Lo que funcionó
-

### Lo que NO funcionó
-

### Sorpresas
-

---

## 7. Bugs/gaps técnicos detectados durante la corrida

(items que van al backlog del proyecto)

|  Item | Backlog destination | Prioridad |
|---|---|---|
|  |  |  |

---

## 8. Decisiones para próxima campaña

| Cambio propuesto | Razón |
|---|---|
|  |  |

---

## 9. Métricas para benchmark futuro

(guardar valores específicos como referencia para comparar próximas campañas)

```
CPM:        (valor real)
CTR:        (valor real)
CPL:        (valor real)
Conv rate:  (valor real)
```

---

## 10. Status del modo bootstrap (si aplica)

- ☐ Bootstrap **se cierra** con esta campaña → doctrina v0.X → v1.0
- ☐ Bootstrap **continúa** → próxima campaña sigue capturando feedback

---

## 11. Archivado

Post-mortem cerrado:
- [ ] Esta carpeta `docs/campaigns/{{CAMPAIGN_SLUG}}/` se mueve a `docs/campaigns/_archive/`
- [ ] Aprendizajes durables migrados a memorias permanentes (si aplica)
- [ ] Backlog actualizado con items detectados
- [ ] Próxima campaña planificada (si corresponde)

---

**Status del post-mortem:** `pending` → marcar `closed` cuando se complete.
