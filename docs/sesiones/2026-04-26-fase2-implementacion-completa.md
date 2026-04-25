# Sesión 2026-04-26 — Fase 2: implementación ERP refactorizado funcional con data real

**Duración:** ~10-12 horas (sesión maratoniana)
**Tipo:** ejecución intensa (stack completo deployed) + ciclo TEST con bug fixes + auditoría profunda + backfill real
**Participantes:** Dario + Claude Code
**Fase del roadmap:** Fase 2 — implementación ~95% completada

---

## Objetivo de la sesión

Implementar el ERP refactorizado completo en VPS 3, dejarlo funcional con data real del negocio, y validar que el formulario HTML del Flask original (3500+ líneas) sigue posteando exitosamente al backend nuevo. **Modo "SEGUIREMOS HASTA QUE TENGAMOS EL ERP YA EN FUNCIONAMIENTO"** declarado por Dario al arrancar.

## Estado al cierre

**Implementación funcional al 95%.** ERP refactorizado deployed en `https://erp.livskin.site`, responde con formulario, dashboard muestra los 88 ventas y 134 clientes reales backfilleados desde el Excel productivo. CI/CD workflow cubre todo el stack con retry verify. Atomicidad de las 6 fases de venta validada por TEST cycle. Pendiente solo auth+audit middleware + tests coverage + decisión erp-staging mañana.

---

## Trabajo realizado

### 1. Stack ERP refactorizado — implementación bloque por bloque

**Migration 0001** (`815cb0b`) — 12 tablas Postgres aplicadas vía Alembic:
- `clientes` (master cliente, code `LIVCLIENT####`)
- `ventas` (master transacción, code `LIVTRAT####`/`LIVPROD####`)
- `pagos` (master pago, code `LIVPAGO####`)
- `gastos` (master gasto)
- `catalogos` (tratamientos + productos)
- `users` + `user_sessions` (preparado para ADR-0026)
- `audit_log` (preparado para ADR-0027)
- `leads` + `lead_touchpoints` + `dedup_candidates` (ADR-0011 + 0013)
- `form_submissions` (webhook entry point)

**Migration 0002** (`974ebcc`) — trigger DEBE dinámico:
- Función PL/pgSQL `recompute_venta_debe(target_cod_item TEXT)`
- Recalcula `ventas.pagado` y `ventas.debe` atómicamente al INSERT/UPDATE/DELETE de pagos
- Garantiza invariante: `ventas.pagado = SUM(pagos.monto WHERE cod_item=ventas.cod_item)`

**Models, schemas, services, routes** implementados:
- 12 models SQLAlchemy 2.0 (`models/`)
- 7 schemas Pydantic v2 (`schemas/`)
- 10 services con lógica de negocio (`services/`)
- 12 route blueprints (`routes/`)

### 2. Las 6 fases de venta del Flask original — preservadas exactas

`venta_service.save_venta()` ejecuta en orden:

1. **Generar códigos batch** (fix `next_codigos_batch` resolvió bug de duplicados)
2. **Insertar ventas** (1 fila por item, código por item)
3. **Insertar pagos normales** (efectivo, yape, plin, giro distribuidos prorrata)
4. **Aplicar crédito del cliente** (FIFO si tiene crédito acumulado)
5. **Procesar abonos explícitos** a deudas anteriores (input del usuario)
6. **Auto-aplicar leftover_cash a deudas FIFO** (NUEVA — diseñada hoy por feedback de Dario)
7. **Generar crédito si sobra** (queda como saldo a favor del cliente)

### 3. Auto-aplicar leftover con override (commit `15a52a6`)

**Problema reportado por Dario:**
> "si el 1ro de mayo viene y se va debiendo 300 por tratamiento, pero otro dia viene por un producto, y paga de mas, se esta generando un credito de 50?"

**Solución:** flag `auto_aplicar_a_deudas` (default True):
- **Default**: leftover_cash se aplica automáticamente a deuda más antigua (FIFO)
- **Override**: si Dario/doctora ponen flag a False → leftover se queda como crédito generado
- **Granular**: si hay abonos explícitos a items específicos, se hace eso primero, y el sobrante restante se auto-aplica a otras deudas (skip cod_items ya tocados)

### 4. Capa de compat form-data → JSON (commit `a1d7a14`)

