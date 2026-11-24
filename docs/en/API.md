# API — endpoint reference

[ES](../es/API.md) · [EN](API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](../oc/API.md)

Generated from `app/routers/*.py` (each `APIRouter` prefix plus the one in `app/main.py`) and each endpoint's dependencies.
Interactive detail: `/docs` (Swagger) and `/redoc` with the backend running.

All uploads return a relative `/uploads/<folder>/<file>` path, never an absolute URL. The client resolves it with `resolveMediaUrl()`, which prepends the active server; `http(s)` URLs are left unchanged. Media fields (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) accept both formats.

## `admin` → `/api/admin`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/admin/stats` | yes (admin) |
| GET | `/api/admin/tables` | yes (admin) |
| GET | `/api/admin/audit-log` | yes (admin) |
| POST | `/api/admin/reset` | yes (admin) |

## `auth` → `/api/users`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/users/login` | no |

## `auth_sessions` → `/api/auth`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | no |
| GET | `/api/auth/sessions` | yes |
| DELETE | `/api/auth/sessions/{session_id}` | yes |
| POST | `/api/auth/sessions/revoke-all` | yes |

## `badges` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/badges/status` | no |
| PUT | `/api/badges/settings` | yes (admin) |
| GET | `/api/badges` | optional |
| POST | `/api/badges` | yes (admin) |
| GET | `/api/badges/{badge_id}` | optional |
| PUT | `/api/badges/{badge_id}` | yes (admin) |
| DELETE | `/api/badges/{badge_id}` | yes (admin) |
| POST | `/api/badges/{badge_id}/image` | yes (admin) |
| GET | `/api/badges/{badge_id}/eligibility` | optional |
| POST | `/api/badges/{badge_id}/assign` | yes (admin) |
| DELETE | `/api/badge-assignments/{assignment_id}` | yes |
| GET | `/api/users/{user_id}/badges` | optional |
| GET | `/api/festivals/{festival_id}/badges` | optional |

## `calendar` → `/api/calendar`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | optional |
| GET | `/api/calendar/agenda/export/ics` | optional |
| GET | `/api/calendar/settings` | no |
| GET | `/api/calendar/admin/settings` | yes (admin) |
| PUT | `/api/calendar/admin/settings` | yes (admin) |
| POST | `/api/calendar/dav/token` | yes |
| GET | `/api/calendar/dav/token` | yes |
| DELETE | `/api/calendar/dav/token` | yes |

## `channels` → `/api/channels`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/channels` | yes |
| GET | `/api/channels` | yes |
| GET | `/api/channels/public` | yes |
| GET | `/api/channels/{channel_id}` | yes |
| PUT | `/api/channels/{channel_id}` | yes |
| DELETE | `/api/channels/{channel_id}` | yes |
| POST | `/api/channels/{channel_id}/members` | yes |
| GET | `/api/channels/{channel_id}/members` | yes |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | yes |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | yes |

## `chat` → `/api/chat`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/chat/messages` | yes |
| POST | `/api/chat/messages` | yes |
| PUT | `/api/chat/messages/{message_id}/read` | yes |
| DELETE | `/api/chat/messages/{message_id}` | yes |
| GET | `/api/chat/groups` | yes |
| POST | `/api/chat/groups` | yes |
| GET | `/api/chat/groups/{group_id}` | yes |
| DELETE | `/api/chat/groups/{group_id}` | yes |
| GET | `/api/chat/groups/{group_id}/members` | yes |
| POST | `/api/chat/groups/{group_id}/members` | yes |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | yes |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | yes |
| WEBSOCKET | `/api/chat/ws` | token (query, required) |

## `chat_moderation` → `/api/chat/moderation`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/chat/moderation/messages/{message_id}/report` | yes |
| PATCH | `/api/chat/moderation/messages/{message_id}/moderate` | yes |
| GET | `/api/chat/moderation/reports` | yes (admin) |
| POST | `/api/chat/moderation/mutes` | yes |
| GET | `/api/chat/moderation/mutes` | yes (admin) |
| GET | `/api/chat/moderation/limits` | yes (admin) |

