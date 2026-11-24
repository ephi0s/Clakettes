---
name: docs-i18n-sync
description: Sincroniza la documentación de Clakettes en todos los idiomas. El español es canónico y cada cambio se replica a los documentos hermanos y los README, sin introducir recuentos volátiles. Use when editing docs or READMEs in any locale.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 24 Nov 2026 00:00:00 GMT
---
# Skill: docs-i18n-sync

Sincronización y validación de documentación en todos los idiomas de Clakettes. Asegura que cualquier cambio en el documento canónico (español) se replica a todos los documentos hermanos usando referencias estables (rutas de directorio, símbolos y comandos) en lugar de inventarios volátiles.

## Uso

Invocar este skill antes de cerrar cualquier cambio que afecte a `docs/` o a los README raíz/idioma.

## Reglas de sincronización

1. **Canónico = español**. Toda edición parte de `docs/es/X.md`; todos los documentos hermanos (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`) deben reflejar el cambio.
2. **Un esquema común**. Todos los documentos usan la misma estructura: bloque de idiomas, navegación por audiencia, índice por tabla, ruta por perfil, convenciones, FAQ, ver también.
3. **Sin duplicación innecesaria**. Los documentos secundarios enlazan al canónico en lugar de repetirlo.

## Checklist de verificación (ejecutar antes de cerrar)

- [ ] El documento editado en `docs/es/` tiene su equivalente en todos los idiomas hermanos con el mismo nombre de archivo.
- [ ] Los enlaces intra-documento apuntan a los archivos correctos dentro de cada carpeta de idioma (no a `es/` salvo cuando se cite el canónico explícitamente).
- [ ] El bloque de idiomas al inicio de cada archivo lista todas las lenguas con el idioma actual marcado como enlace activo (sin `../` hacia sí mismo).
- [ ] Si cambió un flujo de arranque, se sincronizó `README.<lang>.md`, `USO.md` y `HERRAMIENTAS.md` en todos los idiomas.
- [ ] Si cambió una API pública, se actualizó `API.md` y, si procede, `DESARROLLO.md` en todos los idiomas.
- [ ] Si cambió el esquema o la persistencia, se revisó `DATABASE.md` y las migraciones en todos los idiomas.
- [ ] `AGENTS.md` usa referencias estables (rutas, símbolos y comandos) en lugar de recuentos de archivos o tests.
- [ ] Los flujos CI (`backend-lint`, `frontend-lint`, `backend-test`, `frontend-test`, `docker-build`) no se ven afectados por el cambio de docs; si se tocaron comandos, flags o versiones, se revisó `.github/workflows/ci.yml` y `.gitlab-ci.yml`.
- [ ] Si se cambió un comando de arranque, build o test, se actualizó la referencia en los CI de GitHub y GitLab para evitar roturas y correos de fallo.

## Comandos de verificación sugeridos

```bash
# Desde la raíz del proyecto
cd backend && python -m ruff check . && python -m pytest tests/ -x -q --tb=short
cd frontend && flutter analyze && flutter test
# Revisar CI antes de publicar
cat .github/workflows/ci.yml | grep -E "name:|ruff|flutter|pytest|docker-build"
cat .gitlab-ci.yml | grep -E "stage:|script:|ruff|flutter|pytest|docker-build"
```

## Excepciones

- `AUDITORIA.md` es un informe histórico (rev. 10/10/2026); sus cifras son fijas y no se actualizan salvo nueva revisión de auditoría.
- `API.md` es regenerable con `python tools/gen_api.py --all`; no editar a mano salvo que el script falle. El CI verifica que esté al día con `python tools/gen_api.py --all --check`. El generador combina el prefijo de `main.py` con el de cada `APIRouter` y detecta dependencias de auth; las notas comunes (p. ej. `resolveMediaUrl()`) viven en la constante `media` de `tools/gen_api.py` para sobrevivir a la regeneración.
