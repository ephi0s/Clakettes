# Strumenti build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matrice dei comandi

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

## Migliorie applicate (09/10/2026)

1. **`.dockerignore` nei contesti di build** (`backend/`, `frontend/`).
   Prima esistevano solo in `backend/docker/` e `frontend/docker/`, che NON sono il
   contesto di `docker-compose.yml` (`./backend`, `./frontend`). Ogni
   `docker compose build` inviava `.venv/` (centinaia di MB), `.dart_tool/`,
   `build/`, `*.db` e `*.hive` al daemon. Ora il contesto è minimo.
   Eccezione: `!pubspec.lock` si conserva per build riproducibili.
2. **Config pytest unificata**: eliminato `backend/pytest.ini` (duplicava e
   oscurava `pyproject.toml`); tutta la config vive in
   `[tool.pytest.ini_options]` (testpaths, pattern, markers).
3. **CI coerente**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (come il Dockerfile);
     `flutter pub run` (obsoleto) → `dart run build_runner`.
   - GitLab `backend-test`: aggiunti `TESTING=true` e `SECRET_KEY`
     (prima il rate limiter restava attivo nei test → 429 sporadici).
   - GitLab `frontend-test`: aggiunta generazione degli adapter Hive prima
     di `flutter test` (parità con GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (come
     `requirements-dev.txt`).
4. **Lint multipiattaforma** (`analysis_options.yaml`): `avoid_print` e
   `avoid_web_libraries_in_flutter`. Verificato: `flutter analyze` pulito
   (l'import condizionale web/io è il pattern accettato).
5. **Fix `onReorder` obsoleto** → `onReorderItem` (senza aggiustamento manuale di
   indice); `flutter analyze` passa da 1 info a 0 issues.

## Proposte (non applicate, con motivo)

1. **Gate `ruff format --check` in CI**: bloccato da ~249 violazioni
   E501/W292 esistenti. Passi: `ruff format .`, rivedere diff,
   `ruff check --fix`, e poi aggiungere il gate.
2. **Unificare `start.bat/.ps1/.sh`**: triplicano la logica di porte/processi.
   La via realistica è estrarre la matrice delle porte in `tools/ports.*` o
   documentare un unico entrypoint per OS, non riscrivere i tre insieme.
3. **Copertura in CI** (`pytest --cov`, `flutter test --coverage` + lcov):
    utile quando si amplieranno i test di `syncAll` e router non coperti (vedi
    roadmap in [../README.it.md](../../README.it.md)).
