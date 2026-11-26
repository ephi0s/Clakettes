# Eines build / test / dev — Clakettes

[ES](../es/HERRAMIENTAS.md) · [EN](../en/HERRAMIENTAS.md) · [FR](../fr/HERRAMIENTAS.md) · [DE](../de/HERRAMIENTAS.md) · [IT](../it/HERRAMIENTAS.md) · [CA](HERRAMIENTAS.md) · [EU](../eu/HERRAMIENTAS.md) · [GL](../gl/HERRAMIENTAS.md) · [OC](../oc/HERRAMIENTAS.md)

## Matriu de comandos

| Objectiu | Comando | On |
|---|---|---|
| Dev backend+frontend | `.\start.ps1` / `./start.sh` | Arrel (Docker si està disponible, local si no) |
| Només backend / frontend | `-NoFrontend` / `-NoBackend` | `start.ps1` / `--no-frontend` a `start.sh` |
| Web en navegador de desenvolupament | default / `-Dev` | Docker dev o local; `-Web` força el mode local |
| Prod local (build web + serve) | `-Final` | `start.ps1` / `start.sh` |
| Tests backend | `-TestBackend` | pytest a `.venv` o Docker |
| Tests frontend | `-TestFrontend` | `flutter test` o Docker |
| Porta de qualitat (tot) | `tools/check.ps1` / `tools/check.sh` | Arrel; sense args: ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test |
| Porta ràpida | `-Quick` / `--quick` | Només ruff + flutter analyze |
| Només backend / frontend | `-Backend` / `--backend`, `-Frontend` / `--frontend` | `tools/check.ps1` / `tools/check.sh` |
| Filtrar tests | `-TestFilter EXPR` / `--test-filter=EXPR` | `-k` a pytest i `--plain-name` a Flutter; igual en `start.ps1` / `start.sh`, que afegeixen `-m "not interop"` en local |
| Migracions | `-Migrate` / `-TestMigration` (MariaDB) | alembic |
| Revisar entorn sense arrancar | `-Check` | Doctor: Docker, Python, Flutter, .venv, ports |
| Instal·lar dependències que falten | `-InstallMissing` | winget / gestor del SO + git clone |
| Builds parcials | `-BuildFrontend` / `-BuildBackend` | Requereixen Docker |
| APK Android | `flutter build apk --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| AppBundle (Play Store) | `flutter build appbundle --release --dart-define=BACKEND_URL=<url>` | `frontend/` |
| iOS/iPad (requereix macOS) | `tools/build-ios.sh` | Només en Mac amb Xcode |
| macOS / Windows / Linux | `tools/build-macos.sh` / `flutter build windows` / `flutter build linux` | Host corresponent |
| Docker multi-target | `tools/build-all.ps1` | Requereix Docker |
| Verificar conformitat d'un node | `python tools/federation_conformance.py <url> [--json]` | Arrel (`tools/`) |
| Regenerar referència d'API | `python tools/gen_api.py --all` | Arrel (`tools/`); combina prefixos de `main.py` i de cada `APIRouter` i detecta dependències d'auth |
| Verificar referència d'API generada | `python tools/gen_api.py --all --check` | Arrel (`tools/`); comprova que les `API.md` estan al dia sense escriure-les (exit 1 si alguna difereix); ho executa el job `docs-api` de CI |
| Auditoria de dependències (OSV) | `python tools/audit_deps.py --requirements backend/requirements.txt --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock --venv backend/.venv --fail-on fixable` | Arrel (`tools/`); CVE/GHSA en requirements, `pubspec.lock` i venv |

El CLI de conformitat comprova manifest, JWKS, token, directori, usuaris, WebFinger, reportes, portabilitat, bridge de xat i stream d'esdeveniments; retorna 1 si hi ha fallades `critical`/`high` i 0 en cas contrari, i `--json` imprimeix l'informe complet.

L'script d'auditoria retorna 1 si hi ha avisos corregibles (`--fail-on fixable`); un avís irreparable que aparegui només al `.venv` local i no al graf de requirements no forma part del projecte. Amb `--venv --show-orphans` es llesten els paquets instal·lats que no figuren als requirements i que ningú no requereix (orfes del venv local), per poder desinstal·lar-los.

## Millores aplicades (09/10/2026)

1. **`.dockerignore` en els contextos de build** (`backend/`, `frontend/`). Abans només existien a `backend/docker/` i `frontend/docker/`, que NO són el context de `docker-compose.yml` (`./backend`, `./frontend`). Cada `docker compose build` enviava `.venv/` (centenars de MB), `.dart_tool/`, `build/`, `*.db` i `*.hive` al dimoni. Ara el context és mínim. Excepció: `!pubspec.lock` es conserva per a builds reproducibles.
2. **Config pytest unificada**: eliminat `backend/pytest.ini` (duplicava i eclipsava `pyproject.toml`); tota la config viu a `[tool.pytest.ini_options]` (testpaths, patrons, markers).
3. **CI coherent**:
   - GitHub: Flutter fixat a `3.50.1` (igual que el Dockerfile); `flutter pub run` (obsolet) → `dart run build_runner`.
   - GitHub i GitLab `backend-test`: `TESTING=true` i `SECRET_KEY=test-secret-key-for-ci-only-32bytes!` (36 bytes, evita `InsecureKeyLengthWarning`; abans el rate limiter seguia actiu en tests → 429 esporàdics).
   - GitLab `frontend-test`: afegida generació d'adaptadors Hive abans de `flutter test` (paritat amb GitHub).
   - `pip install ruff` → `pip install "ruff==0.17.6"` a GitHub Actions i GitLab; `requirements-dev.txt` fixa `ruff==0.17.6` també per al desenvolupament local.
    - CodeQL (configuració per defecte de GitHub) analitza el backend Python; Dart no està cobert per CodeQL.
4. **Lints multiplataforma** (`analysis_options.yaml`): `avoid_print` i `avoid_web_libraries_in_flutter`. Verificat: `flutter analyze` net (l'import condicional web/io és el patró acceptat).
5. **Fix `onReorder` obsolet** → `onReorderItem` (sense ajust manual d'índex); `flutter analyze` passa d'1 info a 0 issues.

## Propostes (no aplicades, amb motiu)

1. ~~**Gate `ruff format --check` a CI**~~: ja aplicat a GitHub i GitLab després de corregir ~249 violacions E501/W292 històriques.
2. **Unificar `.ps1`/`.sh`**: dupliquen la lògica de ports/processos. La via realista és extreure la matriu de ports a `tools/ports.*` o documentar un únic entrypoint per SO, no reescriure tots dos alhora.
3. **Cobertura a CI** (`pytest --cov`, `flutter test --coverage` + lcov): útil quan s'ampliïn els tests de `syncAll` i routers sense cobrir (vegeu roadmap a [../README.ca.md](../../README.ca.md)).
