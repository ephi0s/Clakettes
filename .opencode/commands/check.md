---
description: Ejecuta la puerta de calidad del proyecto (ruff + analyze, u completa)
---

Ejecuta la puerta de calidad con `tools/check.ps1` (o `tools/check.sh` en shell POSIX).
Por defecto usa el modo rápido (`-Quick` / `--quick`: ruff check, ruff format --check y flutter analyze).
Si $ARGUMENTS pide "completa" o "full", ejecuta sin modo rápido para incluir pytest con `-m "not interop"` y `flutter test`.
Si $ARGUMENTS contiene un filtro, pásalo como `-TestFilter` / `--test-filter=`.
Corrige cualquier fallo dentro de los archivos permitidos y vuelve a ejecutar la puerta.
