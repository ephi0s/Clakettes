# Desenvolupament — convencions

[ES](DESARROLLO.md) · [EN](DESARROLLO.en.md) · [FR](DESARROLLO.fr.md) · [DE](DESARROLLO.de.md) · [IT](DESARROLLO.it.md) · [CA](DESARROLLO.ca.md) · [EU](DESARROLLO.eu.md) · [GL](DESARROLLO.gl.md) · [OC](DESARROLLO.oc.md)

## Backend: afegir un endpoint

1. Schema a `app/schemas/` (Pydantic v2; rols tancats amb `Literal`).
2. Lògica a `app/services/` heretant `BaseService` (`paginate` /
   `paginate_filtered`; sense `HTTPException` en codi nou).
3. Ruta a `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` i
   `require_*` de `permissions.py`. Auth opcional només per a lectura pública.
4. Migració si canvia l'esquema: `alembic revision --autogenerate -m "..."`.
5. Test a `tests/test_<dominio>.py` (200 + 401 sense token + 403 sense permís +
   404 inexistent). Regenerar [API.md](API.md) amb `tools/gen_api.py`.

## Frontend: afegir una pantalla

1. Servei: mètode al fitxer de `lib/services/api/` del seu domini.
2. Pantalla a `lib/screens/` <600 línies: extreure a `lib/widgets/` la UI
   reutilitzable (bombolles, targetes, barres, seccions).
3. Avisos amb `showAppSnack`; esborrats amb `showConfirmDialog`; errors amb
   `ErrorStateWidget` i reintent.
4. Textos a `assets/l10n/en.arb` primer (fallback) + resta de locales;
   0 claus absents verificat.
5. Test a `test/screens/` o `test/widgets/` (els widgets amb `l10n`
   necessiten un `pump()` extra després de `pumpWidget`).

## Portes (CI les exigeix)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
