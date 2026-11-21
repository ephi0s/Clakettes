# Clakettes Schema v1

Version initiale du schema de fédération. Il définit les entités minimales échangeables entre nœuds, versionnées via `schema_version` dans le manifeste de chaque nœud.

## Modèle de confiance (Phase 2)

L'identité d'un nœud est le tuple **(domaine, certificat TLS X.509)**. Le peering entre nœuds se fait sur mTLS mutuel : chaque nœud valide la chaîne de certificats du pair contre sa CA racine, vérifie que le domaine du certificat correspond à celui déclaré, et rejette les certificats self-signed en production. La rotation et la révocation se gèrent par renouvellement de certificat.

## Entités

- `festival` : id, name, edition, created_at, owner_node
- `user` : id, uuid, did, handle, username, node_origin
- `message` : id, sender, recipient, body, created_at, node_origin
- `moderation_report` : id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect` : old_ref, new_ref, target_domain, created_at
- `migration_audit` : entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox` : message_id (unique), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report` : reporter_id, message_id, reason, status
- `chat_mute` : user_id, channel_id, node_domain, until, reason

## Champs et contraintes

- `uuid` : identifiant stable global (UUID v4).
- `did` : identifiant décentralisé optionnel.
- `handle` : `utilisateur@instance` résoluble via WebFinger.
- `schema_version` : version du schema déclarée par le nœud dans son manifeste (actuelle : `1`).

## Endpoints de fédération

### Identité et répertoire

- `GET /api/federation/manifest` — manifeste du nœud avec `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` et `certificate_chain`. Signature RSA-SHA256 avec la clé privée du certificat TLS du nœud ; le pair valide le PEM de la chaîne et la validité de `expires_at` (24 h).
- `GET /api/federation/directory` — liste des nœuds fiables (`trusted_nodes`) avec `allowed = true`, incluant `cert_fingerprint_sha256` (empreinte du PEM), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — politiques de nœud (allowlist/blocklist) : `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Admin seulement ; les trois dernières sont persistées et appliquées dans le bridge et le bus d'événements.

### Identité fédérée et tokens (Phase 3)

- `GET /api/federation/.well-known/jwks.json` — clé publique RSA du nœud au format JWKS pour valider les tokens de fédération des pairs.
- `POST /api/federation/token` — émet un JWT de fédération signé (RS256). Exige une identité de nœud vérifiée via mTLS.
- `POST /api/federation/peers/verify` — valide l'identité d'un nœud distant (domaine + CN et PEM du certificat + manifeste signé).
- `POST /api/federation/peers/{domain}/revoke` — révoque un nœud fiable (admin).
- `GET /api/federation/whoami` — identité du pair (`iss`, `sub`, nœud) seulement si son Bearer JWT se valide contre son JWKS ; 401 sinon.

### Utilisateurs, signalements et découverte

- `GET /api/federation/users/{ref}` — résout un utilisateur par `uuid`, `did` ou `handle`. Exige un peer mTLS vérifié.
- `GET /api/federation/.well-known/webfinger` — résout `acct:user@domain`. Exige un peer mTLS vérifié.
- `POST/GET/PATCH /api/federation/reports` — signalement de modération entre nœuds.

### Portabilité (Phase 7)

- `POST /api/federation/portability/bundles` — génère un bundle utilisateur avec `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 avec `SECRET_KEY`) et `checksum` (SHA-256 du payload canonique).
- `POST /api/federation/portability/imports` — valide signature et checksum, vérifie la politique d'origine (403 si non autorisé), applique `minimize_data` et enregistre ce qui a été importé (utilisateur, courts, festivals, messages).
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — transfère la propriété du festival et ses courts à `new_owner_id` de `target_domain` avec vérification du checksum ; admin seulement.
- `POST /api/federation/portability/users/{user_ref}/migrate` — réécrit `handle` et `did` vers le domaine cible et crée la redirection ; admin seulement.
- `GET /api/federation/portability/redirects/{old_ref}` — résout l'ancienne ref (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Chat fédéré, modération et événements (Phases 8 et 9)

- `POST /api/federation/chat/bridge/inbound` — accepte une enveloppe signée (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), vérifie la signature RS256 contre la clé publique du pair, écarte les doublons par `message_id`, persiste le message et le diffuse ; `403` si le nœud n'est pas autorisé ou la signature invalide.
- `POST /api/federation/chat/bridge/outbound` — signe l'enveloppe, la met en file dans `chat_outbox` avec le sujet `clakettes.chat.node.{target_node}` et publie via le transport configuré (`DurableQueueBackend`) ; `config` renvoie transport, flux, algorithme et mappage de sujet.
- `GET /api/federation/chat/messages` — historique fédéré dédupliqué par `message_id` et trié par `timestamp` + `message_id` (filtre `node` optionnel).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — signalements, masquer/supprimer, mutes par utilisateur/canal/nœud, filtre de mots bloqués, `disable_chat` par nœud et limite de 10 messages/60 s par nœud et utilisateur (désactivée avec `TESTING=true`).
- `GET /api/federation/events/stream` — SSE avec `since`, `token`, `limit` optionnels, replay des 200 derniers événements et battement `: ping` toutes les 15 s.
- `POST /api/federation/events/publish` — publie sur un sujet dérivé de `node`/`entity` (ou `topic` explicite), signe l'envoi aux pairs avec HMAC (`X-Clakettes-Signature`) et omet les nœuds avec `disable_chat`/`disable_search` ; admin seulement.
- `GET /api/federation/events/retry-queue` — relances en attente ; 3 tentatives avec backoff 300 ms → 1,5 s → 5 s.

### Résilience (Phase 10)

- `GET /api/federation/resilience/health` — état du nœud, base de données, nombre de nœuds et latence.
- `GET /api/federation/resilience/heartbeat` — met à jour le `last_seen_at` du pair et enregistre la latence dans les métriques.
- `GET /api/federation/resilience/metrics` — requêtes, réussites, échecs, relances et latences p50/p95 globales et par nœud.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — révocation immédiate de clés par domaine avec motif, et liste des révocations ; admin seulement pour révoquer.
- `GET /api/federation/resilience/incident-plan` — plan de récupération en cas de compromission de nœud (8 étapes).

### Health et utilitaires

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — endpoints de sondage et de diagnostic.

## Ajustabilité

- Le schema est versionné ; les nœuds déclarent `schema_version` dans le manifeste.
- Les champs optionnels (`did`, `handle`) peuvent être omis si le nœud ne les prend pas en charge.
- La minimisation des données (`minimize_data`) permet d'omettre des champs sensibles dans le peering.
