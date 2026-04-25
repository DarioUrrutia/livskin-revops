# ADR-0023 — ERP refactor Flask: estrategia de modernización

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-25
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos + Infra

---

## 1. Contexto

El ERP actual (`formulario-livskin.onrender.com`) es una aplicación Flask que funciona pero tiene varios problemas estructurales que impiden integrarlo al sistema RevOps profesional que se está construyendo:

**Stack actual** (analizado el 2026-04-21 vía repo público):
- 1 archivo monolítico `app.py` (~1000+ líneas) que mezcla rutas + lógica de negocio + acceso a datos
- Google Sheets como DB (vía gspread + service account) — cuello de botella reconocido (ADR-0002)
- Caché en memoria 90s para mitigar latencia de Sheets API
- **Sin autenticación** (todos los endpoints abiertos al público) — riesgo crítico
- **Sin audit log** (no hay traza de cambios)
- Sin tests automatizados
- Sin tipos estáticos / validación de I/O
- Lógica de negocio densa (las 6 fases de guardado de venta, distribución proporcional de pagos, manejo de créditos/abonos/deudas) preservada en código procedural difícil de testear

**Lo que NO se puede cambiar** (constraints duros):
- Frontend HTML (`templates/formulario.html`) — comerciales lo conocen y lo usan diariamente. Cambiar UX = romper productividad de la clínica
- Lógica de negocio del Flask — las 6 fases de guardado de venta funcionan correctamente; refactorizarlas es rewrite no refactor (riesgo alto de bugs en cutover)
- Endpoints HTTP existentes (rutas, métodos, request/response shapes) — el frontend HTML hace POSTs/GETs específicos

**Lo que SÍ se puede cambiar libremente**:
- Storage layer (Sheets → Postgres)
- Estructura interna del código (split modular)
- Capa de auth + audit
- Tests + tipos + validación

Referencias:
- ADR-0011 v1.1 (modelo de datos destino)
- ADR-0013 v2 (dedup + identity graph)
- ADR-0015 (Source of Truth — ERP es master de cliente + transacciones)
- ADR-0002 (3 VPS + VPC + decisión de Postgres self-hosted)
- ADR-0024 (strangler fig — cómo migra a producción) — siguiente
- ADR-0025 (backfill desde Sheets) — siguiente
- ADR-0026 (auth bcrypt + 2 cuentas) — siguiente
- ADR-0027 (audit log) — siguiente
- Memorias `project_erp_migration`, `project_real_data_source`, `feedback_production_preservation`

---

## 2. Opciones consideradas

### Opción A — Refactor profundo del Flask con modernización stack (RECOMENDADA)
Preservar Flask + frontend + lógica de negocio (las 6 fases). Reescribir capa de datos (gspread → SQLAlchemy + Postgres). Introducir Pydantic para validación, structlog para observabilidad, pytest para tests, mypy para tipos. Reorganizar código en estructura modular (models / services / routes / middleware). Agregar auth y audit como middlewares.

### Opción B — Rewrite completo en FastAPI
Tirar Flask, empezar desde cero en FastAPI moderno. Frontend nuevo (React o similar). Modelo más limpio, más rápido.

### Opción C — Mantener Flask + Sheets, solo agregar capa intermedia
Dejar el ERP actual como está, agregar un proxy/middleware en VPS 3 que sincroniza con Postgres para queries analíticas. ERP sigue escribiendo a Sheets.

### Opción D — Migrar a una solución SaaS comercial (Salesforce, HubSpot, Bitrix24)
Reemplazar todo por un ERP+CRM pago.

---

## 3. Análisis de tradeoffs

