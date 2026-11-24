# API — référence des endpoints

[ES](../es/API.md) · [EN](../en/API.md) · [FR](API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](../oc/API.md)

Généré depuis `app/routers/*.py` (préfixe de chaque `APIRouter` plus celui de `app/main.py`) et des dépendances de chaque endpoint.
Détail interactif : `/docs` (Swagger) et `/redoc` avec le backend lancé.

Tous les téléversements renvoient un chemin relatif `/uploads/<dossier>/<fichier>`, jamais une URL absolue. Le client le résout avec `resolveMediaUrl()`, qui préfixe le serveur actif ; les URL `http(s)` restent inchangées. Les champs de médias (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) acceptent les deux formats.

## `admin` → `/api/admin`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/admin/stats` | oui (admin) |
| GET | `/api/admin/tables` | oui (admin) |
| GET | `/api/admin/audit-log` | oui (admin) |
| POST | `/api/admin/reset` | oui (admin) |

## `auth` → `/api/users`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/users/login` | non |

## `auth_sessions` → `/api/auth`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | non |
| GET | `/api/auth/sessions` | oui |
| DELETE | `/api/auth/sessions/{session_id}` | oui |
| POST | `/api/auth/sessions/revoke-all` | oui |

## `badges` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/badges/status` | non |
| PUT | `/api/badges/settings` | oui (admin) |
| GET | `/api/badges` | optionnel |
| POST | `/api/badges` | oui (admin) |
| GET | `/api/badges/{badge_id}` | optionnel |
| PUT | `/api/badges/{badge_id}` | oui (admin) |
| DELETE | `/api/badges/{badge_id}` | oui (admin) |
| POST | `/api/badges/{badge_id}/image` | oui (admin) |
| GET | `/api/badges/{badge_id}/eligibility` | optionnel |
| POST | `/api/badges/{badge_id}/assign` | oui (admin) |
| DELETE | `/api/badge-assignments/{assignment_id}` | oui |
| GET | `/api/users/{user_id}/badges` | optionnel |
| GET | `/api/festivals/{festival_id}/badges` | optionnel |

## `calendar` → `/api/calendar`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | optionnel |
| GET | `/api/calendar/agenda/export/ics` | optionnel |
| GET | `/api/calendar/settings` | non |
| GET | `/api/calendar/admin/settings` | oui (admin) |
| PUT | `/api/calendar/admin/settings` | oui (admin) |
| POST | `/api/calendar/dav/token` | oui |
| GET | `/api/calendar/dav/token` | oui |
| DELETE | `/api/calendar/dav/token` | oui |

## `channels` → `/api/channels`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/channels` | oui |
| GET | `/api/channels` | oui |
| GET | `/api/channels/public` | oui |
| GET | `/api/channels/{channel_id}` | oui |
| PUT | `/api/channels/{channel_id}` | oui |
| DELETE | `/api/channels/{channel_id}` | oui |
| POST | `/api/channels/{channel_id}/members` | oui |
| GET | `/api/channels/{channel_id}/members` | oui |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | oui |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | oui |

## `chat` → `/api/chat`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/chat/messages` | oui |
| POST | `/api/chat/messages` | oui |
| PUT | `/api/chat/messages/{message_id}/read` | oui |
| DELETE | `/api/chat/messages/{message_id}` | oui |
| GET | `/api/chat/groups` | oui |
| POST | `/api/chat/groups` | oui |
| GET | `/api/chat/groups/{group_id}` | oui |
| DELETE | `/api/chat/groups/{group_id}` | oui |
| GET | `/api/chat/groups/{group_id}/members` | oui |
| POST | `/api/chat/groups/{group_id}/members` | oui |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | oui |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | oui |
| WEBSOCKET | `/api/chat/ws` | jeton (query, obligatoire) |

## `chat_moderation` → `/api/chat/moderation`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/chat/moderation/messages/{message_id}/report` | oui |
| PATCH | `/api/chat/moderation/messages/{message_id}/moderate` | oui |
| GET | `/api/chat/moderation/reports` | oui (admin) |
| POST | `/api/chat/moderation/mutes` | oui |
| GET | `/api/chat/moderation/mutes` | oui (admin) |
| GET | `/api/chat/moderation/limits` | oui (admin) |