El HTML original (`formulario.html`, 3500+ líneas) tiene 3 forms que POSTean `application/x-www-form-urlencoded` a `/venta`, `/pagos`, `/gasto`. **Decisión: no rewrite del HTML.**

`routes/legacy_forms.py` parsea el form-data, construye los Pydantic schemas correctos, llama a los services, y devuelve `redirect()` con flash messages — exactamente como el Flask original.

### 5. Endpoints implementados

- ✅ `/api/clientes` (CRUD + lookup) — bloques A, B
- ✅ `/api/client-lookup` (bridge digital→físico, vertical slice de Fase 1) — `c2b68c4`
- ✅ `/api/catalogo` (tratamientos + productos) — bloque A
- ✅ `/api/config` (constantes globales) — bloque A
- ✅ `/api/dashboard` (KPIs + aging + comparativas mes anterior) — bloque D `12d8413`
- ✅ `/api/gastos` — bloque C
- ✅ `/api/pagos` (día posterior, con auto-aplicación FIFO) — bloque C `07ca43d`
- ✅ `/api/libro` (export plano para Excel/Sheets) — bloque E `7facbc0`
- ✅ `/venta`, `/pagos`, `/gasto` (legacy form endpoints) — bloque F `a1d7a14`
- ✅ `/`, `/ping` (views + health)

### 6. Bugs detectados y corregidos (TEST cycle exhaustivo)

Tras instrucción de Dario "TODOS LOS CASOS HAY QUE PROBAR":

| Bug | Detección | Fix | Commit |
|---|---|---|---|
| Códigos duplicados en venta multi-item (3 items → todos `LIVTRAT0001`) | TEST E | `next_codigos_batch(count)` genera N consecutivos en un lookup | `1c4efb3` |
| Valores negativos aceptados (precio -100 creó venta válida) | TEST schema | Pydantic `Field(ge=0)` en todos campos numéricos | `7a4010a` |
| **Atomicidad rota**: try/except dentro de `session_scope` cachaba excepciones → commit corrupto | TEST U (abono fantasma) | Refactor: try/except FUERA del `with session_scope()` en route handlers | `6542ee5` |
| Abono fantasma (cod_item inexistente aceptado) | TEST U | Excepción `AbonoCodItemInvalido` en `pago_service.create_pago()` | `6eb4f81` |
| Doble counting `credito_aplicado` en `cliente.get_full_history()` | Análisis dashboard | Usar `todos_pagos` para per-item, `pagos_for_display` (excluye credito_aplicado) para agregado | `974ebcc` |
| Race condition CI/CD vs rebuild manual (verify falló mientras erp-flask se rebuildaba) | Workflow run que llegó como mensaje | Workflow ahora maneja erp-flask + retry 3× sleep 5s | `7eb2d63` |

### 7. Auditoría profunda del Flask original

**Feedback crítico de Dario al inicio:**
> "ME PARECE MUY DUDOSO QUE NO HAYAS TENIDO CLARO DE QUE IBA LA PESTANA PAGOS"
> "no se si has leido mi codigo bien antes de hacer esta implementacion, me parece muy dudoso..."

**Acción:** auditoría con 5 WebFetches paralelos al repo `DarioUrrutia/formulario-livskin`. Output: `docs/erp-flask-original-deep-analysis.md` mapea **13 gaps** entre original y refactor.

**Bloques de cierre A → F**:
- A — endpoints feeders del frontend (config + cliente)
- B — auto-create cliente desde POST /venta + crédito por item + trigger DEBE
- C — `/api/gastos` + `/api/pagos` (día posterior)
- D — `/api/dashboard` con KPIs + aging + comparativas
- E — `/api/libro` export plano
- F — HTML template + capa compat form-data

**Cerrados:** 11 de 13 gaps.
**Diferidos no críticos:** métodos pago primera fila (cosmético), multi-currency por item, categoría `__otro__` libre.

### 8. Nginx config — proxy_pass al container

`infra/docker/nginx-vps3/sites/erp.livskin.site.conf` cambió de maintenance page estática a:
```nginx
location / {
    proxy_pass http://erp-flask:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 5s;
    proxy_read_timeout 30s;
    proxy_buffering on;
    proxy_buffers 16 16k;
    proxy_buffer_size 32k;  # templates ~180KB
    client_max_body_size 4m;  # forms con muchos items
}
```

