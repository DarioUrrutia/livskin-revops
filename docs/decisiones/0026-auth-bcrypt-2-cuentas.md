# ADR-0026 — Autenticación: bcrypt + 2 cuentas con roles

**Estado:** ✅ Aprobada (MVP)
**Fecha:** 2026-04-25
**Autor propuesta:** Claude Code
**Decisor final:** Dario
**Fase del roadmap:** Fase 2
**Workstream:** Datos + Seguridad

---

## 1. Contexto

El ERP actual del Render **NO tiene autenticación** — todos los endpoints son públicos. Cualquier persona con la URL puede:
- Registrar/modificar/borrar ventas
- Ver historial completo de clientes (PII expuesta)
- Acceder a dashboards financieros
- Disparar webhooks que afectan datos

Esto es un riesgo crítico de seguridad y **bloquea**:
- Auditoría real (no se sabe QUIÉN registró cada operación)
- Compliance Ley 29733 (protección de datos personales en Perú)
- Diferenciación de roles (admin vs operadora)

Constraint duro: el ERP nuevo en VPS 3 **DEBE tener auth desde día 1** (per ADR-0023 § 6.6 eliminación del default secret inseguro).

Referencias:
- ADR-0023 (ERP refactor — define middleware de auth como capa)
- ADR-0027 (audit log — depende de saber quién hace cada acción)
- ADR-0011 v1.1 (modelo de datos — tabla `users` referenciada)
- Memoria `feedback_production_preservation` (Render no se modifica)
- Memoria `feedback_explain_to_beginner` (UX simple para Dario y doctora)

---

## 2. Opciones consideradas

### Opción A — Auth simple: bcrypt + 2 cuentas + roles + sesión Flask (RECOMENDADA)
Login form HTML. Contraseñas hasheadas con bcrypt. Sesión cookie-based con Flask-Login. 2 roles (admin / operadora). Cuentas creadas manualmente al inicializar el sistema; no hay sistema de registro público.

### Opción B — OAuth con Google
Usar Google Sign-In para login. Vos y la doctora usan sus cuentas de Google.

### Opción C — Magic links (passwordless)
Sin contraseñas. Para loguear, el sistema envía un link al WhatsApp/email del usuario. Click en link = sesión.

### Opción D — 2FA con SMS/app
Login con contraseña + código adicional vía SMS o app authenticator (Google Authenticator).

---

## 3. Análisis de tradeoffs

| Dimensión | A (bcrypt simple) | B (OAuth Google) | C (magic links) | D (2FA) |
|---|---|---|---|---|
| Complejidad implementación | **Baja** | Media (setup OAuth) | Media | Alta |
| UX para Dario y doctora | **Familiar** (user+pass) | OK (si tienen cuentas Google) | Inusual | Fricción extra |
| Costo | $0 | $0 | $0-3/mes (proveedor SMS si email no) | $0-3/mes |
| Reversibilidad | Alta | Media (lock-in con Google) | Alta | Alta |
| Seguridad para sistema interno 2-usuarios | **Apropiado** | Alto (delegado a Google) | Medio (depende de canal) | Muy alto |
| Adecuación a "principiante en implementación" (memoria) | **Excelente** | Medio (Google Cloud setup) | Medio | Bajo (curva aprendizaje) |
| Disaster recovery (qué pasa si pierdo password) | Reset desde DB | Recuperación Google | Reset por canal | Reset complejo |
| Alineación principio 1 (ejecutable > ideal) | ✅ | ✅ | ⚠️ | ❌ (overkill) |

---

## 4. Recomendación

**Opción A — bcrypt + 2 cuentas + roles + sesión Flask.**

Razones:
1. **Apropiado para el caso**: 2 usuarios internos de confianza, NO sistema público. Auth fuerte sin overkill.
2. **UX familiar**: ambas conocen "usuario + contraseña". Cero curva de aprendizaje.
3. **Implementación simple**: Flask-Login + bcrypt son librerías mature, ~200 líneas de código.
4. **Costo cero**: stack 100% self-hosted (principio 8).
5. **Recuperable**: si pierde password, vos resetéas directamente en la DB con un comando.

**Tradeoff aceptado**: Opción D (2FA) es más segura pero overkill para un sistema accedido solo por Dario y la doctora desde dispositivos conocidos. Si en el futuro escalamos a más usuarios o detectamos brechas, se reabre.

---

## 5. Decisión

**Elección:** Opción A.

**Aprobada:** 2026-04-25 por Dario con 6 parámetros explícitos:

| # | Parámetro | Decisión Dario |
|---|---|---|
| 1 | Cantidad de cuentas | 2 (Dario admin + doctora operadora) |
| 2 | Hashing | bcrypt |
| 3 | Duración sesión | **48 horas** |
| 4 | Roles diferenciados | Sí (admin vs operadora) |
| 5 | Lockout por intentos fallidos | **8 intentos + 15 min bloqueo** |
| 6 | Auto-logout por inactividad | **2 horas** |

**Razonamiento de la decisora** (síntesis):
> "Solo dos cuentas. Bcrypt OK. Sesión de 48 horas. Roles diferentes. 8 intentos + 15 min. 2 horas inactividad."

(Las preferencias hacia más comodidad — sesión 48h, 8 intentos, 2h inactividad — reflejan un sistema interno trusted-team donde la fricción de login excesivo dañaría la adopción más que un attacker explotando 48h de sesión.)

---

## 6. Diseño técnico

### 6.1 Schema de la tabla `users`

```sql
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    cod_usuario     TEXT UNIQUE NOT NULL,           -- LIVUSR0001 (Dario), LIVUSR0002 (doctora)
    username        TEXT UNIQUE NOT NULL,           -- 'dario', 'doctora'
    nombre_completo TEXT NOT NULL,                  -- "Dario Urrutia", "[Nombre Doctora]"
    email           TEXT UNIQUE,                    -- opcional, para password recovery futuro
    password_hash   TEXT NOT NULL,                  -- bcrypt hash (60 chars)
    rol             TEXT NOT NULL,                  -- 'admin' o 'operadora'
    activo          BOOLEAN NOT NULL DEFAULT true,
    failed_login_count INTEGER NOT NULL DEFAULT 0,  -- contador para lockout
    locked_until    TIMESTAMPTZ,                    -- timestamp si está bloqueada
    last_login_at   TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT rol_valido CHECK (rol IN ('admin', 'operadora'))
);

CREATE INDEX idx_users_username ON users(username) WHERE activo = true;
```

### 6.2 Schema de la tabla `user_sessions` (sesiones activas)

```sql
CREATE TABLE user_sessions (
    id              BIGSERIAL PRIMARY KEY,
    session_token   TEXT UNIQUE NOT NULL,           -- random 32+ bytes hex
    user_id         BIGINT NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,           -- created_at + 48h
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip              INET,
    user_agent      TEXT,
    revoked         BOOLEAN NOT NULL DEFAULT false,
    revoked_at      TIMESTAMPTZ,
    revoked_reason  TEXT                            -- 'logout', 'inactivity', 'expired', 'admin'
);

CREATE INDEX idx_sessions_token ON user_sessions(session_token) WHERE revoked = false;
CREATE INDEX idx_sessions_user ON user_sessions(user_id, created_at DESC);
```

### 6.3 Inicialización de usuarios (al inicializar sistema)

Migration Alembic incluye un script de seed (o un comando admin separado):

```python
# Pseudocódigo
def seed_users():
    if user_count() > 0:
        return  # ya hay usuarios, no re-seed
    
    create_user(
        cod_usuario='LIVUSR0001',
        username='dario',
        nombre_completo='Dario Urrutia',
        email='dario@livskin.site',  # opcional
        password_hash=bcrypt.hashpw(SEED_PASSWORD_DARIO, bcrypt.gensalt()),
        rol='admin'
    )
    
    create_user(
        cod_usuario='LIVUSR0002',
        username='doctora',
        nombre_completo='[Nombre completo de la doctora]',
        email='doctora@livskin.site',  # opcional
        password_hash=bcrypt.hashpw(SEED_PASSWORD_DOCTORA, bcrypt.gensalt()),
        rol='operadora'
    )
```

Las contraseñas iniciales (`SEED_PASSWORD_DARIO`, `SEED_PASSWORD_DOCTORA`) se generan **en el momento del setup**, son temporales, y Dario/doctora deben cambiarlas en su primer login.

**Mecanismo de password change** (primer login obligatorio): el sistema detecta `last_login_at IS NULL`, redirige al usuario a pantalla "cambia tu password antes de continuar".

### 6.4 Endpoints HTTP de auth

```
POST /login                  Recibe {username, password} → setea cookie sesión
POST /logout                 Invalida sesión actual
POST /change-password        Cambio voluntario o forzado en primer login
GET  /me                     Info del usuario logueado actual (usado por frontend)
POST /admin/users/reset-password    Solo admin: forza reset password de otro usuario
```

### 6.5 Middleware de protección

Cada ruta tiene un decorator:

