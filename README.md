# Livskin RevOps Stack

Infraestructura base del proyecto Livskin VPS Operaciones.

## Base actual
- VPS: DigitalOcean
- OS: Ubuntu 22.04 LTS
- Reverse proxy: Nginx
- Contenedores: Docker
- Automatización: n8n
- CRM: Vtiger
- Base analítica: PostgreSQL
- Dashboards: Metabase

## Objetivo
Construir una arquitectura RevOps personal-profesional reproducible, versionada y documentada.


## FASE 2 COMPLETADA

- Nginx reverse proxy funcionando
- n8n desplegado y accesible en flow.livskin.site
- Cloudflare configurado (Flexible)
- Arquitectura protegida (sin exposición directa de servicios)

---

---

# 📦 FASE 3 — TLS + Cloudflare + Vtiger

## 🎯 Objetivo

Exponer Vtiger CRM mediante dominio seguro (https://crm.livskin.site) utilizando:

- Nginx como reverse proxy
- Cloudflare como proxy externo
- Docker como entorno de ejecución

---

## 🔐 Seguridad

### Cloudflare

- Proxy activo (nube naranja)
- SSL mode: Full (Strict)
- tráfico HTTPS obligatorio

---

### TLS

- Certificado Origin generado en Cloudflare
- Instalado en Nginx:

/etc/nginx/certs/livskin-origin.crt  
/etc/nginx/certs/livskin-origin.key  

---

## ⚙️ Nginx

Configuración:

- reverse proxy hacia Vtiger
- redirección HTTP → HTTPS
- headers:

Host  
X-Real-IP  
X-Forwarded-For  
X-Forwarded-Proto  

Archivo:

docker/nginx/sites/crm.conf

---

## 🐳 Vtiger

Desplegado en Docker:

docker/vtiger/docker-compose.yml

---

## 🧠 Problemas encontrados

### 1. Redirección infinita

Causa:

- conflicto de HTTPS entre Cloudflare, Nginx y Apache interno

---

### 2. Error "Illegal request"

Causa:

- validación interna de Vtiger incompatible con reverse proxy

---

## 🔧 Soluciones aplicadas

### Ajuste site_URL

Archivo:

~/apps/vtiger/data/config.inc.php

Cambio:

$site_URL = 'http://crm.livskin.site/';

---

### Workaround validación

Archivo:

~/apps/vtiger/data/includes/http/Request.php

Cambio:

// throw new Exception('Illegal request');

---

### Seguridad Docker

Eliminado:

ports:
  - "8080:80"

Resultado:

- Vtiger solo accesible vía Nginx

---

## ⚠️ Deuda técnica

- workaround temporal en Vtiger
- pendiente:
  - correcta detección HTTPS detrás de proxy
  - eliminar workaround

---

## ✅ Estado final

- https://crm.livskin.site operativo
- login funcional
- navegación funcional
- sin loops de redirección

---

## 🚀 Preparado para FASE 4

- integración n8n ↔ Vtiger
- automatización RevOps
- conexión con PostgreSQL
