# API — referencia de endpoints

[ES](API.md) · [EN](../en/API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](../oc/API.md)

Generado desde `app/routers/*.py` (prefijo de cada `APIRouter` más el de `app/main.py`) y dependencias de cada endpoint.
Detalle interactivo: `/docs` (Swagger) y `/redoc` con el backend en marcha.

Todas las subidas devuelven una ruta relativa `/uploads/<carpeta>/<archivo>`, nunca una URL absoluta. El cliente la resuelve con `resolveMediaUrl()`, que antepone el servidor activo; las URLs `http(s)` se dejan intactas. Los campos de medios (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) aceptan ambos formatos.

## `admin` → `/api/admin`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/admin/stats` | sí (admin) |
| GET | `/api/admin/tables` | sí (admin) |
| GET | `/api/admin/audit-log` | sí (admin) |
| POST | `/api/admin/reset` | sí (admin) |

## `auth` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/login` | no |

## `auth_sessions` → `/api/auth`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | no |
| GET | `/api/auth/sessions` | sí |
| DELETE | `/api/auth/sessions/{session_id}` | sí |
| POST | `/api/auth/sessions/revoke-all` | sí |

## `badges` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/badges/status` | no |
| PUT | `/api/badges/settings` | sí (admin) |
| GET | `/api/badges` | opcional |
| POST | `/api/badges` | sí (admin) |
| GET | `/api/badges/{badge_id}` | opcional |
| PUT | `/api/badges/{badge_id}` | sí (admin) |
| DELETE | `/api/badges/{badge_id}` | sí (admin) |
| POST | `/api/badges/{badge_id}/image` | sí (admin) |
| GET | `/api/badges/{badge_id}/eligibility` | opcional |
| POST | `/api/badges/{badge_id}/assign` | sí (admin) |
| DELETE | `/api/badge-assignments/{assignment_id}` | sí |
| GET | `/api/users/{user_id}/badges` | opcional |
| GET | `/api/festivals/{festival_id}/badges` | opcional |

## `calendar` → `/api/calendar`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | opcional |
| GET | `/api/calendar/agenda/export/ics` | opcional |
| GET | `/api/calendar/settings` | no |
| GET | `/api/calendar/admin/settings` | sí (admin) |
| PUT | `/api/calendar/admin/settings` | sí (admin) |
| POST | `/api/calendar/dav/token` | sí |
| GET | `/api/calendar/dav/token` | sí |
| DELETE | `/api/calendar/dav/token` | sí |

## `channels` → `/api/channels`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/channels` | sí |
| GET | `/api/channels` | sí |
| GET | `/api/channels/public` | sí |
| GET | `/api/channels/{channel_id}` | sí |
| PUT | `/api/channels/{channel_id}` | sí |
| DELETE | `/api/channels/{channel_id}` | sí |
| POST | `/api/channels/{channel_id}/members` | sí |
| GET | `/api/channels/{channel_id}/members` | sí |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | sí |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | sí |

## `chat` → `/api/chat`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/chat/messages` | sí |
| POST | `/api/chat/messages` | sí |
| PUT | `/api/chat/messages/{message_id}/read` | sí |
| DELETE | `/api/chat/messages/{message_id}` | sí |
| GET | `/api/chat/groups` | sí |
| POST | `/api/chat/groups` | sí |
| GET | `/api/chat/groups/{group_id}` | sí |
| DELETE | `/api/chat/groups/{group_id}` | sí |
| GET | `/api/chat/groups/{group_id}/members` | sí |
| POST | `/api/chat/groups/{group_id}/members` | sí |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | sí |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | sí |
| WEBSOCKET | `/api/chat/ws` | token (query, obligatorio) |

## `chat_moderation` → `/api/chat/moderation`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/chat/moderation/messages/{message_id}/report` | sí |
| PATCH | `/api/chat/moderation/messages/{message_id}/moderate` | sí |
| GET | `/api/chat/moderation/reports` | sí (admin) |
| POST | `/api/chat/moderation/mutes` | sí |
| GET | `/api/chat/moderation/mutes` | sí (admin) |
| GET | `/api/chat/moderation/limits` | sí (admin) |

