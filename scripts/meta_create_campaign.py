"""
Crea campaña FB Ads completa en DRAFT (PAUSED).

Objetivo: OUTCOME_ENGAGEMENT con destination_type=WHATSAPP (Click-to-WhatsApp)
Geo: Wanchaq custom_location radius 4km (Cusco)
Budget: S/350 total / 5 días distribuido 35/35/15/15 entre 4 ad sets
Banners: image_hashes ya uploaded
Pre-fill WA: customizado por producto para que Yossie detecte el referral

Doctrina #11: deterministic, sin IA en pipeline.
Status final: PAUSED — Dario revisa y publica desde UI.
"""
import json
import sys
import io
import urllib.request
import urllib.parse
import urllib.error
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

ENV_FILE = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/keys/.env.integrations"
BANNERS_FILE = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/meta-banners-uploaded.json"
AUDIENCES_FILE = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/meta-audiences-created.json"
OUT_RESULT = "c:/Users/daizu/Claude Code/Union VPS - Maestro - Livskin/docs/brand/raw/meta-campaign-created.json"

AD_ACCOUNT = "act_2885433191763149"
PAGE_ID = "525464061130920"  # Livskin Cusco
IG_ACCOUNT_ID = "17841439311659486"
WABA_ID = "1320785723325168"
WA_PHONE_ID = "1071476852722953"
WA_NUMBER_E164 = "51947741117"
PIXEL_ID = "4410809639201712"

# Budget total S/350 / 5 días = S/70/día — Meta usa centavos
# Distribución: 35% Botox / 35% AH / 15% PRP / 15% Limpieza
DAILY_TOTAL_CENTS = 7000  # S/70.00
DISTRIBUTION = {
    "botox": 0.35,    # S/24.50/día -> 2450 centavos
    "acido": 0.35,    # S/24.50/día -> 2450 centavos
    "prp": 0.15,      # S/10.50/día -> 1050 centavos
    "limpieza": 0.15, # S/10.50/día -> 1050 centavos
}

# Geo: Wanchaq + 4km
GEO_TARGETING = {
    "custom_locations": [{
        "name": "Wanchaq 4km",
        "latitude": -13.5267,
        "longitude": -71.9614,
        "radius": 4,
        "distance_unit": "kilometer"
    }],
    "location_types": ["home", "recent"]
}

# Audiences IDs (de meta-audiences-created.json)
WC_CLIENTES = "120243301610920678"
LAL_1PCT = "120243301614620678"
LAL_1_3 = "120243301610930678"
LAL_1_5 = "120243301611330678"

# Audiences pre-existentes usables (≥1000):
EXISTING_AUDIENCES = {
    "TODO_COMPLETO_FB": "120237645093050678",
    "VIERON_VIDEO_BOTOX": "120235156631900678",
    "INTERACCION_NAVIDAD_IG": "120234906870630678",
    "NAVIDAD_ACCION_BOTON": "120234906824550678",
    "INTERACCION_365_DIAS": "23851745743360677",
}

# Configuración por producto
PRODUCTS = {
    "botox": {
        "banner_filename": "01-botox.jpeg",
        "ad_name": "BOFU-WA-COLDWA-BOTOX-MAY26",
        "ad_set_name": "AS-Botox-Cusco-Wanchaq4km",
        "headline": "Botox profesional en Cusco",
        "primary_text": "Botox aplicado por Médico Cirujano (CMP 091029) — filosofía de resultados naturales sin cambiar tu rostro.\n\nS/250 por zona individual o S/700 tratamiento full face. Consulta gratuita con la Dra. Claudia Delgado.",
        "description": "Livskin Cusco · Maestría UCSUR en curso · Médico colegiada",
        "wa_prefill": "Hola, vi tu anuncio de Botox y quería más información [ad:botox-may26]",
        "include_audiences": [LAL_1_3, EXISTING_AUDIENCES["VIERON_VIDEO_BOTOX"]],
        "exclude_audiences": [WC_CLIENTES],
    },
    "acido": {
        "banner_filename": "02-acido.jpeg",
        "ad_name": "BOFU-WA-COLDWA-ACIDO-MAY26",
        "ad_set_name": "AS-Acido-Cusco-Wanchaq4km",
        "headline": "Ácido Hialurónico — Resultados naturales",
        "primary_text": "Realza tu belleza con Ácido Hialurónico — rinomodelación, ojeras, pómulos, labios o mentón.\n\nResultados inmediatos que duran 18-24 meses. Médico Cirujano (CMP 091029). Consulta gratuita.",
        "description": "Livskin Cusco · Marcas certificadas Yvoire",
        "wa_prefill": "Hola, vi tu anuncio de Ácido Hialurónico y quería más información [ad:acido-may26]",
        "include_audiences": [LAL_1_3, EXISTING_AUDIENCES["TODO_COMPLETO_FB"]],
        "exclude_audiences": [WC_CLIENTES],
    },
    "prp": {
        "banner_filename": "03-prp.jpeg",
        "ad_name": "BOFU-WA-COLDWA-PRP-MAY26",
        "ad_set_name": "AS-PRP-Cusco-Wanchaq4km",
        "headline": "PRP a S/220 — Rejuvenece naturalmente",
        "primary_text": "Plasma Rico en Plaquetas — usa tu propia sangre para regenerar la piel. Mejora textura, firmeza, luminosidad.\n\nS/220 por sesión, 3 sesiones (una cada mes). Médico Cirujano (CMP 091029). Consulta gratuita.",
        "description": "Livskin Cusco · 100% Natural · Resultados visibles",
        "wa_prefill": "Hola, vi tu anuncio de PRP a S/220 y quería más información [ad:prp-may26]",
        "include_audiences": [LAL_1_5],
        "exclude_audiences": [WC_CLIENTES],
    },
    "limpieza": {
        "banner_filename": "04-limpieza.jpeg",
        "ad_name": "BOFU-WA-COLDWA-LIMPIEZA-MAY26",
        "ad_set_name": "AS-Limpieza-Cusco-Wanchaq4km",
        "headline": "Limpieza Facial Profunda desde S/70",
        "primary_text": "Limpieza Facial Profunda — piel limpia, fresca y saludable desde la primera sesión.\n\nElimina impurezas, exceso de grasa y células muertas. Desde S/70 (básica) hasta S/120 (premium). Cada 3-4 semanas.",
        "description": "Livskin Cusco · Apto para todo tipo de piel",
        "wa_prefill": "Hola, vi tu anuncio de Limpieza Facial y quería más información [ad:limpieza-may26]",
        "include_audiences": [LAL_1_5],
        "exclude_audiences": [WC_CLIENTES],
    },
}


