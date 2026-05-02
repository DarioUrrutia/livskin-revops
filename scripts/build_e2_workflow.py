#!/usr/bin/env python3
"""Build n8n workflow [E2] ERP Ventas -> Analytics Opportunities.

Sync incremental cron 5 min. UPSERT por venta_id.
Hace lookup analytics.leads.id desde vtiger_lead_id_origen para vincular.
"""
import json
import sys

ANALYTICS_CRED_ID = "21d033f5-c700-4513-906c-9adcd25c9a99"
WF_ID = "e2-erp-ventas-to-analytics"

OPP_COLUMNS = [
    "venta_id", "num_secuencial", "cod_cliente", "cliente_nombre",
    "cod_lead_origen", "vtiger_lead_id", "fecha_venta",
    "tipo", "cod_item", "categoria", "zona_cantidad_envase",
    "moneda", "total", "descuento", "pagado", "debe",
    "efectivo", "yape", "plin", "giro",
    "created_at", "updated_at"
]

workflow = {
    "id": WF_ID,
    "name": "[E2] ERP Ventas -> Analytics Opportunities",
    "active": True,
    "isArchived": False,
    "nodes": [
        {
            "id": "node-schedule",
            "name": "Schedule Every 5min",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [240, 400],
            "parameters": {
                "rule": {"interval": [{"field": "minutes", "minutesInterval": 5}]}
            }
        },
        {
            "id": "node-get-cursor",
            "name": "Get Last Sync Cursor",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.6,
            "position": [460, 400],
            "credentials": {
                "postgres": {"id": ANALYTICS_CRED_ID, "name": "Postgres Analytics ETL Writer"}
            },
            "parameters": {
                "operation": "executeQuery",
                "query": "SELECT COALESCE(MAX(finished_at), '1970-01-01T00:00:00Z'::timestamptz) AS cursor FROM etl_runs WHERE etl_name = 'E2' AND status = 'success';",
                "options": {}
            }
        },
        {
            "id": "node-build-window",
            "name": "Build Query Window",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 400],
            "parameters": {
                "language": "javaScript",
                "jsCode": (
                    "const cursorRow = $input.first().json;\n"
                    "let cursor = cursorRow.cursor;\n"
                    "if (cursor instanceof Date) cursor = cursor.toISOString();\n"
                    "if (!cursor) cursor = '1970-01-01T00:00:00Z';\n"
                    "const cursorMs = new Date(cursor).getTime() - 30000;\n"
                    "const since = new Date(cursorMs).toISOString();\n"
                    "return [{ json: { since, run_start: new Date().toISOString() } }];"
                )
            }
        },
        {
            "id": "node-http-get-ventas",
            "name": "GET ERP ventas since cursor",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [900, 400],
            "parameters": {
                "method": "GET",
                "url": "https://erp.livskin.site/api/internal/sync/ventas",
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
                "options": {"timeout": 15000}
            },
            "continueOnFail": True,
            "retryOnFail": True,
            "maxTries": 3,
            "waitBetweenTries": 1000
        },
        {
            "id": "node-map-ventas",
            "name": "Map ERP venta -> Analytics opp",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1120, 400],
            "parameters": {
                "language": "javaScript",
                "jsCode": (
                    "const response = $input.first().json;\n"
                    "if (!response.ok) {\n"
                    "  throw new Error('ERP sync failed: ' + JSON.stringify(response).slice(0,300));\n"
                    "}\n"
                    "const items = response.items || [];\n"
                    "const mapped = items.map(v => ({\n"
                    "  venta_id: v.id,\n"
                    "  num_secuencial: v.num_secuencial,\n"
                    "  cod_cliente: v.cod_cliente,\n"
                    "  cliente_nombre: v.cliente_nombre,\n"
                    "  cod_lead_origen: v.cod_lead_origen,\n"
                    "  vtiger_lead_id: v.vtiger_lead_id_origen,\n"
                    "  fecha_venta: v.fecha,\n"
                    "  tipo: v.tipo,\n"
                    "  cod_item: v.cod_item,\n"
                    "  categoria: v.categoria,\n"
                    "  zona_cantidad_envase: v.zona_cantidad_envase,\n"
                    "  moneda: v.moneda,\n"
                    "  total: v.total,\n"
                    "  descuento: v.descuento,\n"
                    "  pagado: v.pagado,\n"
                    "  debe: v.debe,\n"
                    "  efectivo: v.efectivo,\n"
                    "  yape: v.yape,\n"
                    "  plin: v.plin,\n"
                    "  giro: v.giro,\n"
                    "  created_at: v.created_at,\n"
                    "  updated_at: v.updated_at\n"
                    "}));\n"
                    "if (mapped.length === 0) return [{ json: { _empty: true, count: 0 } }];\n"
                    "return mapped.map(m => ({ json: m }));"
                )
            }
        },
        {
            "id": "node-upsert-opps",
            "name": "UPSERT analytics.opportunities",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.6,
            "position": [1340, 400],
            "credentials": {
                "postgres": {"id": ANALYTICS_CRED_ID, "name": "Postgres Analytics ETL Writer"}
            },
            "parameters": {
                "operation": "upsert",
                "schema": {"__rl": True, "mode": "list", "value": "public"},
                "table": {"__rl": True, "mode": "list", "value": "opportunities"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {col: f"={{{{ $json.{col} }}}}" for col in OPP_COLUMNS},
                    "matchingColumns": ["venta_id"],
                    "schema": [
                        {"id": col, "displayName": col, "required": False,
                         "defaultMatch": False, "canBeUsedToMatch": True, "removed": False}
                        for col in OPP_COLUMNS
                    ]
                },
                "options": {}
            },
            "continueOnFail": True
        },
        {
            "id": "node-log-etl-run",
            "name": "INSERT etl_runs",
            "type": "n8n-nodes-base.postgres",
            "typeVersion": 2.6,
            "position": [1560, 400],
            "credentials": {
                "postgres": {"id": ANALYTICS_CRED_ID, "name": "Postgres Analytics ETL Writer"}
            },
            "parameters": {
                "operation": "executeQuery",
                "query": (
                    "INSERT INTO etl_runs (etl_name, started_at, finished_at, status, rows_processed) "
                    "VALUES ('E2', NOW() - INTERVAL '5 seconds', NOW(), 'success', 1);"
                ),
                "options": {}
            }
        }
    ],
    "connections": {
        "Schedule Every 5min": {"main": [[{"node": "Get Last Sync Cursor", "type": "main", "index": 0}]]},
        "Get Last Sync Cursor": {"main": [[{"node": "Build Query Window", "type": "main", "index": 0}]]},
        "Build Query Window": {"main": [[{"node": "GET ERP ventas since cursor", "type": "main", "index": 0}]]},
        "GET ERP ventas since cursor": {"main": [[{"node": "Map ERP venta -> Analytics opp", "type": "main", "index": 0}]]},
        "Map ERP venta -> Analytics opp": {"main": [[{"node": "UPSERT analytics.opportunities", "type": "main", "index": 0}]]},
        "UPSERT analytics.opportunities": {"main": [[{"node": "INSERT etl_runs", "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1", "timezone": "UTC"},
    "staticData": None,
    "meta": None,
    "pinData": {},
    "versionId": "00000000-0000-0000-0000-000000000002",
    "triggerCount": 0,
    "tags": []
}

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/e2-workflow.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([workflow], f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path} ({len(workflow['nodes'])} nodes)")
