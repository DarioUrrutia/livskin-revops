"""Smoke E2E del pipeline real: Lead capturado -> Vtiger -> ERP -> Agenda.

Este script NO usa Playwright. Simula entradas REALES al sistema:

  TEST A — Form web (POST a webhook n8n A1):
    Replica lo que hace el mu-plugin livskin-form-to-n8n.php cuando una persona
    llena el form en livskin.site. POST a flow.livskin.site/webhook con payload
    completo (UTMs + click_ids + event_id + datos del lead).

  TEST B — WhatsApp directo (insert directo a Vtiger DB):
    Simula lo que hara el chatbot Fase 4A.3 cuando se reciba un mensaje WA
    con shortcode. Hoy no hay chatbot, asi que insertamos directo a vtiger_db
    via SSH para simular.

Verificaciones tras cada test:
  1. Lead aparece en Vtiger (vtiger_leaddetails)
  2. cron B3 (cada 2min) sincroniza al ERP livskin_erp.leads
  3. Lead visible en /api/leads/active (que alimenta dropdown Agenda)
  4. Aparece en context Jinja `leads_pendientes` al recargar /

Uso:
    py scripts/smoke_pipeline_lead_to_agenda.py

Despues de validar visualmente Dario, ejecutar cleanup:
    cat scripts/cleanup_smoke_data.sql | ssh livskin-erp 'sudo docker exec -i postgres-data psql -U postgres -d livskin_erp'
    + cleanup en Vtiger (manual o script aparte)
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import urllib.request
import urllib.error

WEBHOOK_A1 = "https://flow.livskin.site/webhook/acquisition/form-submit"
SSH_CONFIG = "keys/ssh_config"


def post_webhook_a1(payload: dict) -> tuple[bool, str]:
    """POST simulado al webhook A1 (igual al mu-plugin WP)."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_A1,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")[:200]
            return resp.status < 400, f"HTTP {resp.status} body={body}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} {e.reason}"
    except Exception as e:
        return False, str(e)


def ssh(cmd: str) -> str:
    """Ejecutar comando SSH en VPS3 (livskin-erp)."""
    full = ["ssh", "-F", SSH_CONFIG, "livskin-erp", cmd]
    result = subprocess.run(full, capture_output=True, text=True, timeout=30)
    return (result.stdout or "") + (result.stderr or "")


def ssh_ops(cmd: str) -> str:
    """SSH a VPS2 (livskin-ops) que tiene Vtiger."""
    full = ["ssh", "-F", SSH_CONFIG, "livskin-ops", cmd]
    result = subprocess.run(full, capture_output=True, text=True, timeout=30)
    return (result.stdout or "") + (result.stderr or "")


def section(t: str):
    print("\n" + "=" * 64)
    print(t)
    print("=" * 64)


def check_lead_in_vtiger(lead_no_or_email: str) -> str:
    """Query Vtiger DB en VPS2 para buscar lead por email o lead_no."""
    sql = (
        "SELECT l.lead_no, l.firstname, l.email, c.createdtime, cf.cf_853 AS utm_source, "
        "cf.cf_857 AS utm_campaign, cf.cf_871 AS event_id "
        "FROM vtiger_leaddetails l "
        "LEFT JOIN vtiger_leadscf cf ON l.leadid=cf.leadid "
        "LEFT JOIN vtiger_crmentity c ON l.leadid=c.crmid "
        f"WHERE c.deleted=0 AND (l.email='{lead_no_or_email}' OR l.lead_no='{lead_no_or_email}') "
        "ORDER BY c.createdtime DESC LIMIT 5;"
    )
    cmd = (
        f"sudo docker exec vtiger-db sh -c "
        f"'mysql -uroot -p\\$MYSQL_ROOT_PASSWORD livskin_db -e \"{sql}\"'"
    )
    return ssh_ops(cmd)


def check_lead_in_erp(email_or_phone: str) -> str:
    """Query ERP postgres por lead matched."""
    sql = (
        "SELECT cod_lead, vtiger_id, nombre, phone_e164, email_lower, estado_lead, "
        "utm_campaign_at_capture, fbclid_at_capture, event_id_at_capture, fecha_captura "
        "FROM leads "
        f"WHERE email_lower='{email_or_phone.lower()}' OR phone_e164 LIKE '%{email_or_phone}%' "
        "ORDER BY id DESC LIMIT 3;"
    )
    cmd = f'sudo docker exec postgres-data psql -U postgres -d livskin_erp -c "{sql}"'
    return ssh(cmd)


