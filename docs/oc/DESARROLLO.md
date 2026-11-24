# Desvolopament — convencions

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](DESARROLLO.md)

## Backend: apondre un endpoint

1. Schema en `app/schemas/` (Pydantic v2; ròtles tampats amb `Literal`).
2. Logica en `app/services/` eiretant `BaseService` (`paginate` /
   `paginate_filtered`; sens `HTTPException` en còde nòu).
3. Rota en `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` e
   `require_*` de `permissions.py`. Auth opcionau sonque per lectura publica.
4. Migracion se cambia l'esquèma: `alembic revision --autogenerate -m "..."`.
5. Tèst en `tests/test_<dominio>.py` (200 + 401 sens token + 403 sens permission +
   404 inexistent).

## Frontend: apondre un ecran

1. Servici: metòde dins lo fichièr de `lib/services/api/` de son domeni.
2. Ecran en `lib/screens/` <600 linhas: extraire cap a `lib/widgets/` l'UI
   reutilizabla (borbolhas, cartas, barras, seccions).
3. Avises amb `showAppSnack`; escafaments amb `showConfirmDialog`; errors amb
   `ErrorStateWidget` e tornada d'ensajar.
4. Tèxtes en `assets/l10n/app_en.arb` d'en primièr (fallback) + rèsta de locales;
   executatz `flutter test test/l10n/arb_parity_test.dart`: exigeís
   las meteissas claus e placeholders dins totes los ARB (referéncia `es`).
5. Tèst en `test/screens/` o `test/widgets/` (los widgets amb `l10n`
   an besonh d'un `pump()` extra aprèp `pumpWidget`).

## Dependéncias (Dependabot)

- pip en `/backend` e pub en `/frontend`, setmanals (diluns), gropats en `backend-deps`/`frontend-deps`; las actualizacions `version-update:semver-major` son ignoradas.
- Patch/minor: `.github/workflows/dependabot-automerge.yml` activa `gh pr merge --auto --squash` solament per `dependabot[bot]`; lo merge efectiu exigís CI verda. Major: revision manuala.
- `.github/workflows/dependabot-rebase.yml` rebaseja los PRs dobèrts los diluns a 04:17 UTC e jos `workflow_dispatch`. Detalh dins [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Pòrtas de qualitat

- Comanda unica: `tools/check.ps1` (Windows) / `tools/check.sh` (POSIX) executa tota la pòrta; sens arguments = ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test, amb `-Quick` / `--quick` sonque ruff + flutter analyze; `-Backend`/`--backend`, `-Frontend`/`--frontend` e `-TestFilter EXPR`/`--test-filter=EXPR` limitan lo camp (dins los launchers `start.ps1` / `start.sh` lo meteis filtre passa `-k` a pytest e `--plain-name` a Flutter, que ajustan tanben `-m "not interop"` en local).
- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Après cambiar endpoints o rotas, regeneratz la referéncia amb `python tools/gen_api.py --all` (combina los prefixes de `main.py` e de cada `APIRouter`).