`erp-staging.livskin.site` sigue con maintenance page — **decisión pendiente para mañana 2026-04-27**.

### 9. CI/CD workflow extendido (commit `7eb2d63`)

`.github/workflows/deploy-vps3.yml` ahora cubre:
- **Long-running services** (postgres-data, embeddings-service, nginx-vps3): `up -d --quiet-pull`
- **ERP Flask**: `up -d --build` (rebuild de imagen ante cambios)
- **One-shot images** (alembic-erp, brain-tools): `build only` (sin run)
- **Nginx reload**: `nginx -t` + `nginx -s reload` (sin downtime)
- **Verify retry**: 3 intentos con sleep 5s, sleep inicial 20s, ambas URLs públicas

### 10. Backfill REAL del Excel productivo (commit `a6deccb`)

`infra/docker/erp-flask/scripts/backfill_excel.py` — script ad-hoc MVP de ADR-0025:
- Lee `Datos_Livskin_2026-04-25.xlsx` (gitignored, 88 ventas + 84 pagos + 134 clientes + 55 catálogos)
- Preserva códigos originales (`LIVCLIENT####`, `LIVTRAT####`, `LIVPAGO####`)
- Normaliza phones a E.164, emails a lowercase + sha256 hash, fechas
- Infiere `tipo_pago` desde notas/categoría del Excel (normal, credito_aplicado, abono_deuda, credito_generado)
- 4 hojas procesadas: Clientes → Ventas → Pagos → Gastos

**Resultado ejecución:** 134 clientes + 88 ventas + 84 pagos insertados sin errores.

**Decisión MVP-speed (Dario aprobó):** saltar plumbing sintético, ir directo a data real. Razón: script idempotente + migration 0001 puede recrear schema limpio si falla + Render sigue intacto como producción.

---

## Decisiones tomadas

### 1. Auto-aplicar leftover_cash a deudas FIFO con override
Default automático (FIFO desde deuda más antigua), con flag `auto_aplicar_a_deudas` para override en momento de la venta. Captura el comportamiento esperado del negocio sin sorprender al operador.

### 2. No rewrite del HTML — capa compat form-data
El HTML del Flask original (3500+ líneas) sigue tal cual. Routes nuevas en `legacy_forms.py` parsean form-data y delegan a services. Preserva trabajo previo + bajo riesgo de regresión visual.

### 3. Backfill directo data real (saltar sintético)
Por velocidad MVP. Posible porque: script idempotente, schema recreable, Render intacto. Acelera validación funcional sin riesgo a producción.

### 4. Try/except FUERA de `session_scope` (regla de oro)
Si una excepción se cacha DENTRO del context manager, el commit ocurre con estado parcial → corrupción silenciosa. Regla nueva: try/except solo en routes, alrededor del `with session_scope()`.

### 5. Diferir 2 gaps cosméticos
Métodos pago primera fila + multi-currency por item: no críticos para operación, se reactivan si la doctora reporta fricción específica.

---

## Capacidades nuevas mapeadas para el 5to agente (Infra+Security)

Cada incidente de hoy mapea a una capacidad concreta del agente futuro (memoria `project_infra_security_agent` actualizada):
- CI/CD orchestration con detección de race conditions deploy vs manual
- Backfill operations con dry-run + idempotency checks
- Public endpoint health monitoring con retry escalonado + content validation
- Trigger DEBE dinámico como invariante crítico monitoreado
- Detección de session_scope leaks vía lint custom
- Race condition detection en códigos secuenciales
- Container image hygiene (SHA divergence detection)
- Code archaeology service (auditoría profunda original vs refactor)
- Lock detection en migrations Alembic
- Forward-only migration validation

---

## Estado del repo al cierre

**8 commits hoy:**
```
7eb2d63 feat(ci): workflow CI/CD cubre erp-flask + alembic + brain-tools + nginx reload
a6deccb feat(erp-flask): script ad-hoc backfill_excel.py para data inicial
4dd18bf feat(nginx): erp.livskin.site -> proxy_pass container erp-flask
a1d7a14 feat(erp-flask): bloque F — HTML template + capa compat form-data
7facbc0 feat(erp-flask): bloque E — /api/libro export plano
12d8413 feat(erp-flask): bloque D — /api/dashboard con KPIs + aging + comparativas
07ca43d feat(erp-flask): bloque C — /api/gastos + /api/pagos (dia posterior)
15a52a6 feat(venta-service): auto-aplicar leftover a deudas FIFO + override
```

