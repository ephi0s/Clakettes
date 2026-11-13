# Administration — Clakettes

[ES](../es/ADMINISTRACION.md) · [EN](../en/ADMINISTRACION.md) · [FR](ADMINISTRACION.md) · [DE](../de/ADMINISTRACION.md) · [IT](../it/ADMINISTRACION.md) · [CA](../ca/ADMINISTRACION.md) · [EU](../eu/ADMINISTRACION.md) · [GL](../gl/ADMINISTRACION.md) · [OC](../oc/ADMINISTRACION.md)

Guide pour quiconque exploite un déploiement. Infrastructure dans [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md), checklist de production dans [SEGURIDAD.md](SEGURIDAD.md).

## Compte initial

En non-prod (`APP_ENV != production`) le démarrage crée `admin` / `setup` (`admin@clakettes.com`, rôle admin) s'il n'existe pas ; en prod **il n'est pas créé**. Changez le mot de passe à la première connexion. La connexion utilise `POST /api/users/login` (JWT 30 min + refresh 30 j, liste et révoque les sessions à `/api/auth/sessions`).

## Endpoints `/api/admin` (rôle admin uniquement, 403 sinon)

| Méthode et route | Effet |
|---|---|
| `GET /api/admin/stats` | Compteurs : utilisateurs, festivals, courts-métrages, messages, actifs |
| `GET /api/admin/tables` | Tables (sauf `alembic_version`) avec nombre de lignes |
| `GET /api/admin/audit-log` | Piste d'audit (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` `{"confirm":"yes","password":"<actual>"}` | `drop_all + create_all`. 400 si `confirm` n'est pas `yes`, 403 si le mot de passe ne vérifie pas ; rate limit propre 3/300s (429, contournement avec `TESTING=true`) |

## Secrets et rotation

- `SECRET_KEY` : obligatoire en prod (le démarrage échoue avec la clé d'exemple et indique `secrets.token_urlsafe(64)`). La rotation invalide tous les JWT et tokens de refresh : faites-le dans une fenêtre de maintenance et prévenez (tous se reconnectent).
- `CORS_ORIGINS` : origines explicites en prod ; `*` + credentials est interdit et bloque le démarrage.
- Derrière un proxy : `uvicorn --proxy-headers` + `FORWARDED_ALLOW_IPS` + TLS frontal.

## Sauvegardes et migrations

- SQLite : copier `*.db` à l'arrêt (`-Kill` avant). MariaDB : `mariadb-dump` (volume `db-data`).
- Migrations : `alembic upgrade head` depuis `backend/` (36 versions ; en prod **seulement** Alembic, jamais `create_all`).
- Changement de moteur : `python export_sqlite_to_mariadb.py` (dev→prod), `python import_mariadb_to_sqlite.py` (prod→dev) ; détail dans [DATABASE.md](DATABASE.md).

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Démarrage aborté par `SECRET_KEY` / CORS | défaut insécurisé ou `*` en prod | Définissez `SECRET_KEY` et `CORS_ORIGINS` explicites |
| `401` sur endpoints publics de formulaires | lien mal généré | Vérifiez le token du lien ; l'accès anonyme ne cause pas 401 par lui-même |
| `403` gérant festival/canal/comité | appelant sans rôle | Vérifiez membres et rôle (`GET …/members`) ; l'auto-join donne seulement `attendee` |
| `409` en rejoignant | déjà membre | Utilisez `leave` ou gérez depuis membres |
| `413` upload | dépasse 10 Mo corps / 5 Mo image / 100 Mo vidéo / 10 Mo pdf | Compressez ou divisez le fichier |
| `429` généralisé | rate limit 100/60s par IP (ou 3/300s sur reset) | Attendez et réessayez ; vérifiez `TESTING=true` résiduel |
| WS ne se connecte pas | JWT sans `type=access` ou session révoquée/expirée | Reconnectez-vous ; vérifiez `/api/auth/sessions` |
| App hors ligne ne synchronise pas | file d'attente avec échecs épuisés (`failed`, 3 tentatives + backoff) | Vérifiez les erreurs dans le prompt de sync ; `clear()` après confirmation sur déconnexion |

## Voir aussi

- [USO.md](USO.md) : démarrage et opération du système
- [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) : déploiement, ports et CI
- [SEGURIDAD.md](SEGURIDAD.md) : checklist d'endurcissement et politiques
- [../README.md](../../README.fr.md) : contexte global du projet