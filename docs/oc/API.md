# API — referéncia dels endpoints

[ES](../es/API.md) · [EN](../en/API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](../oc/API.md)

Generat dempuèi `app/routers/*.py` + prefixes de `app/main.py`.
Datalh interactiu: `/docs` (Swagger) e `/redoc` amb lo backend en marcha.

## `admin` → `/api/admin`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/admin/stats` | òc |
| GET | `/api/admin/tables` | òc |
| GET | `/api/admin/audit-log` | òc |
| POST | `/api/admin/reset` | òc |

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

## `calendar` → `/api/calendar`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | opcional |
| GET | `/api/calendar/agenda/export/ics` | opcional |
| GET | `/api/calendar/settings` | non |
| GET | `/api/calendar/admin/settings` | òc |
| PUT | `/api/calendar/admin/settings` | òc |
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
| WEBSOCKET | `/api/chat/ws` | token (query) |

## `committees` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees/` | opcional |
| POST | `/api/festivals/{festival_id}/committees/` | òc |
| GET | `/api/committees/{committee_id}` | opcional |
| PUT | `/api/committees/{committee_id}` | òc |
| DELETE | `/api/committees/{committee_id}` | òc |
| GET | `/api/committees/{committee_id}/members/` | opcional |
| POST | `/api/committees/{committee_id}/members/` | òc |
| PUT | `/api/committee-members/{member_id}` | òc |
| DELETE | `/api/committee-members/{member_id}` | òc |

## `dav` → `/dav`

| Metòde | Camin | Auth |
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

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/delegations/` | opcional |
| POST | `/api/delegations/` | òc |
| PUT | `/api/delegations/{delegation_id}` | òc |
| POST | `/api/delegations/{delegation_id}/revoke` | òc |
| GET | `/api/users/{user_id}/active-delegations` | opcional |
| GET | `/api/role-transitions/` | òc |
| POST | `/api/role-transitions/` | òc |
| GET | `/api/users/{user_id}/role-transitions` | òc |
| GET | `/api/users/{user_id}/role-check` | òc |

## `events` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events/` | non |
| GET | `/api/festivals/{festival_id}/events/export/ics` | òc |
| POST | `/api/festivals/{festival_id}/events/` | òc |
| GET | `/api/events/{event_id}` | non |
| PUT | `/api/events/{event_id}` | òc |
| DELETE | `/api/events/{event_id}` | òc |
| GET | `/api/festivals/{festival_id}/events/programacion` | non |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | òc |
| GET | `/api/events/{event_id}/screenings` | non |
| PUT | `/api/events/{event_id}/screenings` | òc |
| GET | `/api/events/{event_id}/occupancy` | non |
| GET | `/api/events/{event_id}/ticket-types/` | non |
| POST | `/api/events/{event_id}/ticket-types/` | òc |
| PUT | `/api/ticket-types/{tt_id}` | òc |
| DELETE | `/api/ticket-types/{tt_id}` | òc |
| GET | `/api/events/{event_id}/seats/` | non |
| POST | `/api/events/{event_id}/seats/bulk` | òc |
| GET | `/api/events/{event_id}/seats/sections` | non |
| GET | `/api/events/{event_id}/seats/counts` | non |
| PUT | `/api/seats/{seat_id}` | òc |
| POST | `/api/seats/{seat_id}/release` | òc |
| DELETE | `/api/seats/{seat_id}` | òc |
| GET | `/api/events/{event_id}/reservations/` | òc |
| POST | `/api/events/{event_id}/reservations/` | òc |
| PUT | `/api/reservations/{reservation_id}` | òc |
| POST | `/api/reservations/{reservation_id}/confirm` | òc |
| POST | `/api/reservations/{reservation_id}/cancel` | òc |
| DELETE | `/api/reservations/{reservation_id}` | òc |
| GET | `/api/events/{event_id}/attendees/` | òc |
| POST | `/api/events/{event_id}/attendees/` | òc |
| GET | `/api/attendees/{attendee_id}` | non |
| PUT | `/api/attendees/{attendee_id}` | òc |
| POST | `/api/attendees/{attendee_id}/check-in` | òc |
| GET | `/api/events/{event_id}/attendees/counts` | non |
| GET | `/api/events/{event_id}/attendees/export/csv` | òc |
| DELETE | `/api/attendees/{attendee_id}` | òc |
| POST | `/api/events/{event_id}/assign-vip` | òc |
| GET | `/api/users/me/events/` | òc |
| GET | `/api/users/me/events/{event_id}/reservation` | òc |
| GET | `/api/festivals/{festival_id}/awards/` | non |
| POST | `/api/festivals/{festival_id}/awards/` | òc |
| PUT | `/api/awards/{award_id}` | òc |
| DELETE | `/api/awards/{award_id}` | òc |
| GET | `/api/users/{user_id}/awards/` | non |
| GET | `/api/public/profile/{token}` | non |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | non |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks/` | non |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | non |
| POST | `/api/festivals/{festival_id}/rulebooks/` | òc |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | òc |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | òc |

## `festivals` → `/api/festivals`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/` | non |
| POST | `/api/festivals/` | òc |
| GET | `/api/festivals/{festival_id}` | non |
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
| GET | `/api/forms/` | òc |
| POST | `/api/forms/` | òc |
| GET | `/api/forms/{form_id}` | òc |
| PUT | `/api/forms/{form_id}` | òc |
| DELETE | `/api/forms/{form_id}` | òc |
| POST | `/api/forms/{form_id}/clone` | òc |
| POST | `/api/forms/{form_id}/pages/` | òc |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | òc |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | òc |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields/` | òc |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | òc |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | òc |
| GET | `/api/forms/{form_id}/links/` | òc |
| POST | `/api/forms/{form_id}/links/` | òc |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | òc |
| GET | `/api/forms/public/{token}` | non |
| POST | `/api/forms/public/{token}/submit` | opcional |
| GET | `/api/forms/{form_id}/responses/` | òc |
| GET | `/api/forms/{form_id}/responses/export/csv` | òc |
| PUT | `/api/forms/responses/{response_id}` | òc |
| POST | `/api/forms/responses/{response_id}/approve` | òc |
| POST | `/api/forms/responses/{response_id}/reject` | òc |

## `keys` → `/api/users`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | òc |
| GET | `/api/users/{user_id}/public-key` | òc |

## `location_images` → `/api/locations/{location_id}/images`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images/` | non |
| POST | `/api/locations/{location_id}/images/upload` | òc |
| POST | `/api/locations/{location_id}/images/url` | òc |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | òc |

