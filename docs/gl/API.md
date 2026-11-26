# API — referencia de endpoints

[ES](../es/API.md) · [EN](../en/API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](API.md) · [OC](../oc/API.md)

Xerado desde `app/routers/*.py` (prefixo de cada `APIRouter` máis o de `app/main.py`) e das dependencias de cada endpoint.
Detalle interactivo: `/docs` (Swagger) e `/redoc` co backend en marcha.

Todas as subidas devolven unha ruta relativa `/uploads/<carpeta>/<ficheiro>`, nunca unha URL absoluta. O cliente résolvea con `resolveMediaUrl()`, que antepón o servidor activo; as URL `http(s)` déixanse intactas. Os campos de medios (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) aceptan ambos formatos.

## `admin` → `/api/admin`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/admin/stats` | si (admin) |
| GET | `/api/admin/tables` | si (admin) |
| GET | `/api/admin/audit-log` | si (admin) |
| POST | `/api/admin/reset` | si (admin) |

## `auth` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/login` | non |

## `auth_sessions` → `/api/auth`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | non |
| GET | `/api/auth/sessions` | si |
| DELETE | `/api/auth/sessions/{session_id}` | si |
| POST | `/api/auth/sessions/revoke-all` | si |

## `badges` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/badges/status` | non |
| PUT | `/api/badges/settings` | si (admin) |
| GET | `/api/badges` | opcional |
| POST | `/api/badges` | si (admin) |
| GET | `/api/badges/{badge_id}` | opcional |
| PUT | `/api/badges/{badge_id}` | si (admin) |
| DELETE | `/api/badges/{badge_id}` | si (admin) |
| POST | `/api/badges/{badge_id}/image` | si (admin) |
| GET | `/api/badges/{badge_id}/eligibility` | opcional |
| POST | `/api/badges/{badge_id}/assign` | si (admin) |
| DELETE | `/api/badge-assignments/{assignment_id}` | si |
| GET | `/api/users/{user_id}/badges` | opcional |
| GET | `/api/festivals/{festival_id}/badges` | opcional |

## `calendar` → `/api/calendar`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | opcional |
| GET | `/api/calendar/agenda/export/ics` | opcional |
| GET | `/api/calendar/settings` | non |
| GET | `/api/calendar/admin/settings` | si (admin) |
| PUT | `/api/calendar/admin/settings` | si (admin) |
| POST | `/api/calendar/dav/token` | si |
| GET | `/api/calendar/dav/token` | si |
| DELETE | `/api/calendar/dav/token` | si |

## `channels` → `/api/channels`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/channels` | si |
| GET | `/api/channels` | si |
| GET | `/api/channels/public` | si |
| GET | `/api/channels/{channel_id}` | si |
| PUT | `/api/channels/{channel_id}` | si |
| DELETE | `/api/channels/{channel_id}` | si |
| POST | `/api/channels/{channel_id}/members` | si |
| GET | `/api/channels/{channel_id}/members` | si |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | si |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | si |

## `chat` → `/api/chat`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/chat/messages` | si |
| POST | `/api/chat/messages` | si |
| PUT | `/api/chat/messages/{message_id}/read` | si |
| DELETE | `/api/chat/messages/{message_id}` | si |
| GET | `/api/chat/groups` | si |
| POST | `/api/chat/groups` | si |
| GET | `/api/chat/groups/{group_id}` | si |
| DELETE | `/api/chat/groups/{group_id}` | si |
| GET | `/api/chat/groups/{group_id}/members` | si |
| POST | `/api/chat/groups/{group_id}/members` | si |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | si |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | si |
| WEBSOCKET | `/api/chat/ws` | token (query, obrigatorio) |

## `chat_moderation` → `/api/chat/moderation`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/chat/moderation/messages/{message_id}/report` | si |
| PATCH | `/api/chat/moderation/messages/{message_id}/moderate` | si |
| GET | `/api/chat/moderation/reports` | si (admin) |
| POST | `/api/chat/moderation/mutes` | si |
| GET | `/api/chat/moderation/mutes` | si (admin) |
| GET | `/api/chat/moderation/limits` | si (admin) |

