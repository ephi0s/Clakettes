# Clakettes-Föderationsprotokoll (Phasen 2 bis 10)

Schritte zum Erstellen eines interoperablen Servers/Clients:

1. Implementiere die Endpunkte `/api/federation/*` (siehe `docs/es/FEDERATION_SCHEMA.md`).
2. Konfiguriere zwingendes TLS zwischen Knoten mit gegenseitigem mTLS (Phase 2): Zertifikat ausgestellt von einer vertrauenswürdigen CA, keine Self-Signed-Zertifikate in Produktion.
3. Registriere den Knoten als vertrauenswürdig bei jedem Peer, mit dem gepeert wird (`trusted_nodes`: Domain, SHA-256-Fingerprint des Zertifikats-PEM, Subject-CN, Fähigkeiten, Richtlinien). `POST /api/federation/nodes` speichert `import_only`, `disable_chat` und `disable_search` zusammen mit `consent_required` und `minimize_data`.
4. Stelle das Manifest unter `GET /api/federation/manifest` bereit mit `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`, `signature` und `certificate_chain`. Das Manifest wird in RSA-SHA256 (PKCS#1 v1.5) mit dem privaten Schlüssel des TLS-Zertifikats des Knotens signiert; der Peer validiert die Signatur mit dem PEM von `certificate_chain` und prüft `expires_at` (24 h).
5. Stelle den öffentlichen Schlüssel unter `GET /api/federation/.well-known/jwks.json` bereit, damit Peers Föderations-Tokens validieren können.
6. Validiere Peer-Tokens über JWKS: ein entfernter Knoten, der einen geschützten Endpunkt aufruft, muss einen signierten Bearer-JWT (RS256) vorlegen, dessen `iss` seine Domain ist und dessen Signatur gegen sein JWKS validiert. `GET /api/federation/whoami` gibt die Identität des Peers nur zurück, wenn dieser JWT validiert (sonst 401).
7. Löse entfernte Nutzer über `GET /api/federation/users/{ref}` und `GET /api/federation/.well-known/webfinger` auf (beide erfordern verifiziertes Peer-mTLS).
8. Verwende Clakettes Schema v1 für den Datenaustausch.
9. Portiere Identität und Daten mit `POST /api/federation/portability/bundles` und `/imports`, migriere mit `/festivals/{id}/migrate` und `/users/{ref}/migrate` und löse alte Refs mit `GET /redirects/{ref}` auf.
10. Liefere Chat über die signierte Bridge `/api/federation/chat/bridge/{inbound,outbound,config}`; der Verlauf wird unter `/api/federation/chat/messages` abgefragt, mit Deduplizierung nach `message_id` und Sortierung nach `timestamp` + `message_id`. Die Durable Queue `chat_outbox` erlaubt einen austauschbaren Transport (Details in `docs/es/FEDERATION_CHAT_BROKER.md`).
11. Verbreite Änderungen über den Ereignis-Bus: `GET /api/federation/events/stream` (SSE mit `since` und Herzschlag), `POST /publish` und `GET /retry-queue` (3 Versuche, Backoff 300 ms → 5 s).
12. Überwache die Peering-Gesundheit mit `/api/federation/resilience/{health,heartbeat,metrics,keys/revoke,keys/revoked,incident-plan}`; `metrics` zeigt p50/p95, Latenz, Fehler und Wiederholungen.
13. Prüfe die Konformität eines Drittknotens mit `python tools/federation_conformance.py <url> [--json]` (1 bei kritischen/hohen Fehlern).

## Motivation

Das Protokoll erlaubt es unabhängigen Knoten, Festivals, Nutzer und Nachrichten auszutauschen, ohne Identität oder Nachvollziehbarkeit zu verlieren.

## Anpassungen

- `consent_required`: erfordert ausdrückliche Zustimmung, bevor Daten eines Knotens föderiert werden.
- `import_only`: einseitige Föderation (nur Import, kein Export).
- `disable_chat`/`disable_search`: Berechtigungen pro Funktion pro Knoten.
- `minimize_data`: im Peering nicht mehr als nötig teilen.

## Wichtige Endpunkte

| Endpoint | Methode | Beschreibung |
|---|---|---|
| `/api/federation/manifest` | GET | RSA-SHA256-signiertes Manifest mit `expires_at` und `certificate_chain` |
| `/api/federation/directory` | GET | Verzeichnis vertrauenswürdiger Knoten |
| `/api/federation/nodes` | GET/POST | Allowlist/Blocklist-Richtlinien (`import_only`, `disable_chat`, `disable_search`) |
| `/api/federation/whoami` | GET | Peer-Identität, Validierung seines JWT gegen sein JWKS |
| `/api/federation/.well-known/jwks.json` | GET | JWKS-Öffentlicher Schlüssel des Knotens |
| `/api/federation/token` | POST | Ausstellung eines Föderations-JWT (RS256) |
| `/api/federation/peers/verify` | POST | Verifizierung der Identität eines entfernten Knotens (CN und Zertifikats-PEM) |
| `/api/federation/peers/{domain}/revoke` | POST | Widerruf eines vertrauenswürdigen Knotens (Admin) |
| `/api/federation/users/{ref}` | GET | Auflösung entfernter Nutzer (mTLS) |
| `/api/federation/.well-known/webfinger` | GET | WebFinger `acct:user@domain` (mTLS) |
| `/api/federation/reports` | POST/GET/PATCH | Moderationsmeldungen zwischen Knoten |
| `/api/federation/portability/bundles`, `/imports` | POST | Export und Import signierter Bundles |
| `/api/federation/portability/festivals/{id}/migrate`, `/users/{ref}/migrate` | POST | Migration von Festivals und Nutzeridentität (Admin) |
| `/api/federation/portability/redirects/{ref}` | GET | Auflösung der alten Ref nach Migration |
| `/api/federation/chat/bridge/inbound`, `/outbound`, `/config` | POST/GET | Signierte Chat-Bridge und ihre Konfiguration |
| `/api/federation/chat/messages` | GET | Föderierter Verlauf, dedupliziert und sortiert |
| `/api/chat/moderation/*` | POST/PATCH/GET | Meldungen, Mutes, Wortfilter und Chat-Limit |
| `/api/federation/events/stream`, `/publish`, `/retry-queue` | GET/POST | SSE mit `since` und Herzschlag, Publishing und Wiederholungen |
| `/api/federation/resilience/health`, `/heartbeat`, `/metrics` | GET | Health, Heartbeat und echte p50/p95-Metriken |
| `/api/federation/resilience/keys/revoke`, `/keys/revoked`, `/incident-plan` | POST/GET | Schlüssel-Widerruf und Incident-Plan |