## `committees` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees` | optional |
| POST | `/api/festivals/{festival_id}/committees` | yes |
| GET | `/api/committees/{committee_id}` | optional |
| PUT | `/api/committees/{committee_id}` | yes |
| DELETE | `/api/committees/{committee_id}` | yes |
| GET | `/api/committees/{committee_id}/members` | optional |
| POST | `/api/committees/{committee_id}/members` | yes |
| PUT | `/api/committee-members/{member_id}` | yes |
| DELETE | `/api/committee-members/{member_id}` | yes |

## `dav` → `/dav`

| Method | Path | Auth |
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

| Method | Path | Auth |
|---|---|---|
| GET | `/api/delegations` | optional |
| POST | `/api/delegations` | yes |
| PUT | `/api/delegations/{delegation_id}` | yes |
| POST | `/api/delegations/{delegation_id}/revoke` | yes |
| GET | `/api/users/{user_id}/active-delegations` | optional |
| GET | `/api/role-transitions` | yes |
| POST | `/api/role-transitions` | yes |
| GET | `/api/users/{user_id}/role-transitions` | yes |
| GET | `/api/users/{user_id}/role-check` | yes |

## `events` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events` | no |
| GET | `/api/festivals/{festival_id}/events/export/ics` | yes |
| POST | `/api/festivals/{festival_id}/events` | yes |
| GET | `/api/events/{event_id}` | no |
| PUT | `/api/events/{event_id}` | yes |
| DELETE | `/api/events/{event_id}` | yes |
| GET | `/api/festivals/{festival_id}/events/programacion` | no |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | yes |
| GET | `/api/events/{event_id}/screenings` | no |
| PATCH | `/api/events/{event_id}/screenings/{shortfilm_id}` | yes |
| PUT | `/api/events/{event_id}/screenings/{shortfilm_id}/notes` | yes |
| PUT | `/api/events/{event_id}/screenings` | yes |
| GET | `/api/festivals/{festival_id}/screenings` | no |
| GET | `/api/events/{event_id}/occupancy` | no |
| GET | `/api/events/{event_id}/ticket-types` | no |
| POST | `/api/events/{event_id}/ticket-types` | yes |
| PUT | `/api/ticket-types/{tt_id}` | yes |
| DELETE | `/api/ticket-types/{tt_id}` | yes |
| GET | `/api/events/{event_id}/seats` | no |
| POST | `/api/events/{event_id}/seats/bulk` | yes |
| GET | `/api/events/{event_id}/seats/sections` | no |
| GET | `/api/events/{event_id}/seats/counts` | no |
| PUT | `/api/seats/{seat_id}` | yes |
| POST | `/api/seats/{seat_id}/release` | yes |
| DELETE | `/api/seats/{seat_id}` | yes |
| GET | `/api/events/{event_id}/reservations` | yes |
| POST | `/api/events/{event_id}/reservations` | yes |
| PUT | `/api/reservations/{reservation_id}` | yes |
| POST | `/api/reservations/{reservation_id}/confirm` | yes |
| POST | `/api/reservations/{reservation_id}/cancel` | yes |
| DELETE | `/api/reservations/{reservation_id}` | yes |
| GET | `/api/events/{event_id}/attendees` | yes |
| POST | `/api/events/{event_id}/attendees` | yes |
| GET | `/api/attendees/{attendee_id}` | no |
| PUT | `/api/attendees/{attendee_id}` | yes |
| POST | `/api/attendees/{attendee_id}/check-in` | yes |
| GET | `/api/events/{event_id}/attendees/counts` | no |
| GET | `/api/events/{event_id}/attendees/export/csv` | yes |
| DELETE | `/api/attendees/{attendee_id}` | yes |
| POST | `/api/events/{event_id}/assign-vip` | yes |
| GET | `/api/users/me/events` | yes |
| GET | `/api/users/me/events/{event_id}/reservation` | yes |
| GET | `/api/festivals/{festival_id}/awards` | no |
| POST | `/api/festivals/{festival_id}/awards` | yes |
| PUT | `/api/awards/{award_id}` | yes |
| DELETE | `/api/awards/{award_id}` | yes |
| PATCH | `/api/awards/{award_id}/recipient-verification` | yes |
| GET | `/api/users/{user_id}/awards` | no |
| GET | `/api/public/profile/{token}` | no |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | no |

