# Clakettes

Die Plattform, auf der Filmfestivals das ganze Jahr leben: Ausschreibungen, Kurzfilme, Teams, Spielstätten und Publikum an einem Ort.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Läuft auf Web, Android, iOS und Desktop (Windows, macOS, Linux), in allen Sprachen der Plattform und auch offline.

---

## Für wen ist es?

- **Festivals**: publiziere dein Festival, öffne Ausschreibungen, empfange Kurzfilme, organisiere Komitees und Jurys, verwalte Spielstätten und kommuniziere dein Palmarès.
- **Filmprofis**: erstelle dein Profil (Regie, Schauspiel, Ton, Drehbuch, Schnitt, Kostüm und mehr), zeige dein Palmarès und vernetze dich mit Festivals und Teams.
- **Express-Teams**: koordiniere deine Drehgruppe, geolokalisiere Teilnehmende und reiche deinen Kurzfilm bei Express-Wettbewerben ein.
- **Publikum**: entdecke Festivals, folge Kurzfilmen und kontaktiere die Community.

## Was du tun kannst

- **Festivals und Ausschreibungen**: jedes Festival kann mehrere offene Ausschreibungen mit eigenen Regeln und Anmeldeformularen haben.
- **Kurzfilme**: lade Kurzfilme hoch, verknüpfe sie mit Ausschreibungen und Drehorten.
- **Profile mit Palmarès**: Palmarès verknüpft mit Plattform-Festivals oder extern via Links, mit feldweiser Privatsphärenkontrolle.
- **Chat**: Direkt- und Gruppen-/Kanal-Nachrichten pro Festival, mit Ende-zu-Ende-Verschlüsselung.
- **Karten**: Spielstätten und Drehorte auf interaktiven Karten, mit Öffnen in deiner Lieblings-Kartenapp.
- **Offline**: die App läuft weiter offline, speichert die Herkunft jedes Knotens im Cache und synchronisiert deine Änderungen bei Wiederverbindung.
- **Föderation**: vertrauenswürdige Knoten mit mTLS, Portabilität von Identitäten, Chat und Ereignisse zwischen Knoten, Moderation, Metriken und Resilienz.
- **In deiner Sprache**: Spanisch, Englisch, Französisch, Deutsch, Italienisch, Katalanisch, Baskisch, Galicisch und Okzitanisch, mit automatischer Erkennung des System-Locale.

## Anforderungen und Start

### Mindestanforderungen

- Python 3.12+
- Flutter SDK >= 3.0.0 und < 4.0.0
- Git
- Docker und Docker Compose für Deployment/Produktionsumgebung
- Browser mit Web-Unterstützung (Chrome/Brave empfohlen)

### Schnellstart

En PowerShell:

```powershell
./start.ps1 --dev
```

En Linux/macOS:

```bash
./start.sh --dev
```

Dies startet das Backend auf `http://localhost:8000` und die App im lokalen Modus; die API exponiert Swagger/OpenAPI unter `/docs`. Du kannst jede Seite mit `--no-backend` oder `--no-frontend` deaktivieren.

## Umgebungsvariablen und Konfiguration

### Backend

Erstelle oder passe `backend/.env` mit mindestens an:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
APP_ENV=development
PUBLIC_BASE_URL=https://tu-dominio.com
# Föderation mit mTLS (Produktion)
MTLS_REQUIRED=false
MTLS_CA_BUNDLE_PATH=
MTLS_CLIENT_CERT_PATH=
MTLS_CLIENT_KEY_PATH=
# Zahlungen (Standard: Mock; Stripe/Redsys auf Anfrage)
PAYMENTS_PROVIDER=mock
```

Für die Produktionsumgebung wird MariaDB genutzt; Skripte und Deployment-Doku verwalten es mit Docker.

### Frontend

Die App nutzt das Backend per URL wieder, normal mit `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

Der automatische Projektstart konfiguriert dies bereits, wenn `start.*` genutzt wird.

## Projektdokumentation

