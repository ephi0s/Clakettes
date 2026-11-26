# API — riferimento endpoint

[ES](../es/API.md) · [EN](../en/API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](../oc/API.md)

Generato da `app/routers/*.py` (prefissi di ogni `APIRouter` più quello in `app/main.py`) e dalle dipendenze di ogni endpoint.
Dettaglio interattivo: `/docs` (Swagger) e `/redoc` col backend avviato.

Tutti i caricamenti restituiscono un percorso relativo `/uploads/<cartella>/<file>`, mai un URL assoluto. Il client lo risolve con `resolveMediaUrl()`, che prepone il server attivo; gli URL `http(s)` restano invariati. I campi multimediali (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) accettano entrambi i formati.

## `admin` → `/api/admin`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/admin/stats` | sì (admin) |
| GET | `/api/admin/tables` | sì (admin) |
| GET | `/api/admin/audit-log` | sì (admin) |
| POST | `/api/admin/reset` | sì (admin) |

## `auth` → `/api/users`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/users/login` | no |

## `auth_sessions` → `/api/auth`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | no |
| GET | `/api/auth/sessions` | sì |
| DELETE | `/api/auth/sessions/{session_id}` | sì |
| POST | `/api/auth/sessions/revoke-all` | sì |

## `badges` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/badges/status` | no |
| PUT | `/api/badges/settings` | sì (admin) |
| GET | `/api/badges` | opzionale |
| POST | `/api/badges` | sì (admin) |
| GET | `/api/badges/{badge_id}` | opzionale |
| PUT | `/api/badges/{badge_id}` | sì (admin) |
| DELETE | `/api/badges/{badge_id}` | sì (admin) |
| POST | `/api/badges/{badge_id}/image` | sì (admin) |
| GET | `/api/badges/{badge_id}/eligibility` | opzionale |
| POST | `/api/badges/{badge_id}/assign` | sì (admin) |
| DELETE | `/api/badge-assignments/{assignment_id}` | sì |
| GET | `/api/users/{user_id}/badges` | opzionale |
| GET | `/api/festivals/{festival_id}/badges` | opzionale |

## `calendar` → `/api/calendar`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | opzionale |
| GET | `/api/calendar/agenda/export/ics` | opzionale |
| GET | `/api/calendar/settings` | no |
| GET | `/api/calendar/admin/settings` | sì (admin) |
| PUT | `/api/calendar/admin/settings` | sì (admin) |
| POST | `/api/calendar/dav/token` | sì |
| GET | `/api/calendar/dav/token` | sì |
| DELETE | `/api/calendar/dav/token` | sì |

## `channels` → `/api/channels`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/channels` | sì |
| GET | `/api/channels` | sì |
| GET | `/api/channels/public` | sì |
| GET | `/api/channels/{channel_id}` | sì |
| PUT | `/api/channels/{channel_id}` | sì |
| DELETE | `/api/channels/{channel_id}` | sì |
| POST | `/api/channels/{channel_id}/members` | sì |
| GET | `/api/channels/{channel_id}/members` | sì |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | sì |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | sì |

## `chat` → `/api/chat`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/chat/messages` | sì |
| POST | `/api/chat/messages` | sì |
| PUT | `/api/chat/messages/{message_id}/read` | sì |
| DELETE | `/api/chat/messages/{message_id}` | sì |
| GET | `/api/chat/groups` | sì |
| POST | `/api/chat/groups` | sì |
| GET | `/api/chat/groups/{group_id}` | sì |
| DELETE | `/api/chat/groups/{group_id}` | sì |
| GET | `/api/chat/groups/{group_id}/members` | sì |
| POST | `/api/chat/groups/{group_id}/members` | sì |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | sì |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | sì |
| WEBSOCKET | `/api/chat/ws` | token (query, obbligatorio) |

## `chat_moderation` → `/api/chat/moderation`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/chat/moderation/messages/{message_id}/report` | sì |
| PATCH | `/api/chat/moderation/messages/{message_id}/moderate` | sì |
| GET | `/api/chat/moderation/reports` | sì (admin) |
| POST | `/api/chat/moderation/mutes` | sì |
| GET | `/api/chat/moderation/mutes` | sì (admin) |
| GET | `/api/chat/moderation/limits` | sì (admin) |

