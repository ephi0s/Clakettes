# Desvolopament — convencions

[ES](../es/DESARROLLO.md) · [EN](../en/DESARROLLO.md) · [FR](../fr/DESARROLLO.md) · [DE](../de/DESARROLLO.md) · [IT](../it/DESARROLLO.md) · [CA](../ca/DESARROLLO.md) · [EU](../eu/DESARROLLO.md) · [GL](../gl/DESARROLLO.md) · [OC](DESARROLLO.md)

## Backend: apondre un endpoint

1. Schema en `app/schemas/` (Pydantic v2; ròtles tampats amb `Literal`).
2. Logica en `app/services/` eiretant `BaseService` (`paginate` /
   `paginate_filtered`; sens `HTTPException` en còde nòu).
3. Rota en `app/routers/` + `get_or_404(db, Modelo, id, "Etiqueta")` e
   `require_*` de `permissions.py`. Auth opcionau sonque per lectura publica.
4. Migracion se cambia l'esquèma: `alembic revision --autogenerate -m "..."`.
5. Tèst en `tests/test_<dominio>.py` (200 + 401 sens token + 403 sens permission +
   404 inexistent). Regenerar [API.oc.md](API.md) amb `tools/gen_api.py`.

## Frontend: apondre un ecran

1. Servici: metòde dins lo fichièr de `lib/services/api/` de son domeni.
2. Ecran en `lib/screens/` <600 linhas: extraire cap a `lib/widgets/` l'UI
   reutilizabla (borbolhas, cartas, barras, seccions).
3. Avises amb `showAppSnack`; escafaments amb `showConfirmDialog`; errors amb
   `ErrorStateWidget` e tornada d'ensajar.
4. Tèxtes en `assets/l10n/en.arb` d'en primièr (fallback) + rèsta de locales;
   0 claus absentas verificat.
5. Tèst en `test/screens/` o `test/widgets/` (los widgets amb `l10n`
   an besonh d'un `pump()` extra aprèp `pumpWidget`).

## Pòrtas (CI las exigís)

| Comando | Dónde |
|---|---|
| `ruff check .` + `ruff format --check .` | `backend/` |
| `pytest tests/ -x -q --tb=short` | `backend/` |
| `flutter analyze` (0 issues) | `frontend/` |
| `flutter test` | `frontend/` |
| `dart run build_runner build --delete-conflicting-outputs` antes de test | `frontend/` |