## `committees` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees` | optionnel |
| POST | `/api/festivals/{festival_id}/committees` | oui |
| GET | `/api/committees/{committee_id}` | optionnel |
| PUT | `/api/committees/{committee_id}` | oui |
| DELETE | `/api/committees/{committee_id}` | oui |
| GET | `/api/committees/{committee_id}/members` | optionnel |
| POST | `/api/committees/{committee_id}/members` | oui |
| PUT | `/api/committee-members/{member_id}` | oui |
| DELETE | `/api/committee-members/{member_id}` | oui |

## `dav` → `/dav`

| Méthode | Chemin | Auth |
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

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/delegations` | optionnel |
| POST | `/api/delegations` | oui |
| PUT | `/api/delegations/{delegation_id}` | oui |
| POST | `/api/delegations/{delegation_id}/revoke` | oui |
| GET | `/api/users/{user_id}/active-delegations` | optionnel |
| GET | `/api/role-transitions` | oui |
| POST | `/api/role-transitions` | oui |
| GET | `/api/users/{user_id}/role-transitions` | oui |
| GET | `/api/users/{user_id}/role-check` | oui |

## `events` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events` | non |
| GET | `/api/festivals/{festival_id}/events/export/ics` | oui |
| POST | `/api/festivals/{festival_id}/events` | oui |
| GET | `/api/events/{event_id}` | non |
| PUT | `/api/events/{event_id}` | oui |
| DELETE | `/api/events/{event_id}` | oui |
| GET | `/api/festivals/{festival_id}/events/programacion` | non |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | oui |
| GET | `/api/events/{event_id}/screenings` | non |
| PATCH | `/api/events/{event_id}/screenings/{shortfilm_id}` | oui |
| PUT | `/api/events/{event_id}/screenings/{shortfilm_id}/notes` | oui |
| PUT | `/api/events/{event_id}/screenings` | oui |
| GET | `/api/festivals/{festival_id}/screenings` | non |
| GET | `/api/events/{event_id}/occupancy` | non |
| GET | `/api/events/{event_id}/ticket-types` | non |
| POST | `/api/events/{event_id}/ticket-types` | oui |
| PUT | `/api/ticket-types/{tt_id}` | oui |
| DELETE | `/api/ticket-types/{tt_id}` | oui |
| GET | `/api/events/{event_id}/seats` | non |
| POST | `/api/events/{event_id}/seats/bulk` | oui |
| GET | `/api/events/{event_id}/seats/sections` | non |
| GET | `/api/events/{event_id}/seats/counts` | non |
| PUT | `/api/seats/{seat_id}` | oui |
| POST | `/api/seats/{seat_id}/release` | oui |
| DELETE | `/api/seats/{seat_id}` | oui |
| GET | `/api/events/{event_id}/reservations` | oui |
| POST | `/api/events/{event_id}/reservations` | oui |
| PUT | `/api/reservations/{reservation_id}` | oui |
| POST | `/api/reservations/{reservation_id}/confirm` | oui |
| POST | `/api/reservations/{reservation_id}/cancel` | oui |
| DELETE | `/api/reservations/{reservation_id}` | oui |
| GET | `/api/events/{event_id}/attendees` | oui |
| POST | `/api/events/{event_id}/attendees` | oui |
| GET | `/api/attendees/{attendee_id}` | non |
| PUT | `/api/attendees/{attendee_id}` | oui |
| POST | `/api/attendees/{attendee_id}/check-in` | oui |
| GET | `/api/events/{event_id}/attendees/counts` | non |
| GET | `/api/events/{event_id}/attendees/export/csv` | oui |
| DELETE | `/api/attendees/{attendee_id}` | oui |
| POST | `/api/events/{event_id}/assign-vip` | oui |
| GET | `/api/users/me/events` | oui |
| GET | `/api/users/me/events/{event_id}/reservation` | oui |
| GET | `/api/festivals/{festival_id}/awards` | non |
| POST | `/api/festivals/{festival_id}/awards` | oui |
| PUT | `/api/awards/{award_id}` | oui |
| DELETE | `/api/awards/{award_id}` | oui |
| PATCH | `/api/awards/{award_id}/recipient-verification` | oui |
| GET | `/api/users/{user_id}/awards` | non |
| GET | `/api/public/profile/{token}` | non |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | non |

