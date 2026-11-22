# Chat eta gertaeretarako brokeraren ebaluazioa: MQTT 5 vs NATS JetStream

[ES](../es/FEDERATION_CHAT_BROKER.md) · [EN](../en/FEDERATION_CHAT_BROKER.md) · [FR](../fr/FEDERATION_CHAT_BROKER.md) · [DE](../de/FEDERATION_CHAT_BROKER.md) · [IT](../it/FEDERATION_CHAT_BROKER.md) · [CA](../ca/FEDERATION_CHAT_BROKER.md) · [EU](FEDERATION_CHAT_BROKER.md) · [GL](../gl/FEDERATION_CHAT_BROKER.md) · [OC](../oc/FEDERATION_CHAT_BROKER.md)

Dokumentu honek Clakettesen nodoen arteko chat eta gertaeren hedapenerako zein garraio erabili behar den egiteko dagoen ebaluazioa ixten du. Erabakia Fase 8rako (chat federatu-ilara gisa) loteslea da, eta `docs/es/ARQUITECTURA.md`en deskribatutako WebSocket backendarekin batera bizi da.

**Inplementazio-egoera (6-10 faseak):** erabakiak NATS JetStream hartzen du helmuga gisa, baina gaur egun ekoizpeneko garraio iraunkorra `DurableQueueBackend` da `chat_outbox` taulan WebSocket ordezkariarekin. Migrazio-planerako `NATS_*` aldagaiak eta `CHAT_BACKEND` flag-a **oraindik ez dira existitzen** `.env.example`-n ezta `app/config.py`-n ere: `/api/federation/chat/bridge/config`-ek aurreikusitako helmugaren berri soilik ematen du (`"transport": "nats-jetstream"`).

## Pisatutako irizpideak

Pisuak 100etik, puntuazioa 1 (eskasa) eta 5 (optimoa) artean. Ekarpena pisu × puntuazio / 100 da.

| Irizpidea | Pisua | MQTT 5 | Ekarp. | NATS JetStream | Ekarp. |
|---|---:|---:|---:|---:|---:|
| Iraunkortasuna | 15 | 2 | 0,30 | 5 | 0,75 |
| Ordena | 12 | 3 | 0,36 | 5 | 0,60 |
| Desduplikazioa | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Mezuen sinadura | 8 | 3 | 0,24 | 4 | 0,32 |
| Bridge federalak | 18 | 2 | 0,36 | 5 | 0,90 |
| Eragiketa aztarna | 10 | 3 | 0,30 | 5 | 0,50 |
| FastAPI/SQLite bateragarritasuna | 8 | 3 | 0,24 | 4 | 0,32 |
| Hedapen kostua | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Zergatik zenbaki hauek

- **Iraunkortasuna**: MQTT 5 saio iraunkorrak eta gordetako mezuak eskaintzen ditu, baina benetako historia kanpoko datu-base batera joaten da; JetStream-ek atxikipen konfiguragarria, erreprodukzioa eta kontsumitzaile iraunkorrak dituzten stream-ak eskaintzen ditu binario berean.
- **Ordena**: MQTT-ek ordena mantentzen du topic bakoitzeko saioa bizirik dagoen bitartean; berriro konektatzean edo bridge bat zeharkatzean, ordena hondatzen da. JetStream-ek stream-eko subject bakoitzeko segida-zenbakia ematen du.
- **Desduplikazioa**: MQTT QoS 1 berriro konektatzean duplikatzen da eta QoS 2 ustiatzea garestia da; JetStream-ek `Nats-Msg-Id` goiburuaren bidezko argitalpen-desduplikazioa dakar, leiho konfiguragarri batean (lehenetsita 2 min).
- **mTLS**: biak onartzen dute. MQTT-ek dagokion brokerari delegatzen dio; NATS-ek elkarrekiko TLSrekin integratzen du, eta, gainera, NKeys/JWT identitateekin.
- **Mezuen sinadura**: biek aplikazio mailan sinatzea eskatzen dute nodoaren TLS giltzarekin; NATS hobeto egokitzen da goiburuak muturretik muturrerako eraldaketarik gabe bidaiatzen baitute.
- **Bridge federalak**: pisu handiena duen irizpidea. MQTT hub-and-spoke da eta fabrikatzaile bakoitzak definitzen du bere bridge-a; NATS-ek leaf node-ak eta gateway-ak lehen mailako primitibo gisa dakartza, subject mapping-ekin.
- **Eragiketa aztarna eta kostua**: `nats-server` binario bakarra (Apache-2.0, JetStream barne) iraunkortasunerako datu-base bat eta saio-afinitate arauak arrastatzen dituen MQTT broker baten aurrean.
- **FastAPI/SQLite**: `nats-py` bezeroa asinkronoa da eta `ChatBackend`-en `async` metodoekin bat dator; sinadura egiaztatzeko `cryptography` erabiltzen da, dagoeneko `backend/requirements.txt`en dagoena.

