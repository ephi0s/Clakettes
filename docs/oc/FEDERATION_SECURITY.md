# Seguretat federada (fasas 2 a 10)

## Modèl de fisança

- Identitat de nose = domeni + certificat TLS X.509.
- Peering mutu via mTLS amb certificats de domeni (CA publica o privada): se validan lo CN del subjècte e lo PEM del certificat, non solament lo domeni declarat.
- TLS obligatòri entre noses; validacion estricta dels certificats dins lo peering (sens self-signed en prod).
- L'identitat es servada dins `trusted_nodes` (domeni, emprenta SHA-256 del PEM, CN del subjècte, CA emetritz, validitat, politicas).
- Cada nose expausa un manifest signat en RSA-SHA256 amb la clau privada de son certificat TLS; los pares validan la signatura contra lo PEM de `certificate_chain` e verifican `expires_at` (24 h).

## Rotacion e revocacion

- La rotacion se gestiona per renovacion del certificat: en se renovant, se met a jorn l'emprenta dins `trusted_nodes` sens rompre lo peering (la racina de fisança es la CA, non lo certificat individual).
- Un nose compromés es revocat en marcant `allowed = false` dins `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, solament admin) o en invalidant son certificat dins la CRL de la CA.
- La revocacion administrativa es immediata: la manhada mTLS seguenta fracassa.
- La revocacion d'urgéncia se gestiona tanben dempuèi `POST /api/federation/resilience/keys/revoke` (solament admin, amb motiv) e se consulta a `GET /keys/revoked`; `GET /incident-plan` descriu las 8 estapas de responsa en cas de compromission.

## Contròls d'accès

- Rate limiting global: 100 req/60s per IP (cubèl `middleware:`); `/dav` a 600/60s.
- Rate limiting per endpoint sensible: login 5/300s per IP, refresh 20/60s per IP, federacion 60/60s per IP; chat 10 messatges/60 s per nose e usagi (desactivat amb `TESTING=true`).
- Los endpoints de federacion qu'exausan de donadas d'usagi (`/users/{ref}`, `/.well-known/webfinger`) demandan un peer mTLS verificat.
- `GET /api/federation/whoami` exegís un Bearer JWT de federacion (RS256) validat contra lo JWKS de l'emeteire; sens token valid respon 401.
- Los endpoints d'administracion dels noses (`/nodes`, `/peers/{domain}/revoke`, migracions de portabilitat, `events/publish`, `events/retry-queue`, `keys/revoke`) demandan lo ròtle admin; la moderacion de canal exegís admin o moderator del canal.
- Lo flux SSE dels eveniments exegís un token d'accès valid dins `?token=`; l'eveniment se consulta amb `since` e lo replay es limitat als darrièrs 200 eveniments.

## Integritat, chat e eveniments

- Los bundles de portabilitat portan `signature` HMAC-SHA256 amb `SECRET_KEY` e `checksum` SHA-256 sus lo payload canonic; l'importacion refusa los bundles invalids (400) e las originas non autorizadas (403), e aplica `minimize_data` per ometre de camps sensibles.
- Lo bridge de chat signa en RS256 los camps canonics de l'envelopa (`message_id`, `node_origin`, `content`, `timestamp`, …); lo receptor telecarga la clau publica del par e verifica la signatura abans de servar. La taula `chat_outbox` impausa l'unicitat per `message_id`, de manièra qu'un reenviament es respongut coma `duplicate`; l'istoric es ordenat per `timestamp` + `message_id`.
- Lo transpòrt es intercambiable mejans la còda durabla (`DurableQueueBackend` sus `chat_outbox`), amb reensaji e backoff; la decision de broker (NATS JetStream, WebSocket de riba e fallback mononose) es dins `docs/es/FEDERATION_CHAT_BROKER.md`.
- La moderacion cobrís los rapòrts, amagar/escafar messatges, silencis amb durada e domeni per canal o nose, filtre de mots blocats e `disable_chat` per nose (`POST /api/chat/moderation/*`). Se complèta amb la limita de 10 messatges/60 s per nose e usagi.
- Los eveniments als pares son signats amb HMAC-SHA256 dins lo cap `X-Clakettes-Signature` e propagats solament als noses autorizats; los fracasses intran dins la còda de reensajos (3 ensajos, backoff 300 ms → 1,5 s → 5 s) visibla a `/api/federation/events/retry-queue`.
- Las politicas `disable_chat` e `disable_search` son evaluadas abans d'aplicar los eveniments o messatges entrants, e `import_only` restrinh l'exportacion; `GET /api/federation/resilience/metrics` expausa p50/p95, laténcia, fracasses e reensajos per vigilar lo peering.

## Ajustaments

- `allowlist`/`blocklist` per nose (`node_policies` / `trusted_nodes`).
- Rate limiting e anti-flood a la riba de la federacion.
- Propagacion dels rapòrts de moderacion entre noses.
- `consent_required`: demanda un consentiment explicit abans de federar las donadas d'un nose.
- `import_only`: federacion unidireccionala (solament importar, non exportar).
- `disable_chat`/`disable_search`: permission per foncion per nose.
- `minimize_data`: non partejar mai que lo necessari dins lo peering.

## Referéncias

- `docs/es/MODELO_CONFIANZA_NODOS.md` — concepcion detalhada del modèl de fisança e taulas de basa de donadas.
- `docs/es/FEDERATION_PROTOCOL.md` — estapas d'interoperabilitat nose-servidor/client (fasas 2 a 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entitats e endpoints de federacion.
- `docs/es/FEDERATION_CHAT_BROKER.md` — decision de broker pel chat e los eveniments entre noses.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — menaças per nose e riscs residuals.
