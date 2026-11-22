# Broker-Bewertung für Chat und Ereignisse: MQTT 5 gegenüber NATS JetStream

[ES](../es/FEDERATION_CHAT_BROKER.md) · [EN](../en/FEDERATION_CHAT_BROKER.md) · [FR](../fr/FEDERATION_CHAT_BROKER.md) · [DE](FEDERATION_CHAT_BROKER.md) · [IT](../it/FEDERATION_CHAT_BROKER.md) · [CA](../ca/FEDERATION_CHAT_BROKER.md) · [EU](../eu/FEDERATION_CHAT_BROKER.md) · [GL](../gl/FEDERATION_CHAT_BROKER.md) · [OC](../oc/FEDERATION_CHAT_BROKER.md)

Dieses Dokument schließt die ausstehende Bewertung ab, welcher Transport für Chat und Ereignisverbreitung zwischen Clakettes-Knoten verwendet werden soll. Die Entscheidung ist bindend für Phase 8 (Chat als föderierte Warteschlange) und besteht neben dem aktuellen WebSocket-Backend, das in `docs/es/ARQUITECTURA.md` beschrieben ist.

**Implementierungsstatus (Phasen 6-10):** Die Entscheidung sieht NATS JetStream als Ziel vor, aber derzeit ist der dauerhafte Transport in Produktion `DurableQueueBackend` über die Tabelle `chat_outbox` mit WebSocket-Delegat. Die Variablen `NATS_*` und der Flag `CHAT_BACKEND` aus dem Migrationsplan **existieren weder** in `.env.example` **noch** in `app/config.py`: `/api/federation/chat/bridge/config` meldet nur das vorgesehene Ziel (`"transport": "nats-jetstream"`).

## Gewichtete Kriterien

Gewichte von 100, Bewertung von 1 (mangelhaft) bis 5 (optimal). Der Beitrag ist Gewicht × Bewertung / 100.

| Kriterium | Gewicht | MQTT 5 | Beitrag | NATS JetStream | Beitrag |
|---|---:|---:|---:|---:|---:|
| Persistenz | 15 | 2 | 0,30 | 5 | 0,75 |
| Reihenfolge | 12 | 3 | 0,36 | 5 | 0,60 |
| Deduplizierung | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Nachrichtensignatur | 8 | 3 | 0,24 | 4 | 0,32 |
| Föderierte Bridges | 18 | 2 | 0,36 | 5 | 0,90 |
| Operativer Fußabdruck | 10 | 3 | 0,30 | 5 | 0,50 |
| FastAPI/SQLite-Kompatibilität | 8 | 3 | 0,24 | 4 | 0,32 |
| Bereitstellungskosten | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Warum diese Zahlen

- **Persistenz**: MQTT 5 bietet dauerhafte Sitzungen und retainte Nachrichten, aber die echte Historie landet in einer externen Datenbank; JetStream liefert Streams mit konfigurierbarer Aufbewahrung, Replay und dauerhaften Consumern direkt in der Binary.
- **Reihenfolge**: MQTT bewahrt die Reihenfolge pro Topic, solange die Sitzung lebt; bei Wiederverbindung oder über einen Bridge verschlechtert sie sich. JetStream liefert eine Sequenznummer pro Subject innerhalb des Streams.
- **Deduplizierung**: MQTT QoS 1 dupliziert nach Wiederverbindung und QoS 2 ist aufwendig zu betreiben; JetStream bringt Deduplizierung der Veröffentlichung über den Header `Nats-Msg-Id` innerhalb eines konfigurierbaren Fensters (standardmäßig 2 min).
- **mTLS**: beide unterstützen es. MQTT überlässt es dem jeweiligen Broker; NATS integriert es mit gegenseitigem TLS und zusätzlich NKeys/JWT-Identitäten.
- **Nachrichtensignatur**: beide erfordern eine Signatur auf Anwendungsebene mit dem TLS-Schlüssel des Knotens; NATS passt besser, weil Header unverändert von Ende zu Ende laufen.
- **Föderierte Bridges**: Kriterium mit dem höchsten Gewicht. MQTT ist Hub-and-Spoke und jeder Hersteller definiert seine eigene Bridge; NATS bringt Leaf Nodes und Gateways als Primitive erster Klasse mit Subject Mapping.
- **Operativer Fußabdruck und Kosten**: eine einzige `nats-server`-Binary (Apache-2.0, JetStream inklusive) gegenüber einem MQTT-Broker, der üblicherweise eine Datenbank für Persistenz und Sitzungsaffinitätsregeln mitzieht.
- **FastAPI/SQLite**: der Client `nats-py` ist asynchron und passt zu den `async`-Methoden von `ChatBackend`; die Signaturprüfung nutzt `cryptography` wieder, das bereits in `backend/requirements.txt` vorhanden ist.

