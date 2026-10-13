# Administración — Clakettes

[ES](ADMINISTRACION.md) · [EN](ADMINISTRACION.en.md) · [FR](ADMINISTRACION.fr.md) · [DE](ADMINISTRACION.de.md) · [IT](ADMINISTRACION.it.md) · [CA](ADMINISTRACION.ca.md) · [EU](ADMINISTRACION.eu.md) · [GL](ADMINISTRACION.gl.md) · [OC](ADMINISTRACION.oc.md)

Guía para quen opera un despregamento. Infraestrutura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.gl.md), lista de comprobación de produción en [SEGURIDAD.md](SEGURIDAD.gl.md).

## Conta inicial

En non-prod (`APP_ENV != production`) o arranque crea `admin` / `setup` (`admin@clakettes.com`, rol admin) se non existe; en prod **non se crea**. Cambia o contrasinal ao entrar. A alta usa `POST /api/users/login` (JWT 30 min + refresh 30 d, lista e revoga sesións en `/api/auth/sessions`).

## Endpoints `/api/admin` (só rol admin, 403 noutro caso)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Segredos e rotación

- `SECRET_KEY`: obrigatoria en prod (o arranque falla coa de exemplo e indica `secrets.token_urlsafe(64)`). Rotala invalida todos os JWT e refresh tokens: faino en xanela de mantemento e avisa (todos volven facer login).
- `CORS_ORIGINS`: orixes explícitas en prod; `*` + credenciais está prohibido e bloquea o arranque.
- Detrás de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Copias de seguridade e migracións

- SQLite: copiar `*.db` en quente parado (`-Kill` antes). MariaDB: `mariadb-dump` (volume `db-data`).
- Migracións: `alembic upgrade head` desde `backend/` (18 versións; prod **só** Alembic, nunca `create_all`).
- Cambio de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detalle en [DATABASE.md](DATABASE.gl.md).

## Resolución de problemas

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

## Ver tamén

- [USO.md](USO.gl.md): arranque e operación do sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.gl.md): despregamento, portos e CI
- [SEGURIDAD.md](SEGURIDAD.gl.md): lista de endurecemento e políticas
- [../README.md](../README.gl.md): contexto global do proxecto
