# Build / test / dev tresnak — Clakettes

[ES](HERRAMIENTAS.md) · [EN](HERRAMIENTAS.en.md) · [FR](HERRAMIENTAS.fr.md) · [DE](HERRAMIENTAS.de.md) · [IT](HERRAMIENTAS.it.md) · [CA](HERRAMIENTAS.ca.md) · [EU](HERRAMIENTAS.eu.md) · [GL](HERRAMIENTAS.gl.md) · [OC](HERRAMIENTAS.oc.md)

## Komando-matrizea

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

## Aplikatutako hobekuntzak (09/10/2026)

1. **Build testuinguruetako `.dockerignore`** (`backend/`, `frontend/`).
   Lehen `backend/docker/` eta `frontend/docker/`-en soilik zeuden, EZ direnak
   `docker-compose.yml`-ko testuingurua (`./backend`, `./frontend`). `docker compose build`
   bakoitzak `.venv/` (ehunka MB), `.dart_tool/`,
   `build/`, `*.db` eta `*.hive` bidaltzen zizkion daemon-ari. Orain testuingurua minimoa da.
   Salbuespena: `!pubspec.lock` kontserbatzen da build erreproduzigarrietarako.
2. **Pytest config bateratua**: `backend/pytest.ini` kenduta (bikoiztu eta
   `pyproject.toml` eklipsatzen zuen); config guztia bizi da
   `[tool.pytest.ini_options]`-n (testpaths, ereduak, markers).
3. **CI koherentea**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (Dockerfile-aren berdina);
     `flutter pub run` (zaharkitua) → `dart run build_runner`.
   - GitLab `backend-test`: `TESTING=true` eta `SECRET_KEY` gehituta
     (lehen rate limiter-a aktibo zen test-etan → noizbehinkako 429).
   - GitLab `frontend-test`: Hive egokitzaileen sorkuntza gehituta
     `flutter test` aurretik (GitHub-ekiko parekotasuna).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (berdina
     `requirements-dev.txt`-n).
4. **Plataforma-aniztasun lint-ak** (`analysis_options.yaml`): `avoid_print` eta
   `avoid_web_libraries_in_flutter`. Egiaztatuta: `flutter analyze` garbi
   (web/io inportazio baldintzatua onartutako eredua da).
5. **`onReorder` zaharkituaren konponketa** → `onReorderItem` (indizearen doiketa manualik gabe); `flutter analyze` info 1-etik 0 issue-ra pasatzen da.

## Proposamenak (aplikatu gabeak, arrazoiarekin)

1. **`ruff format --check` gate-a CI-n**: ~249 baliaketa blokeatuta
   E501/W292 existitzen direnak. Pausoak: `ruff format .`, diff-a berrikusi,
   `ruff check --fix`, eta orduan gate-a gehitzea.
2. **`start.bat/.ps1/.sh` bateratzea**: portu/prozesu logika hirukoizten dute.
   Bide errealista portu-matrizea `tools/ports.*`-ra erauztea edo
   OS-ko entrypoint bakarra dokumentatzea da, hirurak batera ez berridaztea.
3. **Estaldura CI-n** (`pytest --cov`, `flutter test --coverage` + lcov):
   erabilgarria `syncAll` eta estali gabeko router-en test-ak zabaltzean (ikusi
   roadmap-a [../README.md](../README.eu.md)-n).