## `committees` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees` | opcional |
| POST | `/api/festivals/{festival_id}/committees` | sí |
| GET | `/api/committees/{committee_id}` | opcional |
| PUT | `/api/committees/{committee_id}` | sí |
| DELETE | `/api/committees/{committee_id}` | sí |
| GET | `/api/committees/{committee_id}/members` | opcional |
| POST | `/api/committees/{committee_id}/members` | sí |
| PUT | `/api/committee-members/{member_id}` | sí |
| DELETE | `/api/committee-members/{member_id}` | sí |

## `dav` → `/dav`

| Método | Ruta | Auth |
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

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/delegations` | opcional |
| POST | `/api/delegations` | sí |
| PUT | `/api/delegations/{delegation_id}` | sí |
| POST | `/api/delegations/{delegation_id}/revoke` | sí |
| GET | `/api/users/{user_id}/active-delegations` | opcional |
| GET | `/api/role-transitions` | sí |
| POST | `/api/role-transitions` | sí |
| GET | `/api/users/{user_id}/role-transitions` | sí |
| GET | `/api/users/{user_id}/role-check` | sí |

## `events` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events` | no |
| GET | `/api/festivals/{festival_id}/events/export/ics` | sí |
| POST | `/api/festivals/{festival_id}/events` | sí |
| GET | `/api/events/{event_id}` | no |
| PUT | `/api/events/{event_id}` | sí |
| DELETE | `/api/events/{event_id}` | sí |
| GET | `/api/festivals/{festival_id}/events/programacion` | no |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | sí |
| GET | `/api/events/{event_id}/screenings` | no |
| PATCH | `/api/events/{event_id}/screenings/{shortfilm_id}` | sí |
| PUT | `/api/events/{event_id}/screenings/{shortfilm_id}/notes` | sí |
| PUT | `/api/events/{event_id}/screenings` | sí |
| GET | `/api/festivals/{festival_id}/screenings` | no |
| GET | `/api/events/{event_id}/occupancy` | no |
| GET | `/api/events/{event_id}/ticket-types` | no |
| POST | `/api/events/{event_id}/ticket-types` | sí |
| PUT | `/api/ticket-types/{tt_id}` | sí |
| DELETE | `/api/ticket-types/{tt_id}` | sí |
| GET | `/api/events/{event_id}/seats` | no |
| POST | `/api/events/{event_id}/seats/bulk` | sí |
| GET | `/api/events/{event_id}/seats/sections` | no |
| GET | `/api/events/{event_id}/seats/counts` | no |
| PUT | `/api/seats/{seat_id}` | sí |
| POST | `/api/seats/{seat_id}/release` | sí |
| DELETE | `/api/seats/{seat_id}` | sí |
| GET | `/api/events/{event_id}/reservations` | sí |
| POST | `/api/events/{event_id}/reservations` | sí |
| PUT | `/api/reservations/{reservation_id}` | sí |
| POST | `/api/reservations/{reservation_id}/confirm` | sí |
| POST | `/api/reservations/{reservation_id}/cancel` | sí |
| DELETE | `/api/reservations/{reservation_id}` | sí |
| GET | `/api/events/{event_id}/attendees` | sí |
| POST | `/api/events/{event_id}/attendees` | sí |
| GET | `/api/attendees/{attendee_id}` | no |
| PUT | `/api/attendees/{attendee_id}` | sí |
| POST | `/api/attendees/{attendee_id}/check-in` | sí |
| GET | `/api/events/{event_id}/attendees/counts` | no |
| GET | `/api/events/{event_id}/attendees/export/csv` | sí |
| DELETE | `/api/attendees/{attendee_id}` | sí |
| POST | `/api/events/{event_id}/assign-vip` | sí |
| GET | `/api/users/me/events` | sí |
| GET | `/api/users/me/events/{event_id}/reservation` | sí |
| GET | `/api/festivals/{festival_id}/awards` | no |
| POST | `/api/festivals/{festival_id}/awards` | sí |
| PUT | `/api/awards/{award_id}` | sí |
| DELETE | `/api/awards/{award_id}` | sí |
| PATCH | `/api/awards/{award_id}/recipient-verification` | sí |
| GET | `/api/users/{user_id}/awards` | no |
| GET | `/api/public/profile/{token}` | no |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | no |

