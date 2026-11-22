# Seguridade federada (fases 2 a 10)

[ES](../es/FEDERATION_SECURITY.md) · [EN](../en/FEDERATION_SECURITY.md) · [FR](../fr/FEDERATION_SECURITY.md) · [DE](../de/FEDERATION_SECURITY.md) · [IT](../it/FEDERATION_SECURITY.md) · [CA](../ca/FEDERATION_SECURITY.md) · [EU](../eu/FEDERATION_SECURITY.md) · [GL](FEDERATION_SECURITY.md) · [OC](../oc/FEDERATION_SECURITY.md)

## Modelo de confianza

- Identidade de nodo = dominio + certificado TLS X.509.
- Peering mutuo vía mTLS con certificados de dominio (CA pública ou privada): validanse o CN do subject e o PEM do certificado, non só o dominio declarado.
- TLS obrigatorio entre nodos; validación estrita de certificados no peering (sen self-signed en prod).
- A identidade almacénase en `trusted_nodes` (dominio, pegada SHA-256 do PEM, CN do subject, CA emisora, vixencia, políticas).
- Cada nodo expón un manifesto asinado en RSA-SHA256 coa clave privada do seu certificado TLS; os pares validan a sinatura contra o PEM de `certificate_chain` e comproban `expires_at` (24 h).

## Rotación e revogación

- A rotación xestiónase por renovación do certificado: ao renovarse, actualízase a pegada en `trusted_nodes` sen romper o peering (a raíz de confianza é a CA, non o certificado individual).
- Un nodo comprometido revógase marcando `allowed = false` en `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, só admin) ou invalidando o seu certificado na CRL da CA.
- A revogación administrativa é inmediata: o seguinte handshake mTLS falla.
- A revogación de emerxencia xestiónase tamén desde `POST /api/federation/resilience/keys/revoke` (só admin, con motivo) e consúltase en `GET /keys/revoked`; `GET /incident-plan` describe os 8 pasos de resposta ante compromiso.

## Controis de acceso

- Rate limiting global: 100 req/60s por IP (bucket `middleware:`); `/dav` ten 600/60s.
- Rate limiting por endpoint sensible: login 5/300s por IP, refresh 20/60s por IP, federación 60/60s por IP; chat 10 mensaxes/60 s por nodo e usuario (desactivado con `TESTING=true`).
- Os endpoints de federación que expoñen datos de usuario (`/users/{ref}`, `/.well-known/webfinger`) requiren peer mTLS verificado.
- `GET /api/federation/whoami` esixe un Bearer JWT de federación (RS256) validado contra o JWKS do emisor; sen token válido responde 401.
- Os endpoints de administración de nodos (`/nodes`, `/peers/{domain}/revoke`, migracións de portabilidade, `events/publish`, `events/retry-queue`, `keys/revoke`) requiren rol admin; a moderación de canal esixe admin ou moderator do canal.
- O stream SSE de eventos esixe un token de acceso válido en `?token=`; o evento consúltase con `since` e o replay limítase aos últimos 200 eventos.

## Integridade, chat e eventos

- Os bundles de portabilidade levan `signature` HMAC-SHA256 con `SECRET_KEY` e `checksum` SHA-256 sobre o payload canónico; a importación rexeita bundles inválidos (400) e orixes non permitidos (403), e aplica `minimize_data` para omitir campos sensibles.
- O bridge de chat asina en RS256 os campos canónicos do sobre (`message_id`, `node_origin`, `content`, `timestamp`, …); o receptor descarga a clave pública do par e verifica a sinatura antes de persistir. A táboa `chat_outbox` impón unicidade por `message_id`, de modo que un reenvío respóndese como `duplicate`; o histórico ordénase por `timestamp` + `message_id`.
- O transporte é intercambiable mediante a cola durable (`DurableQueueBackend` sobre `chat_outbox`), con reintento e backoff; a decisión de broker (NATS JetStream, WebSocket de borde e fallback mononodo) está en `docs/es/FEDERATION_CHAT_BROKER.md`.
- A moderación cobre informes, ocultar/borrar mensaxes, silenciamentos con vixencia e ámbito por canal ou nodo, filtro de palabras bloqueadas e `disable_chat` por nodo (`POST /api/chat/moderation/*`). Complétase co límite de 10 mensaxes/60 s por nodo e usuario.
- Os eventos a pares asígnanse con HMAC-SHA256 na cabeceira `X-Clakettes-Signature` e propáganse só a nodos permitidos; os fallos entran na cola de reintentos (3 intentos, backoff 300 ms → 1,5 s → 5 s) visible en `/api/federation/events/retry-queue`.
- As políticas `disable_chat` e `disable_search` avalíanse antes de aplicar eventos ou mensaxes entrantes, e `import_only` restrinxe a exportación; `GET /api/federation/resilience/metrics` expón p50/p95, latencia, fallos e reintentos para vixiar o peering.

## Axustes

- `allowlist`/`blocklist` por nodo (`node_policies` / `trusted_nodes`).
- Rate limiting e anti-flood no borde de federación.
- Propagación de informes de moderación entre nodos.
- `consent_required`: esixe consentimento explícito antes de federar datos dun nodo.
- `import_only`: federación unidireccional (só importar, non exportar).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: non compartir máis do necesario no peering.

## Referencias

- `docs/es/MODELO_CONFIANZA_NODOS.md` — deseño detallado do modelo de confianza e táboas de base de datos.
- `docs/es/FEDERATION_PROTOCOL.md` — pasos de interoperabilidade nodo-servidor/cliente (fases 2 a 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entidades e endpoints de federación.
- `docs/es/FEDERATION_CHAT_BROKER.md` — decisión de broker para o chat e os eventos entre nodos.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — ameazas por nodo e riscos residuais.
