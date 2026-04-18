-- Analytics Database Schema
-- livskin RevOps System

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    name VARCHAR(255),
    source VARCHAR(100),
    medium VARCHAR(100),
    campaign VARCHAR(255),
    landing_page VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crm_stages (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    crm_stage VARCHAR(100),
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opportunities (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    amount DECIMAL(12,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    event_type VARCHAR(100),
    event_time TIMESTAMP DEFAULT NOW(),
    metadata_json JSONB
);