## `federation` → `/api/federation`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/federation/nodes` | yes (admin) |
| POST | `/api/federation/nodes` | yes (admin) |
| GET | `/api/federation/manifest` | no |
| PATCH | `/api/federation/reports/{report_id}` | no |
| GET | `/api/federation/directory` | no |
| POST | `/api/federation/reports` | no |
| GET | `/api/federation/reports` | no |
| DELETE | `/api/federation/users/{user_ref}` | federation JWT |
| GET | `/api/federation/export/{user_ref}` | no |
| GET | `/api/federation/health` (deprecated) | no |
| POST | `/api/federation/verify` | no |
| POST | `/api/federation/publish` | federation JWT |
| POST | `/api/federation/recover` | no |
| POST | `/api/federation/bridge` | federation JWT |
| GET | `/api/federation/aggregate-nodes` (deprecated) | no |
| GET | `/api/federation/keys` (deprecated) | no |
| GET | `/api/federation/events` (deprecated) | no |
| GET | `/api/federation/capabilities` (deprecated) | no |
| GET | `/api/federation/status` (deprecated) | no |
| GET | `/api/federation/info` (deprecated) | no |
| GET | `/api/federation/ping` (deprecated) | no |
| POST | `/api/federation/echo` | no |
| GET | `/api/federation/time` | no |
| GET | `/api/federation/version` (deprecated) | no |
| POST | `/api/federation/checksum` | no |
| POST | `/api/federation/notify` (deprecated) | no |
| POST | `/api/federation/subscribe` (deprecated) | no |
| POST | `/api/federation/unsubscribe` (deprecated) | no |
| GET | `/api/federation/discover` (deprecated) | no |
| POST | `/api/federation/register` | no |
| POST | `/api/federation/unregister` | no |
| POST | `/api/federation/sync` | no |
| POST | `/api/federation/reconcile` | no |
| GET | `/api/federation/heartbeat` (deprecated) | no |
| GET | `/api/federation/whoami` | federation JWT |
| GET | `/api/federation/peers` (deprecated) | no |
| GET | `/api/federation/links` (deprecated) | no |
| GET | `/api/federation/stats` (deprecated) | no |
| GET | `/api/federation/config` (deprecated) | no |
| GET | `/api/federation/status-check` (deprecated) | no |
| GET | `/api/federation/ready` (deprecated) | no |
| GET | `/api/federation/live` (deprecated) | no |
| GET | `/api/federation/alive` (deprecated) | no |
| GET | `/api/federation/down` (deprecated) | no |
| GET | `/api/federation/maintenance` (deprecated) | no |
| GET | `/api/federation/readyz` (deprecated) | no |
| GET | `/api/federation/livez` (deprecated) | no |
| GET | `/api/federation/healthz` (deprecated) | no |
| GET | `/api/federation/ok` (deprecated) | no |
| GET | `/api/federation/yes` (deprecated) | no |
| GET | `/api/federation/no` (deprecated) | no |
| GET | `/api/federation/maybe` (deprecated) | no |
| GET | `/api/federation/always` (deprecated) | no |
| GET | `/api/federation/never` (deprecated) | no |
| POST | `/api/federation/import` | no |
| POST | `/api/federation/dedup` | no |
| POST | `/api/federation/retry` | no |
| POST | `/api/federation/recover-node` | no |
| GET | `/api/federation/integrity` | no |
| GET | `/api/federation/metrics` | no |
| GET | `/api/federation/users/{ref}` | no |
| GET | `/api/federation/.well-known/webfinger` | no |
| POST | `/api/federation/peers/verify` | no |
| POST | `/api/federation/peers/{domain}/revoke` | yes (admin) |
| GET | `/api/federation/.well-known/jwks.json` | no |
| POST | `/api/federation/token` | no |

## `federation_chat_bridge` → `/api/federation`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/federation/chat/bridge/inbound` | no |
| POST | `/api/federation/chat/bridge/outbound` | no |
| GET | `/api/federation/chat/bridge/config` | no |
| GET | `/api/federation/chat/messages` | no |

