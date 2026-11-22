# Auditoría profunda: amenazas por nodo — federación Clakettes (Fase 2)

> Origen: ítem `TASKS.md` "Auditar endpoints actuales (auth, rate limit, CORS) y documentar amenazas por nodo".
> Estado: completado. Auditoría sobre `backend/app/main.py`, `backend/app/config.py`, `backend/app/rate_limiter.py`, `backend/app/dav/auth.py`, `backend/app/auth.py`, `backend/app/routers/auth.py`, `backend/app/routers/auth_sessions.py`, `backend/app/routers/admin.py`, `backend/app/routers/federation.py`, `backend/app/routers/dependencies.py`, `backend/app/routers/permissions.py`, `backend/app/services/user_service.py`, `backend/app/services/auth_session_service.py`, `backend/app/models/user.py`, `backend/app/models/user_session.py`, `backend/tests/test_auth.py`, `backend/tests/test_federation_rate_limit.py`, `backend/tests/conftest.py`.

## 1. Arquitectura de controles (código fuente)

### 1.1 CORS — `backend/app/config.py:86-103`, `backend/app/main.py:509-523`
- `CORS_ORIGINS` por defecto `None` → `cors_origins_list` retorna `["*"]` (permite cualquier origen).
- `cors_allow_credentials` es `True` solo cuando `CORS_ORIGINS` está explícito y no vacío.
- `main.py` añade `TrustedHostMiddleware` solo si hay orígenes CORS explícitos y ninguno es `*`.
- `CORSMiddleware` se añade siempre con `allow_methods=[GET,POST,PUT,PATCH,DELETE,OPTIONS]`, `allow_headers=["*"]`.
- **Brecha:** en desarrollo sin `CORS_ORIGINS` el backend acepta peticiones cross-origin de cualquier sitio. No hay mitigación adicional (no hay CSRF token en endpoints con credenciales salvo la sesión JWT).

### 1.2 Rate limiting global — `backend/app/main.py:224-261`, `backend/app/rate_limiter.py:1-80`
- `RateLimitMiddleware`: un único `RateLimiter` con dos buckets por IP:
  - Default: 100 req / 60 s, clave `middleware:{ip}`.
  - `/dav`: 600 req / 60 s, clave `dav:{ip}`.
- Backend SQLite en `rate_limits.db` (o `RATE_LIMITS_DB_PATH`), WAL, limpieza cada 300 s, borra entradas > 1 h.
- Desactivado cuando `TESTING=true`/`1`.
- `main.py:499-502` instancia el middleware con esos parámetros.
- **Brecha:** el límite es por IP, no por usuario autenticado ni por endpoint sensible. Un atacante con muchas IPs (botnet) puede eludirlo. No hay límite progresivo ni bloqueo temporal.

### 1.3 Límites por endpoint sensible
- Login: `backend/app/routers/auth.py:17-27` → `RateLimiter()` instancia privada, 5 intentos / 300 s por IP, clave `login:{ip}`. Se resetea solo tras éxito (`auth.py:47`).
- Refresh: `backend/app/routers/auth_sessions.py:22-29` → instancia privada, 20 req / 60 s por IP, clave `refresh:{ip}`.
- Federation: `backend/app/routers/federation.py:16-27` → instancia privada, 60 req / 60 s por IP, clave `federation:{ip}`, aplicada como `dependencies=[Depends(_check_federation_rate_limit)]` en el router (línea 30).
- Admin reset DB: `backend/app/routers/admin.py:18-28` → instancia privada, 3 intentos / 300 s por `user_id`, clave `reset:{user_id}`.

