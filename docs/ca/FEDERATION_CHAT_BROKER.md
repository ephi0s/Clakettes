# Avaluació de broker per a xat i esdeveniments: MQTT 5 davant NATS JetStream

[ES](../es/FEDERATION_CHAT_BROKER.md) · [EN](../en/FEDERATION_CHAT_BROKER.md) · [FR](../fr/FEDERATION_CHAT_BROKER.md) · [DE](../de/FEDERATION_CHAT_BROKER.md) · [IT](../it/FEDERATION_CHAT_BROKER.md) · [CA](FEDERATION_CHAT_BROKER.md) · [EU](../eu/FEDERATION_CHAT_BROKER.md) · [GL](../gl/FEDERATION_CHAT_BROKER.md) · [OC](../oc/FEDERATION_CHAT_BROKER.md)

Aquest document tanca l'avaluació pendent sobre quin transport usar per al xat i la propagació d'esdeveniments entre nodes de Clakettes. La decisió és vinculant per a la Fase 8 (xat com a cua federada) i conviu amb el backend WebSocket actual descrit a `docs/es/ARQUITECTURA.md`.

**Estat d'implementació (Fases 6-10):** la decisió adopta NATS JetStream com a destí, però avui el transport durador en producció és `DurableQueueBackend` sobre la taula `chat_outbox` amb delegat WebSocket. Les variables `NATS_*` i el flag `CHAT_BACKEND` del pla de migració **no existeixen encara** a `.env.example` ni a `app/config.py`: `/api/federation/chat/bridge/config` només informa del destí previst (`"transport": "nats-jetstream"`).

## Criteris ponderats

Pesos sobre 100, puntuació d'1 (deficient) a 5 (òptim). La contribució és pes × puntuació / 100.

| Criteri | Pes | MQTT 5 | Contrib. | NATS JetStream | Contrib. |
|---|---:|---:|---:|---:|---:|
| Persistència | 15 | 2 | 0,30 | 5 | 0,75 |
| Ordre | 12 | 3 | 0,36 | 5 | 0,60 |
| Deduplicació | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Signatura de missatges | 8 | 3 | 0,24 | 4 | 0,32 |
| Bridges federats | 18 | 2 | 0,36 | 5 | 0,90 |
| Petjada operativa | 10 | 3 | 0,30 | 5 | 0,50 |
| Compatibilitat FastAPI/SQLite | 8 | 3 | 0,24 | 4 | 0,32 |
| Cost de desplegament | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Per què aquests números

- **Persistència**: MQTT 5 ofereix sessions duradores i missatges retinguts, però l'historial real acaba en una base externa; JetStream dóna streams amb retenció configurable, replay i consumidors duradors al mateix binari.
- **Ordre**: MQTT preserva l'ordre per tòpic mentre la sessió viu; en reconnectar o travessar un bridge, l'ordre es degrada. JetStream dóna un número de seqüència per subject dins de l'stream.
- **Deduplicació**: el QoS 1 de MQTT duplica en reconnectar i el QoS 2 és costós d'operar; JetStream aporta la deduplicació de publicació mitjançant la capçalera `Nats-Msg-Id` dins d'una finestra configurable (2 min per defecte).
- **mTLS**: tots dos ho suporten. MQTT ho delega al broker de torn; NATS ho integra amb TLS mutu i, a més, identitats NKeys/JWT.
- **Signatura de missatges**: tots dos requereixen signatura a nivell d'aplicació amb la clau TLS del node; NATS encaja millor perquè les capçaleres viatgen sense transformació de punta a punta.
- **Bridges federats**: criteri amb més pes. MQTT és hub-and-spoke i cada fabricant defineix el seu bridge; NATS aporta leaf nodes i gateways com a primitives de primera classe, amb subject mapping.
- **Petjada operativa i cost**: un sol binari `nats-server` (Apache-2.0, JetStream inclòs) davant d'un broker MQTT que sol arrossegar una base per persistir i regles d'afinitat de sessió.
- **FastAPI/SQLite**: el client `nats-py` és asíncron i encaja amb els mètodes `async` de `ChatBackend`; la verificació de signatura reutilitza `cryptography`, ja present a `backend/requirements.txt`.

## Decisió

**Guanya NATS JetStream** (4,84 davant 2,65). No és un empat: el criteri amb més pes, els bridges federats, és on la diferència és més gran i on aquest projecte té un requisit ferm.

Raons concretes per a Clakettes:

1. **El model de confiança existent encaja sense inventar res de nou**: `docs/es/FEDERATION_SECURITY.md` defineix la identitat de node com a domini + certificat X.509, mTLS contra una CA i `trusted_nodes` amb empremta SHA-256. Els leaf nodes de NATS s'autentiquen amb aquest mateix mTLS, de manera que el bridge entre nodes hereta la rotació i la revocació ja documentades (marcar `allowed = false` i l'handshake falla).
2. **Ordre + deduplicació + persistència venen del mateix lloc**: l'intercanvi d'entitats de `docs/es/FEDERATION_SCHEMA.md` inclou `message` amb `node_origin` i `created_at`. Un stream per subject amb número de seqüència i deduplicació per `Nats-Msg-Id` (emprant el `message_id` persistit com a clau d'idempotència) evita reescriure aquesta lògica a cada consumidor.
3. **Un sol binari per a dues necessitats**: el mateix `nats-server` serveix el bus d'esdeveniments efímer (Core NATS, cablejat d'hubs i esdeveniments de sala) i el bus durador (JetStream, missatgeria i informes). Encaja amb el desplegament Docker actual (backend 8000, frontend 3000, MariaDB 3306) sense afegir un altre servei amb la seva base.
4. **El client és asíncron per naturalesa**: `nats-py` s'integra al `lifespan` de FastAPI juntament amb la inicialització de Hive i del registry, sense fils ni bridges extra.

