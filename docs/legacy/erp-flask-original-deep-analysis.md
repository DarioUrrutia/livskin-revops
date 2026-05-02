# Análisis profundo del ERP Flask original (Render)

**Fecha**: 2026-04-25
**Fuente**: `formulario-livskin.onrender.com` ([repo GitHub](https://github.com/DarioUrrutia/formulario-livskin))
**Propósito**: documentar la lógica completa del Flask actual para que el ERP refactorizado en VPS 3 sea funcionalmente equivalente. Esta auditoría profundizada se hizo después de descubrir que se había leído el código superficialmente al inicio de la implementación.

---

## 1. Endpoints del Flask original

| Endpoint | Método | Función | Estado en mi ERP refactorizado |
|---|---|---|---|
| `/` | GET | Carga formulario.html + clientes + config | ⏳ Falta (HTML template no implementado) |
| `/venta` | POST | Las 6 fases de venta | ✅ Implementado (con gaps que documentar) |
| `/pagos` | POST | Pagos posteriores día separado al de venta | ❌ **No implementado** |
| `/gasto` | POST | Registrar gasto | ⏳ Tabla creada, endpoint falta |
| `/cliente` | GET (JSON) | Historial ventas+pagos+saldo del cliente | ❌ **No implementado** (tengo `/api/client-lookup` que es distinto) |
| `/api/dashboard` | GET (JSON) | KPIs + comparativas + aging | ❌ **No implementado** |
| `/api/libro` | GET (JSON) | Export todas las ventas/pagos/gastos | ❌ **No implementado** |
| `/api/config` | GET (JSON) | Catálogos del Listas | ⏳ Tengo `/api/catalogos` con shape distinto |
| `/actualizar-headers` | GET (HTML) | Sincroniza headers del Sheet | ⏳ N/A (uso Alembic en lugar) |
| `/ping` | GET | Keep-alive | ✅ |

---

## 2. Hallazgos críticos del análisis profundo

### 2.1 `/venta` — diferencias entre mi implementación y el original

**A. Auto-creación de cliente desde venta payload**

Original Flask:
```python
# El POST /venta acepta directamente:
cliente = request.form.get("cliente", "")
telefono = request.form.get("telefono", "")
email = request.form.get("email", "")
cumpleanos = request.form.get("cumpleanos", "")
actualizar_cli = request.form.get("actualizar_cliente", "0") == "1"

cod_cliente = get_or_create_cliente(
    clientes_ws, cliente, telefono, cumpleanos, email,
    actualizar=actualizar_cli
)
```

**Comportamiento**:
- Si cliente NO existe → lo crea automáticamente
- Si EXISTE: campos vacíos del cliente se llenan automáticamente con info nueva (sin preguntar)
- Si `actualizar=1`: campos con valor distinto se sobrescriben

Mi implementación: requiere `cod_cliente` exacto, falla con 404 si no existe.

**Gap**: el frontend espera poder enviar `cliente="Carmen Lopez"` + datos y que el sistema:
1. Busque cliente existente o cree uno nuevo
2. Actualice datos del cliente cuando aplique
3. Procese la venta

**B. Métodos de pago — solo en primera fila/pago**

Original Flask:
```python
# En ventas: efectivo, yape, plin, giro SOLO en primera fila
ef = efectivo if idx == 0 else ""
ya = yape if idx == 0 else ""
# (igual en pagos: solo en primer pago)
```

Mi implementación: distribuye `efectivo/yape/plin/giro` proporcionalmente entre TODOS los ítems (cada fila tiene su porción).

**Diferencia**: total monetario = idéntico. Pero shape de la data en DB es distinto.

**Implicación**: si la doctora exporta `/api/libro` y lo abre en Excel, las celdas de métodos en filas 2+ están vacías en el Flask original. En mi sistema, todas tienen valores (proporcionales).

**C. Crédito aplicado — distribución por ítem**

Original Flask:
```python
# Crédito se distribuye proporcionalmente a cada ítem
for idx, item in enumerate(items_prep):
    proporcion = item["precio"] / total_items
    credito_item = round(min(credito_restante, credito_aplicado * proporcion))
    
    pagos.append_row([..., credito_item, ..., 
        "Crédito aplicado",      # NOTAS (string mágico)
        item["cod_item"],         # COD_ITEM vinculado al item
        item["categoria"],        # CATEGORIA original
        next_cod_pago(),
    ])
```

Mi implementación: crea UN solo pago `credito_aplicado` sin `cod_item`.

**Implicación importante**: en el Flask original, `cobrado_real_por_item` se calcula sumando todos los pagos vinculados a `cod_item`. Si crédito_aplicado se reparte por item, contribuye al "cobrado" de cada uno. Mi implementación pierde este vínculo.

**Esto afecta el cálculo de DEBE**: si Carmen aplica S/.200 de crédito a una venta de 2 items (Botox 700 + PRP 300), el original distribuye:
- Botox: 140 crédito aplicado (70% × 200)
- PRP: 60 crédito aplicado (30% × 200)

Mi sistema: 1 pago de 200 sin cod_item → no se distribuye a items específicos.

**D. Identificación por `NOTAS` magic strings vs `tipo_pago` enum**

Original Flask usa el campo `NOTAS` de la hoja Pagos como discriminador:
- `"Pago venta {fecha}"` → pago normal de venta
- `"Crédito generado por exceso de pago"` → exceso = crédito
- `"Crédito aplicado"` → consumo de crédito previo (NO cuenta en cobrado_total)
- `"Abono deuda anterior"` → abono a deuda

Y `CATEGORIA` complementa para créditos:
- `"CRÉDITO"` o `"CRÉDITO: nota"` o `"ANTICIPO"` → es depósito de crédito

Mi implementación: campo `tipo_pago` enum (`normal | credito_generado | credito_aplicado | abono_deuda`).

**Mi modelo es mejor diseño** (enum tipado vs magic strings), pero significa que al hacer backfill desde el Sheets actual, debo MAPEAR los NOTAS+CATEGORIA del original a mi `tipo_pago`.

**E. Multi-currency por ítem (USD/EUR)**

Original Flask: cada ítem puede tener `moneda_item_{i}` distinto + `tc_item_{i}`. Convierte a soles internamente.

Mi implementación: `moneda` y `tc` a nivel de venta (no por item).

**Implicación**: si la doctora vendió un certificado en USD y un tratamiento en soles en la misma venta, mi sistema no soporta esto bien.

**F. Categoría "__otro__" custom**

Original Flask: si `categoria == "__otro__"`, usa `categoria_otro_{i}` (texto libre del usuario).

Mi implementación: solo acepta valores del catálogo. Sin opción "otro" libre.

---

### 2.2 `/pagos` POST — endpoint COMPLETAMENTE no implementado

Detalle exhaustivo en `docs/decisiones/0027-audit-log-inmutable.md` y otras secciones.

**Resumen del comportamiento original**:
- Endpoint para registrar pagos de DÍAS POSTERIORES a la venta
- Acepta cliente + array `cod_item_pago[]`, `monto_item_pago[]`, `categoria_pago[]`
- Métodos de pago en primera fila solamente
- Genera nuevo `cod_pago` por cada item
- **Cero validación de saldo** (frontend valida)
- **Sin lógica de crédito** (a diferencia de /venta)

**Casos de uso reales (per Dario)**:
- Cliente vuelve días después solo a pagar
- Doctora marca múltiples deudas en pantalla y registra pago combinado
- Pago adelantado (cliente deja "depósito" — generaría crédito)

---

### 2.3 `/cliente` GET — endpoint COMPLETAMENTE no implementado

**Estructura JSON exacta esperada**:

```json
{
  "ventas": [
    { /* fila exacta de hoja Ventas como dict */ }
  ],
  "pagos": [
    { /* fila exacta de hoja Pagos como dict, EXCLUYENDO "Crédito aplicado" */ }
  ],
  "facturado_total": 500.0,
  "cobrado_total": 250.0,
  "saldo": 250.0
}
```

**Reglas críticas**:
1. Búsqueda por `nombre` (query param), case-insensitive
2. Excluye filas Pagos con `NOTAS == "Crédito aplicado"` (es transferencia interna)
3. **DEBE se RECALCULA DINÁMICAMENTE**: `max(0, total_venta - sum(pagos_por_cod_item))`
4. NO retorna crédito disponible explícitamente
5. NO filtra por fecha (retorna historial completo)

**Mi `/api/client-lookup`**: usa phone, retorna shape distinto. Falta este `/api/cliente?nombre=X` que el frontend HTML usa.

---

### 2.4 `/api/dashboard` — endpoint COMPLETAMENTE no implementado

KPIs específicos:
- `ventas_total`, `cobrado_total`, `pendiente_total`
- `ticket_promedio`, `tasa_cobro`, `balance_neto`, `total_gastos`
- `num_atenciones`, `num_clientes`, `num_promociones`, `total_descuentos`
- Distribución por método: `ef_efectivo`, `ef_yape`, `ef_plin`, `ef_giro`
- Distribución por tipo: `total_tratamientos`, `total_productos`, `total_otros`
- `por_mes` array — series temporales
- `top_clientes` (top 10 por revenue) + `top20_clientes` (con tendencia, frecuencia)
- `por_categoria` (top 10) + `top_cats_mes` (top 8 mes actual)
- `recientes` + `pagos_recientes`
- Comparativas: `comp_mes_actual`/`comp_mes_anterior`/`comp_mes_delta` + año
- `tipo_mes_actual` / `tipo_mes_anterior`
- `deudores_aging` con buckets (`menos_30` / `30_60` / `60_90` / `mas_90`)
- `pendientes_pago` (idéntico a aging)

**Filtros**: `desde` y `hasta` (formato `dd/mm/yyyy` o `yyyy-mm-dd`).

**Cálculo crítico — debe_real**: usa `pagos_por_item = calcular_pagos_por_item(todos_pagos)` y luego `cobrado_item = min(pagos_acumulados, total_venta)`. **Es JOIN por COD_ITEM, no por fecha**.

---

### 2.5 `/api/libro` — endpoint COMPLETAMENTE no implementado

Retorna `{ventas: [], pagos: [], gastos: []}` con shape de cada fila como dict (formato lowercase de columnas: `cod_cliente`, `total`, `pagado`, etc.).

---

### 2.6 `/api/config` — endpoint COMPLETAMENTE no implementado

Retorna catálogos como dict de listas:
```json
{
  "tipo": ["Tratamiento", "Producto", "Certificado", "Promoción"],
  "cat_Tratamiento": ["Botox", "Ácido Hialurónico", ...],
  "cat_Producto": ["Bloqueador", ...],
  "cat_Certificado": ["Certificado Médico"],
  "area": ["Facial", "Cuello", ...]
}
```

Mi `/api/catalogos` retorna `{"items": [...]}` paginado. Shape distinto.

**Implicación**: el frontend hace `GET /api/config` al cargar el form y espera ESE shape exacto. Si rompo el shape, los selects del form no se llenan.

---

### 2.7 `/gasto` POST — endpoint NO implementado

Payload simple:
```
fecha_gasto, tipo_gasto, descripcion, destinatario, monto_gasto, metodo_pago_gasto
```

Sin validación. Retorna redirect + flash.

---

### 2.8 Caché TTL 90s — diseño que NO necesito replicar

El caché del Flask original era para mitigar latencia de Google Sheets API. Postgres es <10ms — cache no necesaria. Confirmado en ADR-0023 § 6.6.

---

## 3. Gaps consolidados en mi implementación actual

| # | Gap | Impacto | Prioridad |
|---|---|---|---|
| 1 | No auto-creo Cliente desde POST `/venta` | Frontend no funciona como espera | **Crítica** |
| 2 | Métodos de pago se distribuyen por item (vs solo primera fila en original) | Diferencia de shape, no de totales | Media |
| 3 | Crédito aplicado no se distribuye por item | DEBE de items individuales se calcula mal | **Crítica** |
| 4 | Sin endpoint `/api/pagos` (vuelve cliente a pagar otro día) | Use case operativo común no soportado | **Crítica** |
| 5 | Sin endpoint `/api/cliente?nombre=X` (full historial JSON) | Frontend `buscarCliente()` no funciona | **Crítica** |
| 6 | Sin endpoint `/api/dashboard` con KPIs reales | Dashboards no funcionan | **Crítica** |
| 7 | Sin endpoint `/api/libro` | Export no funciona | Alta |
| 8 | `/api/config` shape distinto al esperado por el frontend | Selects del form no se llenan | **Crítica** |
| 9 | Sin endpoint POST `/gasto` | Pestaña Gasto no funciona | Alta |
| 10 | DEBE se calcula a write-time, no dinámicamente | Si entran pagos posteriores via `/api/pagos`, DEBE de la venta queda desactualizada | **Crítica** |
| 11 | Sin soporte multi-currency por item | Casos USD/EUR rotos | Media |
| 12 | Sin soporte categoría `__otro__` libre | Casos donde doctora improvisa categoría | Baja |
| 13 | Sin endpoint GET `/` (form HTML) | No hay UI para usar el sistema | **Crítica** (al cutover) |

---

## 4. Plan de cierre de gaps

**Orden propuesto** (de más crítico al menos):

1. **`/api/cliente?nombre=X`** — bridge que el frontend usa para buscar cliente y mostrar historial + deudas (necesario para `/venta` flow + `/pagos` flow)
2. **`/api/config`** — refactor del shape para que coincida con el original
3. **`/api/pagos`** — endpoint nuevo para pagos día posterior
4. **`/venta` corrections**:
   - Auto-crear cliente desde payload (con flag `actualizar_cliente`)
   - Distribución de crédito_aplicado por item
   - Trigger o cálculo dinámico de DEBE
5. **`/api/dashboard`** — endpoint completo con todos los KPIs
6. **`/api/libro`** — export
7. **`/gasto`** — endpoint
8. **`/`** — HTML template (preserva `formulario.html`)

---

## 5. Lecciones aprendidas

**Causa raíz del problema**: leí el código del Flask superficialmente con un solo WebFetch corto al inicio (2026-04-21). Asumí que "los endpoints son estándar CRUD" y prioricé lo que parecía más complejo (`/venta`).

**Para evitar repetirlo**:
- Antes de implementar cualquier sistema legacy: auditoría endpoint por endpoint, EXHAUSTIVA, antes de la primera línea de código nueva
- Documentar los hallazgos en un solo doc canónico (este)
- Verificar contratos HTTP exactos (request/response shapes)
- No asumir que el "diseño nuevo es claramente mejor" sin entender por qué el viejo hace algo de cierta forma

---

## 6. Cómo se mantiene este documento

- Si encuentro nuevo comportamiento del Flask original que no estaba documentado → agregar acá
- Si re-leo y encuentro detalle que se me pasó → actualizar
- Vinculado desde `docs/decisiones/0023-erp-refactor-flask-strategy.md` (referencias)

---

**Firma**: Análisis hecho por Claude Code el 2026-04-25 después de feedback de Dario que la implementación estaba "muy frágil" sin auditoría profunda. 5 WebFetches paralelos al `app.py` + 1 al `formulario.html`.
