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
| Global roles | unified `require_admin(user, db)`: legacy `admin` role (case-insensitive) or `UserRole` with status `ACTIVE`/`APPROVED`; auto-join only with role `attendee` |
| User aliases | `require_self_or_admin` (owner or admin) on create/update/delete |
| User blocks | `require_owner_or_admin` (owner or `can_edit_user`) on block/unblock/list/status |
| Channel roles | `Literal[admin,moderator,member]` (422 outside list) |
| Payments | owner via registration, festival admin or global admin; mock webhook with `MOCK_WEBHOOK_SECRET` |

## Payments

- `PAYMENTS_PROVIDER=mock|stripe|redsys` (`payment_providers.py`; `mock` by default in `backend/app/config.py`). No PAN/IBAN in DB: only amount, currency, `provider_ref` and status.
- Stripe: lazy SDK + signature verification (`STRIPE_WEBHOOK_SECRET`).
- Redsys: HMAC_SHA256_V1 signature without SDK; Bizum with `pay_methods="z"` (prior merchant enrollment). Validate against sandbox before prod.
- `confirm` and `refund` sync `FestivalRegistration.payment_status` (`paid`/`refunded`) and, on paid, `paid_at`/`payment_method`/`transaction_id`; the Payment's `provider` is taken from the active provider, not from `PAYMENTS_PROVIDER`.
- **Current status**: Stripe and Redsys are NOT operational yet; their webhooks still need wiring (`POST /api/payments/webhook/{stripe,redsys}`). Only the simulated webhook works today (`POST /api/payments/webhook/mock`).
- Redsys `confirm` always returns `"pending"`: it does not confirm real charges until the webhook is wired.

## Perimeter

- SQLite rate limit 100/60 s per IP globally, 600/60 s on `/dav`, 5/300 s login, 20/60 s refresh and 3/300 s reset and 60/60 s on federation. `TESTING` ∈ {1, true, yes, on} (`app.config.is_testing()`) disables all limits and auto-migration.
- Headers: `nosniff`, `DENY`, `Referrer-Policy`, `Permissions-Policy`, strict `Content-Security-Policy` in the API (relaxed only on `/docs`), `HSTS` only in production.
- Bodies ≤10 MB (413). CORS with credentials and explicit origins.
- MariaDB in production requires TLS (`?ssl_ca=…` in `DATABASE_URL`).

## Production checklist

1. `APP_ENV=production`, `SECRET_KEY` of 64 bytes via env (without it startup fails).
2. `CORS_ORIGINS` with explicit domains; `DATABASE_URL` MariaDB + `alembic upgrade head`.
3. TLS with proxy + `FORWARDED_ALLOW_IPS`; no admin `setup` (only created outside prod).
4. Change `appUserModelId`/GUID of Windows notifications if app is renamed.

## Federation (phases 2-10)

Full detail in [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md). Controls in force:

- Node identity = domain + TLS certificate. Mutual peering via mTLS with domain certificates (public or private CA); TLS mandatory, no self-signed in prod.
- RSA-SHA256 signed manifest with own PEM/key and 24 h `expires_at`; `whoami` requires a federation JWT; JWKS to verify peer tokens; `peers/verify` and `peers/revoke`.
- `allowlist`/`blocklist` per node (`node_policies`), with `import_only`, `disable_chat` and `disable_search`. Rate limiting and anti-flood at the edge; moderation report propagation.
- Portability: HMAC-signed bundles and checksum; import validates/sanitizes `MediaUrl` and normalizes `contest_type`; festival and identity migration with `identity_redirects` and auditing in `migration_audits`; migration endpoints require admin.
- Federated chat: RS256-signed bridge, dedup by `message_id` in `chat_outbox`, ordering by `timestamp`; reports and mutes, word filter and limit of 10 messages/60 s per node and user.
- Events: HMAC-signed publish (`X-Clakettes-Signature`), SSE with mandatory `token` in query, optional `since` and `limit`, replay of 200 and 3 retries with backoff.
- Resilience: `/api/federation/resilience/health`, `/heartbeat`, `/metrics` (p50/p95), key revocation (`keys/revoke`) and an 8-step incident plan. Rotation/revocation by certificate renewal; a compromised node is invalidated in the directory.