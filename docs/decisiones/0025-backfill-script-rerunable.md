# ADR-0025 — Script de backfill re-ejecutable (Excel/Sheets → Postgres)

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-25
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2 (implementación) + Fase 6 (ejecución cutover)
**Workstream:** Datos

---

## 1. Contexto

ADR-0023 define el ERP refactorizado (Postgres como DB). ADR-0024 define cómo se migra de Render a VPS 3. Este ADR define **cómo se carga la data del Sheets de producción al Postgres del nuevo ERP** — el "puente" entre ambos sistemas.

**Constraints que aplican**:
- El sistema actual (Render + Google Sheets) se mantiene intacto durante toda la migración (memoria `feedback_production_preservation`)
- La data real es la que vive en el Sheets actual, no el Excel viejo (memoria `project_real_data_source`)
- El método de transferencia en MVP es **export manual** que Dario hace (Excel `.xlsx`), no API directa
- El script debe ser usable múltiples veces: durante desarrollo (Fases 2-5) Y en cutover (Fase 6)
- Dario es principiante en implementación → procedimiento simple, comandos claros (memoria `feedback_explain_to_beginner`)

**Estado actual del archivo de data**: `docs/Datos_Livskin_2026-04-25.xlsx` (gitignored por PII), 5 hojas (Ventas 88, Pagos 84, Clientes 135, Gastos 0, Listas 55).