## `committees` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees` | opcional |
| POST | `/api/festivals/{festival_id}/committees` | si |
| GET | `/api/committees/{committee_id}` | opcional |
| PUT | `/api/committees/{committee_id}` | si |
| DELETE | `/api/committees/{committee_id}` | si |
| GET | `/api/committees/{committee_id}/members` | opcional |
| POST | `/api/committees/{committee_id}/members` | si |
| PUT | `/api/committee-members/{member_id}` | si |
| DELETE | `/api/committee-members/{member_id}` | si |

## `dav` → `/dav`

| Método | Ruta | Auth |
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

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/delegations` | opcional |
| POST | `/api/delegations` | si |
| PUT | `/api/delegations/{delegation_id}` | si |
| POST | `/api/delegations/{delegation_id}/revoke` | si |
| GET | `/api/users/{user_id}/active-delegations` | opcional |
| GET | `/api/role-transitions` | si |
| POST | `/api/role-transitions` | si |
| GET | `/api/users/{user_id}/role-transitions` | si |
| GET | `/api/users/{user_id}/role-check` | si |

## `events` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events` | non |
| GET | `/api/festivals/{festival_id}/events/export/ics` | si |
| POST | `/api/festivals/{festival_id}/events` | si |
| GET | `/api/events/{event_id}` | non |
| PUT | `/api/events/{event_id}` | si |
| DELETE | `/api/events/{event_id}` | si |
| GET | `/api/festivals/{festival_id}/events/programacion` | non |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | si |
| GET | `/api/events/{event_id}/screenings` | non |
| PATCH | `/api/events/{event_id}/screenings/{shortfilm_id}` | si |
| PUT | `/api/events/{event_id}/screenings/{shortfilm_id}/notes` | si |
| PUT | `/api/events/{event_id}/screenings` | si |
| GET | `/api/festivals/{festival_id}/screenings` | non |
| GET | `/api/events/{event_id}/occupancy` | non |
| GET | `/api/events/{event_id}/ticket-types` | non |
| POST | `/api/events/{event_id}/ticket-types` | si |
| PUT | `/api/ticket-types/{tt_id}` | si |
| DELETE | `/api/ticket-types/{tt_id}` | si |
| GET | `/api/events/{event_id}/seats` | non |
| POST | `/api/events/{event_id}/seats/bulk` | si |
| GET | `/api/events/{event_id}/seats/sections` | non |
| GET | `/api/events/{event_id}/seats/counts` | non |
| PUT | `/api/seats/{seat_id}` | si |
| POST | `/api/seats/{seat_id}/release` | si |
| DELETE | `/api/seats/{seat_id}` | si |
| GET | `/api/events/{event_id}/reservations` | si |
| POST | `/api/events/{event_id}/reservations` | si |
| PUT | `/api/reservations/{reservation_id}` | si |
| POST | `/api/reservations/{reservation_id}/confirm` | si |
| POST | `/api/reservations/{reservation_id}/cancel` | si |
| DELETE | `/api/reservations/{reservation_id}` | si |
| GET | `/api/events/{event_id}/attendees` | si |
| POST | `/api/events/{event_id}/attendees` | si |
| GET | `/api/attendees/{attendee_id}` | non |
| PUT | `/api/attendees/{attendee_id}` | si |
| POST | `/api/attendees/{attendee_id}/check-in` | si |
| GET | `/api/events/{event_id}/attendees/counts` | non |
| GET | `/api/events/{event_id}/attendees/export/csv` | si |
| DELETE | `/api/attendees/{attendee_id}` | si |
| POST | `/api/events/{event_id}/assign-vip` | si |
| GET | `/api/users/me/events` | si |
| GET | `/api/users/me/events/{event_id}/reservation` | si |
| GET | `/api/festivals/{festival_id}/awards` | non |
| POST | `/api/festivals/{festival_id}/awards` | si |
| PUT | `/api/awards/{award_id}` | si |
| DELETE | `/api/awards/{award_id}` | si |
| PATCH | `/api/awards/{award_id}/recipient-verification` | si |
| GET | `/api/users/{user_id}/awards` | non |
| GET | `/api/public/profile/{token}` | non |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | non |

