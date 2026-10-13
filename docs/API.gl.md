# API — referencia de endpoints

Xerado desde `app/routers/*.py` + prefixos de `app/main.py`.
Detalle interactivo: `/docs` (Swagger) e `/redoc` co backend en marcha.

## `admin` → `/api/admin`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/admin/stats` | si |
| GET | `/api/admin/tables` | si |
| GET | `/api/admin/audit-log` | si |
| POST | `/api/admin/reset` | si |

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

## `calendar` → `/api/calendar`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | opcional |
| GET | `/api/calendar/agenda/export/ics` | opcional |
| GET | `/api/calendar/settings` | non |
| GET | `/api/calendar/admin/settings` | si |
| PUT | `/api/calendar/admin/settings` | si |
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
| WEBSOCKET | `/api/chat/ws` | token (query) |

## `committees` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees/` | opcional |
| POST | `/api/festivals/{festival_id}/committees/` | si |
| GET | `/api/committees/{committee_id}` | opcional |
| PUT | `/api/committees/{committee_id}` | si |
| DELETE | `/api/committees/{committee_id}` | si |
| GET | `/api/committees/{committee_id}/members/` | opcional |
| POST | `/api/committees/{committee_id}/members/` | si |
| PUT | `/api/committee-members/{member_id}` | si |
| DELETE | `/api/committee-members/{member_id}` | si |

## `dav` → `/dav`

| Método | Ruta | Auth |
|---|---|---|
| OPTIONS | `/dav/` | non |
| OPTIONS | `/dav/{dav_path:path}` | non |
| PROPFIND | `/dav/` | non |
| GET | `/dav/{principal}/calendars/{collection}.ics` | non |
| HEAD | `/dav/{principal}/calendars/{collection}.ics` | non |
| GET | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | non |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | non |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | non |
| PROPFIND | `/dav/{principal}/calendars/{collection}/` | non |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | non |
| REPORT | `/dav/{principal}/calendars/{collection}/` | non |
| REPORT | `/dav/{principal}/calendars/{collection}` | non |
| PROPFIND | `/dav/{principal}/calendars/` | non |
| PROPFIND | `/dav/{principal}/calendars` | non |
| PROPFIND | `/dav/{principal}/` | non |
| PROPFIND | `/dav/{principal}` | non |
| REPORT | `/dav/{principal}/calendars/` | non |
| REPORT | `/dav/{principal}/calendars` | non |
| REPORT | `/dav/{principal}/` | non |
| REPORT | `/dav/{principal}` | non |
| API_ROUTE | `/dav/{write_path:path}` | non |

## `delegations` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/delegations/` | opcional |
| POST | `/api/delegations/` | si |
| PUT | `/api/delegations/{delegation_id}` | si |
| POST | `/api/delegations/{delegation_id}/revoke` | si |
| GET | `/api/users/{user_id}/active-delegations` | opcional |
| GET | `/api/role-transitions/` | si |
| POST | `/api/role-transitions/` | si |
| GET | `/api/users/{user_id}/role-transitions` | si |
| GET | `/api/users/{user_id}/role-check` | si |

