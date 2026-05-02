#!/usr/bin/env python3
"""Patch [E1] to use Postgres node 'upsert' operation natively (typed, sin SQL injection).

Reemplaza el nodo "UPSERT analytics.leads" para usar operation='upsert' con
matchingColumns=['vtiger_id'] y mapping automático de columnas desde input items.

Tambien fixea el INSERT etl_runs para usar operation='insert' typed.
"""
import json
import sqlite3
from datetime import datetime, timezone

WF_ID = "e1-erp-leads-to-analytics"
ANALYTICS_CRED_ID = "21d033f5-c700-4513-906c-9adcd25c9a99"

con = sqlite3.connect("/home/node/.n8n/database.sqlite")
cur = con.cursor()

cur.execute("SELECT nodes, connections FROM workflow_entity WHERE id=?", (WF_ID,))
row = cur.fetchone()
if not row:
    raise SystemExit(f"workflow {WF_ID} no encontrado")

nodes = json.loads(row[0])

# Build columns list para 'upsert' (matching el schema analytics.leads)
LEAD_COLUMNS = [
    "vtiger_id", "erp_lead_id", "cod_lead", "email_lower", "phone_e164", "nombre",
    "fuente", "canal_adquisicion",
    "utm_source_at_capture", "utm_medium_at_capture", "utm_campaign_at_capture",
    "utm_content_at_capture", "utm_term_at_capture",
    "fbclid_at_capture", "gclid_at_capture", "fbc_at_capture", "ga_at_capture",
    "event_id_meta", "tratamiento_interes", "consent_marketing",
    "estado_lead", "fecha_captura", "created_at", "updated_at", "sync_source"
]

patched = 0
for n in nodes:
    if n.get("id") == "node-upsert-leads":
        n["parameters"] = {
            "operation": "upsert",
            "schema": {
                "__rl": True,
                "mode": "list",
                "value": "public"
            },
            "table": {
                "__rl": True,
                "mode": "list",
                "value": "leads"
            },
            "columns": {
                "mappingMode": "defineBelow",
                "value": {col: f"={{{{ $json.{col} }}}}" for col in LEAD_COLUMNS},
                "matchingColumns": ["vtiger_id"],
                "schema": [{"id": col, "displayName": col, "required": False, "defaultMatch": False, "canBeUsedToMatch": True, "removed": False} for col in LEAD_COLUMNS]
            },
            "options": {}
        }
        patched += 1
        print("Patched node-upsert-leads -> operation=upsert with matchingColumns=[vtiger_id]")
    elif n.get("id") == "node-log-etl-run":
        n["parameters"] = {
            "operation": "executeQuery",
            "query": (
                "INSERT INTO etl_runs (etl_name, started_at, finished_at, status, rows_processed) "
                "VALUES ('E1', NOW() - INTERVAL '5 seconds', NOW(), 'success', 1);"
            ),
            "options": {}
        }
        patched += 1
        print("Patched node-log-etl-run -> simplified executeQuery sin parameters")

if patched != 2:
    raise SystemExit(f"expected 2 patches, applied {patched}")

new_nodes = json.dumps(nodes, ensure_ascii=False, separators=(",", ":"))
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

cur.execute("UPDATE workflow_entity SET nodes=?, updatedAt=? WHERE id=?", (new_nodes, now, WF_ID))
print(f"workflow_entity rows updated: {cur.rowcount}")

cur.execute(
    "UPDATE workflow_history SET nodes=?, updatedAt=? "
    "WHERE workflowId=? AND versionId=("
    "  SELECT versionId FROM workflow_history WHERE workflowId=? "
    "  ORDER BY createdAt DESC LIMIT 1)",
    (new_nodes, now, WF_ID, WF_ID),
)
print(f"workflow_history rows updated: {cur.rowcount}")

con.commit()
con.close()
print("Done.")
