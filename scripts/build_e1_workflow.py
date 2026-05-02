#!/usr/bin/env python3
"""
Build n8n workflow [E1] ERP Leads -> Analytics.

Output: JSON consumible por `n8n import:workflow`.

Versión 1 (minimalista): solo sincroniza `leads` (no clientes/ventas/pagos).
Cuando funcione end-to-end, extender en v2.
"""
import json
import os
import sys
from pathlib import Path

ANALYTICS_CREDENTIAL_ID = "21d033f5-c700-4513-906c-9adcd25c9a99"  # Postgres Analytics ETL Writer

WORKFLOW_ID = "e1-erp-leads-to-analytics"
WEBHOOK_ID = "e1-erp-leads"  # not used (cron trigger), but n8n format expects

workflow = {
    "id": WORKFLOW_ID,
    "name": "[E1] ERP Leads -> Analytics Warehouse",
    "active": True,
    "isArchived": False,
    "nodes": [
        # ─── 1. Schedule Trigger ───
        {
            "id": "node-schedule-trigger",
            "name": "Schedule Every 5min",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [240, 400],
            "parameters": {
                "rule": {
                    "interval": [{"field": "minutes", "minutesInterval": 5}]
                }
            }
        },
        # ─── 2. Get Last Sync Cursor (Postgres SELECT) ───
        {
            "id": "node-get-cursor",
            "name": "Get Last Sync Cursor",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.6,
            "position": [460, 400],
            "credentials": {
                "postgres": {
                    "id": ANALYTICS_CREDENTIAL_ID,
                    "name": "Postgres Analytics ETL Writer"
                }
            },
            "parameters": {
                "operation": "executeQuery",
                "query": "SELECT COALESCE(MAX(finished_at), '1970-01-01T00:00:00Z'::timestamptz) AS cursor FROM etl_runs WHERE etl_name = 'E1' AND status = 'success';",
                "options": {}
            }
        },
        # ─── 3. Code: build query window + run start ───
        {
            "id": "node-build-window",
            "name": "Build Query Window",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 400],
            "parameters": {
                "language": "javaScript",
                "jsCode": (
                    "// [E1] paso 3: construir cursor + run start timestamp\n"
                    "const cursorRow = $input.first().json;\n"
                    "// cursor de la query Postgres viene como Date object o string\n"
                    "let cursor = cursorRow.cursor;\n"
                    "if (cursor instanceof Date) cursor = cursor.toISOString();\n"
                    "if (!cursor) cursor = '1970-01-01T00:00:00Z';\n"
                    "// Overlap de 30s para no perder rows en boundary\n"
                    "const cursorMs = new Date(cursor).getTime() - 30000;\n"
                    "const since = new Date(cursorMs).toISOString();\n"
                    "const runStart = new Date().toISOString();\n"
                    "return [{ json: { since, run_start: runStart } }];"
                )
            }
        },
        # ─── 4. HTTP GET ERP /api/internal/sync/leads ───
        {
            "id": "node-http-get-leads",
            "name": "GET ERP leads since cursor",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [900, 400],
            "parameters": {
                "method": "GET",
                "url": "https://erp.livskin.site/api/internal/sync/leads",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {"name": "since", "value": "={{ $json.since }}"},
                        {"name": "limit", "value": "500"}
                    ]
                },
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "X-Internal-Token", "value": "={{ $env.AUDIT_INTERNAL_TOKEN }}"}
                    ]
                },
                "options": {
                    "timeout": 15000
                }
            },
            "continueOnFail": True,
            "retryOnFail": True,
            "maxTries": 3,
            "waitBetweenTries": 1000
        },
        # ─── 5. Code: parse response + map to analytics schema ───
        {
            "id": "node-map-leads",
            "name": "Map ERP -> Analytics schema",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1120, 400],
            "parameters": {
                "language": "javaScript",
                "jsCode": (
                    "// [E1] paso 5: parse response + map field names\n"
                    "const response = $input.first().json;\n"
                    "if (!response.ok) {\n"
                    "  throw new Error('ERP sync failed: ' + JSON.stringify(response).slice(0,300));\n"
                    "}\n"
                    "const items = response.items || [];\n"
                    "const mapped = items.map(l => ({\n"
                    "  vtiger_id: l.vtiger_id,\n"
                    "  erp_lead_id: l.id,\n"
                    "  cod_lead: l.cod_lead,\n"
                    "  email_lower: l.email_lower,\n"
                    "  phone_e164: l.phone_e164,\n"
                    "  nombre: l.nombre,\n"
                    "  fuente: l.fuente,\n"
                    "  canal_adquisicion: l.canal_adquisicion,\n"
                    "  utm_source_at_capture: l.utm_source_at_capture,\n"
                    "  utm_medium_at_capture: l.utm_medium_at_capture,\n"
                    "  utm_campaign_at_capture: l.utm_campaign_at_capture,\n"
                    "  utm_content_at_capture: l.utm_content_at_capture,\n"
                    "  utm_term_at_capture: l.utm_term_at_capture,\n"
                    "  fbclid_at_capture: l.fbclid_at_capture,\n"
                    "  gclid_at_capture: l.gclid_at_capture,\n"
                    "  fbc_at_capture: l.fbc_at_capture,\n"
                    "  ga_at_capture: l.ga_at_capture,\n"
                    "  event_id_meta: l.event_id_at_capture,\n"
                    "  tratamiento_interes: l.tratamiento_interes,\n"
                    "  consent_marketing: l.consent_marketing,\n"
                    "  estado_lead: l.estado_lead,\n"
                    "  fecha_captura: l.fecha_captura,\n"
                    "  created_at: l.created_at,\n"
                    "  updated_at: l.updated_at,\n"
                    "  sync_source: 'erp'\n"
                    "}));\n"
                    "// Filter out items con vtiger_id NULL (wa-click leads que aún no se sincronizaron)\n"
                    "const valid = mapped.filter(m => m.vtiger_id);\n"
                    "// Pasar siempre at least one item para que el etl_runs nodo siga funcionando\n"
                    "if (valid.length === 0) {\n"
                    "  return [{ json: { _empty: true, count: 0 } }];\n"
                    "}\n"
                    "return valid.map(v => ({ json: v }));"
                )
            }
        },
        # ─── 6. Postgres UPSERT analytics.leads ───
        {
            "id": "node-upsert-leads",
            "name": "UPSERT analytics.leads",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.6,
            "position": [1340, 400],
            "credentials": {
                "postgres": {
                    "id": ANALYTICS_CREDENTIAL_ID,
                    "name": "Postgres Analytics ETL Writer"
                }
            },
            "parameters": {
                "operation": "executeQuery",
                "query": (
                    "INSERT INTO leads (\n"
                    "  vtiger_id, erp_lead_id, cod_lead, email_lower, phone_e164, nombre,\n"
                    "  fuente, canal_adquisicion,\n"
                    "  utm_source_at_capture, utm_medium_at_capture, utm_campaign_at_capture,\n"
                    "  utm_content_at_capture, utm_term_at_capture,\n"
                    "  fbclid_at_capture, gclid_at_capture, fbc_at_capture, ga_at_capture,\n"
                    "  event_id_meta, tratamiento_interes, consent_marketing,\n"
                    "  estado_lead, fecha_captura, created_at, updated_at, last_synced_at, sync_source\n"
                    ") VALUES (\n"
                    "  $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,\n"
                    "  $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, NOW(), $25\n"
                    ") ON CONFLICT (vtiger_id) DO UPDATE SET\n"
                    "  erp_lead_id = EXCLUDED.erp_lead_id,\n"
                    "  cod_lead = EXCLUDED.cod_lead,\n"
                    "  email_lower = EXCLUDED.email_lower,\n"
                    "  phone_e164 = EXCLUDED.phone_e164,\n"
                    "  nombre = EXCLUDED.nombre,\n"
                    "  fuente = EXCLUDED.fuente,\n"
                    "  canal_adquisicion = EXCLUDED.canal_adquisicion,\n"
                    "  estado_lead = EXCLUDED.estado_lead,\n"
                    "  consent_marketing = EXCLUDED.consent_marketing,\n"
                    "  updated_at = EXCLUDED.updated_at,\n"
                    "  last_synced_at = NOW();"
                ),
                "queryReplacement": (
                    "={{ $json.vtiger_id }},{{ $json.erp_lead_id }},{{ $json.cod_lead }},"
                    "{{ $json.email_lower }},{{ $json.phone_e164 }},{{ $json.nombre }},"
                    "{{ $json.fuente }},{{ $json.canal_adquisicion }},"
                    "{{ $json.utm_source_at_capture }},{{ $json.utm_medium_at_capture }},{{ $json.utm_campaign_at_capture }},"
                    "{{ $json.utm_content_at_capture }},{{ $json.utm_term_at_capture }},"
                    "{{ $json.fbclid_at_capture }},{{ $json.gclid_at_capture }},{{ $json.fbc_at_capture }},{{ $json.ga_at_capture }},"
                    "{{ $json.event_id_meta }},{{ $json.tratamiento_interes }},{{ $json.consent_marketing }},"
                    "{{ $json.estado_lead }},{{ $json.fecha_captura }},{{ $json.created_at }},{{ $json.updated_at }},"
                    "{{ $json.sync_source }}"
                ),
                "options": {}
            },
            "continueOnFail": True
        },
        # ─── 7. Postgres INSERT etl_runs (audit) ───
        {
            "id": "node-log-etl-run",
            "name": "INSERT etl_runs",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.6,
            "position": [1560, 400],
            "credentials": {
                "postgres": {
                    "id": ANALYTICS_CREDENTIAL_ID,
                    "name": "Postgres Analytics ETL Writer"
                }
            },
            "parameters": {
                "operation": "executeQuery",
                "query": (
                    "INSERT INTO etl_runs (etl_name, started_at, finished_at, status, rows_processed, n8n_execution_id) "
                    "VALUES ('E1', $1::timestamptz, NOW(), 'success', $2::int, $3::int);"
                ),
                "queryReplacement": (
                    "={{ $('Build Query Window').first().json.run_start }},"
                    "{{ $items('UPSERT analytics.leads').length }},"
                    "{{ $execution.id || 0 }}"
                ),
                "options": {}
            }
        }
    ],
    "connections": {
        "Schedule Every 5min": {
            "main": [[{"node": "Get Last Sync Cursor", "type": "main", "index": 0}]]
        },
        "Get Last Sync Cursor": {
            "main": [[{"node": "Build Query Window", "type": "main", "index": 0}]]
        },
        "Build Query Window": {
            "main": [[{"node": "GET ERP leads since cursor", "type": "main", "index": 0}]]
        },
        "GET ERP leads since cursor": {
            "main": [[{"node": "Map ERP -> Analytics schema", "type": "main", "index": 0}]]
        },
        "Map ERP -> Analytics schema": {
            "main": [[{"node": "UPSERT analytics.leads", "type": "main", "index": 0}]]
        },
        "UPSERT analytics.leads": {
            "main": [[{"node": "INSERT etl_runs", "type": "main", "index": 0}]]
        }
    },
    "settings": {
        "executionOrder": "v1",
        "timezone": "UTC"
    },
    "staticData": None,
    "meta": None,
    "pinData": {},
    "versionId": "00000000-0000-0000-0000-000000000001",
    "triggerCount": 0,
    "tags": []
}

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/e1-workflow.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([workflow], f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path} ({len(workflow['nodes'])} nodes)")