| Dimensión | A (refactor profundo) | B (rewrite FastAPI) | C (capa intermedia) | D (SaaS pago) |
|---|---|---|---|---|
| Costo | $0 (self-hosted) | $0 (self-hosted) | $0 | $50-300/mo |
| Tiempo implementación | 2-3 semanas | 6-8 semanas | 1 semana | 1-2 semanas + curva aprendizaje |
| Preserva UX comerciales | **Sí** | No (UI rehecha) | Sí | No |
| Preserva lógica negocio compleja | **Sí** (refactor preserve) | Riesgo de bugs en rewrite | Sí | Hay que recrear |
| Resuelve cuello de botella Sheets | **Sí** (Postgres) | Sí | Parcial | Sí |
| Auth + Audit profesionales | **Sí** | Sí | No | Sí (built-in) |
| Reversibilidad | Alta | Baja (rewrite total) | Alta | Bajísima (vendor lock-in) |
| Portfolio value | Alto | Alto | Bajo | Nulo (no es trabajo nuestro) |
| Alineación principio 8 (no servicios pagos) | ✅ | ✅ | ✅ | ❌ |
| Alineación principio 6 (respeto comerciales) | ✅ | ❌ (UX cambia) | ✅ | ❌ (UX cambia totalmente) |
| Alineación principio 1 (ejecutable > ideal) | ✅ | ❌ (rewrite ambicioso) | ✅ | ✅ |

---

## 4. Recomendación

**Opción A — Refactor profundo del Flask con modernización del stack.**

Razones:
1. **Preserva todo lo que NO debe cambiar**: frontend HTML, UX comercial, lógica de las 6 fases de venta. Alinea con principio 6 y mandato explícito de Dario (2026-04-21, 2026-04-25).
2. **Resuelve los problemas estructurales reales**: storage, auth, audit, tests, tipos.
3. **Costo cero adicional**: stack 100% self-hosted, no introduce dependencias pagas (principio 8).
4. **Reversible**: si algún componente del refactor no funciona, se aísla y reemplaza sin afectar el resto.
5. **Portfolio value alto**: refactor profesional preservando producción es exactamente el caso de estudio que Dario quiere mostrar.

**Tradeoff aceptado**: el refactor toma 2-3 semanas (vs 1 semana de Opción C). Lo aceptamos porque Opción C deja problemas estructurales sin resolver (sin auth, sin audit, Sheets sigue cuello de botella).

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-25 por Dario.

**Razonamiento de la decisora** (síntesis de varias sesiones):
> "El frontend se preserva estricto porque los comerciales ya saben usarlo. Backend tiene que acoplarse a nuestras necesidades sin sobre-complicar. Esto debe escalar con el tiempo pero no ser algo ultra-complejo ahora."

---

## 6. Diseño técnico del refactor

### 6.1 Stack tecnológico

| Capa | Tecnología | Versión | Razón |
|---|---|---|---|
| Lenguaje | Python | 3.13.x | Mismo que Flask actual, continuidad |
| Web framework | Flask | 3.x | Preservado del original (no rewrite) |
| ORM | SQLAlchemy | 2.0+ | Estándar Python, mature, soporte Postgres excelente |
| Validación I/O | Pydantic | v2 | Schemas tipados request/response |
| Migrations | Alembic | 1.13+ | Ya configurado en `alembic-erp/` (Fase 1) |
| DB | Postgres | 16 | Ya en VPS 3 (Fase 1) |
| Logs | structlog | latest | JSON estructurado, observabilidad desde día 1 |
| Tests | pytest + pytest-cov | latest | Estándar Python testing |
| Format/lint | black + ruff | latest | Estándar profesional |
| Type checking | mypy strict | latest | Detecta errores antes de runtime |
| Pre-commit hooks | pre-commit | latest | Calidad antes de cada commit |
| Web server | gunicorn | latest | Mismo que Flask actual |
| Container | Docker + docker-compose | latest | Consistencia con Fase 1 |

### 6.2 Arquitectura de capas (separation of concerns)