## `events` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events/` | non |
| GET | `/api/festivals/{festival_id}/events/export/ics` | si |
| POST | `/api/festivals/{festival_id}/events/` | si |
| GET | `/api/events/{event_id}` | non |
| PUT | `/api/events/{event_id}` | si |
| DELETE | `/api/events/{event_id}` | si |
| GET | `/api/festivals/{festival_id}/events/programacion` | non |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | si |
| GET | `/api/events/{event_id}/screenings` | non |
| PUT | `/api/events/{event_id}/screenings` | si |
| GET | `/api/events/{event_id}/occupancy` | non |
| GET | `/api/events/{event_id}/ticket-types/` | non |
| POST | `/api/events/{event_id}/ticket-types/` | si |
| PUT | `/api/ticket-types/{tt_id}` | si |
| DELETE | `/api/ticket-types/{tt_id}` | si |
| GET | `/api/events/{event_id}/seats/` | non |
| POST | `/api/events/{event_id}/seats/bulk` | si |
| GET | `/api/events/{event_id}/seats/sections` | non |
| GET | `/api/events/{event_id}/seats/counts` | non |
| PUT | `/api/seats/{seat_id}` | si |
| POST | `/api/seats/{seat_id}/release` | si |
| DELETE | `/api/seats/{seat_id}` | si |
| GET | `/api/events/{event_id}/reservations/` | si |
| POST | `/api/events/{event_id}/reservations/` | si |
| PUT | `/api/reservations/{reservation_id}` | si |
| POST | `/api/reservations/{reservation_id}/confirm` | si |
| POST | `/api/reservations/{reservation_id}/cancel` | si |
| DELETE | `/api/reservations/{reservation_id}` | si |
| GET | `/api/events/{event_id}/attendees/` | si |
| POST | `/api/events/{event_id}/attendees/` | si |
| GET | `/api/attendees/{attendee_id}` | non |
| PUT | `/api/attendees/{attendee_id}` | si |
| POST | `/api/attendees/{attendee_id}/check-in` | si |
| GET | `/api/events/{event_id}/attendees/counts` | non |
| GET | `/api/events/{event_id}/attendees/export/csv` | si |
| DELETE | `/api/attendees/{attendee_id}` | si |
| POST | `/api/events/{event_id}/assign-vip` | si |
| GET | `/api/users/me/events/` | si |
| GET | `/api/users/me/events/{event_id}/reservation` | si |
| GET | `/api/festivals/{festival_id}/awards/` | non |
| POST | `/api/festivals/{festival_id}/awards/` | si |
| PUT | `/api/awards/{award_id}` | si |
| DELETE | `/api/awards/{award_id}` | si |
| GET | `/api/users/{user_id}/awards/` | non |
| GET | `/api/public/profile/{token}` | non |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | non |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks/` | non |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | non |
| POST | `/api/festivals/{festival_id}/rulebooks/` | si |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | si |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | si |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | si |

## `festivals` → `/api/festivals`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/` | non |
| POST | `/api/festivals/` | si |
| GET | `/api/festivals/{festival_id}` | non |
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
| GET | `/api/forms/` | si |
| POST | `/api/forms/` | si |
| GET | `/api/forms/{form_id}` | si |
| PUT | `/api/forms/{form_id}` | si |
| DELETE | `/api/forms/{form_id}` | si |
| POST | `/api/forms/{form_id}/clone` | si |
| POST | `/api/forms/{form_id}/pages/` | si |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | si |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | si |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields/` | si |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | si |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | si |
| GET | `/api/forms/{form_id}/links/` | si |
| POST | `/api/forms/{form_id}/links/` | si |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | si |
| GET | `/api/forms/public/{token}` | non |
| POST | `/api/forms/public/{token}/submit` | opcional |
| GET | `/api/forms/{form_id}/responses/` | si |
| GET | `/api/forms/{form_id}/responses/export/csv` | si |
| PUT | `/api/forms/responses/{response_id}` | si |
| POST | `/api/forms/responses/{response_id}/approve` | si |
| POST | `/api/forms/responses/{response_id}/reject` | si |

## `keys` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | si |
| GET | `/api/users/{user_id}/public-key` | si |

## `location_images` → `/api/locations/{location_id}/images`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images/` | non |
| POST | `/api/locations/{location_id}/images/upload` | si |
| POST | `/api/locations/{location_id}/images/url` | si |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | si |

## `location_relations` → `/api/locations/{location_id}/relations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations/` | non |
| POST | `/api/locations/{location_id}/relations/` | si |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | si |
| POST | `/api/locations/{location_id}/relations/suggest` | si |

## `location_tags` → `/api/locations/{location_id}/tags`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags/` | non |
| POST | `/api/locations/{location_id}/tags/` | si |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | si |

## `locations` → `/api/locations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/locations/` | non |
| POST | `/api/locations/` | si |
| GET | `/api/locations/{location_id}` | non |
| PUT | `/api/locations/{location_id}` | si |
| PUT | `/api/locations/{location_id}/badge` | si |
| DELETE | `/api/locations/{location_id}` | si |

## `notifications` → `/api/notifications`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/notifications/` | si |
| GET | `/api/notifications/unread-count` | si |
| PUT | `/api/notifications/{notification_id}/read` | si |
| PUT | `/api/notifications/read-all` | si |
| DELETE | `/api/notifications/{notification_id}` | si |

## `participant_tags` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/participant-tags/` | non |
| POST | `/api/participant-tags/` | si |
| GET | `/api/participant-tags/{tag_id}` | non |
| PUT | `/api/participant-tags/{tag_id}` | si |
| DELETE | `/api/participant-tags/{tag_id}` | si |
| GET | `/api/festivals/{festival_id}/participant-tags/` | non |
| POST | `/api/festivals/{festival_id}/participant-tags/` | si |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | si |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | si |

## `payments` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | si |
| GET | `/api/payments/` | si |
| GET | `/api/payments/{payment_id}` | si |
| POST | `/api/payments/{payment_id}/confirm` | si |
| POST | `/api/payments/{payment_id}/refund` | si |
| POST | `/api/payments/webhook/mock` | non |