## `federation_events` → `/api/federation/events`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/federation/events/stream` | token (query, required) |
| POST | `/api/federation/events/publish` | yes (admin) |
| GET | `/api/federation/events/retry-queue` | yes (admin) |

## `federation_portability` → `/api/federation/portability`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/federation/portability/bundles` | yes |
| POST | `/api/federation/portability/imports` | yes |
| POST | `/api/federation/portability/festivals/{festival_id}/migrate` | yes (admin) |
| POST | `/api/federation/portability/users/{user_ref}/migrate` | yes (admin) |
| GET | `/api/federation/portability/redirects/{old_ref}` | yes |

## `federation_resilience` → `/api/federation/resilience`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/federation/resilience/health` | no |
| GET | `/api/federation/resilience/heartbeat` | no |
| GET | `/api/federation/resilience/metrics` | no |
| POST | `/api/federation/resilience/keys/revoke` | yes (admin) |
| GET | `/api/federation/resilience/keys/revoked` | no |
| GET | `/api/federation/resilience/incident-plan` | no |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks` | no |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | no |
| POST | `/api/festivals/{festival_id}/rulebooks` | yes |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | yes |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | yes |

## `festivals` → `/api/festivals`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals` | no |
| POST | `/api/festivals` | yes |
| GET | `/api/festivals/{festival_id}` | no |
| GET | `/api/festivals/{festival_id}/shortfilms` | no |
| POST | `/api/festivals/{festival_id}/shortfilms` | yes |
| GET | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | no |
| PUT | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | yes |
| PUT | `/api/festivals/{festival_id}` | yes |
| DELETE | `/api/festivals/{festival_id}` | yes |
| POST | `/api/festivals/{festival_id}/images` | yes |
| DELETE | `/api/festivals/{festival_id}/images` | yes |
| GET | `/api/festivals/{festival_id}/locations` | no |
| POST | `/api/festivals/{festival_id}/locations` | yes |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | yes |

## `form_definitions` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/forms` | yes |
| POST | `/api/forms` | yes |
| GET | `/api/forms/{form_id}` | yes |
| PUT | `/api/forms/{form_id}` | yes |
| DELETE | `/api/forms/{form_id}` | yes |
| POST | `/api/forms/{form_id}/clone` | yes |
| POST | `/api/forms/{form_id}/pages` | yes |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | yes |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | yes |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields` | yes |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | yes |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | yes |
| GET | `/api/forms/{form_id}/links` | yes |
| POST | `/api/forms/{form_id}/links` | yes |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | yes |
| GET | `/api/forms/public/{token}` | no |
| POST | `/api/forms/public/{token}/submit` | optional |
| GET | `/api/forms/{form_id}/responses` | yes |
| GET | `/api/forms/{form_id}/responses/export/csv` | yes |
| PUT | `/api/forms/responses/{response_id}` | yes |
| POST | `/api/forms/responses/{response_id}/approve` | yes |
| POST | `/api/forms/responses/{response_id}/reject` | yes |

## `jury_votes` → `/api/jury-votes`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/jury-votes` | yes |
| GET | `/api/jury-votes/{festival_id}` | optional |
| GET | `/api/jury-votes/aggregate/{festival_id}` | no |
| GET | `/api/jury-votes/by-juror/{festival_id}/{juror_id}` | yes |
| GET | `/api/jury-votes/anonymous/{festival_id}` | yes |

## `keys` → `/api/users`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | yes |
| GET | `/api/users/{user_id}/public-key` | yes |

## `location_images` → `/api/locations/{location_id}/images`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images` | no |
| POST | `/api/locations/{location_id}/images/upload` | yes |
| POST | `/api/locations/{location_id}/images/url` | yes |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | yes |

## `location_relations` → `/api/locations/{location_id}/relations`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations` | no |
| POST | `/api/locations/{location_id}/relations` | yes |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | yes |
| POST | `/api/locations/{location_id}/relations/suggest` | yes |

## `location_tags` → `/api/locations/{location_id}/tags`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags` | no |
| POST | `/api/locations/{location_id}/tags` | yes |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | yes |

## `locations` → `/api/locations`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations` | no |
| POST | `/api/locations` | yes |
| GET | `/api/locations/{location_id}` | no |
| PUT | `/api/locations/{location_id}` | yes |
| PUT | `/api/locations/{location_id}/badge` | yes |
| DELETE | `/api/locations/{location_id}` | yes |

