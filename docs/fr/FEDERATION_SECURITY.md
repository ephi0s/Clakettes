# Sécurité fédérée (phases 2 à 10)

[ES](../es/FEDERATION_SECURITY.md) · [EN](../en/FEDERATION_SECURITY.md) · [FR](FEDERATION_SECURITY.md) · [DE](../de/FEDERATION_SECURITY.md) · [IT](../it/FEDERATION_SECURITY.md) · [CA](../ca/FEDERATION_SECURITY.md) · [EU](../eu/FEDERATION_SECURITY.md) · [GL](../gl/FEDERATION_SECURITY.md) · [OC](../oc/FEDERATION_SECURITY.md)

## Modèle de confiance

- Identité de nœud = domaine + certificat TLS X.509.
- Peering mutuel via mTLS avec certificats de domaine (CA publique ou privée) : le CN du sujet et le PEM du certificat sont validés, pas seulement le domaine déclaré.
- TLS obligatoire entre nœuds ; validation stricte des certificats en peering (pas de self-signed en prod).
- L'identité est stockée dans `trusted_nodes` (domaine, empreinte SHA-256 du PEM, CN du sujet, CA émettrice, validité, politiques).
- Chaque nœud expose un manifeste signé en RSA-SHA256 avec la clé privée de son certificat TLS ; les pairs valident la signature contre le PEM de `certificate_chain` et vérifient `expires_at` (24 h).

## Rotation et révocation

- La rotation se gère par renouvellement du certificat : lors du renouvellement, l'empreinte dans `trusted_nodes` est mise à jour sans rompre le peering (la racine de confiance est la CA, pas le certificat individuel).
- Un nœud compromis est révoqué en marquant `allowed = false` dans `trusted_nodes` (`POST /api/federation/peers/{domain}/revoke`, admin seulement) ou en invalidant son certificat dans la CRL de la CA.
- La révocation administrative est immédiate : le prochain handshake mTLS échoue.
- La révocation d'urgence se gère aussi depuis `POST /api/federation/resilience/keys/revoke` (admin seulement, avec motif) et se consulte sur `GET /keys/revoked` ; `GET /incident-plan` décrit les 8 étapes de réponse à une compromission.

## Contrôles d'accès

- Rate limiting global : 100 req/60s par IP (bucket `middleware:`) ; `/dav` a 600/60s.
- Rate limiting par endpoint sensible : login 5/300s par IP, refresh 20/60s par IP, federation 60/60s par IP ; chat 10 messages/60 s par nœud et utilisateur (désactivé avec `TESTING=true`).
- Les endpoints de fédération exposant des données utilisateur (`/users/{ref}`, `/.well-known/webfinger`) exigent un peer mTLS vérifié.
- `GET /api/federation/whoami` exige un Bearer JWT de fédération (RS256) validé contre le JWKS de l'émetteur ; sans token valide, il répond 401.
- Les endpoints d'administration de nœuds (`/nodes`, `/peers/{domain}/revoke`, migrations de portabilité, `events/publish`, `events/retry-queue`, `keys/revoke`) exigent le rôle admin ; la modération de canal exige admin ou modérateur du canal.
- Le flux SSE d'événements exige un token d'accès valide dans `?token=` ; l'événement se consulte avec `since` et le replay est limité aux 200 derniers événements.

## Intégrité, chat et événements

- Les bundles de portabilité portent une `signature` HMAC-SHA256 avec `SECRET_KEY` et un `checksum` SHA-256 sur le payload canonique ; l'import rejette les bundles invalides (400) et les origines non autorisées (403), et applique `minimize_data` pour omettre les champs sensibles.
- Le bridge de chat signe en RS256 les champs canoniques de l'enveloppe (`message_id`, `node_origin`, `content`, `timestamp`, …) ; le destinataire télécharge la clé publique du pair et vérifie la signature avant de persister. La table `chat_outbox` impose l'unicité par `message_id`, si bien qu'un renvoi est répondu comme `duplicate` ; l'historique est trié par `timestamp` + `message_id`.
- Le transport est interchangeable via la file durable (`DurableQueueBackend` sur `chat_outbox`), avec relance et backoff ; la décision de broker (NATS JetStream, WebSocket de bord et repli mononœud) est dans `docs/es/FEDERATION_CHAT_BROKER.md`.
- La modération couvre signalements, masquage/suppression de messages, mutes avec durée et portée par canal ou nœud, filtre de mots bloqués et `disable_chat` par nœud (`POST /api/chat/moderation/*`). Elle est complétée par la limite de 10 messages/60 s par nœud et utilisateur.
- Les événements vers les pairs sont signés avec HMAC-SHA256 dans l'en-tête `X-Clakettes-Signature` et propagés seulement aux nœuds autorisés ; les échecs entrent dans la file de relances (3 tentatives, backoff 300 ms → 1,5 s → 5 s) visible sur `/api/federation/events/retry-queue`.
- Les politiques `disable_chat` et `disable_search` sont évaluées avant d'appliquer les événements ou messages entrants, et `import_only` restreint l'export ; `GET /api/federation/resilience/metrics` expose p50/p95, latence, échecs et relances pour surveiller le peering.

## Réglages

- `allowlist`/`blocklist` par nœud (`node_policies` / `trusted_nodes`).
- Rate limiting et anti-flood au bord de la fédération.
- Propagation des signalements de modération entre nœuds.
- `consent_required` : exige un consentement explicite avant de fédérer les données d'un nœud.
- `import_only` : fédération unidirectionnelle (import seulement, pas d'export).
- `disable_chat`/`disable_search` : permissions par fonction par nœud.
- `minimize_data` : ne partagez pas plus que nécessaire dans le peering.

## Références

- `docs/es/MODELO_CONFIANZA_NODOS.md` — conception détaillée du modèle de confiance et des tables de base de données.
- `docs/es/FEDERATION_PROTOCOL.md` — étapes d'interopérabilité nœud-serveur/client (phases 2 à 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entités et endpoints de fédération.
- `docs/es/FEDERATION_CHAT_BROKER.md` — décision de broker pour le chat et les événements entre nœuds.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — menaces par nœud et risques résiduels.
