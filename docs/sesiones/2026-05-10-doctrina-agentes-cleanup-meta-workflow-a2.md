---
fecha: 2026-05-10
duracion: ~10h (sesión muy larga)
modo: PROYECTO (#12)
participantes: Dario + Claude Code
fase: cleanup Meta + Workflow A2 + doctrina #14
estado: 4 commits mergeados a main + 11 updates en cascada de doctrina
---

# Sesión 2026-05-10 — Cleanup Meta + Workflow A2 + Doctrina #14

## Resumen ejecutivo

Sesión maratónica de ~10h dividida en 4 bloques:

1. **Audit + cleanup Meta Business** (~3h): 15 screenshots auditados, 3 BMs detectados, 4 OAuth integrations eliminadas (Manychat + ReplyRush + agent n8n + n8n agent), Domain Verification livskin.site + www.livskin.site via Cloudflare DNS, dominio agregado al perfil del BM Livskin Perú (potencial unblocker shadow ban)

2. **WhatsApp Cloud API setup parcial** (~2h): App "Livskin Integraciones" creada con producto WhatsApp, test number `+1 555-191-3740` activado, OAuth flow + activeVersionId fix, intento verify número doctora `+51947741117` bloqueado por restricción Meta. Token v4 revocado al final.

3. **Workflow A2 sync ERP→Vtiger bidireccional** (~3h): ADR-0036 escrito, picklist Vtiger leadstatus cleanup (11 legacy → 6 español: Nuevo/Contactado/Agendado/Asistió/Cliente/Perdido), workflow A1 actualizado leadstatus 'New'→'Nuevo', endpoint ERP `/api/internal/leads/pending-vtiger-sync` con 17 tests pytest, workflow n8n A2 importado + activeVersionId fix + smoke E2E real exitoso (Vtiger LEA68 leadstatus Nuevo→Cliente). **Cierre del loop bidireccional ERP↔Vtiger.**

4. **Doctrina #14 + auditoría exhaustiva del proyecto** (~2h): articulación de Principio Operativo #14 nuevo (sesión estratégica de agentes IA dedicada post-backbone), 5 agentes Explore auditaron en paralelo todo el repo, detectaron 2 contradicciones críticas + 6 menores + 8 gaps + 11 archivos a actualizar. Updates en cascada ejecutados.

## Lo construido / actualizado

### Workflow A2 sync ERP→Vtiger (cierre bidireccional)

**ADR-0036** — Workflow [A2] sync ERP→Vtiger (cron pull)
- 4 opciones consideradas, decisión Opción A (cron pull alineado con B3 patrón)
- Latencia 2-5 min aceptable para use case

**Picklist Vtiger leadstatus cleanup (Opción A replace estricto)**:
- 11 valores legacy default eliminados (Hot, Cold, Warm, Qualified, Junk Lead, Lost Lead, etc.)
- 6 valores nuevos en español agregados: Nuevo (305), Contactado (306), Agendado (307), Asistió (308), Cliente (309), Perdido (310)
- Permisos asignados a 5 roles (H1-H5)
- Pre-flight: 0 leads activos (los 67 son smoke tests deleted), 0 FK, 0 workflows en Leads, 0 references — riesgo cero
- Backups transactional en `docs/audits/vtiger-leadstatus-cleanup-2026-05-10/`

**Endpoint ERP** `GET /api/internal/leads/pending-vtiger-sync`:
- Auth `X-Internal-Token`
- Cursor int (audit_log.id)
- Filtros: `appointment.marked_attended` + `appointment.marked_no_show` + `Lead.vtiger_id IS NOT NULL`
- 17 tests pytest cubriendo auth, action filter, vtiger_id filter, cursor, limit, validation, schema response

**Workflow n8n [A2]**:
- 5 nodes: cron 2min + fetch ERP + IF has_items + process+update Vtiger + persist cursor
- Importado via CLI + active=1 + activeVersionId=versionId fix
- Smoke E2E exitoso: latencia ~2 min cron + ~3 sec API calls

**2 audit events nuevos** (categoría tracking.* nueva):
- `tracking.vtiger_leadstatus_synced` (success)
- `tracking.vtiger_leadstatus_sync_failed` (error)

**Total eventos canónicos**: 56 → 60.

### Cleanup ejecutado Meta Business

**Eliminados**:
- App "Claude Audit App" (residual del 2026-04-27)
- App "agent n8n" (residual)
- System User "Claude Audit" — neutralizado (0 access + tokens revoked)
- Pixel legacy "Livksin Pixel" (`670708374433840`) desconectado de cuenta publicitaria
- 4 OAuth integrations: Manychat + ReplyRush + agent n8n + n8n agent

**Setup nuevo**:
- App Meta "Livskin Integraciones" creada (App ID `807721865486018`)
- Producto WhatsApp activado
- Test number Cloud API `+1 555-191-3740` (CONNECTED, GREEN, TIER_250)
- Domain Verification livskin.site + www.livskin.site via Cloudflare DNS TXT records
- Dominio agregado al perfil del BM "Livskin Perú" (potencial unblocker shadow ban — re-revisión Meta 24-48h)

**Pendientes diferidos** (requieren Marketing API token post-Business Verification):
- Eliminar 7 WABAs Livskin vacías (UI Meta no permite)
- Eliminar BM "Livskin Perú Comercial" (bloqueado por residuales SU + pixel + apps fantasma)

### Doctrina #14 articulada — Sesión estratégica agentes IA dedicada

**Principio Operativo #14** nuevo en CLAUDE.md:
- Sesión estratégica de agentes IA = bloque DEDICADO post-backbone determinístico cerrado
- Duración: 4-8h totales divisibles en 1-3 sesiones según necesidad
- Excepción permitida: Brand Orchestrator V0 BOOTSTRAP (discrecional, scope acotado: solo briefs + copy, monolítico, output revisable antes publicar)
- Conversation Agent IA NO bootstrap (mantener rule-based hasta volumen >100 conv/día sostenido 7+ días)
- Interludio estratégico (brand voice + arquetipos + posicionamiento + plan estratégico) ES PARTE del backbone (Fase 4A.6), no input externo a sesión de agentes

### Memorias 🔥 nuevas (2)

- `feedback_sesion_estrategica_agentes_dedicada.md` — doctrina #14 detallada con triggers + outputs + scope V0 vs V1
- `project_interludio_estrategico_es_backbone.md` — clarifica interludio como base conceptual del backbone

### Memorias actualizadas (3)

- `MEMORY.md` — sección 🔥 CRÍTICAS con 2 doctrinas nuevas
- `project_agent_org_design.md` — V0 BOOTSTRAP vs V1 POST-SESIÓN tabla explícita + timing pre-Fase 4B
- `project_roadmap.md` — Bridge cerrado 2026-05-08 + Fase 4 reorganizada con 4A.5 email + 4A.6 interludio + sesión estratégica
- `project_infra_security_agent.md` — clarificación reapertura (decisión arquitectónica, no esperar escalamiento) + timing Fase 7

### ADRs actualizados

- **ADR-0034** Conversation Agent IA Foundation: status 💤 Diferida → 🔄 **Supersedida** por doctrina #14. Linaje completo: ✅ 2026-05-02 → 💤 2026-05-03 → 🔄 2026-05-10. Será reemplazada por ADR-0037 cuando se construya rule-based formal en sesión estratégica.
- **ADR-0001** Segundo cerebro § 9.1: tabla consumidores brain refleja V0/V1 + scripts vs agentes plenos
- **ADR-0036** (nuevo) — Workflow A2 sync ERP→Vtiger
- **README.md decisiones**: 22 ADRs físicos (era 20), reservados 0037-0039 agregados

### Master plan v3.2 — secciones reescritas

- § 10.1 — scope agentes V1 con tabla actualizada
- § 11.5b — interludio es PARTE del backbone (Fase 4A.6)
- § 11.5c — Bridge Episode marcado ✅ EJECUTADO Y CERRADO + Bootstrap abierto hasta 2da campaña
- § 11.6 — Fase 4A expandida con 6 sub-fases + sesión estratégica + excepciones
- § 11.7 — Fase 5 reescrita como scripts con LLM ocasional, NO agentes plenos
- § 19 — entrada v3.2 changelog

### N8N workflows companions creados

- `infra/n8n/workflows/A-acquisition/a2-sync-erp-to-vtiger-leadstatus.md`
- `infra/n8n/workflows/E-etl/e2-erp-ventas-to-analytics.md`

### Doctrinas adicionales articuladas

- `feedback_no_campana_sin_whatsapp_automatico.md` (articulada esta sesión 2026-05-10): no campaña paga sin bot WhatsApp automático funcional. Speed-to-lead <60s + doctora no 24/7 = bot mandatorio. SUPERSEDE planes futuros tipo Bridge Episode original.
- `feedback_congruencia_nombres_cross_system.md` (articulada esta sesión): nombres congruentes 1:1 entre sistemas (ERP `cliente` ↔ Vtiger `Cliente`), no traducir a otro idioma, extender el sistema target con valor canónico si falta.

## Auditoría exhaustiva del proyecto (5 agentes Explore en paralelo)

Dario pidió revisión exhaustiva antes de plasmar la doctrina nueva. Resultado:

| Dimensión | Estado |
|---|---|
| Coherencia general con doctrina nueva | 88-92% |
| Contradicciones críticas | 2 (resolubles con clarificación) |
| Contradicciones menores | 6 |
| Gaps documentales | 8 |
| Archivos a actualizar | 11 |
| Memorias nuevas a crear | 3 (las 2 nuevas + 1 que se mantuvo en planeación) |
| ADRs reservados a agregar | 3 (0037, 0038, 0039) |

**Auto-correcciones de mi propio reporte preliminar**:
- Bridge Episode resultó con **6 leads** (no 0 como dije)
- Bridge Episode cerró **2026-05-08** (no 2026-05-09)
- Bootstrap principio #13 sigue **ABIERTO hasta 2da campaña** (decisión Dario 2026-05-08)
- 14 INS + 6 R doctrina capturados sin aplicar (esperan 2da campaña)

## Bugs encontrados y arreglados

1. **A1 webhookId vacío post-SQL update ayer** → causaba "Cannot read properties of undefined (reading 'endsWith')" al activar workflow. Fix: borrar A1 completo + re-import via CLI con UUID webhookId nuevo.
2. **A2 sin activeVersionId post-import CLI** → n8n no procesaba workflow aunque active=1. Fix: SQL UPDATE `activeVersionId = versionId`.
3. **n8n CLI execute en modo standalone fallaba** porque container ya tenía task broker en port 5679. Workaround: activación + restart en lugar de execute manual.
4. **Token Meta v4 visible en screenshots** del dashboard (problema seguridad) → revocado al final de sesión + valor limpiado de `keys/.env.integrations`.

## Estado al cierre

| Sistema | Estado |
|---|---|
| ERP `erp.livskin.site` | ✅ Funcionando, módulo Agenda + endpoint A2 sync deployed |
| Vtiger picklist leadstatus | ✅ 6 valores en español congruentes con ERP |
| Workflow A1 (form→Vtiger) | ✅ leadstatus='Nuevo' (era 'New') |
| Workflow A2 (ERP→Vtiger) | ✅ ACTIVO en producción, smoke E2E exitoso |
| Workflow B3 (Vtiger→ERP) | ✅ Sin cambios, sigue corriendo |
| Bidireccional ERP↔Vtiger | ✅ CERRADO COMPLETAMENTE |
| Meta App "Livskin Integraciones" | ✅ Creada, test number activo |
| WhatsApp Cloud API +51947741117 | 🔴 Bloqueado por restricción Meta (24-48h re-revisión post Domain Verif) |
| Tests ERP | ✅ 357 tests, coverage 75%+ |
| Audit events | ✅ 60 canónicos en 10 categorías |
| ADRs físicos | ✅ 22 (0001-0036) |
| Master plan | ✅ v3.2 actualizada |

## Commits del día (4)

```
9bb6f14 fix(n8n): A1 webhookId UUID format + smoke E2E A2 exitoso
9599081 feat(erp+n8n): ADR-0036 Workflow [A2] sync ERP -> Vtiger (cierra bidireccional)
e8cd4df docs(meta): audit Meta Business completo + cleanup ejecutado + Domain Verification
ce2f978 fix(vtiger): cleanup leadstatus picklist + workflow A1 + ERP sync mapping
```

Pendiente commitear (esta sesión post-doctrina):
- 11 archivos updates en cascada (CLAUDE.md, master plan, memorias, ADRs, .md companions, backlog, session log)

## Próxima sesión propuesta

**Sprint A — Email institucional + verificación BM Meta** (~1-2 días, baja intensidad):
- Zoho Mail Free + buzón info@livskin.site (~30 min)
- DNS records Cloudflare via API (yo)
- IMAP setup Gmail Android
- Watchpoint: restricción Meta BM levantada (24-48h pasivo)
- Submit Business Verification cuando lleguen docs RUC

O **Sprint B — Diseño Fase 4A.3 bot-broker** (3-4h doc-only):
- Dario decide si arranca o espera unblock Meta

## Memoria efímera de la sesión

Este session log es el record completo. Una vez archivado, conceptos durables ya están en:
- CLAUDE.md (principios #11, #12, #13, #14)
- Master plan v3.2
- Memorias 🔥 CRÍTICAS (2 nuevas + 4 actualizadas)
- ADRs (0034 supersedida + 0036 nuevo + 0001 actualizada)
- Backlog actualizado
- Documentos n8n companions