```python
@route('/venta', methods=['POST'])
@authenticated  # cualquier rol
def venta_post():
    ...

@route('/admin/audit-log', methods=['GET'])
@authenticated
@require_role('admin')  # solo admin
def audit_log_get():
    ...
```

**Excepciones (rutas públicas)**:
- `/login`, `/logout` (obvio)
- `/ping` (keep-alive de Render preservado)
- `/static/*` (assets)
- Webhooks externos protegidos por shared secret (no por session):
  - `/webhook/form-submit` (HMAC signature de SureForms)
  - `/webhook/whatsapp` (Meta verify token)

### 6.6 Flujo de login

```
1. Usuario llena form HTML con username + password
2. POST /login → backend
3. Backend:
   a. Buscar user por username, validar activo=true
   b. Si user.locked_until > NOW() → reject con "cuenta bloqueada hasta XX:XX"
   c. bcrypt.checkpw(password_input, user.password_hash)
      - Si NO match: incrementar failed_login_count, si >=8 → set locked_until = NOW() + 15min, log audit, reject
      - Si SÍ match: reset failed_login_count, continúa
   d. Generar session_token random (secrets.token_hex(32))
   e. INSERT en user_sessions (token, user_id, expires_at = NOW() + 48h, ip, user_agent)
   f. Set cookie HTTP-only secure: 'session_token=XXX' con max-age=172800 (48h)
   g. UPDATE user.last_login_at = NOW()
   h. Audit log entry (login_success o login_failed)
   i. Si user.last_login_at era NULL → redirigir a /change-password (primer login forzado)
   j. Sino → redirigir a /
4. Usuario accede a la app
```

### 6.7 Flujo de cada request autenticado

```
1. Cookie 'session_token' viene en el request
2. Middleware:
   a. SELECT * FROM user_sessions WHERE session_token = X AND revoked = false AND expires_at > NOW()
   b. Si no existe sesión válida → redirect /login
   c. Si NOW() - last_activity_at > 2h → revoke (reason='inactivity'), redirect /login
   d. Si OK → load user, attach a request, UPDATE last_activity_at = NOW()
3. Decorator @require_role chequea user.rol
4. Si OK → ejecuta route handler
5. Si NO → 403 Forbidden con mensaje claro
```

### 6.8 Roles y permisos

**Admin** (Dario):
- Todas las funciones de operadora
- Ver `/admin/users` (lista usuarios, status, last_login)
- POST `/admin/users/reset-password` (forzar reset password de doctora si olvida)
- Ver `/admin/audit-log` (todos los movimientos del sistema)
- Ver `/admin/dedup-candidates` (revisar duplicados pendientes)
- Ver `/admin/sessions` (sesiones activas — puede revocar)
- Ver `/admin/system-health` (status de containers, backups, etc.)

**Operadora** (doctora):
- Registrar venta (POST /venta)
- Registrar pago (POST /pagos)
- Registrar gasto (POST /gasto)
- Ver historial cliente (GET /cliente)
- Ver dashboard (GET /api/dashboard)
- Ver libro (GET /api/libro)
- Cambiar su propia password (POST /change-password)
- Ver `/me` (su info)

**Lo que NO puede operadora**:
- Modificar otros usuarios
- Ver audit log de todos
- Ver sesiones de otros
- Acceder a admin endpoints

### 6.9 Lockout por intentos fallidos

| Intentos fallidos consecutivos | Acción |
|---|---|
| 1-7 | Solo incrementa contador, error UI: "Usuario o contraseña incorrectos" |
| **8** | Lockout: `locked_until = NOW() + 15min`, error UI: "Demasiados intentos. Esperá 15 min." |
| Login exitoso | Resetea contador a 0 |
| Tras 15 min | Contador no se resetea automático; usuario tiene 1 intento más antes de re-lockout |

**Recovery**: si Dario o doctora se lockean, vos (admin) podés:
- Esperar 15 min
- O ejecutar SQL: `UPDATE users SET failed_login_count=0, locked_until=NULL WHERE username='X'`

### 6.10 Auto-logout por inactividad

- Cada request actualiza `user_sessions.last_activity_at = NOW()`
- Middleware compara `NOW() - last_activity_at`
- Si >2h: revoke session, redirect /login con mensaje "Tu sesión expiró por inactividad"
- Background job opcional (cron en n8n): revocar sesiones con last_activity > 2h sin esperar request

### 6.11 Recuperación de password (escenarios)

**Caso 1: Dario olvida su password**
- Como hay solo 1 admin, no hay otro admin que pueda resetear desde UI
- Procedimiento: SSH a VPS 3, ejecutar comando que regenera password y muestra nuevo:
  ```bash
  docker compose exec erp-flask python -m scripts.reset_password --user dario
  ```