def load_env():
    env = {}
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#') or '=' not in ln:
                continue
            k, v = ln.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_banner_hashes():
    with open(BANNERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {b["product"]: b["image_hash"] for b in data if "image_hash" in b}


def graph_post(url, params, body_form=None):
    """POST with form-encoded params. If body_form provided, params goes to query string."""
    if body_form is None:
        data_bytes = urllib.parse.urlencode(params, doseq=True).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, method='POST')
    else:
        params_str = urllib.parse.urlencode(params)
        full = f"{url}?{params_str}"
        data_bytes = urllib.parse.urlencode(body_form, doseq=True).encode('utf-8')
        req = urllib.request.Request(full, data=data_bytes, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')
        print(f"\n[ERROR {e.code}] body: {body[:500]}\n")
        return {"_error_code": e.code, "_error_body": body}


def create_campaign(env, name):
    """Step 1: create campaign in PAUSED status."""
    url = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT}/campaigns"
    params = {
        "access_token": env["META_SYSTEM_USER_TOKEN"],
        "name": name,
        "objective": "OUTCOME_ENGAGEMENT",
        "status": "PAUSED",
        "buying_type": "AUCTION",
        "special_ad_categories": json.dumps([]),
        "is_adset_budget_sharing_enabled": "false",  # Cada ad set tiene su propio budget
    }
    return graph_post(url, params)


def create_ad_set(env, campaign_id, product_key, product_cfg, daily_budget_cents):
    """Create ad set with Click-to-WhatsApp destination."""
    url = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT}/adsets"
    targeting = {
        "geo_locations": GEO_TARGETING,
        "genders": [1, 2],  # All genders (1=male, 2=female)
        "age_min": 22,
        "age_max": 60,
        "custom_audiences": [{"id": aid} for aid in product_cfg["include_audiences"]],
        "excluded_custom_audiences": [{"id": aid} for aid in product_cfg["exclude_audiences"]],
        "targeting_automation": {"advantage_audience": 0},  # 0 = Off (control manual), 1 = On (auto-expand)
    }
    # Promoted object: WhatsApp number for Click-to-WA
    promoted_object = {
        "page_id": PAGE_ID,
        "whatsapp_phone_number": WA_NUMBER_E164,
    }
    params = {
        "access_token": env["META_SYSTEM_USER_TOKEN"],
        "campaign_id": campaign_id,
        "name": product_cfg["ad_set_name"],
        "status": "PAUSED",
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "CONVERSATIONS",
        "destination_type": "WHATSAPP",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "daily_budget": daily_budget_cents,
        "targeting": json.dumps(targeting),
        "promoted_object": json.dumps(promoted_object),
        "start_time": int(time.time()) + 3600,  # +1h from now
        "end_time": int(time.time()) + 5 * 86400 + 3600,  # +5 days
    }
    return graph_post(url, params)


def create_ad_creative(env, product_key, product_cfg, image_hash):
    """Create Click-to-WhatsApp ad creative."""
    url = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT}/adcreatives"

    # Object story spec — based on Día Madre creative recipe
    object_story_spec = {
        "page_id": PAGE_ID,
        "instagram_user_id": IG_ACCOUNT_ID,
        "link_data": {
            "link": "https://api.whatsapp.com/send",
            "message": product_cfg["primary_text"],
            "name": product_cfg["headline"],
            "caption": "livskin.site",
            "description": product_cfg["description"],
            "image_hash": image_hash,
            "call_to_action": {
                "type": "WHATSAPP_MESSAGE",
                "value": {"app_destination": "WHATSAPP"}
            }
        }
    }

    params = {
        "access_token": env["META_SYSTEM_USER_TOKEN"],
        "name": f"Creative-{product_cfg['ad_name']}",
        "object_story_spec": json.dumps(object_story_spec),
    }
    return graph_post(url, params)


