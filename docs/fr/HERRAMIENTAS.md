# Outils build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matrice des commandes

| Objectif | Commande | Où |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Racine (Docker si disponible, local sinon) |
| Backend / frontend seulement | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` dans `start.sh` |
| Web dans le navigateur de développement | défaut / `-Dev` | Docker dev ou local ; `-Web` force le mode local |
| Production locale (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest dans `.venv` ou Docker |
| Tests frontend | `-TestFrontend` | `flutter test` ou Docker |
| Porte de qualité (tout) | `tools/check.ps1` / `tools/check.sh` | Racine ; sans args : ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test |
| Porte rapide | `-Quick` / `--quick` | Seulement ruff + flutter analyze |
| Backend / frontend seulement | `-Backend` / `--backend`, `-Frontend` / `--frontend` | `tools/check.ps1` / `tools/check.sh` |
| Filtrer les tests | `-TestFilter EXPR` / `--test-filter=EXPR` | `-k` à pytest et `--plain-name` à Flutter ; identique dans `start.ps1` / `start.sh`, qui ajoutent aussi `-m "not interop"` en local |
| Migrations | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Vérifier l'environnement sans démarrer | `-Check` | Doctor : Docker, Python, Flutter, .venv, ports |
| Installer les dépendances manquantes | `-InstallMissing` | winget / gestionnaire du OS + git clone |
| Builds partiels | `-BuildFrontend` / `-BuildBackend` | Nécessitent Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (nécessite macOS) | `tools/build-ios.sh` | Seulement sur Mac avec Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Hôte correspondant |
| Docker multi-cible | `tools/build-all.ps1` | Nécessite Docker |
| Vérifier la conformité d'un nœud | `python tools/federation_conformance.py <url> [--json]` | Racine (`tools/`) |
| Régénérer la référence d'API | `python tools/gen_api.py --all` | Racine (`tools/`) ; combine les préfixes de `main.py` et de chaque `APIRouter` et détecte les dépendances d'auth |
| Vérifier la référence d'API générée | `python tools/gen_api.py --all --check` | Racine (`tools/`) ; vérifie que les `API.md` sont à jour sans les écrire (exit 1 si l'une diffère) ; exécuté par le job CI `docs-api` |
| Audit des dépendances (OSV) | `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable` | Racine (`tools/`) ; CVE/GHSA dans requirements, `pubspec.lock` et venv |

Le CLI de conformité vérifie manifeste, JWKS, token, répertoire, utilisateurs, WebFinger, signalements, portabilité, bridge de chat et flux d'événements ; il renvoie 1 en cas d'échecs `critical`/`high` et 0 sinon, et `--json` imprime le rapport complet.

Le script d'audit renvoie 1 s'il existe des avis corrigibles (`--fail-on fixable`) ; un avis non corrigeable présent uniquement dans le `.venv` local et absent du graphe des requirements ne fait pas partie du projet. Avec `--venv --show-orphans`, il liste les paquets installés absents des requirements et que personne ne requiert (orphelins du venv local), afin de pouvoir les désinstaller.

## Améliorations appliquées (09/10/2026)

1. **`.dockerignore` dans les contextes de build** (`backend/`, `frontend/`). Auparavant, ils n'existaient que dans `backend/docker/` et `frontend/docker/`, qui NE sont PAS le contexte de `docker-compose.yml` (`./backend`, `./frontend`). Chaque `docker compose build` envoyait `.venv/` (des centaines de MB), `.dart_tool/`, `build/`, `*.db` et `*.hive` au daemon. Désormais le contexte est minimal. Exception : `!pubspec.lock` est conservé pour des builds reproductibles.
2. **Config pytest unifiée** : suppression de `backend/pytest.ini` (dupliquait et éclipsait `pyproject.toml`) ; toute la config vit dans `[tool.pytest.ini_options]` (testpaths, motifs, markers).
3. **CI cohérente** :
   - GitHub : Flutter épinglé sur `3.50.1` (identique au Dockerfile) ; `flutter pub run` (obsolète) → `dart run build_runner`.
   - GitHub et GitLab `backend-test` : `TESTING=true` et `SECRET_KEY=test-secret-key-for-ci-only-32bytes!` (36 octets, évite `InsecureKeyLengthWarning` ; auparavant le rate limiter restait actif dans les tests → 429 sporadiques).
   - GitLab `frontend-test` : ajout de la génération des adaptateurs Hive avant `flutter test` (parité avec GitHub).
   - `pip install ruff` → `pip install "ruff==0.17.6"` dans GitHub Actions et GitLab ; `requirements-dev.txt` épingle également `ruff==0.17.6` pour le développement local.
4. **Lints multiplateformes** (`analysis_options.yaml`) : `avoid_print` et `avoid_web_libraries_in_flutter`. Vérifié : `flutter analyze` propre (l'import conditionnel web/io est le motif accepté).
5. **Correction de `onReorder` obsolète** → `onReorderItem` (pas d'ajustement manuel d'index) ; `flutter analyze` passe de 1 info à 0 problème.

## Propositions (non appliquées, avec motif)

1. ~~**Gate `ruff format --check` en CI**~~ : déjà appliqué dans GitHub et GitLab après la correction de ~249 violations E501/W292 historiques.
2. **Unifier `.ps1`/`.sh`** : ils dupliquent la logique ports/processus. La voie réaliste est d'extraire la matrice de ports vers `tools/ports.*` ou de documenter un seul point d'entrée par OS, pas de réécrire les deux à la fois.
3. **Couverture en CI** (`pytest --cov`, `flutter test --coverage` + lcov) : utile quand les tests de `syncAll` et des routers non couverts seront étendus (voir roadmap dans [../README.md](../../README.md)).
