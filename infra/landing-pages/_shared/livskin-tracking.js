/**
 * livskin-tracking.js — Standalone tracking + form integration para landings
 *
 * Mini-bloque 3.6 (ADR-0031) — Sistema de convenciones reutilizable.
 *
 * Funcionalidad:
 *   1. UTM + click_ids persistence (cookies lvk_*, domain=.livskin.site, 90 días)
 *   2. event_id UUID v4 generation al form submit + WA click
 *   3. Form intercept → POST async a [A1] webhook (form-submit)
 *   4. Pixel Meta client-side firing con event_id deduplicado
 *   5. WhatsApp link intercept → POST + Pixel + event_id en URL
 *   6. localStorage queue para retry si n8n cae
 *   7. Banner consent ligero (cookies marketing opt-in)
 *
 * Convenciones HTML que la landing debe seguir:
 *   - <meta name="livskin-treatment" content="Botox">
 *   - <meta name="livskin-landing-slug" content="botox-mvp">
 *   - <form data-livskin-form="true">
 *   - inputs name="nombre", name="phone", name="email", name="consent_marketing"
 *   - <a data-livskin-wa="true" href="...">
 *   - <div data-livskin-banner="true"></div>
 *
 * Ver infra/landing-pages/_shared/conventions.md para spec completo.
 */
