# Protocol de federació Clakettes (Fase 4)

Passos per crear un servidor/client interoperable:

1. Implementar els endpoints `/api/federation/*`.
2. Exposar el manifest a `/api/federation/manifest` amb `schema_version`, `node`, `capabilities`.
3. Registrar el node al directori `/api/federation/directory`.
4. Validar els tokens dels peers via JWKS (`/api/federation/.well-known/webfinger`).
5. Usar l'esquema Clakettes v1 per a l'intercanvi de dades.

## Motivació

El protocol permet que nodes independents intercanviïn festivals, usuaris i missatges sense perdre identitat ni traçabilitat.

## Ajustos

- `consent_required`: exigeix consentiment explícit abans de federar dades d'un node.
- `import_only`: federació unidireccional (només import, no export).
- `disable_chat`/`disable_search`: permisos per funció per node.
- `minimize_data`: no compartir més del necessari en el peering.