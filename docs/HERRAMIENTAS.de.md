# Build-/Test-/Dev-Werkzeuge — Clakettes

## Befehlsmatrix

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

## Angewandte Verbesserungen (09/10/2026)

1. **`.dockerignore` in den Build-Kontexten** (`backend/`, `frontend/`).
   Vorher existierten sie nur in `backend/docker/` und `frontend/docker/`, die NICHT der
   Kontext von `docker-compose.yml` sind (`./backend`, `./frontend`). Jedes
   `docker compose build` sendete `.venv/` (hunderte MB), `.dart_tool/`,
   `build/`, `*.db` und `*.hive` an den Daemon. Jetzt ist der Kontext minimal.
   Ausnahme: `!pubspec.lock` bleibt für reproduzierbare Builds erhalten.
2. **Vereinheitlichte Pytest-Config**: `backend/pytest.ini` entfernt (duplizierte und
   überdeckte `pyproject.toml`); die ganze Config lebt in
   `[tool.pytest.ini_options]` (testpaths, Muster, Marker).
3. **Kohärente CI**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (wie das Dockerfile);
     `flutter pub run` (obsolet) → `dart run build_runner`.
   - GitLab `backend-test`: `TESTING=true` und `SECRET_KEY` hinzugefügt
     (vorher blieb der Rate-Limiter in Tests aktiv → sporadische 429).
   - GitLab `frontend-test`: Hive-Adapter-Generierung vor
     `flutter test` hinzugefügt (Parität mit GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (wie
     `requirements-dev.txt`).
4. **Multiplattform-Lints** (`analysis_options.yaml`): `avoid_print` und
   `avoid_web_libraries_in_flutter`. Verifiziert: `flutter analyze` sauber
   (der konditionale Web/IO-Import ist das akzeptierte Muster).
5. **Fix `onReorder` obsolet** → `onReorderItem` (ohne manuelle Index-Anpassung);
   `flutter analyze` geht von 1 Info auf 0 Issues.

## Vorschläge (nicht angewandt, mit Grund)

1. **Gate `ruff format --check` in CI**: blockiert durch ~249 existierende
   E501/W292-Verstöße. Schritte: `ruff format .`, Diff prüfen,
   `ruff check --fix`, und dann das Gate hinzufügen.
2. **`start.bat/.ps1/.sh` vereinen**: verdreifachen die Port-/Prozess-Logik.
   Der realistische Weg ist, die Port-Matrix nach `tools/ports.*` zu extrahieren oder
   einen einzigen Entrypoint pro OS zu dokumentieren, nicht alle drei auf einmal neu zu schreiben.
3. **Coverage in CI** (`pytest --cov`, `flutter test --coverage` + lcov):
   nützlich wenn Tests von `syncAll` und unabgedeckten Routern erweitert werden (siehe
   Roadmap in [../README.de.md](../README.de.md)).
