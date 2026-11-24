---
description: Comprueba y aplica cambios remotos antes de trabajar
---

Sincroniza el repositorio siguiendo `AGENTS.md`: ejecuta `git fetch origin`, `git status -sb` y `git log --oneline '@{u}..HEAD'` (comillas necesarias en PowerShell).
Si faltan commits de `origin/main`, ejecuta `git pull --ff-only` y verifica que no haya conflictos con los cambios locales.
Resume en una línea el estado resultante.
