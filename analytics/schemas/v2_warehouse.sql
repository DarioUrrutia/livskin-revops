-- analytics warehouse schema v2 (Mini-bloque 3.5 - 2026-05-02)
-- Warehouse cross-system con ETL n8n (per ADR-0032).
--
-- Idempotente: DROP CASCADE + CREATE permite reaplicar limpiamente.
-- Solo aplicable cuando las tablas estan vacias (verificar antes con SELECT count(*)).
--
-- Aplicar:
--   docker exec -i postgres-analytics psql -U analytics_user -d analytics < v2_warehouse.sql
--
-- Rollback:
--   El v1_initial.sql original esta en este folder por si hay que volver atras.

-- ================================================================
-- DROP existing minimal tables (estan vacias post-validacion)
-- ================================================================

DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS crm_stages CASCADE;
DROP TABLE IF EXISTS opportunities CASCADE;
DROP TABLE IF EXISTS leads CASCADE;

-- ================================================================
-- TABLA: leads — espejo enriquecido del lead lifecycle
-- ================================================================
-- Source: ETL [E1] livskin_erp.leads + ETL [E2] Vtiger Leads (enrich)
-- Sync: cron 5 min, idempotent UPSERT por vtiger_id

CREATE TABLE leads (
    id              BIGSERIAL PRIMARY KEY,
    -- Identidad cross-system
    vtiger_id       VARCHAR(20) UNIQUE NOT NULL,             -- formato Vtiger "10x123" — primary correlation key
    erp_lead_id     BIGINT,                                  -- livskin_erp.leads.id (NULL si wa-click solo en Vtiger - Op B)
    cod_lead        VARCHAR(20),                             -- LIVLEAD0001 etc del ERP

    -- Identidad PII (lower/normalized para joins)
    email_lower     VARCHAR(255),
    phone_e164      VARCHAR(20),
    nombre          VARCHAR(255),

    -- Source + canal
    fuente          VARCHAR(50),                             -- form_web, wa_click_direct, organic, etc
    canal_adquisicion VARCHAR(50),                           -- digital_paid, digital_organic, referral, walkin
    leadsource_vtiger VARCHAR(100),                          -- 'Web Site' | 'WA Direct Click' | etc

    -- Attribution UTMs at capture (INMUTABLE per first-touch)
    utm_source_at_capture     VARCHAR(255),
    utm_medium_at_capture     VARCHAR(255),
    utm_campaign_at_capture   VARCHAR(255),
    utm_content_at_capture    VARCHAR(255),
    utm_term_at_capture       VARCHAR(255),

    -- Click IDs
    fbclid_at_capture         VARCHAR(500),
    gclid_at_capture          VARCHAR(500),

    -- Cookies for CAPI match quality
    fbc_at_capture            VARCHAR(500),
    ga_at_capture             VARCHAR(255),

    -- Event ID (HILO CONDUCTOR atribución end-to-end per project_attribution_chain_event_id)
    event_id_meta             VARCHAR(100),                  -- UUID v4

    -- Landing context
    landing_url     TEXT,
    tratamiento_interes VARCHAR(100),

    -- Compliance
    consent_marketing BOOLEAN DEFAULT FALSE,

    -- Lifecycle state
    estado_lead     VARCHAR(50),                             -- nuevo | contactado | agendado | asistio | cliente | perdido
    leadstatus_vtiger VARCHAR(50),                           -- raw Vtiger leadstatus value

    -- Lifecycle timestamps (campaign analytics requiere granularidad)
    fecha_captura            TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_primer_contacto    TIMESTAMP WITH TIME ZONE,
    fecha_agendado           TIMESTAMP WITH TIME ZONE,
    fecha_asistido           TIMESTAMP WITH TIME ZONE,
    fecha_cliente            TIMESTAMP WITH TIME ZONE,       -- cuando convertido a cliente_id en ERP
    fecha_primera_venta      TIMESTAMP WITH TIME ZONE,
    fecha_perdido            TIMESTAMP WITH TIME ZONE,

    -- Metadata sync
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_synced_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    sync_source     VARCHAR(20)                              -- 'erp' | 'vtiger' | 'merged'
);

