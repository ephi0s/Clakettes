# Desenvolvemento — convencións

[ES](DESARROLLO.md) · [EN](DESARROLLO.en.md) · [FR](DESARROLLO.fr.md) · [DE](DESARROLLO.de.md) · [IT](DESARROLLO.it.md) · [CA](DESARROLLO.ca.md) · [EU](DESARROLLO.eu.md) · [GL](DESARROLLO.gl.md) · [OC](DESARROLLO.oc.md)

## Backend: engadir un endpoint

1. Schema en `app/schemas/` (Pydantic v2; roles pechados con `Literal`).
2. Lóxica en `app/services/` herdando `BaseService` (`paginate` /
   `paginate_filtered`; sen `HTTPException` en código novo).
3. Ruta en `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` e
   `require_*` de `permissions.py`. Auth opcional só para lectura pública.
4. Migración se cambia o esquema: `alembic revision --autogenerate -m "..."`.
5. Test en `tests/test_<dominio>.py` (200 + 401 sen token + 403 sen permiso +
   404 inexistente). Rexenerar [API.md](API.gl.md) con `tools/gen_api.py`.

## Frontend: engadir unha pantalla

1. Servizo: método no ficheiro de `lib/services/api/` do seu dominio.
2. Pantalla en `lib/screens/` <600 liñas: extraer a `lib/widgets/` a UI
   reutilizable (burbullas, tarxetas, barras, seccións).
3. Avisos con `showAppSnack`; borrados con `showConfirmDialog`; erros con
   `ErrorStateWidget` e reintento.
4. Textos en `assets/l10n/en.arb` primeiro (fallback) + resto de locales;
   0 claves ausentes verificado.
5. Test en `test/screens/` ou `test/widgets/` (os widgets con `l10n`
   necesitan un `pump()` extra tras `pumpWidget`).

## Portas (CI esíxeas)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
