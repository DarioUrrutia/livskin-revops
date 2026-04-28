"""Construye el GTM Tracking Engine + variables + triggers + tags en workspace.

Crea programaticamente:
1. 9 variables 1st Party Cookie (5 UTMs + 4 click IDs)
2. 2 variables 1st Party Cookie auxiliares (landing_url, first_referrer)
3. 3 variables Data Layer (event_id, wa_phone, form_id)
4. 1 trigger Custom Event 'form_submit_lvk'
5. 1 trigger Custom Event 'whatsapp_click'
6. 1 trigger Scroll Depth 75%
7. 1 tag Custom HTML 'lvk - Tracking Engine' (All Pages)
8. 1 tag GA4 Event 'whatsapp_click'
9. 1 tag GA4 Event 'lead' (form_submit con UTMs)
10. 1 tag Meta Pixel Custom 'Lead' (form_submit)
11. 1 tag Meta Pixel Custom 'Contact' (whatsapp_click)

NO publica todavia — eso es paso separado para revision.
"""
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = "keys/google-oauth-token.json"
WS_PATH = "accounts/6344785058/containers/246604629/workspaces/18"
GA4_MEASUREMENT_ID = "G-9CNPWS3NRX"


# JS del Tracking Engine — UTM persistence + hidden field populator + WA click + form submit listeners
TRACKING_ENGINE_JS = r"""<script>
(function() {
  'use strict';
  var COOKIE_DAYS = 30;
  var COOKIE_PREFIX = 'lvk_';
  var UTM_PARAMS = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term'];
  var CLICK_IDS = ['fbclid','gclid','ttclid','msclkid'];
  var ALL_PARAMS = UTM_PARAMS.concat(CLICK_IDS);

  function setCookie(name, value, days) {
    var d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    var domain = location.hostname.replace(/^www\./, '');
    document.cookie = name + '=' + encodeURIComponent(value) +
      ';expires=' + d.toUTCString() +
      ';path=/;SameSite=Lax;domain=.' + domain;
  }
  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : '';
  }
  function genEventId(prefix) {
    return prefix + '_' + Date.now() + '_' + Math.random().toString(36).slice(2, 11);
  }

  // 1) Capture URL params -> cookies (only on first visit or if param present)
  try {
    var urlParams = new URLSearchParams(window.location.search);
    ALL_PARAMS.forEach(function(p) {
      var v = urlParams.get(p);
      if (v) setCookie(COOKIE_PREFIX + p, v, COOKIE_DAYS);
    });

    // First-touch landing URL + referrer
    if (!getCookie(COOKIE_PREFIX + 'landing_url')) {
      setCookie(COOKIE_PREFIX + 'landing_url', location.href, COOKIE_DAYS);
    }
    if (!getCookie(COOKIE_PREFIX + 'first_referrer')) {
      setCookie(COOKIE_PREFIX + 'first_referrer', document.referrer || '(direct)', COOKIE_DAYS);
    }
  } catch (e) {
    /* fail silent */
  }

  // 2) Hidden field populator for SureForms (and any form with matching name attribs)
  function populateForms() {
    var fieldMap = {
      'utm_source': 'utm_source','utm_medium': 'utm_medium','utm_campaign': 'utm_campaign',
      'utm_content': 'utm_content','utm_term': 'utm_term',
      'fbclid': 'fbclid','gclid': 'gclid','ttclid': 'ttclid','msclkid': 'msclkid',
      'landing_url': 'landing_url','first_referrer': 'first_referrer'
    };
    Object.keys(fieldMap).forEach(function(slug) {
      var v = getCookie(COOKIE_PREFIX + slug);
      if (!v) return;
      // Match SureForms hidden fields (name contains slug) or generic input[name=slug]
      var inputs = document.querySelectorAll('input[name="' + slug + '"], input[name$="-' + slug + '"]');
      inputs.forEach(function(inp) {
        if (inp.type === 'hidden' || inp.type === 'text') inp.value = v;
      });
    });
  }
  // Run multiple times to catch async-rendered forms
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', populateForms);
  } else { populateForms(); }
  setTimeout(populateForms, 800);
  setTimeout(populateForms, 2500);

  // 3) WhatsApp click listener -> dataLayer
  document.addEventListener('click', function(e) {
    var target = e.target && e.target.closest && e.target.closest('a[href*="api.whatsapp.com"], a[href*="wa.me"]');
    if (!target) return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      'event': 'whatsapp_click',
      'event_id': genEventId('wa'),
      'click_url': target.href,
      'utm_source_v': getCookie(COOKIE_PREFIX + 'utm_source'),
      'utm_medium_v': getCookie(COOKIE_PREFIX + 'utm_medium'),
      'utm_campaign_v': getCookie(COOKIE_PREFIX + 'utm_campaign')
    });
  }, true);

  // 4) SureForms submit listener -> dataLayer (event_id for CAPI dedup)
  document.addEventListener('submit', function(e) {
    var form = e.target;
    if (!form || !form.classList) return;
    if (!form.classList.contains('srfm-form')) return;
    var formId = form.dataset.formId || form.getAttribute('form_id') || 'unknown';
    var eventId = genEventId('lead');
    // Inject event_id as hidden field so backend (when wired) sees the same ID
    var hidden = form.querySelector('input[name="event_id"]');
    if (!hidden) {
      hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = 'event_id';
      form.appendChild(hidden);
    }
    hidden.value = eventId;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      'event': 'form_submit_lvk',
      'event_id': eventId,
      'form_id': formId,
      'utm_source_v': getCookie(COOKIE_PREFIX + 'utm_source'),
      'utm_medium_v': getCookie(COOKIE_PREFIX + 'utm_medium'),
      'utm_campaign_v': getCookie(COOKIE_PREFIX + 'utm_campaign')
    });
  }, true);
})();
</script>"""


