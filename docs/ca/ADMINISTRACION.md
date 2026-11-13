# Administració — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guia per a qui opera un desplegament. Infraestructura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), llista de comprovacio de producció a [SEGURIDAD.md](SEGURIDAD.md).

## Compte inicial

A no-produccio (`APP_ENV != production`) l'arrancada crea `admin` / `setup` (`admin@clakettes.com`, rol admin) si no existeix; a producció **no es crea**. Canvia la contrasenya a l'entrar. L'alta usa `POST /api/users/login` (JWT 30 min + refresh 30 d, llista i revoca sessions a `/api/auth/sessions`).

## Endpoints `/api/admin` (sol rol admin, 403 en altre cas)

| Metode i ruta | Efecte |
|---------------|--------|
| `GET /api/admin/stats` | Comptadors: usuaris, festivals, curts, missatges, actius |
| `GET /api/admin/tables` | Taules (excepte `alembic_version`) amb numero de files |
| `GET /api/admin/audit-log` | Traccia d'auditoria (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contrasenya no verifica; limit propi 3/300s (429, omissio amb `TESTING=true`) |

## Secrets i rotacio

- `SECRET_KEY`: obligatori a prod (l'arrancada falla amb l'exemple i indica `secrets.token_urlsafe(64)`). Rotarla invalida tots els JWT i refresh tokens: fes-ho en una finestra de manteniment i avisa (tots tornen a fer login).
- `CORS_ORIGINS`: origens explicitos a prod; `*` + credencials esta prohibit i bloqueja l'arrancada.
- Detras de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Copies de seguretat i migracions

- SQLite: copiar `*.db` en calent aturat (`-Kill` abans). MariaDB: `mariadb-dump` (volum `db-data`).
- Migracions: `alembic upgrade head` des de `backend/` (36 versions; prod **sol** Alembic, mai `create_all`).
- Canvi de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detall a [DATABASE.md](DATABASE.md).

## Solucio de problemes

| Sintoma | Causa probable | Accio |
|---------|----------------|-------|
| Arrancada aborta per `SECRET_KEY` / CORS | default insegur o `*` a prod | Defineix `SECRET_KEY` i `CORS_ORIGINS` explicit |
| `401` en endpoints public de formularis | enllaç mal generat | Revisa el token del linç; l'accés anonima no dona 401 per si sol |
| `403` gestionant festival/canal/comitat | cridor sense rol | Verifica membresia i rol (`GET …/members`); l'auto-join només dona `attendee` |
| `409` al unir-se | ja es membre | Usa `leave` o gestiona des de membres |
| `413` pujant | supera 10 MB cos / 5 MB imatge / 100 MB video / 10 MB pdf | Comprimeix o divideix l'arxiu |
| `429` generalitzat | rate limit 100/60s per IP (o 3/300s al reset) | Espera i reintenta; revisa `TESTING=true` residual |
| WS no connecta | JWT sense `type=access` o sessio revocada/expirada | Torna a fer login; revisa `/api/auth/sessions` |
| App fora de linia no sincronitza | cua amb fallos agotats (`failed`, 3 intents + backoff) | Revisa errors al prompt de sinc; `clear()` despres de confirmar al logout |

## Veure també

- [USO.md](USO.md): arrancada i operacio del sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): desplegament, ports i CI
- [SEGURIDAD.md](SEGURIDAD.md): llista d'enduriment i politiques
- [../README.ca.md](../../README.ca.md): context global del projecte