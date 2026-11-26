# API — referéncia dels endpoints

[ES](../es/API.md) · [EN](../en/API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](API.md)

Generat dempuèi `app/routers/*.py` (prefixe de cada `APIRouter` plus aquel de `app/main.py`) e las dependéncias de cada endpoint.
Datalh interactiu: `/docs` (Swagger) e `/redoc` amb lo backend en marcha.

Totes las pujadas retornan un camin relatiu `/uploads/<dossièr>/<fichièr>`, jamai una URL absoluda. Lo client lo resòlv amb `resolveMediaUrl()`, que apond lo servidor actiu; las URL `http(s)` demoran intactas. Los camps de mèdia (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) acceptan ambedos formats.

## `admin` → `/api/admin`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/admin/stats` | òc (admin) |
| GET | `/api/admin/tables` | òc (admin) |
| GET | `/api/admin/audit-log` | òc (admin) |
| POST | `/api/admin/reset` | òc (admin) |

## `auth` → `/api/users`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/users/login` | non |

## `auth_sessions` → `/api/auth`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | non |
| GET | `/api/auth/sessions` | òc |
| DELETE | `/api/auth/sessions/{session_id}` | òc |
| POST | `/api/auth/sessions/revoke-all` | òc |

## `badges` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/badges/status` | non |
| PUT | `/api/badges/settings` | òc (admin) |
| GET | `/api/badges` | opcional |
| POST | `/api/badges` | òc (admin) |
| GET | `/api/badges/{badge_id}` | opcional |
| PUT | `/api/badges/{badge_id}` | òc (admin) |
| DELETE | `/api/badges/{badge_id}` | òc (admin) |
| POST | `/api/badges/{badge_id}/image` | òc (admin) |
| GET | `/api/badges/{badge_id}/eligibility` | opcional |
| POST | `/api/badges/{badge_id}/assign` | òc (admin) |
| DELETE | `/api/badge-assignments/{assignment_id}` | òc |
| GET | `/api/users/{user_id}/badges` | opcional |
| GET | `/api/festivals/{festival_id}/badges` | opcional |

## `calendar` → `/api/calendar`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | opcional |
| GET | `/api/calendar/agenda/export/ics` | opcional |
| GET | `/api/calendar/settings` | non |
| GET | `/api/calendar/admin/settings` | òc (admin) |
| PUT | `/api/calendar/admin/settings` | òc (admin) |
| POST | `/api/calendar/dav/token` | òc |
| GET | `/api/calendar/dav/token` | òc |
| DELETE | `/api/calendar/dav/token` | òc |

## `channels` → `/api/channels`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/channels` | òc |
| GET | `/api/channels` | òc |
| GET | `/api/channels/public` | òc |
| GET | `/api/channels/{channel_id}` | òc |
| PUT | `/api/channels/{channel_id}` | òc |
| DELETE | `/api/channels/{channel_id}` | òc |
| POST | `/api/channels/{channel_id}/members` | òc |
| GET | `/api/channels/{channel_id}/members` | òc |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | òc |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | òc |

## `chat` → `/api/chat`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/chat/messages` | òc |
| POST | `/api/chat/messages` | òc |
| PUT | `/api/chat/messages/{message_id}/read` | òc |
| DELETE | `/api/chat/messages/{message_id}` | òc |
| GET | `/api/chat/groups` | òc |
| POST | `/api/chat/groups` | òc |
| GET | `/api/chat/groups/{group_id}` | òc |
| DELETE | `/api/chat/groups/{group_id}` | òc |
| GET | `/api/chat/groups/{group_id}/members` | òc |
| POST | `/api/chat/groups/{group_id}/members` | òc |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | òc |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | òc |
| WEBSOCKET | `/api/chat/ws` | jeton (query, obligatòri) |

## `chat_moderation` → `/api/chat/moderation`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/chat/moderation/messages/{message_id}/report` | òc |
| PATCH | `/api/chat/moderation/messages/{message_id}/moderate` | òc |
| GET | `/api/chat/moderation/reports` | òc (admin) |
| POST | `/api/chat/moderation/mutes` | òc |
| GET | `/api/chat/moderation/mutes` | òc (admin) |
| GET | `/api/chat/moderation/limits` | òc (admin) |

