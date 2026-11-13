# Dokumentation — Clakettes

Dieser Index ist der Haupteinstieg in die Projektdokumentation. Er ist so aufgebaut, dass Nutzer, Administratoren und Entwickler die richtige Anleitung finden, ohne Dateien wahllos zu lesen.

## Sprachen

Die gesamte Dokumentation existiert in den 9 Sprachen der Plattform. Spanisch (kanarisch) ist kanonisch:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Navigation in der Dokumentation

- **Ich möchte die App nutzen** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Ich verwalte eine Bereitstellung** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Entwicklung** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md)
- **KI / Agent** → [ARQUITECTURA.md](ARQUITECTURA.md) und das Aufgaben-Dokument; die verpflichtenden Befehle und Konventionen stehen in [../AGENTS.md](../../AGENTS.md)

## Grundsätze der Dokumentation

- **Ein einziges kanonisches Dokument pro Thema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) und [API.md](API.md) sind die offizielle Referenz für ihren Bereich.
- **Zielgruppenbezogene Dokumentation**: jede Anleitung ist für einen Lesertyp geschrieben, nicht für einen einzelnen Befehlssatz.
- **Direkte Links**: von hier aus ist der relevante Inhalt in weniger als einem Klick erreichbar.
- **Keine unnötige Duplizierung**: sekundäre Dokumente verlinken auf das kanonische Dokument, anstatt es zu wiederholen.

## Dokumentenindex

| Dokument | Deckt ab | Zielgruppe |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Realer Wert nach Rolle und Flows (Festival, Anmeldung, Komitees, Auszeichnungen, Chat/E2EE, Juryabstimmung) | Nutzer, Admin, KI |
| [USO.md](USO.md) | Start, Variablen, Migration SQLite↔MariaDB, Backups, Rollen, Betrieb | Nutzer, Admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpunkte `/api/admin`, erstes Konto, Schlüsselrotation, Limits, Fehlerbehebung | Admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Docker-Profile, Ports, Volumes, Nginx, Health, CI (GitHub + GitLab) | Admin, Dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, `require_*`-Matrix, Perimeter, Produktions-Checkliste | Admin, Dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Systemkarte + Backend/Frontend-Regeln + zentrale Flows | Dev, KI |
| [API.md](API.md) | Endpunkt-Referenz (neu generierbar mit `tools/gen_api.py`) | Dev, KI |
| [DESARROLLO.md](DESARROLLO.md) | Konvention zum Hinzufügen von Endpoint/Bildschirm + CI-Tore | Dev, KI |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | `start.*`-Skripte, verteilbare Builds, Docker, CI-Fixes | Dev |
| [PUSH.md](PUSH.md) | Entscheidung zu Benachrichtigungen ohne Firebase | Dev |
| [DATABASE.md](DATABASE.md) | Duales SQLite/MariaDB-Schema, pro-Modell-Karten, ER | Dev, KI |
| [BACKEND.md](BACKEND.md) | Backend-Anleitung (Ebenen, Konfiguration, Auth, Tests) | Dev |
| [AUDITORIA.md](AUDITORIA.md) | Audit-Bericht (Rev. 10/10/2026) | Referenz |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Föderationsprotokoll zwischen Knoten (Phase 4) | Dev, KI |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (minimale federierte Entitäten) | Dev, KI |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Föderiertes Vertrauensmodell, mTLS, Zertifikatsrotation | Dev, KI |

## Empfohlener Pfad nach Profil

### Endanwender

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) nur falls Berechtigungen oder Produktionsumgebung geprüft werden müssen

### Bereitstellungsadministrator

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

## Konventionen zur Dokumentationspflege

- Aktualisiere das kanonische Dokument vor jeder Zusammenfassung oder jedem Index.
- Wenn du einen Startablauf änderst, synchronisiere [README.de.md](../../README.de.md), [USO.md](USO.md) und [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Wenn du eine öffentliche API änderst, aktualisiere [API.md](API.md) und, falls zutreffend, [DESARROLLO.md](DESARROLLO.md).
- Wenn du das Schema oder die Persistenz änderst, überprüfe [DATABASE.md](DATABASE.md) und die Migrationen.
- Wenn du ein Dokument in `docs/es/` bearbeitest, repliziere die Änderung an die 8 Schwestern (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## Kurze FAQ

- **Wo fange ich an?** Lies [USO.md](USO.md) wenn du die App betreibst; lies [ARQUITECTURA.md](ARQUITECTURA.md) wenn du entwickelst.
- **Was ist kanonisch und was nicht?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) und [DATABASE.md](DATABASE.md) sind die offizielle Referenz für diese Themen.
- **Wo finde ich einen Befehl oder ein Skript?** Prüfe [HERRAMIENTAS.md](HERRAMIENTAS.md) und [../README.md](../../README.de.md).
- **Wie weiß ich, ob eine Änderung Dokumentation benötigt?** Wenn sie Start, Berechtigungen, Infrastruktur, API oder Datenmodell betrifft, muss sie in der relevanten Dokumentation reflektiert werden.

## Siehe auch

- [../README.de.md](../../README.de.md): Projektübersicht
- [USO.md](USO.md): lokaler Betrieb und Konfiguration
- [ADMINISTRACION.md](ADMINISTRACION.md): Bereitstellungs- und Verwaltungsbereich
- [ARQUITECTURA.md](ARQUITECTURA.md): technische Systemkarte
- [API.md](API.md): Endpunkt-Referenz

## Empfohlener Start

Für den Start in einer lokalen Umgebung:

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

Oder mit den Projektskripten:

```bat
start.bat --dev
```

Die vollständige Befehls- und Profilreferenz steht in [HERRAMIENTAS.md](HERRAMIENTAS.md) und in [../README.md](../../README.de.md).