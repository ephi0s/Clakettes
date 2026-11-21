# Clakettes federazio-protokoloa (2tik 10erako faseak)

Elkarrekikotasunezko zerbitzari/bezero bat sortzeko urratsak:

1. Ezarri `/api/federation/*` endpoint-ak (ikusi `docs/es/FEDERATION_SCHEMA.md`).
2. Konfiguratu nahitaezko TLS nodoen artean elkarrekiko mTLS erabiliz (2. Fasea): konfiantzazko CA batek emandako ziurtagiria, ekoizpenean self-signed-ik gabe.
3. Erregistratu nodoa konfiantzazko gisa harekin peering-a egingo duen pare bakoitzean (`trusted_nodes`: domeinua, ziurtagiriaren PEM-aren SHA-256 hatz-marka, subjektuaren CNa, gaitasunak, politikak). `POST /api/federation/nodes` bidez `import_only`, `disable_chat` eta `disable_search` gordetzen dira `consent_required` eta `minimize_data`rekin batera.
4. Arraztu manifestua `GET /api/federation/manifest` bidez `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` eta `certificate_chain` eremuekin. Manifestua RSA-SHA256 (PKCS#1 v1.5) bidez sinatzen da nodoaren TLS ziurtagiriaren gako pribatuarekin; pareak `certificate_chain`-eko PEMarekin balioztatzen du sinadura eta `expires_at` (24 h) egiaztatzen du.
5. Arraztu gako publikoa `GET /api/federation/.well-known/jwks.json` bidez, pareek federazio-tokenak baliozta ditzaten.
6. Balioztatu pareen tokenak JWKS bidez: babestutako endpoint batera deitzen duen urruneko nodo batek sinatutako (RS256) Bearer JWT aurkeztu behar du, `iss` bere domeinua izanik eta sinadura bere JWKSen kontra baliozta dela. `GET /api/federation/whoami` bidez parearen identitatea itzultzen da JWT hori baliozkoa denean soilik (bestela 401).
7. Ebaztu urruneko erabiltzaileak `GET /api/federation/users/{ref}` eta `GET /api/federation/.well-known/webfinger` bidez (biek egiaztatutako pare mTLS eskatzen dute).
8. Erabili Clakettes Schema v1 datu-trukaketarako.
9. Transferitu identitatea eta datuak `POST /api/federation/portability/bundles` eta `/imports` bidez (HMAC-SHA256 sinadura eta checksum), migratu `/festivals/{id}/migrate` eta `/users/{ref}/migrate` bidez, eta ebaztu erreferentzia zaharrak `GET /redirects/{ref}` bidez.
10. Banatu txata sinatutako `/api/federation/chat/bridge/{inbound,outbound,config}` bridge-aren bidez; historia `/api/federation/chat/messages` bidez kontsultatzen da, `message_id` bidez deduplikatuta eta `timestamp` + `message_id` bidez ordenatuta. `chat_outbox` ilara iraunkorrak garraio trukagarria ahalbidetzen du (xehetasuna `docs/es/FEDERATION_CHAT_BROKER.md` fitxategian).
11. Hedatu aldaketak gertaera-busaren bidez: `GET /api/federation/events/stream` (SSE `since` eta bihotz-taupadarekin), `POST /publish` eta `GET /retry-queue` (3 saiakera, 300 ms → 5 s atzerapena).
12. Zaindu peering-aren osasuna `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}` bidez; `metrics`-ek p50/p95, latentzia, hutsegiteak eta birsaioak erakusten ditu.
13. Egiaztatu hirugarren nodo baten betetze-maila `python tools/federation_conformance.py <url> [--json]` bidez (1 hutsegite kritiko edo altuak badaude).

## Motibazioa

Protokoloari esker nodo independenteek jaialdiak, erabiltzaileak eta mezuak truka ditzakete identitatea edo trazabilitatea galdu gabe.

## Doikuntzak

- `consent_required`: nodo baten datuak federatu aurretik berariazko baimena eskatzen du.
- `import_only`: federazio norabide bakarrekoa (soilik inportatu, esportatu gabe).
- `disable_chat`/`disable_search`: nodo bakoitzeko funtzioen araberako baimenak.
- `minimize_data`: peering-ean beharrezkoa baino gehiago ez partekatu.

## Endpoint giltzarriak

| Endpoint | Metodoa | Deskribapena |
|---|---|---|
| `/api/federation/manifest` | GET | RSA-SHA256 sinatutako manifestua `expires_at` eta `certificate_chain` eremuekin |
| `/api/federation/directory` | GET | Konfiantzazko nodoen direktorioa |
| `/api/federation/nodes` | GET/POST | Allowlist/blocklist politikak (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Parearen identitatea, bere JWT bere JWKSen kontra balioztatuz |
| `/api/federation/.well-known/jwks.json` | GET | Nodoaren JWKS gako publikoa |
| `/api/federation/token` | POST | Federazio-JWTa igortzea (RS256) |
| `/api/federation/peers/verify` | POST | Urruneko nodoaren identitatea egiaztatzea (ziurtagiriaren CNa eta PEMa) |
| `/api/federation/peers/{domain}/revoke` | POST | Konfiantzazko nodoa errebokatzea (admin) |
| `/api/federation/users/{ref}` | GET | Urruneko erabiltzailea ebaztea (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Nodoen arteko moderazio-txostenak |
| `/api/federation/portability/bundles`, `/imports` | POST | Sinatutako bundle-ak esportatu eta inportatu |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Jaialdiak eta erabiltzailearen identitatea migratu (admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Erreferentzia zaharra ebaztea migrazioaren ondoren |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Sinatutako txat-bridge-a eta haren konfigurazioa |
| `/api/federation/chat/messages` | GET | Federazio-historia, deduplikatuta eta ordenatuta |
| `/api/chat/moderation/*` | POST/PATCH/GET | Txostenak, isiltzeak, iragazkia eta txat-muga |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE `since` eta bihotz-taupadarekin, argitaratzea eta birsaioak |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Osasuna, taupada eta benetako p50/p95 metrikak |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Gakoen errebokazioa eta intzidente-plana |
