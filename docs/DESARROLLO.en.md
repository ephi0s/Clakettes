# Development — conventions

## Backend: adding an endpoint

1. Schema in `app/schemas/` (Pydantic v2; closed roles with `Literal`).
2. Logic in `app/services/` inheriting `BaseService` (`paginate` /
   `paginate_filtered`; no `HTTPException` in new code).
3. Route in `app/routers/` + `get_or_404(db, Model, id, "Label")` and
   `require_*` from `permissions.py`. Optional auth for public reads only.
4. Migration if the schema changes: `alembic revision --autogenerate -m "..."`.
5. Test in `tests/test_<domain>.py` (200 + 401 without token + 403 without permission +
   404 for missing). Regenerate [API.md](API.md) with `tools/gen_api.py`.

## Frontend: adding a screen

1. Service: method in the `lib/services/api/` file for its domain.
2. Screen in `lib/screens/` under 600 lines: extract reusable UI to `lib/widgets/`
   (bubbles, cards, bars, sections).
3. Notices with `showAppSnack`; deletions with `showConfirmDialog`; errors with
   `ErrorStateWidget` and retry.
4. Strings in `assets/l10n/en.arb` first (fallback) + remaining locales;
   0 missing keys verified.
5. Test in `test/screens/` or `test/widgets/` (widgets with `l10n`
   need an extra `pump()` after `pumpWidget`).

## Gates (CI enforces them)

| Command | Location |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` before test | `frontend/` |
