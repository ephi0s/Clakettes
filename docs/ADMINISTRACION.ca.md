# Administració — Clakettes

Guia per a qui opera un desplegament. Infraestructura a [INFRAESTRUCTURA.ca.md](INFRAESTRUCTURA.ca.md), checklist de producció a [SEGURIDAD.ca.md](SEGURIDAD.ca.md).

## Compte inicial

En no-prod (`APP_ENV != production`) l'arrencada crea `admin` / `setup` (`admin@clakettes.com`, rol admin) si no existeix; en prod **no es crea**. Canvia la contrasenya en entrar. L'alta utilitza `POST /api/users/login` (JWT 30 min + refresh 30 d, llista i revoca sessions a `/api/auth/sessions`).

## Endpoints `/api/admin` (solo rol admin, 403 en otro caso)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Secrets i rotació

- `SECRET_KEY`: obligatòria en prod (l'arrencada falla amb la d'exemple i indica `secrets.token_urlsafe(64)`). Rotar-la invalida tots els JWT i refresh tokens: fes-ho en finestra de manteniment i avisa (tots refan login).
- `CORS_ORIGINS`: orígens explícits en prod; `*` + credencials està prohibit i bloqueja l'arrencada.
- Darrere de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Backups i migracions

- SQLite: copiar `*.db` en calent aturat (`-Kill` abans). MariaDB: `mariadb-dump` (volum `db-data`).
- Migracions: `alembic upgrade head` des de `backend/` (18 versions; prod **només** Alembic, mai `create_all`).
- Canvi de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detall a [DATABASE.ca.md](DATABASE.ca.md).

## Troubleshooting

| Síntoma | Causa probable | Acción |
|---|---|---|
| Arranque aborta por `SECRET_KEY` / CORS | default inseguro o `*` en prod | Define `SECRET_KEY` y `CORS_ORIGINS` explícitos |
| `401` en endpoints públicos de formularios | enlace mal generado | Revisa el token del link; el acceso anónimo no da 401 por sí solo |
| `403` gestionando festival/canal/comité | caller sin rol | Verifica membresía y rol (`GET …/members`); el auto-join solo da `attendee` |
| `409` al unirse | ya es miembro | Usa `leave` o gestiona desde miembros |
| `413` subiendo | supera 10 MB cuerpo / 5 MB imagen / 100 MB vídeo / 10 MB pdf | Comprime o parte el archivo |
| `429` generalizado | rate limit 100/60s por IP (o 3/300s en reset) | Espera y reintenta; revisa `TESTING=true` residual |
| WS no conecta | JWT sin `type=access` o sesión revocada/expirada | Re-login; revisa `/api/auth/sessions` |
| App offline no sincroniza | cola con fallos agotados (`failed`, 3 intentos + backoff) | Revisa errores en el prompt de sync; `clear()` tras confirmar en logout |

## Vegeu també

- [USO.ca.md](USO.ca.md): arrencada i operació del sistema
- [INFRAESTRUCTURA.ca.md](INFRAESTRUCTURA.ca.md): desplegament, ports i CI
- [SEGURIDAD.ca.md](SEGURIDAD.ca.md): checklist d'enduriment i polítiques
- [../README.ca.md](../README.ca.md): context global del projecte
