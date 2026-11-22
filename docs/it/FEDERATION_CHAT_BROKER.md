# Valutazione del broker per chat ed eventi: MQTT 5 contro NATS JetStream

[ES](../es/FEDERATION_CHAT_BROKER.md) · [EN](../en/FEDERATION_CHAT_BROKER.md) · [FR](../fr/FEDERATION_CHAT_BROKER.md) · [DE](../de/FEDERATION_CHAT_BROKER.md) · [IT](FEDERATION_CHAT_BROKER.md) · [CA](../ca/FEDERATION_CHAT_BROKER.md) · [EU](../eu/FEDERATION_CHAT_BROKER.md) · [GL](../gl/FEDERATION_CHAT_BROKER.md) · [OC](../oc/FEDERATION_CHAT_BROKER.md)

Questo documento chiude la valutazione pendente su quale trasporto usare per la chat e la propagazione degli eventi tra i nodi di Clakettes. La decisione è vincolante per la Fase 8 (chat come coda federata) e convive con il backend WebSocket attuale descritto in `docs/es/ARQUITECTURA.md`.

**Stato di implementazione (Fasi 6-10):** la decisione adotta NATS JetStream come destinazione, ma oggi il trasporto duraturo in produzione è `DurableQueueBackend` sulla tabella `chat_outbox` con delegato WebSocket. Le variabili `NATS_*` e il flag `CHAT_BACKEND` del piano di migrazione **non esistono ancora** in `.env.example` né in `app/config.py`: `/api/federation/chat/bridge/config` segnala solo la destinazione prevista (`"transport": "nats-jetstream"`).

## Criteri ponderati

Pesi su 100, punteggio da 1 (deficiente) a 5 (ottimale). Il contributo è peso × punteggio / 100.

| Criterio | Peso | MQTT 5 | Contrib. | NATS JetStream | Contrib. |
|---|---:|---:|---:|---:|---:|
| Persistenza | 15 | 2 | 0,30 | 5 | 0,75 |
| Ordine | 12 | 3 | 0,36 | 5 | 0,60 |
| Deduplicazione | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Firma dei messaggi | 8 | 3 | 0,24 | 4 | 0,32 |
| Bridge federati | 18 | 2 | 0,36 | 5 | 0,90 |
| Impronta operativa | 10 | 3 | 0,30 | 5 | 0,50 |
| Compatibilità FastAPI/SQLite | 8 | 3 | 0,24 | 4 | 0,32 |
| Costo di distribuzione | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Perché questi numeri

- **Persistenza**: MQTT 5 offre sessioni durevoli e messaggi trattenuti, ma la storia vera finisce in un database esterno; JetStream fornisce stream con conservazione configurabile, replay e consumer durevoli nel binario stesso.
- **Ordine**: MQTT preserva l'ordine per topic finché la sessione è viva; alla riconnessione o attraverso un bridge, l'ordine si degrada. JetStream fornisce un numero di sequenza per subject all'interno dello stream.
- **Deduplicazione**: il QoS 1 di MQTT duplica dopo la riconnessione e il QoS 2 è costoso da gestire; JetStream porta la deduplicazione della pubblicazione tramite l'header `Nats-Msg-Id` entro una finestra configurabile (2 min per impostazione predefinita).
- **mTLS**: entrambi lo supportano. MQTT lo delega al broker di turno; NATS lo integra con TLS reciproco e, inoltre, identità NKeys/JWT.
- **Firma dei messaggi**: entrambi richiedono la firma a livello applicativo con la chiave TLS del nodo; NATS si adatta meglio perché gli header viaggiano senza trasformazione da estremo a estremo.
- **Bridge federati**: criterio con il peso maggiore. MQTT è hub-and-spoke e ogni fornitore definisce il proprio bridge; NATS porta leaf node e gateway come primitive di prima classe, con subject mapping.
- **Impronta operativa e costo**: un solo binario `nats-server` (Apache-2.0, JetStream incluso) contro un broker MQTT che di solito si trascina un database per persistere e regole di affinità di sessione.
- **FastAPI/SQLite**: il client `nats-py` è asincrono e si adatta ai metodi `async` di `ChatBackend`; la verifica della firma riutilizza `cryptography`, già presente in `backend/requirements.txt`.

## Decisione

**Vince NATS JetStream** (4,84 contro 2,65). Non è un pareggio: il criterio con il peso maggiore, i bridge federati, è quello in cui la differenza è più grande e in cui questo progetto ha un requisito tassativo.

Ragioni concrete per Clakettes:

1. **Il modello di fiducia esistente si adatta senza inventare nulla di nuovo**: `docs/es/FEDERATION_SECURITY.md` definisce l'identità del nodo come dominio + certificato X.509, mTLS verso una CA e `trusted_nodes` con impronta SHA-256. I leaf node di NATS si autenticano con lo stesso mTLS, così il bridge tra nodi eredita la rotazione e la revoca già documentate (impostare `allowed = false` e l'handshake fallisce).
2. **Ordine + deduplicazione + persistenza arrivano dallo stesso posto**: lo scambio di entità di `docs/es/FEDERATION_SCHEMA.md` include `message` con `node_origin` e `created_at`. Uno stream per subject con numero di sequenza e deduplicazione tramite `Nats-Msg-Id` (usando il `message_id` persistito come chiave di idempotenza) evita di riscrivere quella logica in ogni consumer.
3. **Un solo binario per due esigenze**: lo stesso `nats-server` serve il bus eventi effimero (Core NATS, cablaggio di hub ed eventi di sala) e il bus durevole (JetStream, messaggistica e report). Si adatta al deployment Docker attuale (backend 8000, frontend 3000, MariaDB 3306) senza aggiungere un altro servizio con il proprio database.
4. **Il client è asincrono per natura**: `nats-py` si integra nel `lifespan` di FastAPI insieme all'inizializzazione di Hive e del registry, senza thread o bridge extra.

