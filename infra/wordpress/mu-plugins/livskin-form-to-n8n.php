<?php
/**
 * Plugin Name: Livskin Form to n8n Integration
 * Description: Captura submissions de SureForms y POSTea a n8n [A1] webhook con
 *              tracking attribution completo (UTMs + click_ids + cookies + event_id).
 *              Form-id agnostic + opt-in por post_meta. Adaptable a múltiples forms.
 * Version: 1.0.0
 * Author: Livskin RevOps
 *
 * Documentación completa: docs/runbooks/wordpress-form-livskin-integration.md
 *
 * Decisiones arquitectónicas (resumen):
 * - Form 1569 NO se modifica estructuralmente — los hidden inputs se inyectan via JS
 * - Mapping de campos por slug semántico (resiliente a renames de labels)
 * - Modo opt-in: 'prod' (POST a n8n), 'test' (solo log), 'off' (no hace nada)
 * - Fire-and-forget POST (non-blocking — UX del form no bloqueada por n8n)
 * - Fallback hardcoded para forms canónicos si post_meta no está seteado
 *
 * Cómo activar un form nuevo:
 * 1. Crear form en SureForms admin
 * 2. Setear post_meta '_livskin_n8n_sync' = 'prod' (o 'test')
 *    O agregarlo al array LIVSKIN_FORMS_DEFAULT abajo
 * 3. Verificar en error_log que las submissions disparan POST a n8n
 *
 * Adaptarse a ediciones del form:
 * - Renombrar field labels: SIGUE funcionando (matching por slug)
 * - Reordenar fields: SIGUE funcionando
 * - Agregar field nuevo: pasa silently (n8n schema lo ignora si no está mapeado)
 * - Eliminar field: mu-plugin omite silently
 */

// Bloquear acceso directo
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ─────────────────────────────────────────────────────────────────────
// CONFIG — adaptable sin tocar lógica
// ─────────────────────────────────────────────────────────────────────

if ( ! defined( 'LIVSKIN_WEBHOOK_PROD' ) ) {
    define( 'LIVSKIN_WEBHOOK_PROD', 'https://flow.livskin.site/webhook/acquisition/form-submit' );
}

/**
 * Forms canónicos hardcoded — fallback si post_meta '_livskin_n8n_sync' no está seteado.
 * Para activar un form nuevo: agregarlo acá O setear post_meta en admin.
 */
function livskin_forms_default() {
    return [
        1569 => [
            'mode' => 'prod',
            'treatment_default' => null, // landing genérica home, sin tratamiento default
        ],
        // Ejemplos para forms futuros:
        // 1570 => ['mode' => 'prod', 'treatment_default' => 'Botox'],     // landing /botox
        // 1571 => ['mode' => 'prod', 'treatment_default' => 'PRP'],       // landing /prp
        // 1572 => ['mode' => 'test', 'treatment_default' => null],        // form en pruebas
    ];
}

/**
 * Hidden inputs estándar que el mu-plugin inyecta en TODOS los SureForms forms.
 * GTM Tracking Engine (Mini-bloque 3.2) los populates al cargar página + al submit.
 */
function livskin_hidden_inputs() {
    return [
        'lvk_utm_source', 'lvk_utm_medium', 'lvk_utm_campaign',
        'lvk_utm_content', 'lvk_utm_term',
        'lvk_fbclid', 'lvk_gclid',
        'lvk_fbc', 'lvk_ga',
        'lvk_event_id', 'lvk_landing_url',
    ];
}

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

/**
 * Devuelve el modo de sync del form: 'prod' | 'test' | 'off'.
 * Prioridad: post_meta > hardcoded default > 'off'.
 */
function livskin_get_form_mode( $form_id ) {
    $form_id = intval( $form_id );
    if ( ! $form_id ) {
        return 'off';
    }

    $meta = get_post_meta( $form_id, '_livskin_n8n_sync', true );
    if ( $meta && in_array( $meta, [ 'prod', 'test', 'off' ], true ) ) {
        return $meta;
    }

    $defaults = livskin_forms_default();
    return $defaults[ $form_id ]['mode'] ?? 'off';
}

/**
 * Devuelve treatment default si form lo tiene configurado (para landings).
 */
function livskin_get_treatment_default( $form_id ) {
    $form_id = intval( $form_id );
    $defaults = livskin_forms_default();
    return $defaults[ $form_id ]['treatment_default'] ?? null;
}

