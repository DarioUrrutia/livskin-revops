# `_legacy/` — Docker compose files deprecated en período de gracia

> **Estado:** deprecated — preservados en período de gracia hasta validación final.
> **Acción futura:** eliminar con `rm -rf infra/docker/_legacy/` en una sesión separada (~2-3 sesiones después de mover aquí, una vez validado que nada los usa).

---

## ¿Qué hay aquí?

5 folders con `docker-compose.yml` originales de la **Fase 1** (pre-Bloque 0 v2). Fueron **superseded** por equivalentes en `infra/docker/vps2-ops/<service>/` durante el Bloque 0 v2 (sesión 2026-04-26):

| Path actual `_legacy/` | Reemplazado por |
|---|---|
| `_legacy/n8n/docker-compose.yml` | `infra/docker/vps2-ops/n8n/docker-compose.yml` (más completo, con env vars) |
| `_legacy/metabase/docker-compose.yml` | `infra/docker/vps2-ops/metabase/docker-compose.yml` |
| `_legacy/vtiger/docker-compose.yml` | `infra/docker/vps2-ops/vtiger/docker-compose.yml` |
| `_legacy/nginx/docker-compose.yml` | `infra/docker/vps2-ops/nginx/docker-compose.yml` (con conf/ + sites/) |
| `_legacy/postgres/docker-compose.yml` | `infra/docker/vps2-ops/postgres-analytics/docker-compose.yml` |

## ¿Por qué `_legacy/` y no `rm -rf` directo?

**Período de gracia.** Antes del Bloque 0 v2, los containers en VPS 2 corrían desde `/home/livskin/apps/` (paths legacy NO en repo) — no desde el repo. La migración (`migrate-from-home.sh`) está pendiente. Hasta que esa migración se ejecute y se valide, **mantenemos los compose files originales accesibles** por si algún script desconocido los referencia.

Mover (no borrar) preserva:
- Historia git (`git log --follow`)
- Capacidad de rollback rápido (`git mv` inverso)
- Visibilidad en grep si algo los referencia

## ¿Cuándo se eliminan?

**Trigger para `rm -rf`:**
1. Migración VPS 2 ejecutada (`migrate-from-home.sh`) — los containers corren desde paths del repo (`infra/docker/vps2-ops/<service>/`)
2. 1-2 semanas sin que aparezca ningún issue ni referencia a paths `_legacy/`
3. Sesión dedicada de cleanup definitivo (no incluir en feature work)

## ¿Cómo verifico que ningún proceso los usa?

```bash
# Grep en repo (debería retornar 0 matches)
grep -rE 'infra/docker/_legacy/' .github/ docs/ infra/ 2>/dev/null

# Grep en VPS 2 (verifica que ningún workflow apunta a _legacy/)
ssh livskin-ops 'grep -rE "infra/docker/_legacy/" /srv/livskin-revops/'
```

Si ambos retornan 0 matches y migrate-from-home.sh ya fue ejecutado, safe to delete.

## Recovery rápido (si algo se rompe en producción)

```bash
git mv infra/docker/_legacy/n8n infra/docker/n8n
# repetir para los otros 4 folders
git commit -m "Revert: restore docker-compose legacy paths"
```

Tiempo de recovery: <2 minutos.

---

**Generado:** Sesión 2026-04-29 (audit organización + cleanup) — ver session log.