## `federation` → `/api/federation`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/federation/nodes` | oui (admin) |
| POST | `/api/federation/nodes` | oui (admin) |
| GET | `/api/federation/manifest` | non |
| PATCH | `/api/federation/reports/{report_id}` | non |
| GET | `/api/federation/directory` | non |
| POST | `/api/federation/reports` | non |
| GET | `/api/federation/reports` | non |
| DELETE | `/api/federation/users/{user_ref}` | JWT de fédération |
| GET | `/api/federation/export/{user_ref}` | non |
| GET | `/api/federation/health` (obsolète) | non |
| POST | `/api/federation/verify` | non |
| POST | `/api/federation/publish` | JWT de fédération |
| POST | `/api/federation/recover` | non |
| POST | `/api/federation/bridge` | JWT de fédération |
| GET | `/api/federation/aggregate-nodes` (obsolète) | non |
| GET | `/api/federation/keys` (obsolète) | non |
| GET | `/api/federation/events` (obsolète) | non |
| GET | `/api/federation/capabilities` (obsolète) | non |
| GET | `/api/federation/status` (obsolète) | non |
| GET | `/api/federation/info` (obsolète) | non |
| GET | `/api/federation/ping` (obsolète) | non |
| POST | `/api/federation/echo` | non |
| GET | `/api/federation/time` | non |
| GET | `/api/federation/version` (obsolète) | non |
| POST | `/api/federation/checksum` | non |
| POST | `/api/federation/notify` (obsolète) | non |
| POST | `/api/federation/subscribe` (obsolète) | non |
| POST | `/api/federation/unsubscribe` (obsolète) | non |
| GET | `/api/federation/discover` (obsolète) | non |
| POST | `/api/federation/register` | non |
| POST | `/api/federation/unregister` | non |
| POST | `/api/federation/sync` | non |
| POST | `/api/federation/reconcile` | non |
| GET | `/api/federation/heartbeat` (obsolète) | non |
| GET | `/api/federation/whoami` | JWT de fédération |
| GET | `/api/federation/peers` (obsolète) | non |
| GET | `/api/federation/links` (obsolète) | non |
| GET | `/api/federation/stats` (obsolète) | non |
| GET | `/api/federation/config` (obsolète) | non |
| GET | `/api/federation/status-check` (obsolète) | non |
| GET | `/api/federation/ready` (obsolète) | non |
| GET | `/api/federation/live` (obsolète) | non |
| GET | `/api/federation/alive` (obsolète) | non |
| GET | `/api/federation/down` (obsolète) | non |
| GET | `/api/federation/maintenance` (obsolète) | non |
| GET | `/api/federation/readyz` (obsolète) | non |
| GET | `/api/federation/livez` (obsolète) | non |
| GET | `/api/federation/healthz` (obsolète) | non |
| GET | `/api/federation/ok` (obsolète) | non |
| GET | `/api/federation/yes` (obsolète) | non |
| GET | `/api/federation/no` (obsolète) | non |
| GET | `/api/federation/maybe` (obsolète) | non |
| GET | `/api/federation/always` (obsolète) | non |
| GET | `/api/federation/never` (obsolète) | non |
| POST | `/api/federation/import` | non |
| POST | `/api/federation/dedup` | non |
| POST | `/api/federation/retry` | non |
| POST | `/api/federation/recover-node` | non |
| GET | `/api/federation/integrity` | non |
| GET | `/api/federation/metrics` | non |
| GET | `/api/federation/users/{ref}` | non |
| GET | `/api/federation/.well-known/webfinger` | non |
| POST | `/api/federation/peers/verify` | non |
| POST | `/api/federation/peers/{domain}/revoke` | oui (admin) |
| GET | `/api/federation/.well-known/jwks.json` | non |
| POST | `/api/federation/token` | non |

## `federation_chat_bridge` → `/api/federation`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/federation/chat/bridge/inbound` | non |
| POST | `/api/federation/chat/bridge/outbound` | non |
| GET | `/api/federation/chat/bridge/config` | non |
| GET | `/api/federation/chat/messages` | non |