## `committees` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees` | opcional |
| POST | `/api/festivals/{festival_id}/committees` | òc |
| GET | `/api/committees/{committee_id}` | opcional |
| PUT | `/api/committees/{committee_id}` | òc |
| DELETE | `/api/committees/{committee_id}` | òc |
| GET | `/api/committees/{committee_id}/members` | opcional |
| POST | `/api/committees/{committee_id}/members` | òc |
| PUT | `/api/committee-members/{member_id}` | òc |
| DELETE | `/api/committee-members/{member_id}` | òc |

## `dav` → `/dav`

| Metòde | Camin | Auth |
|---|---|---|
| OPTIONS | `/dav` | non |
| OPTIONS | `/dav/{dav_path:path}` | non |
| PROPFIND | `/dav` | non |
| GET | `/dav/{principal}/calendars/{collection}.ics` | non |
| HEAD | `/dav/{principal}/calendars/{collection}.ics` | non |
| GET | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| GET/HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| PROPFIND | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| REPORT | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| PROPFIND/REPORT | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | non |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | non |
| REPORT | `/dav/{principal}/calendars/{collection}` | non |
| REPORT | `/dav/{principal}/calendars/{collection}` | non |
| PROPFIND | `/dav/{principal}/calendars` | non |
| PROPFIND | `/dav/{principal}/calendars` | non |
| PROPFIND | `/dav/{principal}` | non |
| PROPFIND | `/dav/{principal}` | non |
| REPORT | `/dav/{principal}/calendars` | non |
| REPORT | `/dav/{principal}/calendars` | non |
| REPORT | `/dav/{principal}` | non |
| REPORT | `/dav/{principal}` | non |
| PUT/POST/DELETE/PATCH/MOVE/COPY/LOCK/UNLOCK/PROPPATCH | `/dav/{write_path:path}` | non |

## `delegations` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/delegations` | opcional |
| POST | `/api/delegations` | òc |
| PUT | `/api/delegations/{delegation_id}` | òc |
| POST | `/api/delegations/{delegation_id}/revoke` | òc |
| GET | `/api/users/{user_id}/active-delegations` | opcional |
| GET | `/api/role-transitions` | òc |
| POST | `/api/role-transitions` | òc |
| GET | `/api/users/{user_id}/role-transitions` | òc |
| GET | `/api/users/{user_id}/role-check` | òc |

## `events` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events` | non |
| GET | `/api/festivals/{festival_id}/events/export/ics` | òc |
| POST | `/api/festivals/{festival_id}/events` | òc |
| GET | `/api/events/{event_id}` | non |
| PUT | `/api/events/{event_id}` | òc |
| DELETE | `/api/events/{event_id}` | òc |
| GET | `/api/festivals/{festival_id}/events/programacion` | non |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | òc |
| GET | `/api/events/{event_id}/screenings` | non |
| PATCH | `/api/events/{event_id}/screenings/{shortfilm_id}` | òc |
| PUT | `/api/events/{event_id}/screenings/{shortfilm_id}/notes` | òc |
| PUT | `/api/events/{event_id}/screenings` | òc |
| GET | `/api/festivals/{festival_id}/screenings` | non |
| GET | `/api/events/{event_id}/occupancy` | non |
| GET | `/api/events/{event_id}/ticket-types` | non |
| POST | `/api/events/{event_id}/ticket-types` | òc |
| PUT | `/api/ticket-types/{tt_id}` | òc |
| DELETE | `/api/ticket-types/{tt_id}` | òc |
| GET | `/api/events/{event_id}/seats` | non |
| POST | `/api/events/{event_id}/seats/bulk` | òc |
| GET | `/api/events/{event_id}/seats/sections` | non |
| GET | `/api/events/{event_id}/seats/counts` | non |
| PUT | `/api/seats/{seat_id}` | òc |
| POST | `/api/seats/{seat_id}/release` | òc |
| DELETE | `/api/seats/{seat_id}` | òc |
| GET | `/api/events/{event_id}/reservations` | òc |
| POST | `/api/events/{event_id}/reservations` | òc |
| PUT | `/api/reservations/{reservation_id}` | òc |
| POST | `/api/reservations/{reservation_id}/confirm` | òc |
| POST | `/api/reservations/{reservation_id}/cancel` | òc |
| DELETE | `/api/reservations/{reservation_id}` | òc |
| GET | `/api/events/{event_id}/attendees` | òc |
| POST | `/api/events/{event_id}/attendees` | òc |
| GET | `/api/attendees/{attendee_id}` | non |
| PUT | `/api/attendees/{attendee_id}` | òc |
| POST | `/api/attendees/{attendee_id}/check-in` | òc |
| GET | `/api/events/{event_id}/attendees/counts` | non |
| GET | `/api/events/{event_id}/attendees/export/csv` | òc |
| DELETE | `/api/attendees/{attendee_id}` | òc |
| POST | `/api/events/{event_id}/assign-vip` | òc |
| GET | `/api/users/me/events` | òc |
| GET | `/api/users/me/events/{event_id}/reservation` | òc |
| GET | `/api/festivals/{festival_id}/awards` | non |
| POST | `/api/festivals/{festival_id}/awards` | òc |
| PUT | `/api/awards/{award_id}` | òc |
| DELETE | `/api/awards/{award_id}` | òc |
| PATCH | `/api/awards/{award_id}/recipient-verification` | òc |
| GET | `/api/users/{user_id}/awards` | non |
| GET | `/api/public/profile/{token}` | non |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | non |