-- Índices para queries dashboards típicas
CREATE INDEX idx_leads_fecha_captura ON leads (fecha_captura DESC);
CREATE INDEX idx_leads_utm_source_campaign ON leads (utm_source_at_capture, utm_campaign_at_capture);
CREATE INDEX idx_leads_fuente ON leads (fuente);
CREATE INDEX idx_leads_estado ON leads (estado_lead);
CREATE INDEX idx_leads_fbclid ON leads (fbclid_at_capture) WHERE fbclid_at_capture IS NOT NULL;
CREATE INDEX idx_leads_gclid ON leads (gclid_at_capture) WHERE gclid_at_capture IS NOT NULL;
CREATE INDEX idx_leads_event_id ON leads (event_id_meta);
CREATE INDEX idx_leads_tratamiento ON leads (tratamiento_interes);
CREATE INDEX idx_leads_erp_id ON leads (erp_lead_id) WHERE erp_lead_id IS NOT NULL;

-- ================================================================
-- TABLA: opportunities — ventas/conversiones con join a leads
-- ================================================================
-- Source: ETL [E1] livskin_erp.ventas + livskin_erp.pagos (rollup por venta)
-- Sync: cron 5 min, idempotent UPSERT por venta_id

CREATE TABLE opportunities (
    id              BIGSERIAL PRIMARY KEY,
    venta_id        BIGINT UNIQUE NOT NULL,                   -- livskin_erp.ventas.id
    cliente_id      BIGINT NOT NULL,                          -- livskin_erp.clientes.id
    lead_id         BIGINT REFERENCES leads(id) ON DELETE SET NULL, -- joinable para attribution

    -- Vinculación marketing journey
    vtiger_lead_id  VARCHAR(20),                              -- match con leads.vtiger_id
    event_id_meta   VARCHAR(100),                             -- hilo conductor para Purchase event

    -- Datos de la venta
    cod_venta       VARCHAR(20),                              -- LIVVTA0001 etc
    fecha_venta     TIMESTAMP WITH TIME ZONE NOT NULL,
    tratamiento     VARCHAR(100),
    cantidad_sesiones INT,
    monto_neto      NUMERIC(12,2),
    monto_descuento NUMERIC(12,2),
    monto_total     NUMERIC(12,2),
    monto_pagado    NUMERIC(12,2) DEFAULT 0,
    saldo_pendiente NUMERIC(12,2) DEFAULT 0,
    moneda          VARCHAR(3) DEFAULT 'PEN',
    estado_venta    VARCHAR(30),                              -- pendiente | cobrada | cancelada
    estado_pago     VARCHAR(30),                              -- sin_pago | parcial | total
    vendedor        VARCHAR(100),

    -- Audit
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_synced_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_opps_fecha_venta ON opportunities (fecha_venta DESC);
CREATE INDEX idx_opps_cliente ON opportunities (cliente_id);
CREATE INDEX idx_opps_lead ON opportunities (lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_opps_event_id ON opportunities (event_id_meta) WHERE event_id_meta IS NOT NULL;
CREATE INDEX idx_opps_vendedor ON opportunities (vendedor);
CREATE INDEX idx_opps_tratamiento ON opportunities (tratamiento);

-- ================================================================
-- TABLA: crm_stages — historial cambios de etapa del lead
-- ================================================================
-- Source: ETL [E3] livskin_erp.audit_log (action='lead.stage_changed' o similar)
-- Sync: cron 5 min, append-only

CREATE TABLE crm_stages (
    id                BIGSERIAL PRIMARY KEY,
    lead_id           BIGINT REFERENCES leads(id) ON DELETE CASCADE,
    vtiger_lead_id    VARCHAR(20),                            -- denormalized para queries directas
    previous_stage    VARCHAR(50),
    new_stage         VARCHAR(50) NOT NULL,
    changed_at        TIMESTAMP WITH TIME ZONE NOT NULL,
    actor             VARCHAR(100),                           -- usuario que cambio (doctora, agente, system)
    audit_event_id    BIGINT,                                 -- link a livskin_erp.audit_log.id
    notes             TEXT
);

CREATE INDEX idx_crm_stages_lead ON crm_stages (lead_id);
CREATE INDEX idx_crm_stages_changed_at ON crm_stages (changed_at DESC);
CREATE INDEX idx_crm_stages_new_stage ON crm_stages (new_stage);

-- ================================================================
-- TABLA: events — eventos tracking (Pixel + CAPI + GA4)
-- ================================================================
-- Source: ETL [E7] (Fase 3.5.B) o tap directo desde n8n [G3] CAPI emit
-- Sync: real-time (idempotent por event_id_meta + event_name)

CREATE TABLE events (
    id              BIGSERIAL PRIMARY KEY,
    event_id_meta   VARCHAR(100) NOT NULL,                    -- UUID hilo conductor
    event_name      VARCHAR(50) NOT NULL,                     -- PageView | Lead | Schedule | Purchase | etc
    event_time      TIMESTAMP WITH TIME ZONE NOT NULL,
    source          VARCHAR(20) NOT NULL,                     -- 'pixel_client' | 'capi_server' | 'ga4'
    lead_id         BIGINT REFERENCES leads(id) ON DELETE SET NULL,
    vtiger_lead_id  VARCHAR(20),
    -- Match data hash (para validar match quality CAPI)
    has_email       BOOLEAN DEFAULT FALSE,
    has_phone       BOOLEAN DEFAULT FALSE,
    has_fbc         BOOLEAN DEFAULT FALSE,
    has_fbp         BOOLEAN DEFAULT FALSE,
    -- Detalles
    value           NUMERIC(12,2),
    currency        VARCHAR(3),
    metadata_json   JSONB,
    -- Audit
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (event_id_meta, event_name, source)                -- dedup natural
);

CREATE INDEX idx_events_event_id ON events (event_id_meta);
CREATE INDEX idx_events_event_name_time ON events (event_name, event_time DESC);
CREATE INDEX idx_events_lead ON events (lead_id) WHERE lead_id IS NOT NULL;
CREATE INDEX idx_events_source ON events (source);

-- ================================================================
-- TABLA NUEVA: ads_metrics — métricas Meta + Google Ads
-- ================================================================
-- Source: ETL [E5] Meta Ads API + ETL [E6] Google Ads API (Fase 3.5.B - DIFERIDO)
-- Vacía hoy. Schema definido para que ETLs futuros plug-and-play.

CREATE TABLE ads_metrics (
    id              BIGSERIAL PRIMARY KEY,
    platform        VARCHAR(20) NOT NULL,                     -- 'meta' | 'google'
    account_id      VARCHAR(50) NOT NULL,
    campaign_id     VARCHAR(100) NOT NULL,
    campaign_name   VARCHAR(255),
    adset_id        VARCHAR(100),
    adset_name      VARCHAR(255),
    ad_id           VARCHAR(100),
    ad_name         VARCHAR(255),
    creative_id     VARCHAR(100),

    date_day        DATE NOT NULL,                            -- granularidad diaria

    -- Métricas
    impressions     BIGINT DEFAULT 0,
    clicks          BIGINT DEFAULT 0,
    spend           NUMERIC(12,2) DEFAULT 0,
    currency        VARCHAR(3) DEFAULT 'PEN',
    reach           BIGINT,
    frequency       NUMERIC(8,4),
    ctr             NUMERIC(8,6),                             -- clicks/impressions
    cpc             NUMERIC(8,2),                             -- spend/clicks
    cpm             NUMERIC(8,2),
    -- Conversion metrics (cuando viene del platform)
    conversions     INT DEFAULT 0,
    conversion_value NUMERIC(12,2) DEFAULT 0,

    -- UTM passthrough (para join con leads.utm_*_at_capture)
    utm_source      VARCHAR(255),
    utm_medium      VARCHAR(255),
    utm_campaign    VARCHAR(255),

    -- Audit
    last_synced_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (platform, ad_id, date_day)                        -- idempotent UPSERT key
);

CREATE INDEX idx_ads_date_day ON ads_metrics (date_day DESC);
CREATE INDEX idx_ads_platform_campaign ON ads_metrics (platform, campaign_id);
CREATE INDEX idx_ads_utm ON ads_metrics (utm_source, utm_campaign) WHERE utm_source IS NOT NULL;

-- ================================================================
-- TABLA NUEVA: infra_snapshots_daily — rollup diario de sensores
-- ================================================================
-- Source: ETL [E4] livskin_erp.infra_snapshots (rollup nocturno)
-- Sync: cron daily 03:00

CREATE TABLE infra_snapshots_daily (
    id              BIGSERIAL PRIMARY KEY,
    vps_alias       VARCHAR(30) NOT NULL,                     -- livskin-wp | livskin-ops | livskin-erp
    date_day        DATE NOT NULL,
    -- CPU
    avg_cpu_pct     NUMERIC(5,2),
    max_cpu_pct     NUMERIC(5,2),
    p95_cpu_pct     NUMERIC(5,2),
    -- Memory
    avg_mem_pct     NUMERIC(5,2),
    max_mem_pct     NUMERIC(5,2),
    -- Disk
    avg_disk_pct    NUMERIC(5,2),
    max_disk_pct    NUMERIC(5,2),
    -- Container health
    container_restarts_count INT DEFAULT 0,
    containers_unhealthy_max INT DEFAULT 0,
    -- Sample count (para validar completeness)
    samples_count   INT,
    expected_samples INT,                                     -- 24h * 12 (5min) = 288 esperados
    sample_completeness_pct NUMERIC(5,2),                     -- samples_count/expected_samples * 100
    -- Audit
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (vps_alias, date_day)
);

CREATE INDEX idx_infra_daily_date ON infra_snapshots_daily (date_day DESC);
CREATE INDEX idx_infra_daily_vps ON infra_snapshots_daily (vps_alias);

-- ================================================================
-- TABLA NUEVA: agent_costs — costos LLM por agente/día (Fase 5+)
-- ================================================================
-- Source: ETL futuro desde livskin_erp.agent_api_calls (Bloque 0.10)
-- Vacía hoy. Schema ready.

CREATE TABLE agent_costs (
    id              BIGSERIAL PRIMARY KEY,
    agent_name      VARCHAR(50) NOT NULL,                     -- conversation | brand_orchestrator | etc
    date_day        DATE NOT NULL,
    -- Tokens
    input_tokens    BIGINT DEFAULT 0,
    output_tokens   BIGINT DEFAULT 0,
    cache_read_tokens BIGINT DEFAULT 0,
    cache_creation_tokens BIGINT DEFAULT 0,
    -- Costs
    cost_input_usd  NUMERIC(10,4) DEFAULT 0,
    cost_output_usd NUMERIC(10,4) DEFAULT 0,
    cost_cache_usd  NUMERIC(10,4) DEFAULT 0,
    cost_total_usd  NUMERIC(10,4) DEFAULT 0,
    -- Volumen
    calls_count     INT DEFAULT 0,
    success_count   INT DEFAULT 0,
    error_count     INT DEFAULT 0,
    -- Modelo
    model_name      VARCHAR(50),                              -- claude-opus-4-7 | claude-sonnet-4-6 | etc
    -- Audit
    last_synced_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (agent_name, model_name, date_day)
);

CREATE INDEX idx_agent_costs_date ON agent_costs (date_day DESC);
CREATE INDEX idx_agent_costs_agent ON agent_costs (agent_name);

-- ================================================================
-- TABLA NUEVA: etl_runs — meta-observability del warehouse mismo
-- ================================================================
-- Tracking de cada ejecución de ETL para alerting + dashboards meta

CREATE TABLE etl_runs (
    id              BIGSERIAL PRIMARY KEY,
    etl_name        VARCHAR(20) NOT NULL,                     -- E1 | E2 | E3 | E4 | E5 | E6
    started_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at     TIMESTAMP WITH TIME ZONE,
    status          VARCHAR(20) NOT NULL,                     -- running | success | error | partial
    rows_processed  INT DEFAULT 0,
    rows_inserted   INT DEFAULT 0,
    rows_updated    INT DEFAULT 0,
    rows_skipped    INT DEFAULT 0,
    error_message   TEXT,
    n8n_execution_id INT,
    duration_ms     INT,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_etl_runs_name_started ON etl_runs (etl_name, started_at DESC);
CREATE INDEX idx_etl_runs_status ON etl_runs (status, started_at DESC);

-- ================================================================
-- VIEWS auxiliares para Metabase (queries comunes)
-- ================================================================

-- View: leads_con_conversion — denormaliza para funnel queries
CREATE OR REPLACE VIEW leads_con_conversion AS
SELECT
    l.id, l.vtiger_id, l.fuente, l.canal_adquisicion,
    l.utm_source_at_capture, l.utm_medium_at_capture, l.utm_campaign_at_capture,
    l.fbclid_at_capture, l.gclid_at_capture, l.event_id_meta,
    l.tratamiento_interes, l.estado_lead,
    l.fecha_captura, l.fecha_primer_contacto, l.fecha_agendado,
    l.fecha_asistido, l.fecha_cliente, l.fecha_primera_venta,
    -- Flags lifecycle
    (l.fecha_primer_contacto IS NOT NULL) AS contactado,
    (l.fecha_agendado IS NOT NULL)        AS agendado,
    (l.fecha_asistido IS NOT NULL)        AS asistio,
    (l.fecha_cliente IS NOT NULL)         AS convertido,
    -- Tiempo a etapas (en horas)
    EXTRACT(EPOCH FROM (l.fecha_primer_contacto - l.fecha_captura)) / 3600 AS horas_lead_a_contacto,
    EXTRACT(EPOCH FROM (l.fecha_agendado       - l.fecha_captura)) / 3600 AS horas_lead_a_agendado,
    EXTRACT(EPOCH FROM (l.fecha_cliente        - l.fecha_captura)) / 3600 AS horas_lead_a_cliente,
    -- Revenue agregado
    COALESCE(SUM(o.monto_total), 0)  AS revenue_total,
    COALESCE(SUM(o.monto_pagado), 0) AS revenue_pagado,
    COUNT(o.id)                      AS ventas_count
FROM leads l
LEFT JOIN opportunities o ON o.lead_id = l.id
GROUP BY l.id;

-- View: cac_por_canal_dia (placeholder — solo joineable cuando ads_metrics tenga data)
CREATE OR REPLACE VIEW cac_por_canal_dia AS
SELECT
    a.date_day,
    a.platform,
    a.utm_source,
    a.utm_campaign,
    SUM(a.spend) AS spend_total,
    SUM(a.clicks) AS clicks_total,
    SUM(a.impressions) AS impressions_total,
    -- Lookup leads atribuidos en mismo día con mismo utm
    (SELECT COUNT(*) FROM leads l
       WHERE l.utm_source_at_capture = a.utm_source
         AND l.utm_campaign_at_capture = a.utm_campaign
         AND l.fecha_captura::date = a.date_day) AS leads_atribuidos,
    -- Lookup clientes (leads convertidos) en mismo día con mismo utm
    (SELECT COUNT(*) FROM leads l
       WHERE l.utm_source_at_capture = a.utm_source
         AND l.utm_campaign_at_capture = a.utm_campaign
         AND l.fecha_captura::date = a.date_day
         AND l.fecha_cliente IS NOT NULL) AS clientes_atribuidos,
    -- CAC = spend / clientes (NULL si 0 clientes para evitar div/0)
    CASE WHEN (SELECT COUNT(*) FROM leads l
                 WHERE l.utm_source_at_capture = a.utm_source
                   AND l.utm_campaign_at_capture = a.utm_campaign
                   AND l.fecha_captura::date = a.date_day
                   AND l.fecha_cliente IS NOT NULL) > 0
         THEN SUM(a.spend) / (SELECT COUNT(*) FROM leads l
                                WHERE l.utm_source_at_capture = a.utm_source
                                  AND l.utm_campaign_at_capture = a.utm_campaign
                                  AND l.fecha_captura::date = a.date_day
                                  AND l.fecha_cliente IS NOT NULL)
         ELSE NULL END AS cac_por_canal
FROM ads_metrics a
GROUP BY a.date_day, a.platform, a.utm_source, a.utm_campaign;

-- ================================================================
-- ROL: metabase_reader — solo SELECT (para conexión Metabase)
-- ================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'metabase_reader') THEN
        CREATE ROLE metabase_reader WITH LOGIN PASSWORD 'metabase_reader_changeme_in_env';
    END IF;
END $$;

GRANT CONNECT ON DATABASE analytics TO metabase_reader;
GRANT USAGE ON SCHEMA public TO metabase_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO metabase_reader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO metabase_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO metabase_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO metabase_reader;

-- ================================================================
-- ROL: etl_writer — INSERT/UPDATE para n8n ETL workflows
-- ================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'etl_writer') THEN
        CREATE ROLE etl_writer WITH LOGIN PASSWORD 'etl_writer_changeme_in_env';
    END IF;
END $$;

GRANT CONNECT ON DATABASE analytics TO etl_writer;
GRANT USAGE ON SCHEMA public TO etl_writer;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO etl_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO etl_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO etl_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO etl_writer;

-- ================================================================
-- VERIFICACIÓN
-- ================================================================

\echo 'Schema v2 aplicado. Verificación:'
\dt
\echo ''
\echo 'Roles creados:'
SELECT rolname FROM pg_roles WHERE rolname IN ('metabase_reader','etl_writer','analytics_user');
