# Evaluacion de broker per lo chat e los eveniments: MQTT 5 contra NATS JetStream

[OC](FEDERATION_CHAT_BROKER.md)

Aqueste document clau l'evaluacion en espera sus quin transport usar per lo chat e la propagacion d'eveniments entre los nodes de Clakettes. La decision es constrenhenta per la Fasa 8 (lo chat coma cua federada) e conviu amb lo backend WebSocket actual descrit dins `docs/es/ARQUITECTURA.md`.

## Criteris pesats

Peses sus 100, nota de 1 (deficient) a 5 (optimal). La contribucion es pes × nota / 100.

| Criteri | Pes | MQTT 5 | Contrib. | NATS JetStream | Contrib. |
|---|---:|---:|---:|---:|---:|
| Persisténcia | 15 | 2 | 0,30 | 5 | 0,75 |
| Òrdre | 12 | 3 | 0,36 | 5 | 0,60 |
| Desduplicacion | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Signatura dels messatges | 8 | 3 | 0,24 | 4 | 0,32 |
| Bridges federats | 18 | 2 | 0,36 | 5 | 0,90 |
| Emprenta operacional | 10 | 3 | 0,30 | 5 | 0,50 |
| Compatibilitat FastAPI/SQLite | 8 | 3 | 0,24 | 4 | 0,32 |
| Cost de desplegament | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Perque aquestes chifras

- **Persisténcia**: MQTT 5 ofrís de sessions durablas e de messatges retenguts, mas l'istoric real acaba dins una basa extèrna; JetStream dona de streams amb retencion configurabla, replay e consomidors durablas dins lo binari meteis.
- **Òrdre**: MQTT preserva l'òrdre per tòpic mientras que la session viu; a la recomnexion o a travèrs d'un bridge, l'òrdre se degrada. JetStream dona un numèro de sequéncia per subject dins l'stream.
- **Desduplicacion**: lo QoS 1 de MQTT duplica après recomnexion e lo QoS 2 es car de gestionar; JetStream apòrta la desduplicacion de publicacion per l'entèsta `Nats-Msg-Id` dins una fenèstra configurabla (2 min per defaut).
- **mTLS**: ambdos dos o suportan. MQTT o delegua al broker del moment; NATS o integra amb TLS mutu e, en mai, las identitats NKeys/JWT.
- **Signatura dels messatges**: ambdos dos demandan una signatura al nivèl de l'aplicacion amb la clau TLS del node; NATS conven melhor perque las entèstas viatjan sens transformacion de cap a cap.
- **Bridges federats**: criteri amb lo pes mai grand. MQTT es hub-and-spoke e cada fabricant definís son bridge; NATS apòrta los leaf nodes e los gateways coma primitivas de primièr nivèl, amb subject mapping.
- **Emprenta operacional e cost**: un sol binari `nats-server` (Apache-2.0, JetStream inclús) contra un broker MQTT que trai generalament una basa per persistir e de règlas d'afinitat de session.
- **FastAPI/SQLite**: lo client `nats-py` es asincròn e conven amb los metòdes `async` de `ChatBackend`; la verificacion de signatura reutiliza `cryptography`, ja present dins `backend/requirements.txt`.

## Decision

**NATS JetStream ganha** (4,84 contra 2,65). Es pas un egalatge: lo criteri amb lo pes mai grand, los bridges federats, es ont la diferéncia es la mai granda e ont aqueste projecte a una exigéncia absoluda.

Rasons concretas per Clakettes:

1. **Lo modèl de fisança existent conven sens inventar res de nòu**: `docs/es/FEDERATION_SECURITY.md` definís l'identitat de node coma domeni + certificat X.509, mTLS contra una CA e `trusted_nodes` amb emprenta SHA-256. Los leaf nodes de NATS s'autentican amb aquel meteis mTLS, atal lo bridge entre nodes ereta de la rotacion e de la revocacion ja documentadas (metre `allowed = false` e lo handshake fracassa).
2. **Òrdre + desduplicacion + persisténcia venon del meteis luòc**: l'escambi d'entitats de `docs/es/FEDERATION_SCHEMA.md` inclutz `message` amb `node_origin` e `created_at`. Un stream per subject amb numèro de sequéncia e desduplicacion per `Nats-Msg-Id` (en utilisant lo `message_id` persistit coma clau d'idempoténcia) evita de reescriure aquela logica dins cada consomidor.
3. **Un sol binari per dos besonhs**: lo meteis `nats-server` servís lo bus d'eveniments efemèr (Core NATS, cablatge dels hubs e eveniments de sala) e lo bus durabl (JetStream, messatgeria e rapòrts). Conven amb lo desplegament Docker actual (backend 8000, frontend 3000, MariaDB 3306) sens ajustar un autre servici amb sa basa.
4. **Lo client es asincròn per natura**: `nats-py` s'integra dins lo `lifespan` de FastAPI amb l'inicializacion de Hive e del registry, sens fils ni bridges suplementaris.

Inconvenients atenuats:

1. **Pas d'exactly-once coma lo QoS 2 de MQTT**: JetStream es at-least-once. Atenuacion: desduplicacion de publicacion per `Nats-Msg-Id` mai de consomidors idempotents qu'utilizan `message_id` coma clau d'idempoténcia; SQLite demòra la font de vertat e l'estat del messatge es escrich abans de publicar.
2. **Lo navigador parla pas nativament lo protocol NATS**: lo frontend utiliza `web_socket_channel` (vejatz `frontend/pubspec.yaml`). Atenuacion: lo WebSocket de bord demòra viu; lo backend s'abona a un consomidor JetStream e reenvia cap al `ConnectionManager` existent. Lo cambiament es interne e l'API que vei Flutter es pas tocat.
3. **Lo listener MQTT de `nats-server` compren sonque MQTT 3.1.1** (rebuta los CONNECT MQTT 5): se d'avenir apareis un dispositiu que demand MQTT 5, se metrà en plaça un broker MQTT de bord dedicat que publicarà dins l'stream meteis. Aquò demòra fòra del perimetre actual: i a pas de dispositius MQTT dins l'inventari de `frontend/pubspec.yaml`.

## Consequéncias d'implementacion

### Backend abstrach

L'interfacia `ChatBackend` existís ja dins `backend/app/chat_backend/base.py` amb `start()`, `stop()` e `send_message(...)`, e `backend/app/chat_backend/registry.py` permet de remplaçar l'implementacion en l'enregistrant un sol còp al demarratge. I a res a tocar ni a l'interfacia ni als routers: s'ajusta una implementacion nòva, `NatsJetStreamChatBackend`, que dins `start()` se connecta a `NATS_URL`, declara l'stream `CLAKETTES_EVENTS` sul subject `clakettes.events.>` e crea lo consomidor durabl de bord; dins `stop()` fa un `drain` e tampa la connexion; dins `send_message(...)` publica la meteissa carga utila que bastís uèi `WebSocketChatBackend`, mai d'entèstas amb `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) e `signature`. La signatura es RS256 sus la representacion canonica del messatge amb la clau privada del certificat TLS del node, la meteissa que signa lo manifest (`docs/es/FEDERATION_PROTOCOL.md`). Lo pair la valida contra son JWKS o contra lo certificat del manifest abans d'aplicar l'eveniment.

### Fallback mononode

Es gardat atal: `WebSocketChatBackend` demòra lo backend enregistrat per defaut en desvolopament e amb `TESTING=true`. SQLite garda la tabla dels messatges coma font de vertat; lo frontend contunha amb Hive (`OfflineCacheService`) e la cua FIFO (`SyncQueueService`) per lo mòde fòra linha. Se lo broker es pas disponible, `send_message` met l'eveniment en cua dins la cua de sincronizacion amb lo meteis `message_id`/`event_id` e es rejugat a la recomnexion, sens doblons. Lo WebSocket de bord contunha de liurar a las connexions autentificadas gestionadas uèi per `ConnectionManager`.

### Bridge entre nodes

Cada node levanta son `nats-server` amb JetStream e declara un leaf node (o un gateway entre clustres) cap al node hub. Lo leaf s'autentica amb mTLS en utilisant la CA federada; lo certificat del pair es validat contra `trusted_nodes.cert_fingerprint_sha256`. Lo subject mapping separa los eveniments per `node_origin`, per canau e per tipe, atal las politicas existentas `disable_chat`, `minimize_data`, `import_only`, `consent_required` e `disable_search` son aplicadas dins lo consomidor d'intrada abans de persistir. La revocacion d'un pair demòra immediata: en passant `allowed = false`, lo handshake mTLS seguent del leaf fracassa e sos eveniments arrèstan d'intrar.

## Pla de migracion en 4 etapas

1. **Preparar**: ajustar `nats-py` a `backend/requirements.txt` e las variablas `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` a `.env.example`. Implementar `NatsJetStreamChatBackend` darrièr lo drapèl `CHAT_BACKEND=nats`. Lo registry contunha d'enregistrar WebSocket per defaut: cap de test existent cambia.
2. **Ombra**: publicar tanben dins NATS sens que degun consome per la liurason; un consomidor de validacion verifica sequéncia, desduplicacion e signatura entre dos nodes en staging. La liurason vertadièra passa encara per WebSocket.
3. **Bascule**: enregistrar lo backend NATS en produccion e convertir l'endpoint WebSocket en bridge: son consomidor JetStream alimenta `ConnectionManager.broadcast()`. Ajustar de tests ponctuals del bridge amb lo doble de transpòrt e `TESTING=true`, sens demarrar de broker real dins la suite. Liurason en parallèl: WS demòra actiu pendent lo cambiament.
4. **Clavar**: retirar la difusion en procès per la messatgeria entre nodes, activar los leaf nodes mTLS entre dos nodes reals e daissar lo mòde mononode coma fallback documentat. Actualizar dins lo meteis cambiament l'API (`python tools/gen_api.py --all`), las chifras e la roadmap del README, e replicar aqueste document a las uèch sòrs segon la règla de `AGENTS.md`.

## Estat

**Decision adoptada lo 2026-11-20: NATS JetStream coma broker de chat e d'eveniments**, amb WebSocket coma bord e fallback mononode, e MQTT 5 regetat per lo nuclèu federat.

Desbloca l'element «Evaluar broker (MQTT vs NATS JetStream) per lo chat e los eveniments» meteis e, per dependéncia directa, los trabalhs de chat federat entre nodes, propagacion d'eveniments entre instàncias e bridge mTLS amb signatura dels messatges. Desbloca ni remplaça pas lo modèl de fisança ni los endpoints de federacion ja documentats: los reutiliza atal.
