# Protocolo de federación Clakettes (fases 2 a 10)

[ES](../es/FEDERATION_PROTOCOL.md) · [EN](../en/FEDERATION_PROTOCOL.md) · [FR](../fr/FEDERATION_PROTOCOL.md) · [DE](../de/FEDERATION_PROTOCOL.md) · [IT](../it/FEDERATION_PROTOCOL.md) · [CA](../ca/FEDERATION_PROTOCOL.md) · [EU](../eu/FEDERATION_PROTOCOL.md) · [GL](FEDERATION_PROTOCOL.md) · [OC](../oc/FEDERATION_PROTOCOL.md)

Pasos para crear un servidor/cliente interoperable:

1. Implementar os endpoints `/api/federation/*` (ver `docs/es/FEDERATION_SCHEMA.md`).
2. Configurar TLS obrigatorio entre nodos con mTLS mutuo (Fase 2): certificado emitido por unha CA de confianza, sen self-signed en produción.
3. Rexistrar o nodo como confiado en cada par co que fará peering (`trusted_nodes`: dominio, pegada SHA-256 do PEM do certificado, CN do subject, capacidades, políticas). `POST /api/federation/nodes` persiste `import_only`, `disable_chat` e `disable_search` xunto con `consent_required` e `minimize_data`.
4. Expor o manifesto en `GET /api/federation/manifest` con `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` e `certificate_chain`. O manifesto asígnase en RSA-SHA256 (PKCS#1 v1.5) coa clave privada do certificado TLS do nodo; o par valida a sinatura co PEM de `certificate_chain` e comproba `expires_at` (24 h).
5. Expor a clave pública en `GET /api/federation/.well-known/jwks.json` para que os pares validen os tokens de federación.
6. Validar tokens de pares vía JWKS: un nodo remoto que chama a un endpoint protexido debe presentar un Bearer JWT asinado (RS256) cuxo `iss` sexa o seu dominio e cuxa sinatura se valide contra o seu JWKS. `GET /api/federation/whoami` devolve a identidade do par só cando ese JWT valida (401 en caso contrario).
7. Resolver usuarios remotos vía `GET /api/federation/users/{ref}` e `GET /api/federation/.well-known/webfinger` (ambos requiren peer mTLS verificado só cando `MTLS_REQUIRED=true`; por defecto `False`).
8. Usar Clakettes Schema v1 para o intercambio de datos.
9. Portar identidade e datos con `POST /api/federation/portability/bundles` e `/imports` (sinatura HMAC-SHA256 e checksum), migrar con `/festivals/{id}/migrate` e `/users/{ref}/migrate`, e resolver refs antigas con `GET /redirects/{ref}`.
10. Entregar chat polo bridge asinado `/api/federation/chat/bridge/{inbound,outbound,config}`; o histórico consúltase en `/api/federation/chat/messages`, con deduplicación por `message_id` e orde por `timestamp` + `message_id`. A cola durable `chat_outbox` permite transporte intercambiable (detalle en `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Propagar cambios polo bus de eventos: `GET /api/federation/events/stream` (SSE con `since` e latido), `POST /publish` e `GET /retry-queue` (3 intentos, backoff 300 ms → 1,5 s → 5 s).
12. Vixiar a saúde do peering con `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}`; `metrics` expón p50/p95, latencia, fallos e reintentos.
13. Verificar a conformidade dun nodo terceiro con `python tools/federation_conformance.py <url> [--json]` (1 se hai fallos críticos/altos).

## Motivación

O protocolo permite que nodos independentes intercambien festivais, usuarios e mensaxes sen perder identidade nin trazabilidade.

## Axustes

- `consent_required`: esixe consentimento explícito antes de federar datos dun nodo.
- `import_only`: federación unidireccional (só importar, non exportar).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: non compartir máis do necesario no peering.

## Endpoints clave

| Endpoint | Método | Descrición |
|---|---|---|
| `/api/federation/manifest` | GET | Manifesto asinado RSA-SHA256 con `expires_at` e `certificate_chain` |
| `/api/federation/directory` | GET | Directorio de nodos confiados |
| `/api/federation/nodes` | GET/POST | Políticas de allowlist/blocklist (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Identidade do par, validando o seu JWT contra o seu JWKS |
| `/api/federation/.well-known/jwks.json` | GET | Clave pública JWKS do nodo |
| `/api/federation/token` | POST | Emisión de JWT de federación (RS256) |
| `/api/federation/peers/verify` | POST | Verificación de identidade de nodo remoto (CN e PEM do certificado) |
| `/api/federation/peers/{domain}/revoke` | POST | Revogación de nodo confiado (admin) |
| `/api/federation/users/{ref}` | GET | Resolución de usuario remoto (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Informes de moderación entre nodos |
| `/api/federation/portability/bundles`, `/imports` | POST | Exportación e importación de bundles asinados |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migración de festivais e identidade de usuario (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Resolución da ref antiga tras a migración |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Bridge de chat asinado e a súa configuración |
| `/api/federation/chat/messages` | GET | Histórico federado, deduplicado e ordenado |
| `/api/chat/moderation/*` | POST/PATCH/GET | Informes, silenciamentos, filtro e límite de chat |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE con `since` e latido, publicación e reintentos |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Saúde, latido e métricas reais p50/p95 |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Revogación de claves e plan de incidentes |
