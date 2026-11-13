# Functional — what you can do in Clakettes

[ES](../es/FUNCIONAL.md) · [EN](FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Real project value by role, with the flow that supports it. Operational detail in [USO.md](USO.md), endpoint reference in [API.md](API.md).

## Festival (organizer)

1. Create the festival (`POST /api/festivals/`) with description, website, venue and logo.
2. Open calls: registration forms with sections, roles and tags (`RegistrationForm + Sections + Links`), exposed via public link that anyone can fill without an account.
3. Receive shorts linked to your calls and shooting locations.
4. Set up programming: events (gala, screening, workshop, panel, networking, awards, party, masterclass, Q&A) with ticket types, seats (available/reserved/sold/assigned/blocked), reservations and attendee check-in; export attendees to CSV and events to ICS. Screen each work with status `pending/screened/disqualified` and reason, filter by status, disqualified or participant tag. The organization verifies participant eligibility tags (resident, student) with external methods, and the participant can request verification by attaching a residency or enrollment certificate.
5. Appoint committees with members and publish awards (verified or not, public or not) per festival, short or user, with eligibility tags and recipient verification.
6. Communicate: festival channels (admin/moderator/member), messages and images on the profile, rulebooks.

Only edits/deletes their own festivals and manages their users (`require_festival_admin`). Members join automatically as `attendee`; other roles are assigned by an admin (409 if already a member).

## Professional (user, jury, other crafts)

- Profile with craft (directing, acting, sound, writing, editing, costume, makeup, extra, dubbing, foley, press, production, distribution…), bio and awards linked to platform festivals or external via link.
- Field-by-field privacy (email, bio, location) and public/private profiles.
- Each user edits their profile and their shorts; the jury consults and votes according to their festival.
- Direct and group/channel chat with end-to-end encryption: public keys are published at `POST /api/users/me/public-key`, the server only stores and forwards encrypted data, real encryption happens in the app.

## Express team (attendee)

- Auto-join to festival (`POST /api/festivals/{id}/join`, role `attendee`) and free exit (`leave`).
- Geolocate participants, coordinate the group via chat and submit the short to the express contest.
- Reserve a seat at events and submit registrations via public link (states: pending/approved/rejected/waitlisted/cancelled; payments: unpaid/pending/paid/refunded/cancelled).

## Audience

Discover festivals (`GET /api/festivals/` paginated and public), follow shorts and awards, contact via chat and consult venues on the map.

## Global administrator (admin)

Sees and edits everything (users, festivals, shorts, channels, forms). Operations in [ADMINISTRACION.md](ADMINISTRACION.md) (stats, tables, reset, backups, secrets).

## Jury (juror)

- Consults works assigned to their festival and casts votes per short (`POST /api/jury-votes/`).
- Scoring per work with automatic aggregation; optional anonymity.
- Consults aggregated results for organizers.

## States you should know

- Festival member: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Registration: `draft → submitted → approved / rejected`; submission: `pending / approved / rejected / waitlisted / cancelled`.
- Event attendee: `registered / attended / no_show / cancelled`.
- Projection screening: `pending / screened / disqualified`.
- Jury notes and minutes per work, with annotation: `special_mention / accesit / other`.
- Participant tag verification: `unverified / pending / verified / rejected`.
- Event visibility scope: `public / festival_members / roles / attendees_only`.

## See also

- [USO.md](USO.md): system startup and operation
- [API.md](API.md): endpoint reference
- [ADMINISTRACION.md](ADMINISTRACION.md): deployment administration