## `committees` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees` | opzionale |
| POST | `/api/festivals/{festival_id}/committees` | sì |
| GET | `/api/committees/{committee_id}` | opzionale |
| PUT | `/api/committees/{committee_id}` | sì |
| DELETE | `/api/committees/{committee_id}` | sì |
| GET | `/api/committees/{committee_id}/members` | opzionale |
| POST | `/api/committees/{committee_id}/members` | sì |
| PUT | `/api/committee-members/{member_id}` | sì |
| DELETE | `/api/committee-members/{member_id}` | sì |

## `dav` → `/dav`

| Metodo | Percorso | Auth |
|---|---|---|
| OPTIONS | `/dav` | no |
| OPTIONS | `/dav/{dav_path:path}` | no |
| PROPFIND | `/dav` | no |
| GET | `/dav/{principal}/calendars/{collection}.ics` | no |
| HEAD | `/dav/{principal}/calendars/{collection}.ics` | no |
| GET | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| GET/HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| PROPFIND | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| REPORT | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| PROPFIND/REPORT | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | no |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | no |
| REPORT | `/dav/{principal}/calendars/{collection}` | no |
| REPORT | `/dav/{principal}/calendars/{collection}` | no |
| PROPFIND | `/dav/{principal}/calendars` | no |
| PROPFIND | `/dav/{principal}/calendars` | no |
| PROPFIND | `/dav/{principal}` | no |
| PROPFIND | `/dav/{principal}` | no |
| REPORT | `/dav/{principal}/calendars` | no |
| REPORT | `/dav/{principal}/calendars` | no |
| REPORT | `/dav/{principal}` | no |
| REPORT | `/dav/{principal}` | no |
| PUT/POST/DELETE/PATCH/MOVE/COPY/LOCK/UNLOCK/PROPPATCH | `/dav/{write_path:path}` | no |

## `delegations` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/delegations` | opzionale |
| POST | `/api/delegations` | sì |
| PUT | `/api/delegations/{delegation_id}` | sì |
| POST | `/api/delegations/{delegation_id}/revoke` | sì |
| GET | `/api/users/{user_id}/active-delegations` | opzionale |
| GET | `/api/role-transitions` | sì |
| POST | `/api/role-transitions` | sì |
| GET | `/api/users/{user_id}/role-transitions` | sì |
| GET | `/api/users/{user_id}/role-check` | sì |

## `events` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events` | no |
| GET | `/api/festivals/{festival_id}/events/export/ics` | sì |
| POST | `/api/festivals/{festival_id}/events` | sì |
| GET | `/api/events/{event_id}` | no |
| PUT | `/api/events/{event_id}` | sì |
| DELETE | `/api/events/{event_id}` | sì |
| GET | `/api/festivals/{festival_id}/events/programacion` | no |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | sì |
| GET | `/api/events/{event_id}/screenings` | no |
| PATCH | `/api/events/{event_id}/screenings/{shortfilm_id}` | sì |
| PUT | `/api/events/{event_id}/screenings/{shortfilm_id}/notes` | sì |
| PUT | `/api/events/{event_id}/screenings` | sì |
| GET | `/api/festivals/{festival_id}/screenings` | no |
| GET | `/api/events/{event_id}/occupancy` | no |
| GET | `/api/events/{event_id}/ticket-types` | no |
| POST | `/api/events/{event_id}/ticket-types` | sì |
| PUT | `/api/ticket-types/{tt_id}` | sì |
| DELETE | `/api/ticket-types/{tt_id}` | sì |
| GET | `/api/events/{event_id}/seats` | no |
| POST | `/api/events/{event_id}/seats/bulk` | sì |
| GET | `/api/events/{event_id}/seats/sections` | no |
| GET | `/api/events/{event_id}/seats/counts` | no |
| PUT | `/api/seats/{seat_id}` | sì |
| POST | `/api/seats/{seat_id}/release` | sì |
| DELETE | `/api/seats/{seat_id}` | sì |
| GET | `/api/events/{event_id}/reservations` | sì |
| POST | `/api/events/{event_id}/reservations` | sì |
| PUT | `/api/reservations/{reservation_id}` | sì |
| POST | `/api/reservations/{reservation_id}/confirm` | sì |
| POST | `/api/reservations/{reservation_id}/cancel` | sì |
| DELETE | `/api/reservations/{reservation_id}` | sì |
| GET | `/api/events/{event_id}/attendees` | sì |
| POST | `/api/events/{event_id}/attendees` | sì |
| GET | `/api/attendees/{attendee_id}` | no |
| PUT | `/api/attendees/{attendee_id}` | sì |
| POST | `/api/attendees/{attendee_id}/check-in` | sì |
| GET | `/api/events/{event_id}/attendees/counts` | no |
| GET | `/api/events/{event_id}/attendees/export/csv` | sì |
| DELETE | `/api/attendees/{attendee_id}` | sì |
| POST | `/api/events/{event_id}/assign-vip` | sì |
| GET | `/api/users/me/events` | sì |
| GET | `/api/users/me/events/{event_id}/reservation` | sì |
| GET | `/api/festivals/{festival_id}/awards` | no |
| POST | `/api/festivals/{festival_id}/awards` | sì |
| PUT | `/api/awards/{award_id}` | sì |
| DELETE | `/api/awards/{award_id}` | sì |
| PATCH | `/api/awards/{award_id}/recipient-verification` | sì |
| GET | `/api/users/{user_id}/awards` | no |
| GET | `/api/public/profile/{token}` | no |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | no |

