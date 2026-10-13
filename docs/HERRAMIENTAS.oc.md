# Aisinas build / test / dev — Clakettes

[ES](HERRAMIENTAS.md) · [EN](HERRAMIENTAS.en.md) · [FR](HERRAMIENTAS.fr.md) · [DE](HERRAMIENTAS.de.md) · [IT](HERRAMIENTAS.it.md) · [CA](HERRAMIENTAS.ca.md) · [EU](HERRAMIENTAS.eu.md) · [GL](HERRAMIENTAS.gl.md) · [OC](HERRAMIENTAS.oc.md)

## Matritz de comandas

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

## Amelhoraments aplicats (09/10/2026)

1. **`.dockerignore` dins los contèxtes de build** (`backend/`, `frontend/`).
   Abans sonque existissián en `backend/docker/` e `frontend/docker/`, que SON PAS lo
   contèxte de `docker-compose.yml` (`./backend`, `./frontend`). Cada
   `docker compose build` mandava `.venv/` (centenats de MB), `.dart_tool/`,
   `build/`, `*.db` e `*.hive` al daemon. Ara lo contèxte es minim.
   Excepcion: `!pubspec.lock` se consèrva per builds reproduchibles.
2. **Config pytest unificada**: escafat `backend/pytest.ini` (duplicava e
   eclipsava `pyproject.toml`); tota la config viu en
   `[tool.pytest.ini_options]` (testpaths, patrons, markers).
3. **CI coerenta**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (parièr que lo Dockerfile);
     `flutter pub run` (obsolet) → `dart run build_runner`.
   - GitLab `backend-test`: aponduts `TESTING=true` e `SECRET_KEY`
     (abans lo rate limiter demorava actiu en tèsts → 429 esporadics).
   - GitLab `frontend-test`: aponduda generacion d'adaptadors Hive abans
     de `flutter test` (paritat amb GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (parièr que
     `requirements-dev.txt`).
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` e
   `avoid_web_libraries_in_flutter`. Verificat: `flutter analyze` net
   (l'import condicionau web/io es lo patron acceptat).
5. **Corrècte `onReorder` obsolet** → `onReorderItem` (sens ajustament manuau d'
   indici); `flutter analyze` passa de 1 info a 0 issues.

## Prepausicions (non aplicadas, amb motiu)

1. **Pòrta `ruff format --check` en CI**: blocat per ~249 violacions
   E501/W292 existentas. Passas: `ruff format .`, revisar diff,
   `ruff check --fix`, e alara apondre la pòrta.
2. **Unificar `start.bat/.ps1/.sh`**: triplican la logica de pòrts/processús.
   La via realista es extraire la matritz de pòrts cap a `tools/ports.*` o
   documentar un sol entrypoint per OS, non reescriure los tres a l'encòp.
3. **Cobertura en CI** (`pytest --cov`, `flutter test --coverage` + lcov):
    utila quand s'ampliaràn tèsts de `syncAll` e routers sens cubrir (veire
    roadmap en [../README.oc.md](../README.oc.md)).
