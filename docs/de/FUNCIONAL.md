# Funktional — was man in Clakettes tun kann

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Reeller Nutzen des Projekts pro Rolle, mit dem Ablauf, der ihn stützt. Operative Details in [USO.md](USO.md), Endpoint-Referenz in [API.md](API.md).

## Festival (Organisator)

1. Erstellt das Festival (`POST /api/festivals/`) mit Beschreibung, Website, Ort und Logo.
2. Öffnet Ausschreibungen: Anmeldeformulare mit Abschnitten, Rollen und Tags (`RegistrationForm + Sections + Links`), zugänglich über einen öffentlichen Link, den jede Person ohne Konto ausfüllen kann.
3. Erhält Kurzfilme, die mit deinen Ausschreibungen und Drehorten verknüpft sind, verwaltet unter `/api/festivals/{id}/shortfilms` und klassifiziert als `official_section` (Standard) oder `contest`; das Festival-Profil zeigt den Zähler und die App ermöglicht die Filterung nach Typ.
4. Stellt das Programm zusammen: Events (Gala, Vorführung, Workshop, Podium, Networking, Preise, Party, Masterclass, Q&A) mit Ticketarten, Sitzplätzen (verfügbar/reserviert/verkauft/zugewiesen/blockiert), Reservierungen und Check-in der Teilnehmer; exportiert Teilnehmer als CSV und Events als ICS. Sichtet jedes Werk der Vorführung mit Status `pending/screened/disqualified` und Begründung und filtert nach Status, Disqualifizierten oder Teilnehmer-Tag. Nur Vorführungen mit Kurzfilmen desselben Festivals können programmiert werden (`EventService` lehnt fremde Ids ab). Die Organisation prüft die Eligibilitäts-Tags der Teilnehmer (Einwohner, Student) mit externen Methoden, und der Teilnehmer kann eine Prüfung durch Beifügen eines Wohnnachweises oder einer Immatrikulationsbescheinigung beantragen.
5. Benennt Komitees mit Mitgliedern und veröffentlicht Preise (verifiziert oder nicht, öffentlich oder nicht) pro Festival, Kurzfilm oder Nutzer, mit Eligibilitäts-Tags und Verifizierung des Empfängers.
6. Kommuniziert: Festival-Kanäle (admin/moderator/member), Nachrichten und Bilder im Profil, Rulebooks.

Er bearbeitet/löscht nur seine eigenen Festivals und verwaltet seine Nutzer (`require_festival_admin`). Mitglieder treten automatisch als `attendee` bei; andere Rollen werden von einem Admin zugewiesen (409, wenn bereits Mitglied).

## Profi (Nutzer, Jury, weitere Berufe)

- Profil mit Beruf (Regie, Schauspiel, Ton, Drehbuch, Schnitt, Kostüm, Make-up, Komparse, Synchronisation, Foley, Presse, Produktion, Vertrieb…) , Bio und Palmarès, verknüpft mit Festival-Plattform oder extern per Link.
- Feldweise Privatsphäre (E-Mail, Bio, Standort) und öffentliche/private Profile.
- Jeder Nutzer bearbeitet sein Profil und seine Kurzfilme; die Jury konsultiert und stimmt je nach Festival ab und darf nur dessen Kurzfilme bewerten.
- Direkt- und Gruppen-/Kanal-Chat mit Ende-zu-Ende-Verschlüsselung: öffentliche Schlüssel werden über `POST /api/users/me/public-key` veröffentlicht, der Server speichert und leitet nur Verschlüsseltes weiter, die eigentliche Verschlüsselung findet in der App statt. Zwischen föderierten Knoten läuft die Nachricht über die signierte Bridge, wird nach `message_id` dedupliziert und nach Datum sortiert; du kannst Nachrichten melden, und Administratoren können Nutzer stummschalten oder Wörter filtern. Die App zeigt Schreibindikator, Latenz und Lesebestätigungen, erlaubt die Suche im Verlauf und reiht offline Nachrichten dauerhaft mit derselben `message_id` ein.

## Express-Team (Attendee)
- Der Express-Wettbewerb (auch Guerrilla genannt) ist der Bürgerwettbewerb **innerhalb des Festivals**: Kurzfilme werden mit `contest_type = contest` erstellt und bewertet (der Standardwert ist `official_section`; Express und Guerrilla sind derselbe Wettbewerb).

- Automatischer Beitritt zum Festival (`POST /api/festivals/{id}/join`, Rolle `attendee`) und freier Austritt (`leave`).
- Geolokalisiert Teilnehmer, koordiniert die Gruppe per Chat und reicht den Kurzfilm für den Express-Wettbewerb ein.
- Reserviert Sitzplätze bei Events und sendet Anmeldungen über öffentlichen Link (Status: ausstehend/genehmigt/abgelehnt/Warteliste/storniert; Zahlungen: unbezahlt/ausstehend/bezahlt/erstattet/storniert).

## Publikum

Entdeckt Festivals (`GET /api/festivals/` paginiert und öffentlich), folgt Kurzfilmen und Palmarès, kontaktiert per Chat und konsultiert Veranstaltungsorte auf der Karte.

## Globaler Administrator (Admin)

Sieht und bearbeitet alles (Nutzer, Festivals, Kurzfilme, Kanäle, Formulare). Betrieb in [ADMINISTRACION.md](ADMINISTRACION.md) (Statistiken, Tabellen, Reset, Backups, Secrets). In der Föderation registriert er Knoten und ihre Richtlinien (`import_only`, `disable_chat`, `disable_search`), exportiert und importiert Bundles, migriert Festivals und Nutzeridentitäten mit ihren Redirects, veröffentlicht Ereignisse, moderiert den Chat und überwacht die Resilienz (p50/p95-Metriken und Schlüssel-Widerruf).

## Jury (Juror)

- Konsultiert die dem Festival zugewiesenen Werke und gibt Stimmen pro Kurzfilm ab (`POST /api/jury-votes/`).
- Bewertung pro Werk mit automatischer Aggregation; optionale Anonymität.
- Konsultiert aggregierte Ergebnisse für Organisatoren.

## Status, die man kennen sollte

- Festival-Mitglied: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Anmeldung: `draft → submitted → approved / rejected`; Einreichung: `pending / approved / rejected / waitlisted / cancelled`.
- Event-Teilnehmer: `registered / attended / no_show / cancelled`.
- Sichtung in der Vorführung: `pending / screened / disqualified`.
- Jury-Notizen und Protokolle pro Werk, mit Anmerkung: `special_mention / accesit / other`.
- Verifizierung des Teilnehmer-Tags: `unverified / pending / verified / rejected`.
- Sichtbarkeitsbereich von Events: `public / festival_members / roles / attendees_only`.

## Siehe auch

- [USO.md](USO.md): Systemstart und Betrieb
- [API.md](API.md): Endpoint-Referenz
- [ADMINISTRACION.md](ADMINISTRACION.md): Deployment-Administration