Inconvenients mitigats:

1. **No hi ha exactly-once com el QoS 2 de MQTT**: JetStream és at-least-once. Mitigació: deduplicació de publicació per `Nats-Msg-Id` més consumidors idempotents que usen `message_id` com a clau d'idempotència; SQLite continua sent la font de veritat i l'estat del missatge s'escriu abans de publicar.
2. **El navegador no parla el protocol NATS de forma nativa**: el frontend fa servir `web_socket_channel` (vegeu `frontend/pubspec.yaml`). Mitigació: el WebSocket de vora continua viu; el backend subscriu un consumidor de JetStream i reenvia al `ConnectionManager` existent. El canvi és intern i l'API que veu Flutter no es toca.
3. **El listener MQTT de `nats-server` només entén MQTT 3.1.1** (rebutja el CONNECT de MQTT 5): si en el futur apareix un dispositiu que exigeixi MQTT 5, es muntarà un broker MQTT de vora dedicat que publiqui al mateix stream. Queda fora de l'àmbit actual: no hi ha dispositius MQTT a l'inventari de `frontend/pubspec.yaml`.

## Conseqüències d'implementació

### Backend abstracte

La interfície `ChatBackend` ja existeix a `backend/app/chat_backend/base.py` amb `start()`, `stop()` i `send_message(...)`, i `backend/app/chat_backend/registry.py` permet substituir la implementació registrant-la una sola vegada a l'arrencada. No cal tocar ni la interfície ni els routers: s'afegeix una implementació nova, `NatsJetStreamChatBackend`, que a `start()` es connecta a `NATS_URL`, declara l'stream `CLAKETTES_EVENTS` sobre el subject `clakettes.events.>` i crea el consumidor durador de vora; a `stop()` fa `drain` i tanca la connexió; a `send_message(...)` publica el mateix payload que avui construeix `WebSocketChatBackend`, més capçaleres amb `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) i `signature`. La signatura és RS256 sobre la representació canònica del missatge amb la clau privada del certificat TLS del node, la mateixa que signa el manifest (`docs/es/FEDERATION_PROTOCOL.md`). El parell la valida contra el seu JWKS o contra el certificat del manifest abans d'aplicar l'esdeveniment.

### Fallback mononode

Es manté tal qual: `WebSocketChatBackend` continua sent el backend registrat per defecte en desenvolupament i amb `TESTING=true`. SQLite conserva la taula de missatges com a font de veritat; el frontend continua amb Hive (`OfflineCacheService`) i la cua FIFO (`SyncQueueService`) per al mode offline. Si el broker no està disponible, `send_message` encua l'esdeveniment a la cua de sincronització amb el mateix `message_id`/`event_id` i es replaya en reconnectar, sense duplicats. El WebSocket de vora continua lliurant a les connexions autenticades que avui gestiona `ConnectionManager`.

### Bridge entre nodes

Cada node aixeca el seu `nats-server` amb JetStream i declara un leaf node (o un gateway entre clústers) cap al node hub. El leaf s'autentica amb mTLS mitjançant la CA federada; el certificat del parell es valida contra `trusted_nodes.cert_fingerprint_sha256`. El subject mapping separa els esdeveniments per `node_origin`, per canal i per tipus, de manera que les polítiques existents `disable_chat`, `minimize_data`, `import_only`, `consent_required` i `disable_search` s'apliquen al consumidor d'entrada abans de persistir. La revocació d'un parell continua sent immediata: en canviar `allowed = false`, el següent handshake mTLS del leaf falla i els seus esdeveniments deixen d'entrar.

## Pla de migració en 4 passos

1. **Preparar**: afegir `nats-py` a `backend/requirements.txt` i les variables `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` a `.env.example`. Implementar `NatsJetStreamChatBackend` darrere del flag `CHAT_BACKEND=nats`. El registry continua registrant WebSocket per defecte: cap test existent canvia.
2. **Ombra**: publicar també a NATS sense que ningú consumeixi per lliurar; un consumidor de validació comprova seqüència, deduplicació i signatura entre dos nodes a staging. El lliurament real segueix anant per WebSocket.
3. **Cut-over**: registrar el backend NATS a producció i convertir l'endpoint WebSocket en pont: el seu consumidor de JetStream alimenta `ConnectionManager.broadcast()`. Afegir tests puntuals del bridge amb el doble de transport i `TESTING=true`, sense arrencar un broker real a la suite. Lliurament en paral·lel: WS continua actiu durant el canvi.
4. **Tancar**: retirar la difusió en procés per a la missatgeria entre nodes, activar els leaf nodes mTLS entre dos nodes reals i deixar el mode mononode com a fallback documentat. Actualitzar en el mateix canvi l'API (`python tools/gen_api.py --all`), les xifres i el roadmap del README, i replicar aquest doc a les vuit germanes segons la norma de `AGENTS.md`.

## Estat

**Decisió adoptada el 2026-11-20: NATS JetStream com a broker de xat i esdeveniments**, amb WebSocket com a vora i fallback mononode, i MQTT 5 descartat per al nucli federat.

Desbloqueja el propi ítem «Avaluar broker (MQTT vs NATS JetStream) per a xat i esdeveniments» i, per dependència directa, els treballs de xat federat entre nodes, propagació d'esdeveniments entre instàncies i bridge mTLS amb signatura de missatges. No desbloqueja ni substitueix el model de confiança ni els endpoints de federació ja documentats: els reutilitza tal qual.