## `federation_events` → `/api/federation/events`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/federation/events/stream` | jeton (query, obligatoire) |
| POST | `/api/federation/events/publish` | oui (admin) |
| GET | `/api/federation/events/retry-queue` | oui (admin) |

## `federation_portability` → `/api/federation/portability`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/federation/portability/bundles` | oui |
| POST | `/api/federation/portability/imports` | oui |
| POST | `/api/federation/portability/festivals/{festival_id}/migrate` | oui (admin) |
| POST | `/api/federation/portability/users/{user_ref}/migrate` | oui (admin) |
| GET | `/api/federation/portability/redirects/{old_ref}` | oui |

## `federation_resilience` → `/api/federation/resilience`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/federation/resilience/health` | non |
| GET | `/api/federation/resilience/heartbeat` | non |
| GET | `/api/federation/resilience/metrics` | non |
| POST | `/api/federation/resilience/keys/revoke` | oui (admin) |
| GET | `/api/federation/resilience/keys/revoked` | non |
| GET | `/api/federation/resilience/incident-plan` | non |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks` | non |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | non |
| POST | `/api/festivals/{festival_id}/rulebooks` | oui |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | oui |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | oui |

## `festivals` → `/api/festivals`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals` | non |
| POST | `/api/festivals` | oui |
| GET | `/api/festivals/{festival_id}` | non |
| GET | `/api/festivals/{festival_id}/shortfilms` | non |
| POST | `/api/festivals/{festival_id}/shortfilms` | oui |
| GET | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | non |
| PUT | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | oui |
| PUT | `/api/festivals/{festival_id}` | oui |
| DELETE | `/api/festivals/{festival_id}` | oui |
| POST | `/api/festivals/{festival_id}/images` | oui |
| DELETE | `/api/festivals/{festival_id}/images` | oui |
| GET | `/api/festivals/{festival_id}/locations` | non |
| POST | `/api/festivals/{festival_id}/locations` | oui |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | oui |

## `form_definitions` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/forms` | oui |
| POST | `/api/forms` | oui |
| GET | `/api/forms/{form_id}` | oui |
| PUT | `/api/forms/{form_id}` | oui |
| DELETE | `/api/forms/{form_id}` | oui |
| POST | `/api/forms/{form_id}/clone` | oui |
| POST | `/api/forms/{form_id}/pages` | oui |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | oui |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | oui |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields` | oui |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | oui |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | oui |
| GET | `/api/forms/{form_id}/links` | oui |
| POST | `/api/forms/{form_id}/links` | oui |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | oui |
| GET | `/api/forms/public/{token}` | non |
| POST | `/api/forms/public/{token}/submit` | optionnel |
| GET | `/api/forms/{form_id}/responses` | oui |
| GET | `/api/forms/{form_id}/responses/export/csv` | oui |
| PUT | `/api/forms/responses/{response_id}` | oui |
| POST | `/api/forms/responses/{response_id}/approve` | oui |
| POST | `/api/forms/responses/{response_id}/reject` | oui |

## `jury_votes` → `/api/jury-votes`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/jury-votes` | oui |
| GET | `/api/jury-votes/{festival_id}` | optionnel |
| GET | `/api/jury-votes/aggregate/{festival_id}` | non |
| GET | `/api/jury-votes/by-juror/{festival_id}/{juror_id}` | oui |
| GET | `/api/jury-votes/anonymous/{festival_id}` | oui |

## `keys` → `/api/users`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | oui |
| GET | `/api/users/{user_id}/public-key` | oui |

## `location_images` → `/api/locations/{location_id}/images`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images` | non |
| POST | `/api/locations/{location_id}/images/upload` | oui |
| POST | `/api/locations/{location_id}/images/url` | oui |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | oui |

## `location_relations` → `/api/locations/{location_id}/relations`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations` | non |
| POST | `/api/locations/{location_id}/relations` | oui |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | oui |
| POST | `/api/locations/{location_id}/relations/suggest` | oui |

## `location_tags` → `/api/locations/{location_id}/tags`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags` | non |
| POST | `/api/locations/{location_id}/tags` | oui |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | oui |

