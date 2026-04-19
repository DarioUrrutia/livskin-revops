#!/bin/bash
# Init step 01 — crear roles app con least privilege
# Se ejecuta SOLO la primera vez que se crea el volumen postgres-data-vol.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOSQL
  -- Owner/app del ERP transaccional
  CREATE ROLE erp_user WITH LOGIN PASSWORD '$ERP_USER_PASSWORD';

  -- Lector read-only usado por n8n (VPS 2) para ETL hacia analytics
  CREATE ROLE analytics_etl_reader WITH LOGIN PASSWORD '$ANALYTICS_ETL_READER_PASSWORD';

  -- Owner/app del segundo cerebro
  CREATE ROLE brain_user WITH LOGIN PASSWORD '$BRAIN_USER_PASSWORD';

  -- Lector read-only del cerebro (Metabase, tooling)
  CREATE ROLE brain_reader WITH LOGIN PASSWORD '$BRAIN_READER_PASSWORD';
EOSQL

echo "[init 01] roles creados: erp_user, analytics_etl_reader, brain_user, brain_reader"
