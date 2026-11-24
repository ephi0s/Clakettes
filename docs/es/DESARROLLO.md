# Desarrollo — convenciones

[ES](DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: añadir un endpoint

1. Schema en `app/schemas/` (Pydantic v2; roles cerrados con `Literal`).
2. Lógica en `app/services/` heredando `BaseService` (`paginate` / `paginate_filtered`; sin `HTTPException` en código nuevo).
3. Ruta en `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` y `require_*` de `permissions.py`. Auth opcional solo para lectura pública.
4. Migración si cambia el esquema: `alembic revision --autogenerate -m "..."`.
5. Test en `tests/test_<dominio>.py` (200 + 401 sin token + 403 sin permiso + 404 inexistente).

## Frontend: añadir una pantalla

1. Servicio: método en el fichero de `lib/services/api/` de su dominio.
2. Pantalla en `lib/screens/` <600 líneas: extraer a `lib/widgets/` la UI reutilizable (burbujas, tarjetas, barras, secciones).
3. Avisos con `showAppSnack`; borrados con `showConfirmDialog`; errores con `ErrorStateWidget` y reintento.
4. Textos en `assets/l10n/app_en.arb` primero (fallback) + el resto de los locales de `assets/l10n/`; ejecuta `flutter test test/l10n/arb_parity_test.dart`: exige las mismas claves y placeholders en todos los ARB (referencia `es`).
5. Test en `test/screens/` o `test/widgets/` (los widgets con `l10n` necesitan un `pump()` extra tras `pumpWidget`).

## Dependencias (Dependabot)

- pip en `/backend` y pub en `/frontend`, semanales (lunes), agrupados en `backend-deps`/`frontend-deps`; se ignoran actualizaciones `version-update:semver-major`.
- Patch/minor: `.github/workflows/dependabot-automerge.yml` activa `gh pr merge --auto --squash` solo para `dependabot[bot]`; el merge efectivo exige CI verde. Major: revisión manual.
- `.github/workflows/dependabot-rebase.yml` rebasea los PRs abiertos los lunes 04:17 UTC y bajo `workflow_dispatch`. Detalle en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Puertas de calidad

- Comando único: `tools/check.ps1` (Windows) / `tools/check.sh` (POSIX) ejecuta toda la puerta; sin args = ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test, con `-Quick` / `--quick` solo ruff + flutter analyze; `-Backend`/`--backend`, `-Frontend`/`--frontend` y `-TestFilter EXPR`/`--test-filter=EXPR` limitan el alcance (en los launchers `start.ps1` / `start.sh` el mismo filtro pasa `-k` a pytest y `--plain-name` a Flutter, que además añaden `-m "not interop"` en local).
- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Tras cambiar endpoints o rutas, regenera la referencia con `python tools/gen_api.py --all` (combina prefijos de `main.py` y de cada `APIRouter`).