## `registration_forms` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms/` | si |
| POST | `/api/festivals/{festival_id}/registration-forms/` | si |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | si |
| GET | `/api/registration-forms/{form_id}` | si |
| PUT | `/api/registration-forms/{form_id}` | si |
| DELETE | `/api/registration-forms/{form_id}` | si |
| GET | `/api/registration-forms/{form_id}/registrations/` | si |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | si |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | si |
| GET | `/api/public/forms/{token}` | non |
| POST | `/api/public/forms/{token}/register` | opcional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | si |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | si |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | si |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | si |
| GET | `/api/registration-forms/{form_id}/links/` | si |
| POST | `/api/registration-forms/{form_id}/links/` | si |
| DELETE | `/api/registration-form-links/{link_id}` | si |
| POST | `/api/registration-form-links/{link_id}/regenerate` | si |
| GET | `/api/festivals/{festival_id}/registrations/` | si |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | si |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | si |
| GET | `/api/users/{user_id}/registrations/` | si |
| PUT | `/api/registrations/{registration_id}` | si |
| POST | `/api/registrations/{registration_id}/approve` | si |
| POST | `/api/registrations/{registration_id}/reject` | si |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | si |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | si |
| DELETE | `/api/registrations/{registration_id}` | si |
| POST | `/api/registration-forms/{form_id}/sections/` | si |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | si |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | si |

## `role_groups` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/role-groups/` | non |
| POST | `/api/role-groups/` | si |
| GET | `/api/role-groups/{group_id}` | non |
| PUT | `/api/role-groups/{group_id}` | si |
| DELETE | `/api/role-groups/{group_id}` | si |
| GET | `/api/role-groups/{group_id}/memberships/` | non |
| POST | `/api/role-groups/{group_id}/memberships/` | si |
| PUT | `/api/role-group-memberships/{membership_id}` | si |
| DELETE | `/api/role-group-memberships/{membership_id}` | si |

## `roles` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/roles/` | si |
| POST | `/api/roles/` | si |
| GET | `/api/roles/hierarchy/` | opcional |
| GET | `/api/roles/{role_id}` | opcional |
| PUT | `/api/roles/{role_id}` | si |
| DELETE | `/api/roles/{role_id}` | si |
| GET | `/api/festivals/{festival_id}/roles/` | opcional |
| POST | `/api/festivals/{festival_id}/roles/` | si |
| POST | `/api/festivals/{festival_id}/roles/initialize` | si |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | si |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | si |
| GET | `/api/roles/{role_id}/dependencies` | opcional |
| POST | `/api/role-dependencies/` | si |
| DELETE | `/api/role-dependencies/{dependency_id}` | si |
| GET | `/api/roles/{role_id}/conflicts` | opcional |
| POST | `/api/role-conflicts/` | si |
| DELETE | `/api/role-conflicts/{conflict_id}` | si |
| GET | `/api/roles/{role_id}/check-conflicts` | opcional |

## `search` → `/api/search`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/search/` | si |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations/` | non |
| POST | `/api/shortfilms/{shortfilm_id}/locations/` | si |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | si |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | si |

## `shortfilms` → `/api/shortfilms`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/shortfilms/` | non |
| POST | `/api/shortfilms/` | si |
| GET | `/api/shortfilms/{shortfilm_id}` | non |
| PUT | `/api/shortfilms/{shortfilm_id}` | si |
| DELETE | `/api/shortfilms/{shortfilm_id}` | si |

## `uploads` → `/api/uploads`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | si |
| POST | `/api/uploads/thumbnail` | si |
| POST | `/api/uploads/video` | si |
| POST | `/api/uploads/chat-image` | si |

## `user_aliases` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases/` | non |
| POST | `/api/users/{user_id}/aliases/` | si |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | si |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | si |

## `user_festival` → `/api/festivals`

| Método | Ruta | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | si |
| DELETE | `/api/festivals/{festival_id}/leave` | si |
| GET | `/api/festivals/{festival_id}/members` | si |
| GET | `/api/festivals/user/{user_id}/festivals` | si |

## `user_roles` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles/` | si |
| POST | `/api/users/{user_id}/roles/` | si |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | si |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | si |
| GET | `/api/users/{user_id}/participant-tags/` | si |
| POST | `/api/users/{user_id}/participant-tags/` | si |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | si |

## `users` → `/api/users`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/users/` | si |
| GET | `/api/users/public` | non |
| GET | `/api/users/me` | si |
| GET | `/api/users/me/export` | si |
| DELETE | `/api/users/me` | si |
| POST | `/api/users/` | si |
| GET | `/api/users/{user_id}` | si |
| GET | `/api/users/{user_id}/public` | non |
| PUT | `/api/users/{user_id}` | si |
| DELETE | `/api/users/{user_id}` | si |

## `validation_rules` → `/api`

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/validation-rules/` | non |
| POST | `/api/validation-rules/` | si |
| GET | `/api/validation-rules/{rule_id}` | non |
| PUT | `/api/validation-rules/{rule_id}` | si |
| DELETE | `/api/validation-rules/{rule_id}` | si |
| GET | `/api/validation-rule-groups/` | non |
| POST | `/api/validation-rule-groups/` | si |

Total: 310 endpoints en 33 routers.