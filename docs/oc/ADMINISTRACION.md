# Administracion — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](ADMINISTRACION.md)

Guia per qual opera un desplegament. Infraestructura dins [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), lista de contraròtle de produccion dins [SEGURIDAD.md](SEGURIDAD.md).

## Compte inicial

En non-prod (`APP_ENV != production`) l'arranjada crea `admin` / `setup` (`admin@clakettes.com`, ròtle admin) se existís pas; en prod **es crea pas**. Cambiat lo senhal en intrant. L'inscripcion utilize `POST /api/users/login` (JWT 30 min + refresh 30 d, lista e revoca las sessions a `/api/auth/sessions`).

## Endpoints `/api/admin` (solament ròtle admin, 403 autrament)

| Metòde e rota | Efecte |
|---|---|
| `GET /api/admin/stats` | Comptaires: usagis, festivals, corts, messatges, actius |
| `GET /api/admin/tables` | Taulas (levat `alembic_version`) amb un nombre de linhas |
| `GET /api/admin/audit-log` | Traça d'audit (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 se `confirm` es pas `yes`, 403 se lo senhal valida pas; rate-limit propi 3/300s (429, bypass amb `TESTING=true`) |

## Secrets e rotacion

- `SECRET_KEY`: obligatòria en prod (l'arranjada fracassa amb la d'exemple e indica `secrets.token_urlsafe(64)`). La rotar invalida totes los JWT e refresh tokens: faguetz-o dins una fenestra de mantenença e avisatz (totes devon tornar far login).
- `CORS_ORIGINS`: origines explicitas en prod; `*` + credencials es interdit e bloca l'arranjada.
- Darrièr un proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Federacion

| Operacion | Endpoint / aisina | Efecte |
|---|---|---|
| Noses e politicas | `GET/POST /api/federation/nodes` | Allowlist/blocklist amb `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (admin) |
| Identitat del par | `GET /api/federation/whoami` | Valida lo JWT RS256 del par contra son JWKS; 401 se es pas valid |
| Portabilitat | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Exportar/importar de bundles signats, migrar proprietat e identitat e resòlver las refs ancianas (las migracions, solament admin) |
| Chat e moderacion | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Bridge signat, istoric deduplicat, rapòrts, silencis, filtre e limita de 10 messatges/60 s per nose e usagi |
| Eveniments | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE amb `since` e batement, publicacion als pares e reensajos (3 ensajos, 300 ms→5 s) |
| Resiliéncia | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Santat, batement, metricas p50/p95, revocacion immediata de claus e plan d'incident |
| Conformitat | `python tools/federation_conformance.py <url> [--json]` | Verifica un nose tèrç; sòrt 1 se i a de fracasses critics/ausats |

Lo detalh del modèl de fisança e del transpòrt es dins [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) e [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Còpias de seguretat e migracions

- SQLite: copiar `*.db` a cald arrestat (`-Kill` abans). MariaDB: `mariadb-dump` (volum `db-data`).
- Migracions: `alembic upgrade head` dempuèi `backend/` (prod **solament** Alembic, jamai `create_all`). Lo head actual es `c1d2e3f4a5b6` (42 revisions) e aponda `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports` e `chat_mutes`.
- Cambi de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detalh dins [DATABASE.md](DATABASE.md).

## Resolucion de problèmas

| Sintòma | Causa probabla | Accion |
|---|---|---|
| L'arranjada s'arrèsta per `SECRET_KEY` / CORS | defaut pauc segur o `*` en prod | Definir `SECRET_KEY` e `CORS_ORIGINS` explicits |
| `401` suls endpoints publics de formularis | ligam mal generat | Revisar lo token del ligam; l'accès anonim dona pas 401 per el meteis |
| `403` en gestionant festival/canal/comitat | caller sens ròtle | Verificar l'adjoncion e lo ròtle (`GET …/members`); l'auto-join dona solament `attendee` |
| `409` en s'adjonhent | ja es membre | Utilizar `leave` o gestionar dempuèi los membres |
| `413` en montant | passa 10 MB còs / 5 MB imatge / 100 MB vidèo / 10 MB pdf | Comprimir o partejar lo fichièr |
| `429` generalizat | rate limit 100/60s per IP (o 3/300s al reset) | Espèrar e tornar ensajar; revisar `TESTING=true` residual |
| WS se connecta pas | JWT sens `type=access` o session revocada/expirada | Tornar far login; revisar `/api/auth/sessions` |
| App fòra linha se sincroniza pas | còda amb de fracasses agotats (`failed`, 3 ensajos + backoff) | Revisar las errors dins l'invite de sync; `clear()` après confirmacion al logout |
| `403` en important un bundle | `origin_domain` non autorizat dins la politica del nose | Revisar `/api/federation/nodes` e tornar importar |
| `429` en chat federat | mai de 10 messatges/60 s per nose e usagi | Espèrar lo `Retry-After`; en tèsts se desactiva amb `TESTING=true` |
| Eveniments SSE copats o sens donadas | token invalid o `since` davant lo replay | Tornan far login e recomençan amb `since=0` (replay de 200 eveniments) |
| Messatges federats duplicats | reenviament del bridge | Son escartats per `message_id` dins `chat_outbox`; revisar `/api/federation/chat/messages` |

## Vejatz tanben

- [USO.md](USO.md): arranjada e operacion del sistèma
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): desplegament, pòrts e CI
- [SEGURIDAD.md](SEGURIDAD.md): lista de renforçament e politicas
- [../README.oc.md](../../README.oc.md): context general del projècte
