# Seguridade — modelo e checklist

[ES](../es/SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Tokens e sesións

- Access JWT (HS256, 30 min, `type=access`, `jti` único) + refresh opaco (SHA-256 en BD, 30 d, rotación ao usar). Sesión (`UserSession`) con IP, dispositivo, expiración e revocación; `last_used_at` lazy cada 5 min.
- Purga no arranque: elimínanse sesións revocadas ou caducadas fai >30 d.
- Toda a validación pasa por `validate_access_token` (firma + tipo + sesión activa); o WS do chateo tamén. Revocar unha sesión pecha o WS.
- Contrasinais con bcrypt; CalDAV usa bearer na URL (redactado en logs). Os tokens DAV caducan aos 180 días (`dav_token_expires_at`, regenerables).

## RGPD

- Privacidade por defecto: `is_public*` en `False` (perfil, email, bio, ubicación).
- Consentimento: `privacy_policy_version` + `privacy_accepted_at` ao crear a conta.
- Olvido: `DELETE /api/users/me` (e `DELETE /api/users/{id}` admin/organizer) anonimiza a conta, borra sesións/chaves/alias/notificacións/inscripcions e desvincula referencias; bloquea borrar o último admin activo.
- Portabilidade: `GET /api/users/me/export` (JSON con perfil, roles, inscripcions, mensaxes, sesións, etc.).
- Auditoria (art. 5.2): `audit_logs` append-only con actor, acción, obxectivo e IP en borrados, exportacións, roles/tags e tokens DAV; lectura en `GET /api/admin/audit-log` (solo admin).
- Subidas: todo arquivo pasa por `_save_file` (tipos e maía validados) e elimínanse metadatos identificativos antes de gardar: EXIF/XMP en imaxes (Pillow), etiquetas en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen se non hai ffmpeg), `/Info` en PDF (pypdf). WebM sen ffwxénese rechaza (422).

## Autorización

| Ámbito | Regra |
|--------|-------|
| Festival | `require_festival_admin` (admin global u organizador do festival) |
| Canal | `require_channel_admin` (creador/admin) para xestionar; `require_channel_member` para ler privados |
| Grupo de chat | rol `admin` do grupo para borrar; membro para ler |
| Formulario | `require_form_admin` (creador/admin/organizador) |
| Delegación | delegador ou admin para editar/revocar |
| Roles globais | `require_admin(user, db)` unificado: rol legacy `admin` (case-insensitive) ou `UserRole` con estado `ACTIVE`/`APPROVED`; auto-join só con rol `attendee` |
| Alias de usuario | `require_self_or_admin` (propietario ou admin) en create/update/delete |
| Bloqueos de usuario | `require_owner_or_admin` (propietario ou `can_edit_user`) en block/unblock/list/status |
| Roles de canal | `Literal[admin,moderator,member]` (422 fóra da lista) |
| Pagos | doente vía inscripción, admin do festival ou global; webhook mock con `MOCK_WEBHOOK_SECRET` |

## Pagos

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; `mock` por defecto en `backend/app/config.py`). Sen PAN/IBAN na BD: só importe, moeda, `provider_ref` e estado.
- Stripe: SDK preguizoso + verificación de firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 sen SDK; Bizum con `pay_methods="z"` (alta previa no comercio). Validar no sandbox antes de prod.
- `confirm` e `refund` sincronizan `FestivalRegistration.payment_status` (`paid`/`refunded`) e, en paid, `paid_at`/`payment_method`/`transaction_id`; o `provider` do Payment tómao do provider activo, non de `PAYMENTS_PROVIDER`.
- **Estado real**: Stripe e Redsys NON están operativos aínda; falta cablear os seus webhooks (`POST /api/payments/webhook/{stripe,redsys}`). Hoxe só funciona o webhook simulado (`POST /api/payments/webhook/mock`).
- O `confirm` de Redsys devolve sempre `"pending"`: non confirma cobros reais ata que se cablee o webhook.

## Perímetro

