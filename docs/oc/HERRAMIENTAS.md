# Aisinas build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](../ca/HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](HERRAMIENTAS.md)

## Matritz de comandas

| Objectiu | Comanda | Ont |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Raíç (Docker se disponible, local autrament) |
| Solament backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` dins `start.sh` |
| Web dins un navegador de desvolopament | per defaut / `-Dev` | Docker dev o local; `-Web` força lo mode local |
| Prod locala (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tèsts backend | `-TestBackend` | pytest dins `.venv` o Docker |
| Tèsts frontend | `-TestFrontend` | `flutter test` o Docker |
| Pòrta de qualitat (tot) | `tools/check.ps1` / `tools/check.sh` | Raíç; sens arguments: ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test |
| Pòrta rapida | `-Quick` / `--quick` | Sonque ruff + flutter analyze |
| Solament backend / frontend | `-Backend` / `--backend`, `-Frontend` / `--frontend` | `tools/check.ps1` / `tools/check.sh` |
| Filtrar los tèsts | `-TestFilter EXPR` / `--test-filter=EXPR` | `-k` a pytest e `--plain-name` a Flutter; parier dins `start.ps1` / `start.sh`, que ajustan tanben `-m "not interop"` en local |
| Migracions | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Revisar l'environament sens arrancar | `-Check` | Doctor: Docker, Python, Flutter, .venv, pòrts |
| Installar las dependéncias que mancan | `-InstallMissing` | winget / gestor del SO + git clone |
| Builds parcials | `-BuildFrontend` / `-BuildBackend` | Demandan Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (demanda macOS) | `tools/build-ios.sh` | Solament sus Mac amb Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Ost correspondente |
| Docker multi-target | `tools/build-all.ps1` | Demanda Docker |
| Verificar la conformitat d'un nose | `python tools/federation_conformance.py <url> [--json]` | Raíç (`tools/`) |
| Regenerar la referéncia d'API | `python tools/gen_api.py --all` | Raíç (`tools/`); combina los prefixes de `main.py` e de cada `APIRouter` e detecta las dependéncias d'auth |
| Verificar la referéncia d'API generada | `python tools/gen_api.py --all --check` | Raíç (`tools/`); verifica que las `API.md` sigan al dia senza las escriure (exit 1 se una difier); executat per lo job `docs-api` de CI |

Lo CLI de conformitat verifica manifest, JWKS, token, directòri, usagis, WebFinger, rapòrts, portabilitat, bridge de chat e flux d'eveniments; torna 1 se i a de fracasses `critical`/`high` e 0 autrament, e `--json` imprime lo rapòrt complet.

## Amelioracions aplicadas (09/10/2026)

1. **`.dockerignore` dins los contextes de build** (`backend/`, `frontend/`). Abans existissian solament dins `backend/docker/` e `frontend/docker/`, que SON PAS lo context de `docker-compose.yml` (`./backend`, `./frontend`). Cada `docker compose build` enviava `.venv/` (centenas de MB), `.dart_tool/`, `build/`, `*.db` e `*.hive` al daemon. Ara lo context es minimal. Excepcion: `!pubspec.lock` es servat per de builds reproductibles.
2. **Config pytest unificada**: suprimit `backend/pytest.ini` (duplicava e eclipsava `pyproject.toml`); tota la config es dins `[tool.pytest.ini_options]` (testpaths, patrons, markers).
3. **CI coherenta**:
   - GitHub: Flutter fixat en `3.50.1` (meteis que lo Dockerfile); `flutter pub run` (obsolèt) → `dart run build_runner`.
   - GitHub e GitLab `backend-test`: `TESTING=true` e `SECRET_KEY=test-secret-key-for-ci-only-32bytes!` (36 bytes, evita `InsecureKeyLengthWarning`; abans lo rate limiter demorava actiu dins los tèsts → 429 esporadics).
   - GitLab `frontend-test`: ajustada la generacion dels adaptadors Hive abans de `flutter test` (paritat amb GitHub).
   - `pip install ruff` → `pip install "ruff==0.17.6"` en GitHub Actions e GitLab; `requirements-dev.txt` fixa `ruff==0.17.6` tanben per desvolopament local.
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` e `avoid_web_libraries_in_flutter`. Verificat: `flutter analyze` net (l'import condicional web/io es lo patron acceptat).
5. **Fix `onReorder` obsolèt** → `onReorderItem` (sens ajustament manual d'indèx); `flutter analyze` passa d'1 info a 0 problems.

## Proposicions (non aplicadas, amb motiv)

1. ~~**Pòrta `ruff format --check` en CI**~~: ja aplicada en GitHub e GitLab après aver corregit ~249 violacions E501/W292 istoricas.
2. **Unificar `.ps1`/`.sh`**: duplican la logica de pòrts/proceses. La via realista es de tirar la matritz dels pòrts a `tools/ports.*` o documentar un sol entrypoint per SO, non pas reescriure ambedos a l'encòp.
3. **Cobertura en CI** (`pytest --cov`, `flutter test --coverage` + lcov): utila quand se espandisson los tèsts de `syncAll` e los routers non cobèrts (vejatz roadmap dins [../README.oc.md](../../README.oc.md)).
