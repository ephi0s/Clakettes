# Protocolo de federación Clakettes (Fase 4)

Pasos para crear un servidor/cliente interoperable:

1. Implementar os endpoints `/api/federation/*`.
2. Expor o manifest en `/api/federation/manifest` con `schema_version`, `node`, `capabilities`.
3. Rexistrar o nodo no directorio `/api/federation/directory`.
4. Validar os tokens dos peers via JWKS (`/api/federation/.well-known/webfinger`).
5. Usar o esquema Clakettes v1 para o intercambio de datos.

## Motivación

O protocolo permite que nodos independentes intercambien festivais, usuarios e mensaxes sen perder identidade nin trazabilidade.

## Adecuacións

- `consent_required`: esixe consentimento explícito antes de federar datos dun nodo.
- `import_only`: federación unidireccional (só import, non export).
- `disable_chat`/`disable_search`: permisos por función por nodo.
- `minimize_data`: non compartir máis do necesario no peering.