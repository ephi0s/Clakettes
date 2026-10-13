# Entwicklung — Konventionen

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: einen Endpunkt hinzufügen

1. Schema in `app/schemas/` (Pydantic v2; geschlossene Rollen mit `Literal`).
2. Logik in `app/services/` erbend von `BaseService` (`paginate` /
   `paginate_filtered`; ohne `HTTPException` in neuem Code).
3. Route in `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` und
   `require_*` aus `permissions.py`. Optionale Auth nur für öffentliches Lesen.
4. Migration bei Schemaänderung: `alembic revision --autogenerate -m "..."`.
5. Test in `tests/test_<dominio>.py` (200 + 401 ohne Token + 403 ohne Berechtigung +
   404 nicht existent). [API.md](../es/API.md) mit `tools/gen_api.py` regenerieren.

## Frontend: einen Screen hinzufügen

1. Service: Methode in der Datei von `lib/services/api/` seiner Domäne.
2. Screen in `lib/screens/` <600 Zeilen: wiederverwendbare UI nach `lib/widgets/`
   extrahieren (Bubbles, Karten, Leisten, Sektionen).
3. Hinweise mit `showAppSnack`; Löschen mit `showConfirmDialog`; Fehler mit
   `ErrorStateWidget` und Retry.
4. Texte zuerst in `assets/l10n/en.arb` (Fallback) + restliche Locales;
   0 fehlende Keys verifiziert.
5. Test in `test/screens/` oder `test/widgets/` (Widgets mit `l10n`
   brauchen ein extra `pump()` nach `pumpWidget`).

## Gates (CI verlangt sie)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