## `federation` → `/api/federation`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/federation/nodes` | sí (admin) |
| POST | `/api/federation/nodes` | sí (admin) |
| GET | `/api/federation/manifest` | no |
| PATCH | `/api/federation/reports/{report_id}` | no |
| GET | `/api/federation/directory` | no |
| POST | `/api/federation/reports` | no |
| GET | `/api/federation/reports` | no |
| DELETE | `/api/federation/users/{user_ref}` | no |
| GET | `/api/federation/export/{user_ref}` | no |
| GET | `/api/federation/health` (obsoleto) | no |
| POST | `/api/federation/verify` | no |
| POST | `/api/federation/publish` | JWT de federación |
| POST | `/api/federation/recover` | no |
| POST | `/api/federation/bridge` | JWT de federación |
| GET | `/api/federation/aggregate-nodes` (obsoleto) | no |
| GET | `/api/federation/keys` (obsoleto) | no |
| GET | `/api/federation/events` (obsoleto) | no |
| GET | `/api/federation/capabilities` (obsoleto) | no |
| GET | `/api/federation/status` (obsoleto) | no |
| GET | `/api/federation/info` (obsoleto) | no |
| GET | `/api/federation/ping` (obsoleto) | no |
| POST | `/api/federation/echo` | no |
| GET | `/api/federation/time` | no |
| GET | `/api/federation/version` (obsoleto) | no |
| POST | `/api/federation/checksum` | no |
| POST | `/api/federation/notify` (obsoleto) | no |
| POST | `/api/federation/subscribe` (obsoleto) | no |
| POST | `/api/federation/unsubscribe` (obsoleto) | no |
| GET | `/api/federation/discover` (obsoleto) | no |
| POST | `/api/federation/register` | JWT de federación |
| POST | `/api/federation/unregister` | no |
| POST | `/api/federation/sync` | no |
| POST | `/api/federation/reconcile` | no |
| GET | `/api/federation/heartbeat` (obsoleto) | no |
| GET | `/api/federation/whoami` | JWT de federación |
| GET | `/api/federation/peers` (obsoleto) | no |
| GET | `/api/federation/links` (obsoleto) | no |
| GET | `/api/federation/stats` (obsoleto) | no |
| GET | `/api/federation/config` (obsoleto) | no |
| GET | `/api/federation/status-check` (obsoleto) | no |
| GET | `/api/federation/ready` (obsoleto) | no |
| GET | `/api/federation/live` (obsoleto) | no |
| GET | `/api/federation/alive` (obsoleto) | no |
| GET | `/api/federation/down` (obsoleto) | no |
| GET | `/api/federation/maintenance` (obsoleto) | no |
| GET | `/api/federation/readyz` (obsoleto) | no |
| GET | `/api/federation/livez` (obsoleto) | no |
| GET | `/api/federation/healthz` (obsoleto) | no |
| GET | `/api/federation/ok` (obsoleto) | no |
| GET | `/api/federation/yes` (obsoleto) | no |
| GET | `/api/federation/no` (obsoleto) | no |
| GET | `/api/federation/maybe` (obsoleto) | no |
| GET | `/api/federation/always` (obsoleto) | no |
| GET | `/api/federation/never` (obsoleto) | no |
| POST | `/api/federation/import` | no |
| POST | `/api/federation/dedup` | no |
| POST | `/api/federation/retry` | no |
| POST | `/api/federation/recover-node` | no |
| GET | `/api/federation/integrity` | no |
| GET | `/api/federation/metrics` | no |
| GET | `/api/federation/users/{ref}` | no |
| GET | `/api/federation/.well-known/webfinger` | no |
| POST | `/api/federation/peers/verify` | no |
| POST | `/api/federation/peers/{domain}/revoke` | sí (admin) |
| GET | `/api/federation/.well-known/jwks.json` | no |
| POST | `/api/federation/token` | no |

## `federation_chat_bridge` → `/api/federation`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/federation/chat/bridge/inbound` | no |
| POST | `/api/federation/chat/bridge/outbound` | no |
| GET | `/api/federation/chat/bridge/config` | no |
| GET | `/api/federation/chat/messages` | no |

