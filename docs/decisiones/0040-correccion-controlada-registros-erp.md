# ADR-0040 — Corrección controlada de registros en ERP (campos no-monetarios)

- **Estado:** ✅ Aprobada (v1.0)
- **Fecha:** 2026-07-15
- **Autor:** Claude Code
- **Decisor:** Dario
- **Fase:** Post-bootstrap (operación continua)
- **Workstream:** ERP

---

## 1. Contexto

El 2026-07-15, durante ingreso de un lote de 13 ventas históricas (nov 2025), la venta `LIVTRAT0081` (Mery Salas Galindo) y su pago `LIVPAGO0095` quedaron con `fecha = 2026-07-15` (default del formulario) en vez de la correcta `2025-11-21`.

Al intentar corregirlo, se constató que el ERP **no tiene ninguna vía de edición**:
- La pestaña Libro es 100% read-only (por diseño, `api_libro.py` solo GET).
- No existe ningún endpoint UPDATE/PATCH/DELETE para ventas ni pagos.
- La única corrección posible era SQL directo en Postgres (hecho como hotfix, documentado en audit_log `venta.corrected_manual`).

Errores de tipeo en campos no-monetarios (fecha, notas, categoría, próxima cita) son inevitables en operación humana. Depender de SQL manual no escala (la doctora no puede corregirse sola) y sin trazabilidad estructurada erosiona la confianza en la data.

## 2. Decisión

Implementar **corrección controlada** con estas reglas duras:

1. **Whitelist de campos corregibles** (server-side, inviolable):
   - Ventas: `fecha`, `notas`, `proxima_cita`, `categoria`
   - Pagos: `fecha`, `notas`
2. **Montos NUNCA corregibles por esta vía** (`total`, `pagado`, `debe`, `descuento`, `monto`, `efectivo`, `yape`, `plin`, `giro`). El cálculo `debe`/`pagado` depende del trigger Postgres sobre `pagos` (migración 0002) y de `venta_service`; editar montos directamente los desincronizaría. Corrección de montos → futuro patrón **anulación + re-registro** (ADR pendiente cuando se necesite).
3. **Audit trail obligatorio**: cada corrección emite `venta.corrected` / `pago.corrected` con `before_state`/`after_state` completos. Identidad del operador capturada por el middleware de auth.
4. **Auth bcrypt requerido** (endpoints NO públicos — operación humana).
5. **Feature flag** `CORRECTIONS_ENABLED` (default `false` en código; `true` en compose de VPS3 tras validación).

Endpoints:
- `PATCH /api/ventas/<cod_item>/corregir`
- `PATCH /api/pagos/<cod_pago>/corregir`

UI: botón "✏️" por fila en pestaña Libro (ventas y pagos) → modal con campos whitelisted → PATCH → recarga.

## 3. Alternativas consideradas

| Opción | Veredicto | Razón |
|---|---|---|
| A) Todo editable, incluyendo montos | ❌ Rechazada | Desincroniza trigger DEBE; rompe integridad contable; sin patrón de reversa |
| B) Solo SQL manual documentado | ❌ Rechazada | No escala a doctora; fricción alta; trazabilidad ad-hoc |
| C) Whitelist no-monetaria + audit (ELEGIDA) | ✅ | Cubre el 90% de errores reales (fechas/textos) sin riesgo contable |
| D) Patrón anulación total (estilo contable puro) | ⏳ Diferida | Correcto para montos, pero overkill para corregir una fecha; se hará cuando surja la necesidad real |

## 4. Consecuencias

**Positivas:**
- Errores de fecha/texto corregibles en segundos desde la UI, por cualquiera de las 2 cuentas.
- Trazabilidad completa (quién, qué, antes/después) en audit_log inmutable.
- Whitelist server-side hace imposible corromper montos por esta vía incluso con requests manuales.

**Negativas / deuda aceptada:**
- Corrección de montos sigue sin vía en la app (anulación pendiente de diseño).
- El Libro deja de ser "100% read-only" conceptualmente — mitigado por whitelist + audit + flag.

## 5. Decisión hermana incluida en el mismo cambio

**Guard CAPI backfill**: ventas con `fecha` más antigua que 7 días (`CAPI_BACKFILL_MAX_DAYS` en `legacy_forms.py`) NO emiten CAPI Purchase — son backfills históricos y emitir contaminaría la atribución de Meta con conversiones falsas fechadas "hoy" (ocurrió con las 12 ventas históricas del 2026-07-15, ya irrecuperables). Audit: `tracking.capi_event_skipped_backfill`.

**Alineación ORM**: columnas `is_test` (migración 0009) declaradas ahora en los modelos `Venta` y `Pago` (antes solo existían en DB — drift).

## 6. Métricas de éxito

- 0 correcciones vía SQL manual post-deploy (todas por endpoint con audit).
- 0 registros con montos desincronizados (`debe != total - pagado` fuera del trigger).
- 0 eventos CAPI Purchase con `fecha` histórica post-guard.

## 7. Referencias

- `infra/docker/erp-flask/routes/api_correcciones.py` (implementación)
- `infra/docker/erp-flask/tests/routes/test_api_correcciones.py` (tests)
- Migración 0002 (trigger DEBE) + 0009 (`is_test`)
- Memoria `feedback_surgical_precision_erp` (protocolo aplicado)
- Incidente origen: audit_log `venta.corrected_manual` LIVTRAT0081 (2026-07-15)
