# Auditoria del Sistema RevOps — 2026-04-16

## 1. Resumen ejecutivo

El sistema RevOps de livskin.site opera sobre dos VPS independientes. Toda la infraestructura esta levantada y accesible por HTTPS. Los servicios estan aislados correctamente. No hay integraciones activas entre sistemas todavia — todos los componentes funcionan de forma independiente.

### Estado por capa

| Capa | Componente | Estado | Ubicacion |
|------|-----------|--------|-----------|
| Entrada | WordPress 6.9.4 | Operativo | VPS WP (46.101.97.246) |
| Tracking | PixelYourSite 11.2.0.4 | Instalado | VPS WP |
| Formularios | SureForms 2.7.0 | Instalado, webhook disponible | VPS WP |
| Reservas | LatePoint 5.3.2 | Instalado, webhook disponible | VPS WP |
| Automatizacion | n8n 2.14.2 | Operativo, sin workflows | VPS Ops (167.172.97.197) |
| CRM | Vtiger 8.2.0 | Operativo, sin configurar | VPS Ops |
| Base analitica | PostgreSQL 16 | Operativo, schema creado | VPS Ops |
| Dashboards | Metabase (latest) | Operativo, sin dashboards | VPS Ops |
| Reverse proxy | Nginx (stable) | Operativo, 3 sites | VPS Ops |

---

## 2. VPS WordPress — Livskin-WP-01

### Especificaciones

| Recurso | Valor | Estado |
|---------|-------|--------|
| IP | 46.101.97.246 | - |
| OS | Ubuntu 22.04.5 LTS | OK |
| CPU | 1 vCPU | Justo |
| RAM | 957 MB (453 MB usados, 47%) | Ajustado |
| Disco | 25 GB (4.3 GB usados, 18%) | OK |
| Stack | Nativo (sin Docker) | Correcto para WP |

### Software

| Componente | Version | Notas |
|-----------|---------|-------|
| WordPress | 6.9.4 | Actualizado |
| PHP | 8.1.2 FPM | OK |
| MariaDB | 10.6.23 | Solo localhost |
| Nginx | - | Con Let's Encrypt |
| Certbot SSL | Expira 2026-06-19 | Auto-renewal |

### Plugins activos

| Plugin | Version | Funcion RevOps |
|--------|---------|---------------|
| PixelYourSite | 11.2.0.4 | Tracking Meta/FB/Google/GTM/Pinterest/Bing/Reddit |
| SureForms | 2.7.0 | Formularios — tiene webhook nativo para integracion |
| LatePoint | 5.3.2 | Reservas/citas — tiene trigger_webhook |
| Complianz GDPR | - | Compliance cookies (legal) |
| Elementor | - | Page builder |
| Header Footer Elementor | - | Extension Elementor |
| UpdraftPlus | - | Backups (ultimo: 2026-03-30) |
| Duplicate Page | - | Utilidad menor |

### Seguridad

- [x] UFW activo (22, 80, 443)
- [x] Fail2Ban activo (3+ semanas uptime)
- [x] SSL Let's Encrypt (valido 64 dias mas)
- [x] wp-config.php bloqueado en Nginx
- [x] PHP en uploads bloqueado
- [x] Headers de seguridad configurados
- [x] MariaDB solo en 127.0.0.1
- [ ] No hay cron de mantenimiento visible
- [ ] Backups no automatizados (manual via UpdraftPlus)

### WordPress DB

- DB name: livskin_wp
- DB user: livskin_user
- DB host: localhost
- Table prefix: wp_

---

## 3. VPS Operaciones — livskin-vps-operations

### Especificaciones

| Recurso | Valor | Estado |
|---------|-------|--------|
| IP | 167.172.97.197 | - |
| OS | Ubuntu 22.04 LTS | OK |
| CPU | 2 vCPU | OK |
| RAM | 3.82 GB (2.03 GB Docker, 53%) | Vigilar |
| Disco | 78 GB (7.9 GB usados, 11%) | Amplio |
| Stack | Docker + Docker Compose | Correcto |

