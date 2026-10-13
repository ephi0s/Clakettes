# Administración — Clakettes

Guía para quien opera un despliegue. Infraestructura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de producción en [SEGURIDAD.md](SEGURIDAD.md).

## Cuenta inicial

En no-prod (`APP_ENV != production`) el arranque crea `admin` / `setup` (`admin@clakettes.com`, rol admin) si no existe; en prod **no se crea**. Cambia la contraseña al entrar. El alta usa `POST /api/users/login` (JWT 30 min + refresh 30 d, lista y revoca sesiones en `/api/auth/sessions`).

## Endpoints `/api/admin` (solo rol admin, 403 en otro caso)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Secretos y rotación

- `SECRET_KEY`: obligatoria en prod (el arranque falla con la de ejemplo e indica `secrets.token_urlsafe(64)`). Rotarla invalida todos los JWT y refresh tokens: hazlo en ventana de mantenimiento y avisa (todos re-hacen login).
- `CORS_ORIGINS`: orígenes explícitos en prod; `*` + credenciales está prohibido y bloquea el arranque.
- Detrás de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Backups y migraciones

- SQLite: copiar `*.db` en caliente parado (`-Kill` antes). MariaDB: `mariadb-dump` (volumen `db-data`).
- Migraciones: `alembic upgrade head` desde `backend/` (18 versiones; prod **solo** Alembic, nunca `create_all`).
- Cambio de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detalle en [DATABASE.md](DATABASE.md).

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

## Ver también

- [USO.md](USO.md): arranque y operación del sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): despliegue, puertos y CI
- [SEGURIDAD.md](SEGURIDAD.md): checklist de endurecimiento y políticas
- [../README.md](../README.md): contexto global del proyecto
