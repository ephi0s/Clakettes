---
name: quality-gate-ci
description: Expert guidance for Clakettes quality gates and CI. Covers ruff check + format --check (line-length 120), pytest tests/ -x -q --tb=short with Alembic upgrade head, flutter analyze/test with build_runner, and the GitHub Actions + GitLab CI job graphs. Use when validating changes or touching CI config.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Sat, 10 Oct 2026 00:00:00 GMT
---
# Clakettes Quality Gate and CI

## Local Gate (run before finishing)

Backend from `backend/`:

```powershell
ruff check .
ruff format --check .
alembic upgrade head
pytest tests/ -x -q --tb=short
```

Frontend from `frontend/`:

```powershell
flutter analyze
dart run build_runner build --delete-conflicting-outputs
flutter test
```

Fix failures before continuing. `ruff check` before `format --check` (same order as CI). Config: `backend/pyproject.toml` (`line-length = 120`, lint selects `E,F,W`; `testpaths = ["tests"]`, `python_files = test_*.py`).

## GitHub Actions (`.github/workflows/ci.yml`)

Push/PR to `main,develop` on `ubuntu-26.04` (Python 3.12, Flutter 3.47.3, ruff 0.15.22). Parallel jobs `backend-lint`, `frontend-lint`, `backend-test`, `frontend-test` gate `docker-build` via `needs`.

- `backend-test` runs against MariaDB 11 service (`DATABASE_URL=mariadb+pymysql://...`, `TESTING=true`, `SECRET_KEY=test-secret-key-for-ci-only`), with `alembic upgrade head` before pytest.
- `frontend-test` runs build_runner before `flutter test`.
- `docker-build` builds `backend`, `frontend`, `backend-prod`, `frontend-prod` images.

## GitLab CI (`.gitlab-ci.yml`)

Stages `lint → test → build`, same commands (pytest via `python -m pytest`). `docker-build` runs only on `main` and pushes `$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA-backend/frontend`.

## Scale

37 backend test files (~1400 tests), 69 frontend test files, 18 Alembic migrations. Never skip the gate on changes touching `backend/app/` or `frontend/lib/`.

## Docs de oro (anti-desfase)

La documentación va en español (estilo canario, ustedes) y nunca queda desfasada:
todo cambio que la afecte actualiza TODA la info pertinente en el mismo cambio.

- Cifras: routers (36 ficheros, 33 con `APIRouter`), servicios (36), modelos (34),
  schemas (33), migraciones (18), tests backend (37 ficheros, ~1400) y frontend
  (69 ficheros). Están en `AGENTS.md`, `README.md`, `docs/BACKEND.md`,
  `docs/ARQUITECTURA.md`, `docs/ADMINISTRACION.md` y `docs/AUDITORIA.md` (addendum, sin reescribir).
- Endpoints nuevos/movidos: regenera `docs/API.md` con `python tools/gen_api.py`
  y revisa `docs/USO.md` + `docs/SEGURIDAD.md` (auth, pagos, RGPD).
- Flags de arranque: ayuda de `start.ps1`/`start.bat`/`start.sh` + `docs/USO.md` +
  `docs/HERRAMIENTAS.md` + línea de `AGENTS.md`.
- Roadmap y variables: `README.md` + `backend/.env.example` al día.
