# Funktional — was man in Clakettes tun kann

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Realer Projektwert nach Rolle, mit dem Fluss, der ihn stützt. Betrieblicher Detail in [USO.md](USO.md), Endpunkt-Referenz in [API.md](API.md).

## Festival (Organizer)

1. Festival erstellen (`POST /api/festivals/`) mit Beschreibung, Web, Sitz und Logo.
2. Ausschreibungen öffnen: Anmeldeformulare mit Abschnitten, Rollen und Tags (`RegistrationForm + Sections + Links`), über öffentlichen Link zugänglich, den jeder ohne Konto ausfüllen kann.
3. Kurzfilme empfangen, verknüpft mit Ausschreibungen und Drehorten.
4. Programmierung aufbauen: Events (Gala, Vorführung, Workshop, Podium, Networking, Auszeichnungen, Party, Masterclass, Q&A) mit Ticket-Typen, Sitzen (verfügbar/reserviert/verkauft/zugegeben/blockiert), Reservierungen und Check-in der Teilnehmer; Teilnehmer nach CSV exportieren und Events nach ICS. Jedes Werk beim Sichten mit Status `pending/screened/disqualified` und Grund kennzeichnen, nach Status, Disqualifizierten oder Teilnehmer-Tag filtern. Die Organisation verifiziert Teilnehmer-Eignungs-Tags (Einwohner, Student) über externe Methoden, und der Teilnehmer kann Verifizierung beantragen, indem er Wohnsitz- oder Immatrikulationsbescheinigung anhängt.
5. Komitees mit Mitgliedern benennen und Auszeichnungen (verifiziert oder nicht, öffentlich oder nicht) pro Festival, Kurzfilm oder Nutzer veröffentlichen, mit Eignungs-Tags und Empfänger-Verifizierung.
6. Kommunizieren: Festival-Kanäle (admin/moderator/member), Nachrichten und Bilder auf dem Profil, Regelwerke.

Nur eigene Festivals bearbeiten/löschen und eigene Nutzer verwalten (`require_festival_admin`). Mitglieder treten automatisch als `attendee` bei; andere Rollen werden von einem Admin zugewiesen (409 wenn bereits Mitglied).

## Professionell (Nutzer, Jury, andere Berufe)

- Profil mit Beruf (Regie, Schauspiel, Ton, Drehbuch, Schnitt, Kostüm, Maske, Statist, Synchronisation, Foley, Presse, Produktion, Vertrieb…), Bio und Auszeichnungen verknüpft mit Plattform-Festivals oder extern über Link.
- Feld-für-Feld-Privatsphäre (E-Mail, Bio, Standort) und öffentliche/private Profile.
- Jeder Nutzer bearbeitet sein Profil und seine Kurzfilme; die Jury konsultiert und stimmt gemäß ihrem Festival ab.
- Direkter und Gruppen/Kanal-Chat mit Ende-zu-Ende-Verschlüsselung: öffentliche Schlüssel werden bei `POST /api/users/me/public-key` veröffentlicht, der Server speichert und leitet nur Verschlüsseltes weiter, die eigentliche Verschlüsselung erfolgt in der App.

## Express-Team (attendee)

- Auto-Join zum Festival (`POST /api/festivals/{id}/join`, Rolle `attendee`) und freier Austritt (`leave`).
- Teilnehmer geolokalisieren, Gruppe per Chat koordinieren und Kurzfilm zum Express-Wettbewerb einreichen.
- Sitz bei Events reservieren und Anmeldungen über öffentlichen Link einreichen (Status: ausstehend/abgelehnt/angenommen/Warteliste/storniert; Zahlungen: unbezahlbar/ausstehend/bezahlt/erstattet/storniert).

## Publikum

Festivals entdecken (`GET /api/festivals/` paginiert und öffentlich), Kurzfilmen und Auszeichnungen folgen, per Chat kontaktieren und Orte auf der Karte einsehen.

## Globaler Admin (admin)

Sieht und bearbeitet alles (Nutzer, Festivals, Kurzfilme, Kanäle, Formulare). Betrieb in [ADMINISTRACION.md](ADMINISTRACION.md) (Stats, Tabellen, Reset, Backups, Geheimnisse).

## Jury (juror)

- Zugewiesene Werke des eigenen Festivals einsehen und Stimmen pro Kurzfilm abgeben (`POST /api/jury-votes/`).
- Bewertung pro Werk mit automatischer Aggregation; optionale Anonymität.
- Aggregierte Ergebnisse für Organisatoren einsehen.

## Zustände, die Sie kennen sollten

- Festival-Mitglied: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Anmeldung: `draft → submitted → approved / rejected`; Einreichung: `pending / approved / rejected / waitlisted / cancelled`.
- Event-Teilnehmer: `registered / attended / no_show / cancelled`.
- Sichtung bei Vorführung: `pending / screened / disqualified`.
- Jury-Notizen und Protokolle pro Werk, mit Anmerkung: `special_mention / accesit / other`.
- Verifizierung von Teilnehmer-Tag: `unverified / pending / verified / rejected`.
- Sichtbarkeitsumfang von Events: `public / festival_members / roles / attendees_only`.

## Siehe auch

- [USO.md](USO.md): Systemstart und Betrieb
- [API.md](API.md): Endpunkt-Referenz
- [ADMINISTRACION.md](ADMINISTRACION.md): Bereitstellungsverwaltung