## `federation` → `/api/federation`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/federation/nodes` | si (admin) |
| POST | `/api/federation/nodes` | si (admin) |
| GET | `/api/federation/manifest` | non |
| PATCH | `/api/federation/reports/{report_id}` | non |
| GET | `/api/federation/directory` | non |
| POST | `/api/federation/reports` | non |
| GET | `/api/federation/reports` | non |
| DELETE | `/api/federation/users/{user_ref}` | non |
| GET | `/api/federation/export/{user_ref}` | non |
| GET | `/api/federation/health` (obsoleto) | non |
| POST | `/api/federation/verify` | non |
| POST | `/api/federation/publish` | JWT de federación |
| POST | `/api/federation/recover` | non |
| POST | `/api/federation/bridge` | JWT de federación |
| GET | `/api/federation/aggregate-nodes` (obsoleto) | non |
| GET | `/api/federation/keys` (obsoleto) | non |
| GET | `/api/federation/events` (obsoleto) | non |
| GET | `/api/federation/capabilities` (obsoleto) | non |
| GET | `/api/federation/status` (obsoleto) | non |
| GET | `/api/federation/info` (obsoleto) | non |
| GET | `/api/federation/ping` (obsoleto) | non |
| POST | `/api/federation/echo` | non |
| GET | `/api/federation/time` | non |
| GET | `/api/federation/version` (obsoleto) | non |
| POST | `/api/federation/checksum` | non |
| POST | `/api/federation/notify` (obsoleto) | non |
| POST | `/api/federation/subscribe` (obsoleto) | non |
| POST | `/api/federation/unsubscribe` (obsoleto) | non |
| GET | `/api/federation/discover` (obsoleto) | non |
| POST | `/api/federation/register` | JWT de federación |
| POST | `/api/federation/unregister` | non |
| POST | `/api/federation/sync` | non |
| POST | `/api/federation/reconcile` | non |
| GET | `/api/federation/heartbeat` (obsoleto) | non |
| GET | `/api/federation/whoami` | JWT de federación |
| GET | `/api/federation/peers` (obsoleto) | non |
| GET | `/api/federation/links` (obsoleto) | non |
| GET | `/api/federation/stats` (obsoleto) | non |
| GET | `/api/federation/config` (obsoleto) | non |
| GET | `/api/federation/status-check` (obsoleto) | non |
| GET | `/api/federation/ready` (obsoleto) | non |
| GET | `/api/federation/live` (obsoleto) | non |
| GET | `/api/federation/alive` (obsoleto) | non |
| GET | `/api/federation/down` (obsoleto) | non |
| GET | `/api/federation/maintenance` (obsoleto) | non |
| GET | `/api/federation/readyz` (obsoleto) | non |
| GET | `/api/federation/livez` (obsoleto) | non |
| GET | `/api/federation/healthz` (obsoleto) | non |
| GET | `/api/federation/ok` (obsoleto) | non |
| GET | `/api/federation/yes` (obsoleto) | non |
| GET | `/api/federation/no` (obsoleto) | non |
| GET | `/api/federation/maybe` (obsoleto) | non |
| GET | `/api/federation/always` (obsoleto) | non |
| GET | `/api/federation/never` (obsoleto) | non |
| POST | `/api/federation/import` | non |
| POST | `/api/federation/dedup` | non |
| POST | `/api/federation/retry` | non |
| POST | `/api/federation/recover-node` | non |
| GET | `/api/federation/integrity` | non |
| GET | `/api/federation/metrics` | non |
| GET | `/api/federation/users/{ref}` | non |
| GET | `/api/federation/.well-known/webfinger` | non |
| POST | `/api/federation/peers/verify` | non |
| POST | `/api/federation/peers/{domain}/revoke` | si (admin) |
| GET | `/api/federation/.well-known/jwks.json` | non |
| POST | `/api/federation/token` | non |

## `federation_chat_bridge` → `/api/federation`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/federation/chat/bridge/inbound` | non |
| POST | `/api/federation/chat/bridge/outbound` | non |
| GET | `/api/federation/chat/bridge/config` | non |
| GET | `/api/federation/chat/messages` | non |

