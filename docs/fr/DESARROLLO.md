# Développement — conventions

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend : ajouter un endpoint

1. Schema dans `app/schemas/` (Pydantic v2 ; rôles fermés avec `Literal`).
2. Logique dans `app/services/` héritant `BaseService` (`paginate` /
   `paginate_filtered` ; sans `HTTPException` dans code nouveau).
3. Route dans `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` et
   `require_*` de `permissions.py`. Auth optionnelle seulement pour lecture publique.
4. Migration si le schéma change : `alembic revision --autogenerate -m "..."`.
5. Test dans `tests/test_<dominio>.py` (200 + 401 sans token + 403 sans permission +
   404 inexistant). Régénérer [API.md](../es/API.md) avec `tools/gen_api.py`.

## Frontend : ajouter un écran

1. Service : méthode dans le fichier de `lib/services/api/` de son domaine.
2. Écran dans `lib/screens/` <600 lignes : extraire vers `lib/widgets/` l'UI
   réutilisable (bulles, cartes, barres, sections).
3. Avis avec `showAppSnack` ; suppressions avec `showConfirmDialog` ; erreurs avec
   `ErrorStateWidget` et réessai.
4. Textes dans `assets/l10n/en.arb` d'abord (fallback) + reste des locales ;
   0 clés manquantes vérifié.
5. Test dans `test/screens/` ou `test/widgets/` (les widgets avec `l10n`
   ont besoin d'un `pump()` supplémentaire après `pumpWidget`).

## Portes (CI les exige)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
