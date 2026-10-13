# Sviluppo — convenzioni

[ES](DESARROLLO.md) · [EN](DESARROLLO.en.md) · [FR](DESARROLLO.fr.md) · [DE](DESARROLLO.de.md) · [IT](DESARROLLO.it.md) · [CA](DESARROLLO.ca.md) · [EU](DESARROLLO.eu.md) · [GL](DESARROLLO.gl.md) · [OC](DESARROLLO.oc.md)

## Backend: aggiungere un endpoint

1. Schema in `app/schemas/` (Pydantic v2; ruoli chiusi con `Literal`).
2. Logica in `app/services/` ereditando `BaseService` (`paginate` /
   `paginate_filtered`; senza `HTTPException` nel codice nuovo).
3. Rotta in `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` e
   `require_*` di `permissions.py`. Auth opzionale solo per lettura pubblica.
4. Migrazione se cambia lo schema: `alembic revision --autogenerate -m "..."`.
5. Test in `tests/test_<dominio>.py` (200 + 401 senza token + 403 senza permesso +
   404 inesistente). Rigenerare [API.md](API.md) con `tools/gen_api.py`.

## Frontend: aggiungere una schermata

1. Servizio: metodo nel file di `lib/services/api/` del suo dominio.
2. Schermata in `lib/screens/` <600 righe: estrarre in `lib/widgets/` la UI
   riutilizzabile (fumetti, schede, barre, sezioni).
3. Avvisi con `showAppSnack`; cancellazioni con `showConfirmDialog`; errori con
   `ErrorStateWidget` e nuovo tentativo.
4. Testi in `assets/l10n/en.arb` prima (fallback) + resto dei locale;
   0 chiavi mancanti verificato.
5. Test in `test/screens/` o `test/widgets/` (i widget con `l10n`
   necessitano di un `pump()` extra dopo `pumpWidget`).

## Cancelli (il CI li esige)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
