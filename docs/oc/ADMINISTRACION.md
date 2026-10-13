# Administracion — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](ADMINISTRACION.md)

Guida per qui opera un desplegament. Infraestructura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de produccion en [SEGURIDAD.md](SEGURIDAD.md).

## Compte inicial

En non-prod (`APP_ENV != production`) l'aviada crea `admin` / `setup` (`admin@clakettes.com`, ròtle admin) s'existís pas; en prod **se crea pas**. Cambiatz lo senhal en intrar. L'alta utiliza `POST /api/users/login` (JWT 30 min + refresh 30 d, lista e revoca sessions en `/api/auth/sessions`).

## Endpoints `/api/admin` (sonque ròtle admin, 403 dins autre cas)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Secrets e rotacion

- `SECRET_KEY`: obligatòria en prod (l'aviada falha amb aquela d'exemple e indica `secrets.token_urlsafe(64)`). La rotar invalida totes los JWT e refresh tokens: o fatz en fenèstra de mantenença e avisatz (totes tòrnan far login).
- `CORS_ORIGINS`: originhas explicitas en prod; `*` + credencials es proïbit e blòca l'aviada.
- Darrièr proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontau.

## Salvagardas e migracions

- SQLite: copiar `*.db` a caud aturat (`-Kill` abans). MariaDB: `mariadb-dump` (volum `db-data`).
- Migracions: `alembic upgrade head` dempuèi `backend/` (18 versions; prod **sonque** Alembic, jamai `create_all`).
- Cambiament de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detalh en [DATABASE.md](DATABASE.md).

## Depanagatge

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

## Veire tanben

- [USO.md](USO.md): aviada e operacion del sistèma
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): desplegament, pòrts e CI
- [SEGURIDAD.md](SEGURIDAD.md): checklist de durciment e politicas
- [../README.oc.md](../../README.oc.md): contèxte globau del projècte
