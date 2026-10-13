# Dokumentation — Clakettes

Die gesamte Dokumentation gibt es in den 9 Sprachen der Plattform. Spanisch ist kanonisch:
[ES](../es/README.md) · [EN](../en/README.md) · [FR](../fr/README.md) · [DE](README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

Dieser Index ist der Haupteinstieg in die Projektdokumentation. Er soll Nutzer, Administrator oder Entwickler zur richtigen Anleitung führen, ohne Dateien zufällig zu lesen.

## Wie man durch die Dokumentation navigiert

- **Ich will die App nutzen** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **Ich administriere ein Deployment** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Entwicklung** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](../es/API.md) + [DATABASE.md](DATABASE.md)
- **KI / Agent** → [ARQUITECTURA.md](ARQUITECTURA.md) und das Aufgabendokument; Pflichtbefehle und -konventionen stehen in [../AGENTS.md](../../AGENTS.md)

## Dokumentationsprinzipien

- **Ein einziges kanonisches Dokument pro Thema**: [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) und [API.md](../es/API.md) sind die offizielle Referenz ihres Bereichs.
- **Dokumentation pro Zielgruppe**: jede Anleitung ist für einen Lesertyp geschrieben, nicht für eine einzige Befehlsmenge.
- **Direkte Links**: von hier erreicht man relevante Inhalte in weniger als einem Klick.
- **Keine unnötige Duplizierung**: sekundäre Dokumente verlinken aufs Kanonische statt es zu wiederholen.

## Index pro Dokument

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](../es/API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Empfohlener Pfad pro Profil

### Endnutzer

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) solo si necesitan revisar permisos o entorno productivo

### Deployment-Administrator

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Entwickler

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](../es/API.md)
5. [DATABASE.md](DATABASE.md)

## Konventionen zur Pflege der Dokumentation

- Aktualisiere das kanonische Dokument vor jeder Zusammenfassung oder jedem Index.
- Wenn du einen Startablauf änderst, synchronisiere [README.de.md](../../README.de.md), [USO.md](USO.md) und [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Wenn du eine öffentliche API änderst, aktualisiere [API.md](../es/API.md) und ggf. [DESARROLLO.md](DESARROLLO.md).
- Wenn du Schema oder Persistenz änderst, prüfe [DATABASE.md](DATABASE.md) und die Migrationen.

## Kurzes FAQ

- **Wo fange ich an?** Lies [USO.md](USO.md) wenn du die App betreiben wirst; lies [ARQUITECTURA.md](ARQUITECTURA.md) wenn du entwickeln wirst.
- **Was ist kanonisch und was nicht?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](../es/API.md) und [DATABASE.md](DATABASE.md) sind die offizielle Referenz für diese Themen.
- **Wo finde ich einen Befehl oder ein Skript?** Siehe [HERRAMIENTAS.md](HERRAMIENTAS.md) und [../README.de.md](../../README.de.md).
- **Woran erkenne ich, ob eine Änderung Dokumentation braucht?** Wenn sie Start, Berechtigungen, Infrastruktur, API oder Datenmodell betrifft, muss sie sich in der einschlägigen Dokumentation widerspiegeln.

## Siehe auch

- [../README.de.md](../../README.de.md): Projektübersicht
- [USO.md](USO.md): Betrieb und lokale Konfiguration
- [ADMINISTRACION.md](ADMINISTRACION.md): Deployment- und Administrationsbereich
- [ARQUITECTURA.md](ARQUITECTURA.md): technische Systemkarte
- [API.md](../es/API.md): Endpunktreferenz

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

Die vollständige Befehls- und Profilreferenz des Projekts steht in [HERRAMIENTAS.md](HERRAMIENTAS.md) und in [../README.de.md](../../README.de.md).
