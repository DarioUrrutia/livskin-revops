#!/usr/bin/env python3
"""Revert Fix A (B3 cron 30s) + Fix B (A1 direct ERP POST) — over-engineering 2026-05-02 PM.

Razon (feedback Dario): el modelo mental es:
- Vtiger = SoT del lead lifecycle (la doctora trabaja desde Vtiger UI real-time)
- ERP = SoT del cliente operacional + ventas (solo necesita lead al cobrar)
- B3 cron 2 min (catch-up no real-time) es suficiente

Fix A y Fix B agregaron complejidad SIN valor. Reverso ambos.
"""
import json
import sqlite3
from datetime import datetime, timezone

con = sqlite3.connect("/home/node/.n8n/database.sqlite")
cur = con.cursor()

# ─── REVERT Fix A: B3 schedule 30s → 2 min ───
cur.execute("SELECT nodes FROM workflow_entity WHERE id=?", ("b3-vtiger-modified-cron-pull",))
b3_nodes = json.loads(cur.fetchone()[0])

for n in b3_nodes:
    if n.get("type") == "n8n-nodes-base.scheduleTrigger":
        n["parameters"]["rule"] = {"interval": [{"field": "minutes", "minutesInterval": 2}]}
        print("Reverted B3 schedule trigger -> 2 minutes")

new_b3_nodes = json.dumps(b3_nodes, ensure_ascii=False, separators=(",", ":"))

# ─── REVERT Fix B: remove 2 nodes from A1 ───
cur.execute("SELECT nodes, connections FROM workflow_entity WHERE id=?", ("a1-form-submit-vtiger-lead",))
row = cur.fetchone()
a1_nodes = json.loads(row[0])
a1_connections = json.loads(row[1])

# Remove the 2 nodes added in Fix B
a1_nodes_filtered = [n for n in a1_nodes if n.get("id") not in ("node-erp-direct-build", "node-erp-direct-post")]
removed = len(a1_nodes) - len(a1_nodes_filtered)
print(f"Removed {removed} nodes from A1 (Build ERP Direct Sync Payload + POST ERP sync direct)")

# Remove related connections
if "Build ERP Direct Sync Payload" in a1_connections:
    del a1_connections["Build ERP Direct Sync Payload"]
if "POST ERP sync direct" in a1_connections:
    del a1_connections["POST ERP sync direct"]

# Remove the connection FROM "Respond 200 OK" -> "Build ERP Direct Sync Payload"
if "Respond 200 OK" in a1_connections:
    main_arr = a1_connections["Respond 200 OK"].get("main", [])
    if main_arr and main_arr[0]:
        main_arr[0] = [c for c in main_arr[0] if c.get("node") != "Build ERP Direct Sync Payload"]
        if not main_arr[0]:
            # Empty: remove entire entry
            del a1_connections["Respond 200 OK"]
            print("Removed empty 'Respond 200 OK' connection entry")
        else:
            a1_connections["Respond 200 OK"]["main"] = main_arr

new_a1_nodes = json.dumps(a1_nodes_filtered, ensure_ascii=False, separators=(",", ":"))
new_a1_conns = json.dumps(a1_connections, ensure_ascii=False, separators=(",", ":"))

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

cur.execute("UPDATE workflow_entity SET nodes=?, updatedAt=? WHERE id=?",
            (new_b3_nodes, now, "b3-vtiger-modified-cron-pull"))
cur.execute("UPDATE workflow_history SET nodes=?, updatedAt=? "
            "WHERE workflowId=? AND versionId=("
            "SELECT versionId FROM workflow_history WHERE workflowId=? ORDER BY createdAt DESC LIMIT 1)",
            (new_b3_nodes, now, "b3-vtiger-modified-cron-pull", "b3-vtiger-modified-cron-pull"))

cur.execute("UPDATE workflow_entity SET nodes=?, connections=?, updatedAt=? WHERE id=?",
            (new_a1_nodes, new_a1_conns, now, "a1-form-submit-vtiger-lead"))
cur.execute("UPDATE workflow_history SET nodes=?, connections=?, updatedAt=? "
            "WHERE workflowId=? AND versionId=("
            "SELECT versionId FROM workflow_history WHERE workflowId=? ORDER BY createdAt DESC LIMIT 1)",
            (new_a1_nodes, new_a1_conns, now, "a1-form-submit-vtiger-lead", "a1-form-submit-vtiger-lead"))

con.commit()

# Verify
cur.execute("SELECT count(*) FROM workflow_entity WHERE id='a1-form-submit-vtiger-lead' AND nodes LIKE '%A1_DIRECT_ERP_SYNC_v1%'")
print(f"A1 still has Fix B marker: {cur.fetchone()[0]} (expect 0)")
cur.execute("SELECT count(*) FROM workflow_entity WHERE id='b3-vtiger-modified-cron-pull' AND nodes LIKE '%minutesInterval%2%'")
print(f"B3 has minutes interval=2: {cur.fetchone()[0]} (expect 1)")

con.close()
print("Done.")
