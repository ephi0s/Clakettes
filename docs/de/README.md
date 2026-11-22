# Dokumentation — Clakettes

Dieser Index ist der Haupteinstieg in die Projektdokumentation. Er ist so aufgebaut, dass Nutzer, Administratoren und Entwickler die richtige Anleitung finden, ohne Dateien wahllos zu lesen.

## Sprachen

Die 18 gemeinsamen Dokumente existieren in den 9 Sprachen der Plattform; in `docs/es/` gibt es zusätzlich zwei spezifische Analysen (`AMENAZAS_NODOS_FEDERACION.md` und `MODELO_CONFIANZA_NODOS.md`). Spanisch (kanarisch) ist kanonisch:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Navigation in der Dokumentation

- **Ich möchte die App nutzen** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Ich verwalte ein Deployment** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Entwicklung** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md) + [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
- **Referenz für Agents** → Die Befehle und Entwicklungskonventionen stehen in [../AGENTS.md](../../AGENTS.md)

## Prinzipien der Dokumentation

- **Ein kanonisches Dokument pro Thema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) und [API.md](API.md) sind die offizielle Referenz für ihren Bereich.
- **Dokumentation nach Zielgruppe**: jede Anleitung ist für einen Lesertyp geschrieben, nicht für einen einzigen Befehlssatz.
- **Direkte Links**: von hier aus sind die relevanten Inhalte weniger als einen Klick entfernt.
- **Keine unnötige Duplizierung**: sekundäre Dokumente verlinken auf das kanonische, statt es zu wiederholen.

## Dokumentenindex

| Dokument | Was es abdeckt | Zielgruppe |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Reeller Nutzen pro Rolle und Abläufe (Festival, Anmeldung, Komitees, Preise, Chat/E2EE, Jury-Abstimmung) | Nutzer, Admin |
| [USO.md](USO.md) | Start, Variablen, SQLite↔MariaDB-Migration, Backups, Rollen und Betrieb | Nutzer, Admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | `/api/admin`-Endpoints, Startkonto, Secret-Rotation, Limits, Fehlerbehebung | Admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Docker-Profile, Ports, Volumes, Nginx, Health, CI (GitHub + GitLab) | Admin, Dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, `require_*`-Matrix, Perimeter, Produktions-Checkliste | Admin, Dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Systemkarte + Backend/Frontend-Regeln + Schlüsselabläufe | Dev |
| [API.md](API.md) | Endpoint-Referenz | Dev |
| [DESARROLLO.md](DESARROLLO.md) | Konvention zum Hinzufügen von Endpoint/Bildschirm + CI-Gates | Dev |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | `start.*`-Skripte, verteilbare Builds, Docker, CI-Fixes | Dev |
| [PUSH.md](PUSH.md) | Benachrichtigungsentscheidung ohne Firebase | Dev |
| [DATABASE.md](DATABASE.md) | Duales SQLite/MariaDB-Schema, Modellkarten, ER | Dev |
| [BACKEND.md](BACKEND.md) | Backend-Anleitung (Schichten, Konfig, Auth, Tests) | Dev |
| [AUDITORIA.md](AUDITORIA.md) | Auditbericht (Rev. 10/10/2026) | Referenz |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Föderationsprotokoll zwischen Knoten (Phasen 2 bis 10) | Dev |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (minimale föderierte Entitäten) | Dev |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Föderiertes Vertrauensmodell, mTLS, signiertes Manifest, Portabilität, Chat und Resilienz | Dev |
| [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) | Broker-Entscheidung (NATS JetStream) für Chat und Ereignisse zwischen Knoten; heute implementierter Transport: `DurableQueueBackend` über `chat_outbox` mit Edge-WebSocket | Dev |
| [AMENAZAS_NODOS_FEDERACION.md](../es/AMENAZAS_NODOS_FEDERACION.md) | Bedrohungsmodell föderierter Knoten (nur auf Spanisch) | Dev |
| [MODELO_CONFIANZA_NODOS.md](../es/MODELO_CONFIANZA_NODOS.md) | Vertrauensmodell zwischen Knoten (nur auf Spanisch) | Dev |

## Empfohlener Pfad nach Profil

### Endnutzer

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) nur wenn Berechtigungen oder die Produktionsumgebung geprüft werden sollen

### Deployment-Administrator

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Entwickler

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)
6. [BACKEND.md](BACKEND.md)
7. [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
8. [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md)
9. [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md)

## Konventionen zur Pflege der Dokumentation

- Aktualisiere das kanonische Dokument vor jeder Zusammenfassung oder jedem Index.
- Wenn du einen Startablauf änderst, synchronisiere [README.md](../../README.md), [USO.md](USO.md) und [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Wenn du eine öffentliche API änderst, aktualisiere [API.md](API.md) und gegebenenfalls [DESARROLLO.md](DESARROLLO.md).
- Wenn du das Schema oder die Persistenz änderst, prüfe [DATABASE.md](DATABASE.md) und die Migrationen.
- Immer wenn du ein Dokument in `docs/es/` bearbeitest, übertrage die Änderung auf die 8 Schwestern (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## Schnell-FAQ

- **Wo fange ich an?** Lies [USO.md](USO.md), wenn du die App betreiben willst; lies [ARQUITECTURA.md](ARQUITECTURA.md), wenn du entwickeln willst.
- **Was ist kanonisch und was nicht?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) und [DATABASE.md](DATABASE.md) sind die offizielle Referenz für diese Themen.
- **Wo finde ich einen Befehl oder ein Skript?** Siehe [HERRAMIENTAS.md](HERRAMIENTAS.md) und [../README.md](../../README.md).
- **Wann benötigt eine Änderung Dokumentation?** Wenn sie Start, Berechtigungen, Infrastruktur, API oder Datenmodell betrifft, muss sie in der einschlägigen Dokumentation erscheinen.

## Siehe auch

- [../README.md](../../README.md): Projektübersicht
- [USO.md](USO.md): lokaler Betrieb und Konfiguration
- [ADMINISTRACION.md](ADMINISTRACION.md): Deployment- und Administrationsbereich
- [ARQUITECTURA.md](ARQUITECTURA.md): technische Systemkarte
- [API.md](API.md): Endpoint-Referenz