(function () {
  'use strict';

  // ───────────────────────────────────────────────────────────────
  // CONFIG (overridable via window.LIVSKIN_CONFIG en index.html)
  // ───────────────────────────────────────────────────────────────
  var DEFAULT_CONFIG = {
    pixel_id: '4410809639201712',
    webhook_url: 'https://flow.livskin.site/webhook/acquisition/form-submit',
    cookie_domain: '.livskin.site',
    cookie_max_age_days: 90,
    consent_required_marketing: true,
    consent_storage_key: 'lvk_consent',
    privacy_policy_url: '/privacy',
    cookie_policy_url: '/cookies'
  };
  var CONFIG = Object.assign({}, DEFAULT_CONFIG, window.LIVSKIN_CONFIG || {});

  // ───────────────────────────────────────────────────────────────
  // HELPERS
  // ───────────────────────────────────────────────────────────────

  function getMeta(name) {
    var el = document.querySelector('meta[name="' + name + '"]');
    return el ? el.getAttribute('content') : null;
  }

  function getQueryParam(name) {
    var match = window.location.search.match(new RegExp('[?&]' + name + '=([^&#]*)'));
    return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : '';
  }

  function getCookie(name) {
    var nameEQ = name + '=';
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i].trim();
      if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length));
    }
    return '';
  }

  function setCookie(name, value, days) {
    if (!value) return;
    var d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + '=' + encodeURIComponent(value) +
                      ';expires=' + d.toUTCString() +
                      ';path=/;domain=' + CONFIG.cookie_domain + ';SameSite=Lax';
  }

  function genUUID() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0;
      var v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  function getConsent() {
    return getCookie(CONFIG.consent_storage_key) || 'pending';
  }

  function setConsent(state) {
    // states: 'accepted_all' | 'rejected_all' | 'pending'
    setCookie(CONFIG.consent_storage_key, state, 365);
  }

  function hasMarketingConsent() {
    return getConsent() === 'accepted_all';
  }

  // ───────────────────────────────────────────────────────────────
  // UTM PERSISTENCE (cookies lvk_* domain=.livskin.site, 90 días)
  // ───────────────────────────────────────────────────────────────

  function captureAttribution() {
    var URL_TO_COOKIE = {
      utm_source: 'lvk_utm_source',
      utm_medium: 'lvk_utm_medium',
      utm_campaign: 'lvk_utm_campaign',
      utm_content: 'lvk_utm_content',
      utm_term: 'lvk_utm_term',
      fbclid: 'lvk_fbclid',
      gclid: 'lvk_gclid'
    };

    Object.keys(URL_TO_COOKIE).forEach(function (urlKey) {
      var fromUrl = getQueryParam(urlKey);
      if (fromUrl) setCookie(URL_TO_COOKIE[urlKey], fromUrl, CONFIG.cookie_max_age_days);
    });

    setCookie('lvk_landing_url', window.location.href, CONFIG.cookie_max_age_days);
  }

  function getAttribution() {
    return {
      utm_source: getQueryParam('utm_source') || getCookie('lvk_utm_source') || '',
      utm_medium: getQueryParam('utm_medium') || getCookie('lvk_utm_medium') || '',
      utm_campaign: getQueryParam('utm_campaign') || getCookie('lvk_utm_campaign') || '',
      utm_content: getQueryParam('utm_content') || getCookie('lvk_utm_content') || '',
      utm_term: getQueryParam('utm_term') || getCookie('lvk_utm_term') || '',
      fbclid: getQueryParam('fbclid') || getCookie('lvk_fbclid') || '',
      gclid: getQueryParam('gclid') || getCookie('lvk_gclid') || '',
      fbc: getCookie('_fbc') || '',
      ga: getCookie('_ga') || '',
      landing_url: getCookie('lvk_landing_url') || window.location.href
    };
  }

  // ───────────────────────────────────────────────────────────────
  // CONSENT BANNER (ligero, inyectado via JS)
  // ───────────────────────────────────────────────────────────────

  function injectConsentBanner() {
    if (getConsent() !== 'pending') return;

    var placeholder = document.querySelector('[data-livskin-banner="true"]');
    if (!placeholder) {
      placeholder = document.createElement('div');
      placeholder.setAttribute('data-livskin-banner', 'true');
      document.body.appendChild(placeholder);
    }

    if (!document.getElementById('lvk-consent-styles')) {
      var styleTag = document.createElement('style');
      styleTag.id = 'lvk-consent-styles';
      styleTag.textContent =
        '@keyframes lvkBackdropFade{from{opacity:0}to{opacity:1}}' +
        '@keyframes lvkCardIn{from{transform:scale(.94) translateY(8px);opacity:0}to{transform:scale(1) translateY(0);opacity:1}}' +
        '.lvk-consent-backdrop{position:fixed;inset:0;background:rgba(31,26,26,0.55);' +
        'z-index:999998;display:flex;align-items:center;justify-content:center;' +
        'padding:20px;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;' +
        'animation:lvkBackdropFade .35s ease .5s both}' +
        '.lvk-consent-card{background:#FFFFFF;color:#1F1A1A;border-radius:14px;' +
        'box-shadow:0 24px 64px rgba(31,26,26,0.35);max-width:480px;width:100%;' +
        'position:relative;padding:36px 32px 28px;' +
        'animation:lvkCardIn .4s cubic-bezier(.2,.8,.2,1) .6s both}' +
        '.lvk-consent-close{position:absolute;top:14px;right:14px;background:none;border:none;' +
        'font-size:22px;line-height:1;color:#8A847F;cursor:pointer;padding:6px 10px;' +
        'border-radius:50%;transition:background .15s,color .15s}' +
        '.lvk-consent-close:hover{background:#F2EDEB;color:#1F1A1A}' +
        '.lvk-consent-logo{display:flex;align-items:center;gap:10px;margin-bottom:18px}' +
        '.lvk-consent-logo-dots{display:flex;gap:4px}' +
        '.lvk-consent-logo-dots span{width:7px;height:7px;border-radius:50%;display:block}' +
        '.lvk-consent-logo-dots span:nth-child(1){background:#5BB5D6}' +
        '.lvk-consent-logo-dots span:nth-child(2){background:#F4A6BB}' +
        '.lvk-consent-logo-dots span:nth-child(3){background:#FCE8EC}' +
        '.lvk-consent-logo-text{font-family:Montserrat,system-ui,sans-serif;font-weight:600;' +
        'letter-spacing:.18em;font-size:13px;color:#1F1A1A;text-transform:uppercase}' +
        '.lvk-consent-title{font-family:Montserrat,system-ui,sans-serif;font-weight:600;' +
        'font-size:20px;letter-spacing:-.005em;margin:0 0 12px;color:#1F1A1A}' +
        '.lvk-consent-body{font-size:14.5px;line-height:1.55;color:#4A4441;margin:0 0 22px}' +
        '.lvk-consent-actions{display:flex;flex-direction:column;gap:10px;margin-bottom:14px}' +
        '.lvk-btn{font-family:inherit;font-size:14.5px;font-weight:600;padding:13px 22px;' +
        'border-radius:8px;cursor:pointer;line-height:1;letter-spacing:.01em;width:100%;' +
        'transition:transform .15s,box-shadow .15s,background .15s,border-color .15s}' +
        '.lvk-btn:hover{transform:translateY(-1px)}' +
        '.lvk-btn-primary{background:#F4A6BB;color:#FFF;border:none;box-shadow:0 4px 14px rgba(244,166,187,0.45)}' +
        '.lvk-btn-primary:hover{background:#E88AA2;box-shadow:0 6px 18px rgba(244,166,187,0.6)}' +
        '.lvk-btn-secondary{background:#FFF;color:#1F1A1A;border:1.5px solid #C9C2BF}' +
        '.lvk-btn-secondary:hover{border-color:#1F1A1A;background:#FAF8F7}' +
        '.lvk-consent-footer{display:flex;justify-content:center;font-size:12.5px;' +
        'border-top:1px solid #F2EDEB;padding-top:14px;margin-top:6px}' +
        '.lvk-consent-footer a{color:#8B1F1F;text-decoration:underline;font-weight:500}' +
        '.lvk-consent-footer a:hover{color:#1F1A1A}' +
        '@media (min-width:560px){' +
        '.lvk-consent-actions{flex-direction:row;flex-wrap:wrap}' +
        '.lvk-btn{width:auto;flex:1 1 0;min-width:120px}}' +
        '@media (max-width:480px){' +
        '.lvk-consent-card{padding:28px 22px 22px}' +
        '.lvk-consent-title{font-size:18px}' +
        '.lvk-consent-body{font-size:14px}}';
      document.head.appendChild(styleTag);
    }

    placeholder.innerHTML =
      '<div class="lvk-consent-backdrop" role="dialog" aria-modal="true" aria-labelledby="lvk-consent-title-h" aria-describedby="lvk-consent-body-p">' +
        '<div class="lvk-consent-card">' +
          '<button class="lvk-consent-close" id="lvk-consent-close" type="button" aria-label="Cerrar">&times;</button>' +
          '<div class="lvk-consent-logo">' +
            '<div class="lvk-consent-logo-dots"><span></span><span></span><span></span></div>' +
            '<span class="lvk-consent-logo-text">Livskin</span>' +
          '</div>' +
          '<h2 class="lvk-consent-title" id="lvk-consent-title-h">Gestionar cookies</h2>' +
          '<p class="lvk-consent-body" id="lvk-consent-body-p">' +
            'Usamos cookies para mejorar tu experiencia, analizar el tráfico y mostrarte ' +
            'campañas relevantes. Podés aceptar todas las cookies, rechazar las opcionales ' +
            'o configurar tus preferencias.' +
          '</p>' +
          '<div class="lvk-consent-actions">' +
            '<button id="lvk-consent-reject" class="lvk-btn lvk-btn-secondary" type="button">Rechazar</button>' +
            '<button id="lvk-consent-prefs"  class="lvk-btn lvk-btn-secondary" type="button">Preferencias</button>' +
            '<button id="lvk-consent-accept" class="lvk-btn lvk-btn-primary"   type="button">Aceptar</button>' +
          '</div>' +
          '<div class="lvk-consent-footer">' +
            '<a href="' + CONFIG.cookie_policy_url + '" target="_blank" rel="noopener">Política de privacidad</a>' +
          '</div>' +
        '</div>' +
      '</div>';

    var acceptBtn = document.getElementById('lvk-consent-accept');
    var rejectBtn = document.getElementById('lvk-consent-reject');
    var prefsBtn  = document.getElementById('lvk-consent-prefs');
    var closeBtn  = document.getElementById('lvk-consent-close');

    function dismiss() { placeholder.innerHTML = ''; }

    if (acceptBtn) acceptBtn.onclick = function () {
      setConsent('accepted_all');
      dismiss();
      loadPixel();
      firePixelEvent('PageView', {});
    };

    if (rejectBtn) rejectBtn.onclick = function () {
      setConsent('rejected_all');
      dismiss();
    };

    // "Preferencias" — hoy se comporta como "rechazar opcionales" (granular UI: futuro);
    // se setea cookie distinta para diferenciar en analytics si la gente prefiere fine-tuning.
    if (prefsBtn) prefsBtn.onclick = function () {
      setConsent('rejected_all');
      dismiss();
    };

    // ✕ — cierre sin decisión: no setea cookie permanente; banner volverá a aparecer en próxima visita.
    if (closeBtn) closeBtn.onclick = function () {
      dismiss();
    };
  }

  // ───────────────────────────────────────────────────────────────
  // META PIXEL — load + fire (only with consent)
  // ───────────────────────────────────────────────────────────────

  function loadPixel() {
    if (window.fbq) return;
    /* Standard Meta Pixel snippet */
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0';
      n.queue = []; t = b.createElement(e); t.async = !0;
      t.src = v; s = b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t, s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    window.fbq('init', CONFIG.pixel_id);
  }

  function firePixelEvent(eventName, customData) {
    if (!hasMarketingConsent()) return null;
    if (!window.fbq) loadPixel();
    var eventId = (customData && customData.event_id) || genUUID();
    var data = Object.assign({}, customData);
    delete data.event_id;
    window.fbq('track', eventName, data, { eventID: eventId });
    return eventId;
  }

  // ───────────────────────────────────────────────────────────────
  // FORM CAPTURE
  // ───────────────────────────────────────────────────────────────

  function findLivskinForm() {
    return document.querySelector('form[data-livskin-form="true"], form.livskin-form');
  }

  function captureFormFields(form) {
    var fields = {};
    ['nombre', 'phone', 'email', 'tratamiento', 'horario', 'mensaje'].forEach(function (n) {
      var input = form.querySelector('[name="' + n + '"]');
      if (input) fields[n] = (input.value || '').trim();
    });

    var consentInput = form.querySelector('[name="consent_marketing"]');
    fields.consent_marketing = consentInput ? consentInput.checked : false;

    var extras = {};
    form.querySelectorAll('[data-livskin-extra="true"]').forEach(function (el) {
      var key = el.getAttribute('data-livskin-erp-field') || el.name;
      if (key && el.value) extras[key] = el.value;
    });
    if (Object.keys(extras).length) fields.extra_fields = extras;

    return fields;
  }

  function buildPayload(fields, eventId) {
    var attribution = getAttribution();
    var treatment = getMeta('livskin-treatment') || fields.tratamiento || '';

    var payload = {
      nombre: fields.nombre || '',
      phone: fields.phone || '',
      email: fields.email || '',
      tratamiento_interes: fields.tratamiento || treatment,
      horario: fields.horario || '',
      mensaje: fields.mensaje || '',
      consent_marketing: fields.consent_marketing,
      utm_source: attribution.utm_source,
      utm_medium: attribution.utm_medium,
      utm_campaign: attribution.utm_campaign,
      utm_content: attribution.utm_content,
      utm_term: attribution.utm_term,
      fbclid: attribution.fbclid,
      gclid: attribution.gclid,
      fbc: attribution.fbc,
      ga: attribution.ga,
      event_id: eventId,
      landing_url: attribution.landing_url,
      landing_slug: getMeta('livskin-landing-slug') || '',
      _payload_version: '1.0',
      _source: 'livskin-tracking-js'
    };

    if (fields.extra_fields) payload.extra_fields = fields.extra_fields;
    return payload;
  }

  function postToWebhook(payload, callback) {
    try {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', CONFIG.webhook_url, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.timeout = 10000;
      xhr.onload = function () {
        var ok = xhr.status >= 200 && xhr.status < 300;
        if (!ok) queueForRetry(payload);
        if (callback) callback(ok, xhr.status);
      };
      xhr.onerror = function () { queueForRetry(payload); if (callback) callback(false, 0); };
      xhr.ontimeout = xhr.onerror;
      xhr.send(JSON.stringify(payload));
    } catch (e) {
      queueForRetry(payload);
      if (callback) callback(false, 0);
    }
  }

  // ───────────────────────────────────────────────────────────────
  // QUEUE / RETRY (localStorage)
  // ───────────────────────────────────────────────────────────────

  var QUEUE_KEY = 'lvk_queue';
  var QUEUE_MAX_ITEMS = 10;
  var QUEUE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000; // 7 días

  function queueForRetry(payload) {
    try {
      var queue = JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
      queue.push({ payload: payload, queued_at: Date.now() });
      localStorage.setItem(QUEUE_KEY, JSON.stringify(queue.slice(-QUEUE_MAX_ITEMS)));
    } catch (e) { /* localStorage full or disabled — drop */ }
  }

  function flushQueue() {
    try {
      var queue = JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
      if (!queue.length) return;
      var pending = [];
      var processed = 0;

      queue.forEach(function (item) {
        if (Date.now() - item.queued_at > QUEUE_MAX_AGE_MS) { processed++; return; }
        postToWebhook(item.payload, function (ok) {
          processed++;
          if (!ok) pending.push(item);
          if (processed === queue.length) {
            localStorage.setItem(QUEUE_KEY, JSON.stringify(pending));
          }
        });
      });
    } catch (e) { /* localStorage error — skip */ }
  }

  // ───────────────────────────────────────────────────────────────
  // FORM SUBMIT HANDLER
  // ───────────────────────────────────────────────────────────────

  function attachFormHandler(form) {
    if (form.dataset.lvkAttached === 'true') return;
    form.dataset.lvkAttached = 'true';

    form.addEventListener('submit', function () {
      var fields = captureFormFields(form);
      if (!fields.consent_marketing) return; // browser native validation handles this

      var eventId = genUUID();
      var payload = buildPayload(fields, eventId);

      // Pixel client-side fire (con same event_id para dedup con CAPI server-side)
      firePixelEvent('Lead', {
        event_id: eventId,
        content_name: payload.tratamiento_interes,
        content_category: 'lead_acquisition'
      });

      // POST async a [A1] (sin bloquear submit)
      postToWebhook(payload);
    }, true);
  }

  // ───────────────────────────────────────────────────────────────
  // WHATSAPP LINK INTERCEPT
  // ───────────────────────────────────────────────────────────────

  function attachWaHandlers() {
    document.querySelectorAll('a[data-livskin-wa="true"]').forEach(function (link) {
      if (link.dataset.lvkAttached === 'true') return;
      link.dataset.lvkAttached = 'true';

      // Forzar nueva pestaña — no perder al visitante de la landing al click WA
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');

      link.addEventListener('click', function () {
        var eventId = genUUID();
        var treatment = getMeta('livskin-treatment') || '';

        firePixelEvent('Lead', {
          event_id: eventId,
          content_name: treatment,
          content_category: 'wa_click'
        });

        var attribution = getAttribution();
        var payload = {
          nombre: '(WhatsApp click)',
          phone: '',
          email: '',
          tratamiento_interes: treatment,
          consent_marketing: hasMarketingConsent(),
          event_id: eventId,
          _source: 'wa-click',
          landing_slug: getMeta('livskin-landing-slug') || '',
          landing_url: attribution.landing_url,
          utm_source: attribution.utm_source,
          utm_medium: attribution.utm_medium,
          utm_campaign: attribution.utm_campaign,
          utm_content: attribution.utm_content,
          utm_term: attribution.utm_term,
          fbclid: attribution.fbclid,
          gclid: attribution.gclid,
          fbc: attribution.fbc,
          ga: attribution.ga,
          _payload_version: '1.0'
        };
        postToWebhook(payload);

        // Append event_id to WA href (para que llegue al admin si revisa link)
        try {
          var url = new URL(link.href);
          url.searchParams.set('event_id', eventId);
          link.href = url.toString();
        } catch (e) { /* URL parse failed — skip */ }
      });
    });
  }

  // ───────────────────────────────────────────────────────────────
  // MAIN INIT
  // ───────────────────────────────────────────────────────────────

  function init() {
    captureAttribution();

    if (CONFIG.consent_required_marketing) {
      injectConsentBanner();
    }

    if (hasMarketingConsent()) {
      loadPixel();
      firePixelEvent('PageView', {});
    }

    var form = findLivskinForm();
    if (form) attachFormHandler(form);
    attachWaHandlers();
    flushQueue();

    // Re-scan defensive (for forms/links rendered late by React/Vue/etc.)
    var attempts = 0;
    var interval = setInterval(function () {
      var f = findLivskinForm();
      if (f) attachFormHandler(f);
      attachWaHandlers();
      if (++attempts >= 5) clearInterval(interval);
    }, 2000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Public API (debug + override)
  window.LivskinTracking = {
    config: CONFIG,
    getAttribution: getAttribution,
    getConsent: getConsent,
    setConsent: setConsent,
    hasMarketingConsent: hasMarketingConsent,
    fireEvent: firePixelEvent,
    flushQueue: flushQueue,
    _version: '1.0'
  };
})();