## `federation` → `/api/federation`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/federation/nodes` | òc (admin) |
| POST | `/api/federation/nodes` | òc (admin) |
| GET | `/api/federation/manifest` | non |
| PATCH | `/api/federation/reports/{report_id}` | non |
| GET | `/api/federation/directory` | non |
| POST | `/api/federation/reports` | non |
| GET | `/api/federation/reports` | non |
| DELETE | `/api/federation/users/{user_ref}` | non |
| GET | `/api/federation/export/{user_ref}` | non |
| GET | `/api/federation/health` (depreciat) | non |
| POST | `/api/federation/verify` | non |
| POST | `/api/federation/publish` | JWT de federacion |
| POST | `/api/federation/recover` | non |
| POST | `/api/federation/bridge` | JWT de federacion |
| GET | `/api/federation/aggregate-nodes` (depreciat) | non |
| GET | `/api/federation/keys` (depreciat) | non |
| GET | `/api/federation/events` (depreciat) | non |
| GET | `/api/federation/capabilities` (depreciat) | non |
| GET | `/api/federation/status` (depreciat) | non |
| GET | `/api/federation/info` (depreciat) | non |
| GET | `/api/federation/ping` (depreciat) | non |
| POST | `/api/federation/echo` | non |
| GET | `/api/federation/time` | non |
| GET | `/api/federation/version` (depreciat) | non |
| POST | `/api/federation/checksum` | non |
| POST | `/api/federation/notify` (depreciat) | non |
| POST | `/api/federation/subscribe` (depreciat) | non |
| POST | `/api/federation/unsubscribe` (depreciat) | non |
| GET | `/api/federation/discover` (depreciat) | non |
| POST | `/api/federation/register` | JWT de federacion |
| POST | `/api/federation/unregister` | non |
| POST | `/api/federation/sync` | non |
| POST | `/api/federation/reconcile` | non |
| GET | `/api/federation/heartbeat` (depreciat) | non |
| GET | `/api/federation/whoami` | JWT de federacion |
| GET | `/api/federation/peers` (depreciat) | non |
| GET | `/api/federation/links` (depreciat) | non |
| GET | `/api/federation/stats` (depreciat) | non |
| GET | `/api/federation/config` (depreciat) | non |
| GET | `/api/federation/status-check` (depreciat) | non |
| GET | `/api/federation/ready` (depreciat) | non |
| GET | `/api/federation/live` (depreciat) | non |
| GET | `/api/federation/alive` (depreciat) | non |
| GET | `/api/federation/down` (depreciat) | non |
| GET | `/api/federation/maintenance` (depreciat) | non |
| GET | `/api/federation/readyz` (depreciat) | non |
| GET | `/api/federation/livez` (depreciat) | non |
| GET | `/api/federation/healthz` (depreciat) | non |
| GET | `/api/federation/ok` (depreciat) | non |
| GET | `/api/federation/yes` (depreciat) | non |
| GET | `/api/federation/no` (depreciat) | non |
| GET | `/api/federation/maybe` (depreciat) | non |
| GET | `/api/federation/always` (depreciat) | non |
| GET | `/api/federation/never` (depreciat) | non |
| POST | `/api/federation/import` | non |
| POST | `/api/federation/dedup` | non |
| POST | `/api/federation/retry` | non |
| POST | `/api/federation/recover-node` | non |
| GET | `/api/federation/integrity` | non |
| GET | `/api/federation/metrics` | non |
| GET | `/api/federation/users/{ref}` | non |
| GET | `/api/federation/.well-known/webfinger` | non |
| POST | `/api/federation/peers/verify` | non |
| POST | `/api/federation/peers/{domain}/revoke` | òc (admin) |
| GET | `/api/federation/.well-known/jwks.json` | non |
| POST | `/api/federation/token` | non |

