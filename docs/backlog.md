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

### 🟡 Capa de auto-mantenimiento — implementar al cierre de Fase 6
Para que Dario NO dependa de intervenir manualmente en el sistema cuando esté dirigiendo la empresa (target: 3-5 h/mes total incluyendo mantenimiento).

**Componentes a implementar en Fase 6:**
- **Watchtower** (gratis, self-hosted) — monitorea containers y aplica security updates de imágenes Docker automáticamente. Reduce el riesgo de CVEs sin intervención manual.
- **UptimeRobot free tier** (50 monitors gratis) — monitorea cada subdominio público cada 5 min. Si cae algo, email/SMS a Dario.
- **n8n workflows de alertas internas** — vigilan disco, RAM, costos Claude API; alertan vía WhatsApp cuando crucen umbrales (definidos en ADR-0003 § 15.2).
- **Monthly audit auto-ejecutado** — cron job del día 1-5 de cada mes corre audit completo (Lynis + docker state + cert expiry + disk + etc.) y commitea el report a `docs/audits/`.
- **Runbooks operativos completos** — en `docs/runbooks/` documentar procedimientos paso a paso para los 5-10 incidentes más probables (SSL expirado, disco lleno, container crash, API key comprometida, etc.). Así cualquier persona puede resolver sin experticia.

**Objetivo cuantitativo:** reducir mantenimiento a <5h/mes rutinario + incidentes que alerten automáticamente.

**Decisión a futuro (Año 1-2):** según volumen real de incidentes, evaluar Ruta A (tú + Claude Code), Ruta B (fractional DevOps $300-800/mo) o Ruta C (managed services DO Managed Postgres +$15/mo).

**Referencia:** esta decisión fue formalizada tras consulta de Dario el 2026-04-20 sobre "cómo se mantiene esto cuando yo esté dirigiendo la empresa". Documentado en master plan § "Operación post-MVP y mantenimiento".

**Fase sugerida:** Fase 6 (Semana 10) + ajustes post-lanzamiento según data real.  
**Agregado por:** Claude Code · 2026-04-20

---

### 🟢 Workflow CI/CD: agregar `nginx -s reload` tras cambios de nginx.conf/sites
Hoy `docker compose up -d` es idempotente: si nada cambió en el compose file, nginx no reinicia. Pero los archivos `nginx.conf` y `sites/*.conf` están bind-mounted, así que cambios ahí NO disparan restart automático del container. Para que un cambio de config de nginx se aplique, hay que:
- `docker exec nginx-vps3 nginx -t` (validar)
- `docker exec nginx-vps3 nginx -s reload` (reload sin downtime)

**Mejora al workflow:** en el step Deploy, detectar si archivos bajo `infra/docker/nginx-vps3/{nginx.conf,sites/}` cambiaron en el git pull; si sí, ejecutar reload. Alternativamente, siempre intentar reload (idempotente).

**Por ahora no urgente** — cambios de HTML (en `html/prod|staging/`) sí se reflejan automáticamente porque nginx los lee en cada request. Solo configs del server requieren reload.

**Fase sugerida:** cuando hagamos el primer cambio real a nginx.conf o sites/*.conf (probablemente en Fase 2 al agregar el proxy_pass al ERP Flask).  
**Agregado por:** Claude Code · 2026-04-20

---

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

### 🟡 Limpiar `/srv/livskin/` en VPS 3 (carpeta vieja pre-migración)
El 2026-04-20 se migraron los containers de `/srv/livskin/<svc>/` a `/srv/livskin-revops/infra/docker/<svc>/` como parte del setup de CI/CD. La carpeta vieja `/srv/livskin/` (postgres-data, embeddings-service, nginx) quedó como backup temporal.

**Cuándo borrarla:** después de 24-48h de operación estable desde la nueva ubicación (probable: 2026-04-22).  
**Cómo:** SSH a VPS 3 → `sudo rm -rf /srv/livskin/postgres-data /srv/livskin/embeddings-service /srv/livskin/nginx` (preservando `/srv/livskin/` mismo por si se necesita para algo futuro, o borrar todo si ya no tiene uso).  
**Agregado por:** Claude Code · 2026-04-20

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
