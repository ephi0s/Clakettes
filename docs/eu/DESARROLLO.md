# Garapena — konbentzioak

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend-a: endpoint bat gehitzea

1. Schema `app/schemas/`-n (Pydantic v2; rol itxiak `Literal`-ekin).
2. Logika `app/services/`-n `BaseService` heredatuz (`paginate` /
   `paginate_filtered`; `HTTPException` gabe kode berrian).
3. Ibilbidea `app/routers/`-n + `get_or_404(db, Modelo, id, "Etiketa")` eta
   `permissions.py`-ko `require_*`. Auth aukerakoa irakurketa publikorako soilik.
4. Migrazioa eskema aldatzen bada: `alembic revision --autogenerate -m "..."`.
5. Test-a `tests/test_<dominio>.py`-n (200 + 401 token gabe + 403 baimen gabe +
   404 existitzen ez dena).

## Frontend-a: pantaila bat gehitzea

1. Zerbitzua: metodoa bere domeinuko `lib/services/api/` fitxategian.
2. Pantaila `lib/screens/`-n <600 lerro: erauzi `lib/widgets/`-ra UI
   berrerabilgarria (burbuilak, txartelak, barrak, sekzioak).
3. Abisuak `showAppSnack`-ekin; ezabaketak `showConfirmDialog`-ekin; erroreak
   `ErrorStateWidget`-ekin eta saiakera-errepikapenarekin.
4. Testuak `assets/l10n/app_en.arb`-n lehenik (fallback) + gainerako locale-ak;
   exekutatu `flutter test test/l10n/arb_parity_test.dart`: ARB guztiek gako eta placeholder
   berberak izatea exigitzen du (erreferentzia `es`).
5. Test-a `test/screens/` edo `test/widgets/`-n (`l10n`-dun widget-ek
   `pump()` gehigarri bat behar dute `pumpWidget` ondoren).

## Mendekotasunak (Dependabot)

- pip `/backend`-n eta pub `/frontend`-n, astero (astelehena), `backend-deps`/`frontend-deps` taldeetan; `version-update:semver-major` eguneraketak baztertzen dira.
- Patch/minor: `.github/workflows/dependabot-automerge.yml`-ek `gh pr merge --auto --squash` aktibatzen du `dependabot[bot]`-entzat soilik; benetako merge-a CI berdea eskatzen du. Major: eskuzko berrikuspena.
- `.github/workflows/dependabot-rebase.yml`-ek irekitako PRak astelehenetan 04:17 UTC-n rebaseatzen ditu eta `workflow_dispatch` bidez. Xehetasuna [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) fitxategian.

## Kalitate-ateak

- Komando bakarra: `tools/check.ps1` (Windows) / `tools/check.sh` (POSIX) exekutatzen du ate osoa; argumenturik gabe = ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test, `-Quick` / `--quick`-ekin soilik ruff + flutter analyze; `-Backend`/`--backend`, `-Frontend`/`--frontend` eta `-TestFilter EXPR`/`--test-filter=EXPR`-k irismena mugatzen dute (`start.ps1` / `start.sh` abiarazleetan filtro berak `-k` pasatzen dio pytest-i eta `--plain-name` Flutter-i, eta tokikoan `-m "not interop"` ere gehitzen dute).
- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Endpoint edo ibilbideak aldatu ondoren, birsortu erreferentzia `python tools/gen_api.py --all` bidez (`main.py`-ko eta `APIRouter` bakoitzeko aurrizkiak konbinatzen ditu).