## `federation_chat_bridge` → `/api/federation`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/federation/chat/bridge/inbound` | non |
| POST | `/api/federation/chat/bridge/outbound` | non |
| GET | `/api/federation/chat/bridge/config` | non |
| GET | `/api/federation/chat/messages` | non |

## `federation_events` → `/api/federation/events`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/federation/events/stream` | Bearer (en-tèsta) o jeton (requèsta, obsolèt) |
| POST | `/api/federation/events/publish` | òc (admin) |
| GET | `/api/federation/events/retry-queue` | òc (admin) |

## `federation_portability` → `/api/federation/portability`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/federation/portability/bundles` | òc |
| POST | `/api/federation/portability/imports` | òc |
| POST | `/api/federation/portability/festivals/{festival_id}/migrate` | òc (admin) |
| POST | `/api/federation/portability/users/{user_ref}/migrate` | òc (admin) |
| GET | `/api/federation/portability/redirects/{old_ref}` | òc |

## `federation_resilience` → `/api/federation/resilience`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/federation/resilience/health` | non |
| GET | `/api/federation/resilience/heartbeat` | non |
| GET | `/api/federation/resilience/metrics` | non |
| POST | `/api/federation/resilience/keys/revoke` | òc (admin) |
| GET | `/api/federation/resilience/keys/revoked` | non |
| GET | `/api/federation/resilience/incident-plan` | non |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks` | non |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | non |
| POST | `/api/festivals/{festival_id}/rulebooks` | òc |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | òc |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | òc |

## `festivals` → `/api/festivals`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals` | non |
| POST | `/api/festivals` | òc |
| GET | `/api/festivals/{festival_id}` | non |
| GET | `/api/festivals/{festival_id}/shortfilms` | non |
| POST | `/api/festivals/{festival_id}/shortfilms` | òc |
| GET | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | non |
| PUT | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | òc |
| PUT | `/api/festivals/{festival_id}` | òc |
| DELETE | `/api/festivals/{festival_id}` | òc |
| POST | `/api/festivals/{festival_id}/images` | òc |
| DELETE | `/api/festivals/{festival_id}/images` | òc |
| GET | `/api/festivals/{festival_id}/locations` | non |
| POST | `/api/festivals/{festival_id}/locations` | òc |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | òc |

## `form_definitions` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/forms` | òc |
| POST | `/api/forms` | òc |
| GET | `/api/forms/{form_id}` | òc |
| PUT | `/api/forms/{form_id}` | òc |
| DELETE | `/api/forms/{form_id}` | òc |
| POST | `/api/forms/{form_id}/clone` | òc |
| POST | `/api/forms/{form_id}/pages` | òc |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | òc |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | òc |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields` | òc |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | òc |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | òc |
| GET | `/api/forms/{form_id}/links` | òc |
| POST | `/api/forms/{form_id}/links` | òc |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | òc |
| GET | `/api/forms/public/{token}` | non |
| POST | `/api/forms/public/{token}/submit` | opcional |
| GET | `/api/forms/{form_id}/responses` | òc |
| GET | `/api/forms/{form_id}/responses/export/csv` | òc |
| PUT | `/api/forms/responses/{response_id}` | òc |
| POST | `/api/forms/responses/{response_id}/approve` | òc |
| POST | `/api/forms/responses/{response_id}/reject` | òc |

## `jury_votes` → `/api/jury-votes`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/jury-votes` | òc |
| GET | `/api/jury-votes/{festival_id}` | opcional |
| GET | `/api/jury-votes/aggregate/{festival_id}` | non |
| GET | `/api/jury-votes/by-juror/{festival_id}/{juror_id}` | òc |
| GET | `/api/jury-votes/anonymous/{festival_id}` | òc |

## `keys` → `/api/users`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | òc |
| GET | `/api/users/{user_id}/public-key` | òc |

## `location_images` → `/api/locations/{location_id}/images`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images` | non |
| POST | `/api/locations/{location_id}/images/upload` | òc |
| POST | `/api/locations/{location_id}/images/url` | òc |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | òc |

