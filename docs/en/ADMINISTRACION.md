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

## Backups and migrations

- SQLite: copy `*.db` while stopped (`-Kill` first). MariaDB: `mariadb-dump` (volume `db-data`).
- Migrations: `alembic upgrade head` from `backend/` (36 versions; prod **only** Alembic, never `create_all`).
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

## See also

- [USO.md](USO.md): system startup and operation
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): deployment, ports and CI
- [SEGURIDAD.md](SEGURIDAD.md): hardening checklist and policies
- [../README.md](../../README.en.md): global project context