## `federation` → `/api/federation`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/federation/nodes` | sì (admin) |
| POST | `/api/federation/nodes` | sì (admin) |
| GET | `/api/federation/manifest` | no |
| PATCH | `/api/federation/reports/{report_id}` | no |
| GET | `/api/federation/directory` | no |
| POST | `/api/federation/reports` | no |
| GET | `/api/federation/reports` | no |
| DELETE | `/api/federation/users/{user_ref}` | no |
| GET | `/api/federation/export/{user_ref}` | no |
| GET | `/api/federation/health` (deprecato) | no |
| POST | `/api/federation/verify` | no |
| POST | `/api/federation/publish` | JWT di federazione |
| POST | `/api/federation/recover` | no |
| POST | `/api/federation/bridge` | JWT di federazione |
| GET | `/api/federation/aggregate-nodes` (deprecato) | no |
| GET | `/api/federation/keys` (deprecato) | no |
| GET | `/api/federation/events` (deprecato) | no |
| GET | `/api/federation/capabilities` (deprecato) | no |
| GET | `/api/federation/status` (deprecato) | no |
| GET | `/api/federation/info` (deprecato) | no |
| GET | `/api/federation/ping` (deprecato) | no |
| POST | `/api/federation/echo` | no |
| GET | `/api/federation/time` | no |
| GET | `/api/federation/version` (deprecato) | no |
| POST | `/api/federation/checksum` | no |
| POST | `/api/federation/notify` (deprecato) | no |
| POST | `/api/federation/subscribe` (deprecato) | no |
| POST | `/api/federation/unsubscribe` (deprecato) | no |
| GET | `/api/federation/discover` (deprecato) | no |
| POST | `/api/federation/register` | JWT di federazione |
| POST | `/api/federation/unregister` | no |
| POST | `/api/federation/sync` | no |
| POST | `/api/federation/reconcile` | no |
| GET | `/api/federation/heartbeat` (deprecato) | no |
| GET | `/api/federation/whoami` | JWT di federazione |
| GET | `/api/federation/peers` (deprecato) | no |
| GET | `/api/federation/links` (deprecato) | no |
| GET | `/api/federation/stats` (deprecato) | no |
| GET | `/api/federation/config` (deprecato) | no |
| GET | `/api/federation/status-check` (deprecato) | no |
| GET | `/api/federation/ready` (deprecato) | no |
| GET | `/api/federation/live` (deprecato) | no |
| GET | `/api/federation/alive` (deprecato) | no |
| GET | `/api/federation/down` (deprecato) | no |
| GET | `/api/federation/maintenance` (deprecato) | no |
| GET | `/api/federation/readyz` (deprecato) | no |
| GET | `/api/federation/livez` (deprecato) | no |
| GET | `/api/federation/healthz` (deprecato) | no |
| GET | `/api/federation/ok` (deprecato) | no |
| GET | `/api/federation/yes` (deprecato) | no |
| GET | `/api/federation/no` (deprecato) | no |
| GET | `/api/federation/maybe` (deprecato) | no |
| GET | `/api/federation/always` (deprecato) | no |
| GET | `/api/federation/never` (deprecato) | no |
| POST | `/api/federation/import` | no |
| POST | `/api/federation/dedup` | no |
| POST | `/api/federation/retry` | no |
| POST | `/api/federation/recover-node` | no |
| GET | `/api/federation/integrity` | no |
| GET | `/api/federation/metrics` | no |
| GET | `/api/federation/users/{ref}` | no |
| GET | `/api/federation/.well-known/webfinger` | no |
| POST | `/api/federation/peers/verify` | no |
| POST | `/api/federation/peers/{domain}/revoke` | sì (admin) |
| GET | `/api/federation/.well-known/jwks.json` | no |
| POST | `/api/federation/token` | no |