## `location_relations` → `/api/locations/{location_id}/relations`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations/` | non |
| POST | `/api/locations/{location_id}/relations/` | òc |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | òc |
| POST | `/api/locations/{location_id}/relations/suggest` | òc |

## `location_tags` → `/api/locations/{location_id}/tags`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags/` | non |
| POST | `/api/locations/{location_id}/tags/` | òc |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | òc |

## `locations` → `/api/locations`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/locations/` | non |
| POST | `/api/locations/` | òc |
| GET | `/api/locations/{location_id}` | non |
| PUT | `/api/locations/{location_id}` | òc |
| PUT | `/api/locations/{location_id}/badge` | òc |
| DELETE | `/api/locations/{location_id}` | òc |

## `notifications` → `/api/notifications`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/notifications/` | òc |
| GET | `/api/notifications/unread-count` | òc |
| PUT | `/api/notifications/{notification_id}/read` | òc |
| PUT | `/api/notifications/read-all` | òc |
| DELETE | `/api/notifications/{notification_id}` | òc |

## `participant_tags` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/participant-tags/` | non |
| POST | `/api/participant-tags/` | òc |
| GET | `/api/participant-tags/{tag_id}` | non |
| PUT | `/api/participant-tags/{tag_id}` | òc |
| DELETE | `/api/participant-tags/{tag_id}` | òc |
| GET | `/api/festivals/{festival_id}/participant-tags/` | non |
| POST | `/api/festivals/{festival_id}/participant-tags/` | òc |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | òc |

## `payments` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | òc |
| GET | `/api/payments/` | òc |
| GET | `/api/payments/{payment_id}` | òc |
| POST | `/api/payments/{payment_id}/confirm` | òc |
| POST | `/api/payments/{payment_id}/refund` | òc |
| POST | `/api/payments/webhook/mock` | non |

## `registration_forms` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms/` | òc |
| POST | `/api/festivals/{festival_id}/registration-forms/` | òc |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | òc |
| GET | `/api/registration-forms/{form_id}` | òc |
| PUT | `/api/registration-forms/{form_id}` | òc |
| DELETE | `/api/registration-forms/{form_id}` | òc |
| GET | `/api/registration-forms/{form_id}/registrations/` | òc |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | òc |
| GET | `/api/public/forms/{token}` | non |
| POST | `/api/public/forms/{token}/register` | opcional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | òc |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | òc |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | òc |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | òc |
| GET | `/api/registration-forms/{form_id}/links/` | òc |
| POST | `/api/registration-forms/{form_id}/links/` | òc |
| DELETE | `/api/registration-form-links/{link_id}` | òc |
| POST | `/api/registration-form-links/{link_id}/regenerate` | òc |
| GET | `/api/festivals/{festival_id}/registrations/` | òc |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | òc |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | òc |
| GET | `/api/users/{user_id}/registrations/` | òc |
| PUT | `/api/registrations/{registration_id}` | òc |
| POST | `/api/registrations/{registration_id}/approve` | òc |
| POST | `/api/registrations/{registration_id}/reject` | òc |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | òc |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | òc |
| DELETE | `/api/registrations/{registration_id}` | òc |
| POST | `/api/registration-forms/{form_id}/sections/` | òc |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | òc |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | òc |

