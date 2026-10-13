# Funktional — was man in Clakettes tun kann

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Realer Projektnutzen pro Rolle, mit dem Ablauf, der ihn trägt. Operative Details in [USO.md](USO.md), Endpunktreferenz in [API.md](../es/API.md).

## Festival (organizer)

1. Erstellt das Festival (`POST /api/festivals/`) mit Beschreibung, Web, Sitz und Logo.
2. Öffnet Ausschreibungen: Anmeldeformulare mit Sektionen, Rollen und Tags (`RegistrationForm + Sections + Links`), über öffentlichen Link exponiert, den jeder ohne Konto ausfüllen kann.
3. Empfängt Kurzfilme zu seinen Ausschreibungen und Drehorte.
4. Baut das Programm: Events (Gala, Screening, Workshop, Panel, Networking, Preise, Feier, Masterclass, Q&A) mit Tickettypen, Sitzen (verfügbar/reserviert/verkauft/zugewiesen/blockiert), Reservierungen und Check-in von Teilnehmenden; exportiert Teilnehmende nach CSV und Events nach ICS.
5. Ernennt Komitees mit Mitgliedern und publiziert Preise (verifiziert oder nicht, öffentlich oder nicht) pro Festival, Kurzfilm oder Nutzer.
6. Kommuniziert: Festival-Kanäle (admin/moderator/member), Nachrichten und Bilder im Profil, Rulebooks.

Bearbeitet/löscht nur seine Festivals und verwaltet seine Nutzer (`require_festival_admin`). Mitglieder treten allein als `attendee` bei; restliche Rollen vergibt ein Admin (409 wenn bereits Mitglied).

## Profi (user, jury, restliche Gewerke)

- Profil mit Gewerk (Regie, Schauspiel, Ton, Drehbuch, Schnitt, Kostüm, Maske, Komparserie, Synchron, Foley, Presse, Produktion, Verleih …), Bio und Palmarès verknüpft mit Plattform-Festivals oder extern per Link.
- Privatsphäre Feld für Feld (E-Mail, Bio, Standort) und öffentliche/private Profile.
- Jeder Nutzer bearbeitet sein Profil und seine Kurzfilme; die Jury sichtet und stimmt je nach Festival ab.
- Direkt- und Gruppen-/Kanal-Chat mit Ende-zu-Ende-Verschlüsselung: öffentliche Schlüssel werden in `POST /api/users/me/public-key` publiziert, der Server speichert und relayt nur Verschlüsseltes, die echte Verschlüsselung passiert in der App.

## Express-Team (attendee)

- Auto-Join zum Festival (`POST /api/festivals/{id}/join`, Rolle `attendee`) und freier Austritt (`leave`).
- Geolokalisiert Teilnehmende, koordiniert die Gruppe per Chat und reicht den Kurzfilm beim Express-Wettbewerb ein.
- Reserviert Sitz in Events und sendet Anmeldungen per öffentlichem Link (Status: ausstehend/genehmigt/abgelehnt/warteliste/storniert; Zahlungen: unbezahlt/ausstehend/bezahlt/erstattet/storniert).

## Publikum

Entdeckt Festivals (`GET /api/festivals/` paginiert und öffentlich), folgt Kurzfilmen und Palmarès, kontaktiert per Chat und sieht Spielstätten auf der Karte.

## Globaler Admin (admin)

Sieht und bearbeitet alles (Nutzer, Festivals, Kurzfilme, Kanäle, Formulare). Operatives in [ADMINISTRACION.md](ADMINISTRACION.md) (Stats, Tabellen, Reset, Backups, Secrets).

## Status, die du kennen musst

- Festival-Mitglied: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Anmeldung: `draft → submitted → approved / rejected`; Einreichung: `pending / approved / rejected / waitlisted / cancelled`.
- Event-Teilnehmer: `registered / attended / no_show / cancelled`.
- Event-Sichtbarkeitsreichweite: `public / festival_members / roles / attendees_only`.
