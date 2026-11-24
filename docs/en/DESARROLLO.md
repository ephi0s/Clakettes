# Development — conventions

[ES](../es/DESARROLLO.md) · [EN](DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: add an endpoint

1. Schema in `app/schemas/` (Pydantic v2; roles closed with `Literal`).
2. Logic in `app/services/` inheriting `BaseService` (`paginate` / `paginate_filtered`; no `HTTPException` in new code).
3. Route in `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` and `require_*` from `permissions.py`. Optional auth only for public read.
4. Migration if schema changes: `alembic revision --autogenerate -m "..."`.
5. Test in `tests/test_<dominio>.py` (200 + 401 without token + 403 without permission + 404 non-existent).

## Frontend: add a screen

1. Service: method in the file of `lib/services/api/` for its domain.
2. Screen in `lib/screens/` <600 lines: extract to `lib/widgets/` the reusable UI (bubbles, cards, bars, sections).
3. Notices with `showAppSnack`; deletions with `showConfirmDialog`; errors with `ErrorStateWidget` and retry.
4. Texts in `assets/l10n/app_en.arb` first (fallback) + the remaining locales in `assets/l10n/`; run `flutter test test/l10n/arb_parity_test.dart`: it requires the same keys and placeholders in all ARBs (`es` reference).
5. Test in `test/screens/` or `test/widgets/` (widgets with `l10n` need an extra `pump()` after `pumpWidget`).

## Dependencies (Dependabot)

- pip in `/backend` and pub in `/frontend`, weekly (Monday), grouped in `backend-deps`/`frontend-deps`; `version-update:semver-major` updates are ignored.
- Patch/minor: `.github/workflows/dependabot-automerge.yml` enables `gh pr merge --auto --squash` only for `dependabot[bot]`; the actual merge requires green CI. Major: manual review.
- `.github/workflows/dependabot-rebase.yml` rebases open PRs on Monday 04:17 UTC and on `workflow_dispatch`. Detail in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Quality gates

- Single command: `tools/check.ps1` (Windows) / `tools/check.sh` (POSIX) runs the whole gate; with no args = ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test, with `-Quick` / `--quick` only ruff + flutter analyze; `-Backend`/`--backend`, `-Frontend`/`--frontend` and `-TestFilter EXPR`/`--test-filter=EXPR` narrow the scope (in the `start.ps1` / `start.sh` launchers the same filter passes `-k` to pytest and `--plain-name` to Flutter, and they also add `-m "not interop"` locally).
- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- After changing endpoints or routes, regenerate the reference with `python tools/gen_api.py --all` (combines prefixes from `main.py` and each `APIRouter`).

