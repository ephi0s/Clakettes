# Garapena — konbentzioak

## Backend-a: endpoint bat gehitzea

1. Schema `app/schemas/`-n (Pydantic v2; rol itxiak `Literal`-ekin).
2. Logika `app/services/`-n `BaseService` heredatuz (`paginate` /
   `paginate_filtered`; `HTTPException` gabe kode berrian).
3. Ibilbidea `app/routers/`-n + `get_or_404(db, Modelo, id, "Etiketa")` eta
   `permissions.py`-ko `require_*`. Auth aukerakoa irakurketa publikorako soilik.
4. Migrazioa eskema aldatzen bada: `alembic revision --autogenerate -m "..."`.
5. Test-a `tests/test_<dominio>.py`-n (200 + 401 token gabe + 403 baimen gabe +
   404 existitzen ez dena). Birsortu [API.md](API.md) `tools/gen_api.py`-rekin.

## Frontend-a: pantaila bat gehitzea

1. Zerbitzua: metodoa bere domeinuko `lib/services/api/` fitxategian.
2. Pantaila `lib/screens/`-n <600 lerro: erauzi `lib/widgets/`-ra UI
   berrerabilgarria (burbuilak, txartelak, barrak, sekzioak).
3. Abisuak `showAppSnack`-ekin; ezabaketak `showConfirmDialog`-ekin; erroreak
   `ErrorStateWidget`-ekin eta saiakera-errepikapenarekin.
4. Testuak `assets/l10n/en.arb`-n lehenik (fallback) + gainerako locale-ak;
   0 giltza falta egiaztatuta.
5. Test-a `test/screens/` edo `test/widgets/`-n (`l10n`-dun widget-ek
   `pump()` gehigarri bat behar dute `pumpWidget` ondoren).

## Ateak (CI-k exijitzen ditu)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
