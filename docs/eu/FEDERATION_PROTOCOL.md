# Clakettes federazio protokoloa (4. fasea)

Zerbitzari/bezero interoperagarria sortzeko pausoak:

1. `/api/federation/*` endpointak inplementatu.
2. Manifestua `/api/federation/manifest`-en erakutsi `schema_version`, `node`, `capabilities`-ekin.
3. Nodoa `/api/federation/directory`-n erregistratu.
4. Peer tokenak JWKS bidez balioztatu (`/api/federation/.well-known/webfinger`).
5. Clakettes Schema v1 erabili datu-trukerako.

## Motibazioa

Protokoloak nodo independenteek jaialdiak, erabiltzaileak eta mezuak trukatzea ahalbidetzen du identitatea edo trazabilitatea galdu gabe.

## Doikuntzak

- `consent_required`: nodo baten datuak federatu aurretik berariazko baimena eskatzen du.
- `import_only`: federazio unidirekzionala (inportazioa soilik, esportaziorik ez).
- `disable_chat`/`disable_search`: funtzio baimenak nodoaren arabera.
- `minimize_data`: peeringean behar baino gehiago ez partekatu.