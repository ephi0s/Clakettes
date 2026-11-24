# Utilisation — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Démarrage rapide

| Je veux | Commande |
|---|---|
| Tout en local | `.\start.ps1` ou `./start.sh` (Docker si disponible, local sinon) |
| Backend / frontend seulement | `-NoFrontend` / `-NoBackend` |
| Tester dans le navigateur de développement | défaut / `-Dev` (ou `-Web` pour forcer le mode local) |
| Production locale | `-Final` (build web + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migrations / avec MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Tout arrêter | `-Kill` |
| Installer les dépendances manquantes | `-InstallMissing` (Windows : winget + git clone ; Linux/macOS : gestionnaire du OS + git clone) |
| Vérifier l'environnement sans démarrer | `-Check` (doctor : Docker, Python, Flutter, .venv, ports ; sort 1 si quelque chose manque) |
| Builds distribuables | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sans Docker, le lanceur crée un environnement local bare-metal : détecte Python 3.12+ et Flutter, montre comment les installer selon votre OS et propose de les installer avec `-InstallMissing` (demande avant sauf si vous passez le flag).

URLs dev : backend `http://localhost:8000` (Swagger sur `/docs`), frontend `http://localhost:3000`.
Si le port est occupé, il est réattribué automatiquement (voir `[PUERTO]` dans la sortie).
Admin initial (non-prod seulement) : `admin` / `setup` — à changer à la première connexion.

## Configuration

| Variable / flag | Où | Effet |
|---|---|---|
| `BACKEND_URL` | `--dart-define` ou écran backend dans l'app | URL de l'API (persistée dans SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev ; dans Docker `./data/clakettes.db`) ou `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatoire) |
| `SECRET_KEY` | env (obligatoire dans `APP_ENV=production`) | Signature JWT ; défaut non sécurisé bloque le démarrage en prod |
| `CORS_ORIGINS` | env | Origines explicites en prod (`*` interdit avec identifiants) |
| `APP_ENV` | env | `development` crée admin + `create_all` ; `production` exige Alembic |
| `PUBLIC_BASE_URL` | `backend/.env` | Domaine public du nœud ; apparaît dans le manifeste et les bundles de portabilité |
| `MTLS_REQUIRED` | env | Impose le mTLS de pair vérifié en fédération (CN et PEM du certificat) |
| `MTLS_CA_BUNDLE_PATH` | env | CA racine pour valider les certificats des clients fédérés |
| `MTLS_CLIENT_CERT_PATH`, `MTLS_CLIENT_KEY_PATH` | env | PEM du certificat et clé privée qui signent le manifeste (RSA-SHA256) |
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on` : `TESTING` désactive les rate limits et l'auto-migration ; `SKIP_AUTO_MIGRATE` ignore seulement l'auto-migration |
| `RATE_LIMITS_DB_PATH` | env | Chemin de la BD SQLite des limites (par défaut `backend/rate_limits.db`) |
| `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_EXPIRE_MINUTES` | env | Claims et durée de vie du JWT d'accès |
| `PAYMENTS_PROVIDER`, `MOCK_WEBHOOK_SECRET`, `MOCK_PAYMENTS_FORCE_FAIL` | env | Passerelle (`mock` par défaut) et secrets du webhook simulé |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDSYS_*` | env | Identifiants de paiement réels ; détail dans [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) |

**Note sur les paiements** : `PAYMENTS_PROVIDER=mock` est la valeur par défaut (`backend/app/config.py`). Stripe et Redsys ne sont PAS opérationnels tant que leurs webhooks ne sont pas câblés (`POST /api/payments/webhook/{stripe,redsys}`) ; aujourd'hui seul le webhook simulé fonctionne. Le `confirm` de Redsys renvoie toujours `"pending"`.
| `TESTING`, `SKIP_AUTO_MIGRATE` | env | `1/true/yes/on` : `TESTING` désactive les rate limits et l'auto-migration ; `SKIP_AUTO_MIGRATE` omet seulement l'auto-migration |

## Exploitation

- **Migrer** : `alembic upgrade head` depuis `backend/` (Docker : `-Migrate`).
- **Migration automatique** : l'app migre elle-même la DB au démarrage et scelle les nouvelles DB avec la révision courante ; `SKIP_AUTO_MIGRATE=1` pour l'ignorer (DB gérées extérieurement).
- **SQLite → MariaDB** : `export_sqlite_to_mariadb.py` ; retour avec `import_mariadb_to_sqlite.py` (détail dans [DATABASE.md](DATABASE.md)).
- **Sauvegardes** : SQLite = copier `*.db` ; MariaDB = `mariadb-dump` (volume `db-data` dans Docker).
- **Logs** : stdout d'uvicorn (tokens DAV expurgés) ; erreurs d'API dans SnackBar + `debugPrint`.
- **Limites** : corps ≤10 MB (413 si plus grand) ; rate limit avec 429 + relance (global 100/60 s par IP, `/dav` 600/60 s, login 5/300 s, refresh 20/60 s, reset 3/300 s, federation 60/60 s ; chat 10/60 s par nœud et utilisateur). `TESTING` ∈ {1,true,yes,on} désactive toutes les limites.
- **Sans connexion** : le cache Hive conserve la provenance de chaque nœud ; `reconcile` fusionne à la reconnexion et `clearOrigin` écarte un nœud. Si certains nœuds ne répondent pas mais que le principal le fait, `DegradedNodesBanner` s'affiche avec le décompte et un bouton pour recharger.
- **Médias** : les chemins `/uploads/...` renvoyés par l'API sont préfixés avec le serveur actif côté client (`resolveMediaUrl()`) ; les URL `http(s)` sont utilisées telles quelles.
- **Fédération** : vérifiez un nœud tiers avec `python tools/federation_conformance.py <url> [--json]` ; la santé du peering est sur `/api/federation/resilience/health` et les métriques p50/p95 sur `/metrics`.
- **Portabilité** : exportez/importez des bundles depuis `/api/federation/portability/{bundles,imports}` et consultez les redirections d'identité sur `/redirects/{ref}`.

## Rôles utilisateur

`admin` (tout) → `organizer` (son festival : événements, formulaires, comités) → `attendee`/`juror`/etc. (assignés par les organizers ; l'auto-join ne donne que `attendee`). Canaux : `admin`/`moderator`/`member` ; comités avec compte de membres en liste.

## Fonctions en développement actif

🚧 Les fonctions suivantes sont en développement actif et peuvent changer :

- **Profils sociaux** : murs de publications (microblogging avec Markdown et intégrations vidéo/podcast) sur les profils utilisateur et festival, avec fils de réponses optionnels par publication et modération par rôles (administrateurs, gestion du festival, modérateurs). Pas de réactions, stickers ni GIF pour l'instant.
- **Personnalisation des profils** : couverture, tagline et liens sociaux sur les utilisateurs et festivals.
- **Badges** : désactivés par défaut ; seule l'équipe administrative peut les activer (`PUT /api/badges/settings`). Les badges de plateforme sont attribués par les administrateurs ; les badges de mérite de festival (vétéran, populaire, rôle, prix spécial), leur gestion. Chaque badge porte une image (SVG préféré).
- **Vote du jury** : déjà opérationnel (notation par œuvre, agrégation et anonymat optionnel) ; n'accepte que les courts du festival assigné.

## Voir aussi

- [README.md](../../README.md) : description générale du projet et accès rapide
- [HERRAMIENTAS.md](HERRAMIENTAS.md) : scripts et commandes d'exécution
- [ADMINISTRACION.md](ADMINISTRACION.md) : administration du déploiement et rotation des secrets
- [SEGURIDAD.md](SEGURIDAD.md) : checklist et bonnes pratiques de production
