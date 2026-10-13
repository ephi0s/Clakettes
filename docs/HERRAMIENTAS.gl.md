# Ferramentas build / test / dev — Clakettes

## Matriz de comandos

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

## Melloras aplicadas (09/10/2026)

1. **`.dockerignore` nos contextos de build** (`backend/`, `frontend/`).
   Antes só existían en `backend/docker/` e `frontend/docker/`, que NON son o
   contexto de `docker-compose.yml` (`./backend`, `./frontend`). Cada
   `docker compose build` enviaba `.venv/` (centos de MB), `.dart_tool/`,
   `build/`, `*.db` e `*.hive` ao daemon. Agora o contexto é mínimo.
   Excepción: `!pubspec.lock` consérvase para builds reproducibles.
2. **Config pytest unificada**: eliminado `backend/pytest.ini` (duplicaba e
   eclipsaba a `pyproject.toml`); toda a config vive en
   `[tool.pytest.ini_options]` (testpaths, patróns, markers).
3. **CI coherente**:
   - GitHub: Flutter `3.22.0` → `3.24.0` (igual que o Dockerfile);
     `flutter pub run` (obsoleto) → `dart run build_runner`.
   - GitLab `backend-test`: engadidos `TESTING=true` e `SECRET_KEY`
     (antes o rate limiter seguía activo en tests → 429 esporádicos).
   - GitLab `frontend-test`: engadida xeración de adaptadores Hive antes
     de `flutter test` (paridade con GitHub).
   - `pip install ruff` → `pip install "ruff>=0.5.0"` (igual que
     `requirements-dev.txt`).
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` e
   `avoid_web_libraries_in_flutter`. Verificado: `flutter analyze` limpo
   (o import condicional web/io é o patrón aceptado).
5. **Fix `onReorder` obsoleto** → `onReorderItem` (sen axuste manual de
   índice); `flutter analyze` pasa de 1 info a 0 issues.

## Propostas (non aplicadas, con motivo)

1. **Gate `ruff format --check` en CI**: bloqueado por ~249 violacións
   E501/W292 existentes. Pasos: `ruff format .`, revisar diff,
   `ruff check --fix`, e entón engadir o gate.
2. **Unificar `start.bat/.ps1/.sh`**: triplican a lóxica de portos/procesos.
   A vía realista é extraer a matriz de portos a `tools/ports.*` ou
   documentar un único entrypoint por SO, non reescribir os tres á vez.
3. **Cobertura en CI** (`pytest --cov`, `flutter test --coverage` + lcov):
    útil cando se amplíen tests de `syncAll` e routers sen cubrir (ver
    roadmap en [../README.md](../README.gl.md)).