Referencias:
- ADR-0011 v1.1 (modelo de datos destino — 9 tablas)
- ADR-0013 v2 (dedup + normalización)
- ADR-0014 (naming conventions LIVXXXX####)
- ADR-0023 (ERP refactor — define dónde corre el código)
- ADR-0024 (strangler fig — cuándo se ejecuta el backfill final)
- Memorias `project_backfill_decisions`, `project_real_data_source`, `feedback_production_preservation`

---

## 2. Opciones consideradas

### Opción A — Script Python en container Docker, lee Excel local, idempotente con 3 modos (RECOMENDADA)
Script profesional como todos los containers del proyecto. Lee `.xlsx`, escribe a Postgres usando los mismos models SQLAlchemy del ERP. 3 modos de ejecución: dry-run, apply, verify. Logs detallados. INSERT-only en dev, UPSERT en cutover.

### Opción B — Migration de Alembic con datos
Empaquetar la carga inicial como una Alembic migration. Postgres se popula al hacer `alembic upgrade`.

### Opción C — Carga manual via SQL inserts
Generar un `.sql` con `INSERT INTO ...` por cada fila y ejecutarlo con `psql`.

### Opción D — Acceso directo via Google Sheets API
Saltarse el Excel intermedio. Script lee Sheets vía service account credentials.

---

## 3. Análisis de tradeoffs

| Dimensión | A (Docker + Excel) | B (Alembic data) | C (SQL inserts) | D (Sheets API directo) |
|---|---|---|---|---|
| Complejidad implementación | Media | Baja | Muy baja | Alta (setup credenciales) |
| Re-ejecutable (idempotente) | **Sí** (UPSERT) | No (migrations one-shot) | No (duplica si corre 2 veces) | Sí |
| Modos múltiples (dry-run/apply/verify) | **Sí** | No | No | Sí |
| Manejo de errores en filas | **Sí** (continue + log) | No (fail all) | No (fail all) | Sí |
| Reusable para cutover | **Sí** | No (mezcla schema con data) | Sí (re-generando SQL) | Sí |
| Testeable | **Sí** | Limitado | No | Sí |
| Aprovecha models del ERP | **Sí** | Parcial | No (raw SQL) | Sí |
| Setup técnico para Dario | Medio (1 ssh + 1 cmd) | Bajo | Bajo (psql) | **Alto** (Google Cloud setup) |
| Apropiado para volumen Livskin (cientos de filas) | **Excelente** | OK | OK | Overkill |
| Alineación con `feedback_production_preservation` | ✅ | ✅ | ✅ | ⚠️ (requiere credenciales del Sheets en VPS 3) |

---

## 4. Recomendación

**Opción A — Script Python en container Docker, lee Excel, 3 modos.**

Razones:
1. **Idempotente y reusable**: misma herramienta funciona en dev, refresh durante desarrollo, y cutover final
2. **Manejo robusto de errores**: continúa con el resto si una fila falla → no pierde tiempo con runs incompletos
3. **Reusa los models del ERP**: single source of truth, se actualiza automáticamente con migrations
4. **Mismo patrón que el resto del stack**: alembic-erp, brain-tools, erp-flask — todos containers Docker en VPS 3
5. **Setup mínimo para Dario**: dos comandos SSH para ejecutar; cero setup de Google Cloud
6. **Testeable**: tests unitarios validan transformaciones (encoding, normalización, mapeo)

**Tradeoff aceptado**: Opción D (API directa) es más "profesional" pero requiere setup de Google Cloud Service Account que es overhead técnico ahora. El export manual es simple y funciona. Opción D queda como mejora futura si el manual se vuelve doloroso.

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-25 por Dario.

**Razonamiento de la decisora:**
> "OK está bien, igual todo esto debe quedar en una memoria, porque incluso estoy pensando que deberemos tener un agente especializado en el mantenimiento de toda nuestra infraestructura."

(Dario aprobó las 11 decisiones técnicas que se desglosan abajo y propuso adicionalmente que en el futuro un Agente de Infra+Security ejecute este script con autorización — ver memoria `project_infra_security_agent`.)

---

## 6. Diseño técnico del script

### 6.1 Las 11 decisiones técnicas (ya validadas)

| # | Decisión | Detalle |
|---|---|---|
| 1 | Idempotente | Re-ejecutable N veces sin duplicar (UPSERT por código único LIVXXXX####) |
| 2 | 3 modos | `dry-run` / `apply` / `verify` |
| 3 | INSERT-only en dev, UPSERT en cutover | Flag `--mode-write=insert` (default dev) o `--mode-write=upsert` (cutover) |
| 4 | Logs detallados por ejecución | `infra/scripts/backfill-logs/<timestamp>.log` |
| 5 | Importar datos "raros" tal cual | Sin limpiar nombres "???", encoding, etc. |
| 6 | Container Docker en VPS 3 | `infra/docker/erp-backfill/` |
| 7 | Errores en filas = log + continuar | NO parar al primer error; reporte final con problemas |
| 8 | Orden de carga (FK deps) | Catálogos → Catálogos NUEVOS → Clientes → Ventas → Pagos |
| 9 | Tablas vacías post-backfill | leads, lead_touchpoints, form_submissions, dedup_candidates, audit_log, users, gastos |
| 10 | Reusa models del ERP | Importa `erp-flask/models/` |
| 11 | Modo verify | Conteos + sumas revenue + catálogos completos + no-huérfanos + sample 5 random |

### 6.2 Estructura del container

```
infra/docker/erp-backfill/
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh             # Dispatcher: dry-run | apply | verify | help
├── backfill.py               # Lógica principal
├── readers/
│   ├── excel_reader.py       # openpyxl para leer .xlsx
│   └── sheets_reader.py      # FUTURO: Google Sheets API (Opción D)
├── transformers/
│   ├── catalogos.py          # Hoja Listas → tabla catalogos
│   ├── clientes.py           # Hoja Clientes → tabla clientes (con defaults legacy)
│   ├── ventas.py             # Hoja Ventas → tabla ventas (preservando flat 1-fila-1-item)
│   ├── pagos.py              # Hoja Pagos → tabla pagos (preservando 4 tipos)
│   └── catalogos_nuevos.py   # Hardcode: fuente, canal_adquisicion, metodo_pago
├── verifiers/
│   ├── count_check.py        # Conteos coinciden Excel vs Postgres
│   ├── sum_check.py          # SUM(total) coincide
│   ├── orphan_check.py       # No huérfanos en FK
│   └── sample_check.py       # 5 random clients deep-equal
├── tests/
│   ├── test_excel_reader.py
│   ├── test_transformers.py
│   ├── test_idempotence.py   # Run 2x → mismo resultado
│   └── ...
└── README.md
```

**Reusa**: imports desde `erp-flask/models/` para los modelos SQLAlchemy.

### 6.3 Comandos canónicos

**Conexión al VPS 3** (Dario lo hace desde su laptop):

```bash
ssh -F keys/ssh_config livskin-erp
```

**Una vez dentro del VPS 3**:

```bash
cd /srv/livskin-revops/infra/docker/erp-backfill

# Modo 1: dry-run (no escribe nada, muestra qué haría)
docker compose run --rm erp-backfill dry-run \
    --source /repo/docs/Datos_Livskin_2026-04-25.xlsx

# Modo 2: apply (ejecuta de verdad)
docker compose run --rm erp-backfill apply \
    --source /repo/docs/Datos_Livskin_2026-04-25.xlsx \
    --mode-write insert     # default: insert; en cutover: upsert

# Modo 3: verify (compara Excel y Postgres post-apply)
docker compose run --rm erp-backfill verify \
    --source /repo/docs/Datos_Livskin_2026-04-25.xlsx
```

**Wrapper script en `infra/scripts/`** (alias rápido):

```bash
# Desde la raíz del repo en VPS 3:
./infra/scripts/backfill-dry-run.sh docs/Datos_Livskin_2026-04-25.xlsx
./infra/scripts/backfill-apply.sh docs/Datos_Livskin_2026-04-25.xlsx
./infra/scripts/backfill-verify.sh docs/Datos_Livskin_2026-04-25.xlsx
```

### 6.4 Defaults aplicados a los 135 clientes históricos

Per memoria `project_erp_migration` y ADR-0014:

| Columna | Valor para históricos |
|---|---|
| `fuente` | `'organico'` |
| `canal_adquisicion` | `'legacy'` |
| `consent_marketing` | `false` |
| `consent_date` | NULL |
| `utm_*_at_capture, fbclid_at_capture, gclid_at_capture` | NULL |
| `cod_lead_origen` | NULL (no vinieron de funnel digital) |
| `vtiger_lead_id_origen` | NULL |
| `activo` | `true` |
| `tratamiento_interes` | NULL (se inferirá del histórico de ventas si se quiere) |
| `phone_e164` | normalizado de `TELEFONO` con función ADR-0013 v2 |
| `email_lower` | NULL (Excel histórico casi no tiene emails) |

### 6.5 Flujo del script (pseudocódigo)

```
def backfill(source_path, mode, write_mode):
    log_init()
    
    # 1. Leer Excel
    workbook = read_excel(source_path)
    log("Excel leído: {} hojas", len(workbook.sheets))
    
    # 2. Hoja Listas → catalogos (más NUEVOS hardcoded)
    catalogos_excel = transform_listas(workbook['Listas'])
    catalogos_nuevos = hardcoded_catalogos()  # fuente, canal_adquisicion, metodo_pago
    if mode == 'apply':
        write_catalogos(catalogos_excel + catalogos_nuevos, write_mode)
    
    # 3. Hoja Clientes → clientes (con defaults legacy)
    clientes = transform_clientes(workbook['Clientes'])
    if mode == 'apply':
        for cliente in clientes:
            try:
                write_cliente(cliente, write_mode)
            except Exception as e:
                log_error(e, row=cliente)  # decisión 7: continuar
                continue
    
    # 4. Hoja Ventas → ventas (preserva flat)
    ventas = transform_ventas(workbook['Ventas'])
    if mode == 'apply':
        for venta in ventas:
            try:
                write_venta(venta, write_mode)
            except Exception as e:
                log_error(e, row=venta)
                continue
    
    # 5. Hoja Pagos → pagos
    pagos = transform_pagos(workbook['Pagos'])
    if mode == 'apply':
        for pago in pagos:
            try:
                write_pago(pago, write_mode)
            except Exception as e:
                log_error(e, row=pago)
                continue
    
    # 6. Reporte final
    log_summary({
        'catalogos': len(catalogos_excel),
        'clientes_ok': clientes_ok,
        'clientes_skipped': clientes_skipped,
        'ventas_ok': ventas_ok,
        'ventas_errors': ventas_errors,
        ...
    })
    
    if mode == 'verify':
        run_verifiers(workbook, postgres_state)
```

### 6.6 Verify mode — los 5 chequeos

| # | Chequeo | Cómo se valida |
|---|---|---|
| 1 | Conteos coinciden | `len(excel.Ventas) == COUNT(*) FROM ventas` (idem Pagos, Clientes, Listas) |
| 2 | Sumas de revenue coinciden | `SUM(excel.Ventas.TOTAL) == SUM(postgres.ventas.total)` |
| 3 | Catálogos completos | Las 21 categorías de tratamiento + 12 productos + áreas + valores hardcoded están todos en `catalogos` |
| 4 | Sin huérfanos FK | `SELECT * FROM ventas WHERE cod_cliente NOT IN (SELECT cod_cliente FROM clientes)` debe devolver 0 |
| 5 | Sample deep-equal | 5 clientes random seleccionados, comparar todos sus campos Excel vs Postgres |

**Output**:
```
✅ Conteos: 88 ventas, 84 pagos, 135 clientes, 55 catalogos — TODOS COINCIDEN
✅ Sumas revenue: S/.32,540 (Excel) == S/.32,540 (Postgres)
✅ Catálogos completos: 21 trat + 12 prod + 1 cert + 9 áreas + 12 fuentes + 5 canales + 5 métodos
✅ Sin huérfanos FK
✅ Sample (5 random): todos coinciden
=== BACKFILL VERIFICADO ===
```

### 6.7 Manejo de Listas (catálogos del Excel + hardcoded nuevos)

El Excel tiene en su hoja Listas:
- `tipo`: 3 valores (Tratamiento, Producto, Certificado)
- `cat_Tratamiento`: 21 valores
- `cat_Producto`: 12 valores
- `cat_Certificado`: 1 valor
- `area`: 9 valores

El script agrega hardcoded (per ADR-0014):
- `fuente`: 12 valores (meta_ad, instagram_organic, ..., organico)
- `canal_adquisicion`: 6 valores (paid, organic, referral, walk_in, direct, legacy)
- `metodo_pago`: 5 valores (efectivo, yape, plin, giro, tc)
- `tipo_pago`: 4 valores (normal, credito_generado, credito_aplicado, abono_deuda)
- `estado_lead`: 5 valores (nuevo, contactado, agendado, asistio, cliente, perdido — ADR-0012)
- `intent_level`: 4 valores (investigando, evaluando, listo_comprar, cold)
- `nurture_state`: 4 valores (inactivo, activo, pausado, handed_off)

Total: ~46 valores hardcoded + ~46 del Excel = ~92 entradas en `catalogos` post-backfill.

### 6.8 Encoding y caracteres especiales

El Excel tiene encoding raro en algunos catálogos (`Acido Hialur�nico` debe ser `Ácido Hialurónico`). Per Decisión 5 (importar tal cual):

- Script lee bytes del Excel sin re-encodear
- Si hay caracteres rotos (`�`), se importan tal cual a Postgres
- En modo verify, se reportan como "data quality concerns" pero no bloquean
- Limpieza posible en fase posterior con SQL UPDATE manuales (decisión Dario)

### 6.9 Conexión a Postgres

Variables de entorno (vienen de `infra/docker/postgres-data/.env`):
- `BRAIN_USER_PASSWORD` (no aplica a este servicio, es del brain)
- `ERP_USER_PASSWORD` (futuro — definir cuando se cree el rol erp_user)
- `POSTGRES_SUPERUSER_PASSWORD` (existe — usable para backfill inicial)

**Decisión MVP**: backfill usa `postgres_superuser` (es operación admin, low frequency, single user). En post-MVP refinable a `erp_user` con permisos específicos.

### 6.10 Tests automáticos

Tests obligatorios (per ADR-0023, coverage ≥75%):

| Test | Cubre |
|---|---|
| `test_excel_reader.py` | Lectura del Excel, manejo de hojas vacías |
| `test_transformer_clientes.py` | Mapeo Excel.Clientes → models.Cliente con defaults legacy |
| `test_transformer_ventas.py` | Mapeo flat 1-fila-1-item preservado |
| `test_transformer_pagos.py` | 4 tipos preservados (normal, credito_generado, credito_aplicado, abono_deuda) |
| `test_idempotence.py` | Run apply 2x → estado idéntico, no duplicados |
| `test_error_continue.py` | Inyectar fila errónea → log + continúa |
| `test_verify_mode.py` | Verify detecta discrepancias inyectadas |
| `test_normalization.py` | Phone E.164, email lowercase, nombre preservando acentos |

---

## 7. Consecuencias

### Desbloqueado
- ADR-0024 (cutover) puede ejecutar el backfill como parte de los 7 pasos sin definir mecánica adicional
- Implementación de Fase 2 puede arrancar populando Postgres con data real desde día 1
- ADR-0023 (refactor ERP) puede testear contra data real — bug discovery más realista
- Memoria `project_real_data_source` tiene mecanismo concreto materializado
- Futuro Agente Infra (memoria `project_infra_security_agent`) puede invocar este script con autorización

### Bloqueado / descartado
- Opción D (Sheets API directo) descartada para MVP — overhead de Google Cloud setup
- Opción B (Alembic data migration) descartada — viola separation of concerns (schema vs data)
- Opción C (SQL inserts manuales) descartada — no idempotente, frágil

### Implementación derivada
- [ ] Crear `infra/docker/erp-backfill/` con Dockerfile + compose + entrypoint
- [ ] Implementar `backfill.py` + `readers/` + `transformers/` + `verifiers/`
- [ ] Crear wrappers `infra/scripts/backfill-{dry-run,apply,verify}.sh`
- [ ] Tests con coverage ≥75% (ADR-0023)
- [ ] Documentar en `infra/docker/erp-backfill/README.md` el procedimiento end-to-end
- [ ] Test end-to-end: con `Datos_Livskin_2026-04-25.xlsx`, dry-run debe completar sin errores antes de apply
- [ ] Verificar que el Excel en `docs/` se pueda leer desde el container (bind mount `/srv/livskin-revops:/repo:ro`)

### Cuándo reabrir
- Si manual export del Sheets se vuelve doloroso por frecuencia (>1/semana) → migrar a Opción D (Google API)
- Si volumen de datos crece >100MB → reconsiderar streaming en lugar de carga completa
- Si emergen patrones de errores frecuentes en transformers → reabrir Decisión 5 (limpieza al importar)
- Si surge el Agente Infra (memoria `project_infra_security_agent`) → integrar este script como tool autorizable
- Revisión obligatoria post primera ejecución productiva (en cutover Fase 6) — si hubo issues, refinar ADR

---

## 8. Changelog

- 2026-04-25 — v1.0 — Creada y aprobada (MVP Fase 2). Cierra la 3ra de las 5 ADRs huérfanas (0023-0027). Incorpora las 11 decisiones técnicas validadas en sesión + 3 decisiones nuevas adicionales (Dario aprobó "usemos tus recomendaciones, lo más lógico y útil").
