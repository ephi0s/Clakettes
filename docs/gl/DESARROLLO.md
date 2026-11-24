# Desenvolvemento — convencións

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: engadir un endpoint

1. Schema en `app/schemas/` (Pydantic v2; roles pechados con `Literal`).
2. Lóxica en `app/services/` herdando `BaseService` (`paginate` /
   `paginate_filtered`; sen `HTTPException` en código novo).
3. Ruta en `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` e
   `require_*` de `permissions.py`. Auth opcional só para lectura pública.
4. Migración se cambia o esquema: `alembic revision --autogenerate -m "..."`.
5. Test en `tests/test_<dominio>.py` (200 + 401 sen token + 403 sen permiso +
   404 inexistente).

## Frontend: engadir unha pantalla

1. Servizo: método no ficheiro de `lib/services/api/` do seu dominio.
2. Pantalla en `lib/screens/` <600 liñas: extraer a `lib/widgets/` a UI
   reutilizable (burbullas, tarxetas, barras, seccións).
3. Avisos con `showAppSnack`; borrados con `showConfirmDialog`; erros con
   `ErrorStateWidget` e reintento.
4. Textos en `assets/l10n/app_en.arb` primeiro (fallback) + resto de locales; executa `flutter test test/l10n/arb_parity_test.dart`: esixe as mesmas claves e placeholders en todos os ARB (referencia `es`).
5. Test en `test/screens/` ou `test/widgets/` (os widgets con `l10n`
   necesitan un `pump()` extra tras `pumpWidget`).

## Dependencias (Dependabot)

- pip en `/backend` e pub en `/frontend`, semanais (luns), agrupados en `backend-deps`/`frontend-deps`; ignóranse actualizacións `version-update:semver-major`.
- Patch/minor: `.github/workflows/dependabot-automerge.yml` activa `gh pr merge --auto --squash` só para `dependabot[bot]`; o merge efectivo esixe CI verde. Major: revisión manual.
- `.github/workflows/dependabot-rebase.yml` rebasea os PRs abertos os luns 04:17 UTC e baixo `workflow_dispatch`. Detalle en [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Portas de calidade

- Comando único: `tools/check.ps1` (Windows) / `tools/check.sh` (POSIX) executa toda a porta; sen argumentos = ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test, con `-Quick` / `--quick` só ruff + flutter analyze; `-Backend`/`--backend`, `-Frontend`/`--frontend` e `-TestFilter EXPR`/`--test-filter=EXPR` limitan o alcance (nos launchers `start.ps1` / `start.sh` o mesmo filtro pasa `-k` a pytest e `--plain-name` a Flutter, que engaden tamén `-m "not interop"` en local).
- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Tras cambiar endpoints ou rutas, xera a referencia con `python tools/gen_api.py --all` (combina prefixos de `main.py` e de cada `APIRouter`).


