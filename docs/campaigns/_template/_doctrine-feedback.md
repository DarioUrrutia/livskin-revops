---
campaign: {{CAMPAIGN_SLUG}}
type: bootstrap-feedback
mode: BOOTSTRAP (principio operativo #13) — solo aplica si el bootstrap está activo
purpose: capturar insights durante producción + ejecución de campaña que deben refinar la doctrina
processed_at_close: post-mortem (a llenar fecha)
---

# Doctrine Feedback — {{CAMPAIGN_NAME}}

> **Solo aplica mientras estamos en modo BOOTSTRAP** (principio operativo #13). Si el bootstrap ya está cerrado al inicio de esta campaña, este archivo se queda vacío y se procesa de manera más liviana en el post-mortem.

---

## Cómo se llena este archivo

Durante:
- **Producción** (banners, copies, landing)
- **Configuración** (setup Ads Manager)
- **Lanzamiento** (primeras impresiones, ajustes)
- **Monitoring** (daily reports identifican patrones)

Cualquier insight del tipo *"esto debería ir en la doctrina porque..."* se anota aquí con:
- Insight concreto
- Archivo de doctrina afectado
- Por qué (razón)
- Quién lo detectó
- Fecha
- Estado (pendiente / promovido / descartado)

---

## Insights acumulados

(formato a usar para cada insight nuevo:)

```markdown
#### [INS-NNN] (FECHA, Quién detectó) — Título corto del insight

**Contexto**: (qué pasó)

**Razón**: (por qué importa para doctrina)

**Archivo afectado**: `docs/brand/<archivo>.md`

**Refinamiento propuesto a v0.X**: (qué cambio aplicar)

**Estado**: 🟡 pendiente promoción al cierre del bootstrap
```

---

## Insights post-monitoring

### Patrones de performance

(a llenar conforme corre la campaña)

### Sorpresas en audience

(a llenar)

### Creatives que rompen la doctrina pero performean (paradojas)

(a llenar)

### Refinamientos a copy-principles.md sugeridos por data real

(a llenar)

---

## Procesamiento al cierre (post-mortem)

Al cierre del modo bootstrap o al post-mortem de la campaña:

1. Cada [INS-NNN] se evalúa: ¿promueve a doctrina o se descarta?
2. Si promueve: commit `docs(brand): refinamiento v0.X → v0.X+1 — [razón breve]`
3. Si se descarta: marcar 🔴 con razón
4. Estados finales se documentan en `post-mortem.md`
