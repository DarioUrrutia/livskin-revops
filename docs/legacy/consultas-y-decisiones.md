# Consultas, decisiones y conceptos — Sesion 2026-04-16

Este documento resume todas las consultas realizadas durante la primera sesion de trabajo con Claude Code, las decisiones tomadas, los conceptos explicados y el estado resultante. Sirve como base de continuidad para futuras sesiones.

---

## 1. Estado del proyecto al iniciar esta sesion

### Que existia antes de hoy

- VPS Operaciones (167.172.97.197) con Docker, Nginx, n8n y Vtiger funcionando
- VPS WordPress (46.101.97.246) con WordPress 6.9.4 operativo en livskin.site
- Repo GitHub (DarioUrrutia/livskin-revops) con estructura basica
- Subdominios flow.livskin.site y crm.livskin.site activos
- Fases 0-3 del brief maestro completadas parcialmente

### Que faltaba

- Fail2Ban no estaba activo en VPS Operaciones
- PostgreSQL analytics no instalado
- Metabase no instalado
- Subdominio dash.livskin.site no existia
- Estructura del repo GitHub incompleta
- Sin acceso SSH desde Claude Code a ningun VPS
- Sin documentacion de auditoria
- Sin conexion entre WordPress y el backend

---

## 2. Lo que se hizo en esta sesion

### Acceso SSH establecido

- Se genero clave SSH ed25519 para VPS Operaciones (.ssh/livskin_vps)
- Se genero clave SSH ed25519 para VPS WordPress (.ssh/wordpress_vps)
- Ambas claves agregadas a authorized_keys de cada VPS
- sudo NOPASSWD configurado en ambos VPS para usuario livskin
- Conexion verificada y funcional a ambos servidores

### Seguridad resuelta

- Fail2Ban instalado y activo en VPS Operaciones (SSH jail, 3 intentos, ban 2 horas)
- Ya estaba activo en VPS WordPress (3+ semanas uptime)

### Infraestructura nueva instalada

- PostgreSQL 16 desplegado en Docker (container: postgres-analytics)
  - DB: analytics, User: analytics_user
  - Schema creado: tablas leads, crm_stages, opportunities, events
  - DB adicional "metabase" para uso interno de Metabase
  - Conectado a revops_net, sin puertos expuestos

- Metabase desplegado en Docker (container: metabase)
  - Accesible en dash.livskin.site
  - Usa PostgreSQL como DB interna
  - Puerto 3000 solo en localhost, expuesto via Nginx

- Nginx configurado para dash.livskin.site (HTTPS, Cloudflare Origin Cert)
- Registro DNS creado en Cloudflare para dash.livskin.site

### Repo GitHub limpiado y profesionalizado

- Eliminados archivos duplicados (nginx configs en dos lugares)
- Agregados .ssh/, *.ppk, .claude/ a .gitignore
- Estructura final del repo definida y funcional
- Documento de auditoria completa subido

### Auditoria completa realizada

- Ambos VPS auditados en detalle
- Documento docs/system-audit-2026-04-16.md creado
- Plugins WordPress analizados y capacidades de integracion descubiertas

---

## 3. Auditoria resumida de ambos sistemas

### VPS WordPress (46.101.97.246) — Livskin-WP-01

| Item | Detalle |
|------|---------|
| OS | Ubuntu 22.04.5 LTS |
| Hardware | 1 vCPU, 957 MB RAM (47% usado), 25 GB SSD (18%) |
| Stack | Nativo: Nginx + PHP 8.1 FPM + MariaDB 10.6 |
| WordPress | 6.9.4 |
| SSL | Let's Encrypt, expira 2026-06-19 |
| Seguridad | UFW + Fail2Ban + headers + wp-config bloqueado |
| DB | livskin_wp, user: livskin_user, host: localhost |

#### Plugins relevantes para RevOps

| Plugin | Version | Capacidad descubierta |
|--------|---------|----------------------|
| PixelYourSite | 11.2.0.4 | Tracking Meta/FB/Google/GTM/Pinterest/Bing/Reddit. Captura UTMs automaticamente |
| SureForms | 2.7.0 | Formularios con webhook nativo (_srfm_integrations_webhooks). Puede enviar datos directamente a n8n |
| LatePoint | 5.3.2 | Reservas/citas con trigger_webhook en procesos. Puede disparar webhook al crear reserva |
| UpdraftPlus | - | Backups (ultimo: 2026-03-30, hace 17 dias) |
| Complianz GDPR | - | Compliance cookies |
| Elementor | - | Page builder |

### VPS Operaciones (167.172.97.197) — livskin-vps-operations

| Item | Detalle |
|------|---------|
| OS | Ubuntu 22.04 LTS |
| Hardware | 2 vCPU, 3.82 GB RAM (53% usado por Docker), 78 GB SSD (11%) |
| Stack | Docker + Docker Compose |
| SSL | Cloudflare Origin Certificate, Full (Strict) |
| Seguridad | UFW + Fail2Ban + DB no expuestas |

