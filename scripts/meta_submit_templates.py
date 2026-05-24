"""
Submit los 7 templates Meta WhatsApp via Graph API.

Doctrina: drafts en integrations/whatsapp/templates/drafts-v1.md.
"""
import json
import sys
import io
import urllib.request
import urllib.parse
import urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

ENV_FILE = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/keys/.env.integrations"
OUT_RESULT = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/integrations/whatsapp/templates/submitted-v1.json"


def load_env():
    env = {}
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# Template specs ajustadas para Click-to-WhatsApp campaign (Cusco mayo 2026)
TEMPLATES = [
    {
        "name": "new_lead_appointment_request_v1",
        "language": "es_PE",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "Hola {{1}} ☺️ Gracias por escribirnos a Livskin.\n\nSoy Yossie, asistente de la Dra. Claudia Delgado.\nVi que te interesa {{2}}.\n\nLa Dra. ofrece una consulta gratuita personalizada para evaluar tu caso y conversar sobre el tratamiento. ¿Te gustaría agendar?\n\nWanchaq, Cusco — atendemos previa coordinación.",
                "example": {
                    "body_text": [["María", "Botox"]]
                }
            },
            {
                "type": "BUTTONS",
                "buttons": [
                    {"type": "QUICK_REPLY", "text": "Sí, agendar consulta"},
                    {"type": "QUICK_REPLY", "text": "Tengo más preguntas"},
                    {"type": "QUICK_REPLY", "text": "Por ahora no"}
                ]
            }
        ]
    },
    {
        "name": "lead_confirmed_appointment_v1",
        "language": "es_PE",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "Listo, {{1}} ☺️\n\nTu consulta con la Dra. Claudia Delgado queda agendada para *{{2}}* a las *{{3}}*.\n\n📍 Urbanización La Florida O-7, Wanchaq — detrás del templo de los Mormones, media cuadra encima.\n\nSi necesitas reagendar, avísame con 24h de anticipación.\n\nNos vemos ✨",
                "example": {
                    "body_text": [["María", "viernes 30 de mayo", "6:00 pm"]]
                }
            },
            {
                "type": "BUTTONS",
                "buttons": [
                    {"type": "QUICK_REPLY", "text": "Confirmar asistencia"},
                    {"type": "QUICK_REPLY", "text": "Necesito reagendar"}
                ]
            }
        ]
    },
    {
        "name": "lead_proposed_alternatives_v1",
        "language": "es_PE",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "Hola {{1}} ☺️\n\nVi tu propuesta para *{{2}}*, pero ese horario no está disponible. La Dra. te ofrece estas opciones:\n\n1. {{3}}\n2. {{4}}\n\n¿Cuál te acomoda mejor?",
                "example": {
                    "body_text": [["María", "viernes 5pm", "Viernes a las 6pm", "Sábado a las 5pm"]]
                }
            },
            {
                "type": "BUTTONS",
                "buttons": [
                    {"type": "QUICK_REPLY", "text": "Opción 1"},
                    {"type": "QUICK_REPLY", "text": "Opción 2"},
                    {"type": "QUICK_REPLY", "text": "Ninguna me sirve"}
                ]
            }
        ]
    },
    {
        "name": "lead_waiting_4h_followup_v1",
        "language": "es_PE",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "Hola {{1}} ☺️\n\nQuería confirmar si recibiste mi mensaje. ¿Sigue en pie tu interés en {{2}}?\n\nLa Dra. Claudia está disponible para responder tus dudas cuando puedas.\n\nEstamos en contacto ✨",
                "example": {
                    "body_text": [["María", "Botox"]]
                }
            },
            {
                "type": "BUTTONS",
                "buttons": [
                    {"type": "QUICK_REPLY", "text": "Sí, sigo interesada"},
                    {"type": "QUICK_REPLY", "text": "Más tarde respondo"},
                    {"type": "QUICK_REPLY", "text": "Ya no, gracias"}
                ]
            }
        ]
    },
    {
        "name": "appointment_reminder_24h_v1",
        "language": "es_PE",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "Hola {{1}} ☺️ Te recordamos tu cita con la Dra. Claudia Delgado:\n\n📅 *{{2}}* a las *{{3}}*\n📍 Urbanización La Florida O-7, Wanchaq\n\nSi necesitas reagendar, avísanos lo antes posible.\n\nTe esperamos ✨",
                "example": {
                    "body_text": [["María", "viernes 30 de mayo", "6:00 pm"]]
                }
            },
            {
                "type": "BUTTONS",
                "buttons": [
                    {"type": "QUICK_REPLY", "text": "Confirmar asistencia"},
                    {"type": "QUICK_REPLY", "text": "Reagendar"}
                ]
            }
        ]
    },
    {
        "name": "appointment_reminder_3h_v1",
        "language": "es_PE",
        "category": "UTILITY",
        "components": [
            {
                "type": "BODY",
                "text": "{{1}} ☺️ Te esperamos en {{2}}h para tu cita.\n\n📍 Urbanización La Florida O-7, Wanchaq — detrás del templo de los Mormones.\n\nNos vemos ✨",
                "example": {
                    "body_text": [["María", "3"]]
                }
            }
        ]
    },
    {
        "name": "reengagement_inactive_30d_v1",
        "language": "es_PE",
        "category": "MARKETING",
        "components": [
            {
                "type": "BODY",
                "text": "Hola {{1}} ☺️\n\nHace un tiempo que conversamos. ¿Cómo va todo?\n\nSi necesitas información o quieres agendar una consulta gratuita con la Dra. Claudia, aquí estoy.\n\n*Ama tu piel siempre* ✨",
                "example": {
                    "body_text": [["María"]]
                }
            },
            {
                "type": "BUTTONS",
                "buttons": [
                    {"type": "QUICK_REPLY", "text": "Quiero info"},
                    {"type": "QUICK_REPLY", "text": "Agendar consulta"}
                ]
            }
        ]
    }
]


