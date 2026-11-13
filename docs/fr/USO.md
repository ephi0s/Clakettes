# Utilisation — Clakettes

[ES](../es/USO.md) · [EN](../en/USO.md) · [FR](USO.md) · [DE](../de/USO.md) · [IT](../it/USO.md) · [CA](../ca/USO.md) · [EU](../eu/USO.md) · [GL](../gl/USO.md) · [OC](../oc/USO.md)

## Démarrage rapide

| Je veux | Commande |
|---|---|
| Tout en local | `.\start.ps1` ou `./start.sh` (Docker si disponible, local sinon) |
| Seulement backend / frontend | `-NoFrontend` / `-NoBackend` |
| Tester dans le navigateur | `-Web` (mode local) |
| Production locale | `-Final` (build web + serve) |
| Tests | `-TestBackend` / `-TestFrontend` |
| Migrations / avec MariaDB | `-Migrate` / `-MariaDB` / `-TestMigration` |
| Arrêter tout | `-Kill` |
| Installer les dépendances manquantes | `-InstallMissing` (Windows : winget + git clone ; Linux/macOS : gestionnaire de paquets de l'OS + git clone) |
| Vérifier l'environnement sans démarrer | `-Check` (médecin : Docker, Python, Flutter, .venv, ports ; sort 1 s'il manque quelque chose) |
| Builds distribuables | `-BuildAll` (`tools/build-all.ps1` → `builds/`) |

Sans Docker, le lanceur crée un environnement bare-metal local : détecte Python 3.12+ et Flutter, montre comment les installer selon votre OS et propose de les installer avec `-InstallMissing` (demande avant sauf si vous passez le flag).

URLs dev : backend `http://localhost:8000` (Swagger à `/docs`), frontend `http://localhost:3000`.
Si le port est occupé, il est réassigné automatiquement (voir `[PUERTO]` dans la sortie).
Admin initial (non-prod uniquement) : `admin` / `setup` — changer à la première connexion.

## Configuration

| Variable / flag | Où | Effet |
|---|---|---|
| `BACKEND_URL` | `--dart-define` ou écran backend dans l'app | URL de l'API (persisté dans SharedPreferences) |
| `DATABASE_URL` | `backend/.env` | `sqlite:///./clakettes.db` (dev ; dans Docker `./data/clakettes.db`) ou `mariadb+pymysql://…?ssl_ca=…` (prod, TLS obligatoire) |
| `SECRET_KEY` | env (obligatoire en `APP_ENV=production`) | Signe JWT ; default insécurisé bloque le démarrage en prod |
| `CORS_ORIGINS` | env | Origines explicites en prod (`*` interdit avec credentials) |
| `APP_ENV` | env | `development` crée admin + `create_all` ; `production` exige Alembic |

## Opération

- **Migrer** : `alembic upgrade head` depuis `backend/` (Docker : `-Migrate`).
- **Migration automatique** : l'app migre la DB elle-même au démarber et scelle les nouvelles DB avec la révision actuelle ; `SKIP_AUTO_MIGRATE=1` pour l'omettre (DBs gérées externement).
- **SQLite → MariaDB** : `export_sqlite_to_mariadb.py` ; retour avec `import_mariadb_to_sqlite.py` (détail dans [DATABASE.md](DATABASE.md)).
- **Sauvegardes** : SQLite = copier `*.db` ; MariaDB = `mariadb-dump` (volume `db-data` dans Docker).
- **Logs** : stdout uvicorn (tokens DAV déjà redactés) ; erreurs API dans SnackBar + `debugPrint`.
- **Limites** : corps ≤10 Mo (413 si plus) ; rate limit avec 429 + réessai.

## Rôles utilisateur

`admin` (tout) → `organizer` (son festival : événements, formulaires, comités) → `attendee`/`juror`/etc. (assignés par organizers ; l'auto-join donne seulement `attendee`). Canaux : `admin`/`moderator`/`member` ; comités avec décompte de membres dans la liste.

## Fonctions en développement actif

🚧 Les fonctions suivantes sont en développement actif et peuvent changer :

- **Profils sociaux** : murs de publications (microblogging avec Markdown et intégrations vidéo/podcast) sur les profils utilisateur et festival, avec fils de réponses optionnels par publication et modération par rôles (administrateurs, gestion du festival, modérateurs). Pas de réactions, stickers ni GIF pour l'instant.
- **Personnalisation de profils** : couverture, tagline et liens sociaux sur utilisateurs et festivals.
- **Insignes** : désactivées par défaut ; seule l'équipe administrative peut les activer (`PUT /api/badges/settings`). Les insignes de plateforme sont octroyées par les administrateurs ; les insignes de mérite de festival (vétéran, populaire, rôle, prix spécial), leur gestion. Chaque insigne porte une image (SVG préféré).
- **Vote du jury** : notation par œuvre, agrégation et anonymat optionnel (phase 5 de la feuille de route).

## Voir aussi

- [README.md](../../README.fr.md) : description générale du projet et accès rapide
- [HERRAMIENTAS.md](HERRAMIENTAS.md) : scripts et commandes d'exécution
- [ADMINISTRACION.md](ADMINISTRACION.md) : administration du déploiement et rotation de secrets
- [SEGURIDAD.md](SEGURIDAD.md) : checklist et bonnes pratiques de production