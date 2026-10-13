# Outils build / test / dev — Clakettes

[ES](HERRAMIENTAS.md) · [EN](HERRAMIENTAS.en.md) · [FR](HERRAMIENTAS.fr.md) · [DE](HERRAMIENTAS.de.md) · [IT](HERRAMIENTAS.it.md) · [CA](HERRAMIENTAS.ca.md) · [EU](HERRAMIENTAS.eu.md) · [GL](HERRAMIENTAS.gl.md) · [OC](HERRAMIENTAS.oc.md)

## Matrice de commandes

| Objetivo | Comando | Dónde |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Raíz (Docker si disponible, local si no) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` en `start.sh` |
| Web en navegador | `-Web` | Solo modo local |
| Prod local (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest en `.venv` o Docker |
| Tests frontend | `-TestFrontend` | `flutter test` o Docker |
| Migraciones | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Revisar entorno sin arrancar | `-Check` | Doctor: Docker, Python, Flutter, .venv, puertos |
| Instalar dependencias que falten | `-InstallMissing` | winget / gestor del SO + git clone |
| Builds parciales | `-BuildFrontend` / `-BuildBackend` | Requieren Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (requiere macOS) | `tools/build-ios.sh` | Solo en Mac con Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Host correspondiente |
| Docker multi-target | `tools/build-all.ps1` | Requiere Docker |

## Améliorations appliquées (09/10/2026)

1. **`.dockerignore` dans les contextes de build** (`backend/`, `frontend/`).
   Avant ils n'existaient que dans `backend/docker/` et `frontend/docker/`, qui NE sont pas le
   contexte de `docker-compose.yml` (`./backend`, `./frontend`). Chaque
   `docker compose build` envoyait `.venv/` (centaines de MB), `.dart_tool/`,
   `build/`, `*.db` et `*.hive` au daemon. Maintenant le contexte est minimal.
   Exception : `!pubspec.lock` est conservé pour builds reproductibles.
2. **Config pytest unifiée** : supprimé `backend/pytest.ini` (dupliquait et
   éclipsait `pyproject.toml`) ; toute la config vit dans
   `[tool.pytest.ini_options]` (testpaths, motifs, markers).
3. **CI cohérente** :
   - GitHub : Flutter `3.22.0` → `3.24.0` (pareil que le Dockerfile) ;
     `flutter pub run` (obsolète) → `dart run build_runner`.
   - GitLab `backend-test` : ajoutés `TESTING=true` et `SECRET_KEY`
     (avant le rate limiter restait actif en tests → 429 sporadiques).
   - GitLab `frontend-test` : ajoutée génération d'adaptateurs Hive avant
     `flutter test` (parité avec GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (pareil que
     `requirements-dev.txt`).
4. **Lints multiplateformes** (`analysis_options.yaml`) : `avoid_print` et
   `avoid_web_libraries_in_flutter`. Vérifié : `flutter analyze` propre
   (l'import conditionnel web/io est le motif accepté).
5. **Fix `onReorder` obsolète** → `onReorderItem` (sans ajustement manuel d'
   indice) ; `flutter analyze` passe de 1 info à 0 issues.

## Propositions (non appliquées, avec motif)

1. **Gate `ruff format --check` en CI** : bloqué par ~249 violations
   E501/W292 existantes. Étapes : `ruff format .`, réviser diff,
   `ruff check --fix`, et alors ajouter le gate.
2. **Unifier `start.bat/.ps1/.sh`** : triplent la logique de ports/processus.
   La voie réaliste est extraire la matrice de ports vers `tools/ports.*` ou
   documenter un seul entrypoint par OS, pas réécrire les trois à la fois.
3. **Couverture en CI** (`pytest --cov`, `flutter test --coverage` + lcov) :
   utile quand s'étendront tests de `syncAll` et routers sans couvrir (voir
   roadmap dans [../README.fr.md](../README.fr.md)).