/**
 * Mapea $modified_message (SureForms) → user-fillable fields del payload n8n.
 *
 * Estrategia defensiva multi-pass:
 *   Pass 1: match exacto por key conocida (text-field, email, phone-number, dropdown)
 *   Pass 2: fuzzy match (key contains 'phone', 'email', 'tel', 'tratamiento', etc.)
 *
 * Logueamos todo el $data raw a error_log para debugging del primer real submission.
 */
function livskin_extract_user_fields( $data ) {
    $fields = [
        'nombre' => '',
        'phone'  => '',
        'email'  => '',
        'tratamiento_interes' => '',
    ];

    if ( ! is_array( $data ) ) {
        return $fields;
    }

    // Pass 1: keys exactas (slug match)
    if ( isset( $data['email'] ) ) {
        $fields['email'] = livskin_normalize_value( $data['email'] );
    }
    if ( isset( $data['phone-number'] ) ) {
        $fields['phone'] = livskin_normalize_value( $data['phone-number'] );
    }
    if ( isset( $data['dropdown'] ) ) {
        $fields['tratamiento_interes'] = livskin_normalize_value( $data['dropdown'] );
    }
    if ( isset( $data['text-field'] ) ) {
        $fields['nombre'] = livskin_normalize_value( $data['text-field'] );
    }

    // Pass 2: fuzzy match para keys variants (form 1570+ podría tener labels distintos)
    foreach ( $data as $key => $value ) {
        $key_lower = strtolower( (string) $key );
        $val_str = livskin_normalize_value( $value );
        if ( empty( $val_str ) ) {
            continue;
        }

        if ( empty( $fields['phone'] ) && (
            strpos( $key_lower, 'phone' ) !== false ||
            strpos( $key_lower, 'tel' ) !== false ||
            strpos( $key_lower, 'whatsapp' ) !== false ||
            strpos( $key_lower, 'celular' ) !== false
        ) ) {
            $fields['phone'] = $val_str;
        }

        if ( empty( $fields['email'] ) && (
            strpos( $key_lower, 'email' ) !== false ||
            strpos( $key_lower, 'correo' ) !== false
        ) ) {
            $fields['email'] = $val_str;
        }

        if ( empty( $fields['tratamiento_interes'] ) && (
            strpos( $key_lower, 'dropdown' ) !== false ||
            strpos( $key_lower, 'tratamiento' ) !== false ||
            strpos( $key_lower, 'treatment' ) !== false ||
            strpos( $key_lower, 'servicio' ) !== false
        ) ) {
            $fields['tratamiento_interes'] = $val_str;
        }

        if ( empty( $fields['nombre'] ) && (
            strpos( $key_lower, 'text-field' ) !== false ||
            strpos( $key_lower, 'nombre' ) !== false ||
            strpos( $key_lower, 'name' ) !== false
        ) ) {
            $fields['nombre'] = $val_str;
        }
    }

    return $fields;
}

/**
 * Convierte value (string|array) a string normalizado.
 * Arrays (multiSelect dropdown, multi-checkbox) → comma-separated.
 */
function livskin_normalize_value( $value ) {
    if ( is_array( $value ) ) {
        $value = implode( ', ', array_filter( array_map( 'strval', $value ) ) );
    }
    return trim( html_entity_decode( (string) $value, ENT_QUOTES, 'UTF-8' ) );
}

/**
 * Construye el payload completo a postear a n8n.
 */
function livskin_build_payload( $form_id, $data ) {
    $user = livskin_extract_user_fields( $data );

    // Fallback: si tratamiento vacío Y el form tiene default → usarlo
    if ( empty( $user['tratamiento_interes'] ) ) {
        $default = livskin_get_treatment_default( $form_id );
        if ( ! empty( $default ) ) {
            $user['tratamiento_interes'] = $default;
        }
    }

    // Hidden fields desde $_POST (rellenos por GTM Tracking Engine)
    $tracking = [
        'utm_source'   => livskin_post_field( 'lvk_utm_source' ),
        'utm_medium'   => livskin_post_field( 'lvk_utm_medium' ),
        'utm_campaign' => livskin_post_field( 'lvk_utm_campaign' ),
        'utm_content'  => livskin_post_field( 'lvk_utm_content' ),
        'utm_term'     => livskin_post_field( 'lvk_utm_term' ),
        'fbclid'       => livskin_post_field( 'lvk_fbclid' ),
        'gclid'        => livskin_post_field( 'lvk_gclid' ),
        'fbc'          => livskin_post_field( 'lvk_fbc' )    ?: livskin_cookie_field( '_fbc' ),
        'ga'           => livskin_post_field( 'lvk_ga' )     ?: livskin_cookie_field( '_ga' ),
        'event_id'     => livskin_post_field( 'lvk_event_id' ),
        'landing_url'  => livskin_post_field( 'lvk_landing_url' ),
    ];

    // Server-side context
    $server = [
        'ip_at_submit' => livskin_extract_ip(),
        'ua_at_submit' => isset( $_SERVER['HTTP_USER_AGENT'] ) ? sanitize_text_field( wp_unslash( $_SERVER['HTTP_USER_AGENT'] ) ) : '',
        'referer'      => isset( $_SERVER['HTTP_REFERER'] ) ? esc_url_raw( wp_unslash( $_SERVER['HTTP_REFERER'] ) ) : '',
    ];

    return array_merge(
        $user,
        $tracking,
        $server,
        [
            'form_id' => intval( $form_id ),
            'consent_marketing' => true, // implícito al submitear (legal en footer del form)
            '_livskin_payload_version' => '1.0',
        ]
    );
}