#### Contenedores Docker

| Contenedor | Imagen | RAM | Funcion |
|-----------|--------|-----|---------|
| nginx | nginx:stable | 5 MB | Reverse proxy + TLS |
| n8n | n8nio/n8n v2.14.2 | 267 MB | Automatizacion (sin workflows aun) |
| vtiger | vtigercrm-8.2.0 | 446 MB | CRM (sin configurar pipeline aun) |
| vtiger-db | mariadb:10.6 | 93 MB | DB del CRM (red aislada) |
| postgres-analytics | postgres:16 | 86 MB | Base analitica (schema listo) |
| metabase | metabase/metabase | 1,142 MB | Dashboards (sin dashboards aun) |

#### Redes Docker

- revops_net: nginx, n8n, vtiger, postgres-analytics, metabase (comunicacion entre servicios)
- vtiger_vtiger_internal: vtiger + vtiger-db (DB aislada del CRM)

#### Subdominios (todos HTTPS 200 OK)

- flow.livskin.site → n8n
- crm.livskin.site → Vtiger
- dash.livskin.site → Metabase

---

## 4. Consulta: Como se conectan los dos VPS

### Problema

Los dos VPS son maquinas completamente separadas. No comparten red interna, no comparten base de datos, no se ven entre si.

### Opciones evaluadas

| Opcion | Descripcion | Veredicto |
|--------|-------------|-----------|
| **Webhooks sobre HTTPS** | WordPress hace POST a una URL publica de n8n | **ELEGIDA** — simple, segura, estandar de la industria |
| VPN (WireGuard/Tailscale) | Tunel privado entre VPS | Excesivo para este caso, agrega complejidad |
| DigitalOcean VPC | Red privada del proveedor | Requiere misma region, agrega complejidad |

### Decision: Webhooks sobre HTTPS

Razones:
- Ya tenemos HTTPS funcionando (Cloudflare + Origin Cert)
- SureForms y LatePoint soportan webhooks nativamente
- n8n esta disenado para recibir webhooks
- Es el patron que usan Zapier, HubSpot, Salesforce
- No requiere configuracion adicional de red
- Seguro (cifrado HTTPS via Cloudflare)

### Flujo real decidido

```
Usuario llena formulario en livskin.site
    |
    v
SureForms hace POST a https://flow.livskin.site/webhook/lead
    |
    v (viaja por internet, cifrado HTTPS via Cloudflare)
    |
    v
n8n recibe JSON con datos del formulario
    |
    v
n8n valida, normaliza, deduplica
    |
    v
n8n crea/actualiza Lead en Vtiger via API
    |
    v
n8n (ETL programado) copia datos a PostgreSQL
    |
    v
Metabase muestra dashboards
```

---

## 5. Consulta: Que son las APIs REST y como aplican aqui

### Concepto

Una API REST es una forma estandar de que dos sistemas se hablen por HTTP. En vez de recibir una pagina web (HTML), un sistema recibe datos estructurados (JSON).

### Los 4 verbos

| Verbo | Que hace | Ejemplo en este sistema |
|-------|----------|------------------------|
| GET | Leer datos | n8n pide lista de leads desde Vtiger |
| POST | Crear algo nuevo | n8n crea un lead en Vtiger |
| PUT | Actualizar existente | n8n actualiza telefono de un lead |
| DELETE | Eliminar | n8n elimina un duplicado |

### APIs REST disponibles en el sistema

