# API — Endpunktreferenz

[ES](../es/API.md) · [EN](../en/API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](../oc/API.md)

Erzeugt aus `app/routers/*.py` + Präfixen in `app/main.py`.
Interaktive Details: `/docs` (Swagger) und `/redoc` bei laufendem Backend.

## `admin` → `/api/admin`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/admin/stats` | ja |
| GET | `/api/admin/tables` | ja |
| GET | `/api/admin/audit-log` | ja |
| POST | `/api/admin/reset` | ja |

## `auth` → `/api/users`

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/api/users/login` | nein |

## `auth_sessions` → `/api/auth`

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | nein |
| GET | `/api/auth/sessions` | ja |
| DELETE | `/api/auth/sessions/{session_id}` | ja |
| POST | `/api/auth/sessions/revoke-all` | ja |

## `calendar` → `/api/calendar`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | optional |
| GET | `/api/calendar/agenda/export/ics` | optional |
| GET | `/api/calendar/settings` | nein |
| GET | `/api/calendar/admin/settings` | ja |
| PUT | `/api/calendar/admin/settings` | ja |
| POST | `/api/calendar/dav/token` | ja |
| GET | `/api/calendar/dav/token` | ja |
| DELETE | `/api/calendar/dav/token` | ja |

## `channels` → `/api/channels`

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/api/channels` | ja |
| GET | `/api/channels` | ja |
| GET | `/api/channels/public` | ja |
| GET | `/api/channels/{channel_id}` | ja |
| PUT | `/api/channels/{channel_id}` | ja |
| DELETE | `/api/channels/{channel_id}` | ja |
| POST | `/api/channels/{channel_id}/members` | ja |
| GET | `/api/channels/{channel_id}/members` | ja |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | ja |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | ja |

## `chat` → `/api/chat`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/chat/messages` | ja |
| POST | `/api/chat/messages` | ja |
| PUT | `/api/chat/messages/{message_id}/read` | ja |
| DELETE | `/api/chat/messages/{message_id}` | ja |
| GET | `/api/chat/groups` | ja |
| POST | `/api/chat/groups` | ja |
| GET | `/api/chat/groups/{group_id}` | ja |
| DELETE | `/api/chat/groups/{group_id}` | ja |
| GET | `/api/chat/groups/{group_id}/members` | ja |
| POST | `/api/chat/groups/{group_id}/members` | ja |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | ja |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | ja |
| WEBSOCKET | `/api/chat/ws` | token (query) |

## `committees` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees/` | optional |
| POST | `/api/festivals/{festival_id}/committees/` | ja |
| GET | `/api/committees/{committee_id}` | optional |
| PUT | `/api/committees/{committee_id}` | ja |
| DELETE | `/api/committees/{committee_id}` | ja |
| GET | `/api/committees/{committee_id}/members/` | optional |
| POST | `/api/committees/{committee_id}/members/` | ja |
| PUT | `/api/committee-members/{member_id}` | ja |
| DELETE | `/api/committee-members/{member_id}` | ja |

## `dav` → `/dav`

| Methode | Pfad | Auth |
|---|---|---|
| OPTIONS | `/dav/` | nein |
| OPTIONS | `/dav/{dav_path:path}` | nein |
| PROPFIND | `/dav/` | nein |
| GET | `/dav/{principal}/calendars/{collection}.ics` | nein |
| HEAD | `/dav/{principal}/calendars/{collection}.ics` | nein |
| GET | `/dav/{principal}/calendars/{collection}/{resource}` | nein |
| HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | nein |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | nein |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | nein |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | nein |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | nein |
| PROPFIND | `/dav/{principal}/calendars/{collection}/` | nein |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | nein |
| REPORT | `/dav/{principal}/calendars/{collection}/` | nein |
| REPORT | `/dav/{principal}/calendars/{collection}` | nein |
| PROPFIND | `/dav/{principal}/calendars/` | nein |
| PROPFIND | `/dav/{principal}/calendars` | nein |
| PROPFIND | `/dav/{principal}/` | nein |
| PROPFIND | `/dav/{principal}` | nein |
| REPORT | `/dav/{principal}/calendars/` | nein |
| REPORT | `/dav/{principal}/calendars` | nein |
| REPORT | `/dav/{principal}/` | nein |
| REPORT | `/dav/{principal}` | nein |
| API_ROUTE | `/dav/{write_path:path}` | nein |

