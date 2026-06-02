---
title: Fix VPS3 deploy failure (local git divergence)
type: runbook
last_validated: 2026-06-02
trigger: GitHub Actions deploy-vps3.yml falla con "Your local changes would be overwritten by merge"
estimated_time: 5 min
---

# Runbook — Fix deploy VPS3 failure por divergencia git local

> Diagnóstico aplicado el 2026-06-02 tras 15 deploys consecutivos fallidos
> desde 2026-05-24. Root cause: `sudo cp` directos a /srv/livskin-revops/ en
> VPS3 dejaron archivos modificados que bloquean `git pull` del CI/CD.

---

## Síntomas

- GitHub Actions `Deploy to VPS 3 (livskin-vps-erp)` falla repetidamente
- Step "Deploy to VPS 3" exit code != 0
- VPS3 producción funcional (deploys manuales lo mantuvieron al día)
- Email de GitHub notifica fallas

## Diagnóstico

```bash
ssh livskin-erp
cd /srv/livskin-revops
git status --short  # muestra muchos files modificados sin commit
git log --oneline -1  # HEAD atascado en commit antiguo
git fetch origin main
git log --oneline origin/main -1  # remote tiene commits más nuevos
```

Si `git status` muestra files modificados (que también están como nuevos commits en origin/main): **divergencia confirmada**.

## Fix (~5 min)

```bash
# 1. Confirmar ownership de files cp'd con sudo
# Si retention-*.sh u otros files están root-owned, chown primero:
sudo chown -R livskin:livskin /srv/livskin-revops/

# 2. Reset hard a origin/main (los cambios locales YA están en origin/main
#    porque tu workflow es: cp local → commit en repo)
cd /srv/livskin-revops
git fetch origin main
git reset --hard origin/main
git clean -fd  # remueve untracked

# 3. Verificar
git status --short  # debe estar vacío
git log --oneline -1  # debe coincidir con origin/main

# 4. Verificar ERP sigue UP (containers usan imágenes ya buildeadas, no
#    deberían reiniciar):
curl -s -o /dev/null -w "%{http_code}\n" https://erp.livskin.site/login  # 200
```

## Prevención

**NUNCA hacer `sudo cp` a /srv/livskin-revops/ en VPS3 directamente.**

Workflow correcto:
1. Edit local en Windows
2. Commit + push a GitHub
3. CI/CD GitHub Actions hace `git pull` + `docker compose up -d --build` en VPS3
4. Si necesitas validar antes de commit: probar en docker test env primero

Si por alguna razón necesitas patchear directamente VPS3 (ej. emergencia):
- Hacer `docker cp` al container running (afecta solo runtime, no persistente)
- Recordar que próximo deploy lo sobreescribe (el commit en git es la fuente de verdad)