## Erabakia

**NATS JetStream irabazi du** (4,84 vs 2,65). Ez da berdinketa: pisu handiena duen irizpidea, bridge federalak, diferentziarik handiena dagoen tokia da, eta proiektu honek bertan behar gogorra du.

Claketteserako arrazoi zehatzak:

1. **Dagoen konfiantza eredua egokitzen da ezer berririk asmatu gabe**: `docs/es/FEDERATION_SECURITY.md`ek nodoaren identitatea dominiu + X.509 ziurtagiri gisa definitzen du, CA baten aurkako mTLS eta `trusted_nodes` SHA-256 hatz-markarekin. NATS leaf node-ek mTLS berarekin autentikatzen dira, beraz, nodoen arteko bridge-ak dagoeneko dokumentatutako biraketa eta errebokazioa heredatzen ditu (`allowed = false` jarri eta eskua-ematea huts egiten du).
2. **Ordena + desduplikazioa + iraunkortasuna leku berean datoz**: `docs/es/FEDERATION_SCHEMA.md`eko entitateen trukeak `message` sartzen du `node_origin` eta `created_at`rekin. Subject bakoitzeko stream bat segida-zenbakiarekin eta `Nats-Msg-Id` bidezko desduplikazioarekin (gordetako `message_id` idempotentzia-giltza gisa erabiliz) logika hori kontsumitzaile bakoitzean berridaztea saihesten du.
3. **Binario bakarra bi beharrizanetarako**: `nats-server` berak zerbitzatzen du gertaera-bus iragankorra (Core NATS, huben eta gelako gertaeren kableatua) eta bus iraunkorra (JetStream, mezularitza eta txostenak). Docker hedapenarekin bat dator (backend 8000, frontend 3000, MariaDB 3306), bere datu-basea duen zerbitzu gehigarririk gehitu gabe.
4. **Bezeroa jatorriz asinkronoa da**: `nats-py` FastAPIren `lifespan`en integratzen da Hive eta erregistroaren hasieratzearekin batera, hari edo bridge gehigarririk gabe.

Arintutako eragozpenak:

1. **Ez dago MQTT QoS 2ren antzeko exactly-once-rik**: JetStream at-least-once da. Arintzea: `Nats-Msg-Id` bidezko argitalpen-desduplikazioa eta `message_id` idempotentzia-giltza gisa erabiltzen duten kontsumitzaile idempotenteak; SQLite da egia-iturria eta mezuaren egoera argitaratu aurretik idazten da.
2. **Nabigatzaileak ez du NATS protokoloa modu natiboan hitz egiten**: frontend-ek `web_socket_channel` erabiltzen du (ikusi `frontend/pubspec.yaml`). Arintzea: ertzeko WebSocket-a bizirik dirau; backend-ek JetStream kontsumitzaile bati harpidetu eta lehendik dagoen `ConnectionManager`era birbidaltzen du. Aldaketa barnekoa da eta Flutterrek ikusten duen APIa ukitu gabe dago.
3. **`nats-server`en MQTT entzuleak MQTT 3.1.1 baino ez du ulertzen** (MQTT 5 CONNECT baztertzen du): etorkizunean MQTT 5 eskatzen duen gailu bat agertuz gero, stream berean argitaratzen duen ertzeko MQTT broker dedikatu bat jarriko da. Uneko esparrutik kanpo dago: ez dago MQTT gailurik `frontend/pubspec.yaml`en inbentarioan.

## Ezartzearen ondorioak

### Backend abstraktua