## `notifications` → `/api/notifications`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/notifications` | yes |
| GET | `/api/notifications/unread-count` | yes |
| PUT | `/api/notifications/{notification_id}/read` | yes |
| PUT | `/api/notifications/read-all` | yes |
| DELETE | `/api/notifications/{notification_id}` | yes |

## `participant_tags` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/participant-tags` | no |
| POST | `/api/participant-tags` | yes (admin) |
| GET | `/api/participant-tags/{tag_id}` | no |
| PUT | `/api/participant-tags/{tag_id}` | yes (admin) |
| DELETE | `/api/participant-tags/{tag_id}` | yes (admin) |
| GET | `/api/festivals/{festival_id}/participant-tags` | no |
| POST | `/api/festivals/{festival_id}/participant-tags` | yes |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | yes |

## `payments` → `/api`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | yes |
| GET | `/api/payments` | yes |
| GET | `/api/payments/{payment_id}` | yes |
| POST | `/api/payments/{payment_id}/confirm` | yes |
| POST | `/api/payments/{payment_id}/refund` | yes |
| POST | `/api/payments/webhook/mock` | no |
| POST | `/api/payments/webhook/stripe` | no |
| POST | `/api/payments/webhook/redsys` | no |

## `posts` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/posts` | optional |
| POST | `/api/users/{user_id}/posts` | yes |
| GET | `/api/festivals/{festival_id}/posts` | optional |
| POST | `/api/festivals/{festival_id}/posts` | yes |
| GET | `/api/posts/{post_id}` | optional |
| PUT | `/api/posts/{post_id}` | yes |
| DELETE | `/api/posts/{post_id}` | yes |
| GET | `/api/posts/{post_id}/replies` | optional |
| POST | `/api/posts/{post_id}/replies` | yes |
| POST | `/api/posts/{post_id}/moderate` | yes |

## `registration_forms` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms` | yes |
| POST | `/api/festivals/{festival_id}/registration-forms` | yes |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | yes |
| GET | `/api/registration-forms/{form_id}` | yes |
| PUT | `/api/registration-forms/{form_id}` | yes |
| DELETE | `/api/registration-forms/{form_id}` | yes |
| GET | `/api/registration-forms/{form_id}/registrations` | yes |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | yes |
| GET | `/api/public/forms/{token}` | no |
| POST | `/api/public/forms/{token}/register` | optional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | yes |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | yes |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | yes |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | yes |
| GET | `/api/registration-forms/{form_id}/links` | yes |
| POST | `/api/registration-forms/{form_id}/links` | yes |
| DELETE | `/api/registration-form-links/{link_id}` | yes |
| POST | `/api/registration-form-links/{link_id}/regenerate` | yes |
| GET | `/api/festivals/{festival_id}/registrations` | yes |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | yes |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | yes |
| GET | `/api/users/{user_id}/registrations` | yes |
| PUT | `/api/registrations/{registration_id}` | yes |
| POST | `/api/registrations/{registration_id}/approve` | yes |
| POST | `/api/registrations/{registration_id}/reject` | yes |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | yes |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | yes |
| DELETE | `/api/registrations/{registration_id}` | yes |
| POST | `/api/registration-forms/{form_id}/sections` | yes |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | yes |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | yes |

## `role_groups` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/role-groups` | no |
| POST | `/api/role-groups` | yes (admin) |
| GET | `/api/role-groups/{group_id}` | no |
| PUT | `/api/role-groups/{group_id}` | yes (admin) |
| DELETE | `/api/role-groups/{group_id}` | yes (admin) |
| GET | `/api/role-groups/{group_id}/memberships` | no |
| POST | `/api/role-groups/{group_id}/memberships` | yes (admin) |
| PUT | `/api/role-group-memberships/{membership_id}` | yes (admin) |
| DELETE | `/api/role-group-memberships/{membership_id}` | yes (admin) |