| Sistema | Tiene API | URL base | Uso principal |
|---------|-----------|----------|---------------|
| Vtiger | Si, nativa | crm.livskin.site/webservice.php | Crear/leer/actualizar leads, contactos, oportunidades |
| WordPress | Si, nativa | livskin.site/wp-json/wp/v2/ | Leer posts, pages (menos relevante) |
| n8n | Si, webhooks | flow.livskin.site/webhook/* | Recibir datos de cualquier fuente |
| Metabase | Si | dash.livskin.site/api/ | Consultar dashboards programaticamente (futuro) |
| PostgreSQL | No directamente | - | Se accede via n8n o Metabase |

### Mapa completo de APIs en el sistema

```
APIs que ENVIAN datos a n8n (webhooks = POST)
=============================================
SureForms ------POST webhook------> n8n
LatePoint ------POST webhook------> n8n
WhatsApp API ---POST webhook------> n8n (futuro)

APIs que n8n CONSUME
====================
n8n ---POST/GET---> Vtiger API       (crear/leer leads)
n8n ---GET--------> Meta Ads API     (leer metricas de campanas, futuro)
n8n ---INSERT-----> PostgreSQL       (escribir datos analiticos)

APIs de CONSULTA
================
Metabase ---SELECT---> PostgreSQL    (leer para dashboards)
```

### Punto clave

No se necesita escribir codigo. n8n tiene nodos visuales para cada API (Vtiger, HTTP Request, PostgreSQL). Se configura arrastrando nodos y poniendo credenciales.

---

## 6. Consideraciones criticas identificadas

### RAM del VPS Operaciones (vigilar)

Metabase consume 1.14 GB solo. Con 53% de RAM usada (2.03 GB de 3.82 GB), queda ~1.7 GB libres. Si se agrega WhatsApp API u otro servicio, upgrade a 8 GB necesario.

### RAM del VPS WordPress (limite)

Solo 957 MB total, 47% en uso. Sin margen para mas software.

### Backups no automatizados (riesgo)

- WordPress: UpdraftPlus manual (ultimo hace 17 dias)
- Operaciones: scripts backup.sh y restore.sh listos, pero sin cron
- Si cae un VPS hoy, se pierde configuracion reciente

### SSL WordPress

Let's Encrypt expira 2026-06-19. Certbot deberia renovar auto, pero verificar.

### n8n completamente vacio

Sin workflows, sin credenciales, sin conexiones. Primer sistema a configurar.

### Vtiger sin configurar

Instalado pero sin: pipeline, campos custom, stages, reglas de negocio.

### Gobierno de datos pendiente

Sin definir: campos minimos por lead, reglas de deduplicacion, naming conventions, stages del pipeline.

### Deuda tecnica en Vtiger

Workaround aplicado en Fase 3: se comento `throw new Exception('Illegal request')` en Request.php para evitar error con reverse proxy. Funciona pero reduce validacion interna. Documentado en docs/fase-3-tls-vtiger.md.

---

## 7. Decision: Proyecto multi-maquina

El usuario trabaja desde dos computadoras. Cada una necesita su propia configuracion local:
- Claves SSH propias (no se comparten entre maquinas)
- Clon del repo desde GitHub
- Los archivos .ppk y .ssh/ estan en .gitignore (nunca suben a GitHub)

Setup para maquina nueva:
1. Clonar repo
2. Generar claves SSH
3. Agregar public keys a ambos VPS via PuTTY
4. Probar conexion

---

## 8. Estructura actual del repo GitHub

```
livskin-revops/
├── docker/
│   ├── metabase/docker-compose.yml
│   ├── n8n/docker-compose.yml
│   ├── nginx/docker-compose.yml
│   ├── postgres/docker-compose.yml
│   └── vtiger/docker-compose.yml
├── nginx/
│   ├── nginx.conf
│   └── sites/
│       ├── crm.conf
│       ├── dash.conf
│       └── n8n.conf
├── scripts/
│   ├── backup.sh
│   └── restore.sh
├── sql/
│   └── schema.sql
├── docs/
│   ├── consultas-y-decisiones.md    (este documento)
│   ├── system-audit-2026-04-16.md
│   ├── fase-2-reverse-proxy-n8n.md
│   └── fase-3-tls-vtiger.md
├── n8n/workflows/                    (vacio, para futuros exports)
├── .env.example
├── .gitignore
└── README.md
```

---

## 9. Orden recomendado de integracion (siguiente fase)

| Paso | Tarea | Dependencia |
|------|-------|-------------|
| 1 | Definir gobierno de datos (campos, stages, naming) | Ninguna |
| 2 | Configurar Vtiger (pipeline, campos, stages) | Paso 1 |
| 3 | Configurar n8n (credenciales Vtiger, primer webhook) | Paso 2 |
| 4 | SureForms → n8n webhook | Paso 3 |
| 5 | n8n → Vtiger (crear/actualizar leads) | Paso 3 |
| 6 | PixelYourSite UTMs en formularios (campos hidden) | Paso 4 |
| 7 | n8n ETL → PostgreSQL | Paso 5 |
| 8 | Metabase dashboards | Paso 7 |
| 9 | LatePoint → n8n (reservas) | Paso 3 |
| 10 | Backups automaticos (cron ambos VPS) | Independiente |
| 11 | WhatsApp API | Cuando flujo base este estable |
| 12 | Meta/FB Ads API → PostgreSQL (metricas de campanas) | Paso 7 |

---

## 10. Ideas pendientes para lluvia de ideas

- Como estructurar los campos hidden en SureForms para capturar UTMs
- Que stages definir en el pipeline de Vtiger
- Que campos minimos debe tener un lead
- Como manejar leads de WhatsApp vs leads de formulario
- Que dashboards crear primero en Metabase
- Como integrar metricas de Meta Ads con datos de conversion de Vtiger
- Naming conventions para campanas, fuentes, medios
- Reglas de deduplicacion (email como clave primaria?)
- Automatizaciones de respuesta (email, WhatsApp)
- Alertas cuando un lead cambia de etapa