### 1.4 Autenticación y sesiones — `backend/app/auth.py:1-241`
- Access token: JWT HS256, TTL 30 min (`settings.ACCESS_TOKEN_EXPIRE_MINUTES`), claims `exp`, `type="access"`, `jti`, `iss=clakettes`, `aud=clakettes-api`. Firmado con `settings.SECRET_KEY`.
- Refresh token: string opaca aleatoria de 48 bytes (96 hex), no es JWT, TTL 30 días. Almacenado como hash SHA-256 en `UserSession.refresh_token_hash`.
- `create_session` (`auth.py:89-123`): crea `UserSession` con `token_hash` (access), `refresh_token_hash`, `device_name`, `ip_address`, `user_agent`, `expires_at = now + 30 días`.
- `rotate_refresh_token` (`auth.py:126-138`): genera nuevo access + nuevo refresh, actualiza ambos hashes en la sesión, `last_used_at = now`.
- `validate_access_token` (`auth.py:148-195`): decodifica JWT, verifica firma, `iss`, `aud`, `exp`; rechaza si `type != "access"`; luego busca sesión por `token_hash` en DB y verifica `is_active`, `revoked_at IS NULL`, `expires_at`. Retorna `None` si falla cualquiera.
- `get_current_user` (`auth.py:198-241`): dependencia FastAPI; usa `validate_access_token`, toca `last_used_at` solo si > 5 min viejo, carga usuario con `user_roles` + `role` eager-loaded.
- `get_current_user_optional` (`backend/app/routers/dependencies.py:26-49`): mismo flujo pero devuelve `None` en lugar de 401.

### 1.5 Modelo de usuario y sesión — `backend/app/models/user.py:1-98`, `backend/app/models/user_session.py:1-23`
- `User`: `username` (unique, index), `email` (unique), `password_hash`, `role` (legacy), `is_active`, `is_public` + flags de visibilidad por campo, `privacy_policy_version`, `privacy_accepted_at`, `dav_token_hash` (unique, index), `dav_token_expires_at`.
- `UserSession`: `token_hash` (unique, index), `refresh_token_hash` (unique, index), `ip_address` (String 45), `user_agent`, `last_used_at`, `expires_at`, `revoked_at`, `is_active`.

### 1.6 Hash de contraseñas — `backend/app/services/user_service.py:12-17`
- `hash_password`: bcrypt con `gensalt()` (costo por defecto 12).
- `verify_password`: `bcrypt.checkpw`.
- En tests (`conftest.py:49-60`) se monkeypatea a costo 4 para acelerar.

### 1.7 DAV (CalDAV) — `backend/app/dav/auth.py:1-132`
- Token bearer aleatorio (`secrets.token_urlsafe(32)`, 43 chars), hash SHA-256 en `User.dav_token_hash`.
- Extrae credencial de `Authorization: Basic` o `Authorization: Bearer`.
- Caducidad 180 días (`DAV_TOKEN_EXPIRE_DAYS`).
- `main.py:264-284`: advierte en producción si no hay `FORWARDED_ALLOW_IPS` (no se puede verificar terminación TLS).
- `main.py:186-222`: `RedactDavTokenMiddleware` borra el token de la URL de los access logs de uvicorn.

### 1.8 Cabeceras de seguridad — `backend/app/main.py:124-152`
- `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`.
- `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'` (API), `frame-ancestors 'none'` (docs).
- `Strict-Transport-Security: max-age=63072000; includeSubDomains` solo en producción.

### 1.9 Validación de arranque — `backend/app/main.py:83-118`
- `_validate_secret_key`: rechaza `SECRET_KEY` insegura o < 32 chars en producción; rechaza `CORS_ORIGINS=["*"]` en producción con credenciales.
- TLS obligatorio para MariaDB en producción (`ssl_ca` etc.).

## 2. Endpoints de federación — estado real de implementación

El router `backend/app/routers/federation.py` (prefijo `/api/federation`, tag `federation`) expone ~60 endpoints. Tras las fases 6-10, el manifiesto está firmado, el directorio usa políticas reales, `whoami` exige JWT de par y existe mTLS opcional. La mayoría de los antiguos placeholders ya ejecutan operaciones reales (incluido el borrado propagado); solo quedan como **placeholder** los endpoints de sondeo, ahora marcados `deprecated=True` en OpenAPI:

| Endpoint | Método | Auth real | Comportamiento |
|---|---|---|---|
| `/nodes` | GET | Sí (admin) | Lista políticas reales (`NodePolicyService`) |
| `/nodes` | POST | Sí (admin) | Crea/actualiza política real |
| `/manifest` | GET | **No** | Manifiesto firmado RSA-SHA256 (`signature`, `certificate_chain`, `issued_at`, `expires_at` 24 h) |
| `/directory` | GET | **No** | Nodos permitidos reales vía `NodePeeringService().list_allowed(db)` |
| `/reports` | POST | **No** | Crea reporte real (`ModerationReportService`) |
| `/reports` | GET | **No** (filtra por `node` query) | Lista reportes reales |
| `/reports/{id}` | PATCH | **No** | Actualiza estado real |
| `/users/{ref}` | DELETE | **Sí** (propietario, admin o par verificado con el dominio en el ref) | Borrado RGPD real vía `UserService.erase_personal_data` + emisión `user.erase` en el bus y a los pares permitidos; 400/403/404/503; responde `{"erased":true,"ref":...,"user_id":...,"summary":...,"propagated":[...],"failed":[...]}` |
| `/export/{ref}` | GET | **No** | Genera el bundle real con `PortabilityService.create_bundle`; 404 si el ref no existe |
| `/verify` | POST | **No** | Verifica checksum canónico, HMAC/RSA y huella del certificado; `valid: false` si falta material criptográfico |
| `/checksum` | POST | **No** | SHA-256 del payload canónico (`canonical_json`) |
| `/publish`, `/bridge` | POST | JWT/mTLS de par | Publican en `EventBusService` / envían por `federation_chat_bridge.outbound`; sin suplantación de nodo |
| `/recover`, `/recover-node` | POST | JWT/mTLS de par | Reactivan al nodo vía resiliencia; estados `recovered`/`recovering`, nunca `revoked` |
| `/unregister`, `/sync`, `/reconcile`, `/import`, `/dedup`, `/retry` | POST | JWT/mTLS de par | Operaciones reales: revocación, replay del bus, políticas, importación de bundles, deduplicación y cola de reintentos |
| `/integrity`, `/metrics` | GET | **No** | Integridad real de `trusted_nodes` (certificados, huellas, firma del manifiesto) y snapshot de `FederationMetricsService` |
| `/health`, `/status`, `/info`, `/ping`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/notify`, `/subscribe`, `/unsubscribe`, `/discover`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` | GET/POST | **No** | Respuestas estáticas, marcadas `deprecated=True`; no reflejan estado real |
| `/whoami` | GET | JWT federado | Valida el token RS256 del par contra su JWKS; 401 si no es válido |
| `/echo`, `/time`, `/register` | GET/POST | **No** | Reales (no deprecados) |
| `/users/{ref}` | GET | **No** (solo `db` dep) | Resuelve usuario por `uuid`/`did`/`handle` — expone datos de usuario sin auth |
| `/.well-known/webfinger` | GET | **No** (solo `db` dep) | Resuelve `acct:user@domain` vía handle/username — expone existencia de usuario sin auth |

Nota: `/fallback` y `/degrade` se eliminaron porque no existía backend real de degradación; `/metrics` e `/integrity` sí exponen datos reales.

**Conclusión:** el peering real ya cuenta con mTLS, manifiesto firmado, JWKS, token federado, verificación criptográfica, portabilidad, borrado RGPD autorizado (`DELETE /api/federation/users/{ref}`), bus de eventos, bridge de chat y métricas reales. Quedan como superficie de riesgo los endpoints de sondeo obsoletos, que devuelven respuestas fijas. `/users/{ref}` (GET) y `/.well-known/webfinger` siguen exponiendo existencia de usuario sin auth de usuario (mitigable con `MTLS_REQUIRED=true`).

## 3. Tests de seguridad existentes