`ChatBackend` interfazea dagoeneko badago `backend/app/chat_backend/base.py`en `start()`, `stop()` eta `send_message(...)`rekin, eta `backend/app/chat_backend/registry.py`ek abiaraztean behin erregistratuz inplementazioa ordezkatzea ahalbidetzen du. Ez dago interfazea ezta router-ak ukitu beharrik: inplementazio berri bat gehitzen da, `NatsJetStreamChatBackend`, `start()`en `NATS_URL`era konektatzen dena, `clakettes.events.>` subjectean `CLAKETTES_EVENTS` stream-a deklaratzen duena eta ertzeko kontsumitzaile iraunkorra sortzen duena; `stop()`en `drain` egin eta konexioa ixten du; `send_message(...)`en gaur egun `WebSocketChatBackend`ek eraikitzen duen payload bera argitaratzen du, `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) eta `signature`rekin batera. Sinadura RS256 da mezuaren irudikapen kanonikoaren gainean nodoaren TLS ziurtagiriaren giltza pribatuarekin, manifestua sinatzen duen bera (`docs/es/FEDERATION_PROTOCOL.md`). Pareak bere JWKSen aurka edo manifestuaren ziurtagiriaren aurka balioztatzen du gertaera aplikatu aurretik.

### Nodo bakarreko fallback-a

Bera utzi da: `WebSocketChatBackend` garapenean eta `TESTING=true`rekin lehenetsita erregistratutako backend-a da. SQLite-ek mezuak taula egia-iturri gisa mantentzen du; frontend-ek Hive (`OfflineCacheService`) eta FIFO ilara (`SyncQueueService`) erabiltzen ditu lineaz kanpoko modurako. Broker-a erabilgarri ez badago, `send_message`ek gertaera sinkronizazio-ilaran sartzen du `message_id`/`event_id` berarekin eta berriro konektatzean erreproduzitzen da, bikoizketarik gabe. Ertzeko WebSocket-a gaur egun `ConnectionManager`ek kudeatzen dituen konexio autentifikatuei entregatzen jarraitzen du.

### Nodoen arteko bridge-a

Nodo bakoitzak bere `nats-server` altxatzen du JetStream-ekin eta leaf node bat (edo clusteren arteko gateway bat) deklaratzen du hub nodoarantz. Leaf-a federazioko CAa erabiliz mTLS bidez autentikatzen da; parearen ziurtagiria `trusted_nodes.cert_fingerprint_sha256`en aurka balioztatzen da. Subject mapping-ek gertaerak `node_origin`, kanal eta motaren arabera bereizten ditu, horrela lehendik dauden `disable_chat`, `minimize_data`, `import_only`, `consent_required` eta `disable_search` politikak sarrerako kontsumitzailean aplikatzen dira iraunkortu aurretik. Parearen errebokazioa berehalakoa izaten jarraitzen du: `allowed = false` aldatzean, leaf-aren hurrengo mTLS eskua-emateak huts egiten du eta bere gertaerak sartzeari uzten diote.

## 4 urratseko migrazio-plana

1. **Prestatu**: gehitu `nats-py` `backend/requirements.txt`en eta `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` aldagaiak `.env.example`en. Ezarri `NatsJetStreamChatBackend` `CHAT_BACKEND=nats` banderaren atzean. Erregistroak lehenetsita WebSocket erregistratzen jarraitzen du: lehendik dagoen testik ez da aldatzen.
2. **Itzala**: NATSera ere argitaratu, inork entregatzeko kontsumitu gabe; balioztatze-kontsumitzaile batek segida, desduplikazioa eta sinadura egiaztatzen ditu bi nodoren artean stagingen. Benetako entrega WebSocket bidez doa oraindik.
3. **Aldaketa**: erregistratu NATS backend-a produkzioan eta bihurtu WebSocket endpoint-a bridge: bere JetStream kontsumitzaileak `ConnectionManager.broadcast()` elikatzen du. Gehitu bridge-aren puntuzko testak garraioaren bikoitzarekin eta `TESTING=true`rekin, suitean broker errealik abiarazi gabe. Entrega paraleloa: WS aktibo dirau aldaketan zehar.
4. **Itxi**: kendu prozesu barruko difusioa nodoen arteko mezularitzarako, gaitu mTLS leaf node-ak bi nodo errealen artean eta utzi nodo bakarreko modua dokumentatutako fallback gisa. Eguneratu aldaketa berean APIa (`python tools/gen_api.py --all`), zenbakiak eta READMEren roadmap-a, eta erreplikatu dokumentu hau zortzi ahizpetara `AGENTS.md`en arauaren arabera.

## Egoera

**2026-11-20an hartutako erabakia: NATS JetStream chat eta gertaeren broker gisa**, WebSocket ertze eta nodo bakarreko fallback gisa, eta MQTT 5 nukleo federaturako baztertuta.

Bere burua desblokeatzen du «Ebaluatu broker-a (MQTT vs NATS JetStream) chat eta gertaeretarako» elementuak, eta, zuzeneko mendekotasunez, nodoen arteko chat federatuaren, instantzien arteko gertaeren hedapenaren eta mezu-sinaduradun mTLS bridge-aren lanak. Ez du konfiantza eredua ezta dagoeneko dokumentatutako federazio endpoint-ak desblokeatzen edo ordezkatzen: horiek bezala erabiltzen ditu.
