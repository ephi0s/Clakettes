# Administración — Clakettes

[ES](ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guía para quien opera un despliegue. Infraestructura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de producción en [SEGURIDAD.md](SEGURIDAD.md).

## Cuenta inicial

En no-prod (`APP_ENV != production`) el arranque crea `admin` / `setup` (`admin@clakettes.com`, rol admin) si no existe; en prod **no se crea**. Cambia la contraseña al entrar. El alta usa `POST /api/users/login` (JWT 30 min + refresh 30 d, lista y revoca sesiones en `/api/auth/sessions`).

## Endpoints `/api/admin` (solo rol admin, 403 en otro caso)

| Método y ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivales, cortos, mensajes, activos |
| `GET /api/admin/tables` | Tablas (menos `alembic_version`) con nº de filas |
| `GET /api/admin/audit-log` | Traza de auditoría (filtros `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` no es `yes`, 403 si la contraseña no verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Secretos y rotación

- `SECRET_KEY`: obligatoria en prod (el arranque falla con la de ejemplo e indica `secrets.token_urlsafe(64)`). Rotarla invalida todos los JWT y refresh tokens: hazlo en ventana de mantenimiento y avisa (todos re-hacen login).
- `CORS_ORIGINS`: orígenes explícitos en prod; `*` + credenciales está prohibido y bloquea el arranque.
- Detrás de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Federación

| Operación | Endpoint / herramienta | Efecto |
|---|---|---|
| Nodos y políticas | `GET/POST /api/federation/nodes` | Allowlist/blocklist con `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (admin) |
| Identidad del par | `GET /api/federation/whoami` | Valida el JWT RS256 del par contra su JWKS; 401 si no es válido |
| Portabilidad | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Exportar/importar bundles firmados, migrar propiedad e identidad y resolver refs antiguas (las migraciones, solo admin) |
| Chat y moderación | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Bridge firmado, historial deduplicado, reportes, mutes, filtro y límite de 10 mensajes/60 s por nodo y usuario |
| Eventos | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE con `since` y latido, publicación a pares y reintentos (3 intentos, 300 ms → 1,5 s → 5 s) |
| Resiliencia | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Salud, latido, métricas p50/p95, revocación inmediata de claves y plan de incidente |
| Conformidad | `python tools/federation_conformance.py <url> [--json]` | Verifica un nodo tercero; sale 1 si hay fallos críticos/altos |

El detalle del modelo de confianza y del transporte está en [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) y [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Backups y migraciones

- SQLite: copiar `*.db` en caliente parado (`-Kill` antes). MariaDB: `mariadb-dump` (volumen `db-data`).
- Migraciones: `alembic upgrade head` desde `backend/` (prod **solo** Alembic, nunca `create_all`). El head actual es `d1e2f3a4b5c6` (45 revisiones); las últimas añaden `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports`, `chat_mutes`, la unicidad de asiento (`uq_event_seat_location`) y `contest_type` en cortos con `festival_id` obligatorio.
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
| `403` importando un bundle | `origin_domain` no permitido en la política del nodo | Revisa `/api/federation/nodes` y vuelve a importar |
| `429` en chat federado | más de 10 mensajes/60 s por nodo y usuario | Espera al `Retry-After`; en tests se desactiva con `TESTING=true` |
| Eventos SSE cortados o sin datos | token inválido o `since` por delante del replay | Re-hacen login y reinician con `since=0` (replay de 200 eventos) |
| Mensajes federados duplicados | reenvío del bridge | Se descartan por `message_id` en `chat_outbox`; revisa `/api/federation/chat/messages` |

## Ver también

- [USO.md](USO.md): arranque y operación del sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): despliegue, puertos y CI
- [SEGURIDAD.md](SEGURIDAD.md): checklist de endurecimiento y políticas
- [../README.md](../../README.md): contexto global del proyecto