## `federation_events` → `/api/federation/events`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/federation/events/stream` | Bearer (cabecera) o token (query, obsoleto) |
| POST | `/api/federation/events/publish` | sí (admin) |
| GET | `/api/federation/events/retry-queue` | sí (admin) |

## `federation_portability` → `/api/federation/portability`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/federation/portability/bundles` | sí |
| POST | `/api/federation/portability/imports` | sí |
| POST | `/api/federation/portability/festivals/{festival_id}/migrate` | sí (admin) |
| POST | `/api/federation/portability/users/{user_ref}/migrate` | sí (admin) |
| GET | `/api/federation/portability/redirects/{old_ref}` | sí |

## `federation_resilience` → `/api/federation/resilience`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/federation/resilience/health` | no |
| GET | `/api/federation/resilience/heartbeat` | no |
| GET | `/api/federation/resilience/metrics` | no |
| POST | `/api/federation/resilience/keys/revoke` | sí (admin) |
| GET | `/api/federation/resilience/keys/revoked` | no |
| GET | `/api/federation/resilience/incident-plan` | no |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks` | no |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | no |
| POST | `/api/festivals/{festival_id}/rulebooks` | sí |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | sí |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | sí |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | sí |

## `festivals` → `/api/festivals`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals` | no |
| POST | `/api/festivals` | sí |
| GET | `/api/festivals/{festival_id}` | no |
| GET | `/api/festivals/{festival_id}/shortfilms` | no |
| POST | `/api/festivals/{festival_id}/shortfilms` | sí |
| GET | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | no |
| PUT | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | sí |
| DELETE | `/api/festivals/{festival_id}/shortfilms/{shortfilm_id}` | sí |
| PUT | `/api/festivals/{festival_id}` | sí |
| DELETE | `/api/festivals/{festival_id}` | sí |
| POST | `/api/festivals/{festival_id}/images` | sí |
| DELETE | `/api/festivals/{festival_id}/images` | sí |
| GET | `/api/festivals/{festival_id}/locations` | no |
| POST | `/api/festivals/{festival_id}/locations` | sí |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | sí |

## `form_definitions` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/forms` | sí |
| POST | `/api/forms` | sí |
| GET | `/api/forms/{form_id}` | sí |
| PUT | `/api/forms/{form_id}` | sí |
| DELETE | `/api/forms/{form_id}` | sí |
| POST | `/api/forms/{form_id}/clone` | sí |
| POST | `/api/forms/{form_id}/pages` | sí |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | sí |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | sí |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields` | sí |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | sí |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | sí |
| GET | `/api/forms/{form_id}/links` | sí |
| POST | `/api/forms/{form_id}/links` | sí |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | sí |
| GET | `/api/forms/public/{token}` | no |
| POST | `/api/forms/public/{token}/submit` | opcional |
| GET | `/api/forms/{form_id}/responses` | sí |
| GET | `/api/forms/{form_id}/responses/export/csv` | sí |
| PUT | `/api/forms/responses/{response_id}` | sí |
| POST | `/api/forms/responses/{response_id}/approve` | sí |
| POST | `/api/forms/responses/{response_id}/reject` | sí |

## `jury_votes` → `/api/jury-votes`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/jury-votes` | sí |
| GET | `/api/jury-votes/{festival_id}` | opcional |
| GET | `/api/jury-votes/aggregate/{festival_id}` | no |
| GET | `/api/jury-votes/by-juror/{festival_id}/{juror_id}` | sí |
| GET | `/api/jury-votes/anonymous/{festival_id}` | sí |

## `keys` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | sí |
| GET | `/api/users/{user_id}/public-key` | sí |

## `location_images` → `/api/locations/{location_id}/images`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images` | no |
| POST | `/api/locations/{location_id}/images/upload` | sí |
| POST | `/api/locations/{location_id}/images/url` | sí |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | sí |

## `location_relations` → `/api/locations/{location_id}/relations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations` | no |
| POST | `/api/locations/{location_id}/relations` | sí |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | sí |
| POST | `/api/locations/{location_id}/relations/suggest` | sí |

## `location_tags` → `/api/locations/{location_id}/tags`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags` | no |
| POST | `/api/locations/{location_id}/tags` | sí |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | sí |

