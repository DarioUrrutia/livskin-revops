# Meta Business Audit + Cleanup — 2026-05-09

**Sesión:** modo PROYECTO + coordinación pre-Fase 4A.2
**Operador:** Dario (UI clicks) + Claude (análisis + plan)
**Duración:** ~2h
**Trigger:** prerequisito para activar Fase 4A.2 WhatsApp Cloud API + dejar el sistema Meta limpio antes de invertir más capital publicitario.

---

## 🎯 Resumen ejecutivo

Auditados **15 puntos del ecosistema Meta Business**: BMs, cuenta publicitaria, pixels/datasets, apps, system users, página FB, cuenta IG. Detectados:

- 🚨 **3 Business Managers** (no 1 como asumía CLAUDE.md), 2 bajo Dario y 1 con la doctora
- 🚨 **Página FB + cuenta IG** viven en BM ajeno ("D'Claudia") creado años atrás desde una cuenta perdida — puzzle de ownership pendiente con la doctora
- 🚨 **Doble pixel** confirmado (activo + legacy) en cuenta publicitaria — fuente del double-fire detectado en audit 2026-04-26
- 🟢 **Residuales del intento Marketing API 2026-04-27** identificados y limpiados (1 app + 1 SU + 1 access)
- 🟢 **App residual de tests viejos** ("agent n8n") eliminada
- 🟡 **Eliminación BM "Livskin Perú Comercial"** iniciada pero bloqueada por residuales SU+pixel — diferida

---

## 📋 Inventario final del ecosistema Meta

### Business Managers

| BM | Status | Contenido | Decisión |
|---|---|---|---|
| **Livskin Perú** | ✅ Activo, sano | 1 cuenta publicitaria + 1 dataset activo + 1 pixel legacy + 1 SU CAPI | Keep como BM principal |
| **Livskin Perú Comercial** | 🟡 Vacío en assets relevantes | Solo "fantasmas" residuales bloqueando delete | DELETE diferido (no urgente) |
| **D'Claudia** | 🟡 Hosting Página FB + cuenta IG | Creado por cuenta vieja perdida; doctora con acceso desconocido | Coordinar con doctora |

### Cuenta publicitaria

| ID | Status | Acceso | Activos conectados |
|---|---|---|---|
| `2885433191763149` | ✅ Activa | Dario (Control total) — Claude Audit removido | Dataset Livksin Pixel 2026 + Pixel Livksin Pixel 2026 (legacy desconectado 2026-05-09) |

### Pixels / Datasets (en BM Livskin Perú)

| Asset | ID | Tipo | Status | Decisión |
|---|---|---|---|---|
| **Livksin Pixel 2026** | `4410809639201712` | Dataset (Meta Pixel + CAPI) | ✅ Recibiendo eventos | Keep — pixel productivo |
| **WhatsApp Marketing Message Event Sharing** | — | Dataset placeholder | Sin datos | Activar en Fase 4A.2 cuando se conecte WA Cloud API |
| **Livksin Pixel** (legacy) | `670708374433840` | Pixel legacy | 🔴 Sin eventos, sin datos conectados | Desconectado de cuenta publicitaria 2026-05-09; eliminación final no soportada por Meta UI |

> **Nota typo**: ambos pixels tienen "Livksin" (no "Livskin") en el nombre — typo del proyecto original, no urgente, no afecta funcionalidad.

### Apps Meta for Developers

| App | ID | Status pre-audit | Status post-cleanup |
|---|---|---|---|
| **Claude Audit App** | `941702218481777` | Residual del 2026-04-27 | ✅ ELIMINADA 2026-05-09 |
| **agent n8n** | `2261551344333617` | Test app antigua para Marketing API + n8n (sin uso productivo) | ✅ ELIMINADA 2026-05-09 |
| **Conversions API Application** | (sistema Meta interno) | App de sistema, NO custom | Keep — usada por el SU "Conversions API System User" para el flow CAPI vía n8n workflow [G3] |

### System Users (en BM Livskin Perú)

| SU | ID | Tipo | Status post-cleanup |
|---|---|---|---|
| **Claude Audit** | `61560721390798` | Residual 2026-04-27 | ✅ NEUTRALIZADO 2026-05-09 (0 activos + 0 tokens). Eliminación final NO soportada por Meta UI — zombie inofensivo |
| **Conversions API System User** | `61579475681790` | Legítimo — emite events CAPI | Keep |

### Página Facebook + Cuenta Instagram

| Asset | Datos | BM hosting | Riesgo |
|---|---|---|---|
| **Livskin - Centro Estético Cusco** (FB Page) | 157 seguidores · slug `LivskinCentroEsteticoCusco` · ID `525464061130920` | D'Claudia (cuenta vieja) | 🟡 Cadena de permisos frágil |
| **`@livskin_medicinaestetica_cusco`** (IG Account) | 56 seguidores · NUEVO descubrimiento (no estaba documentado) | Conectada via FB Page | 🟡 Mismo riesgo que la página |

---

## 🧹 Cleanup ejecutado 2026-05-09

| # | Acción | Resultado |
|---|---|---|
| 1 | Eliminar App "Claude Audit App" (ID `941702218481777`) | ✅ Confirmado en developers.facebook.com/apps/ |
| 2 | Eliminar App "agent n8n" (ID `2261551344333617`) | ✅ Lista quedó vacía ("Aún no hay apps") |
| 3 | Revocar acceso de SU "Claude Audit" a 3 activos (cuenta pub + pixel + dataset) | ✅ "No hay activos asignados" |
| 4 | Revocar tokens de SU "Claude Audit" | ✅ "Se revocaron correctamente todos los tokens" |
| 5 | Desconectar Pixel legacy "Livksin Pixel" (`670708374433840`) de cuenta publicitaria | ✅ Cuenta pub pasó de 3 → 2 activos conectados |
| 6 | Iniciar eliminación BM "Livskin Perú Comercial" | 🟡 Bloqueado: Meta lista 3 dependencias (SU residual + pixel + app conectada) — diferido a otra sesión |