## `locations` → `/api/locations`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations` | non |
| POST | `/api/locations` | oui |
| GET | `/api/locations/{location_id}` | non |
| PUT | `/api/locations/{location_id}` | oui |
| PUT | `/api/locations/{location_id}/badge` | oui |
| DELETE | `/api/locations/{location_id}` | oui |

## `notifications` → `/api/notifications`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/notifications` | oui |
| GET | `/api/notifications/unread-count` | oui |
| PUT | `/api/notifications/{notification_id}/read` | oui |
| PUT | `/api/notifications/read-all` | oui |
| DELETE | `/api/notifications/{notification_id}` | oui |

## `participant_tags` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/participant-tags` | non |
| POST | `/api/participant-tags` | oui (admin) |
| GET | `/api/participant-tags/{tag_id}` | non |
| PUT | `/api/participant-tags/{tag_id}` | oui (admin) |
| DELETE | `/api/participant-tags/{tag_id}` | oui (admin) |
| GET | `/api/festivals/{festival_id}/participant-tags` | non |
| POST | `/api/festivals/{festival_id}/participant-tags` | oui |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | oui |

## `payments` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | oui |
| GET | `/api/payments` | oui |
| GET | `/api/payments/{payment_id}` | oui |
| POST | `/api/payments/{payment_id}/confirm` | oui |
| POST | `/api/payments/{payment_id}/refund` | oui |
| POST | `/api/payments/webhook/mock` | non |
| POST | `/api/payments/webhook/stripe` | non |
| POST | `/api/payments/webhook/redsys` | non |

## `posts` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/posts` | optionnel |
| POST | `/api/users/{user_id}/posts` | oui |
| GET | `/api/festivals/{festival_id}/posts` | optionnel |
| POST | `/api/festivals/{festival_id}/posts` | oui |
| GET | `/api/posts/{post_id}` | optionnel |
| PUT | `/api/posts/{post_id}` | oui |
| DELETE | `/api/posts/{post_id}` | oui |
| GET | `/api/posts/{post_id}/replies` | optionnel |
| POST | `/api/posts/{post_id}/replies` | oui |
| POST | `/api/posts/{post_id}/moderate` | oui |

## `registration_forms` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms` | oui |
| POST | `/api/festivals/{festival_id}/registration-forms` | oui |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | oui |
| GET | `/api/registration-forms/{form_id}` | oui |
| PUT | `/api/registration-forms/{form_id}` | oui |
| DELETE | `/api/registration-forms/{form_id}` | oui |
| GET | `/api/registration-forms/{form_id}/registrations` | oui |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | oui |
| GET | `/api/public/forms/{token}` | non |
| POST | `/api/public/forms/{token}/register` | optionnel |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | oui |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | oui |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | oui |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | oui |
| GET | `/api/registration-forms/{form_id}/links` | oui |
| POST | `/api/registration-forms/{form_id}/links` | oui |
| DELETE | `/api/registration-form-links/{link_id}` | oui |
| POST | `/api/registration-form-links/{link_id}/regenerate` | oui |
| GET | `/api/festivals/{festival_id}/registrations` | oui |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | oui |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | oui |
| GET | `/api/users/{user_id}/registrations` | oui |
| PUT | `/api/registrations/{registration_id}` | oui |
| POST | `/api/registrations/{registration_id}/approve` | oui |
| POST | `/api/registrations/{registration_id}/reject` | oui |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | oui |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | oui |
| DELETE | `/api/registrations/{registration_id}` | oui |
| POST | `/api/registration-forms/{form_id}/sections` | oui |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | oui |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | oui |

## `role_groups` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/role-groups` | non |
| POST | `/api/role-groups` | oui (admin) |
| GET | `/api/role-groups/{group_id}` | non |
| PUT | `/api/role-groups/{group_id}` | oui (admin) |
| DELETE | `/api/role-groups/{group_id}` | oui (admin) |
| GET | `/api/role-groups/{group_id}/memberships` | non |
| POST | `/api/role-groups/{group_id}/memberships` | oui (admin) |
| PUT | `/api/role-group-memberships/{membership_id}` | oui (admin) |
| DELETE | `/api/role-group-memberships/{membership_id}` | oui (admin) |