## `role_groups` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/role-groups/` | non |
| POST | `/api/role-groups/` | òc |
| GET | `/api/role-groups/{group_id}` | non |
| PUT | `/api/role-groups/{group_id}` | òc |
| DELETE | `/api/role-groups/{group_id}` | òc |
| GET | `/api/role-groups/{group_id}/memberships/` | non |
| POST | `/api/role-groups/{group_id}/memberships/` | òc |
| PUT | `/api/role-group-memberships/{membership_id}` | òc |
| DELETE | `/api/role-group-memberships/{membership_id}` | òc |

## `roles` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/roles/` | òc |
| POST | `/api/roles/` | òc |
| GET | `/api/roles/hierarchy/` | opcional |
| GET | `/api/roles/{role_id}` | opcional |
| PUT | `/api/roles/{role_id}` | òc |
| DELETE | `/api/roles/{role_id}` | òc |
| GET | `/api/festivals/{festival_id}/roles/` | opcional |
| POST | `/api/festivals/{festival_id}/roles/` | òc |
| POST | `/api/festivals/{festival_id}/roles/initialize` | òc |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | òc |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | òc |
| GET | `/api/roles/{role_id}/dependencies` | opcional |
| POST | `/api/role-dependencies/` | òc |
| DELETE | `/api/role-dependencies/{dependency_id}` | òc |
| GET | `/api/roles/{role_id}/conflicts` | opcional |
| POST | `/api/role-conflicts/` | òc |
| DELETE | `/api/role-conflicts/{conflict_id}` | òc |
| GET | `/api/roles/{role_id}/check-conflicts` | opcional |

## `search` → `/api/search`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/search/` | òc |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations/` | non |
| POST | `/api/shortfilms/{shortfilm_id}/locations/` | òc |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | òc |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | òc |

## `shortfilms` → `/api/shortfilms`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/shortfilms/` | non |
| POST | `/api/shortfilms/` | òc |
| GET | `/api/shortfilms/{shortfilm_id}` | non |
| PUT | `/api/shortfilms/{shortfilm_id}` | òc |
| DELETE | `/api/shortfilms/{shortfilm_id}` | òc |

## `uploads` → `/api/uploads`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | òc |
| POST | `/api/uploads/thumbnail` | òc |
| POST | `/api/uploads/video` | òc |
| POST | `/api/uploads/chat-image` | òc |

## `user_aliases` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases/` | non |
| POST | `/api/users/{user_id}/aliases/` | òc |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | òc |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | òc |

## `user_festival` → `/api/festivals`

| Metòde | Camin | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | òc |
| DELETE | `/api/festivals/{festival_id}/leave` | òc |
| GET | `/api/festivals/{festival_id}/members` | òc |
| GET | `/api/festivals/user/{user_id}/festivals` | òc |

## `user_roles` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles/` | òc |
| POST | `/api/users/{user_id}/roles/` | òc |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | òc |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | òc |
| GET | `/api/users/{user_id}/participant-tags/` | òc |
| POST | `/api/users/{user_id}/participant-tags/` | òc |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | òc |

## `users` → `/api/users`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/users/` | òc |
| GET | `/api/users/public` | non |
| GET | `/api/users/me` | òc |
| GET | `/api/users/me/export` | òc |
| DELETE | `/api/users/me` | òc |
| POST | `/api/users/` | òc |
| GET | `/api/users/{user_id}` | òc |
| GET | `/api/users/{user_id}/public` | non |
| PUT | `/api/users/{user_id}` | òc |
| DELETE | `/api/users/{user_id}` | òc |

## `validation_rules` → `/api`

| Metòde | Camin | Auth |
|---|---|---|
| GET | `/api/validation-rules/` | non |
| POST | `/api/validation-rules/` | òc |
| GET | `/api/validation-rules/{rule_id}` | non |
| PUT | `/api/validation-rules/{rule_id}` | òc |
| DELETE | `/api/validation-rules/{rule_id}` | òc |
| GET | `/api/validation-rule-groups/` | non |
| POST | `/api/validation-rule-groups/` | òc |

Total: 310 endpoints en 33 routers.