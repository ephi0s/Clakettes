# Clakettes Schema v1

[ES](../es/FEDERATION_SCHEMA.md) · [EN](../en/FEDERATION_SCHEMA.md) · [FR](../fr/FEDERATION_SCHEMA.md) · [DE](../de/FEDERATION_SCHEMA.md) · [IT](../it/FEDERATION_SCHEMA.md) · [CA](../ca/FEDERATION_SCHEMA.md) · [EU](FEDERATION_SCHEMA.md) · [GL](../gl/FEDERATION_SCHEMA.md) · [OC](../oc/FEDERATION_SCHEMA.md)

Federazio-eskemaren hasierako bertsioa. Nodoen artean trukagarriak diren gutxieneko entitateak definitzen ditu, nodo bakoitzaren manifestuan `schema_version` bidez bertsionatuta.

## Konfiantza-eredua (2. Fasea)

Nodo baten identitatea **(domeinua, X.509 TLS ziurtagiria)** tupla da. Nodoen arteko peering-a elkarrekiko mTLS bidez egiten da: nodo bakoitzak parearen ziurtagiri-katea bere CA erroaren kontra balioztatzen du, ziurtagiriaren domeinua deklaratutakoarekin bat datorla egiaztatzen du, eta ekoizpenean self-signed ziurtagiriak baztertzen ditu. Birzirkulazioa eta errebokazioa ziurtagiria berrituz kudeatzen dira.

