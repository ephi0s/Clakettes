# Protocole de fédération Clakettes (phases 2 à 10)

Étapes pour créer un serveur/client interopérable :

1. Implémentez les endpoints `/api/federation/*` (voir `docs/es/FEDERATION_SCHEMA.md`).
2. Configurez le TLS obligatoire entre nœuds avec mTLS mutuel (Phase 2) : certificat émis par une CA de confiance, pas de self-signed en production.
3. Enregistrez le nœud comme fiable chez chaque pair avec lequel il fera du peering (`trusted_nodes` : domaine, empreinte SHA-256 du PEM du certificat, CN du sujet, capacités, politiques). `POST /api/federation/nodes` persiste `import_only`, `disable_chat` et `disable_search` ainsi que `consent_required` et `minimize_data`.
4. Exposez le manifeste sur `GET /api/federation/manifest` avec `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` et `certificate_chain`. Le manifeste est signé en RSA-SHA256 (PKCS#1 v1.5) avec la clé privée du certificat TLS du nœud ; le pair valide la signature avec le PEM de `certificate_chain` et vérifie `expires_at` (24 h).
5. Exposez la clé publique sur `GET /api/federation/.well-known/jwks.json` pour que les pairs valident les tokens de fédération.
6. Validez les tokens des pairs via JWKS : un nœud distant appelant un endpoint protégé doit présenter un Bearer JWT signé (RS256) dont l'`iss` est son domaine et dont la signature se valide contre son JWKS. `GET /api/federation/whoami` renvoie l'identité du pair seulement quand ce JWT se valide (401 sinon).
7. Résolvez les utilisateurs distants via `GET /api/federation/users/{ref}` et `GET /api/federation/.well-known/webfinger` (tous deux exigent un peer mTLS vérifié).
8. Utilisez Clakettes Schema v1 pour l'échange de données.
9. Portez l'identité et les données avec `POST /api/federation/portability/bundles` et `/imports`, migrez avec `/festivals/{id}/migrate` et `/users/{ref}/migrate`, et résolvez les anciennes refs avec `GET /redirects/{ref}`.
10. Livrez le chat par le bridge signé `/api/federation/chat/bridge/{inbound,outbound,config}` ; l'historique se consulte sur `/api/federation/chat/messages`, avec déduplication par `message_id` et tri par `timestamp` + `message_id`. La file durable `chat_outbox` permet un transport interchangeable (détail dans `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Propagez les changements par le bus d'événements : `GET /api/federation/events/stream` (SSE avec `since` et battement), `POST /publish` et `GET /retry-queue` (3 tentatives, backoff 300 ms → 5 s).
12. Surveillez la santé du peering avec `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}` ; `metrics` expose p50/p95, latence, échecs et relances.
13. Vérifiez la conformité d'un nœud tiers avec `python tools/federation_conformance.py <url> [--json]` (1 en cas d'échecs critiques/élevés).

## Motivation

Le protocole permet à des nœuds indépendants d'échanger festivals, utilisateurs et messages sans perdre d'identité ni de traçabilité.

## Réglages

- `consent_required` : exige un consentement explicite avant de fédérer les données d'un nœud.
- `import_only` : fédération unidirectionnelle (import seulement, pas d'export).
- `disable_chat`/`disable_search` : permissions par fonction par nœud.
- `minimize_data` : ne partagez pas plus que nécessaire dans le peering.

## Endpoints clés

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/federation/manifest` | GET | Manifeste signé RSA-SHA256 avec `expires_at` et `certificate_chain` |
| `/api/federation/directory` | GET | Répertoire des nœuds fiables |
| `/api/federation/nodes` | GET/POST | Politiques allowlist/blocklist (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Identité du pair, en validant son JWT contre son JWKS |
| `/api/federation/.well-known/jwks.json` | GET | Clé publique JWKS du nœud |
| `/api/federation/token` | POST | Émission de JWT de fédération (RS256) |
| `/api/federation/peers/verify` | POST | Vérification de l'identité d'un nœud distant (CN et PEM du certificat) |
| `/api/federation/peers/{domain}/revoke` | POST | Révocation d'un nœud fiable (admin) |
| `/api/federation/users/{ref}` | GET | Résolution d'utilisateur distant (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Signalements de modération entre nœuds |
| `/api/federation/portability/bundles`, `/imports` | POST | Export et import de bundles signés |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migration des festivals et de l'identité utilisateur (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Résolution de l'ancienne ref après migration |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Bridge de chat signé et sa configuration |
| `/api/federation/chat/messages` | GET | Historique fédéré, dédupliqué et trié |
| `/api/chat/moderation/*` | POST/PATCH/GET | Signalements, mutes, filtre et limite de chat |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE avec `since` et battement, publication et relances |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Santé, battement et métriques réelles p50/p95 |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Révocation de clés et plan d'incident |