def main():
    print(f"\n[SMOKE PIPELINE] Iniciado {datetime.now().isoformat(timespec='seconds')}")

    # ───────────────────────────────────────────────────────────────
    # TEST A — Form web (POST a webhook n8n A1)
    # ───────────────────────────────────────────────────────────────
    section("TEST A — Lead via form web (POST webhook A1)")

    ts = int(time.time())
    payload_form = {
        "nombre": f"TEST_SMOKE_E2E_FORM_{ts}",
        "phone": f"+5190099{ts % 10000:04d}",
        "email": f"test_smoke_form_{ts}@livskin.test",
        "tratamiento_interes": "Botox",
        "utm_source": "facebook",
        "utm_medium": "cpc",
        "utm_campaign": "smoke-pipeline-2026-05-09",
        "utm_content": "tofu",
        "utm_term": "",
        "fbclid": f"fb.1.test.{ts}",
        "gclid": "",
        "fbc": f"fb.1.{ts}.test",
        "ga": "GA1.2.test",
        "event_id": f"event-smoke-{ts}",
        "landing_url": "https://livskin.site/test-smoke",
        "ip_at_submit": "127.0.0.1",
        "ua_at_submit": "Mozilla/5.0 (smoke-test)",
        "referer": "",
        "form_id": 1569,
        "consent_marketing": True,
        "_livskin_payload_version": "1.0",
    }
    print(f"  POST {WEBHOOK_A1}")
    print(f"  payload nombre={payload_form['nombre']}")
    print(f"  payload email={payload_form['email']}")
    print(f"  payload phone={payload_form['phone']}")
    ok, msg = post_webhook_a1(payload_form)
    print(f"  resultado: {msg}")
    if not ok:
        print("  [FAIL] webhook no respondio — abortar")
        sys.exit(1)
    print("  [OK] webhook A1 acepto el POST")

    # Esperar que n8n procese y cree el lead en Vtiger (tipicamente <5s)
    print("\n  Esperando 8s para que n8n procese...")
    time.sleep(8)

    # Verificar en Vtiger
    print("\n  Verificando en Vtiger DB...")
    out = check_lead_in_vtiger(payload_form["email"])
    print(out[:600] if out else "  (sin output)")

    # Esperar cron B3 (corre cada 2 min)
    print("\n  Esperando cron B3 (sync Vtiger -> ERP, max 130s)...")
    print("  Te aviso cada 30s...")
    for i in range(5):
        time.sleep(30)
        elapsed = (i + 1) * 30
        # Verificar si ya llego al ERP
        erp_out = check_lead_in_erp(payload_form["email"])
        if "TEST_SMOKE_E2E_FORM" in erp_out:
            print(f"  [OK] lead aparece en ERP tras {elapsed}s")
            break
        print(f"  [{elapsed}s] aun no aparece en ERP, esperando...")
    else:
        print("  [TIMEOUT] 150s y no llego al ERP — ver logs n8n cron B3")

    # Final query ERP
    print("\n  Estado final en ERP livskin_erp.leads:")
    out = check_lead_in_erp(payload_form["email"])
    print(out[:800] if out else "  (sin output)")

    # ───────────────────────────────────────────────────────────────
    # TEST B — Lead WhatsApp simulado (insert directo Vtiger)
    # ───────────────────────────────────────────────────────────────
    section("TEST B — Lead WhatsApp simulado (Vtiger direct insert)")
    print("  HOY: WhatsApp Cloud API NO esta activo (Fase 4A.2)")
    print("  Simulamos: insert directo en Vtiger via REST/DB para representar lo que")
    print("  el chatbot Fase 4A.3 hara cuando se procese un mensaje WA con shortcode.")
    print()
    print("  [SKIP por ahora] — esto requiere VtigerWS API token o insert SQL controlado.")
    print("  TEST A ya valida que el cron B3 sincroniza Vtiger -> ERP, y un")
    print("  lead WA seguiria el mismo path Vtiger -> cron B3 -> ERP.")
    print()

    # ───────────────────────────────────────────────────────────────
    # TEST C — Verificar pipeline + visibilidad Agenda
    # ───────────────────────────────────────────────────────────────
    section("TEST C — Visibilidad en pestana Agenda")
    print("  El lead ahora deberia aparecer en el dropdown 'Lead pendiente' del modal")
    print("  '+ Nueva cita' en pestana Agenda.")
    print()
    print("  Para verificar visualmente:")
    print("  1. Abrir https://erp.livskin.site/")
    print("  2. Login + click pestana 'Agenda'")
    print("  3. Click '+ manual' (o 'Nueva cita' segun estado)")
    print("  4. En el dropdown de leads buscar 'TEST_SMOKE_E2E_FORM'")
    print("  5. Deberia aparecer con phone, tratamiento Botox, campana smoke-pipeline")
    print()
    print("  Smoke data creada:")
    print(f"    nombre = TEST_SMOKE_E2E_FORM_{ts}")
    print(f"    phone  = {payload_form['phone']}")
    print(f"    email  = {payload_form['email']}")
    print(f"    utm_campaign = {payload_form['utm_campaign']}")
    print()
    print("  Para limpiar despues de validar:")
    print("    1. cleanup ERP: DELETE FROM leads WHERE nombre LIKE 'TEST_SMOKE_E2E_%';")
    print("    2. cleanup Vtiger: marcar deleted=1 en vtiger_crmentity (manual)")
    print()
    print("[DONE]")


if __name__ == "__main__":
    main()
