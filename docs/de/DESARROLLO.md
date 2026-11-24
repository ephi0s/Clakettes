# Entwicklung — Konventionen

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: Endpunkt hinzufügen

1. Schema in `app/schemas/` (Pydantic v2; Rollen geschlossen mit `Literal`).
2. Logik in `app/services/` erbt `BaseService` (`paginate` / `paginate_filtered`; kein `HTTPException` in neuem Code).
3. Route in `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` und `require_*` aus `permissions.py`. Optionale Auth nur für öffentliche Lesung.
4. Migration wenn Schema sich ändert: `alembic revision --autogenerate -m "..."`.
5. Test in `tests/test_<dominio>.py` (200 + 401 ohne Token + 403 ohne Berechtigung + 404 nicht vorhanden). [API.md](API.md) neu generieren mit `tools/gen_api.py`.

## Frontend: Bildschirm hinzufügen

1. Dienst: Methode in der Datei von `lib/services/api/` der eigenen Domäne.
2. Bildschirm in `lib/screens/` <600 Zeilen: wiederverwendbare UI nach `lib/widgets/` extrahieren (Blasen, Karten, Leisten, Abschnitte).
3. Hinweise mit `showAppSnack`; Löschungen mit `showConfirmDialog`; Fehler mit `ErrorStateWidget` und Wiederholung.
4. Texte zuerst in `assets/l10n/app_en.arb` (Fallback) + restliche Locales; führe `flutter test test/l10n/arb_parity_test.dart` aus: es erfordert identische Schlüssel und Placeholders in allen ARBs (Referenz `es`).
5. Test in `test/screens/` oder `test/widgets/` (Widgets mit `l10n` benötigen ein zusätzliches `pump()` nach `pumpWidget`).

## Abhängigkeiten (Dependabot)

- pip in `/backend` und pub in `/frontend`, wöchentlich (montags), gruppiert in `backend-deps`/`frontend-deps`; Aktualisierungen vom Typ `version-update:semver-major` werden ignoriert.
- Patch/Minor: `.github/workflows/dependabot-automerge.yml` aktiviert `gh pr merge --auto --squash` nur für `dependabot[bot]`; der tatsächliche Merge erfordert grünes CI. Major: manuelle Prüfung.
- `.github/workflows/dependabot-rebase.yml` führt einen Rebase offener PRs montags 04:17 UTC und bei `workflow_dispatch` durch. Details in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Qualitätstore

- Einzelner Befehl: `tools/check.ps1` (Windows) / `tools/check.sh` (POSIX) führt die gesamte Store aus; ohne Argumente = ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test, mit `-Quick` / `--quick` nur ruff + flutter analyze; `-Backend`/`--backend`, `-Frontend`/`--frontend` und `-TestFilter EXPR`/`--test-filter=EXPR` schränken den Umfang ein (in den Launchern `start.ps1` / `start.sh` übergibt derselbe Filter `-k` an pytest und `--plain-name` an Flutter, und sie ergänzen lokal zusätzlich `-m "not interop"`).
- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Nach Änderungen an Endpoints oder Routen die Referenz neu erzeugen mit `python tools/gen_api.py --all` (kombiniert Präfixe aus `main.py` und jedem `APIRouter`).