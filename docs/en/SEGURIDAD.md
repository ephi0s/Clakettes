# Security — model and checklist

[ES](../es/SEGURIDAD.md) · [EN](SEGURIDAD.md) · [FR](../fr/SEGURIDAD.md) · [DE](../de/SEGURIDAD.md) · [IT](../it/SEGURIDAD.md) · [CA](../ca/SEGURIDAD.md) · [EU](../eu/SEGURIDAD.md) · [GL](../gl/SEGURIDAD.md) · [OC](../oc/SEGURIDAD.md)

## Tokens and sessions

- Access JWT (HS256, 30 min, `type=access`, unique `jti`) + opaque refresh (SHA-256 in DB, 30 d, rotation on use). Session (`UserSession`) with IP, device, expiration and revocation; `last_used_at` lazy every 5 min.
- Startup purge: revoked or expired sessions older than 30 d are deleted.
- All validation goes through `validate_access_token` (signature + type + active session); the chat WS too. Revoking a session closes the WS.
- Passwords with bcrypt; CalDAV uses bearer in URL (redacted in logs). DAV tokens expire after 180 days (`dav_token_expires_at`, renewable).

## RGPD

- Privacy by default: `is_public*` in `False` (profile, email, bio, location).
- Consent: `privacy_policy_version` + `privacy_accepted_at` at account creation.
- Right to be forgotten: `DELETE /api/users/me` (and `DELETE /api/users/{id}` admin/organizer) anonymizes the account, deletes sessions/keys/aliases/notifications/registrations and unlinks references; blocks deleting the last active admin.
- Portability: `GET /api/users/me/export` (JSON with profile, roles, registrations, messages, sessions, etc.).
- Audit (art. 5.2): `audit_logs` append-only with actor, action, target and IP on deletions, exports, roles/tags and DAV tokens; read at `GET /api/admin/audit-log` (admin only).
- Uploads: every file goes through `_save_file` (types and magic validated) and identifying metadata is removed before saving: EXIF/XMP in images (Pillow), tags in MP4/MOV (`ffmpeg -map_metadata -1`, mutagen if no ffmpeg), `/Info` in PDF (pypdf). WebM without ffmpeg is rejected (422).

## Authorization

| Scope | Rule |
|---|---|
| Festival | `require_festival_admin` (global admin or festival organizer) |
| Channel | `require_channel_admin` (creator/admin) to manage; `require_channel_member` to read private |
| Chat group | group role `admin` to delete; member to read |
| Form | `require_form_admin` (creator/admin/organizer) |
| Delegation | delegator or admin to edit/revoke |
| Global roles | `is_admin`; auto-join only with role `attendee` |
| Channel roles | `Literal[admin,moderator,member]` (422 outside list) |
| Payments | owner via registration, festival admin or global admin; mock webhook with `MOCK_WEBHOOK_SECRET` |

## Payments

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). No PAN/IBAN in DB: only amount, currency, `provider_ref` and status.
- Stripe: lazy SDK + signature verification (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1 signature without SDK; Bizum with `pay_methods="z"` (prior merchant enrollment). Validate against sandbox before prod.

## Perimeter

- Rate limit SQLite 100/60s per IP (`/dav` 600/60s); `TESTING=true` disables it.
- Headers: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, strict `Content-Security-Policy` in the API (relaxed only on `/docs`), `HSTS` only in production.
- Bodies ≤10 MB (413). CORS with credentials and explicit origins.
- MariaDB in production requires TLS (`?ssl_ca=…` in `DATABASE_URL`).

## Production checklist

1. `APP_ENV=production`, `SECRET_KEY` of 64 bytes via env (without it startup fails).
2. `CORS_ORIGINS` with explicit domains; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS with proxy + `FORWARDED_ALLOW_IPS`; no admin `setup` (only created outside prod).
4. Change `appUserModelId`/GUID of Windows notifications if app is renamed.

## Federation (phase 2)

- Node identity = domain + TLS certificate.
- Mutual peering via mTLS with domain certificates (public or private CA).
- TLS mandatory between nodes; strict validation (no self-signed in prod).
- Rotation/revocation managed by certificate renewal. A compromised node is revoked by invalidating its certificate and its directory entry.
- `allowlist`/`blocklist` per node (`node_policies`). Rate limiting and anti-flood at federation edge. Moderation report propagation between nodes.