# Administration — Clakettes

Guide for anyone operating a deployment. Infrastructure in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.en.md), production checklist in [SEGURIDAD.md](SEGURIDAD.en.md).

## Initial account

In non-prod (`APP_ENV != production`) startup creates `admin` / `setup` (`admin@clakettes.com`, admin role) if it does not exist; in prod **it is not created**. Change the password on sign-in. Sign-in uses `POST /api/users/login` (30-min JWT + 30-d refresh, list and revoke sessions at `/api/auth/sessions`).

## `/api/admin` endpoints (admin role only, 403 otherwise)

| Method and route | Effect |
|---|---|
| `GET /api/admin/stats` | Counters: users, festivals, short films, messages, active |
| `GET /api/admin/tables` | Tables (except `alembic_version`) with row counts |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 if `confirm` is not `yes`, 403 if the password does not verify; own rate limit 3/300s (429, bypass with `TESTING=true`) |

## Secrets and rotation

- `SECRET_KEY`: required in prod (startup fails with the example one and suggests `secrets.token_urlsafe(64)`). Rotating it invalidates all JWTs and refresh tokens: do it in a maintenance window and notify (everyone signs in again).
- `CORS_ORIGINS`: explicit origins in prod; `*` + credentials is forbidden and blocks startup.
- Behind a proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + front TLS.

## Backups and migrations

- SQLite: copy `*.db` with the server stopped (`-Kill` first). MariaDB: `mariadb-dump` (`db-data` volume).
- Migrations: `alembic upgrade head` from `backend/` (18 versions; prod **only** Alembic, never `create_all`).
- Engine switch: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); details in [DATABASE.md](DATABASE.en.md).

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| Startup aborts on `SECRET_KEY` / CORS | insecure default or `*` in prod | Set explicit `SECRET_KEY` and `CORS_ORIGINS` |
| `401` on public form endpoints | badly generated link | Check the link token; anonymous access alone does not cause 401 |
| `403` managing festival/channel/committee | caller without role | Verify membership and role (`GET …/members`); auto-join only grants `attendee` |
| `409` on join | already a member | Use `leave` or manage from members |
| `413` on upload | exceeds 10 MB body / 5 MB image / 100 MB video / 10 MB pdf | Compress or split the file |
| `429` widespread | rate limit 100/60s per IP (or 3/300s on reset) | Wait and retry; check for leftover `TESTING=true` |
| WS does not connect | JWT without `type=access` or revoked/expired session | Sign in again; check `/api/auth/sessions` |
| Offline app does not sync | queue with exhausted failures (`failed`, 3 attempts + backoff) | Review errors in the sync prompt; `clear()` after confirming on logout |

## See also

- [USO.md](USO.en.md): system startup and operation
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.en.md): deployment, ports and CI
- [SEGURIDAD.md](SEGURIDAD.en.md): hardening checklist and policies
- [../README.md](../README.en.md): global project context
