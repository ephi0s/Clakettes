# Build / test / dev tresnak — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Komando-matrizea

| Helburua | Komandoa | Non |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Erroa (Docker eskuragarri badago, bestela lokala) |
| Soilik backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` `start.sh`-en |
| Web-a nabigatzailean | `-Web` | Soilik modu lokalean |
| Tokiko prod-a (web build + serve) | `-Final` | `start.ps1` / `start.sh` |
| Backend testak | `-TestBackend` | pytest `.venv`-n edo Docker-en |
| Frontend testak | `-TestFrontend` | `flutter test` edo Docker |
| Migrazioak | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Ingurunea abiarazi gabe berrikusi | `-Check` | Doctor: Docker, Python, Flutter, .venv, atak |
| Falta diren mendekotasunak instalatu | `-InstallMissing` | winget / SOaren kudeatzailea + git clone |
| Build partzialak | `-BuildFrontend` / `-BuildBackend` | Docker eskatzen dute |
| Android APK | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (macOS behar du) | `tools/build-ios.sh` | Soilik Mac batean Xcode-kin |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Dagokion ostalaria |
| Docker multi-target | `tools/build-all.ps1` | Docker eskatzen du |
| Nodo baten betetzea egiaztatu | `python tools/federation_conformance.py <url> [--json]` | Erroa (`tools/`) |
| API erreferentzia birsortu | `python tools/gen_api.py --all` | Erroa (`tools/`) |

Betetze-CLIak manifestua, JWKS, tokena, direktorioa, erabiltzaileak, WebFinger, txostenak, portabilitatea, txat-bridge-a eta gertaera-stream-a egiaztatzen ditu; 1 itzultzen du `critical`/`high` hutsegiteak badaude eta 0 bestela, eta `--json`-ek txosten osoa inprimatzen du.

## Aplikatutako hobekuntzak (09/10/2026)

1. **`.dockerignore` build-testuinguruetan** (`backend/`, `frontend/`). Lehen `backend/docker/` eta `frontend/docker/`-en soilik zeuden, eta horiek ez dira `docker-compose.yml`-en testuingurua (`./backend`, `./frontend`). `docker compose build` bakoitzak `.venv/` (ehunka MB), `.dart_tool/`, `build/`, `*.db` eta `*.hive` bidaltzen zizkion daemon-ari. Orain testuingurua gutxienekoa da. Salbuespena: `!pubspec.lock` gordetzen da build errepikagarrietarako.
2. **pytest konfigurazio bateratua**: `backend/pytest.ini` ezabatu zen (`pyproject.toml` bikoiztu eta eklipsatzen zuen); konfigurazio osoa `[tool.pytest.ini_options]`-en dago (testpaths, patroiak, marker-ak).
3. **CI koherentea**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (Dockerfile-eko bera); `flutter pub run` (zaharkitua) → `dart run build_runner`.
   - GitLab `backend-test`: `TESTING=true` eta `SECRET_KEY` gehitu ziren (lehen rate limiter-a testetan aktibo zegoen → noizbehinkako 429).
   - GitLab `frontend-test`: Hive egokitzaileen sorrera gehitu zen `flutter test` baino lehen (GitHub-ekiko paritatea).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (`requirements-dev.txt`-en bezala).
4. **Plataforma anitzeko lint-ak** (`analysis_options.yaml`): `avoid_print` eta `avoid_web_libraries_in_flutter`. Egiaztatuta: `flutter analyze` garbi (web/io inportazio baldintzatua onartutako eredua da).
5. **`onReorder` zaharkituaren konponketa** → `onReorderItem` (indize-egokitze manualik gabe); `flutter analyze`-k 1 info-tik 0 arazoetara pasatzen da.

## Proposamenak (aplikatu gabe, arrazoiarekin)

1. **`ruff format --check` atea CI-n**: ~249 E501/W292 urratze daudelako blokeatuta. Urratsak: `ruff format .`, diff-a berrikusi, `ruff check --fix`, eta orduan gehitu atea.
2. **`.ps1`/`.sh` bateratu**: ataka/prozesu logika bikoizten dute. Bide errealista ports/process matrica `tools/ports.*`-era ateratzea edo SO bakoitzeko sarrera-puntu bakarra dokumentatzea da, biak aldi berean biridatzi beharrean.
3. **CI-n estaldura** (`pytest --cov`, `flutter test --coverage` + lcov): erabilgarria `syncAll` eta estali gabeko router-en testak zabaltzen direnean (ikusi roadmap-a [../README.eu.md](../../README.eu.md) fitxategian).