## `locations` → `/api/locations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations` | no |
| POST | `/api/locations` | sí |
| GET | `/api/locations/{location_id}` | no |
| PUT | `/api/locations/{location_id}` | sí |
| PUT | `/api/locations/{location_id}/badge` | sí |
| DELETE | `/api/locations/{location_id}` | sí |

## `notifications` → `/api/notifications`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/notifications` | sí |
| GET | `/api/notifications/unread-count` | sí |
| PUT | `/api/notifications/{notification_id}/read` | sí |
| PUT | `/api/notifications/read-all` | sí |
| DELETE | `/api/notifications/{notification_id}` | sí |

## `participant_tags` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/participant-tags` | no |
| POST | `/api/participant-tags` | sí (admin) |
| GET | `/api/participant-tags/{tag_id}` | no |
| PUT | `/api/participant-tags/{tag_id}` | sí (admin) |
| DELETE | `/api/participant-tags/{tag_id}` | sí (admin) |
| GET | `/api/festivals/{festival_id}/participant-tags` | no |
| POST | `/api/festivals/{festival_id}/participant-tags` | sí |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | sí |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | sí |

## `payments` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | sí |
| GET | `/api/payments` | sí |
| GET | `/api/payments/{payment_id}` | sí |
| POST | `/api/payments/{payment_id}/confirm` | sí |
| POST | `/api/payments/{payment_id}/refund` | sí |
| POST | `/api/payments/webhook/mock` | no |
| POST | `/api/payments/webhook/stripe` | no |
| POST | `/api/payments/webhook/redsys` | no |

## `posts` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/posts` | opcional |
| POST | `/api/users/{user_id}/posts` | sí |
| GET | `/api/festivals/{festival_id}/posts` | opcional |
| POST | `/api/festivals/{festival_id}/posts` | sí |
| GET | `/api/posts/{post_id}` | opcional |
| PUT | `/api/posts/{post_id}` | sí |
| DELETE | `/api/posts/{post_id}` | sí |
| GET | `/api/posts/{post_id}/replies` | opcional |
| POST | `/api/posts/{post_id}/replies` | sí |
| POST | `/api/posts/{post_id}/moderate` | sí |

## `registration_forms` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms` | sí |
| POST | `/api/festivals/{festival_id}/registration-forms` | sí |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sí |
| GET | `/api/registration-forms/{form_id}` | sí |
| PUT | `/api/registration-forms/{form_id}` | sí |
| DELETE | `/api/registration-forms/{form_id}` | sí |
| GET | `/api/registration-forms/{form_id}/registrations` | sí |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sí |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sí |
| GET | `/api/public/forms/{token}` | no |
| POST | `/api/public/forms/{token}/register` | opcional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | sí |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links` | sí |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | sí |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | sí |
| GET | `/api/registration-forms/{form_id}/links` | sí |
| POST | `/api/registration-forms/{form_id}/links` | sí |
| DELETE | `/api/registration-form-links/{link_id}` | sí |
| POST | `/api/registration-form-links/{link_id}/regenerate` | sí |
| GET | `/api/festivals/{festival_id}/registrations` | sí |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | sí |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | sí |
| GET | `/api/users/{user_id}/registrations` | sí |
| PUT | `/api/registrations/{registration_id}` | sí |
| POST | `/api/registrations/{registration_id}/approve` | sí |
| POST | `/api/registrations/{registration_id}/reject` | sí |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | sí |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | sí |
| DELETE | `/api/registrations/{registration_id}` | sí |
| POST | `/api/registration-forms/{form_id}/sections` | sí |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | sí |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | sí |

## `role_groups` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/role-groups` | no |
| POST | `/api/role-groups` | sí (admin) |
| GET | `/api/role-groups/{group_id}` | no |
| PUT | `/api/role-groups/{group_id}` | sí (admin) |
| DELETE | `/api/role-groups/{group_id}` | sí (admin) |
| GET | `/api/role-groups/{group_id}/memberships` | no |
| POST | `/api/role-groups/{group_id}/memberships` | sí (admin) |
| PUT | `/api/role-group-memberships/{membership_id}` | sí (admin) |
| DELETE | `/api/role-group-memberships/{membership_id}` | sí (admin) |

