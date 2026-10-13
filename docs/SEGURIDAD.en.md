# Security — model and checklist

[ES](SEGURIDAD.md) · [EN](SEGURIDAD.en.md) · [FR](SEGURIDAD.fr.md) · [DE](SEGURIDAD.de.md) · [IT](SEGURIDAD.it.md) · [CA](SEGURIDAD.ca.md) · [EU](SEGURIDAD.eu.md) · [GL](SEGURIDAD.gl.md) · [OC](SEGURIDAD.oc.md)

## Tokens and sessions

- Access JWT (HS256, 30 min, `type=access`, unique `jti`) + opaque refresh (SHA-256 in DB,
  30 d, rotation on use). Session (`UserSession`) with IP, device,
  expiry and revocation; lazy `last_used_at` every 5 min.
- Purge at startup: sessions revoked or expired more than 30 d ago are deleted.
- All validation goes through `validate_access_token` (signature + type + active
  session); the chat WS too. Revoking a session closes the WS.
- Passwords with bcrypt; CalDAV uses bearer in URL (redacted in logs).
  DAV tokens expire after 180 days (`dav_token_expires_at`, regenerable).

## GDPR

- Privacy by default: `is_public*` set to `False` (profile, email, bio, location).
- Consent: `privacy_policy_version` + `privacy_accepted_at` at account creation.
- Right to erasure: `DELETE /api/users/me` (and `DELETE /api/users/{id}` admin/organizer)
  anonymizes the account, deletes sessions/keys/aliases/notifications/registrations
  and unlinks references; blocks deleting the last active admin.
- Portability: `GET /api/users/me/export` (JSON with profile, roles, registrations,
  messages, sessions, etc.).
- Audit (art. 5.2): append-only `audit_logs` with actor, action, target and IP
  on deletions, exports, roles/tags and DAV tokens; read at
  `GET /api/admin/audit-log` (admin only).
- Uploads: every file goes through `_save_file` (types and magic validated) and has
  identifying metadata stripped before saving: EXIF/XMP in images
  (Pillow), tags in MP4/MOV (`ffmpeg -map_metadata -1`, mutagen if no
  ffmpeg), `/Info` in PDF (pypdf). WebM without ffmpeg is rejected (422).

## Authorization

| Scope | Rule |
|---|---|
| Festival | `require_festival_admin` (global admin or festival organizer) |
| Channel | `require_channel_admin` (creator/admin) to manage; `require_channel_member` to read private ones |
| Chat group | group `admin` role to delete; member to read |
| Form | `require_form_admin` (creator/admin/organizer) |
| Delegation | delegator or admin to edit/revoke |
| Global roles | `is_admin`; auto-join only with `attendee` role |
| Channel roles | `Literal[admin,moderator,member]` (422 outside the list) |
| Payments | owner via registration, festival or global admin; mock webhook with `MOCK_WEBHOOK_SECRET` |

## Payments

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`). No PAN/IBAN in DB: only amount, currency, `provider_ref` and status.
- Stripe: lazy SDK + signature verification (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1 signature without SDK; Bizum with `pay_methods="z"` (prior setup at the merchant). Validate against the sandbox before prod.

## Perimeter

- SQLite rate limit 100/60s per IP (`/dav` 600/60s); `TESTING=true` turns it off.
- Headers: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`,
  strict `Content-Security-Policy` on the API (relaxed only on `/docs`),
  `HSTS` in production only.
- Bodies ≤10 MB (413). CORS with credentials and explicit origins.
- MariaDB in production requires TLS (`?ssl_ca=…` in `DATABASE_URL`).

## Production checklist

1. `APP_ENV=production`, 64-byte `SECRET_KEY` via env (without it startup fails).
2. `CORS_ORIGINS` with explicit domains; MariaDB `DATABASE_URL` + `alembic upgrade head`.
3. TLS with proxy + `FORWARDED_ALLOW_IPS`; no `setup` admin (only created outside prod).
4. Change Windows notification `appUserModelId`/GUID if the app is renamed.
