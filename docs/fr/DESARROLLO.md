# Développement — conventions

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend : ajouter un endpoint

1. Schéma dans `app/schemas/` (Pydantic v2 ; rôles fermés avec `Literal`).
2. Logique dans `app/services/` héritant de `BaseService` (`paginate` / `paginate_filtered` ; pas de `HTTPException` dans le nouveau code).
3. Route dans `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` et `require_*` de `permissions.py`. Auth optionnel seulement pour la lecture publique.
4. Migration si le schéma change : `alembic revision --autogenerate -m "..."`.
5. Test dans `tests/test_<dominio>.py` (200 + 401 sans token + 403 sans permission + 404 inexistant).

## Frontend : ajouter un écran

1. Service : méthode dans le fichier de `lib/services/api/` de son domaine.
2. Écran dans `lib/screens/` <600 lignes : extraire dans `lib/widgets/` l'UI réutilisable (bulles, cartes, barres, sections).
3. Avis avec `showAppSnack` ; suppressions avec `showConfirmDialog` ; erreurs avec `ErrorStateWidget` et réessai.
4. Textes dans `assets/l10n/app_en.arb` d'abord (fallback) + le reste des locales de `assets/l10n/` ; exécutez `flutter test test/l10n/arb_parity_test.dart` : exige les mêmes clés et placeholders dans tous les ARB (référence `es`).
5. Test dans `test/screens/` ou `test/widgets/` (les widgets avec `l10n` nécessitent un `pump()` supplémentaire après `pumpWidget`).

## Dépendances (Dependabot)

- pip dans `/backend` et pub dans `/frontend`, hebdomadaires (lundi), regroupés dans `backend-deps`/`frontend-deps` ; les mises à jour `version-update:semver-major` sont ignorées.
- Patch/minor : `.github/workflows/dependabot-automerge.yml` active `gh pr merge --auto --squash` seulement pour `dependabot[bot]` ; le merge effectif exige une CI verte. Major : revue manuelle.
- `.github/workflows/dependabot-rebase.yml` rebase les PR ouvertes le lundi à 04:17 UTC et sur `workflow_dispatch`. Détail dans [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Portes de qualité

- Commande unique : `tools/check.ps1` (Windows) / `tools/check.sh` (POSIX) exécute toute la porte ; sans arguments = ruff check + ruff format --check + pytest (`-m "not interop"`) + flutter test, avec `-Quick` / `--quick` seulement ruff + flutter analyze ; `-Backend`/`--backend`, `-Frontend`/`--frontend` et `-TestFilter EXPR`/`--test-filter=EXPR` limitent la portée (dans les launchers `start.ps1` / `start.sh`, le même filtre passe `-k` à pytest et `--plain-name` à Flutter, et ils ajoutent aussi `-m "not interop"` en local).
- Backend : `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend : `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Après changement d'endpoints ou de routes, régénérez la référence avec `python tools/gen_api.py --all` (combine les préfixes de `main.py` et de chaque `APIRouter`).