## `federation_chat_bridge` → `/api/federation`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/federation/chat/bridge/inbound` | no |
| POST | `/api/federation/chat/bridge/outbound` | no |
| GET | `/api/federation/chat/bridge/config` | no |
| GET | `/api/federation/chat/messages` | no |

## `federation_events` → `/api/federation/events`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/federation/events/stream` | Bearer (header) o token (query, obsoleto) |
| POST | `/api/federation/events/publish` | sì (admin) |
| GET | `/api/federation/events/retry-queue` | sì (admin) |

## `federation_portability` → `/api/federation/portability`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/federation/portability/bundles` | sì |
| POST | `/api/federation/portability/imports` | sì |
| POST | `/api/federation/portability/festivals/{festival_id}/migrate` | sì (admin) |
| POST | `/api/federation/portability/users/{user_ref}/migrate` | sì (admin) |
| GET | `/api/federation/portability/redirects/{old_ref}` | sì |

## `federation_resilience` → `/api/federation/resilience`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/federation/resilience/health` | no |
| GET | `/api/federation/resilience/heartbeat` | no |
| GET | `/api/federation/resilience/metrics` | no |
| POST | `/api/federation/resilience/keys/revoke` | sì (admin) |
| GET | `/api/federation/resilience/keys/revoked` | no |
| GET | `/api/federation/resilience/incident-plan` | no |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks` | no |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | no |
| POST | `/api/festivals/{festival_id}/rulebooks` | sì |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | sì |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | sì |

## `festivals` → `/api/festivals`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals` | no |
| POST | `/api/festivals` | sì |
| GET | `/api/festivals/{festival_id}` | no |
| GET | `/api/festivals/{festival_id}/shortfilms` | no |
| POST | `/api/festivals/{festival_id}/shortfilms` | sì |
| GET | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | no |
| PUT | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | sì |
| PUT | `/api/festivals/{festival_id}` | sì |
| DELETE | `/api/festivals/{festival_id}` | sì |
| POST | `/api/festivals/{festival_id}/images` | sì |
| DELETE | `/api/festivals/{festival_id}/images` | sì |
| GET | `/api/festivals/{festival_id}/locations` | no |
| POST | `/api/festivals/{festival_id}/locations` | sì |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | sì |

## `form_definitions` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/forms` | sì |
| POST | `/api/forms` | sì |
| GET | `/api/forms/{form_id}` | sì |
| PUT | `/api/forms/{form_id}` | sì |
| DELETE | `/api/forms/{form_id}` | sì |
| POST | `/api/forms/{form_id}/clone` | sì |
| POST | `/api/forms/{form_id}/pages` | sì |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | sì |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | sì |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields` | sì |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | sì |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | sì |
| GET | `/api/forms/{form_id}/links` | sì |
| POST | `/api/forms/{form_id}/links` | sì |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | sì |
| GET | `/api/forms/public/{token}` | no |
| POST | `/api/forms/public/{token}/submit` | opzionale |
| GET | `/api/forms/{form_id}/responses` | sì |
| GET | `/api/forms/{form_id}/responses/export/csv` | sì |
| PUT | `/api/forms/responses/{response_id}` | sì |
| POST | `/api/forms/responses/{response_id}/approve` | sì |
| POST | `/api/forms/responses/{response_id}/reject` | sì |

## `jury_votes` → `/api/jury-votes`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/jury-votes` | sì |
| GET | `/api/jury-votes/{festival_id}` | opzionale |
| GET | `/api/jury-votes/aggregate/{festival_id}` | no |
| GET | `/api/jury-votes/by-juror/{festival_id}/{juror_id}` | sì |
| GET | `/api/jury-votes/anonymous/{festival_id}` | sì |

## `keys` → `/api/users`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | sì |
| GET | `/api/users/{user_id}/public-key` | sì |

## `location_images` → `/api/locations/{location_id}/images`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images` | no |
| POST | `/api/locations/{location_id}/images/upload` | sì |
| POST | `/api/locations/{location_id}/images/url` | sì |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | sì |