```
┌────────────────────────────────────────────┐
│  HTTP Layer (Flask routes)                 │
│  - Recibe requests, parsea body            │
│  - Valida schema con Pydantic              │
│  - Llama al service apropiado              │
│  - Devuelve response (HTML o JSON)         │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  Service Layer (business logic)            │
│  - VentaService.save_venta() — 6 fases     │
│  - PagoService — créditos, abonos, deudas  │
│  - DedupService — phone, email, nombre     │
│  - ClienteService, LeadService, GastoService│
│  - 100% testeable sin DB ni HTTP           │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  Repository Layer (DB access via SQLAlchemy)│
│  - ClienteRepo, VentaRepo, etc.            │
│  - Transactions, queries, writes           │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  Postgres (livskin_erp database)           │
└────────────────────────────────────────────┘

[Cross-cutting: middleware (auth, audit, normalize)]
```

**Cambio vs actual**: hoy `app.py` mezcla las 4 capas en línea. Refactor las separa, cada una testeable de forma aislada.

### 6.3 Estructura de archivos

```
erp-flask/
├── app.py                       # Flask init, middleware setup, route registration (~50 líneas)
├── config.py                    # Pydantic Settings, env vars
├── models/                      # SQLAlchemy models (1 archivo por entidad)
│   ├── __init__.py
│   ├── cliente.py
│   ├── lead.py
│   ├── lead_touchpoint.py
│   ├── venta.py
│   ├── pago.py
│   ├── gasto.py
│   ├── form_submission.py
│   ├── catalogo.py
│   ├── dedup_candidate.py
│   └── audit_log.py
├── schemas/                     # Pydantic models (request/response validation)
│   ├── __init__.py
│   ├── cliente.py
│   ├── lead.py
│   ├── venta.py
│   ├── pago.py
│   └── gasto.py
├── services/                    # Business logic (testeable sin DB ni HTTP)
│   ├── __init__.py
│   ├── venta_service.py         # Las 6 fases preservadas exactas
│   ├── pago_service.py          # Créditos, abonos, distribución proporcional
│   ├── cliente_service.py
│   ├── lead_service.py
│   ├── dedup_service.py         # Algoritmo ADR-0013 v2
│   ├── gasto_service.py
│   ├── client_lookup_service.py # Bridge digital→físico (ADR-0011 v1.1, 0013 v2)
│   └── normalize_service.py     # phone, email, nombre
├── repositories/                # DB access layer
│   ├── __init__.py
│   └── (un archivo por entidad)
├── routes/                      # Flask blueprints (thin handlers)
│   ├── __init__.py
│   ├── venta.py
│   ├── gasto.py
│   ├── pagos.py
│   ├── cliente.py
│   ├── api_dashboard.py
│   ├── api_libro.py
│   ├── api_config.py
│   ├── api_client_lookup.py     # NUEVO: GET /api/client-lookup?phone=X
│   ├── webhook_form_submit.py   # NUEVO: POST /webhook/form-submit
│   ├── webhook_whatsapp.py      # NUEVO: POST /webhook/whatsapp
│   └── admin.py                 # /actualizar-headers, /ping
├── middleware/
│   ├── __init__.py
│   ├── auth.py                  # bcrypt + sessions (ADR-0026)
│   ├── audit.py                 # write to audit_log (ADR-0027)
│   └── error_handler.py         # 4xx/5xx structured responses
├── templates/
│   └── formulario.html          # PRESERVADO 100% en estructura visual + comportamiento
├── static/
│   ├── logo.png                 # Preservado
│   └── client_lookup.js         # NUEVO: AJAX para banner "Lead detectado"
├── tests/
│   ├── unit/
│   │   ├── test_venta_service.py    # Las 6 fases — coverage máxima aquí
│   │   ├── test_pago_service.py
│   │   ├── test_dedup_service.py
│   │   ├── test_normalize.py
│   │   └── ...
│   ├── integration/
│   │   ├── test_routes_venta.py     # POST /venta end-to-end
│   │   ├── test_routes_api.py
│   │   └── test_client_lookup.py
│   └── conftest.py
├── alembic/                     # Reusa el alembic-erp ya creado (Fase 1)
│   ├── env.py
│   └── versions/
│       └── 0001_initial_schema.py  # PRIMER migration (Fase 2 implementación)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml               # configs de mypy/black/ruff/pytest
├── .pre-commit-config.yaml
├── .env.example
└── README.md
```