**Caso 2: Doctora olvida su password**
- Dario va a `/admin/users/reset-password?user=doctora`
- Sistema genera password temporal, la muestra a Dario
- Dario se la pasa a la doctora por WhatsApp
- Doctora hace login → forzado a cambiar password al primer login

**Caso 3: ambos olvidan al mismo tiempo** (improbable)
- Mismo procedimiento que caso 1 vía SSH

### 6.12 Seguridad operativa adicional

- **Cookie HTTP-only**: el JS del frontend no puede leer la cookie de sesión (mitiga XSS)
- **Cookie Secure**: solo se envía sobre HTTPS (ya tenemos TLS via nginx + Cloudflare)
- **Cookie SameSite=Lax**: previene CSRF en navegación cross-origin
- **CSRF tokens** en formularios POST (Flask-WTF) — extra layer
- **Rate limiting** en /login: máx 30 intentos por IP por hora (independiente del lockout por user)
- **Logs de auth**: todos los login_success, login_failed, lockout, logout van a audit_log (ADR-0027)
- **No password en logs**: el código nunca debe loguear password en plain (ni siquiera en debug)

### 6.13 Audit log integration (ADR-0027)

Cada evento de auth genera entrada en audit_log:

| Evento | Acción registrada |
|---|---|
| Login exitoso | `auth.login_success` con user, ip, user_agent |
| Login fallido | `auth.login_failed` con username intentado (no password), ip |
| Lockout activado | `auth.lockout` con user, contador alcanzado |
| Logout voluntario | `auth.logout_voluntary` con user, session_id |
| Logout por inactividad | `auth.logout_inactivity` con user, last_activity |
| Password change | `auth.password_changed` con user (no el password) |
| Admin reset password | `auth.password_reset_by_admin` con admin_user, target_user |

---

## 7. Consecuencias

### Desbloqueado
- ERP refactorizado tiene auth desde día 1 (ADR-0023 puede implementarse)
- Audit log (ADR-0027) tiene `created_by`/`updated_by` para trazabilidad
- Compliance Ley 29733 más cerca (control de acceso explícito)
- Roles permiten que la doctora trabaje sin riesgo de tocar configs admin
- Webhooks externos pueden tener su propio mechanism de auth (HMAC, no sesiones)

### Bloqueado / descartado
- Opción C (magic links) y D (2FA) descartados — overkill para 2-user team
- Opción B (OAuth Google) descartado — vendor lock-in innecesario
- NO hay sistema de registro público (las cuentas se crean a mano)

### Implementación derivada
- [ ] Migration Alembic: tablas `users` y `user_sessions`
- [ ] Seed script: crear cuenta admin Dario + operadora doctora con passwords temporales
- [ ] Implementar `middleware/auth.py`: decorators `@authenticated`, `@require_role('admin')`
- [ ] Endpoints: `/login`, `/logout`, `/change-password`, `/me`
- [ ] Endpoints admin: `/admin/users`, `/admin/users/reset-password`, `/admin/sessions`
- [ ] HTML templates: login page, change password page (estilo similar al formulario actual)
- [ ] Cookie config (HTTP-only, Secure, SameSite=Lax, max-age=48h)
- [ ] CSRF tokens en forms POST
- [ ] Rate limiting en /login (Flask-Limiter o similar)
- [ ] Tests: login success, login fail, lockout, role enforcement, inactivity timeout, password change
- [ ] Script `scripts/reset_password.py` para emergencia (CLI)
- [ ] Integration con audit_log (ADR-0027)
- [ ] Documentar en `erp-flask/README.md`: cómo crear usuarios, cómo resetear passwords

### Cuándo reabrir
- Si entran usuarios adicionales al ERP (>3): considerar Opción D (2FA) por superficie de riesgo
- Si se detecta brecha de seguridad o intento de brute force masivo
- Si compliance Ley 29733 / GDPR requiere 2FA explícitamente
- Si la doctora pide "no tener que loguearse" más fricción → considerar opciones biométricas en mobile (futuro)
- Revisión obligatoria: 2026-07-25

---

## 8. Changelog

- 2026-04-25 — v1.0 — Creada y aprobada (MVP Fase 2). Cierra la 4ta de las 5 ADRs huérfanas (0023-0027). Parámetros ajustados a preferencias de Dario (sesión 48h vs 8h propuesta, 8 intentos vs 5, inactividad 2h vs 30min) reflejando contexto trusted-team interno donde fricción excesiva daña adopción más que riesgo de exposición.