### Limitaciones de Meta UI descubiertas

- **System Users no eliminables desde UI** una vez creados (solo via Marketing API). Workaround: revocar todos los activos + revocar tokens = SU zombie inofensivo.
- **Pixels no archivables/eliminables desde UI**. Workaround: desconectar de assets que los consumen (cuenta publicitaria) = pixel sin tráfico nuevo.
- **BM con dependencias residuales no eliminable** sin limpiar todas (incluyendo las que UI no permite eliminar). Workaround: mantener BM "Comercial" como contenedor vacío harmless.

---

## 🚨 Hallazgos críticos pendientes — coordinación con doctora

### Puzzle de ownership Página + BM D'Claudia

```
Cuenta vieja Dario (perdida hace años)
   ├── Creó BM "D'Claudia"
   ├── Creó Página "Livskin - Centro Estético Cusco"
   └── Asignó acceso a la doctora (rol = ?)
           └── Doctora asignó acceso a Dario actual (rol = ?)
```

**Lo que NO sabemos hoy**:
- ¿Quedó algún Admin con Control Total activo? (la cuenta vieja podría seguir siendo el Owner técnico)
- ¿Doctora tiene rol "Administrador" del BM D'Claudia o solo "Empleado"?
- ¿Doctora tiene "Control Total" de la página o solo acceso a tareas?

**Lo que está en riesgo si nadie tiene Control Total**:
- No se puede vincular página a BM "Livskin Perú" (necesario para click-to-WhatsApp ads)
- Si Meta audita ownership o cuenta vieja se desactiva, página podría perderse
- Cadena de permisos frágil para crecer publicidad

### Pregunta exacta para doctora

> "Hola doctora, una consulta rápida que te toma 30 segundos:
>
> En el Meta Business Manager **'D'Claudia'** (el que creé yo hace años con mi cuenta vieja y al que después te di acceso), **¿qué rol tenés vos ahí? ¿Administrador o Empleado?**
>
> Para verificarlo: entrá a https://business.facebook.com/settings/info → arriba seleccioná D'Claudia si no aparece → en sidebar izquierdo 'Personas' → buscás tu nombre → al lado dice 'Administrador' o 'Empleado'.
>
> Lo necesito para resolver un tema técnico del setup publicitario antes de la próxima campaña."

### Decisión condicional según respuesta

| Respuesta doctora | Plan |
|---|---|
| **"Administrador"** | Doctora promueve a Dario a Admin → Dario hace Partner setup BM Livskin Perú ↔ D'Claudia → click-to-WhatsApp ads habilitados ✅ |
| **"Empleado"** | Plan B: crear página nueva en BM Livskin Perú (perdés 157 seguidores, ganás control 100%) — decisión a tomar con datos en frío |
| **"No tengo idea, mirá vos"** | Sesión conjunta de 30 min con la doctora para revisar permisos juntos |

---

## 📞 Coordinación pendiente con doctora — combo único

Cuando coordines con la doctora aprovechá el contacto para resolver 2 cosas simultáneas:

1. **Pregunta de roles BM D'Claudia** (texto arriba)
2. **Estado del número +51947741117**:
   - ¿Ya está activado en su iPhone con SIM puesta?
   - ¿Tiene buena señal en Wanchaq?
   - ¿Está usando ese número en WhatsApp Business app actualmente? (si sí, debe desloguearse antes del setup Cloud API)
   - ¿Acepta que ese número se use exclusivamente como Cloud API (no más WhatsApp Business app personal en ese número)?
   - ¿Disponible para recibir el SMS de verificación cuando arranquemos Fase 4A.2?

---

## 🛣 Próximos pasos recomendados

| Step | Owner | Bloqueante | ETA |
|---|---|---|---|
| 1. Mensaje a doctora con las 2 preguntas | Dario | — | Hoy/mañana |
| 2. Recibir respuestas + clasificar escenario A/B/C | Dario + Claude | Doctora | 1-2 días |
| 3. Si escenario A: Partner setup BM cross-link + vincular página | Dario + Claude | doctora promueve | ~30 min |
| 4. Si escenario B: decisión página nueva vs aceptar limitaciones | Dario | Decisión estratégica | sesión separada |
| 5. Fase 4A.2 — Setup WhatsApp Cloud API + número +51947741117 | Dario + Claude | doctora confirma número disponible | 2-3h |
| 6. Cleanup final BM "Livskin Perú Comercial" | Dario + Claude | No urgente | sesión futura |

---

## 📎 Anexos

- Checklist original de screenshots: [CHECKLIST_screenshots.md](CHECKLIST_screenshots.md)
- Memoria 🔥 nueva pendiente: `project_meta_business_state_2026_05_09.md` — snapshot del ecosistema Meta para próximas sesiones (a crear si se considera necesario)

---

## 🔗 Cross-links

- Memoria proyecto adjacente: `project_attribution_chain_event_id` (eveny_id como hilo conductor de attribution end-to-end — Meta dedup vía CAPI ya configurado en [G3])
- ADR-0019 v1.0: CAPI emitida vía ERP→n8n→Meta (mantiene validez post-cleanup)
- Memoria `project_meta_audit_2026_04_27_failed`: por qué no se completó el audit programático ese día — explica origen de los residuales limpiados hoy
