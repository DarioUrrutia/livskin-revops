# 📦 FASE 3 — TLS + Cloudflare + Vtiger

## 🎯 Objetivo

Exponer Vtiger CRM mediante dominio seguro (`https://crm.livskin.site`) usando:

- Nginx como reverse proxy
- Cloudflare como proxy externo (Full Strict)
- Docker como entorno de ejecución

---

## 🌐 Arquitectura final

Cliente → Cloudflare → Nginx (Docker) → Vtiger (Docker)

---

## 🔐 TLS

- Cloudflare configurado en modo:
  
  Full (Strict)

- Certificado origin instalado en Nginx:

  /etc/nginx/certs/livskin-origin.crt  
  /etc/nginx/certs/livskin-origin.key

---

## ⚙️ Nginx

### Archivo: `crm.conf`

Ubicación:

docker/nginx/sites/crm.conf

Configuración clave:

- Redirección HTTP → HTTPS
- Proxy interno a contenedor `vtiger`
- Headers necesarios:

Host  
X-Real-IP  
X-Forwarded-For  
X-Forwarded-Proto  

---

## 🧠 Problema encontrado

### ❌ Redirección infinita (ERR_TOO_MANY_REDIRECTS)

Causa:

- Vtiger no detecta correctamente HTTPS detrás del proxy
- conflicto entre:
  - Cloudflare (HTTPS)
  - Nginx (HTTPS)
  - Apache interno (HTTP)

---

## 🔧 Solución aplicada

### 1. Ajuste de `site_URL`

Archivo:

~/apps/vtiger/data/config.inc.php

Cambio:

$site_URL = 'http://crm.livskin.site/';

---

### 2. Workaround “Illegal request”

Archivo modificado:

~/apps/vtiger/data/includes/http/Request.php

Cambio:

// throw new Exception('Illegal request');

Motivo:

- evitar validación estricta incompatible con reverse proxy

---

## ⚠️ Nota (deuda técnica)

Este workaround:

- NO afecta integraciones (n8n, API, etc.)
- PERO reduce validación interna de Vtiger

Pendiente futuro:

- resolver detección correcta de HTTPS detrás de proxy

---

## 🐳 Docker — Vtiger

Archivo:

docker/vtiger/docker-compose.yml

### Seguridad aplicada:

Se eliminó:

ports:
  - "8080:80"

Resultado:

- Vtiger NO expuesto públicamente
- acceso SOLO vía Nginx

---

## 🔐 Seguridad final

- Firewall activo (22, 80, 443)
- Cloudflare activo
- acceso solo por dominio
- backend aislado

---

## ✅ Estado final

- https://crm.livskin.site → operativo
- login funcional
- navegación funcional
- sin redirecciones infinitas

---

## 🚀 Preparado para siguiente fase

El sistema está listo para:

- integración con n8n
- automatizaciones RevOps
- conexión con PostgreSQL (analytics)
- dashboards (Metabase)