Contro mitigati:

1. **Nessun exactly-once come il QoS 2 di MQTT**: JetStream è at-least-once. Mitigazione: deduplicazione della pubblicazione tramite `Nats-Msg-Id` più consumer idempotenti che usano `message_id` come chiave di idempotenza; SQLite resta la fonte di verità e lo stato del messaggio viene scritto prima della pubblicazione.
2. **Il browser non parla il protocollo NATS in modo nativo**: il frontend usa `web_socket_channel` (vedi `frontend/pubspec.yaml`). Mitigazione: il WebSocket di bordo resta attivo; il backend sottoscrive un consumer JetStream e inoltra al `ConnectionManager` esistente. Il cambiamento è interno e l'API che vede Flutter non viene toccata.
3. **Il listener MQTT di `nats-server` capisce solo MQTT 3.1.1** (rifiuta il CONNECT MQTT 5): se in futuro comparirà un dispositivo che richiede MQTT 5, si installerà un broker MQTT di bordo dedicato che pubblica nello stesso stream. Questo esula dall'ambito attuale: non ci sono dispositivi MQTT nell'inventario di `frontend/pubspec.yaml`.

## Conseguenze dell'implementazione

### Backend astratto

L'interfaccia `ChatBackend` esiste già in `backend/app/chat_backend/base.py` con `start()`, `stop()` e `send_message(...)`, e `backend/app/chat_backend/registry.py` permette di sostituire l'implementazione registrandola una sola volta all'avvio. Non c'è bisogno di toccare né l'interfaccia né i router: si aggiunge una nuova implementazione, `NatsJetStreamChatBackend`, che in `start()` si connette a `NATS_URL`, dichiara lo stream `CLAKETTES_EVENTS` sul subject `clakettes.events.>` e crea il consumer durevole di bordo; in `stop()` esegue il `drain` e chiude la connessione; in `send_message(...)` pubblica lo stesso payload che oggi costruisce `WebSocketChatBackend`, più gli header con `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) e `signature`. La firma è RS256 sulla rappresentazione canonica del messaggio con la chiave privata del certificato TLS del nodo, la stessa che firma il manifest (`docs/es/FEDERATION_PROTOCOL.md`). Il peer la valida contro il suo JWKS o contro il certificato del manifest prima di applicare l'evento.

### Fallback mononodo

Viene mantenuto così com'è: `WebSocketChatBackend` resta il backend registrato per impostazione predefinita in sviluppo e con `TESTING=true`. SQLite conserva la tabella dei messaggi come fonte di verità; il frontend continua con Hive (`OfflineCacheService`) e la coda FIFO (`SyncQueueService`) per la modalità offline. Se il broker non è disponibile, `send_message` accoda l'evento nella coda di sincronizzazione con lo stesso `message_id`/`event_id` e viene riprodotto alla riconnessione, senza duplicati. Il WebSocket di bordo continua a consegnare alle connessioni autenticate gestite oggi da `ConnectionManager`.

### Bridge tra nodi

Ogni nodo avvia il proprio `nats-server` con JetStream e dichiara un leaf node (o un gateway tra cluster) verso il nodo hub. Il leaf si autentica con mTLS usando la CA federata; il certificato del peer viene validato contro `trusted_nodes.cert_fingerprint_sha256`. Il subject mapping separa gli eventi per `node_origin`, per canale e per tipo, così le policy esistenti `disable_chat`, `minimize_data`, `import_only`, `consent_required` e `disable_search` vengono applicate nel consumer in ingresso prima della persistenza. La revoca di un peer resta immediata: impostando `allowed = false`, il successivo handshake mTLS del leaf fallisce e i suoi eventi smettono di arrivare.

## Piano di migrazione in 4 passi

1. **Preparare**: aggiungere `nats-py` a `backend/requirements.txt` e le variabili `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` a `.env.example`. Implementare `NatsJetStreamChatBackend` dietro il flag `CHAT_BACKEND=nats`. Il registry continua a registrare WebSocket per impostazione predefinita: nessun test esistente cambia.
2. **Ombra**: pubblicare anche su NATS senza che nessuno consumi per la consegna; un consumer di validazione controlla sequenza, deduplicazione e firma tra due nodi in staging. La consegna reale passa ancora da WebSocket.
3. **Cut-over**: registrare il backend NATS in produzione e trasformare l'endpoint WebSocket in un bridge: il suo consumer JetStream alimenta `ConnectionManager.broadcast()`. Aggiungere test puntuali del bridge con il doppio del trasporto e `TESTING=true`, senza avviare un broker reale nella suite. Consegna in parallelo: WS resta attivo durante il cambio.
4. **Chiudere**: rimuovere il broadcast in-process per la messaggistica tra nodi, attivare i leaf node mTLS tra due nodi reali e lasciare la modalità mononodo come fallback documentato. Aggiornare nello stesso cambio l'API (`python tools/gen_api.py --all`), le cifre e la roadmap del README, e replicare questa doc nelle otto sorelle secondo la regola di `AGENTS.md`.

## Stato

**Decisione adottata il 2026-11-20: NATS JetStream come broker di chat ed eventi**, con WebSocket come bordo e fallback mononodo, e MQTT 5 scartato per il nucleo federato.

Sblocca la voce «Valutare il broker (MQTT vs NATS JetStream) per chat ed eventi» stessa e, per dipendenza diretta, i lavori di chat federata tra nodi, propagazione degli eventi tra istanze e bridge mTLS con firma dei messaggi. Non sblocca né sostituisce il modello di fiducia né gli endpoint di federazione già documentati: li riutilizza così come sono.
