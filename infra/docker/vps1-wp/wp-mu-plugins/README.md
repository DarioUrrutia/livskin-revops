# WordPress mu-plugins (must-use plugins)

Esta carpeta se sincroniza con `/var/www/livskin/wp-content/mu-plugins/` en VPS 1
vía el workflow `deploy-vps1.yml`.

## Qué es un mu-plugin

Plugins **must-use**: WordPress los carga automáticamente sin necesidad de
activación desde el admin. Son código custom que el equipo mantiene como parte
del repo (versionado), no plugins de terceros instalados por UI.

## Plugins planeados (Fase 3)

| Archivo | Propósito | Estado |
|---|---|---|
| `livskin-utm-persistence.php` | Captura UTMs de URL → guarda en localStorage del navegador → adjunta a SureForms submissions | ⏳ Fase 3 |
| `livskin-tracking-context.php` | Inyecta `data-livskin-context` en pages: cliente_id (si está logueado), session_id, consent state | ⏳ Fase 3 |
| `livskin-form-webhook.php` | Hook a SureForms `wp_after_insert_post` que envía payload a https://flow.livskin.site/webhook/sureforms con UTMs + fbclid + consent | ⏳ Fase 3 |

## Cómo agregar uno nuevo

1. Crear archivo `.php` en este directorio
2. Header WP estándar:
   ```php
   <?php
   /**
    * Plugin Name: Livskin <Name>
    * Description: ...
    * Version: 1.0
    */
   ```
3. Push al branch → CI/CD lo despliega vía rsync
4. WordPress lo carga automáticamente en el siguiente request

## Por qué mu-plugins y no theme functions.php

- Independencia del theme (sobrevive a cambios)
- No requiere activación
- Versionable
- No se desactiva por accident
