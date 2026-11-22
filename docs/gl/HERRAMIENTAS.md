# Ferramentas build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matriz de comandos

| Obxectivo | Comando | Onde |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Raíz (Docker se dispoñible, local se non) |
| Só backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` en `start.sh` |
| Web en navegador | `-Web` | Só modo local |
| Prod local (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest en `.venv` ou Docker |
| Tests frontend | `-TestFrontend` | `flutter test` ou Docker |
| Migracións | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Revisar contorno sen arrancar | `-Check` | Doctor: Docker, Python, Flutter, .venv, portos |
| Instalar dependencias que falten | `-InstallMissing` | winget / xestor do SO + git clone |
| Builds parciais | `-BuildFrontend` / `-BuildBackend` | Requeren Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (require macOS) | `tools/build-ios.sh` | Só en Mac con Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Host correspondente |
| Docker multi-target | `tools/build-all.ps1` | Require Docker |
| Verificar conformidade dun nodo | `python tools/federation_conformance.py <url> [--json]` | Raíz (`tools/`) |
| Regenerar referencia de API | `python tools/gen_api.py --all` | Raíz (`tools/`); combina prefixos de `main.py` e de cada `APIRouter` e detecta dependencias de auth |

O CLI de conformidade comproba manifesto, JWKS, token, directorio, usuarios, WebFinger, informes, portabilidade, bridge de chat e stream de eventos; devolve 1 se hai fallos `critical`/`high` e 0 en caso contrario, e `--json` imprime o informe completo.

## Melloras aplicadas (09/10/2026)

1. **`.dockerignore` nos contextos de build** (`backend/`, `frontend/`). Antes só existían en `backend/docker/` e `frontend/docker/`, que NON son o contexto de `docker-compose.yml` (`./backend`, `./frontend`). Cada `docker compose build` enviaba `.venv/` (centos de MB), `.dart_tool/`, `build/`, `*.db` e `*.hive` ao daemon. Agora o contexto é mínimo. Excepción: `!pubspec.lock` consérvase para builds reproducibles.
2. **Config pytest unificada**: eliminado `backend/pytest.ini` (duplicaba e eclipsaba a `pyproject.toml`); toda a config vive en `[tool.pytest.ini_options]` (testpaths, patróns, markers).
3. **CI coherente**:
   - GitHub: Flutter fixado en `3.47.3` (igual que o Dockerfile); `flutter pub run` (obsoleto) → `dart run build_runner`.
   - GitHub e GitLab `backend-test`: `TESTING=true` e `SECRET_KEY=test-secret-key-for-ci-only-32bytes!` (36 bytes, evita `InsecureKeyLengthWarning`; antes o rate limiter seguía activo en tests → 429 esporádicos).
   - GitLab `frontend-test`: engadida xeración de adaptadores Hive antes de `flutter test` (paridade con GitHub).
   - `pip install ruff` → `pip install "ruff==0.15.22"` en GitHub Actions; GitLab usa `pip install "ruff>=0.5.0"` e `requirements-dev.txt` fixa `ruff==0.17.5` para desenvolvemento local.
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` e `avoid_web_libraries_in_flutter`. Verificado: `flutter analyze` limpo (a import condicional web/io é o patrón aceptado).
5. **Fix `onReorder` obsoleto** → `onReorderItem` (sen axuste manual de índice); `flutter analyze` pasa de 1 info a 0 issues.

## Propostas (non aplicadas, con motivo)

1. ~~**Gate `ruff format --check` en CI**~~: xa aplicado en GitHub e GitLab tras corrixir ~249 violacións E501/W292 históricas.
2. **Unificar `.ps1`/`.sh`**: duplican a lóxica de portos/procesos. A vía realista é extraer a matriz de portos a `tools/ports.*` ou documentar un único entrypoint por SO, non reescribir ambos á vez.
3. **Cobertura en CI** (`pytest --cov`, `flutter test --coverage` + lcov): útil cando se amplíen os tests de `syncAll` e routers sen cubrir (ver roadmap en [../README.gl.md](../../README.gl.md)).