## `delegations` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/delegations/` | optional |
| POST | `/api/delegations/` | ja |
| PUT | `/api/delegations/{delegation_id}` | ja |
| POST | `/api/delegations/{delegation_id}/revoke` | ja |
| GET | `/api/users/{user_id}/active-delegations` | optional |
| GET | `/api/role-transitions/` | ja |
| POST | `/api/role-transitions/` | ja |
| GET | `/api/users/{user_id}/role-transitions` | ja |
| GET | `/api/users/{user_id}/role-check` | ja |

## `events` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events/` | nein |
| GET | `/api/festivals/{festival_id}/events/export/ics` | ja |
| POST | `/api/festivals/{festival_id}/events/` | ja |
| GET | `/api/events/{event_id}` | nein |
| PUT | `/api/events/{event_id}` | ja |
| DELETE | `/api/events/{event_id}` | ja |
| GET | `/api/festivals/{festival_id}/events/programacion` | nein |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | ja |
| GET | `/api/events/{event_id}/screenings` | nein |
| PUT | `/api/events/{event_id}/screenings` | ja |
| GET | `/api/events/{event_id}/occupancy` | nein |
| GET | `/api/events/{event_id}/ticket-types/` | nein |
| POST | `/api/events/{event_id}/ticket-types/` | ja |
| PUT | `/api/ticket-types/{tt_id}` | ja |
| DELETE | `/api/ticket-types/{tt_id}` | ja |
| GET | `/api/events/{event_id}/seats/` | nein |
| POST | `/api/events/{event_id}/seats/bulk` | ja |
| GET | `/api/events/{event_id}/seats/sections` | nein |
| GET | `/api/events/{event_id}/seats/counts` | nein |
| PUT | `/api/seats/{seat_id}` | ja |
| POST | `/api/seats/{seat_id}/release` | ja |
| DELETE | `/api/seats/{seat_id}` | ja |
| GET | `/api/events/{event_id}/reservations/` | ja |
| POST | `/api/events/{event_id}/reservations/` | ja |
| PUT | `/api/reservations/{reservation_id}` | ja |
| POST | `/api/reservations/{reservation_id}/confirm` | ja |
| POST | `/api/reservations/{reservation_id}/cancel` | ja |
| DELETE | `/api/reservations/{reservation_id}` | ja |
| GET | `/api/events/{event_id}/attendees/` | ja |
| POST | `/api/events/{event_id}/attendees/` | ja |
| GET | `/api/attendees/{attendee_id}` | nein |
| PUT | `/api/attendees/{attendee_id}` | ja |
| POST | `/api/attendees/{attendee_id}/check-in` | ja |
| GET | `/api/events/{event_id}/attendees/counts` | nein |
| GET | `/api/events/{event_id}/attendees/export/csv` | ja |
| DELETE | `/api/attendees/{attendee_id}` | ja |
| POST | `/api/events/{event_id}/assign-vip` | ja |
| GET | `/api/users/me/events/` | ja |
| GET | `/api/users/me/events/{event_id}/reservation` | ja |
| GET | `/api/festivals/{festival_id}/awards/` | nein |
| POST | `/api/festivals/{festival_id}/awards/` | ja |
| PUT | `/api/awards/{award_id}` | ja |
| DELETE | `/api/awards/{award_id}` | ja |
| GET | `/api/users/{user_id}/awards/` | nein |
| GET | `/api/public/profile/{token}` | nein |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | nein |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks/` | nein |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | nein |
| POST | `/api/festivals/{festival_id}/rulebooks/` | ja |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | ja |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | ja |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | ja |

## `festivals` → `/api/festivals`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/festivals/` | nein |
| POST | `/api/festivals/` | ja |
| GET | `/api/festivals/{festival_id}` | nein |
| PUT | `/api/festivals/{festival_id}` | ja |
| DELETE | `/api/festivals/{festival_id}` | ja |
| POST | `/api/festivals/{festival_id}/images` | ja |
| DELETE | `/api/festivals/{festival_id}/images` | ja |
| GET | `/api/festivals/{festival_id}/locations` | nein |
| POST | `/api/festivals/{festival_id}/locations` | ja |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | ja |