### 6.4 Endpoints HTTP

**Preservados del Flask actual (idéntico contract)**:

| Ruta | Método | Función |
|---|---|---|
| `/` | GET | Carga formulario.html + clientes + config |
| `/venta` | POST | Las 6 fases: códigos → ventas → pagos → crédito excedente → crédito aplicado → abonos |
| `/gasto` | POST | Registrar gasto |
| `/pagos` | POST | Registrar pago manual (multi-item) |
| `/cliente` | GET (JSON) | Historial de cliente, calcula debe |
| `/api/dashboard` | GET (JSON) | KPIs financieros |
| `/api/libro` | GET (JSON) | Export completo |
| `/api/config` | GET (JSON) | Catálogos (Listas) |
| `/actualizar-headers` | GET | Admin (preservado por compatibilidad, deprecable) |
| `/ping` | GET | Keep-alive (preservado) |

**Nuevos (críticos para Fase 4)**:

| Ruta | Método | Función | ADR |
|---|---|---|---|
| `/api/client-lookup?phone=X` | GET | Bridge digital→físico: busca match en `clientes` y `leads` por phone | 0011, 0013 |
| `/webhook/form-submit` | POST | Recibe submit de landing → crea lead + dispara WA template | 0011, 0013 |
| `/webhook/whatsapp` | POST | Recibe WA Cloud API inbound → dedup + lifecycle | 0011, 0013 |
| `/login` | POST | Auth (ADR-0026) | 0026 |
| `/logout` | POST | Cierre de sesión (ADR-0026) | 0026 |

### 6.5 Tests — coverage objetivo: 75%

Distribución del 75%:

| Capa | Coverage objetivo | Por qué |
|---|---|---|
| Services (business logic) | **90%+** | Lógica densa: 6 fases, créditos, dedup. Tests aquí valen oro. |
| Models / schemas | 60% | Tests obvios; validar serialización/deserialización. |
| Repositories | 70% | Queries complejas; tests con DB en memoria (SQLite) o testcontainers. |
| Routes | 60% | Integration tests para happy path + error cases principales. |
| Middleware | 80% | Auth y audit son críticos. |
| Utils / config | 30% | Trivial, no vale el costo testear. |

**Coverage promedio del codebase**: ≥75%.

Tests que NO se hacen en MVP:
- Load testing (perf bajo carga) — diferido a Fase 6 si volumen lo justifica
- Property-based testing (Hypothesis) — overkill para MVP
- E2E browser testing (Selenium / Playwright) — diferido; el form HTML es estático y simple

### 6.6 Eliminaciones del código actual

**Removidos en refactor** (con justificación):

| Eliminado | Por qué |
|---|---|
| Toda referencia a `gspread` y Google Sheets | DB nueva = Postgres |
| `_data_cache`, `_worksheets_cache`, `_invalidate_cache()` (caché 90s) | Postgres es <10ms; caché era band-aid de Sheets API |
| `os.environ.get("FLASK_SECRET_KEY", "livskin2024-dev-only")` con default inseguro | Auth nueva con secret obligatorio (ADR-0026) |
| Generación de códigos via "leer max + counter en memoria" | Reemplazado por sequences nativas de Postgres |
| Acceso abierto sin auth | Login obligatorio (ADR-0026) |

### 6.7 Preservaciones críticas (NON-NEGOTIABLE)

✅ `formulario.html` — estructura visual y campos preservados al 100%; única adición permitida es banner condicional pequeño "Lead detectado" cuando `/api/client-lookup` retorna match (mejora invisible si no aplica)

✅ Las 6 fases de `save_venta()` — lógica preservada palabra-por-palabra dentro de `VentaService.save_venta()`. Tests verifican equivalencia con flujo del Render

