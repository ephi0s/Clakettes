# Dokumentation — Clakettes

Die gesamte Dokumentation gibt es in den 9 Sprachen der Plattform. Spanisch ist kanonisch:
[Español](README.md) · [English](README.en.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Català](README.ca.md) · [Euskara](README.eu.md) · [Galego](README.gl.md) · [Occitan](README.oc.md).

Dieser Index ist der Haupteinstieg in die Projektdokumentation. Er soll Nutzer, Administrator oder Entwickler zur richtigen Anleitung führen, ohne Dateien zufällig zu lesen.

## Wie man durch die Dokumentation navigiert

- **Ich will die App nutzen** → [USO.de.md](USO.de.md) + [FUNCIONAL.de.md](FUNCIONAL.de.md)
- **Ich administriere ein Deployment** → [ADMINISTRACION.de.md](ADMINISTRACION.de.md) + [INFRAESTRUCTURA.de.md](INFRAESTRUCTURA.de.md) + [SEGURIDAD.de.md](SEGURIDAD.de.md)
- **Entwicklung** → [ARQUITECTURA.de.md](ARQUITECTURA.de.md) + [DESARROLLO.de.md](DESARROLLO.de.md) + [API.md](API.md) + [DATABASE.de.md](DATABASE.de.md)
- **KI / Agent** → [ARQUITECTURA.de.md](ARQUITECTURA.de.md) und das Aufgabendokument; Pflichtbefehle und -konventionen stehen in [../AGENTS.md](../AGENTS.md)

## Dokumentationsprinzipien

- **Ein einziges kanonisches Dokument pro Thema**: [SEGURIDAD.de.md](SEGURIDAD.de.md), [USO.de.md](USO.de.md), [DATABASE.de.md](DATABASE.de.md) und [API.md](API.md) sind die offizielle Referenz ihres Bereichs.
- **Dokumentation pro Zielgruppe**: jede Anleitung ist für einen Lesertyp geschrieben, nicht für eine einzige Befehlsmenge.
- **Direkte Links**: von hier erreicht man relevante Inhalte in weniger als einem Klick.
- **Keine unnötige Duplizierung**: sekundäre Dokumente verlinken aufs Kanonische statt es zu wiederholen.

## Index pro Dokument

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.de.md](FUNCIONAL.de.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.de.md](USO.de.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.de.md](ADMINISTRACION.de.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.de.md](INFRAESTRUCTURA.de.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.de.md](SEGURIDAD.de.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.de.md](ARQUITECTURA.de.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.de.md](DESARROLLO.de.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.de.md](HERRAMIENTAS.de.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.de.md](PUSH.de.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.de.md](DATABASE.de.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.de.md](BACKEND.de.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.de.md](AUDITORIA.de.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Empfohlener Pfad pro Profil

### Endnutzer

1. [USO.de.md](USO.de.md)
2. [FUNCIONAL.de.md](FUNCIONAL.de.md)
3. [SEGURIDAD.de.md](SEGURIDAD.de.md) solo si necesitan revisar permisos o entorno productivo

### Deployment-Administrator

1. [ADMINISTRACION.de.md](ADMINISTRACION.de.md)
2. [INFRAESTRUCTURA.de.md](INFRAESTRUCTURA.de.md)
3. [SEGURIDAD.de.md](SEGURIDAD.de.md)
4. [USO.de.md](USO.de.md)

### Entwickler

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.de.md](ARQUITECTURA.de.md)
3. [DESARROLLO.de.md](DESARROLLO.de.md)
4. [API.md](API.md)
5. [DATABASE.de.md](DATABASE.de.md)

## Konventionen zur Pflege der Dokumentation

- Aktualisiere das kanonische Dokument vor jeder Zusammenfassung oder jedem Index.
- Wenn du einen Startablauf änderst, synchronisiere [README.de.md](../README.de.md), [USO.de.md](USO.de.md) und [HERRAMIENTAS.de.md](HERRAMIENTAS.de.md).
- Wenn du eine öffentliche API änderst, aktualisiere [API.md](API.md) und ggf. [DESARROLLO.de.md](DESARROLLO.de.md).
- Wenn du Schema oder Persistenz änderst, prüfe [DATABASE.de.md](DATABASE.de.md) und die Migrationen.

## Kurzes FAQ

- **Wo fange ich an?** Lies [USO.de.md](USO.de.md) wenn du die App betreiben wirst; lies [ARQUITECTURA.de.md](ARQUITECTURA.de.md) wenn du entwickeln wirst.
- **Was ist kanonisch und was nicht?** [USO.de.md](USO.de.md), [SEGURIDAD.de.md](SEGURIDAD.de.md), [API.md](API.md) und [DATABASE.de.md](DATABASE.de.md) sind die offizielle Referenz für diese Themen.
- **Wo finde ich einen Befehl oder ein Skript?** Siehe [HERRAMIENTAS.de.md](HERRAMIENTAS.de.md) und [../README.de.md](../README.de.md).
- **Woran erkenne ich, ob eine Änderung Dokumentation braucht?** Wenn sie Start, Berechtigungen, Infrastruktur, API oder Datenmodell betrifft, muss sie sich in der einschlägigen Dokumentation widerspiegeln.

## Siehe auch

- [../README.de.md](../README.de.md): Projektübersicht
- [USO.de.md](USO.de.md): Betrieb und lokale Konfiguration
- [ADMINISTRACION.de.md](ADMINISTRACION.de.md): Deployment- und Administrationsbereich
- [ARQUITECTURA.de.md](ARQUITECTURA.de.md): technische Systemkarte
- [API.md](API.md): Endpunktreferenz

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

Die vollständige Befehls- und Profilreferenz des Projekts steht in [HERRAMIENTAS.de.md](HERRAMIENTAS.de.md) und in [../README.de.md](../README.de.md).
