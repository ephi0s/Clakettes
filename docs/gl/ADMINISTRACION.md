# Administración — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](../fr/ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guía para quen opera un despregue. Infraestrutura en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de produción en [SEGURIDAD.md](SEGURIDAD.md).

## Conta inicial

En non-prod (`APP_ENV != production`) o arranque crea `admin` / `setup` (`admin@clakettes.com`, rol admin) se non existe; en prod **non se crea**. Cambia o contrasinal ao entrar. O alta usa `POST /api/users/login` (JWT 30 min + refresh 30 d, lista e revoga sesións en `/api/auth/sessions`).

## Endpoints `/api/admin` (só rol admin, 403 noutro caso)

| Método e ruta | Efecto |
|---|---|
| `GET /api/admin/stats` | Contadores: usuarios, festivais, curtos, mensaxes, activos |
| `GET /api/admin/tables` | Táboas (menos `alembic_version`) con nº de filas |
| `GET /api/admin/audit-log` | Traza de auditoría (filtros `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 se `confirm` non é `yes`, 403 se o contrasinal non verifica; rate-limit propio 3/300s (429, bypass con `TESTING=true`) |

## Segredos e rotación

- `SECRET_KEY`: obrigatoria en prod (o arranque falla coa de exemplo e indica `secrets.token_urlsafe(64)`). Rotala invalida todos os JWT e refresh tokens: faino en xanela de mantemento e avisa (todos refan login).
- `CORS_ORIGINS`: orixes explícitos en prod; `*` + credenciais está prohibido e bloquea o arranque.
- Detrás de proxy: `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Federación

| Operación | Endpoint / ferramenta | Efecto |
|---|---|---|
| Nodos e políticas | `GET/POST /api/federation/nodes` | Allowlist/blocklist con `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (admin) |
| Identidade do par | `GET /api/federation/whoami` | Valida o JWT RS256 do par contra o seu JWKS; 401 se non é válido |
| Portabilidade | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Exportar/importar bundles asinados, migrar propiedade e identidade e resolver refs antigas (as migracións, só admin) |
| Chat e moderación | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Bridge asinado, histórico deduplicado, informes, silenciamentos, filtro e límite de 10 mensaxes/60 s por nodo e usuario |
| Eventos | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE con `since` e latido, publicación a pares e reintentos (3 intentos, 300 ms → 1,5 s → 5 s) |
| Resiliencia | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Saúde, latido, métricas p50/p95, revogación inmediata de claves e plan de incidente |
| Conformidade | `python tools/federation_conformance.py <url> [--json]` | Verifica un nodo terceiro; sae 1 se hai fallos críticos/altos |

O detalle do modelo de confianza e do transporte está en [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) e [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Backups e migracións

- SQLite: copiar `*.db` en quente parado (`-Kill` antes). MariaDB: `mariadb-dump` (volume `db-data`).
- Migracións: `alembic upgrade head` desde `backend/` (prod **só** Alembic, nunca `create_all`). O head actual é `d1e2f3a4b5c6` (45 revisións); as últimas engaden `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports`, `chat_mutes`, a unicidade de asento (`uq_event_seat_location`) e `contest_type` en curtos con `festival_id` obrigatorio.
- Cambio de motor: `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev); detalle en [DATABASE.md](DATABASE.md).

## Resolución de problemas

| Síntoma | Causa probable | Acción |
|---|---|---|
| Arranque aborta por `SECRET_KEY` / CORS | default inseguro ou `*` en prod | Define `SECRET_KEY` e `CORS_ORIGINS` explícitos |
| `401` en endpoints públicos de formularios | ligazón mal xerada | Revisa o token da ligazón; o acceso anónimo non dá 401 por si só |
| `403` xestionando festival/canal/comité | caller sen rol | Verifica membresía e rol (`GET …/members`); o auto-join só dá `attendee` |
| `409` ao unirse | xa é membro | Usa `leave` ou xestiona desde membros |
| `413` ao subir | supera 10 MB corpo / 5 MB imaxe / 100 MB vídeo / 10 MB pdf | Comprime ou parte o ficheiro |
| `429` xeneralizado | rate limit 100/60s por IP (ou 3/300s no reset) | Espera e reintenta; revisa `TESTING=true` residual |
| WS non conecta | JWT sen `type=access` ou sesión revogada/expirada | Refai login; revisa `/api/auth/sessions` |
| App offline non sincroniza | cola con fallos esgotados (`failed`, 3 intentos + backoff) | Revisa erros no prompt de sync; `clear()` tras confirmar en logout |
| `403` importando un bundle | `origin_domain` non permitido na política do nodo | Revisa `/api/federation/nodes` e volve importar |
| `429` en chat federado | máis de 10 mensaxes/60 s por nodo e usuario | Espera ao `Retry-After`; en tests desactívase con `TESTING=true` |
| Eventos SSE cortados ou sen datos | token inválido ou `since` por diante do replay | Refan login e reinician con `since=0` (replay de 200 eventos) |
| Mensaxes federados duplicados | reenvío do bridge | Descártanse por `message_id` en `chat_outbox`; revisa `/api/federation/chat/messages` |

## Ver tamén

- [USO.md](USO.md): arranque e operación do sistema
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md): despregue, portos e CI
- [SEGURIDAD.md](SEGURIDAD.md): checklist de endurecemento e políticas
- [../README.gl.md](../../README.gl.md): contexto global do proxecto
