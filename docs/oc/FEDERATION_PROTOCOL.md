# Protocòl de federacion Clakettes (Fase 4)

Passes per crear un servidor/client interoperable:

1. Implementar los endpoints `/api/federation/*`.
2. Expausir lo manifest a `/api/federation/manifest` amb `schema_version`, `node`, `capabilities`.
3. Registrar lo node dins lo repertòri `/api/federation/directory`.
4. Validar los tokens dels peers via JWKS (`/api/federation/.well-known/webfinger`).
5. Utilizar l'esquèma Clakettes v1 per l'escambi de donadas.

## Motivacion

Lo protocòl permet a de nodes independents d'escambiar festivals, utilizaires e messatges sens pèrdre l'identitat ni la traçabilitat.

## Ajustaments

- `consent_required`: exigís un consentiment explicit abans de federar las donadas d'un node.
- `import_only`: federacion unidireccionala (import solament, pas d'export).
- `disable_chat`/`disable_search`: permissions per foncion per node.
- `minimize_data`: partejar pas mai que çò necessari dins lo peering.