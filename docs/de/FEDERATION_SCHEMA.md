# Clakettes Schema v1

[ES](../es/FEDERATION_SCHEMA.md) · [EN](../en/FEDERATION_SCHEMA.md) · [FR](../fr/FEDERATION_SCHEMA.md) · [DE](FEDERATION_SCHEMA.md) · [IT](../it/FEDERATION_SCHEMA.md) · [CA](../ca/FEDERATION_SCHEMA.md) · [EU](../eu/FEDERATION_SCHEMA.md) · [GL](../gl/FEDERATION_SCHEMA.md) · [OC](../oc/FEDERATION_SCHEMA.md)

Initiale Version des Föderations-Schemas. Es definiert die minimalen zwischen Knoten austauschbaren Entitäten, versioniert über `schema_version` im Manifest jedes Knotens.

## Vertrauensmodell (Phase 2)

Die Identität eines Knotens ist das Tupel **(Domain, X.509-TLS-Zertifikat)**. Das Peering zwischen Knoten erfolgt über gegenseitiges mTLS: jeder Knoten validiert die Zertifikatskette des Peers gegen seine Root-CA, prüft, dass die Domain des Zertifikats mit der deklarierten übereinstimmt, und lehnt Self-Signed-Zertifikate in Produktion ab. Rotation und Widerruf werden über Zertifikatserneuerung verwaltet.

## Entitäten

- `festival`: id, name, edition, created_at, owner_node
- `user`: id, uuid, did, handle, username, node_origin
- `message`: id, sender, recipient, body, created_at, node_origin
- `moderation_report`: id, reporter_node, target_node, target_user_ref, reason, status
- `identity_redirect`: old_ref, new_ref, target_domain, created_at
- `migration_audit`: entity_type, entity_id, action, source_domain, target_domain, details, created_at
- `chat_outbox`: message_id (eindeutig), node_origin, subject, payload, signature, status, attempts, last_error, created_at
- `message_report`: reporter_id, message_id, reason, status
- `chat_mute`: user_id, channel_id, node_domain, until, reason

## Felder und Einschränkungen

- `uuid`: global stabile Kennung (UUID v4).
- `did`: optionale dezentralisierte Kennung.
- `handle`: `nutzer@instanz`, auflösbar über WebFinger.
- `schema_version`: vom Knoten im Manifest deklarierte Schema-Version (aktuell: `1`).

## Föderations-Endpunkte

### Identität und Verzeichnis

- `GET /api/federation/manifest` — Knoten-Manifest mit `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` und `certificate_chain`. RSA-SHA256-Signatur mit dem privaten Schlüssel des TLS-Zertifikats des Knotens; der Peer validiert das PEM der Kette und die Gültigkeit von `expires_at` (24 h).
- `GET /api/federation/directory` — Liste vertrauenswürdiger Knoten (`trusted_nodes`) mit `allowed = true`, einschließlich `cert_fingerprint_sha256` (PEM-Fingerprint), `capabilities`, `consent_required`, `minimize_data`.
- `GET/POST /api/federation/nodes` — Knotenrichtlinien (Allowlist/Blocklist): `consent_required`, `minimize_data`, `import_only`, `disable_chat`, `disable_search`. Nur Admin; die letzten drei werden persistiert und in der Bridge und im Ereignis-Bus angewendet.

### Föderierte Identität und Tokens (Phase 3)

- `GET /api/federation/.well-known/jwks.json` — RSA-Öffentlicher Schlüssel des Knotens im JWKS-Format zur Validierung von Peer-Föderations-Tokens.
- `POST /api/federation/token` — stellt ein signiertes Föderations-JWT aus (RS256). Erfordert über mTLS verifizierte Knotenidentität.
- `POST /api/federation/peers/verify` — validiert die Identität eines entfernten Knotens (Domain + CN und Zertifikats-PEM + signiertes Manifest).
- `POST /api/federation/peers/{domain}/revoke` — widerruft einen vertrauenswürdigen Knoten (Admin).
- `GET /api/federation/whoami` — Peer-Identität (`iss`, `sub`, Knoten) nur, wenn sein Bearer-JWT gegen sein JWKS validiert; sonst 401.

### Nutzer, Meldungen und Entdeckung

- `GET /api/federation/users/{ref}` — löst Nutzer nach `uuid`, `did` oder `handle` auf. Erfordert verifiziertes Peer-mTLS.
- `GET /api/federation/.well-known/webfinger` — löst `acct:user@domain` auf. Erfordert verifiziertes Peer-mTLS.
- `POST/GET/PATCH /api/federation/reports` — Moderationsmeldung zwischen Knoten.

### Portabilität (Phase 7)

