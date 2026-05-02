#!/usr/bin/env python3
"""Patch [E1] node-http-get-leads URL to absolute path (no env var template)."""
import json
import sqlite3
from datetime import datetime, timezone

WF_ID = "e1-erp-leads-to-analytics"
NEW_URL = "https://erp.livskin.site/api/internal/sync/leads"

con = sqlite3.connect("/home/node/.n8n/database.sqlite")
cur = con.cursor()

cur.execute("SELECT nodes FROM workflow_entity WHERE id=?", (WF_ID,))
row = cur.fetchone()
if not row:
    raise SystemExit(f"workflow {WF_ID} no encontrado")

nodes = json.loads(row[0])
patched = 0
for n in nodes:
    if n.get("id") == "node-http-get-leads":
        old = n["parameters"]["url"]
        n["parameters"]["url"] = NEW_URL
        print(f"Patched URL: {old} -> {n['parameters']['url']}")
        patched += 1

if patched != 1:
    raise SystemExit(f"expected 1 patch, applied {patched}")

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
