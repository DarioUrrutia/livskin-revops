# Backlog del proyecto Livskin

**Propósito:** artefacto vivo para capturar ideas, cambios, dudas y observaciones que no son acción inmediata pero **no deben perderse**.

**Uso:**
- Cualquier de los dos (Dario o Claude Code) agrega entradas cuando surjan ideas
- Al inicio de cada sesión, yo reviso el backlog y te propongo qué retomar
- Al cierre de cada sesión, movemos a "Hecho" o reordenamos prioridades
- Priorización por **impacto al proyecto**, no por orden cronológico

---

## Leyenda

- 🔴 Alta prioridad (bloquea algo o es riesgo activo)
- 🟡 Media prioridad (mejora importante, no bloquea)
- 🟢 Baja prioridad (nice to have)
- 💡 Idea/brainstorm (todavía sin decisión, a discutir)
- ❓ Duda abierta (requiere respuesta de usuaria)
- ✅ Hecho (se mantiene como historial)

---

## Prioritario

<!-- Cosas que hay que hacer pronto -->

### 🟡 Agregar passphrase a `livskin-vps-erp.ppk` al cerrar Fase 2
Durante Fase 1-2 la `.ppk` no tiene passphrase (decisión consciente por fricción de setup). Al terminar Fase 2 (cutover ERP completo), agregarle passphrase y guardar en Bitwarden.

**Cómo:** PuTTYgen → Load → tipear nueva passphrase + confirm → Save private key.  
**Fase sugerida:** cierre de Fase 2 (semana 4)  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Agregar IP de laptop de trabajo de Dario al whitelist Fail2Ban
La IP pública actual (`78.208.67.189`) es solo de la laptop personal en Milán. Cuando Dario conecte desde la laptop de trabajo por primera vez, si Fail2Ban la banea automáticamente, lo arreglamos y agregamos esa IP al `ignoreip` en `/etc/fail2ban/jail.d/ignoreip.local` en los 3 VPS.

**Fase sugerida:** cuando aparezca por primera vez (reactivo)  
**Agregado por:** Claude Code · 2026-04-19

---

### 🔴 Borrar snapshot VPS 3 cuando Fase 1 esté estable
Snapshot `livskin-vps-erp-baseline-post-hardening-2026-04-19` cuesta ~$3/mes si se mantiene permanente. Debe borrarse cuando la Fase 1 esté operativamente estable (típicamente 1-2 semanas post-deploy sin incidentes). Mientras tanto es cobertura por si algo falla y necesitamos rollback al estado pre-Postgres.

**Cuándo borrarlo:** ~2 semanas después de que Postgres + embeddings service estén corriendo sin incidentes (probable fecha: semana del 2026-05-03).  
**Dónde:** DO panel → droplet livskin-vps-erp → Backups & Snapshots → Delete.  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟢 Configurar email para `livskin.site` (MX + SPF + DKIM + DMARC)
Cloudflare alerta sobre falta de MX records. No bloquea nada operativo, pero:
- Sin MX: nadie puede mandar email a info@livskin.site, doctora@livskin.site, etc.
- Sin SPF/DKIM/DMARC: spammers pueden suplantar @livskin.site (afecta deliverability de marketing)

**Decisiones pendientes:**
- ¿Email propio en livskin.site? ¿O solo usan Gmail/Yahoo personales?
- Si sí: ¿qué proveedor? Google Workspace ($6/user/mes), Zoho Mail ($1/user/mes), ProtonMail (más caro), o self-hosted (descartado — dolor de cabeza para PYME)
- Dario confirma si necesita este canal de comunicación formal

**Fase sugerida:** no crítico hasta lanzamiento comercial formal. Si se decide email propio, 30 min de setup.  
**Agregado por:** Claude Code · 2026-04-19

---

### 🟡 Crear Dossier ADR-0019 (tracking architecture) en versión full
Actualmente es stub en el index. Al llegar a Fase 3 debe escribirse completo. Incluye server-side tracking, eventos, consent, match quality targets.

**Referencia:** docs/decisiones/README.md línea 0019  
**Fase sugerida:** Fase 3 (Semana 5)  
**Agregado por:** Claude Code · 2026-04-18

---

### ❓ Confirmar nombre del repo GitHub del ERP Livskin
La usuaria mencionó que el ERP tiene su propio repo GitHub. Necesario al llegar a Fase 2 para clonarlo en `erp/` local.

**Referencia:** ADR-0023 (ERP refactor)  
**Acción:** preguntar a Dario en próxima sesión  
**Agregado por:** Claude Code · 2026-04-18

