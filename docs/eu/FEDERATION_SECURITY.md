# Federazio-segurtasuna (2tik 10erako faseak)

## Konfiantza-eredua

- Nodo-identitatea = domeinua + X.509 TLS ziurtagiria.
- Elkarrekiko peering-a mTLS bidez domeinu-ziurtagiriekin (CA publikoa edo pribatua): subjektuaren CNa eta ziurtagiriaren PEMa balioztatzen dira, deklaratutako domeinua soilik ez.
- TLS nahitaezkoa nodoen artean; ziurtagirien balioztatze zorrotza peering-ean (ekoizpenean self-signed-ik gabe).
- Identitatea `trusted_nodes` fitxategian gordetzen da (domeinua, PEMaren SHA-256 hatz-marka, subjektuaren CNa, jaulkitzaile CAa, baliozkotasuna, politikak).
- Nodo bakoitzak RSA-SHA256 bidez sinatutako manifestua arrazten du bere TLS ziurtagiriaren gako pribatuarekin; pareek `certificate_chain`-eko PEMaren kontra balioztatzen dute sinadura eta `expires_at` (24 h) egiaztatzen dute.

## Birzirkulazioa eta errebokazioa

- Birzirkulazioa ziurtagiria berrituz kudeatzen da: berritzean `trusted_nodes`-eko hatz-marka eguneratzen da peering-a hautsi gabe (konfiantzaren erroa CAa da, ez ziurtagiri indibiduala).
- Arriskuan dagoen nodo bat `trusted_nodes`-en `allowed = false` markatuz errebokatzen da (`POST /api/federation/peers/{domain}/revoke`, soilik admin) edo haren ziurtagiria CAaren CRL-ean baliogabetuz.
- Errebokazio administratiboa berehalakoa da: hurrengo mTLS eskua kaltetzen da.
- Larrialdiko errebokazioa `POST /api/federation/resilience/keys/revoke` bidez ere kudeatzen da (soilik admin, arrazoiarekin) eta `GET /keys/revoked` bidez kontsultatzen da; `GET /incident-plan`-ek arriskuaren aurrean erantzuteko 8 urratsak deskribatzen ditu.

## Sarbide-kontrolak

- Rate limiting globala: 100 req/60s IP bakoitzeko (`middleware:` depositua); `/dav`-ek 600/60s ditu.
- Endpoint sentikor bakoitzeko rate limiting-a: login 5/300s IP bakoitzeko, refresh 20/60s IP bakoitzeko, federazioa 60/60s IP bakoitzeko; txata 10 mezu/60 s nodo eta erabiltzaile bakoitzeko (`TESTING=true` bidez desaktibatuta).
- Erabiltzaile-datuak erakusten dituzten federazio-endpoint-ek (`/users/{ref}`, `/.well-known/webfinger`) egiaztatutako pare mTLS eskatzen dute.
- `GET /api/federation/whoami`-k federazioko Bearer JWTa (RS256) eskatzen du, jaulkitzailearen JWKSen kontra balioztatuta; token balidorik gabe 401 erantzuten du.
- Nodoen administrazio-endpoint-ek (`/nodes`, `/peers/{domain}/revoke`, portabilitate-migrazioak, `events/publish`, `events/retry-queue`, `keys/revoke`) admin rola eskatzen dute; kanalaren moderazioak admin edo kanalaren moderator izatea eskatzen du.
- Gertaeren SSE stream-ak sarbide-token baliozkoa eskatzen du `?token=` parametroan; gertaera `since` bidez kontsultatzen da eta replay-a azken 200 gertaeretara mugatzen da.

## Osotasuna, txata eta gertaerak

- Portabilitate-bundle-ek `signature` HMAC-SHA256 dute `SECRET_KEY` erabiliz eta `checksum` SHA-256 payload kanonikoaren gainean; inportazioak bundle baliogabeak (400) eta baimendu gabeko jatorriak (403) baztertzen ditu, eta `minimize_data` aplikatzen du eremu sentikorrak aldeztzeko.
- Txat-bridge-ak RS256 bidez sinatzen ditu gutun-azalaren eremu kanonikoak (`message_id`, `node_origin`, `content`, `timestamp`, …); hartzaileak parearen gako publikoa deskargatu eta sinadura egiaztatzen du gorde aurretik. `chat_outbox` taulak `message_id` bidezko bakartasuna ezartzen du, beraz birbidaltze bat `duplicate` gisa erantzuten da; historia `timestamp` + `message_id` bidez ordenatzen da.
- Garraioa ilara iraunkorraren bidez trukagarria da (`DurableQueueBackend` `chat_outbox`-en gainean), birsaio eta atzerapenarekin; broker-erabakia (NATS JetStream, ertzeko WebSocket eta nodo bakarreko fallback-a) `docs/es/FEDERATION_CHAT_BROKER.md` fitxategian dago.
- Moderazioak txostenak, mezuak ezkutatu/ezabatu, iraupen eta kanal edo nodo bidezko irismena duten isiltzeak, blokeatutako hitzen iragazkia eta nodo bidezko `disable_chat` estaltzen ditu (`POST /api/chat/moderation/*`). Nodo eta erabiltzaile bakoitzeko 10 mezu/60 s muga gehitzen zaio.
- Pareei bidalitako gertaerak HMAC-SHA256 bidez sinatzen dira `X-Clakettes-Signature` goiburuan eta baimendutako nodoei soilik hedatzen zaizkie; hutsegiteak birsaio-ilaran sartzen dira (3 saiakera, 300 ms → 1,5 s → 5 s atzerapena) `/api/federation/events/retry-queue` bidez ikusgai.
- `disable_chat` eta `disable_search` politikak sarrerako gertaerak edo mezuak aplikatu aurretik ebaluatzen dira, eta `import_only`-k esportazioa murrizten du; `GET /api/federation/resilience/metrics`-ek p50/p95, latentzia, hutsegiteak eta birsaioak erakusten ditu peering-a zaintzeko.

## Doikuntzak

- `allowlist`/`blocklist` nodo bakoitzeko (`node_policies` / `trusted_nodes`).
- Rate limiting-a eta anti-flood-a federazioaren ertzean.
- Moderazio-txostenak nodoen artean hedatzea.
- `consent_required`: nodo baten datuak federatu aurretik berariazko baimena eskatzen du.
- `import_only`: federazio norabide bakarrekoa (soilik inportatu, esportatu gabe).
- `disable_chat`/`disable_search`: nodo bakoitzeko funtzioen araberako baimenak.
- `minimize_data`: peering-ean beharrezkoa baino gehiago ez partekatu.

## Erreferentziak

- `docs/es/MODELO_CONFIANZA_NODOS.md` — konfiantza-ereduaren eta datu-base-taulen diseinu zehatza.
- `docs/es/FEDERATION_PROTOCOL.md` — nodo-zerbitzari/bezeroaren elkarrekikotasun-urratsak (2tik 10erako faseak).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, federazio-entitateak eta endpoint-ak.
- `docs/es/FEDERATION_CHAT_BROKER.md` — nodoen arteko txat eta gertaeretarako broker-erabakia.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — nodo bakoitzeko mehatxuak eta arrisku hondarrak.