function livskin_post_field( $key ) {
    return isset( $_POST[ $key ] ) ? sanitize_text_field( wp_unslash( $_POST[ $key ] ) ) : '';
}

function livskin_cookie_field( $key ) {
    return isset( $_COOKIE[ $key ] ) ? sanitize_text_field( wp_unslash( $_COOKIE[ $key ] ) ) : '';
}

function livskin_extract_ip() {
    // Cloudflare passes real IP en X-Forwarded-For. Tomar primera IP del header.
    $xff = isset( $_SERVER['HTTP_X_FORWARDED_FOR'] ) ? wp_unslash( $_SERVER['HTTP_X_FORWARDED_FOR'] ) : '';
    if ( $xff ) {
        $first = trim( explode( ',', $xff )[0] );
        if ( $first ) {
            return $first;
        }
    }
    return isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '';
}

/**
 * POST fire-and-forget al webhook n8n. Non-blocking — UX del form NO bloqueada.
 * Loguea a WP error_log el resultado (success/fail) para debug.
 */
function livskin_post_to_n8n( $webhook, $payload, $form_id ) {
    $args = [
        'body'        => wp_json_encode( $payload ),
        'headers'     => [ 'Content-Type' => 'application/json' ],
        'timeout'     => 5,    // hardcap 5s (no bloquea form si n8n lento)
        'blocking'    => false, // FIRE-AND-FORGET
        'data_format' => 'body',
    ];
    wp_remote_post( $webhook, $args );

    // Log resumen (sin PII completa) para debug
    error_log( sprintf(
        '[livskin] form_id=%d webhook=%s nombre_present=%d phone_present=%d email_present=%d tratamiento=%s event_id=%s',
        $form_id,
        $webhook,
        ! empty( $payload['nombre'] ) ? 1 : 0,
        ! empty( $payload['phone'] ) ? 1 : 0,
        ! empty( $payload['email'] ) ? 1 : 0,
        $payload['tratamiento_interes'] ?? '',
        $payload['event_id'] ?? ''
    ) );
}

// ─────────────────────────────────────────────────────────────────────
// HOOK 1 — Inyectar hidden inputs vía JS al renderear cualquier SureForms form
// ─────────────────────────────────────────────────────────────────────

