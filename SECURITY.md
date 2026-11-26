# Política de seguridad

Clakettes toma en serio los informes de vulnerabilidades.

## Cómo reportar

Usa el canal privado de GitHub del repositorio (**Security → Report a vulnerability**).
No abras un issue público ni incluyas datos reales de producción. Incluye:

- Componente afectado (backend, frontend, Docker/CI) y versión o commit.
- Pasos para reproducirlo y impacto esperado.
- Prueba de concepto mínima, si la tienes.

## Qué esperar

- Confirmación de recepción en un plazo razonable.
- Triage y, si procede, corrección antes de publicar el detalle.
- Crédito en el aviso si el reportero lo desea.

## Versiones soportadas

Se soporta la rama `main` y la última versión publicada. Las correcciones de seguridad
se priorizan en `main` y se publican en el siguiente lanzamiento.

## Configuración segura

Consulta [docs/es/SEGURIDAD.md](docs/es/SEGURIDAD.md) para los requisitos de
producción (`APP_ENV`, `SECRET_KEY`, `CORS_ORIGINS`, TLS de base de datos), la
auditoría de dependencias con `tools/audit_deps.py` y las defensas del frontend.