**Más bug fixes anteriores en la sesión:**
```
974ebcc feat(erp-flask): bloque B — auto-create cliente + credito por item + trigger DEBE
8ea44ca feat(erp-flask): bloque A — endpoints feeders del frontend (config + cliente)
6542ee5 fix(routes): try/except FUERA de session_scope para que rollback funcione
6eb4f81 fix(pago-service): validar cod_item existe en abono_deuda (no abono fantasma)
7a4010a fix(venta-schema): rechazar valores negativos en precios/pagos (ge=0)
1c4efb3 fix(venta-service): generar codigos en batch por prefijo
be8e1e6 feat(erp-flask): VentaService con las 6 fases + Catalogo + Pago services
1820d19 feat(erp-flask): ClienteService + endpoints CRUD /api/clientes
```

**Plus** docs (master plan, memorias, backlog, este log) + commit final de cleanup.

---

## Verificación end-to-end

✅ `https://erp.livskin.site` responde HTTP 200
✅ Formulario carga (HTML legacy preservado)
✅ Dashboard muestra los 88 ventas y 134 clientes reales backfilleados
✅ CI/CD workflow corre verde sobre push a main
✅ Trigger DEBE dinámico verifica invariante en cada pago insertado
✅ Las 6 fases de venta atómicas (rollback funciona si alguna falla)

---

## Próxima sesión 2026-04-27

**Bloque 1 — Decisión rápida:**
1. Decidir destino de `erp-staging.livskin.site` (A eliminar / B alias mismo container / C staging real con DB separada). Recomendación inicial: A para Fase 2-5, C en Fase 6.

**Bloque 2 — Cerrar Fase 2 al 100%:**
2. Implementar auth bcrypt middleware + login/logout (ADR-0026)
3. Implementar audit log middleware (ADR-0027) — tabla ya existe, falta after-request hook
4. Tests poblados a coverage ≥75%

**Bloque 3 — Si llega aprobación Meta API:**
5. Vtiger configurado + Conversation Agent inicial (Fase 4 puede arrancar en paralelo)

---

## Métricas de la sesión

- **Líneas de código nuevas:** ~3,500 (estimado entre models + schemas + services + routes + tests stubs + migrations + workflow + nginx config + script backfill)
- **Bugs detectados y corregidos:** 6
- **Commits:** 8 features + 6 fixes/bloques anteriores = 14
- **Decisiones documentadas:** 5
- **ADRs implementados:** 0023 (refactor) parcial, 0024 (strangler) marcado como dormant standby, 0025 (backfill) MVP version aplicada
- **ADRs pendientes implementación:** 0026 (auth), 0027 (audit)
- **Data real importada:** 134 clientes + 88 ventas + 84 pagos
- **URLs públicas funcionales:** 1 (erp.livskin.site) + 1 pendiente (erp-staging decision)

---

## Lecciones de hoy

1. **"Lectura superficial inicial" es un riesgo real**: Dario detectó que no había leído el Flask original con suficiente profundidad. La auditoría detallada con `WebFetch` paralelo del repo descubrió 13 gaps. **Lección:** ante refactor de código existente, leer el original ANTES de implementar — no después.

2. **TEST cycle exhaustivo descubre bugs invisibles**: 6 bugs corregidos hoy, todos detectados por TEST cycle. Ninguno habría aparecido en happy path. **Lección:** "TODOS LOS CASOS HAY QUE PROBAR" no es exageración.

3. **Atomicidad de transacciones es crítica y sutil**: el bug try/except dentro de `session_scope` es el clásico que se ve en post-mortems de outages reales. **Regla:** try/except FUERA del context manager, siempre.

4. **MVP-speed bien aplicado**: saltar el plumbing sintético al backfill real fue decisión correcta para esta sesión específica (script idempotente, Render intacto). **No es regla general** — es contextual a esta combinación de factores.

5. **Cada incidente operativo es spec del 5to agente**: las 10+ capacidades nuevas mapeadas hoy no son especulación sino respuesta a problemas observados. El agente Infra+Security se construye sobre incidentes reales, no sobre best practices abstractos.