## `location_relations` → `/api/locations/{location_id}/relations`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations` | non |
| POST | `/api/locations/{location_id}/relations` | òc |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | òc |
| POST | `/api/locations/{location_id}/relations/suggest` | òc |

## `location_tags` → `/api/locations/{location_id}/tags`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags` | non |
| POST | `/api/locations/{location_id}/tags` | òc |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | òc |

## `locations` → `/api/locations`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations` | non |
| POST | `/api/locations` | òc |
| GET | `/api/locations/{location_id}` | non |
| PUT | `/api/locations/{location_id}` | òc |
| PUT | `/api/locations/{location_id}/badge` | òc |
| DELETE | `/api/locations/{location_id}` | òc |

## `notifications` → `/api/notifications`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/notifications` | òc |
| GET | `/api/notifications/unread-count` | òc |
| PUT | `/api/notifications/{notification_id}/read` | òc |
| PUT | `/api/notifications/read-all` | òc |
| DELETE | `/api/notifications/{notification_id}` | òc |

## `participant_tags` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/participant-tags` | non |
| POST | `/api/participant-tags` | òc (admin) |
| GET | `/api/participant-tags/{tag_id}` | non |
| PUT | `/api/participant-tags/{tag_id}` | òc (admin) |
| DELETE | `/api/participant-tags/{tag_id}` | òc (admin) |
| GET | `/api/festivals/{festival_id}/participant-tags` | non |
| POST | `/api/festivals/{festival_id}/participant-tags` | òc |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | òc |

## `payments` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | òc |
| GET | `/api/payments` | òc |
| GET | `/api/payments/{payment_id}` | òc |
| POST | `/api/payments/{payment_id}/confirm` | òc |
| POST | `/api/payments/{payment_id}/refund` | òc |
| POST | `/api/payments/webhook/mock` | non |
| POST | `/api/payments/webhook/stripe` | non |
| POST | `/api/payments/webhook/redsys` | non |

## `posts` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/posts` | opcional |
| POST | `/api/users/{user_id}/posts` | òc |
| GET | `/api/festivals/{festival_id}/posts` | opcional |
| POST | `/api/festivals/{festival_id}/posts` | òc |
| GET | `/api/posts/{post_id}` | opcional |
| PUT | `/api/posts/{post_id}` | òc |
| DELETE | `/api/posts/{post_id}` | òc |
| GET | `/api/posts/{post_id}/replies` | opcional |
| POST | `/api/posts/{post_id}/replies` | òc |
| POST | `/api/posts/{post_id}/moderate` | òc |

## `registration_forms` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms` | òc |
| POST | `/api/festivals/{festival_id}/registration-forms` | òc |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | òc |
| GET | `/api/registration-forms/{form_id}` | òc |
| PUT | `/api/registration-forms/{form_id}` | òc |
| DELETE | `/api/registration-forms/{form_id}` | òc |
| GET | `/api/registration-forms/{form_id}/registrations` | òc |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | òc |
| GET | `/api/public/forms/{token}` | non |
| POST | `/api/public/forms/{token}/register` | opcional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | òc |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | òc |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | òc |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | òc |
| GET | `/api/registration-forms/{form_id}/links` | òc |
| POST | `/api/registration-forms/{form_id}/links` | òc |
| DELETE | `/api/registration-form-links/{link_id}` | òc |
| POST | `/api/registration-form-links/{link_id}/regenerate` | òc |
| GET | `/api/festivals/{festival_id}/registrations` | òc |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | òc |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | òc |
| GET | `/api/users/{user_id}/registrations` | òc |
| PUT | `/api/registrations/{registration_id}` | òc |
| POST | `/api/registrations/{registration_id}/approve` | òc |
| POST | `/api/registrations/{registration_id}/reject` | òc |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | òc |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | òc |
| DELETE | `/api/registrations/{registration_id}` | òc |
| POST | `/api/registration-forms/{form_id}/sections` | òc |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | òc |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | òc |

## `role_groups` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/role-groups` | non |
| POST | `/api/role-groups` | òc (admin) |
| GET | `/api/role-groups/{group_id}` | non |
| PUT | `/api/role-groups/{group_id}` | òc (admin) |
| DELETE | `/api/role-groups/{group_id}` | òc (admin) |
| GET | `/api/role-groups/{group_id}/memberships` | non |
| POST | `/api/role-groups/{group_id}/memberships` | òc (admin) |
| PUT | `/api/role-group-memberships/{membership_id}` | òc (admin) |
| DELETE | `/api/role-group-memberships/{membership_id}` | òc (admin) |

