# Build-/Test-/Dev-Werkzeuge — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Befehlsmatrix

| Ziel | Befehl | Wo |
|---|---|---|
| Dev Backend+Frontend | `.\start.ps1` / `./start.sh` | Root (Docker, falls verfügbar, sonst lokal) |
| Nur Backend / Frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` in `start.sh` |
| Web im Browser | `-Web` | Nur im lokalen Modus |
| Lokale Produktion (Web-Build + Serve) | `-Final` | `start.ps1` / `start.sh` |
| Backend-Tests | `-TestBackend` | pytest in `.venv` oder Docker |
| Frontend-Tests | `-TestFrontend` | `flutter test` oder Docker |
| Migrationen | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Umgebung ohne Start prüfen | `-Check` | Doctor: Docker, Python, Flutter, .venv, Ports |
| Fehlende Abhängigkeiten installieren | `-InstallMissing` | winget / OS-Paketmanager + git clone |
| Teil-Builds | `-BuildFrontend` / `-BuildBackend` | Erfordern Docker |
| Android-APK | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (erfordert macOS) | `tools/build-ios.sh` | Nur auf Mac mit Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Entsprechender Host |
| Docker-Multi-Target | `tools/build-all.ps1` | Erfordert Docker |
| Knoten-Konformität prüfen | `python tools/federation_conformance.py <url> [--json]` | Root (`tools/`) |
| API-Referenz neu erzeugen | `python tools/gen_api.py --all` | Root (`tools/`) |

Das Konformitäts-CLI prüft Manifest, JWKS, Token, Verzeichnis, Nutzer, WebFinger, Meldungen, Portabilität, Chat-Bridge und Ereignis-Stream; es gibt 1 bei `critical`/`high`-Fehlern und sonst 0 zurück, und `--json` gibt den vollständigen Bericht aus.

## Angewendete Verbesserungen (09/10/2026)

1. **`.dockerignore` in Build-Kontexten** (`backend/`, `frontend/`). Zuvor existierten sie nur in `backend/docker/` und `frontend/docker/`, die NICHT der Kontext von `docker-compose.yml` sind (`./backend`, `./frontend`). Jedes `docker compose build` sandte `.venv/` (Hunderte MB), `.dart_tool/`, `build/`, `*.db` und `*.hive` an den Daemon. Jetzt ist der Kontext minimal. Ausnahme: `!pubspec.lock` wird für reproduzierbare Builds behalten.
2. **Vereinheitlichte pytest-Konfiguration**: `backend/pytest.ini` entfernt (duplizierte und überschattete `pyproject.toml`); die gesamte Konfiguration liegt in `[tool.pytest.ini_options]` (testpaths, Muster, Marker).
3. **Kohärente CI**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (wie im Dockerfile); `flutter pub run` (veraltet) → `dart run build_runner`.
   - GitLab `backend-test`: `TESTING=true` und `SECRET_KEY` hinzugefügt (zuvor blieb der Rate-Limiter in Tests aktiv → sporadische 429er).
   - GitLab `frontend-test`: Hive-Adapter-Generierung vor `flutter test` ergänzt (Parität mit GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (wie `requirements-dev.txt`).
4. **Plattformübergreifende Lints** (`analysis_options.yaml`): `avoid_print` und `avoid_web_libraries_in_flutter`. Geprüft: `flutter analyze` sauber (bedingter web/io-Import ist das akzeptierte Muster).
5. **Fix für veraltetes `onReorder`** → `onReorderItem` (keine manuelle Index-Anpassung); `flutter analyze` geht von 1 Info auf 0 Probleme.

## Vorschläge (nicht angewendet, mit Grund)

1. **`ruff format --check`-Gate in CI**: blockiert durch ~249 bestehende E501/W292-Verstöße. Schritte: `ruff format .`, Diff prüfen, `ruff check --fix`, dann das Gate hinzufügen.
2. **`.ps1`/`.sh` vereinheitlichen**: sie verdoppeln die Port-/Prozess-Logik. Der realistische Weg ist, die Port-Matrix nach `tools/ports.*` auszulagern oder einen einzigen Entry Point pro OS zu dokumentieren, nicht beide gleichzeitig neu zu schreiben.
3. **Coverage in CI** (`pytest --cov`, `flutter test --coverage` + lcov): nützlich, wenn die Tests für `syncAll` und ungetestete Router erweitert werden (siehe Roadmap in [../README.md](../../README.md)).
