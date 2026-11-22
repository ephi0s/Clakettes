# Seguretat federada (fases 2 a 10)

[ES](../es/FEDERATION_SECURITY.md) · [EN](../en/FEDERATION_SECURITY.md) · [FR](../fr/FEDERATION_SECURITY.md) · [DE](../de/FEDERATION_SECURITY.md) · [IT](../it/FEDERATION_SECURITY.md) · [CA](FEDERATION_SECURITY.md) · [EU](../eu/FEDERATION_SECURITY.md) · [GL](../gl/FEDERATION_SECURITY.md) · [OC](../oc/FEDERATION_SECURITY.md)

## Model de confiança

- Identitat de node = domini + certificat TLS X.509.
- Peering mutu via mTLS amb certificats de domini (CA pública o privada): es validen el CN del subject i el PEM del certificat, no només el domini declarat.
- TLS obligatori entre nodes; validació estricta de certificats en peering (sense self-signed en prod).
- La identitat es desa a `trusted_nodes` (domini, huella SHA-256 del PEM, CN del subject, CA emisora, vigència, polítiques).
- Cada node exposa un manifest signat en RSA-SHA256 amb la clau privada del seu certificat TLS; els pares validen la signatura contra el PEM de `certificate_chain` i comproven `expires_at` (24 h).

## Rotació i revocació

- La rotació es gestiona per renovació del certificat: en renovar-se, s'actualitza la huella a `trusted_nodes` sense trencar el peering (l'arrel de confiança és la CA, no el cert individual).
- Un node compromès es revoca marcant `allowed = false` a `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, només admin) o invalidant el seu certificat a la CRL de la CA.
- La revocació administrativa és immediata: el següent handshake mTLS falla.
- La revocació d'emergència es gestiona també des de `POST /api/federation/resilience/keys/revoke` (només admin, amb motiu) i es consulta a `GET /keys/revoked`; `GET /incident-plan` descriu els 8 passos de resposta davant compromís.

## Controls d'accés

- Rate limiting global: 100 req/60s per IP (cubet `middleware:`); `/dav` té 600/60s.
- Rate limiting per endpoint sensible: login 5/300s per IP, refresh 20/60s per IP, federació 60/60s per IP; xat 10 missatges/60 s per node i usuari (desactivat amb `TESTING=true`).
- Els endpoints de federació que exposen dades d'usuari (`/users/{ref}`, `/.well-known/webfinger`) requereixen peer mTLS verificat.
- `GET /api/federation/whoami` exigeix un Bearer JWT de federació (RS256) validat contra el JWKS de l'emissor; sense token vàlid respon 401.
- Els endpoints d'administració de nodes (`/nodes`, `/peers/{domain}/revoke`, migracions de portabilitat, `events/publish`, `events/retry-queue`, `keys/revoke`) requereixen rol admin; la moderació de canal exigeix admin o moderator del canal.
- L'stream SSE d'esdeveniments exigeix un token d'accés vàlid a `?token=`; l'esdeveniment es consulta amb `since` i el replay es limita als últims 200 esdeveniments.

## Integritat, xat i esdeveniments

- Els bundles de portabilitat porten `signature` HMAC-SHA256 amb `SECRET_KEY` i `checksum` SHA-256 sobre el payload canònic; la importació rebutja bundles invàlids (400) i orígens no permesos (403), i aplica `minimize_data` per ometre camps sensibles.
- El bridge de xat signa en RS256 els camps canònics del sobre (`message_id`, `node_origin`, `content`, `timestamp`, …); el receptor descarrega la clau pública del pare i verifica la signatura abans de desar. La taula `chat_outbox` imposa unicitat per `message_id`, de manera que un reenviament es respon com a `duplicate`; l'historial s'ordena per `timestamp` + `message_id`.
- El transport és intercambiable mitjançant la cua durable (`DurableQueueBackend` sobre `chat_outbox`), amb reintent i backoff; la decisió de broker (NATS JetStream, WebSocket de vora i fallback mononode) està a `docs/es/FEDERATION_CHAT_BROKER.md`.
- La moderació cobreix reportes, amagar/borrar missatges, silenciaments amb vigència i àmbit per canal o node, filtre de paraules bloquejades i `disable_chat` per node (`POST /api/chat/moderation/*`). Es complementa amb el límit de 10 missatges/60 s per node i usuari.
- Els esdeveniments a pares es signen amb HMAC-SHA256 a la capçalera `X-Clakettes-Signature` i es propaguen només a nodes permesos; els fallades entren a la cua de reintents (3 intents, backoff 300 ms → 1,5 s → 5 s) visible a `/api/federation/events/retry-queue`.
- Les polítiques `disable_chat` i `disable_search` s'evaluen abans d'aplicar esdeveniments o missatges entrants, i `import_only` restringeix l'exportació; `GET /api/federation/resilience/metrics` exposa p50/p95, latència, fallades i reintents per vigilar el peering.

## Ajustos

- `allowlist`/`blocklist` per node (`node_policies` / `trusted_nodes`).
- Rate limiting i anti-flood a la vora de la federació.
- Propagació de reportes de moderació entre nodes.
- `consent_required`: exigeix consentiment explícit abans de federar dades d'un node.
- `import_only`: federació unidireccional (només importar, no exportar).
- `disable_chat`/`disable_search`: permisos per funció per node.
- `minimize_data`: no compartir més del necessari en el peering.

## Referències

- `docs/es/MODELO_CONFIANZA_NODOS.md` — disseny detallat del model de confiança i taules de base de dades.
- `docs/es/FEDERATION_PROTOCOL.md` — passos d'interoperabilitat node-servidor/client (fases 2 a 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entitats i endpoints de federació.
- `docs/es/FEDERATION_CHAT_BROKER.md` — decisió de broker per al xat i els esdeveniments entre nodes.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — amenaces per node i riscos residuals.