def load_creds() -> Credentials:
    data = json.loads(Path(TOKEN_FILE).read_text(encoding="utf-8"))
    return Credentials(
        token=data["token"], refresh_token=data["refresh_token"],
        token_uri=data["token_uri"], client_id=data["client_id"],
        client_secret=data["client_secret"], scopes=data["scopes"],
    )


def cookie_var(name: str, cookie_name: str) -> dict:
    """Build payload for 1st Party Cookie variable."""
    return {
        "name": name,
        "type": "k",  # 1st Party Cookie
        "parameter": [
            {"type": "TEMPLATE", "key": "name", "value": cookie_name},
            {"type": "BOOLEAN", "key": "decodeCookie", "value": "true"},
        ],
    }


def dlv_var(name: str, dlv_name: str, default: str = "") -> dict:
    """Build payload for Data Layer Variable."""
    return {
        "name": name,
        "type": "v",  # Data Layer Variable
        "parameter": [
            {"type": "TEMPLATE", "key": "name", "value": dlv_name},
            {"type": "INTEGER", "key": "dataLayerVersion", "value": "2"},
            {"type": "BOOLEAN", "key": "setDefaultValue", "value": "true"},
            {"type": "TEMPLATE", "key": "defaultValue", "value": default},
        ],
    }


def custom_event_trigger(name: str, event_name: str) -> dict:
    return {
        "name": name,
        "type": "customEvent",
        "customEventFilter": [
            {
                "type": "equals",
                "parameter": [
                    {"type": "TEMPLATE", "key": "arg0", "value": "{{_event}}"},
                    {"type": "TEMPLATE", "key": "arg1", "value": event_name},
                ],
            }
        ],
    }


