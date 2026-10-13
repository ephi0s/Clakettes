# Desarrollo — convenciones

[ES](DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: añadir un endpoint

1. Schema en `app/schemas/` (Pydantic v2; roles cerrados con `Literal`).
2. Lógica en `app/services/` heredando `BaseService` (`paginate` /
   `paginate_filtered`; sin `HTTPException` en código nuevo).
3. Ruta en `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` y
   `require_*` de `permissions.py`. Auth opcional solo para lectura pública.
4. Migración si cambia el esquema: `alembic revision --autogenerate -m "..."`.
5. Test en `tests/test_<dominio>.py` (200 + 401 sin token + 403 sin permiso +
   404 inexistente). Regenerar [API.md](API.md) con `tools/gen_api.py`.

## Frontend: añadir una pantalla

1. Servicio: método en el fichero de `lib/services/api/` de su dominio.
2. Pantalla en `lib/screens/` <600 líneas: extraer a `lib/widgets/` la UI
   reutilizable (burbujas, tarjetas, barras, secciones).
3. Avisos con `showAppSnack`; borrados con `showConfirmDialog`; errores con
   `ErrorStateWidget` y reintento.
4. Textos en `assets/l10n/en.arb` primero (fallback) + resto de locales;
   0 claves ausentes verificado.
5. Test en `test/screens/` o `test/widgets/` (los widgets con `l10n`
   necesitan un `pump()` extra tras `pumpWidget`).

## Puertas (CI las exige)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