## `roles` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/roles` | yes |
| POST | `/api/roles` | yes (admin) |
| GET | `/api/roles/hierarchy` | optional |
| GET | `/api/roles/{role_id}` | optional |
| PUT | `/api/roles/{role_id}` | yes (admin) |
| DELETE | `/api/roles/{role_id}` | yes (admin) |
| GET | `/api/festivals/{festival_id}/roles` | optional |
| POST | `/api/festivals/{festival_id}/roles` | yes |
| POST | `/api/festivals/{festival_id}/roles/initialize` | yes (admin) |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | yes |
| GET | `/api/roles/{role_id}/dependencies` | optional |
| POST | `/api/role-dependencies` | yes (admin) |
| DELETE | `/api/role-dependencies/{dependency_id}` | yes (admin) |
| GET | `/api/roles/{role_id}/conflicts` | optional |
| POST | `/api/role-conflicts` | yes (admin) |
| DELETE | `/api/role-conflicts/{conflict_id}` | yes (admin) |
| GET | `/api/roles/{role_id}/check-conflicts` | optional |

## `search` → `/api/search`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/search` | yes |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations` | no |
| POST | `/api/shortfilms/{shortfilm_id}/locations` | yes |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | yes |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | yes |

## `shortfilms` → `/api/shortfilms`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/shortfilms` (deprecated) | no |
| POST | `/api/shortfilms` (deprecated) | yes |
| GET | `/api/shortfilms/{shortfilm_id}` (deprecated) | no |
| PUT | `/api/shortfilms/{shortfilm_id}` (deprecated) | yes |
| DELETE | `/api/shortfilms/{shortfilm_id}` (deprecated) | yes |

## `uploads` → `/api/uploads`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | yes |
| POST | `/api/uploads/thumbnail` | yes |
| POST | `/api/uploads/video` | yes |
| POST | `/api/uploads/document` | yes |
| POST | `/api/uploads/chat-image` | yes |

## `user_aliases` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases` | no |
| POST | `/api/users/{user_id}/aliases` | yes |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | yes |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | yes |

## `user_blocks` → `/api`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/blocks` | yes |
| DELETE | `/api/users/{user_id}/blocks/{blocked_id}` | yes |
| GET | `/api/users/{user_id}/blocks` | yes |
| GET | `/api/users/{user_id}/blocks/{blocked_id}/status` | yes |

## `user_festival` → `/api/festivals`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | yes |
| DELETE | `/api/festivals/{festival_id}/leave` | yes |
| GET | `/api/festivals/{festival_id}/members` | yes |
| GET | `/api/festivals/user/{user_id}/festivals` | yes |

## `user_follows` → `/api`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/follow` | yes |
| DELETE | `/api/users/{user_id}/follow` | yes |
| GET | `/api/users/{user_id}/follow/status` | yes |
| GET | `/api/users/{user_id}/followers` | yes |
| GET | `/api/users/{user_id}/following` | yes |

## `user_roles` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles` | yes |
| POST | `/api/users/{user_id}/roles` | yes |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | yes |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | yes |
| GET | `/api/users/{user_id}/participant-tags` | yes |
| PATCH | `/api/users/{user_id}/participant-tags/{upt_id}/verify` | yes |
| POST | `/api/users/{user_id}/participant-tags/{upt_id}/request-verification` | yes |
| POST | `/api/users/{user_id}/participant-tags` | yes |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | yes |

## `users` → `/api/users`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/users` | yes |
| GET | `/api/users/public` | no |
| GET | `/api/users/me` | yes |
| GET | `/api/users/me/export` | yes |
| DELETE | `/api/users/me` | yes |
| POST | `/api/users` | yes |
| GET | `/api/users/{user_id}` | yes |
| GET | `/api/users/{user_id}/public` | no |
| PUT | `/api/users/{user_id}` | yes |
| DELETE | `/api/users/{user_id}` | yes |

## `validation_rules` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/validation-rules` | no |
| POST | `/api/validation-rules` | yes (admin) |
| GET | `/api/validation-rules/{rule_id}` | no |
| PUT | `/api/validation-rules/{rule_id}` | yes (admin) |
| DELETE | `/api/validation-rules/{rule_id}` | yes (admin) |
| GET | `/api/validation-rule-groups` | no |
| POST | `/api/validation-rule-groups` | yes (admin) |
