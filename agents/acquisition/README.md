# Acquisition Engine

**Rol:** gestión autónoma de campañas publicitarias en Meta Ads. No solo lanza ads — los optimiza continuamente.

**Fase de construcción:** Fase 5 (Semana 8)

## Objetivo

- Convertir creativos aprobados del domingo → ads el lunes
- Testing matrix: S/.15-20/día por creativo × 3 días
- Escalado automático de ganadores (CPL bajo)
- Pausa automática de perdedores
- Retargeting sobre visitantes WP

## Tools

- `meta_ads_create_campaign(objective, budget)` → crea estructura
- `meta_ads_create_adset(campaign_id, audience, budget)` → audiencia
- `meta_ads_create_ad(adset_id, creative_id)` → ad específico
- `meta_ads_upload_creative(file, format)` → sube imagen/video
- `meta_ads_update_budget(adset_id, new_budget)` → escalar
- `meta_ads_pause(ad_id)` → pausar
- `meta_ads_get_performance(ad_id, date_range)` → leer métricas
- `brain_save_creative_performance(creative_id, metrics)` → update L5

## Matriz de testing

Cada domingo se aprueban 12 briefs. El lunes:
1. Se lanzan 12 ads en paralelo
2. Budget S/.15-20/día × 3 días por ad = ~S/.60/ad
3. Budget total semana inicial: ~S/.720
4. Al día 3 se evalúa CPL por ad

**Reglas de escalamiento:**
- CPL < S/.50 → escalar 50% budget
- CPL S/.50-80 → mantener
- CPL > S/.80 → pausar (ahorra budget para ganadores)
- Top 2 ganadores pasan a "evergreen" con budget estable

**Reglas de retargeting:**
- Visitantes WP que no convirtieron → audiencia custom
- Lead completo pero no cita → mensaje WA específico (no ad)
- Ex-cliente 45+ días sin volver → reactivación via agent, no ad

## Dashboard

- Decisiones automáticas ejecutadas (transparencia)
- CPL por creativo
- Budget utilization
- Top/bottom performers semana

## Intervención humana

10 minutos lunes revisando dashboard:
- Aprobar decisiones de alto impacto (pausar ad que costó >S/.200)
- Override manual si hay contexto externo (ej: evento local)

## Referencias

- ADR-0031 — Acquisition Engine
- ADR-0019 — Tracking architecture
- ADR-0020 — Modelo atribución

## Estado actual

⏳ Pendiente — construcción en Fase 5 (Semana 8).