## Entscheidung

**NATS JetStream gewinnt** (4,84 gegenüber 2,65). Kein Unentschieden: das Kriterium mit dem größten Gewicht, föderierte Bridges, ist genau dort, wo der Unterschied am größten ist und wo dieses Projekt eine harte Anforderung hat.

Konkrete Gründe für Clakettes:

1. **Das bestehende Vertrauensmodell passt, ohne etwas Neues zu erfinden**: `docs/es/FEDERATION_SECURITY.md` definiert die Knotenidentität als Domäne + X.509-Zertifikat, mTLS gegen eine CA und `trusted_nodes` mit SHA-256-Fingerprint. Die Leaf Nodes von NATS authentifizieren sich mit genau diesem mTLS, sodass die Bridge zwischen Knoten die bereits dokumentierte Rotation und Widerrufung erbt (`allowed = false` setzen und der Handshake schlägt fehl).
2. **Reihenfolge + Deduplizierung + Persistenz kommen aus derselben Quelle**: der Entitätentausch in `docs/es/FEDERATION_SCHEMA.md` enthält `message` mit `node_origin` und `created_at`. Ein Stream pro Subject mit Sequenznummer und Deduplizierung über `Nats-Msg-Id` (mit der persistierten `message_id` als Idempotenzschlüssel) vermeidet es, diese Logik in jedem Consumer neu zu schreiben.
3. **Eine Binary für zwei Bedürfnisse**: derselbe `nats-server` bedient den flüchtigen Event-Bus (Core NATS, Verdrahtung von Hubs und Raumereignissen) und den dauerhaften Bus (JetStream, Nachrichten und Berichte). Das passt zum aktuellen Docker-Deployment (Backend 8000, Frontend 3000, MariaDB 3306), ohne einen weiteren Dienst mit eigener Datenbank hinzuzufügen.
4. **Der Client ist von Natur aus asynchron**: `nats-py` integriert sich in den `lifespan` von FastAPI neben der Initialisierung von Hive und dem Registry, ohne zusätzliche Threads oder Bridges.

Gemilderte Nachteile:

1. **Kein exactly-once wie bei MQTT QoS 2**: JetStream ist at-least-once. Milderung: Deduplizierung der Veröffentlichung über `Nats-Msg-Id` plus idempotente Consumer, die `message_id` als Idempotenzschlüssel verwenden; SQLite bleibt die Quelle der Wahrheit und der Nachrichtenstatus wird vor der Veröffentlichung geschrieben.
2. **Der Browser spricht das NATS-Protokoll nicht nativ**: das Frontend verwendet `web_socket_channel` (siehe `frontend/pubspec.yaml`). Milderung: das Edge-WebSocket bleibt bestehen; das Backend abonniert einen JetStream-Consumer und leitet an das bestehende `ConnectionManager` weiter. Die Änderung ist intern und die API, die Flutter sieht, bleibt unberührt.
3. **Der MQTT-Listener von `nats-server` versteht nur MQTT 3.1.1** (lehnt MQTT-5-CONNECT ab): falls künftig ein Gerät auftaucht, das MQTT 5 verlangt, wird ein dedizierter Edge-MQTT-Broker eingerichtet, der in denselben Stream veröffentlicht. Das liegt außerhalb des aktuellen Umfangs: im Inventar von `frontend/pubspec.yaml` gibt es keine MQTT-Geräte.

## Implementierungsfolgen

### Abstraktes Backend

