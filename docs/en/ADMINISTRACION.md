# Administration — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guide for whoever operates a deployment. Infrastructure in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), production checklist in [SEGURIDAD.md](SEGURIDAD.md).

## Initial account

In non-prod (`APP_ENV != production`) startup creates `admin` / `setup` (`admin@clakettes.com`, admin role) if it does not exist; in prod **it is not created**. Change the password on first login. Login uses `POST /api/users/login` (JWT 30 min + refresh 30 d, list and revoke sessions at `/api/auth/sessions`).

## `/api/admin` endpoints (admin role only, 403 otherwise)

| Method and route | Effect |
|---|---|
| `GET /api/admin/stats` | Counters: users, festivals, shorts, messages, active |
| `GET /api/admin/tables` | Tables (except `alembic_version`) with row count |
| `GET /api/admin/audit-log` | Audit trail (filters `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 if `confirm` is not `yes`, 403 if password does not verify; own rate limit 3/300s (429, bypass with `TESTING=true`) |

## Secrets and rotation

- `SECRET_KEY`: mandatory in prod (startup fails with example key and indicates `secrets.token_urlsafe(64)`). Rotating it invalidates all JWT and refresh tokens: do it in a maintenance window and warn (everyone re-logs in).
- `CORS_ORIGINS`: explicit origins in prod; `*` + credentials is prohibited and blocks startup.
- Behind proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + frontend TLS.

## Federation

| Operation | Endpoint / tool | Effect |
|---|---|---|
| Nodes and policies | `GET/POST /api/federation/nodes` | Allowlist/blocklist with `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (admin) |
| Peer identity | `GET /api/federation/whoami` | Validates the peer's RS256 JWT against its JWKS; 401 if not valid |
| Portability | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Export/import signed bundles, migrate ownership and identity and resolve old refs (migrations, admin only) |
| Chat and moderation | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Signed bridge, deduplicated history, reports, mutes, word filter and limit of 10 messages/60 s per node and user |
| Events | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE with `since` and heartbeat, publish to peers and retries (3 attempts, 300 ms → 1.5 s → 5 s) |
| Resilience | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Health, heartbeat, p50/p95 metrics, immediate key revocation and incident plan |
| Conformance | `python tools/federation_conformance.py <url> [--json]` | Verifies a third-party node; exits 1 if there are critical/high failures |

The detail of the trust model and transport is in [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) and [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Backups and migrations

- SQLite: copy `*.db` while stopped (`-Kill` first). MariaDB: `mariadb-dump` (volume `db-data`).
- Migrations: `alembic upgrade head` from `backend/` (prod **only** Alembic, never `create_all`). The current head is `d1e2f3a4b5c6` (45 revisions); the latest add `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports`, `chat_mutes`, seat uniqueness (`uq_event_seat_location`) and `contest_type` in shorts with required `festival_id`.
- Engine change: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detail in [DATABASE.md](DATABASE.md).

## Troubleshooting

| Symptom | Probable cause | Action |
|---|---|---|
| Startup aborts due to `SECRET_KEY` / CORS | insecure default or `*` in prod | Define explicit `SECRET_KEY` and `CORS_ORIGINS` |
| `401` on public form endpoints | malformed link | Check the link token; anonymous access does not cause 401 by itself |
| `403` managing festival/channel/committee | caller without role | Verify membership and role (`GET …/members`); auto-join only gives `attendee` |
| `409` on joining | already a member | Use `leave` or manage from members |
| `413` uploading | exceeds 10 MB body / 5 MB image / 100 MB video / 10 MB pdf | Compress or split the file |
| `429` generalized | rate limit 100/60s per IP (or 3/300s on reset) | Wait and retry; check residual `TESTING=true` |
| WS does not connect | JWT without `type=access` or revoked/expired session | Re-login; check `/api/auth/sessions` |
| App offline does not sync | queue with exhausted failures (`failed`, 3 attempts + backoff) | Check errors in sync prompt; `clear()` after confirming on logout |
| `403` importing a bundle | `origin_domain` not allowed in the node policy | Review `/api/federation/nodes` and import again |
| `429` in federated chat | more than 10 messages/60 s per node and user | Wait for `Retry-After`; in tests it is disabled with `TESTING=true` |
| SSE events cut off or without data | invalid token or `since` ahead of the replay | Re-login and restart with `since=0` (replay of 200 events) |
| Duplicate federated messages | bridge resend | Discarded by `message_id` in `chat_outbox`; check `/api/federation/chat/messages` |

## See also

- [USO.md](USO.md): system startup and operation
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): deployment, ports and CI
- [SEGURIDAD.md](SEGURIDAD.md): hardening checklist and policies
- [../README.md](../../README.md): global project context