### Contenedores Docker

| Contenedor | Imagen | RAM | CPU | Estado |
|-----------|--------|-----|-----|--------|
| nginx | nginx:stable | 5 MB | 0.00% | Up 10 days |
| n8n | n8nio/n8n:latest (v2.14.2) | 267 MB | 0.40% | Up 10 days |
| vtiger | vtigercrm-8.2.0 | 446 MB | 1.03% | Up 10 days |
| vtiger-db | mariadb:10.6 | 93 MB | 0.02% | Up 10 days |
| postgres-analytics | postgres:16 | 86 MB | 0.76% | Up |
| metabase | metabase/metabase:latest | 1,142 MB | 1.91% | Up |
| **TOTAL** | | **2,039 MB** | | |

### Redes Docker

| Red | Contenedores | Proposito |
|-----|-------------|-----------|
| revops_net | nginx, n8n, vtiger, postgres-analytics, metabase | Comunicacion entre servicios |
| vtiger_vtiger_internal | vtiger, vtiger-db | Aislamiento DB del CRM |

### Subdominios

| Subdominio | Servicio | SSL | HTTP Status |
|-----------|----------|-----|-------------|
| flow.livskin.site | n8n | Cloudflare Origin Cert (Full Strict) | 200 |
| crm.livskin.site | Vtiger | Cloudflare Origin Cert (Full Strict) | 200 |
| dash.livskin.site | Metabase | Cloudflare Origin Cert (Full Strict) | 200 |

### Seguridad

- [x] UFW activo (22, 80, 443)
- [x] Fail2Ban activo (SSH: 3 intentos, ban 2h)
- [x] SSL Cloudflare Origin Certificate
- [x] Root login deshabilitado
- [x] DB no expuestas publicamente
- [x] Puertos internos no expuestos
- [ ] Backups no automatizados (scripts listos, falta cron)

### PostgreSQL Analytics — Schema

```sql
leads (id, external_id, email, phone, name, source, medium, campaign, landing_page, created_at, updated_at)
crm_stages (id, lead_id, crm_stage, changed_at)
opportunities (id, lead_id, amount, status, created_at, closed_at)
events (id, lead_id, event_type, event_time, metadata_json)
```

### Vtiger — Modulos disponibles

Leads, Contacts, Accounts, Potentials (Opportunities), Campaigns, Calendar, Events, HelpDesk, Invoice, Documents, Emails, ModTracker

### n8n

- Version: 2.14.2
- DB interna: SQLite
- Workflows: ninguno configurado
- Credenciales: ninguna configurada

---

## 4. Capacidades de integracion descubiertas

### SureForms (formularios)

SureForms 2.7.0 tiene soporte nativo de webhook en su sistema de integraciones. El campo de configuracion se llama `_srfm_integrations_webhooks`. Esto significa que puede enviar datos de formulario directamente a una URL externa (n8n webhook) sin necesidad de plugins adicionales.

**Campos que puede enviar:** todos los campos del formulario + metadata del submission.

### LatePoint (reservas)

LatePoint 5.3.2 tiene `trigger_webhook` como tipo de accion en su sistema de procesos (process_action). Esto permite disparar un webhook cuando ocurre un evento (nueva reserva, cancelacion, etc.).

**Datos que puede enviar:** informacion de la reserva, cliente, servicio, fecha/hora.

### PixelYourSite (tracking de ads)

PixelYourSite 11.2.0.4 tiene modulos para: Facebook, Google Analytics, GTM, Pinterest, Bing, Reddit. Captura automaticamente UTMs y parametros de tracking (fbclid, gclid). Estos datos pueden pasarse a formularios mediante campos hidden para que lleguen a n8n junto con el lead.

### WordPress REST API

La REST API de WordPress esta activa con rutas estandar. Esto permite que n8n consulte datos de WordPress si fuera necesario (posts, pages, media, etc.).

### Vtiger API