Die Schnittstelle `ChatBackend` existiert bereits in `backend/app/chat_backend/base.py` mit `start()`, `stop()` und `send_message(...)`, und `backend/app/chat_backend/registry.py` erlaubt es, die Implementierung durch einmalige Registrierung beim Start zu ersetzen. Weder die Schnittstelle noch die Router müssen angefasst werden: es wird eine neue Implementierung hinzugefügt, `NatsJetStreamChatBackend`, die in `start()` eine Verbindung zu `NATS_URL` herstellt, den Stream `CLAKETTES_EVENTS` über das Subject `clakettes.events.>` deklariert und den dauerhaften Edge-Consumer erstellt; in `stop()` führt sie ein `drain` durch und schließt die Verbindung; in `send_message(...)` veröffentlicht sie dieselbe Nutzlast, die heute `WebSocketChatBackend` erzeugt, plus Header mit `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) und `signature`. Die Signatur ist RS256 über die kanonische Darstellung der Nachricht mit dem privaten Schlüssel des TLS-Zertifikats des Knotens, demselben, der das Manifest signiert (`docs/es/FEDERATION_PROTOCOL.md`). Der Peer validiert sie gegen sein JWKS oder gegen das Manifestzertifikat, bevor er das Ereignis anwendet.

### Single-Node-Fallback

Er bleibt unverändert: `WebSocketChatBackend` ist weiterhin das standardmäßig registrierte Backend in der Entwicklung und mit `TESTING=true`. SQLite behält die Nachrichtentabelle als Quelle der Wahrheit; das Frontend nutzt weiter Hive (`OfflineCacheService`) und die FIFO-Warteschlange (`SyncQueueService`) für den Offline-Modus. Ist der Broker nicht verfügbar, reiht `send_message` das Ereignis mit derselben `message_id`/`event_id` in die Sync-Warteschlange ein und es wird bei Wiederverbindung wiedergegeben, ohne Duplikate. Das Edge-WebSocket liefert weiter an die authentifizierten Verbindungen, die derzeit `ConnectionManager` verwaltet.

### Bridge zwischen Knoten

Jeder Knoten startet seinen `nats-server` mit JetStream und deklariert einen Leaf Node (oder ein Gateway zwischen Clustern) zum Hub-Knoten. Der Leaf authentifiziert sich per mTLS mit der föderierten CA; das Zertifikat des Peers wird gegen `trusted_nodes.cert_fingerprint_sha256` validiert. Das Subject Mapping trennt Ereignisse nach `node_origin`, nach Kanal und nach Typ, sodass die bestehenden Richtlinien `disable_chat`, `minimize_data`, `import_only`, `consent_required` und `disable_search` im eingehenden Consumer vor der Persistenz angewendet werden. Der Widerruf eines Peers bleibt sofort wirksam: durch Setzen von `allowed = false` schlägt der nächste mTLS-Handshake des Leaf fehl und seine Ereignisse kommen nicht mehr an.

## Migrationsplan in 4 Schritten

1. **Vorbereiten**: `nats-py` zu `backend/requirements.txt` hinzufügen und die Variablen `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` zu `.env.example` hinzufügen. `NatsJetStreamChatBackend` hinter dem Flag `CHAT_BACKEND=nats` implementieren. Das Registry registriert weiterhin standardmäßig WebSocket: kein bestehender Test ändert sich.
2. **Schatten**: zusätzlich in NATS veröffentlichen, ohne dass jemand für die Zustellung konsumiert; ein Validierungsconsumer prüft Sequenz, Deduplizierung und Signatur zwischen zwei Knoten im Staging. Die echte Zustellung läuft weiter über WebSocket.
3. **Umstellung**: das NATS-Backend in Produktion registrieren und den WebSocket-Endpoint in eine Bridge umwandeln: sein JetStream-Consumer speist `ConnectionManager.broadcast()`. Gezielte Tests der Bridge mit dem Transport-Double und `TESTING=true` hinzufügen, ohne in der Suite einen echten Broker zu starten. Parallele Zustellung: WS bleibt während der Umstellung aktiv.
4. **Abschließen**: die In-Process-Übertragung für Nachrichten zwischen Knoten entfernen, mTLS-Leaf-Nodes zwischen zwei echten Knoten aktivieren und den Single-Node-Modus als dokumentierten Fallback belassen. Im selben Change die API (`python tools/gen_api.py --all`), die Zahlen und die README-Roadmap aktualisieren und dieses Dokument gemäß der `AGENTS.md`-Regel auf die acht Schwesterdokumente übertragen.

## Status

**Entscheidung getroffen am 2026-11-20: NATS JetStream als Broker für Chat und Ereignisse**, mit WebSocket als Edge und Single-Node-Fallback, MQTT 5 für den föderierten Kern verworfen.

Damit wird der Punkt «Broker bewerten (MQTT vs NATS JetStream) für Chat und Ereignisse» selbst freigegeben und, durch direkte Abhängigkeit, die Arbeiten an föderiertem Chat zwischen Knoten, Ereignisverbreitung zwischen Instanzen und mTLS-Brücke mit Nachrichtensignatur. Damit wird weder das Vertrauensmodell noch die bereits dokumentierten Föderations-Endpunkte freigegeben oder ersetzt: sie werden unverändert wiederverwendet.
