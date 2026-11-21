# Protocolo de federación Clakettes (fases 2 a 10)

Pasos para crear un servidor/cliente interoperable:

1. Implementar los endpoints `/api/federation/*` (ver `docs/es/FEDERATION_SCHEMA.md`).
2. Configurar TLS obligatorio entre nodos con mTLS mutuo (Fase 2): certificado emitido por una CA de confianza, sin self-signed en producción.
3. Registrar el nodo como confiado en cada par con el que hará peering (`trusted_nodes`: dominio, huella SHA-256 del PEM del certificado, CN del subject, capacidades, políticas). `POST /api/federation/nodes` persiste `import_only`, `disable_chat` y `disable_search` junto a `consent_required` y `minimize_data`.
4. Exponer el manifiesto en `GET /api/federation/manifest` con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` y `certificate_chain`. El manifiesto se firma en RSA-SHA256 (PKCS#1 v1.5) con la clave privada del certificado TLS del nodo; el par valida la firma con el PEM de `certificate_chain` y comprueba `expires_at` (24 h).
5. Exponer la clave pública en `GET /api/federation/.well-known/jwks.json` para que los pares validen los tokens de federación.
6. Validar tokens de pares vía JWKS: un nodo remoto que llama a un endpoint protegido debe presentar un Bearer JWT firmado (RS256) cuyo `iss` sea su dominio y cuya firma se valide contra su JWKS. `GET /api/federation/whoami` devuelve la identidad del par solo cuando ese JWT valida (401 en caso contrario).
7. Resolver usuarios remotos vía `GET /api/federation/users/{ref}` y `GET /api/federation/.well-known/webfinger` (ambos requieren peer mTLS verificado).
8. Usar Clakettes Schema v1 para el intercambio de datos.
9. Portar identidad y datos con `POST /api/federation/portability/bundles` y `/imports` (firma HMAC-SHA256 y checksum), migrar con `/festivals/{id}/migrate` y `/users/{ref}/migrate`, y resolver refs antiguas con `GET /redirects/{ref}`.
10. Entregar chat por el bridge firmado `/api/federation/chat/bridge/{inbound,outbound,config}`; el histórico se consulta en `/api/federation/chat/messages`, con deduplicación por `message_id` y orden por `timestamp` + `message_id`. La cola durable `chat_outbox` permite transporte intercambiable (detalle en `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Propagar cambios por el bus de eventos: `GET /api/federation/events/stream` (SSE con `since` y latido), `POST /publish` y `GET /retry-queue` (3 intentos, backoff 300 ms → 5 s).
12. Vigilar la salud del peering con `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}`; `metrics` expone p50/p95, latencia, fallos y reintentos.
13. Verificar la conformidad de un nodo tercero con `python tools/federation_conformance.py <url> [--json]` (1 si hay fallos críticos/altos).

## Motivación

El protocolo permite que nodos independientes intercambien festivales, usuarios y mensajes sin perder identidad ni trazabilidad.

## Ajustes

- `consent_required`: exige consentimiento explícito antes de federar datos de un nodo.
- `import_only`: federación unidireccional (solo importar, no exportar).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: no compartir más de lo necesario en peering.

## Endpoints clave

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/federation/manifest` | GET | Manifiesto firmado RSA-SHA256 con `expires_at` y `certificate_chain` |
| `/api/federation/directory` | GET | Directorio de nodos confiados |
| `/api/federation/nodes` | GET/POST | Políticas de allowlist/blocklist (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Identidad del par, validando su JWT contra su JWKS |
| `/api/federation/.well-known/jwks.json` | GET | Clave pública JWKS del nodo |
| `/api/federation/token` | POST | Emisión de JWT de federación (RS256) |
| `/api/federation/peers/verify` | POST | Verificación de identidad de nodo remoto (CN y PEM del certificado) |
| `/api/federation/peers/{domain}/revoke` | POST | Revocación de nodo confiado (admin) |
| `/api/federation/users/{ref}` | GET | Resolución de usuario remoto (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Reportes de moderación entre nodos |
| `/api/federation/portability/bundles`, `/imports` | POST | Exportación e importación de bundles firmados |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migración de festivales e identidad de usuario (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Resolución de la ref antigua tras la migración |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Bridge de chat firmado y su configuración |
| `/api/federation/chat/messages` | GET | Historial federado, deduplicado y ordenado |
| `/api/chat/moderation/*` | POST/PATCH/GET | Reportes, mutes, filtro y límite de chat |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE con `since` y latido, publicación y reintentos |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Salud, latido y métricas reales p50/p95 |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Revocación de claves y plan de incidentes |
