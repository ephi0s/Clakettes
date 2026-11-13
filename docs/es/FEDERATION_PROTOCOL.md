# Protocolo de federación Clakettes (Fase 4)

Pasos para crear un servidor/cliente interoperable:

1. Implementar los endpoints `/api/federation/*`.
2. Exponer el manifest en `/api/federation/manifest` con `schema_version`, `node`, `capabilities`.
3. Registrar el nodo en el directorio `/api/federation/directory`.
4. Validar tokens de pares vía JWKS (`/api/federation/.well-known/webfinger`).
5. Usar Clakettes Schema v1 para el intercambio de datos.

## Motivación

El protocolo permite que nodos independientes intercambien festivales, usuarios y mensajes sin perder identidad ni trazabilidad.

## Ajustes

- `consent_required`: exige consentimiento explícito antes de federar datos de un nodo.
- `import_only`: federación unidireccional (solo importar, no exportar).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: no compartir más de lo necesario en peering.