### 3.1 `backend/tests/test_auth.py` (136 líneas)
- `TestLogin`: éxito, contraseña errónea (401), usuario inexistente (401).
- `TestProtectedEndpoints`: 401 en creación de festival, shortfilm, mensaje, actualización de usuario sin token; `/api/festivals/` público (200).
- `TestTokenTypeValidation`: token `type=refresh` rechazado (401); token sin `type` rechazado (401); access token válido aceptado (200).
- **Ausente:** no hay test de rate limiting de login (5/300s), no hay test de fuerza bruta, no hay test de expiración de JWT, no hay test de rotación de refresh, no hay test de revocación de sesión.

### 3.2 `backend/tests/test_federation_rate_limit.py` (21 líneas)
- Envía 60 requests a `/api/federation/manifest` (200), el 61º devuelve 429. Valida el límite del router federation.
- **Ausente:** no testa los demás endpoints de federation, no testa el middleware global, no testa login/refresh.

### 3.3 `backend/tests/conftest.py`
- `TESTING=true` desactiva todo rate limiting (línea 8).
- `SECRET_KEY` por defecto `test-secret-key-for-ci-only-32bytes!` (línea 10) — inseguro pero solo para tests.
- `fast_bcrypt` reduce costo a 4 rounds (líneas 49-60).

### 3.4 `backend/tests/test_dav.py:1476-1481`
- Valida que 4 peticiones rápidas a DAV retornan 200 y la 5ª 429 (rate limiting DAV).
- Valida que rate limiting está desactivado bajo `TESTING=true`.

## 4. Matriz de amenazas por nodo (con evidencia de código)

| ID | Amenaza | Vector | Endpoints / código afectado | Control actual | Residual | Fase para cerrar |
|---|---------|--------|----------------------------|----------------|--------|----------|
| A1 | **Suplantación de nodo** | Nodo atacante se hace pasar por otro en peering | `/api/federation/*`, `.well-known/webfinger` | Allowlist/blocklist (`NodePolicyService`), manifiesto firmado RSA-SHA256, mTLS y JWKS | **Media** | Rotación de claves y verificación de CertChain |
| A2 | **Intercepción de credenciales DAV** | Bearer token en URL/path sobre HTTP sin TLS terminante | `/dav/*` | Redactado de logs (`RedactDavTokenMiddleware`), caducidad 180 días | **Alta** en prod sin proxy TLS | Fase 2 (TLS obligatorio) |
| A3 | **CORS abierto en desarrollo** | `CORS_ORIGINS` unset → `["*"]` acepta cualquier origen | Todos los endpoints API | `TrustedHostMiddleware` solo con orígenes explícitos | **Media** en dev; bloqueada en prod por `_validate_secret_key` | Fase 2 (forzar `CORS_ORIGINS` explícito) |
| A4 | **Fuerza bruta en login** | Repetición de credenciales por IP | `POST /api/users/login` | 5 intentos / 300 s por IP (`routers/auth.py:23`) | **Media** (sin bloqueo progresivo, sin CAPTCHA, sin bloqueo por usuario) | Fase 2 |
| A5 | **Flood de refresh tokens** | Agotamiento de sesiones/refresh por IP | `POST /api/auth/refresh` | 20 req / 60 s por IP | **Baja** | — |
| A6 | **Flood de federation** | Saturación de peering/directorio por IP | `/api/federation/*` | 60 req / 60 s por IP | **Baja** | — |
| A7 | **JWT con secreto débil** | Firma de tokens predecible | Todos endpoints con Bearer | `_validate_secret_key` falla en prod si `SECRET_KEY` insegura o < 32 chars | **Baja** si se respeta el env | Fase 2 |
| A8 | **Escalado / secuestro de sesión** | Uso de sesión ajena | `GET/DELETE /api/auth/sessions/*` | Propiedad de usuario verificada (`auth_sessions.py:78`) | **Baja** | — |
| A9 | **Erasure propagada sin verificación** | Borrado de usuario ajeno entre nodos | `DELETE /api/federation/users/{ref}` | Borrado RGPD real; exige propietario/admin (JWT de app) o par verificado (mTLS/JWT) cuyo dominio coincida con el ámbito del ref y no esté bloqueado | **Baja** | Implementado |
| A10 | **Export/verificación sin integridad** | Bundles aceptados sin firma/checksum real | `GET /api/federation/export/{user_ref}`, `POST /api/federation/verify` | Bundle real vía `PortabilityService`; verificación de checksum canónico, HMAC/RSA y huella; `valid: false` si falta material | **Baja** | Implementado |
| A11 | **Enumeración de usuarios** | Consulta sin auth de existencia de usuario | `GET /api/federation/users/{ref}`, `GET /.well-known/webfinger` | Sin auth de usuario; mTLS de par si `MTLS_REQUIRED=true` | **Media** | Exigir mTLS en producción |
| A12 | **Rate limiting eludible por IP** | Ataque distribuido desde muchas IPs | Middleware global + endpoints sensibles | Límite por IP, no por usuario ni por endpoint | **Media** | Fase 2 |
| A13 | **Falta de bloqueo progresivo** | Fuerza bruta lenta por debajo del umbral 5/300s | Login | Solo límite fijo 5/300s, reset tras éxito | **Media** | Fase 2 |
| A14 | **DAV token sin rotación forzada** | Token largo vida (180 días) robado reutilizable | `/dav/*` | Caducidad 180 días, hash SHA-256 | **Media** | Fase 2 |

