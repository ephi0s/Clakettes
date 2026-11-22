# Desenvolupament — convencions

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: afegir un endpoint

1. Schema a `app/schemas/` (Pydantic v2; rols tancats amb `Literal`).
2. Lògica a `app/services/` heretant `BaseService` (`paginate` /
   `paginate_filtered`; sense `HTTPException` en codi nou).
3. Ruta a `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` i
   `require_*` de `permissions.py`. Auth opcional només per a lectura pública.
4. Migració si canvia l'esquema: `alembic revision --autogenerate -m "..."`.
5. Test a `tests/test_<dominio>.py` (200 + 401 sense token + 403 sense permís +
   404 inexistent).

## Frontend: afegir una pantalla

1. Servei: mètode al fitxer de `lib/services/api/` del seu domini.
2. Pantalla a `lib/screens/` <600 línies: extreure a `lib/widgets/` la UI
   reutilitzable (bombolles, targetes, barres, seccions).
3. Avisos amb `showAppSnack`; esborrats amb `showConfirmDialog`; errors amb
   `ErrorStateWidget` i reintent.
4. Textos a `assets/l10n/app_en.arb` primer (fallback) + resta de locals (823 claus); executa `flutter test test/l10n/arb_parity_test.dart`: exigeix les mateixes claus i placeholders als 9 ARB (referència `es`).
5. Test a `test/screens/` o `test/widgets/` (els widgets amb `l10n`
   necessiten un `pump()` extra després de `pumpWidget`).

## Dependències (Dependabot)

- pip a `/backend` i pub a `/frontend`, setmanals (dilluns), agrupats en `backend-deps`/`frontend-deps`; s'ignoren actualitzacions `version-update:semver-major`.
- Patch/minor: `.github/workflows/dependabot-automerge.yml` activa `gh pr merge --auto --squash` només per a `dependabot[bot]`; el merge efectiu exigeix CI verda. Major: revisió manual.
- `.github/workflows/dependabot-rebase.yml` rebaseja els PRs oberts els dilluns 04:17 UTC i sota `workflow_dispatch`. Detall a [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Portes de qualitat

- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Després de canviar endpoints o rutes, regenera la referència amb `python tools/gen_api.py --all` (combina prefixos de `main.py` i de cada `APIRouter`).