---

### 🟡 Definir las 5-10 FAQs típicas de pacientes para Layer 1 del cerebro
Para poblar `clinic_knowledge` con las preguntas que más hacen los pacientes + respuesta autoritativa validada por la doctora.

**Referencia:** ADR-0001 sección 7.1  
**Fase sugerida:** Fase 2 (Semana 3-4)  
**Necesita input de:** la doctora  
**Agregado por:** Claude Code · 2026-04-18

---

## Mediano plazo

### 🟡 Plugin de WordPress para tracking server-side
Evaluar si hay plugin WP open-source que nos ayude con UTM persistence + server-side event forwarding, o si construimos script custom mínimo.

**Referencia:** ADR-0021 (UTMs persistence)  
**Fase sugerida:** Fase 3  
**Agregado por:** Claude Code · 2026-04-18

---

### 🟢 Explorar Dataview plugin de Obsidian para dashboards de proyecto
Dataview permite escribir queries SQL-like sobre frontmatter YAML de los .md. Podríamos generar "estado actual de todos los ADRs" en una tabla viva dentro de Obsidian.

**Fase sugerida:** Fase 0-1 (cuando Obsidian esté instalado)  
**Agregado por:** Claude Code · 2026-04-18

---

## Ideas (brainstorm, sin decisión aún)

### 💡 Integrar Pipedream o similar como redundancia de n8n
Si n8n cae, Pipedream podría actuar como failover para webhooks críticos (form submit). No urgente pero vale la pena evaluar.

**Agregado por:** Claude Code · 2026-04-18

---

### 💡 Caso de estudio público para LinkedIn
Al terminar Fase 6 (mes 2-3 de operación estable), publicar case study técnico: "Cómo construí un sistema RevOps multi-agente en 10 semanas solo con Claude Code". Material excelente para portfolio RevOps.

**Agregado por:** Claude Code · 2026-04-18

---

## Dudas abiertas

### ❓ ¿Livskin emite comprobantes electrónicos a SUNAT hoy?
Si ya factura electrónicamente, necesitamos integración con PSE (Nubefact, Efact, etc.). Si no, decisión de negocio diferida.

**Trigger para responder:** cuando Dario decida estrategia fiscal  
**Relacionado:** ADR-0099 (SUNAT — diferido)  
**Agregado por:** Claude Code · 2026-04-18

---

### ❓ ¿La clínica imprime recibos físicos a pacientes?
Condiciona si necesitamos módulo PDF/impresión en ERP.

**Relacionado:** ADR-0103 (PDFs — diferido)  
**Agregado por:** Claude Code · 2026-04-18

---

## Hecho (historial)

<!-- Los items completados se mueven aquí para mantener historial. No se borran. -->

### ✅ Fase 0 — Repo reorganizado + 3 dossiers + master plan
Completada 2026-04-18. Ver session log correspondiente.

### ✅ ADR-0005 simplificada a "n8n único orquestador"
Originalmente aprobada como híbrido; revisada por Dario en misma sesión. Agent SDK diferido.
2026-04-18.

### ✅ Obsidian integrado al plan como capa humana del segundo cerebro
Dario propuso, se aprobó, se actualizó ADR-0001 con sección 9.2.
2026-04-18.

### ✅ VPS 3 provisionado y hardened
`livskin-vps-erp` @ 139.59.214.7 (VPC 10.114.0.4). Ubuntu 22.04.5, Docker 29.4.0, swap 2GB, UFW+Fail2Ban+unattended-upgrades activos. Lynis score 65/100. VPC connectivity a VPS 1 y 2 verificada (<2ms).
2026-04-19. Ver `docs/sesiones/2026-04-19-fase1-vps3-creado.md`.

### ✅ Whitelist Fail2Ban con ignoreip
Tras incidente de auto-ban en instalación de UFW: whitelist permanente creada en `/etc/fail2ban/jail.d/ignoreip.local` con 127.0.0.1/8, ::1, 10.114.0.0/20 (VPC), 78.208.67.189 (Dario Milan). 2026-04-19.

---

## Cómo agregar una entrada nueva

Copia esta plantilla:

```markdown
### <icono> <título>
<Descripción breve — qué, por qué, qué falta>

**Referencia:** ADR-XXXX o doc relevante  
**Fase sugerida:** Fase N  
**Necesita input de:** <persona o "ninguno">  
**Agregado por:** <Dario | Claude Code> · YYYY-MM-DD
```

Y ubícala en la sección correcta según prioridad.