## 5. Brechas de implementación (falsos controles)

1. **Endpoints de sondeo de federation (~25)** siguen devolviendo `True`/`[]`/`{}` estáticos sin autenticación ni validación; están marcados `deprecated=True` para que los clientes no confíen en ellos. El resto de antiguos placeholders ya ejecutan operaciones reales, aunque muchas sin autenticación de usuario.
2. **`/users/{ref}` y `/.well-known/webfinger` expone datos de usuario sin autenticación** (solo dependen de `get_db`). Un nodo remoto (o cualquier cliente) puede enumerar usuarios por handle/username/uuid/did.
3. **`.env.example` ya existe en `backend/`** y documenta `SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, `APP_ENV`, `PUBLIC_BASE_URL`, mTLS, JWT y pagos; conviene mantenerlo sincronizado con `config.py`.
4. **`RateLimitMiddleware` es por IP global**; no distingue endpoints sensibles (login ya tiene límite propio, pero otros endpoints de escritura no tienen límite por usuario autenticado).
5. **`create_session` almacena `ip_address` y `user_agent` pero nunca se usan para detección de anomalías** (imposible viajar, IP nueva, etc.).
6. **`last_used_at` se toca con `db.commit()` en cada request > 5 min** (`auth.py:230`), lo que es un punto de contención en tráfico alto y escribe en DB en el path de lectura de autenticación.

## 6. Referencias cruzadas

- `docs/es/FEDERATION_SECURITY.md` — modelo de confianza, mTLS, rotación/revocación por certificado.
- `docs/es/FEDERATION_PROTOCOL.md` — pasos de interoperabilidad (manifest, directory, JWKS, webfinger, Schema v1).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entidades y endpoints de federación.
- `docs/es/AUDITORIA.md` — auditoría general de código (rev. 10/10/2026), cifras de routers/servicios/modelos/tests.

## 7. Recomendaciones inmediatas (Fase 2)

1. Forzar `CORS_ORIGINS` explícito en producción (ya validado al arrancar en `main.py:99-103`).
2. No exponer `/dav` sin terminación TLS en un proxy de confianza; definir `FORWARDED_ALLOW_IPS` y ejecutar uvicorn con `--proxy-headers` (`main.py:279-284`).
3. Implementar mTLS entre nodos antes de aceptar peering real (`FEDERATION_SECURITY.md`).
4. Revisar y proteger los placeholder endpoints de federation antes de exponerlos a nodos externos (el borrado propagado ya está protegido).
5. Añadir bloqueo progresivo / CAPTCHA tras fallos repetidos de login más allá del límite 5/300s.
6. Considerar rate limiting por usuario autenticado (no solo por IP) en endpoints sensibles de escritura.
7. Crear `backend/.env.example` documentando todas las variables de producción.