def create_ad(env, ad_set_id, product_cfg, creative_id):
    """Create ad linking ad set + creative. Meta auto-tracks WA conversations from Click-to-WA ads."""
    url = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT}/ads"
    params = {
        "access_token": env["META_SYSTEM_USER_TOKEN"],
        "name": product_cfg["ad_name"],
        "adset_id": ad_set_id,
        "creative": json.dumps({"creative_id": creative_id}),
        "status": "PAUSED",
    }
    return graph_post(url, params)


def main():
    env = load_env()
    banner_hashes = load_banner_hashes()
    print(f"[INIT] Loaded {len(banner_hashes)} banner hashes\n")

    # Reuse existing empty campaign if available, otherwise create new
    EXISTING_CAMPAIGN_ID = "120243301839000678"
    campaign_name = "Livskin — Mayo 2026 — Click-to-WA Wanchaq 4km (BOFU)"

    # Check if existing campaign is valid
    check_url = f"https://graph.facebook.com/v21.0/{EXISTING_CAMPAIGN_ID}?fields=id,name,status&access_token={env['META_SYSTEM_USER_TOKEN']}"
    try:
        with urllib.request.urlopen(check_url, timeout=10) as r:
            existing = json.loads(r.read().decode())
            if 'id' in existing:
                print(f"[1/4] Reusing existing Campaign: {existing.get('name', '')} (ID {EXISTING_CAMPAIGN_ID})")
                campaign_id = EXISTING_CAMPAIGN_ID
                campaign = existing
            else:
                raise Exception("not found")
    except Exception:
        print(f"[1/4] Creating new Campaign: {campaign_name}")
        campaign = create_campaign(env, campaign_name)
        if "_error_code" in campaign:
            print("CAMPAIGN FAILED, aborting.")
            return
        campaign_id = campaign["id"]
    print(f"     campaign_id={campaign_id}\n")

    results = {"campaign": campaign, "ad_sets": [], "creatives": [], "ads": []}

    print("[2/4] Creating 4 ad sets + creatives + ads...")
    for product_key, cfg in PRODUCTS.items():
        daily_cents = int(DAILY_TOTAL_CENTS * DISTRIBUTION[product_key])
        print(f"\n  [{product_key.upper()}] daily_budget=S/{daily_cents/100:.2f}")

        # Ad Set
        print(f"     creating ad set...")
        adset = create_ad_set(env, campaign_id, product_key, cfg, daily_cents)
        if "_error_code" in adset:
            print(f"     AD SET FAILED for {product_key}")
            results["ad_sets"].append({"product": product_key, "error": adset})
            continue
        adset_id = adset["id"]
        print(f"     ad_set_id={adset_id}")
        results["ad_sets"].append({"product": product_key, "id": adset_id, "raw": adset})

        # Creative
        image_hash = banner_hashes.get(product_key)
        if not image_hash:
            print(f"     ERROR: no image hash for {product_key}")
            continue
        print(f"     creating creative with image_hash={image_hash[:12]}...")
        creative = create_ad_creative(env, product_key, cfg, image_hash)
        if "_error_code" in creative:
            print(f"     CREATIVE FAILED for {product_key}")
            results["creatives"].append({"product": product_key, "error": creative})
            continue
        creative_id = creative["id"]
        print(f"     creative_id={creative_id}")
        results["creatives"].append({"product": product_key, "id": creative_id, "raw": creative})

        # Ad
        print(f"     creating ad...")
        ad = create_ad(env, adset_id, cfg, creative_id)
        if "_error_code" in ad:
            print(f"     AD FAILED for {product_key}")
            results["ads"].append({"product": product_key, "error": ad})
            continue
        ad_id = ad["id"]
        print(f"     ad_id={ad_id} ✅")
        results["ads"].append({"product": product_key, "id": ad_id, "raw": ad})

    print("\n[3/4] Saving result...")
    with open(OUT_RESULT, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "campaign_id": campaign_id,
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print("\n[4/4] DONE — Campaign in DRAFT (PAUSED)")
    print(f"  Campaign ID: {campaign_id}")
    print(f"  Ad sets: {sum(1 for x in results['ad_sets'] if 'id' in x)}/4")
    print(f"  Creatives: {sum(1 for x in results['creatives'] if 'id' in x)}/4")
    print(f"  Ads: {sum(1 for x in results['ads'] if 'id' in x)}/4")
    print(f"\nReview URL: https://business.facebook.com/adsmanager/manage/campaigns?act={AD_ACCOUNT.replace('act_', '')}")


if __name__ == '__main__':
    main()
