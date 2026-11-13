# Outils build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matrice de commandes

| Objectif | Commande | Où |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Racine (Docker si disponible, local sinon) |
| Seulement backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` dans `start.sh` |
| Web dans le navigateur | `-Web` | Mode local uniquement |
| Production locale (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest dans `.venv` ou Docker |
| Tests frontend | `-TestFrontend` | `flutter test` ou Docker |
| Migrations | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Vérifier l'environnement sans démarrer | `-Check` | Médecin : Docker, Python, Flutter, .venv, ports |
| Installer les dépendances manquantes | `-InstallMissing` | winget / gestionnaire de paquets de l'OS + git clone |
| Builds partiels | `-BuildFrontend` / `-BuildBackend` | Nécessitent Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (nécessite macOS) | `tools/build-ios.sh` | Seulement sur Mac avec Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Hôte correspondant |
| Docker multi-cible | `tools/build-all.ps1` | Nécessite Docker |

## Améliorations appliquées (09/10/2026)

1. **`.dockerignore` dans les contextes de build** (`backend/`, `frontend/`). Auparavant ils n'existaient que dans `backend/docker/` et `frontend/docker/`, qui NE SONT PAS le contexte de `docker-compose.yml` (`./backend`, `./frontend`). Chaque `docker compose build` envoyait `.venv/` (des centaines de Mo), `.dart_tool/`, `build/`, `*.db` et `*.hive` au daemon. Maintenant le contexte est minimal. Exception : `!pubspec.lock` est conservé pour les builds reproductibles.
2. **Config pytest unifiée** : supprimé `backend/pytest.ini` (dupliquait et éclipsait `pyproject.toml`) ; toute la config vit dans `[tool.pytest.ini_options]` (testpaths, patrons, marqueurs).
3. **CI cohérente** :
   - GitHub : Flutter `3.22.0` → `3.24.0` (identique au Dockerfile) ; `flutter pub run` (obsolète) → `dart run build_runner`.
   - GitLab `backend-test` : ajout de `TESTING=true` et `SECRET_KEY` (auparavant le limitateur de taux restait actif dans les tests → 429 sporadiques).
   - GitLab `frontend-test` : ajout de la génération d'adaptateurs Hive avant `flutter test` (parité avec GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (identique à `requirements-dev.txt`).
4. **Lints multiplateforme** (`analysis_options.yaml`) : `avoid_print` et `avoid_web_libraries_in_flutter`. Vérifié : `flutter analyze` propre (l'import conditionnel web/io est le modèle accepté).
5. **Correction de `onReorder` obsolète** → `onReorderItem` (sans ajustement manuel d'index) ; `flutter analyze` passe de 1 info à 0 problèmes.

## Propositions (non appliquées, avec motif)

1. **Porte `ruff format --check` en CI** : bloquée par ~249 violations E501/W292 existantes. Étapes : `ruff format .`, révisez le diff, `ruff check --fix`, puis ajoutez la porte.
2. **Unifier `start.bat/.ps1/.sh`** : ils triplent la logique de ports/processus. La voie réaliste est d'extraire la matrice de ports vers `tools/ports.*` ou de documenter un seul point d'entrée par OS, sans réécrire les trois à la fois.
3. **Couverture en CI** (`pytest --cov`, `flutter test --coverage` + lcov) : utile quand les tests de `syncAll` et les routers sans couverture seront élargis (voir la feuille de route dans [../README.md](../../README.fr.md)).