## `roles` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/roles` | òc |
| POST | `/api/roles` | òc (admin) |
| GET | `/api/roles/hierarchy` | opcional |
| GET | `/api/roles/{role_id}` | opcional |
| PUT | `/api/roles/{role_id}` | òc (admin) |
| DELETE | `/api/roles/{role_id}` | òc (admin) |
| GET | `/api/festivals/{festival_id}/roles` | opcional |
| POST | `/api/festivals/{festival_id}/roles` | òc |
| POST | `/api/festivals/{festival_id}/roles/initialize` | òc (admin) |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | òc |
| GET | `/api/roles/{role_id}/dependencies` | opcional |
| POST | `/api/role-dependencies` | òc (admin) |
| DELETE | `/api/role-dependencies/{dependency_id}` | òc (admin) |
| GET | `/api/roles/{role_id}/conflicts` | opcional |
| POST | `/api/role-conflicts` | òc (admin) |
| DELETE | `/api/role-conflicts/{conflict_id}` | òc (admin) |
| GET | `/api/roles/{role_id}/check-conflicts` | opcional |

## `search` → `/api/search`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/search` | òc |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations` | non |
| POST | `/api/shortfilms/{shortfilm_id}/locations` | òc |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | òc |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | òc |

## `shortfilms` → `/api/shortfilms`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/shortfilms` (depreciat) | non |
| POST | `/api/shortfilms` (depreciat) | òc |
| GET | `/api/shortfilms/{shortfilm_id}` (depreciat) | non |
| PUT | `/api/shortfilms/{shortfilm_id}` (depreciat) | òc |
| DELETE | `/api/shortfilms/{shortfilm_id}` (depreciat) | òc |

## `uploads` → `/api/uploads`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | òc |
| POST | `/api/uploads/thumbnail` | òc |
| POST | `/api/uploads/video` | òc |
| POST | `/api/uploads/document` | òc |
| POST | `/api/uploads/chat-image` | òc |

## `user_aliases` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases` | non |
| POST | `/api/users/{user_id}/aliases` | òc |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | òc |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | òc |

## `user_blocks` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/blocks` | òc |
| DELETE | `/api/users/{user_id}/blocks/{blocked_id}` | òc |
| GET | `/api/users/{user_id}/blocks` | òc |
| GET | `/api/users/{user_id}/blocks/{blocked_id}/status` | òc |

## `user_festival` → `/api/festivals`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | òc |
| DELETE | `/api/festivals/{festival_id}/leave` | òc |
| GET | `/api/festivals/{festival_id}/members` | òc |
| GET | `/api/festivals/user/{user_id}/festivals` | òc |

## `user_follows` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/follow` | òc |
| DELETE | `/api/users/{user_id}/follow` | òc |
| GET | `/api/users/{user_id}/follow/status` | òc |
| GET | `/api/users/{user_id}/followers` | òc |
| GET | `/api/users/{user_id}/following` | òc |

## `user_roles` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles` | òc |
| POST | `/api/users/{user_id}/roles` | òc |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | òc |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | òc |
| GET | `/api/users/{user_id}/participant-tags` | òc |
| PATCH | `/api/users/{user_id}/participant-tags/{upt_id}/verify` | òc |
| POST | `/api/users/{user_id}/participant-tags/{upt_id}/request-verification` | òc |
| POST | `/api/users/{user_id}/participant-tags` | òc |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | òc |

## `users` → `/api/users`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/users` | òc |
| GET | `/api/users/public` | non |
| GET | `/api/users/me` | òc |
| GET | `/api/users/me/export` | òc |
| DELETE | `/api/users/me` | òc |
| POST | `/api/users` | òc |
| GET | `/api/users/{user_id}` | òc |
| GET | `/api/users/{user_id}/public` | non |
| PUT | `/api/users/{user_id}` | òc |
| DELETE | `/api/users/{user_id}` | òc |

## `validation_rules` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/validation-rules` | non |
| POST | `/api/validation-rules` | òc (admin) |
| GET | `/api/validation-rules/{rule_id}` | non |
| PUT | `/api/validation-rules/{rule_id}` | òc (admin) |
| DELETE | `/api/validation-rules/{rule_id}` | òc (admin) |
| GET | `/api/validation-rule-groups` | non |
| POST | `/api/validation-rule-groups` | òc (admin) |