Vtiger 8.2.0 tiene API REST nativa. n8n tiene nodo oficial de Vtiger. La comunicacion seria:
- n8n -> Vtiger API (crear/actualizar leads, contactos, potentials)
- n8n -> Vtiger API (leer datos para ETL hacia PostgreSQL)

---

## 5. Mapa de conexiones — Estado actual vs Objetivo

### Estado actual (todo desconectado)

```
VPS WordPress                    VPS Operaciones
+-----------------+              +------------------+
| WordPress       |              | n8n (sin flows)  |
| SureForms       |   (nada)     | Vtiger (vacio)   |
| LatePoint       | -----X------ | PostgreSQL       |
| PixelYourSite   |              | Metabase         |
+-----------------+              +------------------+
```

### Objetivo

```
VPS WordPress                         VPS Operaciones
+-----------------+                   +------------------+
| WordPress       |                   |                  |
|                 |  webhook HTTPS    |  n8n             |
| SureForms ------|------------------>|--+-> Vtiger API  |
|                 |                   |  |   (create/    |
| LatePoint ------|------------------>|--+    update     |
|                 |                   |       lead)      |
| PixelYourSite   |                   |                  |
| (UTMs en hidden |                   |  n8n (ETL)       |
|  fields)        |                   |--+-> PostgreSQL  |
|                 |                   |  |               |
+-----------------+                   |  +-> Metabase    |
                                      +------------------+

Futuro:
WhatsApp API --------------------------------> n8n -> Vtiger
Meta/FB Ads API -----------------------------> n8n -> PostgreSQL
```

---

## 6. Como se conectan los dos VPS (explicacion profesional)

### El problema

Los dos VPS son maquinas completamente separadas. WordPress no sabe que n8n existe, y n8n no sabe que WordPress existe. No comparten red interna, no comparten base de datos, no se ven entre si.

### La solucion: webhooks sobre HTTPS

La forma profesional de conectar dos sistemas que viven en servidores distintos es mediante **webhooks**. Un webhook es una llamada HTTP que un sistema hace a otro cuando ocurre un evento.

### Como funciona paso a paso

```
1. Un visitante llena un formulario en livskin.site (SureForms)

2. SureForms detecta el envio y hace un HTTP POST a:
   https://flow.livskin.site/webhook/lead-nuevo
   (esta URL es un webhook de n8n)

3. El POST viaja por internet:
   WordPress (46.101.97.246) --HTTPS--> Cloudflare ---> Nginx (167.172.97.197) ---> n8n

4. n8n recibe el JSON con los datos del formulario:
   {
     "nombre": "Juan Perez",
     "email": "juan@email.com",
     "telefono": "+56912345678",
     "source": "facebook",
     "medium": "cpc",
     "campaign": "skincare-marzo",
     "landing_page": "/promo-facial"
   }

5. n8n procesa los datos:
   - Valida campos obligatorios
   - Normaliza formato (telefono, email)
   - Busca si ya existe en Vtiger (deduplicacion por email)
   - Si es nuevo: crea Lead en Vtiger
   - Si existe: actualiza el registro

6. n8n responde con HTTP 200 a WordPress (confirmacion)
```

### Por que esta es la forma profesional

1. **Seguridad**: La comunicacion va por HTTPS (cifrada). No se abren puertos adicionales. No se exponen bases de datos.

2. **Desacoplamiento**: WordPress no necesita saber nada de Docker, de Vtiger, ni de PostgreSQL. Solo conoce una URL. Si manana cambias n8n por otro sistema, WordPress sigue enviando al mismo webhook.

3. **Escalabilidad**: Puedes agregar mas fuentes (WhatsApp, Meta Ads API, otro formulario) sin tocar WordPress. Cada fuente envia a su propio webhook en n8n.

4. **Trazabilidad**: n8n guarda log de cada ejecucion. Puedes ver que llego, cuando, que se hizo con el dato, si fallo o no.

5. **Estandar de la industria**: Zapier, Make, HubSpot, Salesforce — todos usan webhooks para conectar sistemas. No es un hack, es el patron correcto.

### Diagrama de red real