## `location_relations` → `/api/locations/{location_id}/relations`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations` | no |
| POST | `/api/locations/{location_id}/relations` | sì |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | sì |
| POST | `/api/locations/{location_id}/relations/suggest` | sì |

## `location_tags` → `/api/locations/{location_id}/tags`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags` | no |
| POST | `/api/locations/{location_id}/tags` | sì |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | sì |

## `locations` → `/api/locations`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations` | no |
| POST | `/api/locations` | sì |
| GET | `/api/locations/{location_id}` | no |
| PUT | `/api/locations/{location_id}` | sì |
| PUT | `/api/locations/{location_id}/badge` | sì |
| DELETE | `/api/locations/{location_id}` | sì |

## `notifications` → `/api/notifications`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/notifications` | sì |
| GET | `/api/notifications/unread-count` | sì |
| PUT | `/api/notifications/{notification_id}/read` | sì |
| PUT | `/api/notifications/read-all` | sì |
| DELETE | `/api/notifications/{notification_id}` | sì |

## `participant_tags` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/participant-tags` | no |
| POST | `/api/participant-tags` | sì (admin) |
| GET | `/api/participant-tags/{tag_id}` | no |
| PUT | `/api/participant-tags/{tag_id}` | sì (admin) |
| DELETE | `/api/participant-tags/{tag_id}` | sì (admin) |
| GET | `/api/festivals/{festival_id}/participant-tags` | no |
| POST | `/api/festivals/{festival_id}/participant-tags` | sì |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | sì |

## `payments` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | sì |
| GET | `/api/payments` | sì |
| GET | `/api/payments/{payment_id}` | sì |
| POST | `/api/payments/{payment_id}/confirm` | sì |
| POST | `/api/payments/{payment_id}/refund` | sì |
| POST | `/api/payments/webhook/mock` | no |
| POST | `/api/payments/webhook/stripe` | no |
| POST | `/api/payments/webhook/redsys` | no |

## `posts` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/posts` | opzionale |
| POST | `/api/users/{user_id}/posts` | sì |
| GET | `/api/festivals/{festival_id}/posts` | opzionale |
| POST | `/api/festivals/{festival_id}/posts` | sì |
| GET | `/api/posts/{post_id}` | opzionale |
| PUT | `/api/posts/{post_id}` | sì |
| DELETE | `/api/posts/{post_id}` | sì |
| GET | `/api/posts/{post_id}/replies` | opzionale |
| POST | `/api/posts/{post_id}/replies` | sì |
| POST | `/api/posts/{post_id}/moderate` | sì |

## `registration_forms` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms` | sì |
| POST | `/api/festivals/{festival_id}/registration-forms` | sì |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sì |
| GET | `/api/registration-forms/{form_id}` | sì |
| PUT | `/api/registration-forms/{form_id}` | sì |
| DELETE | `/api/registration-forms/{form_id}` | sì |
| GET | `/api/registration-forms/{form_id}/registrations` | sì |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sì |
| GET | `/api/public/forms/{token}` | no |
| POST | `/api/public/forms/{token}/register` | opzionale |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | sì |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | sì |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | sì |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | sì |
| GET | `/api/registration-forms/{form_id}/links` | sì |
| POST | `/api/registration-forms/{form_id}/links` | sì |
| DELETE | `/api/registration-form-links/{link_id}` | sì |
| POST | `/api/registration-form-links/{link_id}/regenerate` | sì |
| GET | `/api/festivals/{festival_id}/registrations` | sì |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | sì |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | sì |
| GET | `/api/users/{user_id}/registrations` | sì |
| PUT | `/api/registrations/{registration_id}` | sì |
| POST | `/api/registrations/{registration_id}/approve` | sì |
| POST | `/api/registrations/{registration_id}/reject` | sì |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | sì |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | sì |
| DELETE | `/api/registrations/{registration_id}` | sì |
| POST | `/api/registration-forms/{form_id}/sections` | sì |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | sì |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | sì |

## `role_groups` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/role-groups` | no |
| POST | `/api/role-groups` | sì (admin) |
| GET | `/api/role-groups/{group_id}` | no |
| PUT | `/api/role-groups/{group_id}` | sì (admin) |
| DELETE | `/api/role-groups/{group_id}` | sì (admin) |
| GET | `/api/role-groups/{group_id}/memberships` | no |
| POST | `/api/role-groups/{group_id}/memberships` | sì (admin) |
| PUT | `/api/role-group-memberships/{membership_id}` | sì (admin) |
| DELETE | `/api/role-group-memberships/{membership_id}` | sì (admin) |