## `federation_events` → `/api/federation/events`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/federation/events/stream` | Bearer (cabeceira) ou token (consulta, obsoleto) |
| POST | `/api/federation/events/publish` | si (admin) |
| GET | `/api/federation/events/retry-queue` | si (admin) |

## `federation_portability` → `/api/federation/portability`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/federation/portability/bundles` | si |
| POST | `/api/federation/portability/imports` | si |
| POST | `/api/federation/portability/festivals/{festival_id}/migrate` | si (admin) |
| POST | `/api/federation/portability/users/{user_ref}/migrate` | si (admin) |
| GET | `/api/federation/portability/redirects/{old_ref}` | si |

## `federation_resilience` → `/api/federation/resilience`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/federation/resilience/health` | non |
| GET | `/api/federation/resilience/heartbeat` | non |
| GET | `/api/federation/resilience/metrics` | non |
| POST | `/api/federation/resilience/keys/revoke` | si (admin) |
| GET | `/api/federation/resilience/keys/revoked` | non |
| GET | `/api/federation/resilience/incident-plan` | non |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks` | non |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | non |
| POST | `/api/festivals/{festival_id}/rulebooks` | si |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | si |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | si |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | si |

## `festivals` → `/api/festivals`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals` | non |
| POST | `/api/festivals` | si |
| GET | `/api/festivals/{festival_id}` | non |
| GET | `/api/festivals/{festival_id}/shortfilms` | non |
| POST | `/api/festivals/{festival_id}/shortfilms` | si |
| GET | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | non |
| PUT | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | si |
| DELETE | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | si |
| PUT | `/api/festivals/{festival_id}` | si |
| DELETE | `/api/festivals/{festival_id}` | si |
| POST | `/api/festivals/{festival_id}/images` | si |
| DELETE | `/api/festivals/{festival_id}/images` | si |
| GET | `/api/festivals/{festival_id}/locations` | non |
| POST | `/api/festivals/{festival_id}/locations` | si |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | si |

## `form_definitions` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/forms` | si |
| POST | `/api/forms` | si |
| GET | `/api/forms/{form_id}` | si |
| PUT | `/api/forms/{form_id}` | si |
| DELETE | `/api/forms/{form_id}` | si |
| POST | `/api/forms/{form_id}/clone` | si |
| POST | `/api/forms/{form_id}/pages` | si |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | si |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | si |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields` | si |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | si |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | si |
| GET | `/api/forms/{form_id}/links` | si |
| POST | `/api/forms/{form_id}/links` | si |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | si |
| GET | `/api/forms/public/{token}` | non |
| POST | `/api/forms/public/{token}/submit` | opcional |
| GET | `/api/forms/{form_id}/responses` | si |
| GET | `/api/forms/{form_id}/responses/export/csv` | si |
| PUT | `/api/forms/responses/{response_id}` | si |
| POST | `/api/forms/responses/{response_id}/approve` | si |
| POST | `/api/forms/responses/{response_id}/reject` | si |

## `jury_votes` → `/api/jury-votes`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/jury-votes` | si |
| GET | `/api/jury-votes/{festival_id}` | opcional |
| GET | `/api/jury-votes/aggregate/{festival_id}` | non |
| GET | `/api/jury-votes/by-juror/{festival_id}/{juror_id}` | si |
| GET | `/api/jury-votes/anonymous/{festival_id}` | si |

## `keys` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | si |
| GET | `/api/users/{user_id}/public-key` | si |

## `location_images` → `/api/locations/{location_id}/images`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images` | non |
| POST | `/api/locations/{location_id}/images/upload` | si |
| POST | `/api/locations/{location_id}/images/url` | si |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | si |

## `location_relations` → `/api/locations/{location_id}/relations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations` | non |
| POST | `/api/locations/{location_id}/relations` | si |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | si |
| POST | `/api/locations/{location_id}/relations/suggest` | si |

## `location_tags` → `/api/locations/{location_id}/tags`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags` | non |
| POST | `/api/locations/{location_id}/tags` | si |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | si |

