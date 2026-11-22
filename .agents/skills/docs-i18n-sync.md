# Skill: docs-i18n-sync

Sincronización y validación de documentación en los 9 idiomas de Clakettes. Asegura que cualquier cambio en el documento canónico (español) se replica a las 8 hermanas y que las cifras del repositorio (routers, servicios, modelos, migraciones, tests) coinciden entre código y docs.

## Uso

Invocar este skill antes de cerrar cualquier cambio que afecte a `docs/` o a los README raíz/idioma.

## Reglas de sincronización

1. **Canónico = español**. Toda edición parte de `docs/es/X.md`; las 8 hermanas (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`) deben reflejar el cambio.
2. **Un esquema común**. Todos los documentos usan la misma estructura: bloque de idiomas, navegación por audiencia, índice por tabla, ruta por perfil, convenciones, FAQ, ver también.
3. **Sin duplicación innecesaria**. Los documentos secundarios enlazan al canónico en lugar de repetirlo.

## Checklist de verificación (ejecutar antes de cerrar)

- [ ] El documento editado en `docs/es/` tiene su equivalente en los 8 idiomas hermanos con el mismo nombre de archivo.
- [ ] Los enlaces intra-documento apuntan a los archivos correctos dentro de cada carpeta de idioma (no a `es/` salvo cuando se cite el canónico explícitamente).
- [ ] El bloque de idiomas al inicio de cada archivo lista las 9 lenguas con el idioma actual marcado como enlace activo (sin `../` hacia sí mismo).
- [ ] Las cifras citadas coinciden con el estado real del repositorio:
  - Routers: 45 archivos (43 con `APIRouter`, 39 registrados con prefijo en `main.py`)
  - Servicios: 53
  - Modelos de entidad: 43 (+ `base.py`, `__init__.py`)
  - Schemas: 37
  - Migraciones Alembic: 45 (+ `__init__.py`), head `d1e2f3a4b5c6`
  - Tests backend: 54 archivos `test_*.py`, 1544 tests recogidos (1541 con `-m "not interop"`)
  - Widgets frontend: 33 en `lib/widgets/`
  - Pantallas frontend: 38 en `lib/screens/`
  - Tests frontend: 77 archivos `*_test.dart`
  - ARB: 823 claves por locale en 9 idiomas (paridad con `test/l10n/arb_parity_test.dart`)
- [ ] Si cambió un flujo de arranque, se sincronizó `README.<lang>.md`, `USO.md` y `HERRAMIENTAS.md` en todos los idiomas.
- [ ] Si cambió una API pública, se actualizó `API.md` y, si procede, `DESARROLLO.md` en todos los idiomas.
- [ ] Si cambió el esquema o la persistencia, se revisó `DATABASE.md` y las migraciones en todos los idiomas.
- [ ] `AGENTS.md` refleja las cifras actuales si se citan.
- [ ] Los flujos CI (`backend-lint`, `frontend-lint`, `backend-test`, `frontend-test`, `docker-build`) no se ven afectados por el cambio de docs; si se tocaron comandos, flags o versiones, se revisó `.github/workflows/ci.yml` y `.gitlab-ci.yml`.
- [ ] Si se cambió un comando de arranque, build o test, se actualizó la referencia en los CI de GitHub y GitLab para evitar roturas y correos de fallo.

## Comandos de verificación sugeridos

```bash
# Desde la raíz del proyecto
cd backend && python -m ruff check . && python -m pytest tests/ -x -q --tb=short
cd frontend && flutter analyze && flutter test
# Revisar conteos reales si se citan cifras en docs
ls backend/app/routers/*.py | wc -l
ls backend/app/services/*.py | wc -l
ls backend/app/models/*.py | wc -l
ls alembic/versions/*.py | wc -l
ls frontend/lib/widgets/*.dart | wc -l
ls frontend/lib/screens/*.dart | wc -l
ls frontend/test -r --include="*_test.dart" | wc -l
# Revisar CI antes de publicar
cat .github/workflows/ci.yml | grep -E "name:|ruff|flutter|pytest|docker-build"
cat .gitlab-ci.yml | grep -E "stage:|script:|ruff|flutter|pytest|docker-build"
```

## Excepciones

- `AUDITORIA.md` es un informe histórico (rev. 10/10/2026); sus cifras son fijas y no se actualizan salvo nueva revisión de auditoría.
- `API.md` es regenerable con `python tools/gen_api.py --all`; no editar a mano salvo que el script falle. El generador combina el prefijo de `main.py` con el de cada `APIRouter` y detecta dependencias de auth; las notas comunes (p. ej. `resolveMediaUrl()`) viven en la constante `media` de `tools/gen_api.py` para sobrevivir a la regeneración.