## `roles` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/roles` | sì |
| POST | `/api/roles` | sì (admin) |
| GET | `/api/roles/hierarchy` | opzionale |
| GET | `/api/roles/{role_id}` | opzionale |
| PUT | `/api/roles/{role_id}` | sì (admin) |
| DELETE | `/api/roles/{role_id}` | sì (admin) |
| GET | `/api/festivals/{festival_id}/roles` | opzionale |
| POST | `/api/festivals/{festival_id}/roles` | sì |
| POST | `/api/festivals/{festival_id}/roles/initialize` | sì (admin) |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | sì |
| GET | `/api/roles/{role_id}/dependencies` | opzionale |
| POST | `/api/role-dependencies` | sì (admin) |
| DELETE | `/api/role-dependencies/{dependency_id}` | sì (admin) |
| GET | `/api/roles/{role_id}/conflicts` | opzionale |
| POST | `/api/role-conflicts` | sì (admin) |
| DELETE | `/api/role-conflicts/{conflict_id}` | sì (admin) |
| GET | `/api/roles/{role_id}/check-conflicts` | opzionale |

## `search` → `/api/search`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/search` | sì |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations` | no |
| POST | `/api/shortfilms/{shortfilm_id}/locations` | sì |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | sì |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | sì |

## `shortfilms` → `/api/shortfilms`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/shortfilms` (deprecato) | no |
| POST | `/api/shortfilms` (deprecato) | sì |
| GET | `/api/shortfilms/{shortfilm_id}` (deprecato) | no |
| PUT | `/api/shortfilms/{shortfilm_id}` (deprecato) | sì |
| DELETE | `/api/shortfilms/{shortfilm_id}` (deprecato) | sì |

## `uploads` → `/api/uploads`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | sì |
| POST | `/api/uploads/thumbnail` | sì |
| POST | `/api/uploads/video` | sì |
| POST | `/api/uploads/document` | sì |
| POST | `/api/uploads/chat-image` | sì |

## `user_aliases` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases` | no |
| POST | `/api/users/{user_id}/aliases` | sì |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | sì |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | sì |

## `user_blocks` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/blocks` | sì |
| DELETE | `/api/users/{user_id}/blocks/{blocked_id}` | sì |
| GET | `/api/users/{user_id}/blocks` | sì |
| GET | `/api/users/{user_id}/blocks/{blocked_id}/status` | sì |

## `user_festival` → `/api/festivals`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | sì |
| DELETE | `/api/festivals/{festival_id}/leave` | sì |
| GET | `/api/festivals/{festival_id}/members` | sì |
| GET | `/api/festivals/user/{user_id}/festivals` | sì |

## `user_follows` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/follow` | sì |
| DELETE | `/api/users/{user_id}/follow` | sì |
| GET | `/api/users/{user_id}/follow/status` | sì |
| GET | `/api/users/{user_id}/followers` | sì |
| GET | `/api/users/{user_id}/following` | sì |

## `user_roles` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles` | sì |
| POST | `/api/users/{user_id}/roles` | sì |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | sì |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | sì |
| GET | `/api/users/{user_id}/participant-tags` | sì |
| PATCH | `/api/users/{user_id}/participant-tags/{upt_id}/verify` | sì |
| POST | `/api/users/{user_id}/participant-tags/{upt_id}/request-verification` | sì |
| POST | `/api/users/{user_id}/participant-tags` | sì |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | sì |

## `users` → `/api/users`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/users` | sì |
| GET | `/api/users/public` | no |
| GET | `/api/users/me` | sì |
| GET | `/api/users/me/export` | sì |
| DELETE | `/api/users/me` | sì |
| POST | `/api/users` | sì |
| GET | `/api/users/{user_id}` | sì |
| GET | `/api/users/{user_id}/public` | no |
| PUT | `/api/users/{user_id}` | sì |
| DELETE | `/api/users/{user_id}` | sì |

## `validation_rules` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/validation-rules` | no |
| POST | `/api/validation-rules` | sì (admin) |
| GET | `/api/validation-rules/{rule_id}` | no |
| PUT | `/api/validation-rules/{rule_id}` | sì (admin) |
| DELETE | `/api/validation-rules/{rule_id}` | sì (admin) |
| GET | `/api/validation-rule-groups` | no |
| POST | `/api/validation-rule-groups` | sì (admin) |
