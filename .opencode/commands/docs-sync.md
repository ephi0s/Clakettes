---
description: Replica cambios de documentación a todos los idiomas
---

Carga el skill `docs-i18n-sync` y aplícalo a $ARGUMENTS.
Parte siempre del documento canónico en `docs/es/`, replica el cambio a todas las hermanas (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`) y comprueba los enlaces del bloque de idiomas.
No introduzcas recuentos de archivos ni de tests: usa rutas, símbolos y comandos estables.