def graph_post(url, params, payload=None):
    if payload is None:
        data_bytes = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, method='POST')
    else:
        params_str = urllib.parse.urlencode(params)
        full_url = f"{url}?{params_str}"
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(full_url, data=data_bytes,
                                     headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return {"_error_code": e.code, "_error_body": body}


def submit_template(env, template_spec):
    waba_id = env["META_WA_PROD_WABA_ID"]
    token = env["META_SYSTEM_USER_TOKEN"]
    url = f"https://graph.facebook.com/v21.0/{waba_id}/message_templates"
    params = {"access_token": token}
    return graph_post(url, params, payload=template_spec)


def main():
    env = load_env()
    print(f"[1/2] Loaded {len(TEMPLATES)} templates to submit")
    print(f"     WABA ID: {env['META_WA_PROD_WABA_ID']}\n")

    results = []
    for i, t in enumerate(TEMPLATES, 1):
        print(f"[{i}/{len(TEMPLATES)}] Submitting '{t['name']}' (category: {t['category']})...")
        result = submit_template(env, t)
        if "_error_code" in result:
            print(f"     ERROR {result['_error_code']}: {result['_error_body'][:200]}")
        else:
            print(f"     OK: id={result.get('id', 'N/A')} status={result.get('status', 'N/A')}")
        results.append({"name": t["name"], "result": result})

    with open(OUT_RESULT, 'w', encoding='utf-8') as f:
        json.dump({
            "submitted_at": __import__('time').strftime('%Y-%m-%dT%H:%M:%S'),
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {OUT_RESULT}")
    n_ok = sum(1 for r in results if "_error_code" not in r["result"])
    print(f"Summary: {n_ok}/{len(TEMPLATES)} templates submitted successfully")


if __name__ == '__main__':
    main()
