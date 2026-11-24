# Administració — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guia per a qui opera un desplegament. Infraestructura a [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), llista de comprovació de producció a [SEGURIDAD.md](SEGURIDAD.md).

## Compte inicial

En no-prod (`APP_ENV != production`) l'arrancada crea `admin` / `setup` (`admin@clakettes.com`, rol admin) si no existeix; en prod **no es crea**. Canvia la contrasenya en entrar. L'alta usa `POST /api/users/login` (JWT 30 min + refresh 30 d, llista i revoca sessions a `/api/auth/sessions`).

## Endpoints `/api/admin` (només rol admin, 403 en cas contrari)

| Mètode i ruta | Efecte |
|---|---|
| `GET /api/admin/stats` | Comptadors: usuaris, festivals, curts, missatges, actius |
| `GET /api/admin/tables` | Taules (menys `alembic_version`) amb nº de files |
| `GET /api/admin/audit-log` | Traça d'auditoria (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no és `yes`, 403 si la contrasenya no verifica; rate-limit propi 3/300s (429, bypass amb `TESTING=true`) |

## Secrets i rotació

- `SECRET_KEY`: obligatòria en prod (l'arrancada falla amb la d'exemple i indica `secrets.token_urlsafe(64)`). Rotar-la invalida tots els JWT i refresh tokens: fes-ho en finestra de manteniment i avisa (tots tornen a fer login).
- `CORS_ORIGINS`: orígens explícits en prod; `*` + credencials està prohibit i bloqueja l'arrancada.
- Darrere de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Federació

| Operació | Endpoint / eina | Efecte |
|---|---|---|
| Nodes i polítiques | `GET/POST /api/federation/nodes` | Allowlist/blocklist amb `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (admin) |
| Identitat del pare | `GET /api/federation/whoami` | Valida el JWT RS256 del pare contra el seu JWKS; 401 si no és vàlid |
| Portabilitat | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Exportar/importar bundles signats, migrar propietat i identitat i resoldre refs antigues (les migracions, només admin) |
| Xat i moderació | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Bridge signat, historial deduplicat, reportes, silenciaments, filtre i límit de 10 missatges/60 s per node i usuari |
| Esdeveniments | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE amb `since` i batec, publicació a pares i reintents (3 intents, 300 ms → 1,5 s → 5 s) |
| Resiliència | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Salut, batec, mètriques p50/p95, revocació immediata de claus i pla d'incident |
| Conformitat | `python tools/federation_conformance.py <url> [--json]` | Verifica un node tercer; surt 1 si hi ha fallades crítiques/altes |

El detall del model de confiança i del transport està a [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) i [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Còpies de seguretat i migracions

- SQLite: copiar `*.db` en calent aturat (`-Kill` abans). MariaDB: `mariadb-dump` (volum `db-data`).
- Migracions: `alembic upgrade head` des de `backend/` (prod **només** Alembic, mai `create_all`). Les últimes migracions afegeixen `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports`, `chat_mutes`, la unicitat de seient (`uq_event_seat_location`) i `contest_type` en curts amb `festival_id` obligatori.
- Canvi de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detall a [DATABASE.md](DATABASE.md).

## Resolució de problemes

| Símptoma | Causa probable | Acció |
|---|---|---|
| Arrencada aborta per `SECRET_KEY` / CORS | default insegur o `*` en prod | Defineix `SECRET_KEY` i `CORS_ORIGINS` explícits |
| `401` en endpoints públics de formularis | enllaç mal generat | Revisa el token de l'enllaç; l'accés anònim no dona 401 per si sol |
| `403` gestionant festival/canal/comitè | caller sense rol | Verifica membresia i rol (`GET …/members`); l'auto-join només dona `attendee` |
| `409` en unir-s'hi | ja és membre | Usa `leave` o gestiona des de membres |
| `413` en pujar | supera 10 MB cos / 5 MB imatge / 100 MB vídeo / 10 MB pdf | Comprimeix o parteix el fitxer |
| `429` generalitzat | rate limit 100/60s per IP (o 3/300s al reset) | Espera i reintenta; revisa `TESTING=true` residual |
| WS no connecta | JWT sense `type=access` o sessió revocada/expirada | Torna a fer login; revisa `/api/auth/sessions` |
| App offline no sincronitza | cua amb fallades esgotades (`failed`, 3 intents + backoff) | Revisa errors al prompt de sync; `clear()` després de confirmar en logout |
| `403` important un bundle | `origin_domain` no permès a la política del node | Revisa `/api/federation/nodes` i torna a importar |
| `429` en xat federat | més de 10 missatges/60 s per node i usuari | Espera al `Retry-After`; en tests es desactiva amb `TESTING=true` |
| Esdeveniments SSE tallats o sense dades | token invàlid o `since` per davant del replay | Tornen a fer login i reinicien amb `since=0` (replay de 200 esdeveniments) |
| Missatges federats duplicats | reenviament del bridge | Es descarten per `message_id` a `chat_outbox`; revisa `/api/federation/chat/messages` |

## Vegeu també

- [USO.md](USO.md): arrancada i operació del sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): desplegament, ports i CI
- [SEGURIDAD.md](SEGURIDAD.md): llista d'enduriment i polítiques
- [../README.ca.md](../../README.ca.md): context global del projecte
