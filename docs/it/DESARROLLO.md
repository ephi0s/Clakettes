# Sviluppo — convenzioni

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](../oc/DESARROLLO.md)

## Backend: aggiungere un endpoint

1. Schema in `app/schemas/` (Pydantic v2; ruoli chiusi con `Literal`).
2. Logica in `app/services/` ereditando `BaseService` (`paginate` /
   `paginate_filtered`; senza `HTTPException` nel codice nuovo).
3. Rotta in `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` e
   `require_*` di `permissions.py`. Auth opzionale solo per lettura pubblica.
4. Migrazione se cambia lo schema: `alembic revision --autogenerate -m "..."`.
5. Test in `tests/test_<dominio>.py` (200 + 401 senza token + 403 senza permesso +
   404 inesistente).

## Frontend: aggiungere una schermata

1. Servizio: metodo nel file di `lib/services/api/` del suo dominio.
2. Schermata in `lib/screens/` <600 righe: estrarre in `lib/widgets/` la UI
   riutilizzabile (fumetti, schede, barre, sezioni).
3. Avvisi con `showAppSnack`; cancellazioni con `showConfirmDialog`; errori con
   `ErrorStateWidget` e nuovo tentativo.
4. Testi in `assets/l10n/app_en.arb` prima (fallback) + resto dei locale (823 chiavi); esegui `flutter test test/l10n/arb_parity_test.dart`: richiede le stesse chiavi e placeholder nei 9 ARB (referenza `es`).
5. Test in `test/screens/` o `test/widgets/` (i widget con `l10n`
   necessitano di un `pump()` extra dopo `pumpWidget`).

## Dipendenze (Dependabot)

- pip in `/backend` e pub in `/frontend`, settimanali (lunedì), raggruppati in `backend-deps`/`frontend-deps`; si ignorano gli aggiornamenti `version-update:semver-major`.
- Patch/minor: `.github/workflows/dependabot-automerge.yml` attiva `gh pr merge --auto --squash` solo per `dependabot[bot]`; il merge effettivo richiede CI verde. Major: revisione manuale.
- `.github/workflows/dependabot-rebase.yml` riaggiorna i PR aperti il lunedì 04:17 UTC e su `workflow_dispatch`. Dettaglio in [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md).

## Gate di qualità

- Backend: `ruff check .` → `ruff format --check .` → `pytest tests/ -m "not interop" -x -q --tb=short`.
- Frontend: `dart run build_runner build --delete-conflicting-outputs` → `flutter analyze` → `flutter test`.
- Dopo aver cambiato endpoint o rotte, rigenera il riferimento con `python tools/gen_api.py --all` (combina i prefissi di `main.py` e di ogni `APIRouter`).


