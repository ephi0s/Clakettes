# Build / Test / Dev Tools — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Befehlsmatrix

| Ziel | Befehl | Wo |
|------|--------|-----|
| Dev Backend+Frontend | `.\start.ps1` / `./start.sh` | Stamm (Docker wenn verfügbar, lokal wenn nicht) |
| Nur Backend / Frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` in `start.sh` |
| Web im Browser | `-Web` | Nur lokaler Modus |
| Lokale Produktion (Web-Build + Serve) | `-Final` | `start.ps1` / `start.sh` |
| Backend-Tests | `-TestBackend` | pytest in `.venv` oder Docker |
| Frontend-Tests | `-TestFrontend` | `flutter test` oder Docker |
| Migrationen | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Umgebung prüfen ohne Start | `-Check` | Doctor: Docker, Python, Flutter, .venv, Ports |
| Fehlende Abhängigkeiten installieren | `-InstallMissing` | winget / OS-Paketmanager + git clone |
| Partielle Builds | `-BuildFrontend` / `-BuildBackend` | Erfordern Docker |
| Android APK | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (erfordert macOS) | `tools/build-ios.sh` | Nur auf Mac mit Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Entsprechender Host |
| Docker Multi-Target | `tools/build-all.ps1` | Erfordert Docker |

## Angewandte Verbesserungen (09/10/2026)

1. **`.dockerignore` in Build-Kontexten** (`backend/`, `frontend/`). Vorher existierten sie nur in `backend/docker/` und `frontend/docker/`, die NICHT der Kontext von `docker-compose.yml` (`./backend`, `./frontend`) sind. Jeder `docker compose build` sandte `.venv/` (Hunderte MB), `.dart_tool/`, `build/`, `*.db` und `*.hive` an den Daemon. Jetzt ist der Kontext minimal. Ausnahme: `!pubspec.lock` wird für reproduzierbare Builds beibehalten.
2. **Vereinfachte pytest-Konfiguration**: `backend/pytest.ini` entfernt (duplizierte und überschattete `pyproject.toml`); gesamte Konfiguration lebt in `[tool.pytest.ini_options]` (testpaths, Muster, Marker).
3. **Kohärente CI**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (gleich wie Dockerfile); `flutter pub run` (veraltet) → `dart run build_runner`.
   - GitLab `backend-test`: `TESTING=true` und `SECRET_KEY` hinzugefügt (zuvor blieb Rate-Limiter aktiv in Tests → sporadische 429er).
   - GitLab `frontend-test`: Hive-Adapter-Generierung vor `flutter test` hinzugefügt (Parität mit GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (gleich wie `requirements-dev.txt`).
4. **Plattformübergreifende Lints** (`analysis_options.yaml`): `avoid_print` und `avoid_web_libraries_in_flutter`. Verifiziert: `flutter analyze` sauber (bedingter Web/IO-Import ist das akzeptierte Muster).
5. **Fix veraltetes `onReorder`** → `onReorderItem` (ohne manuelle Indexanpassung); `flutter analyze` geht von 1 Info auf 0 Probleme.

## Vorschläge (nicht angewendet, mit Grund)

1. **`ruff format --check`-Tor in CI**: blockiert durch ~249 bestehende E501/W292-Verstöße. Schritte: `ruff format .`, Diff prüfen, `ruff check --fix`, dann Tor hinzufügen.
2. **`start.bat/.ps1/.sh` vereinheitlichen**: sie vervielfachen die Port-/Prozess-Logik. Der realistische Weg ist die Extraktion der Portmatrix nach `tools/ports.*` oder die Dokumentation eines einzelnen Entry-Points pro OS, nicht das gleichzeitige Umschreiben aller drei.
3. **CI-Coverage** (`pytest --cov`, `flutter test --coverage` + lcov): nützlich wenn `syncAll`- und nicht abgedeckte Router-Tests erweitert werden (siehe Roadmap in [../README.md](../../README.de.md)).