# Herramientas build / test / dev — Clakettes

[ES](HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matriz de comandos

| Objetivo | Comando | Dónde |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Raíz (Docker si disponible, local si no) |
| Solo backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` en `start.sh` |
| Web en navegador de desarrollo | default / `-Dev` | Docker dev o local; `-Web` fuerza modo local |
| Prod local (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest en `.venv` o Docker |
| Tests frontend | `-TestFrontend` | `flutter test` o Docker |
| Puerta de calidad (todo) | `tools/check.ps1` / `tools/check.sh` | Raíz; sin args: ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test |
| Puerta rápida | `-Quick` / `--quick` | Solo ruff + flutter analyze |
| Solo backend / frontend | `-Backend` / `--backend`, `-Frontend` / `--frontend` | `tools/check.ps1` / `tools/check.sh` |
| Filtrar tests | `-TestFilter EXPR` / `--test-filter=EXPR` | `-k` en pytest y `--plain-name` en Flutter; igual en `start.ps1` / `start.sh`, que añaden `-m "not interop"` en local |
| Migraciones | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Revisar entorno sin arrancar | `-Check` | Doctor: Docker, Python, Flutter, .venv, puertos |
| Instalar dependencias que falten | `-InstallMissing` | winget / gestor del SO + git clone |
| Builds parciales | `-BuildFrontend` / `-BuildBackend` | Requieren Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (requiere macOS) | `tools/build-ios.sh` | Solo en Mac con Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Host correspondiente |
| Docker multi-target | `tools/build-all.ps1` | Requiere Docker |
| Verificar conformidad de un nodo | `python tools/federation_conformance.py <url> [--json]` | Raíz (`tools/`) |
| Regenerar referencia de API | `python tools/gen_api.py --all` | Raíz (`tools/`); combina prefijos de `main.py` y de cada `APIRouter` y detecta dependencias de auth |
| Verificar referencia de API generada | `python tools/gen_api.py --all --check` | Raíz (`tools/`); comprueba que las `API.md` estén al día sin escribirlas (exit 1 si alguna difiere); lo ejecuta el job `docs-api` de CI |
| Auditoría de dependencias (OSV) | `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable` | Raíz (`tools/`); CVE/GHSA en requirements, `pubspec.lock` y venv |

El CLI de conformidad comprueba manifiesto, JWKS, token, directorio, usuarios, WebFinger, reportes, portabilidad, bridge de chat y stream de eventos; devuelve 1 si hay fallos `critical`/`high` y 0 en caso contrario, y `--json` imprime el informe completo.

El script de auditoría devuelve 1 si hay avisos corregibles (`--fail-on fixable`); un aviso irreparable que aparezca solo en el `.venv` local y no en el grafo de requirements no forma parte del proyecto. Con `--venv --show-orphans` se listan los paquetes instalados que no figuran en requirements y a los que nadie requiere (huérfanos del venv local), para poder desinstalarlos.

## Mejoras aplicadas (09/10/2026)

1. **`.dockerignore` en los contextos de build** (`backend/`, `frontend/`). Antes solo existían en `backend/docker/` y `frontend/docker/`, que NO son el contexto de `docker-compose.yml` (`./backend`, `./frontend`). Cada `docker compose build` enviaba `.venv/` (cientos de MB), `.dart_tool/`, `build/`, `*.db` y `*.hive` al daemon. Ahora el contexto es mínimo. Excepción: `!pubspec.lock` se conserva para builds reproducibles.
2. **Config pytest unificada**: eliminado `backend/pytest.ini` (duplicaba y eclipsaba a `pyproject.toml`); toda la config vive en `[tool.pytest.ini_options]` (testpaths, patrones, markers).
3. **CI coherente**:
   - GitHub: Flutter fijado en `3.50.1` (igual que el Dockerfile); `flutter pub run` (obsoleto) → `dart run build_runner`.
   - GitHub y GitLab `backend-test`: `TESTING=true` y `SECRET_KEY=test-secret-key-for-ci-only-32bytes!` (36 bytes, evita `InsecureKeyLengthWarning`; antes el rate limiter seguía activo en tests → 429 esporádicos).
   - GitLab `frontend-test`: añadida generación de adaptadores Hive antes de `flutter test` (paridad con GitHub).
   - `pip install ruff` → `pip install "ruff==0.17.6"` en GitHub Actions y en GitLab; `requirements-dev.txt` fija `ruff==0.17.6` también para desarrollo local.
    - CodeQL (`.github/workflows/codeql.yml`, Advanced Setup) analiza solo el backend Python con `security-extended`; Dart no está cubierto por CodeQL.
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` y `avoid_web_libraries_in_flutter`. Verificado: `flutter analyze` limpio (el import condicional web/io es el patrón aceptado).
5. **Fix `onReorder` obsoleto** → `onReorderItem` (sin ajuste manual de índice); `flutter analyze` pasa de 1 info a 0 issues.

## Propuestas (no aplicadas, con motivo)

1. ~~**Gate `ruff format --check` en CI**~~: ya aplicado en GitHub y GitLab tras corregir ~249 violaciones E501/W292 históricas.
2. **Unificar `.ps1`/`.sh`**: duplican la lógica de puertos/procesos. La vía realista es extraer la matriz de puertos a `tools/ports.*` o documentar un único entrypoint por OS, no reescribir ambos a la vez.
3. **Cobertura en CI** (`pytest --cov`, `flutter test --coverage` + lcov): útil cuando se amplíen tests de `syncAll` y routers sin cubrir (ver roadmap en [../README.md](../../README.md)).