## `locations` → `/api/locations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations` | non |
| POST | `/api/locations` | si |
| GET | `/api/locations/{location_id}` | non |
| PUT | `/api/locations/{location_id}` | si |
| PUT | `/api/locations/{location_id}/badge` | si |
| DELETE | `/api/locations/{location_id}` | si |

## `notifications` → `/api/notifications`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/notifications` | si |
| GET | `/api/notifications/unread-count` | si |
| PUT | `/api/notifications/{notification_id}/read` | si |
| PUT | `/api/notifications/read-all` | si |
| DELETE | `/api/notifications/{notification_id}` | si |

## `participant_tags` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/participant-tags` | non |
| POST | `/api/participant-tags` | si (admin) |
| GET | `/api/participant-tags/{tag_id}` | non |
| PUT | `/api/participant-tags/{tag_id}` | si (admin) |
| DELETE | `/api/participant-tags/{tag_id}` | si (admin) |
| GET | `/api/festivals/{festival_id}/participant-tags` | non |
| POST | `/api/festivals/{festival_id}/participant-tags` | si |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | si |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | si |

## `payments` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | si |
| GET | `/api/payments` | si |
| GET | `/api/payments/{payment_id}` | si |
| POST | `/api/payments/{payment_id}/confirm` | si |
| POST | `/api/payments/{payment_id}/refund` | si |
| POST | `/api/payments/webhook/mock` | non |
| POST | `/api/payments/webhook/stripe` | non |
| POST | `/api/payments/webhook/redsys` | non |

## `posts` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/posts` | opcional |
| POST | `/api/users/{user_id}/posts` | si |
| GET | `/api/festivals/{festival_id}/posts` | opcional |
| POST | `/api/festivals/{festival_id}/posts` | si |
| GET | `/api/posts/{post_id}` | opcional |
| PUT | `/api/posts/{post_id}` | si |
| DELETE | `/api/posts/{post_id}` | si |
| GET | `/api/posts/{post_id}/replies` | opcional |
| POST | `/api/posts/{post_id}/replies` | si |
| POST | `/api/posts/{post_id}/moderate` | si |

## `registration_forms` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms` | si |
| POST | `/api/festivals/{festival_id}/registration-forms` | si |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | si |
| GET | `/api/registration-forms/{form_id}` | si |
| PUT | `/api/registration-forms/{form_id}` | si |
| DELETE | `/api/registration-forms/{form_id}` | si |
| GET | `/api/registration-forms/{form_id}/registrations` | si |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | si |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | si |
| GET | `/api/public/forms/{token}` | non |
| POST | `/api/public/forms/{token}/register` | opcional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | si |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | si |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | si |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | si |
| GET | `/api/registration-forms/{form_id}/links` | si |
| POST | `/api/registration-forms/{form_id}/links` | si |
| DELETE | `/api/registration-form-links/{link_id}` | si |
| POST | `/api/registration-form-links/{link_id}/regenerate` | si |
| GET | `/api/festivals/{festival_id}/registrations` | si |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | si |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | si |
| GET | `/api/users/{user_id}/registrations` | si |
| PUT | `/api/registrations/{registration_id}` | si |
| POST | `/api/registrations/{registration_id}/approve` | si |
| POST | `/api/registrations/{registration_id}/reject` | si |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | si |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | si |
| DELETE | `/api/registrations/{registration_id}` | si |
| POST | `/api/registration-forms/{form_id}/sections` | si |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | si |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | si |

## `role_groups` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/role-groups` | non |
| POST | `/api/role-groups` | si (admin) |
| GET | `/api/role-groups/{group_id}` | non |
| PUT | `/api/role-groups/{group_id}` | si (admin) |
| DELETE | `/api/role-groups/{group_id}` | si (admin) |
| GET | `/api/role-groups/{group_id}/memberships` | non |
| POST | `/api/role-groups/{group_id}/memberships` | si (admin) |
| PUT | `/api/role-group-memberships/{membership_id}` | si (admin) |
| DELETE | `/api/role-group-memberships/{membership_id}` | si (admin) |