def main() -> None:
    creds = load_creds()
    tm = build("tagmanager", "v2", credentials=creds)
    workspaces = tm.accounts().containers().workspaces()

    created = {"variables": [], "triggers": [], "tags": []}

    print("=== 1) Variables (cookies) ===")
    cookie_specs = [
        ("Cookie - utm_source", "lvk_utm_source"),
        ("Cookie - utm_medium", "lvk_utm_medium"),
        ("Cookie - utm_campaign", "lvk_utm_campaign"),
        ("Cookie - utm_content", "lvk_utm_content"),
        ("Cookie - utm_term", "lvk_utm_term"),
        ("Cookie - fbclid", "lvk_fbclid"),
        ("Cookie - gclid", "lvk_gclid"),
        ("Cookie - ttclid", "lvk_ttclid"),
        ("Cookie - msclkid", "lvk_msclkid"),
        ("Cookie - landing_url", "lvk_landing_url"),
        ("Cookie - first_referrer", "lvk_first_referrer"),
    ]
    for name, ck in cookie_specs:
        body = cookie_var(name, ck)
        v = workspaces.variables().create(parent=WS_PATH, body=body).execute()
        created["variables"].append(v["variableId"])
        print(f"  + {name} (id={v['variableId']})")

    print("\n=== 2) Variables (Data Layer) ===")
    dlv_specs = [
        ("DLV - event_id", "event_id"),
        ("DLV - form_id", "form_id"),
        ("DLV - click_url", "click_url"),
        ("DLV - utm_source_v", "utm_source_v"),
        ("DLV - utm_medium_v", "utm_medium_v"),
        ("DLV - utm_campaign_v", "utm_campaign_v"),
    ]
    for name, dlv in dlv_specs:
        body = dlv_var(name, dlv)
        v = workspaces.variables().create(parent=WS_PATH, body=body).execute()
        created["variables"].append(v["variableId"])
        print(f"  + {name} (id={v['variableId']})")

    print("\n=== 3) Triggers ===")
    # Custom event: form_submit_lvk
    t1 = workspaces.triggers().create(
        parent=WS_PATH,
        body=custom_event_trigger("Trigger - form_submit_lvk", "form_submit_lvk"),
    ).execute()
    created["triggers"].append(t1["triggerId"])
    print(f"  + Trigger - form_submit_lvk (id={t1['triggerId']})")

    # Custom event: whatsapp_click
    t2 = workspaces.triggers().create(
        parent=WS_PATH,
        body=custom_event_trigger("Trigger - whatsapp_click", "whatsapp_click"),
    ).execute()
    created["triggers"].append(t2["triggerId"])
    print(f"  + Trigger - whatsapp_click (id={t2['triggerId']})")

    # Scroll Depth (75%)
    t3 = workspaces.triggers().create(
        parent=WS_PATH,
        body={
            "name": "Trigger - scroll_75",
            "type": "scrollDepth",
            "parameter": [
                {"type": "BOOLEAN", "key": "verticalThresholdOn", "value": "true"},
                {"type": "TEMPLATE", "key": "verticalThresholdUnits", "value": "PERCENT"},
                {"type": "TEMPLATE", "key": "verticalThresholdsPercent", "value": "75"},
                {"type": "TEMPLATE", "key": "triggerStartOption", "value": "DOM_READY"},
            ],
        },
    ).execute()
    created["triggers"].append(t3["triggerId"])
    print(f"  + Trigger - scroll_75 (id={t3['triggerId']})")

    print("\n=== 4) Tags ===")
    # 4a) Custom HTML: lvk - Tracking Engine (All Pages)
    tag_engine = workspaces.tags().create(
        parent=WS_PATH,
        body={
            "name": "lvk - Tracking Engine",
            "type": "html",
            "parameter": [
                {"type": "TEMPLATE", "key": "html", "value": TRACKING_ENGINE_JS},
                {"type": "BOOLEAN", "key": "supportDocumentWrite", "value": "false"},
            ],
            "firingTriggerId": ["2147479553"],  # All Pages built-in
        },
    ).execute()
    created["tags"].append(tag_engine["tagId"])
    print(f"  + lvk - Tracking Engine (id={tag_engine['tagId']})")

    # 4b) GA4 Event: whatsapp_click
    tag_ga4_wa = workspaces.tags().create(
        parent=WS_PATH,
        body={
            "name": "GA4 Event - whatsapp_click",
            "type": "gaawe",  # GA4 Event tag
            "parameter": [
                {"type": "TEMPLATE", "key": "measurementIdOverride", "value": GA4_MEASUREMENT_ID},
                {"type": "TEMPLATE", "key": "eventName", "value": "whatsapp_click"},
                {
                    "type": "LIST", "key": "eventParameters",
                    "list": [
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "event_id"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{DLV - event_id}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "click_url"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{DLV - click_url}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "utm_source"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - utm_source}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "utm_medium"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - utm_medium}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "utm_campaign"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - utm_campaign}}"},
                        ]},
                    ],
                },
            ],
            "firingTriggerId": [t2["triggerId"]],
        },
    ).execute()
    created["tags"].append(tag_ga4_wa["tagId"])
    print(f"  + GA4 Event - whatsapp_click (id={tag_ga4_wa['tagId']})")

    # 4c) GA4 Event: form_submit (con dedup event_id + UTMs)
    tag_ga4_form = workspaces.tags().create(
        parent=WS_PATH,
        body={
            "name": "GA4 Event - lead (form_submit)",
            "type": "gaawe",
            "parameter": [
                {"type": "TEMPLATE", "key": "measurementIdOverride", "value": GA4_MEASUREMENT_ID},
                {"type": "TEMPLATE", "key": "eventName", "value": "lead"},
                {
                    "type": "LIST", "key": "eventParameters",
                    "list": [
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "event_id"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{DLV - event_id}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "form_id"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{DLV - form_id}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "utm_source"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - utm_source}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "utm_medium"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - utm_medium}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "utm_campaign"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - utm_campaign}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "fbclid"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - fbclid}}"},
                        ]},
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "gclid"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Cookie - gclid}}"},
                        ]},
                    ],
                },
            ],
            "firingTriggerId": [t1["triggerId"]],
        },
    ).execute()
    created["tags"].append(tag_ga4_form["tagId"])
    print(f"  + GA4 Event - lead (id={tag_ga4_form['tagId']})")

    # 4d) Meta Pixel - Lead (Custom HTML que dispara fbq)
    pixel_lead_html = """<script>
if (typeof fbq === 'function') {
  fbq('track', 'Lead', {}, {eventID: {{DLV - event_id}}});
}
</script>"""
    tag_pixel_lead = workspaces.tags().create(
        parent=WS_PATH,
        body={
            "name": "Meta Pixel - Lead",
            "type": "html",
            "parameter": [
                {"type": "TEMPLATE", "key": "html", "value": pixel_lead_html},
                {"type": "BOOLEAN", "key": "supportDocumentWrite", "value": "false"},
            ],
            "firingTriggerId": [t1["triggerId"]],
        },
    ).execute()
    created["tags"].append(tag_pixel_lead["tagId"])
    print(f"  + Meta Pixel - Lead (id={tag_pixel_lead['tagId']})")

    # 4e) Meta Pixel - Contact (whatsapp_click)
    pixel_contact_html = """<script>
if (typeof fbq === 'function') {
  fbq('track', 'Contact', {}, {eventID: {{DLV - event_id}}});
}
</script>"""
    tag_pixel_contact = workspaces.tags().create(
        parent=WS_PATH,
        body={
            "name": "Meta Pixel - Contact",
            "type": "html",
            "parameter": [
                {"type": "TEMPLATE", "key": "html", "value": pixel_contact_html},
                {"type": "BOOLEAN", "key": "supportDocumentWrite", "value": "false"},
            ],
            "firingTriggerId": [t2["triggerId"]],
        },
    ).execute()
    created["tags"].append(tag_pixel_contact["tagId"])
    print(f"  + Meta Pixel - Contact (id={tag_pixel_contact['tagId']})")

    # 4f) GA4 Event scroll milestone
    tag_ga4_scroll = workspaces.tags().create(
        parent=WS_PATH,
        body={
            "name": "GA4 Event - scroll_75",
            "type": "gaawe",
            "parameter": [
                {"type": "TEMPLATE", "key": "measurementIdOverride", "value": GA4_MEASUREMENT_ID},
                {"type": "TEMPLATE", "key": "eventName", "value": "scroll_75"},
                {
                    "type": "LIST", "key": "eventParameters",
                    "list": [
                        {"type": "MAP", "map": [
                            {"type": "TEMPLATE", "key": "name", "value": "page_url"},
                            {"type": "TEMPLATE", "key": "value", "value": "{{Page URL}}"},
                        ]},
                    ],
                },
            ],
            "firingTriggerId": [t3["triggerId"]],
        },
    ).execute()
    created["tags"].append(tag_ga4_scroll["tagId"])
    print(f"  + GA4 Event - scroll_75 (id={tag_ga4_scroll['tagId']})")

    print("\n=== Resumen ===")
    print(f"Variables creadas: {len(created['variables'])}")
    print(f"Triggers creados: {len(created['triggers'])}")
    print(f"Tags creados: {len(created['tags'])}")
    print("\nNO se publico version 18 todavia. Revisa con el script de inspect y publica con build_publish.")


if __name__ == "__main__":
    main()