- `POST /api/federation/portability/bundles` — erzeugt ein Nutzer-Bundle mit `bundle_version`, `origin_domain`, `payload`, `signature` (HMAC-SHA256 mit `SECRET_KEY`) und `checksum` (SHA-256 des kanonischen Payloads).
- `POST /api/federation/portability/imports` — validiert Signatur und Checksum, prüft die Ursprungsrichtlinie (403, wenn nicht erlaubt), wendet `minimize_data` an und protokolliert das Importierte (Nutzer, Kurzfilme, Festivals, Nachrichten). Die Bundles enthalten `contest_type` bei jedem Kurzfilm: `MediaUrl` wird validiert/saniert (ungültige URL → `null`), `contest_type` wird bei ungültigem Wert auf `official_section` normalisiert und der Festival-Checksum schließt es ein.
- `POST /api/federation/portability/festivals/{festival_id}/migrate` — überträgt Festival-Eigentum und seine Kurzfilme auf `new_owner_id` von `target_domain` mit Checksum-Prüfung; nur Admin.
- `POST /api/federation/portability/users/{user_ref}/migrate` — schreibt `handle` und `did` auf die Ziel-Domain um und erstellt den Redirect; nur Admin.
- `GET /api/federation/portability/redirects/{old_ref}` — löst die alte Ref auf (`old_ref`, `new_ref`, `target_domain`, `created_at`).

### Föderierter Chat, Moderation und Ereignisse (Phasen 8 und 9)

- `POST /api/federation/chat/bridge/inbound` — akzeptiert ein signiertes Envelope (`message_id`, `node_origin`, `content`, `timestamp`, `signature`), verifiziert die RS256-Signatur gegen den öffentlichen Schlüssel des Peers, verwirft Duplikate nach `message_id`, speichert die Nachricht und verteilt sie; `403`, wenn der Knoten nicht erlaubt oder die Signatur ungültig ist.
- `POST /api/federation/chat/bridge/outbound` — signiert das Envelope, reiht es in `chat_outbox` mit dem Subjekt `clakettes.chat.node.{target_node}` ein und veröffentlicht es über den konfigurierten Transport (`DurableQueueBackend`); `config` liefert Transport, Stream, Algorithmus und Subject-Mapping.
- `GET /api/federation/chat/messages` — föderierter Verlauf, dedupliziert nach `message_id` und sortiert nach `timestamp` + `message_id` (optionaler `node`-Filter).
- `POST /api/chat/moderation/messages/{message_id}/report`, `PATCH /moderate`, `GET /reports`, `POST/GET /mutes`, `GET /limits` — Meldungen, Verbergen/Löschen, Mutes nach Nutzer/Kanal/Knoten, Blockiertwörter-Filter, `disable_chat` pro Knoten und Rate-Limit von 10 Nachrichten/60 s pro Knoten und Nutzer (deaktiviert mit `TESTING=true`).
- `GET /api/federation/events/stream` — SSE mit obligatorischem `token` in der Query (`since` und `limit` optional), Replay der letzten 200 Ereignisse und Herzschlag `: ping` alle 15 s.
- `POST /api/federation/events/publish` — veröffentlicht auf einem aus `node`/`entity` abgeleiteten Topic (oder explizitem `topic`), signiert die Zustellung an Peers mit HMAC (`X-Clakettes-Signature`) und überspringt Knoten mit `disable_chat`/`disable_search`; nur Admin.
- `GET /api/federation/events/retry-queue` — ausstehende Wiederholungen; 3 Versuche mit Backoff 300 ms → 1,5 s → 5 s.

### Resilienz (Phase 10)

- `GET /api/federation/resilience/health` — Knotenstatus, Datenbank, Anzahl der Knoten und Latenz.
- `GET /api/federation/resilience/heartbeat` — aktualisiert `last_seen_at` des Peers und protokolliert die Latenz in den Metriken.
- `GET /api/federation/resilience/metrics` — Anfragen, Erfolge, Fehler, Wiederholungen sowie globale und pro Knoten p50/p95-Latenzen.
- `POST /api/federation/resilience/keys/revoke`, `GET /keys/revoked` — sofortiger Schlüssel-Widerruf pro Domain mit Grund und Liste der Widerrufe; nur Admin zum Widerruf.
- `GET /api/federation/resilience/incident-plan` — Wiederherstellungsplan bei Knoten-Kompromittierung (8 Schritte).

### Health und Hilfsfunktionen

- `GET /api/federation/health`, `/ping`, `/status`, `/info`, `/version`, `/capabilities`, `/keys`, `/events`, `/peers`, `/links`, `/stats`, `/config`, `/heartbeat`, `/aggregate-nodes`, `/ok`, `/yes`, `/no`, `/maybe`, `/always`, `/never` — Platzhalter mit statischen Antworten, die nicht den tatsächlichen Zustand widerspiegeln; keine operationellen Probe- oder Diagnose-Endpunkte.

> **Hinweis:** sie liefern feste Antworten und können ein falsches Sicherheitsgefühl vermitteln; für echte Diagnosen nutzen Sie die oben beschriebenen Resilienz-Endpunkte.

## Anpassbarkeit

- Das Schema ist versioniert; Knoten deklarieren `schema_version` im Manifest.
- Optionale Felder (`did`, `handle`) können ausgelassen werden, wenn der Knoten sie nicht unterstützt.
- Datenminimierung (`minimize_data`) erlaubt das Auslassen sensibler Felder im Peering.