```
Internet
    |
    v
Cloudflare (DNS + proxy + SSL)
    |
    +---> livskin.site ---------> VPS WordPress (46.101.97.246)
    |                              Nginx nativo -> PHP-FPM -> WordPress
    |
    +---> flow.livskin.site -----> VPS Operaciones (167.172.97.197)
    |                              Nginx Docker -> n8n
    +---> crm.livskin.site ------> Nginx Docker -> Vtiger
    +---> dash.livskin.site -----> Nginx Docker -> Metabase
```

### Flujo completo del dato (de ad a dashboard)

```
Meta/FB Ad
    |
    v
Usuario hace click -> llega a livskin.site/promo
    |
    v
PixelYourSite captura UTMs (source, medium, campaign, fbclid)
    |
    v
Usuario llena formulario SureForms (con UTMs en campos hidden)
    |
    v
SureForms envia webhook POST a https://flow.livskin.site/webhook/lead
    |
    v
n8n recibe, valida, normaliza
    |
    +---> Vtiger API: crear/actualizar Lead con todos los campos
    |
    v
n8n (ETL programado, ej: cada hora)
    |
    +---> Lee leads/stages/oportunidades de Vtiger
    +---> Inserta/actualiza en PostgreSQL analytics
    |
    v
Metabase consulta PostgreSQL
    |
    +---> Dashboard Marketing: leads por canal, campana, dia
    +---> Dashboard Ventas: leads por etapa, conversion
    +---> Dashboard Revenue: ingresos por canal, campana
```

### Sobre WhatsApp (futuro)

WhatsApp Business API funciona igual: es un webhook. Cuando alguien te escribe por WhatsApp, el proveedor (Twilio, 360dialog, o Meta Cloud API) envia un webhook a n8n con el mensaje. n8n procesa y crea/actualiza el lead en Vtiger. Mismo patron, distinta fuente.

---

## 7. Consideraciones criticas

### 7.1 RAM del VPS Operaciones (vigilar)

Metabase consume 1.14 GB solo. Con 2.03 GB en uso de 3.82 GB totales (53%), queda ~1.7 GB libres. Si agregas WhatsApp API u otro servicio Docker, necesitaras upgrade a 8 GB RAM.

### 7.2 RAM del VPS WordPress (limite)

Solo 957 MB total con 47% en uso. No hay margen para mas software. Si crece trafico, considerar upgrade.

### 7.3 Backups no automatizados (riesgo)

- WordPress: UpdraftPlus manual (ultimo hace 17 dias)
- Operaciones: scripts listos pero sin cron

Si cae un VPS hoy, se pierde configuracion reciente.

### 7.4 SSL WordPress

Let's Encrypt expira 2026-06-19. Verificar que Certbot auto-renewal funciona.

### 7.5 n8n completamente vacio

Sin workflows, sin credenciales. Es el primer sistema que necesita configuracion.

### 7.6 Vtiger sin configurar

Sin pipeline, sin campos custom, sin stages, sin reglas de negocio.

### 7.7 Gobierno de datos pendiente

Sin definir: campos minimos, deduplicacion, naming conventions, stages del pipeline.

---

## 8. Orden recomendado de integracion

| Paso | Tarea | Dependencia |
|------|-------|-------------|
| 1 | Definir gobierno de datos (campos, stages, naming) | Ninguna |
| 2 | Configurar Vtiger (pipeline, campos, stages) | Paso 1 |
| 3 | Configurar n8n (credenciales Vtiger, primer webhook) | Paso 2 |
| 4 | SureForms -> n8n webhook | Paso 3 |
| 5 | n8n -> Vtiger (crear/actualizar leads) | Paso 3 |
| 6 | PixelYourSite UTMs en formularios (campos hidden) | Paso 4 |
| 7 | n8n ETL -> PostgreSQL | Paso 5 |
| 8 | Metabase dashboards | Paso 7 |
| 9 | LatePoint -> n8n (reservas) | Paso 3 |
| 10 | Backups automaticos (cron ambos VPS) | Independiente |
| 11 | WhatsApp API | Cuando flujo base este estable |
