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

    placeholder.innerHTML =
      '<div role="dialog" aria-label="Consentimiento de cookies" ' +
      'style="position:fixed;bottom:0;left:0;right:0;background:#1F1A1A;color:#FFF;' +
      'padding:16px 20px;z-index:9999;display:flex;flex-direction:column;gap:12px;' +
      'box-shadow:0 -4px 12px rgba(0,0,0,0.15);font-family:system-ui,-apple-system,sans-serif;' +
      'font-size:14px;line-height:1.5;">' +
      '<div>Usamos cookies para analizar tu visita y atribuir campañas. ' +
      '<a href="' + CONFIG.cookie_policy_url + '" target="_blank" rel="noopener" ' +
      'style="color:#F4A6BB;text-decoration:underline">Política de cookies</a>.</div>' +
      '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
      '<button id="lvk-consent-accept" type="button" ' +
      'style="background:#F4A6BB;color:#FFF;border:none;padding:10px 20px;border-radius:4px;' +
      'cursor:pointer;font-weight:600;font-size:14px;">Aceptar todas</button>' +
      '<button id="lvk-consent-reject" type="button" ' +
      'style="background:transparent;color:#FFF;border:1px solid #FFF;padding:10px 20px;' +
      'border-radius:4px;cursor:pointer;font-size:14px;">Solo esenciales</button>' +
      '</div></div>';

    var acceptBtn = document.getElementById('lvk-consent-accept');
    var rejectBtn = document.getElementById('lvk-consent-reject');

    if (acceptBtn) acceptBtn.onclick = function () {
      setConsent('accepted_all');
      placeholder.innerHTML = '';
      loadPixel();
      firePixelEvent('PageView', {});
    };

    if (rejectBtn) rejectBtn.onclick = function () {
      setConsent('rejected_all');
      placeholder.innerHTML = '';
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
