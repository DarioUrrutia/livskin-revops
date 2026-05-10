-- ============================================================
-- Vtiger leadstatus cleanup — Replace estricto (Opción A)
-- Fecha: 2026-05-10
-- Backups: ./backup-leadstatus.sql + ./backup-role2picklist.sql
-- Doctrina: feedback_congruencia_nombres_cross_system.md
--
-- Objetivo:
--   - DELETE 11 valores legacy del picklist (Hot, Cold, Warm, etc.)
--   - INSERT 6 valores nuevos en español congruentes con ERP lead.estado_lead
--     (Nuevo, Contactado, Agendado, Asistió, Cliente, Perdido)
--
-- Pre-requisitos verificados:
--   - 0 leads activos (los 67 son smoke tests deleted=1)
--   - 0 foreign keys hacia vtiger_leadstatus
--   - 0 triggers en vtiger_leadstatus
--   - 0 workflows automáticos en módulo Leads
--   - 0 reports/criteria con valores legacy
--   - leadstatus.defaultvalue está vacío (no hay default hardcoded)
--   - max picklist_valueid actual = 122
--   - vtiger_picklistvalues_seq.id = 304
--   - 5 roles existen: H1 (Organization), H2 (CEO), H3 (VP), H4 (Sales Manager), H5 (Sales Person)
-- ============================================================

START TRANSACTION;

-- 1. Reservar 6 picklist_valueids nuevos (305-310) avanzando sequencer global
UPDATE vtiger_picklistvalues_seq SET id = 310;

-- 2. INSERT 6 valores nuevos en vtiger_leadstatus (sortorderid 1-6 = aparecen primero en UI)
INSERT INTO vtiger_leadstatus (leadstatus, presence, picklist_valueid, sortorderid, color) VALUES
  ('Nuevo',      1, 305, 1, NULL),
  ('Contactado', 1, 306, 2, NULL),
  ('Agendado',   1, 307, 3, NULL),
  ('Asistió',    1, 308, 4, NULL),
  ('Cliente',    1, 309, 5, NULL),
  ('Perdido',    1, 310, 6, NULL);

-- 3. Asignar permisos a los 5 roles para los 6 nuevos valores
INSERT INTO vtiger_role2picklist (roleid, picklistvalueid, picklistid, sortid)
SELECT r.roleid, v.picklistvalueid, 14 AS picklistid, v.sortid
FROM (SELECT 'H1' AS roleid UNION SELECT 'H2' UNION SELECT 'H3' UNION SELECT 'H4' UNION SELECT 'H5') r
CROSS JOIN (
  SELECT 305 AS picklistvalueid, 12 AS sortid UNION ALL
  SELECT 306, 13 UNION ALL
  SELECT 307, 14 UNION ALL
  SELECT 308, 15 UNION ALL
  SELECT 309, 16 UNION ALL
  SELECT 310, 17
) v;

-- 4. DELETE 11 valores legacy de vtiger_leadstatus
DELETE FROM vtiger_leadstatus WHERE picklist_valueid IN (112,113,114,115,116,117,118,119,120,121,122);

-- 5. DELETE permisos de los 11 valores legacy en role2picklist
DELETE FROM vtiger_role2picklist WHERE picklistid=14 AND picklistvalueid IN (112,113,114,115,116,117,118,119,120,121,122);

-- 6. Verificar resultado (debe mostrar SOLO los 6 valores nuevos + 5 roles × 6 valores = 30 r2p rows)
SELECT 'POST_VALUES' AS section, leadstatus, presence, picklist_valueid, sortorderid FROM vtiger_leadstatus ORDER BY sortorderid;
SELECT 'POST_R2P_COUNT' AS section, roleid, COUNT(*) AS n FROM vtiger_role2picklist WHERE picklistid=14 GROUP BY roleid;
SELECT 'POST_TOTAL_VALUES' AS section, COUNT(*) AS total FROM vtiger_leadstatus;

-- COMMIT solo si los SELECT verifican: 6 valores, 5 roles con 6 cada uno (30 total)
COMMIT;

-- En caso de rollback (si algo sale mal en verificación):
-- ROLLBACK;
