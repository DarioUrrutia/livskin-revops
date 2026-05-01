#!/usr/bin/env python3
"""
Direct SQL UPDATE of n8n workflow_entity.nodes for A1 with the WA-click patch.
Runs ON the VPS. Reads /tmp/a1-modified.json (already patched).
Only touches the `nodes` column (connections + settings unchanged).
"""
import json
import sqlite3
import sys
from datetime import datetime

DB = '/home/node/.n8n/database.sqlite'
SRC = '/tmp/a1-modified.json'
WF_ID = 'a1-form-submit-vtiger-lead'

with open(SRC, encoding='utf-8') as f:
    data = json.load(f)

wf = data[0] if isinstance(data, list) else data
new_nodes = json.dumps(wf['nodes'], ensure_ascii=False, separators=(',', ':'))

print(f'patched nodes JSON size: {len(new_nodes)} bytes')
assert 'WA_CLICK_PATCH_v1' in new_nodes, 'patch marker missing in source'

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute('SELECT length(nodes) FROM workflow_entity WHERE id = ?', (WF_ID,))
before = cur.fetchone()[0]
print(f'BEFORE update: nodes column size = {before} bytes')

now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
cur.execute('UPDATE workflow_entity SET nodes = ?, updatedAt = ? WHERE id = ?', (new_nodes, now, WF_ID))
con.commit()

cur.execute('SELECT length(nodes), updatedAt FROM workflow_entity WHERE id = ?', (WF_ID,))
after_size, after_time = cur.fetchone()
print(f'AFTER  update: nodes column size = {after_size} bytes, updatedAt = {after_time}')

cur.execute('SELECT count(*) FROM workflow_entity WHERE id = ? AND nodes LIKE ?', (WF_ID, '%WA_CLICK_PATCH_v1%'))
hits = cur.fetchone()[0]
print(f'Marker presence in DB: {hits} (expect 1)')
con.close()

if hits != 1:
    sys.exit(2)
print('SQL patch applied successfully.')
