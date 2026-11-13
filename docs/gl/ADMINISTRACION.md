# Administración — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [CA](ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guía para quen opera un despliegue. Infraestrutura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de produción en [SEGURIDAD.md](SEGURIDAD.md).

## Conta inicial

En no-prod (`APP_ENV != production`) o arranque crea `admin` / `setup` (`admin@clakettes.com`, rol admin) se non existe; en prod **non se crea**. Cambia o contrasinal ao entrar. O acceso usa `POST /api/users/login` (JWT 30 min + refresh 30 d, lista e revoca sesións en `/api/auth/sessions`).

## Endpoints `/api/admin` (só rol admin, 403 noutro caso)

| Método e ruta | Efecto |
|---------------|--------|
| `GET /api/admin/stats` | Contadores: usuarios, festivais, curtos, mensaxes, activos |
| `GET /api/admin/tables` | Táboas (menos `alembic_version`) con número de filas |
| `GET /api/admin/audit-log` | Traza de auditoría (filtros `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 se `confirm` non é `yes`, 403 se o contrasinal non verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Secretos e rotación

- `SECRET_KEY`: obrigatorio en prod (o arranque falla coa chave de exemplo e indica `secrets.token_urlsafe(64)`). Rotala invalida todos os JWT e refresh tokens: fáselo nunha xanela de manutencion e avisa (todos volven a facer login).
- `CORS_ORIGINS`: oríxenes explícitas en prod; `*` con credenciais está prohibitido e bloquea o arranque.
- Detrás de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Copias de seguridade e migracións

- SQLite: copiar `*.db` parado (`-Kill` antes). MariaDB: `mariadb-dump` (volume `db-data`).
- Migracións: `alembic upgrade head` desde `backend/` (36 versións; prod **só** Alembic, nunca `create_all`).
- Cambio de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detalle en [DATABASE.md](DATABASE.md).

## Solución de problemas

| Sympto | Causa probable | Acción |
|--------|----------------|--------|
| Arranque aborta por `SECRET_KEY` / CORS | default inseguro ou `*` en prod | Define `SECRET_KEY` e `CORS_ORIGINS` explícitos |
| `401` en endpoints públicos de formularios | enlace malxo xerado | Revisa o token do enlace; o acceso anónimo non da 401 por sí solo |
| `403` xestionando festival/canle/comité | caller sen rol | Verifica membresía e rol (`GET …/members`); o auto-join só da `attendee` |
| `409` ao unirse | xa é membro | Usa `leave` ou xestiona desde membros |
| `413` subindo | supera 10 MB corpo / 5 MB imaxe / 100 MB vídeo / 10 MB pdf | Comprime ou parte o arquivo |
| `429` xeralizado | rate limit 100/60s por IP (ou 3/300s no reset) | Espera e reintenta; revisa `TESTING=true` residual |
| WS non conecta | JWT sen `type=access` ou sesión revocada/expirada | Volve a facer login; revisa `/api/auth/sessions` |
| App fora de liña non sincroniza | cola con fallos esgotados (`failed`, 3 intentos + backoff) | Revisa erros no prompt de sync; `clear()` tras confirmar no logout |

## Ver tamén

- [USO.md](USO.md): arranque e operación do sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): despliegue, portos e CI
- [SEGURIDAD.md](SEGURIDAD.md): checklist de endurecemento e políticas
- [../README.gl.md](../../README.gl.md): contexto global do proxecto