Die Dok-Landkarte liegt in [docs/de/README.md](docs/de/README.md). Sie ist der beste Einstieg für jeden Nutzertyp:

- [docs/de/USO.md](docs/de/USO.md): Start, Betrieb, Umgebung und tägliche Nutzung
- [docs/de/ADMINISTRACION.md](docs/de/ADMINISTRACION.md): Administration, Konten und Bereitstellung
- [docs/de/INFRAESTRUCTURA.md](docs/de/INFRAESTRUCTURA.md): Docker, Ports, CI und Infrastruktur
- [docs/de/SEGURIDAD.md](docs/de/SEGURIDAD.md): Token, Richtlinien und Produktionscheckliste
- [docs/de/ARQUITECTURA.md](docs/de/ARQUITECTURA.md): Backend/Frontend-Architektur und zentrale Flows
- [docs/de/API.md](docs/de/API.md): Endpunkt-Referenz
- [docs/de/DESARROLLO.md](docs/de/DESARROLLO.md): wie man Endpoints oder Bildschirme hinzufügt
- [docs/de/BACKEND.md](docs/de/BACKEND.md): Backend-Anleitung (Ebenen, Konfiguration, Auth, Tests)
- [docs/de/DATABASE.md](docs/de/DATABASE.md): Schema und Migrationen
- [docs/de/FEDERATION_PROTOCOL.md](docs/de/FEDERATION_PROTOCOL.md): Föderationsprotokoll zwischen Knoten (Phasen 2-10)
- [docs/de/FEDERATION_SECURITY.md](docs/de/FEDERATION_SECURITY.md): Vertrauen, mTLS, Portabilität und Resilienz
- [docs/de/FEDERATION_SCHEMA.md](docs/de/FEDERATION_SCHEMA.md): föderierte Entitäten und Checksum
- [docs/de/FEDERATION_CHAT_BROKER.md](docs/de/FEDERATION_CHAT_BROKER.md): Transportentscheidung und Implementierungsstatus

Außerdem ist der Startpunkt für Entwicklung und Projektkonvention [AGENTS.md](AGENTS.md).

### Siehe auch

- [docs/de/README.md](docs/de/README.md): allgemeiner Index nach Zielgruppe
- [docs/de/HERRAMIENTAS.md](docs/de/HERRAMIENTAS.md): Build-, Test- und Startbefehle
- [docs/de/FUNCIONAL.md](docs/de/FUNCIONAL.md): realer Produktnutzen pro Rolle

### Kurzes FAQ

- **Brauche ich Docker für den Start?** Nein. Der lokale Start mit `start.*` läuft ohne Docker; Docker dient für Produktionsumgebung und reproduzierbare Builds.
- **Was tun, wenn die API nicht antwortet?** Prüfe, ob das Backend auf `http://localhost:8000` läuft und ob `/docs` antwortet.
- **Welches Dokument soll ich zuerst lesen?** Als Nutzer [docs/de/USO.md](docs/de/USO.md); als Entwickler [docs/de/ARQUITECTURA.md](docs/de/ARQUITECTURA.md).
- **Woran erkenne ich, ob eine Änderung Doku-Update braucht?** Wenn sie Start, API, Rollen, Berechtigungen, Env-Variablen oder Schema ändert, aktualisiere auch die entsprechende Dokumentation.

## Beitragen

1. Forke das Repository.
2. Erstelle einen Branch (`git checkout -b feature/neue-funktion`).
3. Commite mit klaren, beschreibenden Nachrichten (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Pushe den Branch (`git push origin feature/neue-funktion`).
5. Öffne einen Pull Request mit Kontext, Änderungen und Validierung.

**Qualitätskonventionen:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` und `flutter test` müssen vor dem Merge bestehen. GitHub Actions führt diese Gates parallel aus und Dependabot öffnet wöchentlich gruppierte PRs: Patch/Minor wird bei grünem CI automatisch gemergt, Major bleibt zur manuellen Prüfung (Details in [docs/de/INFRAESTRUCTURA.md](docs/de/INFRAESTRUCTURA.md)).

## Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Siehe [LICENSE](LICENSE).
