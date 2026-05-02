-- v3 schema adjustment — opportunities aligned to ERP real schema (2026-05-02 PM)
--
-- Reemplaza la tabla `opportunities` v2 (que asumía columns no existentes en
-- ERP venta) con schema espejo del ERP real:
-- - venta = 1 fila por item vendido (flat per ADR-0011 v1.1 legacy)
-- - JOINS opcionales con leads (solo cuando hay attribution digital)
-- - rollup pagos: pagado_total + saldo del cod_cliente

-- IDEMPOTENT: opportunities está vacía post-cleanup, DROP CASCADE seguro

DROP TABLE IF EXISTS opportunities CASCADE;

CREATE TABLE opportunities (
    id              BIGSERIAL PRIMARY KEY,
    -- Identidad cross-system
    venta_id        BIGINT UNIQUE NOT NULL,                   -- livskin_erp.ventas.id
    num_secuencial  INT,
    cod_cliente     VARCHAR(20) NOT NULL,                     -- livskin_erp.clientes.cod_cliente
    cliente_nombre  VARCHAR(255),

    -- Vinculación marketing journey (NULL si cliente word-of-mouth sin attribution)
    cod_lead_origen VARCHAR(20),                              -- livskin_erp.clientes.cod_lead_origen
    vtiger_lead_id  VARCHAR(20),                              -- livskin_erp.clientes.vtiger_lead_id_origen
    event_id_meta   VARCHAR(100),                             -- de leads.event_id_at_capture (via cod_lead_origen)
    lead_id         BIGINT REFERENCES leads(id) ON DELETE SET NULL,

    -- Datos de la venta (1 fila = 1 item vendido)
    fecha_venta     DATE NOT NULL,
    tipo            VARCHAR(30),                              -- Tratamiento | Producto | Certificado | Promocion
    cod_item        VARCHAR(50),                              -- LIVTRAT0001 etc
    categoria       VARCHAR(50),
    zona_cantidad_envase VARCHAR(100),

    -- Montos
    moneda          VARCHAR(3) DEFAULT 'PEN',
    total           NUMERIC(12,2) NOT NULL,                   -- venta.total (este item)
    descuento       NUMERIC(12,2) DEFAULT 0,
    pagado          NUMERIC(12,2) DEFAULT 0,                  -- venta.pagado (acumulado del item)
    debe            NUMERIC(12,2) DEFAULT 0,
    -- Breakdown métodos pago de esta venta
    efectivo        NUMERIC(12,2),
    yape            NUMERIC(12,2),
    plin            NUMERIC(12,2),
    giro            NUMERIC(12,2),

    -- Audit sync
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_synced_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_opps_fecha_venta ON opportunities (fecha_venta DESC);
CREATE INDEX idx_opps_cod_cliente ON opportunities (cod_cliente);
CREATE INDEX idx_opps_lead ON opportunities (lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_opps_vtiger_lead ON opportunities (vtiger_lead_id) WHERE vtiger_lead_id IS NOT NULL;
CREATE INDEX idx_opps_event_id ON opportunities (event_id_meta) WHERE event_id_meta IS NOT NULL;
CREATE INDEX idx_opps_tipo ON opportunities (tipo);
CREATE INDEX idx_opps_categoria ON opportunities (categoria);

-- Reapply permissions (DROP CASCADE las quitó)
GRANT SELECT ON opportunities TO metabase_reader;
GRANT SELECT, INSERT, UPDATE ON opportunities TO etl_writer;
GRANT USAGE, SELECT ON SEQUENCE opportunities_id_seq TO etl_writer;

-- ────────────────────────────────────────────────────
-- VIEW: opportunities_con_lead — JOIN with leads para attribution analysis
-- ────────────────────────────────────────────────────

CREATE OR REPLACE VIEW opportunities_con_lead AS
SELECT
    o.*,
    -- Tag attribution status
    CASE
        WHEN o.lead_id IS NOT NULL THEN 'digital_attributed'
        WHEN o.cod_lead_origen IS NOT NULL THEN 'digital_orphan'  -- cliente tiene cod_lead pero no encontramos el lead en analytics.leads
        ELSE 'no_attribution'                                      -- word-of-mouth/walk-in/legacy
    END AS attribution_status,
    -- UTMs from leads (NULL si no attribution)
    l.utm_source_at_capture,
    l.utm_medium_at_capture,
    l.utm_campaign_at_capture,
    l.fbclid_at_capture,
    l.gclid_at_capture,
    l.fuente AS lead_fuente,
    l.canal_adquisicion
FROM opportunities o
LEFT JOIN leads l ON l.id = o.lead_id;

GRANT SELECT ON opportunities_con_lead TO metabase_reader;

-- ────────────────────────────────────────────────────
-- VIEW: revenue_mensual — agregado por mes (todas las ventas)
-- ────────────────────────────────────────────────────

CREATE OR REPLACE VIEW revenue_mensual AS
SELECT
    DATE_TRUNC('month', fecha_venta)::date AS mes,
    COUNT(*) AS ventas_count,
    COUNT(DISTINCT cod_cliente) AS clientes_unicos,
    SUM(total) AS revenue_total,
    SUM(pagado) AS revenue_pagado,
    SUM(debe) AS saldo_pendiente,
    COUNT(*) FILTER (WHERE tipo = 'Tratamiento') AS ventas_tratamientos,
    COUNT(*) FILTER (WHERE tipo = 'Producto') AS ventas_productos,
    COUNT(*) FILTER (WHERE cod_lead_origen IS NOT NULL) AS ventas_con_attribution,
    SUM(total) FILTER (WHERE cod_lead_origen IS NOT NULL) AS revenue_attributed_digital,
    SUM(total) FILTER (WHERE cod_lead_origen IS NULL) AS revenue_no_attribution
FROM opportunities
GROUP BY 1
ORDER BY 1 DESC;

GRANT SELECT ON revenue_mensual TO metabase_reader;

\echo 'v3 opportunities + 2 views aplicado.'
\dt
\dv
