# Administratzia — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [CA](ADMINISTRACION.md) · [OC](ADMINISTRACION.md)

Guia per a qui opera un desplegament. Infraestrutura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de productiu en [SEGURIDAD.md](SEGURIDAD.md).

## Compte initial

A no-productiu (`APP_ENV != production`) l'arrancada crea `admin` / `setup` (`admin@clakettes.com`, rol admin) si no existeix; a productiu **no es crea**. Canvia la contrasenya a l'entrar. L'alta usa `POST /api/users/login` (JWT 30 min + refresh 30 d, llista i revoca sessions a `/api/auth/sessions`).

## Endpoints `/api/admin` (sol rol admin, 403 en altre cas)

| Metode i ruta | Efecte |
|---------------|--------|
| `GET /api/admin/stats` | Comptadors: usagis, festivals, curts, missatges, actius |
| `GET /api/admin/tables` | Taules (excepte `alembic_version`) amb numero de files |
| `GET /api/admin/audit-log` | Traccia d'auditoria (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contrasenya no verifica; limit propi 3/300s (429, omissio amb `TESTING=true`) |

## Secrets e rotacio

- `SECRET_KEY`: obligatori a prod (l'arrancada falla amb l'exemple e indica `secrets.token_urlsafe(64)`). Rotarla invalida tots els JWT i refresh tokens: fes-ho en una finestra de manteniment i avisa (tots tornen a fer login).
- `CORS_ORIGINS`: orígens explicitos a prod; `*` + credencials esta prohibit i bloqueja l'arrancada.
- Detras de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Copies de seguretat e migracions

- SQLite: copiar `*.db` en calent aturat (`-Kill` abans). MariaDB: `mariadb-dump` (volum `db-data`).
- Migracions: `alembic upgrade head` des de `backend/` (36 versions; prod **solament** Alembic, mai `create_all`).
- Canvi de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detall a [DATABASE.md](DATABASE.md).

## Solucio de problemes

| Sympto | Causa probable | Accio |
|--------|----------------|-------|
| Arrancada aborta per `SECRET_KEY` / CORS | default insegur o `*` a prod | Defineix `SECRET_KEY` i `CORS_ORIGINS` explicit |
| `401` en endpoints public de formulari | enlace malxo generat | Revisa el token del enllac; l'accés anonima no dona 401 per si sol |
| `403` gestionant festival/canal/comitat | cridor sense rol | Verifica membresia i rol (`GET …/members`); l'auto-join només dona `attendee` |
| `409` al unir-se | ja es membre | Usa `leave` o gestionia des de membres |
| `413` pujant | supera 10 MB cos / 5 MB imatge / 100 MB video / 10 MB pdf | Comprimeix o divideix l'arxiu |
| `429` generalitzat | rate limit 100/60s per IP (ou 3/300s al reset) | Espera e reintenta; revisa `TESTING=true` residual |
| WS non connecta | JWT sense `type=access` o sessio revocada/expirada | Torna a fer login; revisa `/api/auth/sessions` |
| App fora de liña non sincroniza | cola amb fallos esgotats (`failed`, 3 intents + backoff) | Revisa errors en el prompt de sinc; `clear()` després de confirmar al logout |

## Veure ancaus

- [USO.md](USO.md): arrancada e operacio del sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): desplegament, ports e CI
- [SEGURIDAD.md](SEGURIDAD.md): checklist d'enduriment e politicas
- [../README.oc.md](../../README.oc.md): contexto global del projècte