## `form_definitions` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/forms/` | ja |
| POST | `/api/forms/` | ja |
| GET | `/api/forms/{form_id}` | ja |
| PUT | `/api/forms/{form_id}` | ja |
| DELETE | `/api/forms/{form_id}` | ja |
| POST | `/api/forms/{form_id}/clone` | ja |
| POST | `/api/forms/{form_id}/pages/` | ja |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | ja |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | ja |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields/` | ja |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | ja |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | ja |
| GET | `/api/forms/{form_id}/links/` | ja |
| POST | `/api/forms/{form_id}/links/` | ja |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | ja |
| GET | `/api/forms/public/{token}` | nein |
| POST | `/api/forms/public/{token}/submit` | optional |
| GET | `/api/forms/{form_id}/responses/` | ja |
| GET | `/api/forms/{form_id}/responses/export/csv` | ja |
| PUT | `/api/forms/responses/{response_id}` | ja |
| POST | `/api/forms/responses/{response_id}/approve` | ja |
| POST | `/api/forms/responses/{response_id}/reject` | ja |

## `keys` → `/api/users`

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | ja |
| GET | `/api/users/{user_id}/public-key` | ja |

## `location_images` → `/api/locations/{location_id}/images`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images/` | nein |
| POST | `/api/locations/{location_id}/images/upload` | ja |
| POST | `/api/locations/{location_id}/images/url` | ja |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | ja |

## `location_relations` → `/api/locations/{location_id}/relations`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations/` | nein |
| POST | `/api/locations/{location_id}/relations/` | ja |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | ja |
| POST | `/api/locations/{location_id}/relations/suggest` | ja |

## `location_tags` → `/api/locations/{location_id}/tags`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags/` | nein |
| POST | `/api/locations/{location_id}/tags/` | ja |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | ja |

## `locations` → `/api/locations`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/locations/` | nein |
| POST | `/api/locations/` | ja |
| GET | `/api/locations/{location_id}` | nein |
| PUT | `/api/locations/{location_id}` | ja |
| PUT | `/api/locations/{location_id}/badge` | ja |
| DELETE | `/api/locations/{location_id}` | ja |

## `notifications` → `/api/notifications`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/notifications/` | ja |
| GET | `/api/notifications/unread-count` | ja |
| PUT | `/api/notifications/{notification_id}/read` | ja |
| PUT | `/api/notifications/read-all` | ja |
| DELETE | `/api/notifications/{notification_id}` | ja |

## `participant_tags` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/participant-tags/` | nein |
| POST | `/api/participant-tags/` | ja |
| GET | `/api/participant-tags/{tag_id}` | nein |
| PUT | `/api/participant-tags/{tag_id}` | ja |
| DELETE | `/api/participant-tags/{tag_id}` | ja |
| GET | `/api/festivals/{festival_id}/participant-tags/` | nein |
| POST | `/api/festivals/{festival_id}/participant-tags/` | ja |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | ja |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | ja |

## `payments` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | ja |
| GET | `/api/payments/` | ja |
| GET | `/api/payments/{payment_id}` | ja |
| POST | `/api/payments/{payment_id}/confirm` | ja |
| POST | `/api/payments/{payment_id}/refund` | ja |
| POST | `/api/payments/webhook/mock` | nein |

## `registration_forms` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms/` | ja |
| POST | `/api/festivals/{festival_id}/registration-forms/` | ja |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | ja |
| GET | `/api/registration-forms/{form_id}` | ja |
| PUT | `/api/registration-forms/{form_id}` | ja |
| DELETE | `/api/registration-forms/{form_id}` | ja |
| GET | `/api/registration-forms/{form_id}/registrations/` | ja |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | ja |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | ja |
| GET | `/api/public/forms/{token}` | nein |
| POST | `/api/public/forms/{token}/register` | optional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | ja |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | ja |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | ja |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | ja |
| GET | `/api/registration-forms/{form_id}/links/` | ja |
| POST | `/api/registration-forms/{form_id}/links/` | ja |
| DELETE | `/api/registration-form-links/{link_id}` | ja |
| POST | `/api/registration-form-links/{link_id}/regenerate` | ja |
| GET | `/api/festivals/{festival_id}/registrations/` | ja |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | ja |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | ja |
| GET | `/api/users/{user_id}/registrations/` | ja |
| PUT | `/api/registrations/{registration_id}` | ja |
| POST | `/api/registrations/{registration_id}/approve` | ja |
| POST | `/api/registrations/{registration_id}/reject` | ja |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | ja |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | ja |
| DELETE | `/api/registrations/{registration_id}` | ja |
| POST | `/api/registration-forms/{form_id}/sections/` | ja |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | ja |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | ja |

