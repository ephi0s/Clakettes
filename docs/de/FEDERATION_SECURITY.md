# Föderierte Sicherheit (Phasen 2 bis 10)

## Vertrauensmodell

- Knotenidentität = Domain + X.509-TLS-Zertifikat.
- Gegenseitiges Peering über mTLS mit Domain-Zertifikaten (öffentliche oder private CA): Subject-CN und Zertifikats-PEM werden validiert, nicht nur die deklarierte Domain.
- TLS zwischen Knoten zwingend; strikte Zertifikatsvalidierung im Peering (keine Self-Signed-Zertifikate in Prod).
- Die Identität wird in `trusted_nodes` gespeichert (Domain, SHA-256-Fingerprint des PEM, Subject-CN, ausstellende CA, Gültigkeit, Richtlinien).
- Jeder Knoten stellt ein in RSA-SHA256 mit dem privaten Schlüssel seines TLS-Zertifikats signiertes Manifest bereit; Peers validieren die Signatur gegen das PEM von `certificate_chain` und prüfen `expires_at` (24 h).

## Rotation und Widerruf

- Rotation wird über Zertifikatserneuerung verwaltet: bei der Erneuerung wird der Fingerprint in `trusted_nodes` aktualisiert, ohne das Peering zu brechen (die Vertrauenswurzel ist die CA, nicht das individuelle Zertifikat).
- Ein kompromittierter Knoten wird widerrufen, indem `allowed = false` in `trusted_nodes` gesetzt wird (`POST /api/federation/peers/{domain}/revoke`, nur Admin) oder sein Zertifikat in der CRL der CA ungültig gemacht wird.
- Der administrative Widerruf ist sofort: der nächste mTLS-Handshake schlägt fehl.
- Der Notfall-Widerruf wird auch über `POST /api/federation/resilience/keys/revoke` verwaltet (nur Admin, mit Grund) und unter `GET /keys/revoked` abgefragt; `GET /incident-plan` beschreibt die 8 Reaktionsschritte bei einer Kompromittierung.

## Zugriffskontrollen

- Globales Rate-Limiting: 100 req/60s pro IP (Bucket `middleware:`); `/dav` hat 600/60s.
- Rate-Limiting pro sensiblem Endpunkt: Login 5/300s pro IP, Refresh 20/60s pro IP, Federation 60/60s pro IP; Chat 10 Nachrichten/60 s pro Knoten und Nutzer (deaktiviert mit `TESTING=true`).
- Föderations-Endpunkte, die Nutzerdaten exponieren (`/users/{ref}`, `/.well-known/webfinger`), erfordern verifiziertes Peer-mTLS.
- `GET /api/federation/whoami` erfordert einen Föderations-Bearer-JWT (RS256), validiert gegen das JWKS des Ausstellers; ohne gültigen Token antwortet es 401.
- Knoten-Administrations-Endpunkte (`/nodes`, `/peers/{domain}/revoke`, Portabilitäts-Migrationen, `events/publish`, `events/retry-queue`, `keys/revoke`) erfordern die Admin-Rolle; Kanal-Moderation erfordert Admin oder Kanal-Moderator.
- Der SSE-Ereignis-Stream erfordert einen gültigen Zugriffstoken in `?token=`; das Ereignis wird mit `since` abgefragt und das Replay auf die letzten 200 Ereignisse begrenzt.

## Integrität, Chat und Ereignisse

- Portabilitäts-Bundles tragen eine HMAC-SHA256-`signature` mit `SECRET_KEY` und eine SHA-256-`checksum` über dem kanonischen Payload; der Import lehnt ungültige Bundles (400) und nicht erlaubte Ursprünge (403) ab und wendet `minimize_data` an, um sensible Felder auszulassen.
- Die Chat-Bridge signiert in RS256 die kanonischen Felder des Envelopes (`message_id`, `node_origin`, `content`, `timestamp`, …); der Empfänger lädt den öffentlichen Schlüssel des Peers herab und verifiziert die Signatur vor dem Speichern. Die Tabelle `chat_outbox` erzwingt Eindeutigkeit nach `message_id`, sodass ein erneuter Versand als `duplicate` beantwortet wird; der Verlauf wird nach `timestamp` + `message_id` sortiert.
- Der Transport ist über die Durable Queue (`DurableQueueBackend` über `chat_outbox`) austauschbar, mit Wiederholung und Backoff; die Broker-Entscheidung (NATS JetStream, Edge-WebSocket und Single-Node-Fallback) steht in `docs/es/FEDERATION_CHAT_BROKER.md`.
- Die Moderation umfasst Meldungen, Verbergen/Löschen von Nachrichten, Mutes mit Gültigkeit und Reichweite pro Kanal oder Knoten, Blockiertwörter-Filter und `disable_chat` pro Knoten (`POST /api/chat/moderation/*`). Ergänzt wird sie durch das Limit von 10 Nachrichten/60 s pro Knoten und Nutzer.
- Ereignisse an Peers werden mit HMAC-SHA256 im Header `X-Clakettes-Signature` signiert und nur an erlaubte Knoten verbreitet; Fehler landen in der Wiederholungsqueue (3 Versuche, Backoff 300 ms → 1,5 s → 5 s), sichtbar unter `/api/federation/events/retry-queue`.
- Die Richtlinien `disable_chat` und `disable_search` werden vor dem Anwenden eingehender Ereignisse oder Nachrichten ausgewertet, und `import_only` schränkt den Export ein; `GET /api/federation/resilience/metrics` zeigt p50/p95, Latenz, Fehler und Wiederholungen zur Überwachung des Peerings.

## Anpassungen

- `allowlist`/`blocklist` pro Knoten (`node_policies` / `trusted_nodes`).
- Rate-Limiting und Anti-Flood am Föderations-Edge.
- Verbreitung von Moderationsmeldungen zwischen Knoten.
- `consent_required`: erfordert ausdrückliche Zustimmung, bevor Daten eines Knotens föderiert werden.
- `import_only`: einseitige Föderation (nur Import, kein Export).
- `disable_chat`/`disable_search`: Berechtigungen pro Funktion pro Knoten.
- `minimize_data`: im Peering nicht mehr als nötig teilen.

## Referenzen

- `docs/es/MODELO_CONFIANZA_NODOS.md` — detailliertes Design des Vertrauensmodells und der Datenbanktabellen.
- `docs/es/FEDERATION_PROTOCOL.md` — Interoperabilitätsschritte Knoten-Server/Client (Phasen 2 bis 10).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, Entitäten und Föderations-Endpunkte.
- `docs/es/FEDERATION_CHAT_BROKER.md` — Broker-Entscheidung für Chat und Ereignisse zwischen Knoten.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — Bedrohungen pro Knoten und Restrisiken.