add_action( 'wp_footer', function () {
    $hidden = livskin_hidden_inputs();
    ?>
    <script id="livskin-form-tracking-inject">
    (function() {
      var INPUTS = <?php echo wp_json_encode( $hidden ); ?>;
      var COOKIE_DAYS = 90;

      // ─── Helpers ───────────────────────────────────────────────

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
                          ';path=/;SameSite=Lax';
      }

      function genUUID() {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
          return crypto.randomUUID();
        }
        // Fallback RFC4122 v4
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          var r = Math.random() * 16 | 0;
          var v = c === 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
        });
      }

      // ─── Inject hidden inputs into form ─────────────────────────

      function inject() {
        var forms = document.querySelectorAll('form.srfm-form, form[id^="srfm-form-"]');
        forms.forEach(function(form) {
          INPUTS.forEach(function(name) {
            if (form.querySelector('input[name="' + name + '"]')) return;
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = '';
            form.appendChild(input);
          });
          populate(form);
          attachSubmitHandler(form);
        });
      }

      // ─── Populate hidden inputs from URL params + cookies ───────

      function populate(form) {
        // Map de URL param name → input name. UTMs + click IDs.
        var URL_TO_INPUT = {
          'utm_source':   'lvk_utm_source',
          'utm_medium':   'lvk_utm_medium',
          'utm_campaign': 'lvk_utm_campaign',
          'utm_content':  'lvk_utm_content',
          'utm_term':     'lvk_utm_term',
          'fbclid':       'lvk_fbclid',
          'gclid':        'lvk_gclid'
        };

        // Para cada UTM / click ID:
        //   1. Si URL trae el param → usa ese valor + persiste en cookie 90d
        //   2. Si URL vacío → usa cookie lvk_* (persistencia de visitas previas)
        //   3. Si ambos vacíos → input queda vacío (correcto)
        Object.keys(URL_TO_INPUT).forEach(function(urlName) {
          var inputName = URL_TO_INPUT[urlName];
          var input = form.querySelector('input[name="' + inputName + '"]');
          if (!input) return;
          var fromUrl = getQueryParam(urlName);
          if (fromUrl) {
            input.value = fromUrl;
            setCookie(inputName, fromUrl, COOKIE_DAYS);
          } else {
            input.value = getCookie(inputName) || '';
          }
        });

        // Cookies third-party seteadas por Pixel y GA automáticamente
        var fbcInput = form.querySelector('input[name="lvk_fbc"]');
        if (fbcInput) fbcInput.value = getCookie('_fbc') || '';
        var gaInput = form.querySelector('input[name="lvk_ga"]');
        if (gaInput) gaInput.value = getCookie('_ga') || '';

        // landing_url = URL completa de la página (no de la submission, sino de la landing)
        var landingInput = form.querySelector('input[name="lvk_landing_url"]');
        if (landingInput && !landingInput.value) {
          landingInput.value = window.location.href;
        }

        // event_id se setea recién en submit (no al page load — múltiples submits = múltiples IDs)
      }

      // ─── Submit listener para generar event_id único por submission ───

      function attachSubmitHandler(form) {
        if (form.dataset.lvkSubmitAttached === 'true') return;
        form.dataset.lvkSubmitAttached = 'true';
        form.addEventListener('submit', function() {
          var eventInput = form.querySelector('input[name="lvk_event_id"]');
          if (eventInput) eventInput.value = genUUID();
          // landing_url defensive re-set (en caso form se rendereó después de page load)
          var landingInput = form.querySelector('input[name="lvk_landing_url"]');
          if (landingInput && !landingInput.value) landingInput.value = window.location.href;
        }, true); // useCapture=true — fires antes del fetch interno de SureForms
      }

      // ─── Run sequence ───────────────────────────────────────────

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inject);
      } else {
        inject();
      }
      // Re-run cada 2s durante 10s — defensa contra forms que se renderean lazy
      var attempts = 0;
      var interval = setInterval(function() {
        inject();
        if (++attempts >= 5) clearInterval(interval);
      }, 2000);
    })();
    </script>
    <?php
}, 99 );

// ─────────────────────────────────────────────────────────────────────
// HOOK 2 — Capturar submission y POST a n8n
// ─────────────────────────────────────────────────────────────────────

add_action( 'srfm_before_submission', function ( $form_before_submission_data ) {
    // SureForms pasa array con form_id + data
    if ( ! is_array( $form_before_submission_data ) ) {
        return;
    }

    $form_id = isset( $form_before_submission_data['form_id'] ) ? intval( $form_before_submission_data['form_id'] ) : 0;
    $data    = isset( $form_before_submission_data['data'] ) ? $form_before_submission_data['data'] : [];

    if ( ! $form_id ) {
        return;
    }

    $mode = livskin_get_form_mode( $form_id );

    if ( $mode === 'off' ) {
        return; // form no opt-in
    }

    // Log raw data para debugging (primera submission real reveal del formato exacto)
    error_log( '[livskin] srfm_before_submission form_id=' . $form_id . ' mode=' . $mode .
               ' raw_data_keys=' . wp_json_encode( array_keys( (array) $data ) ) );

    if ( $mode === 'test' ) {
        // En test mode: log payload completo, NO postea a n8n
        $payload = livskin_build_payload( $form_id, $data );
        error_log( '[livskin][TEST] form_id=' . $form_id . ' payload=' . wp_json_encode( $payload ) );
        return;
    }

    // mode === 'prod' → POST real
    try {
        $payload = livskin_build_payload( $form_id, $data );
        livskin_post_to_n8n( LIVSKIN_WEBHOOK_PROD, $payload, $form_id );
    } catch ( \Throwable $e ) {
        // NUNCA fallar el submission del form por error en mu-plugin
        error_log( '[livskin] EXCEPTION form_id=' . $form_id . ' msg=' . $e->getMessage() );
    }
}, 10, 1 );
