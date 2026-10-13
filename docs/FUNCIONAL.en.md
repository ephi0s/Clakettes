# Functional — what you can do in Clakettes

Real project value by role, with the flow behind it. Operating details in [USO.md](USO.en.md), endpoint reference in [API.md](API.md).

## Festival (organizer)

1. Create the festival (`POST /api/festivals/`) with description, website, venue and logo.
2. Open calls: registration forms with sections, roles and tags (`RegistrationForm + Sections + Links`), exposed via a public link anyone can fill in without an account.
3. Receive short films linked to your calls and shooting locations.
4. Build the programme: events (gala, screening, workshop, panel, networking, awards, party, masterclass, Q&A) with ticket types, seats (available/reserved/sold/assigned/blocked), reservations and attendee check-in; export attendees to CSV and events to ICS.
5. Appoint committees with members and publish awards (verified or not, public or not) by festival, short film or user.
6. Communicate: festival channels (admin/moderator/member), messages and images on the profile, rulebooks.

They can only edit/delete their festivals and manage their users (`require_festival_admin`). Members join on their own as `attendee`; remaining roles are assigned by an admin (409 if already a member).

## Professional (user, jury, other crafts)

- Profile with craft (directing, acting, sound, screenwriting, editing, wardrobe, makeup, extras, dubbing, foley, press, production, distribution…), bio and awards linked to platform festivals or external via link.
- Field-by-field privacy (email, bio, location) and public/private profiles.
- Each user edits their profile and short films; the jury reviews and votes per its festival.
- Direct and group/channel chat with end-to-end encryption: public keys are published at `POST /api/users/me/public-key`, the server only stores and relays ciphertext, real encryption happens in the app.

## Express crew (attendee)

- Auto-join the festival (`POST /api/festivals/{id}/join`, `attendee` role) and free leave (`leave`).
- Geolocate participants, coordinate the group via chat and submit the short film to the express contest.
- Reserve event seats and send registrations via public link (states: pending/approved/rejected/waitlisted/cancelled; payments: unpaid/pending/paid/refunded/cancelled).

## Audience

Discover festivals (`GET /api/festivals/` paginated and public), follow short films and awards, contact via chat and check venues on the map.

## Global administrator (admin)

Sees and edits everything (users, festivals, short films, channels, forms). Operations in [ADMINISTRACION.md](ADMINISTRACION.en.md) (stats, tables, reset, backups, secrets).

## States you should know

- Festival member: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Registration: `draft → submitted → approved / rejected`; submission: `pending / approved / rejected / waitlisted / cancelled`.
- Event attendee: `registered / attended / no_show / cancelled`.
- Event visibility scope: `public / festival_members / roles / attendees_only`.