✅ Distribución proporcional cuando `sum(pagos_items) > total_pagado_hoy` — preservada exacta

✅ 4 tipos de Pago (`normal`, `credito_generado`, `credito_aplicado`, `abono_deuda`) — preservados

✅ Cálculo dinámico de `debe` por cliente — preservado, ahora desde Postgres en lugar de Sheets

✅ Endpoints existentes — mismo URL, método, request body, response body shape

### 6.8 Deployment

**Container Docker** corriendo en VPS 3:
- `infra/docker/erp-flask/` (nueva carpeta, paralela a las de Fase 1)
- `docker-compose.yml` con servicio `erp-flask` en red `data_net`
- `gunicorn` con 2 workers (RAM disponible en VPS 3 lo permite)
- `nginx-vps3` ya tiene `proxy_pass` configurado a `erp.livskin.site` (Fase 1) — solo redirigir a este container
- Connection pool a Postgres configurado (SQLAlchemy `pool_size=5, max_overflow=10`)

**Estado durante Fases 2-5: dormant standby**
- Container corriendo pero NO recibiendo tráfico de comerciales
- Solo accesible para Dario via auth (ADR-0026) para testing manual
- Render sigue siendo producción (memoria `feedback_production_preservation`)

**Cutover (Fase 6)**: ver ADR-0024.

---

## 7. Consecuencias

### Desbloqueado
- Implementación de Fase 2 puede arrancar inmediatamente con base clara
- Alembic migration `0001_initial_schema.py` puede crearse con todas las tablas de ADR-0011 v1.1
- Endpoints `/api/client-lookup` + webhooks habilitan bridge digital→físico (Fase 4)
- ADR-0024 (strangler fig) tiene sistema concreto que migrar
- ADR-0025 (backfill) sabe a qué schema poblar
- ADR-0026 + 0027 saben dónde y cómo integrarse

### Bloqueado / descartado
- Opción B (rewrite total) descartada — alto riesgo, bajo retorno
- Opción C (capa intermedia) descartada — no resuelve auth ni audit
- Opción D (SaaS pago) descartada — viola principio 8

### Implementación derivada
- [ ] Crear estructura de carpetas `erp-flask/` (Fase 2 semana 3)
- [ ] Configurar `pyproject.toml` con mypy strict, black, ruff, pytest
- [ ] Configurar `.pre-commit-config.yaml`
- [ ] Crear `alembic-erp/versions/0001_initial_schema.py` con 9 tablas de ADR-0011 v1.1
- [ ] Implementar models SQLAlchemy (1 por entidad, 9 archivos)
- [ ] Implementar schemas Pydantic
- [ ] Implementar services (VentaService, PagoService, DedupService primero — son los más densos)
- [ ] Implementar routes preservando contract HTTP idéntico
- [ ] Implementar middleware auth (post-ADR-0026)
- [ ] Implementar middleware audit (post-ADR-0027)
- [ ] Tests unitarios y de integración (coverage ≥75%)
- [ ] Dockerfile + docker-compose.yml
- [ ] Script de smoke test contra el ERP corriendo en VPS 3
- [ ] CI/CD GitHub Actions: corre tests + mypy + linters en PR

### Cuándo reabrir
- Si Postgres resulta ser cuello de botella inesperado (>1s queries) — improbable dado volumen Livskin
- Si lógica de las 6 fases requiere cambios de negocio (nuevo método de pago, nueva moneda, etc.) — reabrir para incorporar
- Si volumen requiere FastAPI async (probable >5,000 ventas/día, no aplica MVP)
- Cuando llegue versión 4.x de Flask con cambios breaking — reabrir compatibilidad
- Revisión trimestral obligatoria: 2026-07-25

---

## 8. Changelog

- 2026-04-25 — v1.0 — Creada y aprobada (MVP Fase 2). Cierra la primera de las 5 ADRs huérfanas (0023-0027) que faltaban para completar definición de Fase 2.
