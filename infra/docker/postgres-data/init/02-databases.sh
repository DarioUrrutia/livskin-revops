#!/bin/bash
# Init step 02 — crear DBs operativas y dar permisos
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOSQL
  CREATE DATABASE livskin_erp OWNER erp_user;
  CREATE DATABASE livskin_brain OWNER brain_user;

  -- Permisos de conexión (read-only users)
  GRANT CONNECT ON DATABASE livskin_erp TO analytics_etl_reader;
  GRANT CONNECT ON DATABASE livskin_brain TO brain_reader;

  -- Quitar acceso default de PUBLIC a las DBs (defensa en profundidad)
  REVOKE ALL ON DATABASE livskin_erp FROM PUBLIC;
  REVOKE ALL ON DATABASE livskin_brain FROM PUBLIC;
EOSQL

# Grants de schema/tables dentro de livskin_erp
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d livskin_erp <<EOSQL
  GRANT USAGE ON SCHEMA public TO analytics_etl_reader;
  -- Default privileges: cuando erp_user cree tablas, auto-grant SELECT a analytics_etl_reader
  ALTER DEFAULT PRIVILEGES FOR ROLE erp_user IN SCHEMA public GRANT SELECT ON TABLES TO analytics_etl_reader;
EOSQL

# Grants de schema/tables dentro de livskin_brain
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d livskin_brain <<EOSQL
  GRANT USAGE ON SCHEMA public TO brain_reader;
  ALTER DEFAULT PRIVILEGES FOR ROLE brain_user IN SCHEMA public GRANT SELECT ON TABLES TO brain_reader;
EOSQL

echo "[init 02] DBs creadas: livskin_erp (owner erp_user), livskin_brain (owner brain_user)"
