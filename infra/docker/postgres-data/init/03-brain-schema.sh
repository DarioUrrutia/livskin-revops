#!/bin/bash
# Init step 03 — schema completo del segundo cerebro (6 capas del ADR-0001)
# Enable pgvector + crea 5 tablas principales + 1 tabla de auditoría
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d livskin_brain <<'EOSQL'
  -- Extensiones necesarias
  CREATE EXTENSION IF NOT EXISTS vector;
  CREATE EXTENSION IF NOT EXISTS pgcrypto;

  -- ============================================================
  -- Layer 1 — Conocimiento clínico
  -- ============================================================
  CREATE TABLE clinic_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_key VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    content_embedding vector(384),
    metadata JSONB DEFAULT '{}'::jsonb,
    language VARCHAR(5) DEFAULT 'es',
    embedding_model_version VARCHAR(50) DEFAULT 'multilingual-e5-small-v1',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
  );
  CREATE INDEX idx_ck_entity ON clinic_knowledge(entity_type, entity_key);
  CREATE INDEX idx_ck_active ON clinic_knowledge(active) WHERE active = true;
  CREATE INDEX idx_ck_embedding ON clinic_knowledge
    USING hnsw (content_embedding vector_cosine_ops);

  -- ============================================================
  -- Layer 2 — Conocimiento del proyecto (docs markdown indexados)
  -- ============================================================
  CREATE TABLE project_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_path VARCHAR(500) NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(384),
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding_model_version VARCHAR(50) DEFAULT 'multilingual-e5-small-v1',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_path, chunk_index)
  );
  CREATE INDEX idx_pk_source ON project_knowledge(source_path);
  CREATE INDEX idx_pk_embedding ON project_knowledge
    USING hnsw (chunk_embedding vector_cosine_ops);

  -- ============================================================
  -- Layer 4 — Conversaciones WhatsApp
  -- ============================================================
  CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(100),
    session_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    content_embedding vector(384),
    message_metadata JSONB DEFAULT '{}'::jsonb,
    agent_prompt_version VARCHAR(20),
    escalated BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    embedding_model_version VARCHAR(50) DEFAULT 'multilingual-e5-small-v1'
  );
  CREATE INDEX idx_conv_patient ON conversations(patient_id, created_at DESC);
  CREATE INDEX idx_conv_session ON conversations(session_id, created_at);
  CREATE INDEX idx_conv_embedding ON conversations
    USING hnsw (content_embedding vector_cosine_ops);

  -- ============================================================
  -- Layer 5 — Memoria creativa (briefs + creativos + performance)
  -- ============================================================
  CREATE TABLE creative_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(100),
    creative_type VARCHAR(20),
    treatment_category VARCHAR(50),
    format VARCHAR(20),
    headline TEXT,
    body TEXT,
    cta VARCHAR(100),
    visual_description TEXT,
    visual_url VARCHAR(500),
    visual_embedding vector(512),
    text_embedding vector(384),
    performance JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'draft',
    learnings TEXT,
    brief_source_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
  );
  CREATE INDEX idx_cm_status ON creative_memory(status, treatment_category);
  CREATE INDEX idx_cm_text_embedding ON creative_memory
    USING hnsw (text_embedding vector_cosine_ops);

  -- ============================================================
  -- Layer 6 — Learnings (insights destilados)
  -- ============================================================
  CREATE TABLE learnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50),
    hypothesis TEXT NOT NULL,
    evidence TEXT NOT NULL,
    outcome VARCHAR(20),
    confidence_score NUMERIC(3,2),
    source_data JSONB DEFAULT '{}'::jsonb,
    embedding vector(384),
    author VARCHAR(50) DEFAULT 'growth_agent',
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    superseded_by UUID REFERENCES learnings(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
  );
  CREATE INDEX idx_learn_category ON learnings(category, outcome);
  CREATE INDEX idx_learn_validity ON learnings(valid_from, valid_until);
  CREATE INDEX idx_learn_embedding ON learnings
    USING hnsw (embedding vector_cosine_ops);

  -- ============================================================
  -- Tabla de auditoría — log de re-embeddings
  -- ============================================================
  CREATE TABLE embedding_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    table_name VARCHAR(100) NOT NULL,
    model_from VARCHAR(50),
    model_to VARCHAR(50) NOT NULL,
    rows_processed INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running',
    notes TEXT
  );

  -- Ownership
  ALTER TABLE clinic_knowledge OWNER TO brain_user;
  ALTER TABLE project_knowledge OWNER TO brain_user;
  ALTER TABLE conversations OWNER TO brain_user;
  ALTER TABLE creative_memory OWNER TO brain_user;
  ALTER TABLE learnings OWNER TO brain_user;
  ALTER TABLE embedding_runs OWNER TO brain_user;

  -- Grants explícitos a brain_reader
  GRANT SELECT ON ALL TABLES IN SCHEMA public TO brain_reader;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO brain_reader;
EOSQL

echo "[init 03] livskin_brain: extensiones + 5 capas + embedding_runs aplicadas"
