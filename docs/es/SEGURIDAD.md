# Seguridad — modelo y checklist

[ES](SEGURIDAD.md) · [EN](../en/SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Tokens y sesiones

- Access JWT (HS256, 30 min, `type=access`, `jti` único) + refresh opaco (SHA-256 en BD, 30 d, rotación al usar). Sesión (`UserSession`) con IP, dispositivo, expiración y revocación; `last_used_at` lazy cada 5 min.
- Purga en arranque: se eliminan sesiones revocadas o caducadas hace >30 d.
- Toda validación pasa por `validate_access_token` (firma + tipo + sesión activa); el WS del chat también. Revocar sesión cierra el WS.
- Passwords con bcrypt; CalDAV usa bearer en URL (redactado en logs). Los tokens DAV caducan a los 180 días (`dav_token_expires_at`, regenerables).

## RGPD

- Privacidad por defecto: `is_public*` en `False` (perfil, email, bio, ubicación).
- Consentimiento: `privacy_policy_version` + `privacy_accepted_at` al crear cuenta.
- Olvido: `DELETE /api/users/me` (y `DELETE /api/users/{id}` admin/organizer) anonimiza la cuenta, borra sesiones/claves/alias/notificaciones/inscripciones y desvincula referencias; bloquea borrar el último admin activo.
- Portabilidad: `GET /api/users/me/export` (JSON con perfil, roles, inscripciones, mensajes, sesiones, etc.).
- Auditoría (art. 5.2): `audit_logs` append-only con actor, acción, objetivo e IP en borrados, exportaciones, roles/tags y tokens DAV; lectura en `GET /api/admin/audit-log` (solo admin).
- Subidas: todo fichero pasa por `_save_file` (tipos y magia validados) y se le eliminan metadatos identificativos antes de guardar: EXIF/XMP en imágenes (Pillow), tags en MP4/MOV (`ffmpeg -map_metadata -1`, mutagen si no hay ffmpeg), `/Info` en PDF (pypdf). WebM sin ffmpeg se rechaza (422).

## Autorización

| Ámbito | Regla |
|---|---|
| Festival | `require_festival_admin` (admin global u organizer del festival) |
| Canal | `require_channel_admin` (creador/admin) para gestionar; `require_channel_member` para leer privados |
| Grupo de chat | rol `admin` del grupo para borrar; miembro para leer |
| Formulario | `require_form_admin` (creador/admin/organizer) |
| Delegación | delegador o admin para editar/revocar |
| Roles globales | `require_admin(user, db)` unificado: rol legacy `admin` (case-insensitive) o `UserRole` con estado `ACTIVE`/`APPROVED`; auto-join solo con rol `attendee` |
| Alias de usuario | `require_self_or_admin` (propietario o admin) en create/update/delete |
| Bloqueos de usuario | `require_owner_or_admin` (propietario o `can_edit_user`) en block/unblock/list/status |
| Roles de canal | `Literal[admin,moderator,member]` (422 fuera de lista) |
| Pagos | dueño vía inscripción, admin de festival o global; webhook mock con `MOCK_WEBHOOK_SECRET` |

## Pagos

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; default `mock` en `backend/app/config.py`). Sin PAN/IBAN en BD: solo importe, moneda, `provider_ref` y estado.
- Stripe: SDK perezoso + verificación de firma (`STRIPE_WEBHOOK_SECRET`).
- Redsys: firma HMAC_SHA256_V1 sin SDK; Bizum con `pay_methods="z"` (alta previa en el comercio). Validar contra el sandbox antes de prod.
- `confirm` y `refund` sincronizan `FestivalRegistration.payment_status` (`paid`/`refunded`) y, en paid, `paid_at`/`payment_method`/`transaction_id`; el `provider` del Payment se toma del provider activo, no de `PAYMENTS_PROVIDER`.
- **Estado real**: Stripe y Redsys NO están operativos todavía; falta cablear sus webhooks (`POST /api/payments/webhook/{stripe,redsys}`). Por ahora solo funciona el webhook simulado (`POST /api/payments/webhook/mock`).
- El `confirm` de Redsys devuelve siempre `"pending"`: no confirma cobros reales hasta que se cablee el webhook.

## Perímetro

- Rate limit SQLite 100/60 s por IP global, 600/60 s en `/dav`, 5/300 s login, 20/60 s refresh, 3/300 s reset y 60/60 s en federación. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) apaga todos los límites y la auto-migración.
- Cabeceras: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` estricta en el API (relajada solo en `/docs`), `HSTS` solo en producción.
- Cuerpos ≤10 MB (413). CORS con credenciales y orígenes explícitos.
- MariaDB en producción exige TLS (`?ssl_ca=…` en `DATABASE_URL`).

## Checklist producción

1. `APP_ENV=production`, `SECRET_KEY` de 64 bytes por env (sin ella no arranca).
2. `CORS_ORIGINS` con dominios explícitos; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS con proxy + `FORWARDED_ALLOW_IPS`; sin admin `setup` (solo se crea fuera de prod).
4. Cambiar `appUserModelId`/GUID de notificaciones Windows si se renombra la app.

## Federación (fases 2-10)

Detalle completo en [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Controles vigentes:

- Identidad de nodo = dominio + certificado TLS. Peering mutuo vía mTLS con certificados de dominio (CA pública o privada); TLS obligatorio, sin self-signed en prod.
- Manifiesto firmado RSA-SHA256 con PEM/clave propios y `expires_at` de 24 h; `whoami` exige JWT federado; JWKS para verificar tokens de pares; `peers/verify` y `peers/revoke`.
- `allowlist`/`blocklist` por nodo (`node_policies`), con `import_only`, `disable_chat` y `disable_search`. Rate limiting y anti-flood en el borde; propagación de reportes de moderación.
- Portabilidad: bundles firmados con HMAC y checksum; import valida/sanea `MediaUrl` y normaliza `contest_type`; migración de festivales e identidades con `identity_redirects` y auditoría en `migration_audits`; los endpoints de migración exigen admin.
- Chat federado: bridge firmado RS256, dedup por `message_id` en `chat_outbox`, orden por `timestamp`; reportes y mutes, filtro de palabras y límite de 10 mensajes/60 s por nodo y usuario.
- Eventos: publicación firmada con HMAC (`X-Clakettes-Signature`), SSE con `token` obligatorio en query, `since` y `limit` opcionales, replay de 200 y 3 reintentos con backoff.
- Resiliencia: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), revocación de claves (`keys/revoke`) y plan de incidente en 8 pasos. Rotación/revocación por renovación del certificado; un nodo comprometido se invalida en el directorio.