- Rate limit SQLite 100/60 s por IP global, 600/60 s en `/dav`, 5/300 s login, 20/60 s refresh e 3/300 s reset e 60/60 s en federación. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) apaga todos os límites e a auto-migración.
- Cabeceras: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` estrita na API (relaxada só en `/docs`), `HSTS` só en produción.
- Corpos ≤10 MB (413). CORS con credenciais e oríxenes explícitas.
- MariaDB en produción exige TLS (`?ssl_ca=…` en `DATABASE_URL`).

## Checklist produción

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes por env (sen ella non arranca).
2. `CORS_ORIGINS` con dominios explícitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS con proxy + `FORWARDED_ALLOW_IPS`; sen admin `setup` (só créase fóra de prod).
4. Cambiar `appUserModelId`/GUID de notificacións Windows se se renomea a app.

## Endurecemento e cadea de subministración (11/2026)

- **Auditoría de dependencias**: `tools/audit_deps.py` consulta OSV (CVE/GHSA) para `requirements`, `pubspec.lock` e un venv. Ex.: `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable`. Durante a auditoría apareceu un aviso irreparable de python-ecdsa (CVE-2024-23342) unicamente no `.venv` local; `pip show` confirma que ningún paquete o require e unha resolución limpa dos requirements non o instala, polo que non forma parte do proxecto.
- **Versións fixadas/parcheadas**: `httpx2>=2.12.0`, `httpcore2>=2.10.0`, `pyasn1>=0.6.5`, `bcrypt==5.0.0`, `pytest==9.2.0`, `icalendar==7.3.2`. As versións directas xa estaban libres de avisos OSV ao facer a auditoría.
- **Produción**: `docker compose --profile prod` exixe `APP_ENV=production`, `SECRET_KEY`, `CORS_ORIGINS` explícito, `PUBLIC_BASE_URL` e `DATABASE_URL` con parámetros TLS; a validación de arranque bloquea claves febles/comodín. `start.ps1` xera unha clave aleatoria se non hai `SECRET_KEY` (antes fixaba unha coñecida).
- **Backend**: middleware e validación de seguridade movidos de `app/main.py` a `app/security.py`; CORS restrinxe cabeceiras; docs/redoc/openapi desactivados en produción; a exportación de portabilidade exixe usuario/admin/nodo federado verificado; o rexistro de nodos exixe autenticación en produción; o JWKS federado só se descarga de nodos rexistrados (anti-SSRF, sen redireccións); SSE acepta Bearer na cabeceira (`token` na query obsoleto); webhooks mock con `compare_digest`; contrasinais >72 bytes rexeitadas con 422; a importación de bundles só aplica campos de perfil (nunca `role`/`is_active`/privacidade); SVG servidos con CSP sandbox.
- **Frontend**: tokens e claves E2EE en `flutter_secure_storage` con migración única (a web usa SharedPreferences); helper único `UrlLauncherService` con allowlist `http`/`https`/`mailto`/`tel`/`geo`; validación HTTPS do backend salvo hosts locais de desenvolvemento; o logout purga as caixas Hive e o socket; CSP en `web/index.html` e HSTS/nosniff en `nginx.conf`.
- **Referencias**: OWASP Top 10 2025 (A02 Configuración, A03 Cadea de subministración, A05 Inxección, A07 Autenticación) e OWASP MASVS para Flutter.

## Federación (fases 2-10)

Detalle completo en [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Controles vixentes:

- Identidade de nodo = dominio + certificado TLS. Peering mutuo vía mTLS con certificados de dominio (CA pública ou privada); TLS obrigatorio, sen self-signed en prod.
- Manifesto asinado RSA-SHA256 con PEM/clave propios e `expires_at` de 24 h; `whoami` esixe JWT federado; JWKS para verificar tokens dos pares; `peers/verify` e `peers/revoke`.
- `allowlist`/`blocklist` por nodo (`node_policies`), con `import_only`, `disable_chat` e `disable_search`. Rate limiting e anti-inundación no borde; propagación de informes de moderación.
- Portabilidade: bundles asinados con HMAC e checksum; a importación valida/sanea `MediaUrl` e normaliza `contest_type`; migración de festivais e identidades con `identity_redirects` e auditoría en `migration_audits`; os endpoints de migración esixen admin.
- Chat federado: bridge asinado RS256, dedup por `message_id` en `chat_outbox`, orde por `timestamp`; informes e silenciamentos, filtro de palabras e límite de 10 mensaxes/60 s por nodo e usuario.
- Eventos: publicación asinada con HMAC (`X-Clakettes-Signature`), SSE con Bearer na cabeceira (`token` na query obsoleto), `since` e `limit` opcionais, replay de 200 e 3 reintentos con backoff.
- Resiliencia: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), revogación de claves (`keys/revoke`) e plan de incidente en 8 pasos. Rotación/revocación por renovación do certificado; un nodo comprometido invalídase no directorio.