## `roles` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/roles` | sí |
| POST | `/api/roles` | sí (admin) |
| GET | `/api/roles/hierarchy` | opcional |
| GET | `/api/roles/{role_id}` | opcional |
| PUT | `/api/roles/{role_id}` | sí (admin) |
| DELETE | `/api/roles/{role_id}` | sí (admin) |
| GET | `/api/festivals/{festival_id}/roles` | opcional |
| POST | `/api/festivals/{festival_id}/roles` | sí |
| POST | `/api/festivals/{festival_id}/roles/initialize` | sí (admin) |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | sí |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | sí |
| GET | `/api/roles/{role_id}/dependencies` | opcional |
| POST | `/api/role-dependencies` | sí (admin) |
| DELETE | `/api/role-dependencies/{dependency_id}` | sí (admin) |
| GET | `/api/roles/{role_id}/conflicts` | opcional |
| POST | `/api/role-conflicts` | sí (admin) |
| DELETE | `/api/role-conflicts/{conflict_id}` | sí (admin) |
| GET | `/api/roles/{role_id}/check-conflicts` | opcional |

## `search` → `/api/search`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/search` | sí |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations` | no |
| POST | `/api/shortfilms/{shortfilm_id}/locations` | sí |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | sí |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | sí |

## `shortfilms` → `/api/shortfilms`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/shortfilms` (obsoleto) | no |
| POST | `/api/shortfilms` (obsoleto) | sí |
| GET | `/api/shortfilms/{shortfilm_id}` (obsoleto) | no |
| PUT | `/api/shortfilms/{shortfilm_id}` (obsoleto) | sí |
| DELETE | `/api/shortfilms/{shortfilm_id}` (obsoleto) | sí |

## `uploads` → `/api/uploads`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | sí |
| POST | `/api/uploads/thumbnail` | sí |
| POST | `/api/uploads/video` | sí |
| POST | `/api/uploads/document` | sí |
| POST | `/api/uploads/chat-image` | sí |

## `user_aliases` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases` | no |
| POST | `/api/users/{user_id}/aliases` | sí |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | sí |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | sí |

## `user_blocks` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/blocks` | sí |
| DELETE | `/api/users/{user_id}/blocks/{blocked_id}` | sí |
| GET | `/api/users/{user_id}/blocks` | sí |
| GET | `/api/users/{user_id}/blocks/{blocked_id}/status` | sí |

## `user_festival` → `/api/festivals`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | sí |
| DELETE | `/api/festivals/{festival_id}/leave` | sí |
| GET | `/api/festivals/{festival_id}/members` | sí |
| GET | `/api/festivals/user/{user_id}/festivals` | sí |

## `user_follows` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/{user_id}/follow` | sí |
| DELETE | `/api/users/{user_id}/follow` | sí |
| GET | `/api/users/{user_id}/follow/status` | sí |
| GET | `/api/users/{user_id}/followers` | sí |
| GET | `/api/users/{user_id}/following` | sí |

## `user_roles` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles` | sí |
| POST | `/api/users/{user_id}/roles` | sí |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | sí |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | sí |
| GET | `/api/users/{user_id}/participant-tags` | sí |
| PATCH | `/api/users/{user_id}/participant-tags/{upt_id}/verify` | sí |
| POST | `/api/users/{user_id}/participant-tags/{upt_id}/request-verification` | sí |
| POST | `/api/users/{user_id}/participant-tags` | sí |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | sí |

## `users` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users` | sí |
| GET | `/api/users/public` | no |
| GET | `/api/users/me` | sí |
| GET | `/api/users/me/export` | sí |
| DELETE | `/api/users/me` | sí |
| POST | `/api/users` | sí |
| GET | `/api/users/{user_id}` | sí |
| GET | `/api/users/{user_id}/public` | no |
| PUT | `/api/users/{user_id}` | sí |
| DELETE | `/api/users/{user_id}` | sí |

## `validation_rules` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/validation-rules` | no |
| POST | `/api/validation-rules` | sí (admin) |
| GET | `/api/validation-rules/{rule_id}` | no |
| PUT | `/api/validation-rules/{rule_id}` | sí (admin) |
| DELETE | `/api/validation-rules/{rule_id}` | sí (admin) |
| GET | `/api/validation-rule-groups` | no |
| POST | `/api/validation-rule-groups` | sí (admin) |