## `roles` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/roles` | oui |
| POST | `/api/roles` | oui (admin) |
| GET | `/api/roles/hierarchy` | optionnel |
| GET | `/api/roles/{role_id}` | optionnel |
| PUT | `/api/roles/{role_id}` | oui (admin) |
| DELETE | `/api/roles/{role_id}` | oui (admin) |
| GET | `/api/festivals/{festival_id}/roles` | optionnel |
| POST | `/api/festivals/{festival_id}/roles` | oui |
| POST | `/api/festivals/{festival_id}/roles/initialize` | oui (admin) |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | oui |
| GET | `/api/roles/{role_id}/dependencies` | optionnel |
| POST | `/api/role-dependencies` | oui (admin) |
| DELETE | `/api/role-dependencies/{dependency_id}` | oui (admin) |
| GET | `/api/roles/{role_id}/conflicts` | optionnel |
| POST | `/api/role-conflicts` | oui (admin) |
| DELETE | `/api/role-conflicts/{conflict_id}` | oui (admin) |
| GET | `/api/roles/{role_id}/check-conflicts` | optionnel |

## `search` → `/api/search`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/search` | oui |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations` | non |
| POST | `/api/shortfilms/{shortfilm_id}/locations` | oui |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | oui |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | oui |

## `shortfilms` → `/api/shortfilms`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/shortfilms` (obsolète) | non |
| POST | `/api/shortfilms` (obsolète) | oui |
| GET | `/api/shortfilms/{shortfilm_id}` (obsolète) | non |
| PUT | `/api/shortfilms/{shortfilm_id}` (obsolète) | oui |
| DELETE | `/api/shortfilms/{shortfilm_id}` (obsolète) | oui |

## `uploads` → `/api/uploads`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | oui |
| POST | `/api/uploads/thumbnail` | oui |
| POST | `/api/uploads/video` | oui |
| POST | `/api/uploads/document` | oui |
| POST | `/api/uploads/chat-image` | oui |

## `user_aliases` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases` | non |
| POST | `/api/users/{user_id}/aliases` | oui |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | oui |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | oui |

## `user_blocks` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/blocks` | oui |
| DELETE | `/api/users/{user_id}/blocks/{blocked_id}` | oui |
| GET | `/api/users/{user_id}/blocks` | oui |
| GET | `/api/users/{user_id}/blocks/{blocked_id}/status` | oui |

## `user_festival` → `/api/festivals`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | oui |
| DELETE | `/api/festivals/{festival_id}/leave` | oui |
| GET | `/api/festivals/{festival_id}/members` | oui |
| GET | `/api/festivals/user/{user_id}/festivals` | oui |

## `user_follows` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/follow` | oui |
| DELETE | `/api/users/{user_id}/follow` | oui |
| GET | `/api/users/{user_id}/follow/status` | oui |
| GET | `/api/users/{user_id}/followers` | oui |
| GET | `/api/users/{user_id}/following` | oui |

## `user_roles` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles` | oui |
| POST | `/api/users/{user_id}/roles` | oui |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | oui |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | oui |
| GET | `/api/users/{user_id}/participant-tags` | oui |
| PATCH | `/api/users/{user_id}/participant-tags/{upt_id}/verify` | oui |
| POST | `/api/users/{user_id}/participant-tags/{upt_id}/request-verification` | oui |
| POST | `/api/users/{user_id}/participant-tags` | oui |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | oui |

## `users` → `/api/users`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/users` | oui |
| GET | `/api/users/public` | non |
| GET | `/api/users/me` | oui |
| GET | `/api/users/me/export` | oui |
| DELETE | `/api/users/me` | oui |
| POST | `/api/users` | oui |
| GET | `/api/users/{user_id}` | oui |
| GET | `/api/users/{user_id}/public` | non |
| PUT | `/api/users/{user_id}` | oui |
| DELETE | `/api/users/{user_id}` | oui |

## `validation_rules` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/validation-rules` | non |
| POST | `/api/validation-rules` | oui (admin) |
| GET | `/api/validation-rules/{rule_id}` | non |
| PUT | `/api/validation-rules/{rule_id}` | oui (admin) |
| DELETE | `/api/validation-rules/{rule_id}` | oui (admin) |
| GET | `/api/validation-rule-groups` | non |
| POST | `/api/validation-rule-groups` | oui (admin) |
