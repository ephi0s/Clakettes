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
4. Texte in `assets/l10n/en.arb` zuerst (Fallback) + restliche Locales; 0 fehlende Schlüssel verifiziert.
5. Test in `test/screens/` oder `test/widgets/` (Widgets mit `l10n` benötigen ein zusätzliches `pump()` nach `pumpWidget`).

## Tore (CI erfordert sie)

| Befehl | Wo |
|--------|----|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 Probleme) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` vor Test | `frontend/` |