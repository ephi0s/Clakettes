# Strumenti build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matrice dei comandi

| Obiettivo | Comando | Dove |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Radice (Docker se disponibile, locale altrimenti) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` in `start.sh` |
| Web nel browser | `-Web` | Solo modalità locale |
| Produzione locale (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Test backend | `-TestBackend` | pytest in `.venv` o Docker |
| Test frontend | `-TestFrontend` | `flutter test` o Docker |
| Migrazioni | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Controllare l'ambiente senza avviare | `-Check` | Doctor: Docker, Python, Flutter, .venv, porte |
| Installare le dipendenze mancanti | `-InstallMissing` | winget / gestore del SO + git clone |
| Build parziali | `-BuildFrontend` / `-BuildBackend` | Richiedono Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (richiede macOS) | `tools/build-ios.sh` | Solo su Mac con Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Host corrispondente |
| Docker multi-target | `tools/build-all.ps1` | Richiede Docker |
| Verificare conformità di un nodo | `python tools/federation_conformance.py <url> [--json]` | Radice (`tools/`) |
| Rigenerare il riferimento API | `python tools/gen_api.py --all` | Radice (`tools/`) |

La CLI di conformità verifica manifesto, JWKS, token, directory, utenti, WebFinger, segnalazioni, portabilità, bridge della chat e stream degli eventi; restituisce 1 in caso di errori `critical`/`high` e 0 altrimenti, e `--json` stampa il report completo.

## Migliorie applicate (09/10/2026)

1. **`.dockerignore` nei contesti di build** (`backend/`, `frontend/`). Prima esistevano solo in `backend/docker/` e `frontend/docker/`, che NON sono il contesto di `docker-compose.yml` (`./backend`, `./frontend`). Ogni `docker compose build` inviava `.venv/` (centinaia di MB), `.dart_tool/`, `build/`, `*.db` e `*.hive` al daemon. Ora il contesto è minimale. Eccezione: `!pubspec.lock` è conservato per build riproducibili.
2. **Config pytest unificata**: rimosso `backend/pytest.ini` (duplicava e oscurava `pyproject.toml`); tutta la config sta in `[tool.pytest.ini_options]` (testpaths, pattern, marker).
3. **CI coerente**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (come nel Dockerfile); `flutter pub run` (obsoleto) → `dart run build_runner`.
   - GitLab `backend-test`: aggiunti `TESTING=true` e `SECRET_KEY` (prima il rate limiter restava attivo nei test → 429 sporadici).
   - GitLab `frontend-test`: aggiunta la generazione degli adattatori Hive prima di `flutter test` (parità con GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (come `requirements-dev.txt`).
4. **Lint multipiattaforma** (`analysis_options.yaml`): `avoid_print` e `avoid_web_libraries_in_flutter`. Verificato: `flutter analyze` pulito (l'import condizionale web/io è il modello accettato).
5. **Fix di `onReorder` obsoleto** → `onReorderItem` (nessuna regolazione manuale dell'indice); `flutter analyze` passa da 1 info a 0 problemi.

## Proposte (non applicate, con motivo)

1. **Gate `ruff format --check` in CI**: bloccato da ~249 violazioni E501/W292 esistenti. Passi: `ruff format .`, rivedere il diff, `ruff check --fix`, poi aggiungere il gate.
2. **Unificare `.ps1`/`.sh`**: duplicano la logica porte/processi. La via realistica è estrarre la matrice delle porte in `tools/ports.*` o documentare un unico entrypoint per SO, non riscrivere entrambi insieme.
3. **Copertura in CI** (`pytest --cov`, `flutter test --coverage` + lcov): utile quando si amplieranno i test di `syncAll` e dei router non coperti (vedi roadmap in [../README.md](../../README.md)).