## Entitateak

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect`: old_ref, new_ref, target_domain, created_at
- `migration_audit`: entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox`: message_id (bakarrak), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report`: reporter_id, message_id, reason, status
- `chat_mute`: user_id, channel_id, node_domain, until, reason

## Eremuak eta murrizketak

- `uuid`: identifikatzaile egonkor globala (UUID v4).
- `did`: identifikatzaile deszentralizatua, aukerakoa.
- `handle`: `erabiltzailea@instantzia`, WebFinger bidez ebazgarria.
- `schema_version`: nodoak manifestuan deklaratutako eskema-bertsioa (une honetan: `1`).

## Federazio-endpoint-ak

### Identitatea eta direktorioa

- `GET /api/federation/manifest` — nodoaren manifestua `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` eta `certificate_chain` eremuekin. RSA-SHA256 sinadura nodoaren TLS ziurtagiriaren gako pribatuarekin; pareak katearen PEMa eta `expires_at` (24 h) baliozkotasuna egiaztatzen ditu.
- `GET /api/federation/directory` — konfiantzazko nodoen zerrenda (`trusted_nodes`), `allowed = true` dutenak, `cert_fingerprint_sha256` (PEMaren hatz-marka), `capabilities`, `consent_required`, `minimize_data` barne.
- `GET/POST /api/federation/nodes` — nodo-politikak (allowlist/blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Soilik admin; azken hirurak gorde eta bridge-ean eta gertaera-busean aplikatzen dira.

### Identitate federatua eta tokenak (3. Fasea)

- `GET /api/federation/.well-known/jwks.json` — nodoaren RSA gako publikoa JWKS formatuan, pareen federazio-tokenak balioztatzeko.
- `POST /api/federation/token` — sinatutako federazio-JWTa igortzen du (RS256). mTLS bidez egiaztatutako nodo-identitatea eskatzen du.
- `POST /api/federation/peers/verify` — urruneko nodo baten identitatea balioztatzen du (domeinua + ziurtagiriaren CNa eta PEMa + sinatutako manifestua).
- `POST /api/federation/peers/{domain}/revoke` — konfiantzazko nodoa errebokatzen du (admin).
- `GET /api/federation/whoami` — parearen identitatea (`iss`, `sub`, nodoa) bere Bearer JWTa bere JWKSen kontra baliozkoa bada soilik; bestela 401.

### Erabiltzaileak, txostenak eta aurkikuntza

- `GET /api/federation/users/{ref}` — erabiltzailea `uuid`, `did` edo `handle` bidez ebazten du. Egiaztatutako pare mTLS eskatzen du.
- `GET /api/federation/.well-known/webfinger` — `acct:user@domain` ebazten du. Egiaztatutako pare mTLS eskatzen du.
- `POST/GET/PATCH /api/federation/reports` — nodoen arteko moderazio-txostena.

### Portabilitatea (7. Fasea)

- `POST /api/federation/portability/bundles` — erabiltzailearen bundle-a sortzen du `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 `SECRET_KEY` erabiliz) eta `checksum` (payload kanonikoaren SHA-256) eremuekin.
- `POST /api/federation/portability/imports` — sinadura eta checksum balioztatzen ditu, jatorri-politika egiaztatzen du (baimenduta ez badago 403), `minimize_data` aplikatzen du eta inportatutakoa erregistratzen du (erabiltzailea, film laburrak, jaialdiak, mezuak). Bundle-ek `contest_type` dute labur bakoitzean: `MediaUrl` balioztatu/saneatzen da (URL baliogabea → `null`), `contest_type` `official_section`-era normalizatzen da baliozkoa ez bada eta jaialdiaren checksum-ak barne hartzen du.
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — jaialdiaren eta haren film laburren jabetza `target_domain`-eko `new_owner_id`-ri transferitzen dio checksum egiaztatuta; soilik admin.
- `POST /api/federation/portability/users/{user_ref}/migrate` — `handle` eta `did` helmugako domeinura berridatzi eta birbideratzea sortzen du; soilik admin.
- `GET /api/federation/portability/redirects/{old_ref}` — erreferentzia zaharra ebazten du (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Txat federatua, moderazioa eta gertaerak (8. eta 9. Faseak)

- `POST /api/federation/chat/bridge/inbound` — sinatutako gutun-azala onartzen du (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), parearen gako publikoaren kontra RS256 sinadura egiaztatzen du, `message_id` bidez bikoiztuak baztertzen ditu, mezua gorde eta hedatzen du; `403` nodoa baimenduta ez badago edo sinadura baliozkoa ez bada.
- `POST /api/federation/chat/bridge/outbound` — gutun-azala sinatu, `chat_outbox`-en ilaratu `clakettes.chat.node.{target_node}` gaiarekin eta konfiguratutako garraioaren bidez argitaratu (`DurableQueueBackend`); `config`-ek garraioa, stream-a, algoritmoa eta gaien mapaketa itzultzen ditu.
- `GET /api/federation/chat/messages` — federatutako historia, `message_id` bidez deduplikatuta eta `timestamp` + `message_id` bidez ordenatuta (aukerako `node` iragazkia).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — txostenak, ezkutatu/ezabatu, erabiltzaile/kanal/nodo bidezko isiltzeak, blokeatutako hitzen iragazkia, nodo bidezko `disable_chat` eta 10 mezu/60 s nodo eta erabiltzaile bakoitzeko (`TESTING=true` bidez desaktibatuta).
- `GET /api/federation/events/stream` — SSE query-n `token` nahitaezkoarekin (`since` eta `limit` aukerakoak), azken 200 gertaeren replay-a eta `: ping` bihotz-taupada 15 s an.
- `POST /api/federation/events/publish` — `node`/`entity`-tik eratorritako gai batean argitaratzen du (edo `topic` esplizitua), pareei bidalitakoa HMAC bidez sinatzen du (`X-Clakettes-Signature`) eta `disable_chat`/`disable_search` duten nodoak saltzen ditu; soilik admin.
- `GET /api/federation/events/retry-queue` — birsaio zain daudenak; 3 saiakera 300 ms → 1,5 s → 5 s atzerapenarekin.

### Erresilientzia (10. Fasea)

- `GET /api/federation/resilience/health` — nodoaren egoera, datu-basea, nodo-kopurua eta latentzia.
- `GET /api/federation/resilience/heartbeat` — parearen `last_seen_at` eguneratzen du eta latentzia metriketan erregistratzen du.
- `GET /api/federation/resilience/metrics` — eskaerak, arrakastak, hutsegiteak, birsaioak eta p50/p95 latentziak orokorrean eta nodo bakoitzeko.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — gakoen berehalako errebokazioa domeinu bidez arrazoiarekin, eta errebokazioen zerrenda; soilik admin errebokatzeko.
- `GET /api/federation/resilience/incident-plan` — nodoa arriskuan jartzearen aurrean berreskuratzeko plana (8 urrats).

### Osasuna eta utilitateak

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — egoera erreala islatzen ez duten erantzun estatikoak dituzten leku-markatzaileak (placeholders); ez dira zundaketa edo diagnostiko endpoint operatiboak.

> **Oharra:** erantzun finkoak itzultzen dituzte eta segurtasun-sentsazio faltsua eman dezakete; benetako diagnostikorako, erabili goian deskribatutako erresilientzia-endpoint-ak.

## Egokitzapena

- Eskema bertsionatuta dago; nodoek `schema_version` deklaratzen dute manifestuan.
- Aukerako eremuak (`did`, `handle`) aldeztu daitezke nodoak onartzen ez baditu.
- Datu-minimizazioak (`minimize_data`) eremu sentikorrak aldeztzea ahalbidetzen du peering-ean.