## `roles` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/roles` | si |
| POST | `/api/roles` | si (admin) |
| GET | `/api/roles/hierarchy` | opcional |
| GET | `/api/roles/{role_id}` | opcional |
| PUT | `/api/roles/{role_id}` | si (admin) |
| DELETE | `/api/roles/{role_id}` | si (admin) |
| GET | `/api/festivals/{festival_id}/roles` | opcional |
| POST | `/api/festivals/{festival_id}/roles` | si |
| POST | `/api/festivals/{festival_id}/roles/initialize` | si (admin) |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | si |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | si |
| GET | `/api/roles/{role_id}/dependencies` | opcional |
| POST | `/api/role-dependencies` | si (admin) |
| DELETE | `/api/role-dependencies/{dependency_id}` | si (admin) |
| GET | `/api/roles/{role_id}/conflicts` | opcional |
| POST | `/api/role-conflicts` | si (admin) |
| DELETE | `/api/role-conflicts/{conflict_id}` | si (admin) |
| GET | `/api/roles/{role_id}/check-conflicts` | opcional |

## `search` → `/api/search`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/search` | si |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations` | non |
| POST | `/api/shortfilms/{shortfilm_id}/locations` | si |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | si |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | si |

## `shortfilms` → `/api/shortfilms`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/shortfilms` (obsoleto) | non |
| POST | `/api/shortfilms` (obsoleto) | si |
| GET | `/api/shortfilms/{shortfilm_id}` (obsoleto) | non |
| PUT | `/api/shortfilms/{shortfilm_id}` (obsoleto) | si |
| DELETE | `/api/shortfilms/{shortfilm_id}` (obsoleto) | si |

## `uploads` → `/api/uploads`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | si |
| POST | `/api/uploads/thumbnail` | si |
| POST | `/api/uploads/video` | si |
| POST | `/api/uploads/document` | si |
| POST | `/api/uploads/chat-image` | si |

## `user_aliases` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases` | non |
| POST | `/api/users/{user_id}/aliases` | si |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | si |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | si |

## `user_blocks` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/blocks` | si |
| DELETE | `/api/users/{user_id}/blocks/{blocked_id}` | si |
| GET | `/api/users/{user_id}/blocks` | si |
| GET | `/api/users/{user_id}/blocks/{blocked_id}/status` | si |

## `user_festival` → `/api/festivals`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | si |
| DELETE | `/api/festivals/{festival_id}/leave` | si |
| GET | `/api/festivals/{festival_id}/members` | si |
| GET | `/api/festivals/user/{user_id}/festivals` | si |

## `user_follows` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/follow` | si |
| DELETE | `/api/users/{user_id}/follow` | si |
| GET | `/api/users/{user_id}/follow/status` | si |
| GET | `/api/users/{user_id}/followers` | si |
| GET | `/api/users/{user_id}/following` | si |

## `user_roles` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles` | si |
| POST | `/api/users/{user_id}/roles` | si |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | si |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | si |
| GET | `/api/users/{user_id}/participant-tags` | si |
| PATCH | `/api/users/{user_id}/participant-tags/{upt_id}/verify` | si |
| POST | `/api/users/{user_id}/participant-tags/{upt_id}/request-verification` | si |
| POST | `/api/users/{user_id}/participant-tags` | si |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | si |

## `users` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users` | si |
| GET | `/api/users/public` | non |
| GET | `/api/users/me` | si |
| GET | `/api/users/me/export` | si |
| DELETE | `/api/users/me` | si |
| POST | `/api/users` | si |
| GET | `/api/users/{user_id}` | si |
| GET | `/api/users/{user_id}/public` | non |
| PUT | `/api/users/{user_id}` | si |
| DELETE | `/api/users/{user_id}` | si |

## `validation_rules` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/validation-rules` | non |
| POST | `/api/validation-rules` | si (admin) |
| GET | `/api/validation-rules/{rule_id}` | non |
| PUT | `/api/validation-rules/{rule_id}` | si (admin) |
| DELETE | `/api/validation-rules/{rule_id}` | si (admin) |
| GET | `/api/validation-rule-groups` | non |
| POST | `/api/validation-rule-groups` | si (admin) |
