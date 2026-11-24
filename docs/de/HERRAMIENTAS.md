# Build-/Test-/Dev-Werkzeuge — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Befehlsmatrix

| Ziel | Befehl | Wo |
|---|---|---|
| Dev Backend+Frontend | `.\start.ps1` / `./start.sh` | Root (Docker, falls verfügbar, sonst lokal) |
| Nur Backend / Frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` in `start.sh` |
| Web im Entwicklungsbrowser | Standard / `-Dev` | Docker-Dev oder lokal; `-Web` erzwingt lokalen Modus |
| Lokale Produktion (Web-Build + Serve) | `-Final` | `start.ps1` / `start.sh` |
| Backend-Tests | `-TestBackend` | pytest in `.venv` oder Docker |
| Frontend-Tests | `-TestFrontend` | `flutter test` oder Docker |
| Qualitätstore (alles) | `tools/check.ps1` / `tools/check.sh` | Root; ohne Argumente: ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test |
| Schnelle Store | `-Quick` / `--quick` | Nur ruff + flutter analyze |
| Nur Backend / Frontend | `-Backend` / `--backend`, `-Frontend` / `--frontend` | `tools/check.ps1` / `tools/check.sh` |
| Tests filtern | `-TestFilter EXPR` / `--test-filter=EXPR` | `-k` an pytest und `--plain-name` an Flutter; ebenso in `start.ps1` / `start.sh`, die lokal zusätzlich `-m "not interop"` ergänzen |
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
| API-Referenz neu erzeugen | `python tools/gen_api.py --all` | Root (`tools/`); kombiniert Präfixe aus `main.py` und jedem `APIRouter` und erkennt Auth-Abhängigkeiten |
| Generierte API-Referenz prüfen | `python tools/gen_api.py --all --check` | Root (`tools/`); prüft, dass die `API.md` aktuell sind, ohne sie zu schreiben (Exit 1, falls eine abweicht); vom `docs-api` CI-Job ausgeführt |

Das Konformitäts-CLI prüft Manifest, JWKS, Token, Verzeichnis, Nutzer, WebFinger, Meldungen, Portabilität, Chat-Bridge und Ereignis-Stream; es gibt 1 bei `critical`/`high`-Fehlern und sonst 0 zurück, und `--json` gibt den vollständigen Bericht aus.

## Angewendete Verbesserungen (09/10/2026)

1. **`.dockerignore` in Build-Kontexten** (`backend/`, `frontend/`). Zuvor existierten sie nur in `backend/docker/` und `frontend/docker/`, die NICHT der Kontext von `docker-compose.yml` sind (`./backend`, `./frontend`). Jedes `docker compose build` sandte `.venv/` (Hunderte MB), `.dart_tool/`, `build/`, `*.db` und `*.hive` an den Daemon. Jetzt ist der Kontext minimal. Ausnahme: `!pubspec.lock` wird für reproduzierbare Builds behalten.
2. **Vereinheitlichte pytest-Konfiguration**: `backend/pytest.ini` entfernt (duplizierte und überschattete `pyproject.toml`); die gesamte Konfiguration liegt in `[tool.pytest.ini_options]` (testpaths, Muster, Marker).
3. **Kohärente CI**:
   - GitHub: Flutter festgelegt auf `3.50.1` (wie im Dockerfile); `flutter pub run` (veraltet) → `dart run build_runner`.
   - GitHub und GitLab `backend-test`: `TESTING=true` und `SECRET_KEY=test-secret-key-for-ci-only-32bytes!` (36 Bytes, vermeidet `InsecureKeyLengthWarning`; zuvor blieb der Rate-Limiter in Tests aktiv → sporadische 429er).
   - GitLab `frontend-test`: Hive-Adapter-Generierung vor `flutter test` ergänzt (Parität mit GitHub).
   - `pip install ruff` → `pip install "ruff==0.17.6"` in GitHub Actions und GitLab; `requirements-dev.txt` fixiert `ruff==0.17.6` auch für die lokale Entwicklung.
4. **Plattformübergreifende Lints** (`analysis_options.yaml`): `avoid_print` und `avoid_web_libraries_in_flutter`. Geprüft: `flutter analyze` sauber (bedingter web/io-Import ist das akzeptierte Muster).
5. **Fix für veraltetes `onReorder`** → `onReorderItem` (keine manuelle Index-Anpassung); `flutter analyze` geht von 1 Info auf 0 Probleme.

## Vorschläge (nicht angewendet, mit Grund)

1. ~~**`ruff format --check`-Gate in CI**~~: nach Korrektur von ~249 historischen E501/W292-Verstößen in GitHub und GitLab angewendet.
2. **`.ps1`/`.sh` vereinheitlichen**: sie verdoppeln die Port-/Prozess-Logik. Der realistische Weg ist, die Port-Matrix nach `tools/ports.*` auszulagern oder einen einzigen Entry Point pro OS zu dokumentieren, nicht beide gleichzeitig neu zu schreiben.
3. **Coverage in CI** (`pytest --cov`, `flutter test --coverage` + lcov): nützlich, wenn die Tests für `syncAll` und ungetestete Router erweitert werden (siehe Roadmap in [../README.md](../../README.md)).
