# Seguridad federada (fases 2 a 10)

## Modelo de confianza

- Identidad de nodo = dominio + certificado TLS X.509.
- Peering mutuo vía mTLS con certificados de dominio (CA pública o privada): se validan el CN del subject y el PEM del certificado, no solo el dominio declarado.
- TLS obligatorio entre nodos; validación estricta de certificados en peering (sin self-signed en prod).
- La identidad se almacena en `trusted_nodes` (dominio, huella SHA-256 del PEM, CN del subject, CA emisora, vigencia, políticas).
- Cada nodo expone un manifiesto firmado en RSA-SHA256 con la clave privada de su certificado TLS; los pares validan la firma contra el PEM de `certificate_chain` y comprueban `expires_at` (24 h).

## Rotación y revocación

- La rotación se gestiona por renovación del certificado: al renovarse, se actualiza la huella en `trusted_nodes` sin romper el peering (la raíz de confianza es la CA, no el cert individual).
- Un nodo comprometido se revoca marcando `allowed = false` en `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, solo admin) o invalidando su certificado en la CRL de la CA.
- La revocación administrativa es inmediata: el siguiente handshake mTLS falla.
- La revocación de emergencia se gestiona también desde `POST /api/federation/resilience/keys/revoke` (solo admin, con motivo) y se consulta en `GET /keys/revoked`; `GET /incident-plan` describe los 8 pasos de respuesta ante compromiso.

## Controles de acceso

- Rate limiting global: 100 req/60s por IP (bucket `middleware:`); `/dav` tiene 600/60s.
- Rate limiting por endpoint sensible: login 5/300s por IP, refresh 20/60s por IP, federation 60/60s por IP; chat 10 mensajes/60 s por nodo y usuario (desactivado con `TESTING=true`).
- Endpoints de federación que exponen datos de usuario (`/users/{ref}`, `/.well-known/webfinger`) requieren peer mTLS verificado.
- `GET /api/federation/whoami` exige un Bearer JWT de federación (RS256) validado contra el JWKS del emisor; sin token válido responde 401.
- Endpoints de administración de nodos (`/nodes`, `/peers/{domain}/revoke`, migraciones de portabilidad, `events/publish`, `events/retry-queue`, `keys/revoke`) requieren rol admin; la moderación de canal exige admin o moderator del canal.
- El stream SSE de eventos exige un token de acceso válido en `?token=`; el evento se consulta con `since` y el replay se limita a los últimos 200 eventos.

## Integridad, chat y eventos

- Los bundles de portabilidad llevan `signature` HMAC-SHA256 con `SECRET_KEY` y `checksum` SHA-256 sobre el payload canónico; la importación rechaza bundles inválidos (400) y orígenes no permitidos (403), y aplica `minimize_data` para omitir campos sensibles.
- El bridge de chat firma en RS256 los campos canónicos del sobre (`message_id`, `node_origin`, `content`, `timestamp`, …); el receptor descarga la clave pública del par y verifica la firma antes de persistir. La tabla `chat_outbox` impone unicidad por `message_id`, de modo que un reenvío se responde como `duplicate`; el historial se ordena por `timestamp` + `message_id`.
- El transporte es intercambiable mediante la cola durable (`DurableQueueBackend` sobre `chat_outbox`), con reintento y backoff; la decisión de broker (NATS JetStream, WebSocket de borde y fallback mononodo) está en `docs/es/FEDERATION_CHAT_BROKER.md`.
- La moderación cubre reportes, ocultar/borrar mensajes, mutes con vigencia y ámbito por canal o nodo, filtro de palabras bloqueadas y `disable_chat` por nodo (`POST /api/chat/moderation/*`). Se complementa con el límite de 10 mensajes/60 s por nodo y usuario.
- Los eventos a pares se firman con HMAC-SHA256 en la cabecera `X-Clakettes-Signature` y se propagan solo a nodos permitidos; los fallos entran en la cola de reintentos (3 intentos, backoff 300 ms → 1,5 s → 5 s) visible en `/api/federation/events/retry-queue`.
- Las políticas `disable_chat` y `disable_search` se evalúan antes de aplicar eventos o mensajes entrantes, y `import_only` restringe la exportación; `GET /api/federation/resilience/metrics` expone p50/p95, latencia, fallos y reintentos para vigilar el peering.

## Ajustes

- `allowlist`/`blocklist` por nodo (`node_policies` / `trusted_nodes`).
- Rate limiting y anti-flood en el borde de federación.
- Propagación de reportes de moderación entre nodos.
- `consent_required`: exige consentimiento explícito antes de federar datos de un nodo.
- `import_only`: federación unidireccional (solo importar, no exportar).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: no compartir más de lo necesario en peering.

## Referencias

- `docs/es/MODELO_CONFIANZA_NODOS.md` — diseño detallado del modelo de confianza y tablas de base de datos.
- `docs/es/FEDERATION_PROTOCOL.md` — pasos de interoperabilidad nodo-servidor/cliente (fases 2 a 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entidades y endpoints de federación.
- `docs/es/FEDERATION_CHAT_BROKER.md` — decisión de broker para chat y eventos entre nodos.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — amenazas por nodo y riesgos residuales.
