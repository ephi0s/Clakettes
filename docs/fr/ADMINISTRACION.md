# Administration — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guide pour qui exploite un déploiement. Infrastructure dans [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de production dans [SEGURIDAD.md](SEGURIDAD.md).

## Compte initial

En non-prod (`APP_ENV != production`) le démarrage crée `admin` / `setup` (`admin@clakettes.com`, rôle admin) s'il n'existe pas ; en prod **il n'est pas créé**. Changez le mot de passe à la première connexion. La connexion utilise `POST /api/users/login` (JWT 30 min + refresh 30 d, liste et révoque les sessions sur `/api/auth/sessions`).

## Endpoints `/api/admin` (rôle admin uniquement, 403 sinon)

| Méthode et route | Effet |
|---|---|
| `GET /api/admin/stats` | Compteurs : utilisateurs, festivals, courts, messages, actifs |
| `GET /api/admin/tables` | Tables (sauf `alembic_version`) avec nombre de lignes |
| `GET /api/admin/audit-log` | Trace d'audit (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` n'est pas `yes`, 403 si le mot de passe ne vérifie pas ; rate-limit propre 3/300s (429, contournement avec `TESTING=true`) |

## Secrets et rotation

- `SECRET_KEY` : obligatoire en prod (le démarrage échoue avec la valeur d'exemple et indique `secrets.token_urlsafe(64)`). La rotation invalide tous les JWT et refresh tokens : faites-le en fenêtre de maintenance et prévenez (tous se reconnectent).
- `CORS_ORIGINS` : origines explicites en prod ; `*` + identifiants est interdit et bloque le démarrage.
- Derrière un proxy : `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Fédération

| Opération | Endpoint / outil | Effet |
|---|---|---|
| Nœuds et politiques | `GET/POST /api/federation/nodes` | Allowlist/blocklist avec `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search` (admin) |
| Identité du pair | `GET /api/federation/whoami` | Valide le JWT RS256 du pair contre son JWKS ; 401 si non valide |
| Portabilité | `POST /api/federation/portability/bundles`, `/imports`, `/festivals/{id}/migrate`, `/users/{ref}/migrate`, `GET /redirects/{ref}` | Exporter/importer des bundles signés, migrer propriété et identité et résoudre les anciennes refs (migrations, admin uniquement) |
| Chat et modération | `/api/federation/chat/bridge/{inbound,outbound,config}`, `GET /api/federation/chat/messages`, `/api/chat/moderation/*` | Bridge signé, historique dédupliqué, signalements, mutes, filtre et limite de 10 messages/60 s par nœud et utilisateur |
| Événements | `GET /api/federation/events/stream`, `POST /publish`, `GET /retry-queue` | SSE avec `since` et battement, publication aux pairs et relances (3 tentatives, 300 ms→5 s) |
| Résilience | `GET /api/federation/resilience/{health,heartbeat,metrics,incident-plan}`, `POST /keys/revoke`, `GET /keys/revoked` | Health, heartbeat, métriques p50/p95, révocation immédiate de clés et plan d'incident |
| Conformité | `python tools/federation_conformance.py <url> [--json]` | Vérifie un nœud tiers ; sort 1 en cas d'échecs critiques/élevés |

Le détail du modèle de confiance et du transport est dans [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) et [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md).

## Sauvegardes et migrations

- SQLite : copier `*.db` à l'arrêt (`-Kill` d'abord). MariaDB : `mariadb-dump` (volume `db-data`).
- Migrations : `alembic upgrade head` depuis `backend/` (prod **uniquement** Alembic, jamais `create_all`). Le head actuel est `c1d2e3f4a5b6` (42 révisions) et ajoute `identity_redirects`, `migration_audits`, `chat_outbox`, `message_reports` et `chat_mutes`.
- Changement de moteur : `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev) ; détail dans [DATABASE.md](DATABASE.md).

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Démarrage interrompu à cause de `SECRET_KEY` / CORS | défaut non sécurisé ou `*` en prod | Définir des `SECRET_KEY` et `CORS_ORIGINS` explicites |
| `401` sur les endpoints publics de formulaires | lien mal généré | Vérifiez le token du lien ; l'accès anonyme ne provoque pas de 401 en soi |
| `403` en gérant festival/canal/comité | appelant sans rôle | Vérifiez l'appartenance et le rôle (`GET …/members`) ; l'auto-join ne donne que `attendee` |
| `409` à l'inscription | déjà membre | Utilisez `leave` ou gérez depuis les membres |
| `413` à l'envoi | dépasse 10 MB de corps / 5 MB d'image / 100 MB de vidéo / 10 MB de pdf | Compressez ou découpez le fichier |
| `429` généralisé | rate limit 100/60s par IP (ou 3/300s sur reset) | Attendez et réessayez ; vérifiez un `TESTING=true` résiduel |
| Le WS ne se connecte pas | JWT sans `type=access` ou session révoquée/expirée | Reconnectez-vous ; vérifiez `/api/auth/sessions` |
| L'app hors ligne ne synchronise pas | file avec échecs épuisés (`failed`, 3 tentatives + backoff) | Vérifiez les erreurs dans l'invite de sync ; `clear()` après confirmation à la déconnexion |
| `403` à l'import d'un bundle | `origin_domain` non autorisé dans la politique du nœud | Vérifiez `/api/federation/nodes` et importez à nouveau |
| `429` en chat fédéré | plus de 10 messages/60 s par nœud et utilisateur | Attendez le `Retry-After` ; en tests, désactivé avec `TESTING=true` |
| Événements SSE coupés ou sans données | token invalide ou `since` en avant du replay | Reconnectez-vous et redémarrez avec `since=0` (replay de 200 événements) |
| Messages fédérés dupliqués | renvoi du bridge | Écartés par `message_id` dans `chat_outbox` ; vérifiez `/api/federation/chat/messages` |

## Voir aussi

- [USO.md](USO.md) : démarrage et exploitation du système
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) : déploiement, ports et CI
- [SEGURIDAD.md](SEGURIDAD.md) : checklist de durcissement et politiques
- [../README.md](../../README.md) : contexte global du projet