## `role_groups` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/role-groups/` | nein |
| POST | `/api/role-groups/` | ja |
| GET | `/api/role-groups/{group_id}` | nein |
| PUT | `/api/role-groups/{group_id}` | ja |
| DELETE | `/api/role-groups/{group_id}` | ja |
| GET | `/api/role-groups/{group_id}/memberships/` | nein |
| POST | `/api/role-groups/{group_id}/memberships/` | ja |
| PUT | `/api/role-group-memberships/{membership_id}` | ja |
| DELETE | `/api/role-group-memberships/{membership_id}` | ja |

## `roles` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/roles/` | ja |
| POST | `/api/roles/` | ja |
| GET | `/api/roles/hierarchy/` | optional |
| GET | `/api/roles/{role_id}` | optional |
| PUT | `/api/roles/{role_id}` | ja |
| DELETE | `/api/roles/{role_id}` | ja |
| GET | `/api/festivals/{festival_id}/roles/` | optional |
| POST | `/api/festivals/{festival_id}/roles/` | ja |
| POST | `/api/festivals/{festival_id}/roles/initialize` | ja |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | ja |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | ja |
| GET | `/api/roles/{role_id}/dependencies` | optional |
| POST | `/api/role-dependencies/` | ja |
| DELETE | `/api/role-dependencies/{dependency_id}` | ja |
| GET | `/api/roles/{role_id}/conflicts` | optional |
| POST | `/api/role-conflicts/` | ja |
| DELETE | `/api/role-conflicts/{conflict_id}` | ja |
| GET | `/api/roles/{role_id}/check-conflicts` | optional |

## `search` → `/api/search`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/search/` | ja |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations/` | nein |
| POST | `/api/shortfilms/{shortfilm_id}/locations/` | ja |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | ja |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | ja |

## `shortfilms` → `/api/shortfilms`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/shortfilms/` | nein |
| POST | `/api/shortfilms/` | ja |
| GET | `/api/shortfilms/{shortfilm_id}` | nein |
| PUT | `/api/shortfilms/{shortfilm_id}` | ja |
| DELETE | `/api/shortfilms/{shortfilm_id}` | ja |

## `uploads` → `/api/uploads`

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | ja |
| POST | `/api/uploads/thumbnail` | ja |
| POST | `/api/uploads/video` | ja |
| POST | `/api/uploads/chat-image` | ja |

## `user_aliases` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases/` | nein |
| POST | `/api/users/{user_id}/aliases/` | ja |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | ja |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | ja |

## `user_festival` → `/api/festivals`

| Methode | Pfad | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | ja |
| DELETE | `/api/festivals/{festival_id}/leave` | ja |
| GET | `/api/festivals/{festival_id}/members` | ja |
| GET | `/api/festivals/user/{user_id}/festivals` | ja |

## `user_roles` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles/` | ja |
| POST | `/api/users/{user_id}/roles/` | ja |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | ja |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | ja |
| GET | `/api/users/{user_id}/participant-tags/` | ja |
| POST | `/api/users/{user_id}/participant-tags/` | ja |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | ja |

## `users` → `/api/users`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/users/` | ja |
| GET | `/api/users/public` | nein |
| GET | `/api/users/me` | ja |
| GET | `/api/users/me/export` | ja |
| DELETE | `/api/users/me` | ja |
| POST | `/api/users/` | ja |
| GET | `/api/users/{user_id}` | ja |
| GET | `/api/users/{user_id}/public` | nein |
| PUT | `/api/users/{user_id}` | ja |
| DELETE | `/api/users/{user_id}` | ja |

## `validation_rules` → `/api`

| Methode | Pfad | Auth |
|---|---|---|
| GET | `/api/validation-rules/` | nein |
| POST | `/api/validation-rules/` | ja |
| GET | `/api/validation-rules/{rule_id}` | nein |
| PUT | `/api/validation-rules/{rule_id}` | ja |
| DELETE | `/api/validation-rules/{rule_id}` | ja |
| GET | `/api/validation-rule-groups/` | nein |
| POST | `/api/validation-rule-groups/` | ja |

Gesamt: 310 Endpunkte in 33 Routern.