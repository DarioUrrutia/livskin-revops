-- ═══════════════════════════════════════════════════════════════════
-- CLEANUP smoke data Fase 4A.1 — ejecutar a la señal de Dario
-- ═══════════════════════════════════════════════════════════════════
-- Borra TODOS los TEST_SMOKE en orden correcto (respetando FKs).
--
-- Uso:
--   ssh livskin-erp 'sudo docker exec -i postgres-data psql -U postgres -d livskin_erp' < scripts/cleanup_smoke_data.sql
-- ═══════════════════════════════════════════════════════════════════

BEGIN;

-- 1. Pagos TEST (referencian ventas + clientes)
DELETE FROM pagos WHERE cod_pago LIKE 'LIVPAGO_TEST_%' OR cliente_nombre LIKE 'TEST_SMOKE%';

-- 2. Ventas TEST (referencian clientes)
DELETE FROM ventas WHERE cod_item LIKE 'LIVTRAT_TEST_%' OR cliente_nombre LIKE 'TEST_SMOKE%';

-- 3. Gastos TEST
DELETE FROM gastos WHERE descripcion LIKE 'TEST_SMOKE%' OR destinatario LIKE 'TEST_SMOKE%';

-- 4. Appointments TEST (referencian leads + clientes)
DELETE FROM appointments WHERE cod_appointment LIKE 'LIVAPT_TEST_%';

-- 5. Leads TEST
DELETE FROM leads WHERE cod_lead LIKE 'LIVLEAD_TEST_%';

-- 6. Clientes TEST creados por mark_attended (workflow ADR-0033)
--    Estos tienen nombre que comienza con "TEST_SMOKE"
DELETE FROM clientes WHERE nombre LIKE 'TEST_SMOKE%';

-- 7. Audit log entries del periodo (mantener por ahora, son inmutables igual)
-- No se borra audit_log — el trigger audit_log_immutable bloquearía DELETE.
-- Los eventos appointment.* TEST se identifican por entity_id LIKE 'LIVAPT_TEST_%'.
-- Quedan como histórico legítimo de la sesión 2026-05-09.

COMMIT;

-- Verificación post-cleanup
SELECT 'pagos_test' AS tabla, COUNT(*) FROM pagos WHERE cod_pago LIKE 'LIVPAGO_TEST_%' OR cliente_nombre LIKE 'TEST_SMOKE%'
UNION ALL SELECT 'ventas_test', COUNT(*) FROM ventas WHERE cod_item LIKE 'LIVTRAT_TEST_%' OR cliente_nombre LIKE 'TEST_SMOKE%'
UNION ALL SELECT 'gastos_test', COUNT(*) FROM gastos WHERE descripcion LIKE 'TEST_SMOKE%' OR destinatario LIKE 'TEST_SMOKE%'
UNION ALL SELECT 'appointments_test', COUNT(*) FROM appointments WHERE cod_appointment LIKE 'LIVAPT_TEST_%'
UNION ALL SELECT 'leads_test', COUNT(*) FROM leads WHERE cod_lead LIKE 'LIVLEAD_TEST_%'
UNION ALL SELECT 'clientes_test', COUNT(*) FROM clientes WHERE nombre LIKE 'TEST_SMOKE%';
-- Esperado: 0 en todas las filas tras commit
