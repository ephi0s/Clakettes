# API — référence des endpoints

[ES](../es/API.md) · [EN](../en/API.md) · [FR](../fr/API.md) · [DE](../de/API.md) · [IT](../it/API.md) · [CA](../ca/API.md) · [EU](../eu/API.md) · [GL](../gl/API.md) · [OC](../oc/API.md)

Généré depuis `app/routers/*.py` + préfixes de `app/main.py`.
Détail interactif : `/docs` (Swagger) et `/redoc` avec le backend lancé.

## `admin` → `/api/admin`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/admin/stats` | oui |
| GET | `/api/admin/tables` | oui |
| GET | `/api/admin/audit-log` | oui |
| POST | `/api/admin/reset` | oui |

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

## `calendar` → `/api/calendar`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | optionnel |
| GET | `/api/calendar/agenda/export/ics` | optionnel |
| GET | `/api/calendar/settings` | non |
| GET | `/api/calendar/admin/settings` | oui |
| PUT | `/api/calendar/admin/settings` | oui |
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
| WEBSOCKET | `/api/chat/ws` | token (query) |

## `committees` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees/` | optionnel |
| POST | `/api/festivals/{festival_id}/committees/` | oui |
| GET | `/api/committees/{committee_id}` | optionnel |
| PUT | `/api/committees/{committee_id}` | oui |
| DELETE | `/api/committees/{committee_id}` | oui |
| GET | `/api/committees/{committee_id}/members/` | optionnel |
| POST | `/api/committees/{committee_id}/members/` | oui |
| PUT | `/api/committee-members/{member_id}` | oui |
| DELETE | `/api/committee-members/{member_id}` | oui |

## `dav` → `/dav`

| Méthode | Chemin | Auth |
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

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/delegations/` | optionnel |
| POST | `/api/delegations/` | oui |
| PUT | `/api/delegations/{delegation_id}` | oui |
| POST | `/api/delegations/{delegation_id}/revoke` | oui |
| GET | `/api/users/{user_id}/active-delegations` | optionnel |
| GET | `/api/role-transitions/` | oui |
| POST | `/api/role-transitions/` | oui |
| GET | `/api/users/{user_id}/role-transitions` | oui |
| GET | `/api/users/{user_id}/role-check` | oui |

## `events` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events/` | non |
| GET | `/api/festivals/{festival_id}/events/export/ics` | oui |
| POST | `/api/festivals/{festival_id}/events/` | oui |
| GET | `/api/events/{event_id}` | non |
| PUT | `/api/events/{event_id}` | oui |
| DELETE | `/api/events/{event_id}` | oui |
| GET | `/api/festivals/{festival_id}/events/programacion` | non |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | oui |
| GET | `/api/events/{event_id}/screenings` | non |
| PUT | `/api/events/{event_id}/screenings` | oui |
| GET | `/api/events/{event_id}/occupancy` | non |
| GET | `/api/events/{event_id}/ticket-types/` | non |
| POST | `/api/events/{event_id}/ticket-types/` | oui |
| PUT | `/api/ticket-types/{tt_id}` | oui |
| DELETE | `/api/ticket-types/{tt_id}` | oui |
| GET | `/api/events/{event_id}/seats/` | non |
| POST | `/api/events/{event_id}/seats/bulk` | oui |
| GET | `/api/events/{event_id}/seats/sections` | non |
| GET | `/api/events/{event_id}/seats/counts` | non |
| PUT | `/api/seats/{seat_id}` | oui |
| POST | `/api/seats/{seat_id}/release` | oui |
| DELETE | `/api/seats/{seat_id}` | oui |
| GET | `/api/events/{event_id}/reservations/` | oui |
| POST | `/api/events/{event_id}/reservations/` | oui |
| PUT | `/api/reservations/{reservation_id}` | oui |
| POST | `/api/reservations/{reservation_id}/confirm` | oui |
| POST | `/api/reservations/{reservation_id}/cancel` | oui |
| DELETE | `/api/reservations/{reservation_id}` | oui |
| GET | `/api/events/{event_id}/attendees/` | oui |
| POST | `/api/events/{event_id}/attendees/` | oui |
| GET | `/api/attendees/{attendee_id}` | non |
| PUT | `/api/attendees/{attendee_id}` | oui |
| POST | `/api/attendees/{attendee_id}/check-in` | oui |
| GET | `/api/events/{event_id}/attendees/counts` | non |
| GET | `/api/events/{event_id}/attendees/export/csv` | oui |
| DELETE | `/api/attendees/{attendee_id}` | oui |
| POST | `/api/events/{event_id}/assign-vip` | oui |
| GET | `/api/users/me/events/` | oui |
| GET | `/api/users/me/events/{event_id}/reservation` | oui |
| GET | `/api/festivals/{festival_id}/awards/` | non |
| POST | `/api/festivals/{festival_id}/awards/` | oui |
| PUT | `/api/awards/{award_id}` | oui |
| DELETE | `/api/awards/{award_id}` | oui |
| GET | `/api/users/{user_id}/awards/` | non |
| GET | `/api/public/profile/{token}` | non |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | non |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks/` | non |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | non |
| POST | `/api/festivals/{festival_id}/rulebooks/` | oui |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | oui |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | oui |

## `festivals` → `/api/festivals`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/` | non |
| POST | `/api/festivals/` | oui |
| GET | `/api/festivals/{festival_id}` | non |
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
| GET | `/api/forms/` | oui |
| POST | `/api/forms/` | oui |
| GET | `/api/forms/{form_id}` | oui |
| PUT | `/api/forms/{form_id}` | oui |
| DELETE | `/api/forms/{form_id}` | oui |
| POST | `/api/forms/{form_id}/clone` | oui |
| POST | `/api/forms/{form_id}/pages/` | oui |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | oui |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | oui |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields/` | oui |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | oui |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | oui |
| GET | `/api/forms/{form_id}/links/` | oui |
| POST | `/api/forms/{form_id}/links/` | oui |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | oui |
| GET | `/api/forms/public/{token}` | non |
| POST | `/api/forms/public/{token}/submit` | optionnel |
| GET | `/api/forms/{form_id}/responses/` | oui |
| GET | `/api/forms/{form_id}/responses/export/csv` | oui |
| PUT | `/api/forms/responses/{response_id}` | oui |
| POST | `/api/forms/responses/{response_id}/approve` | oui |
| POST | `/api/forms/responses/{response_id}/reject` | oui |

## `keys` → `/api/users`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | oui |
| GET | `/api/users/{user_id}/public-key` | oui |

## `location_images` → `/api/locations/{location_id}/images`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images/` | non |
| POST | `/api/locations/{location_id}/images/upload` | oui |
| POST | `/api/locations/{location_id}/images/url` | oui |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | oui |

## `location_relations` → `/api/locations/{location_id}/relations`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations/` | non |
| POST | `/api/locations/{location_id}/relations/` | oui |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | oui |
| POST | `/api/locations/{location_id}/relations/suggest` | oui |

## `location_tags` → `/api/locations/{location_id}/tags`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags/` | non |
| POST | `/api/locations/{location_id}/tags/` | oui |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | oui |

## `locations` → `/api/locations`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/locations/` | non |
| POST | `/api/locations/` | oui |
| GET | `/api/locations/{location_id}` | non |
| PUT | `/api/locations/{location_id}` | oui |
| PUT | `/api/locations/{location_id}/badge` | oui |
| DELETE | `/api/locations/{location_id}` | oui |

## `notifications` → `/api/notifications`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/notifications/` | oui |
| GET | `/api/notifications/unread-count` | oui |
| PUT | `/api/notifications/{notification_id}/read` | oui |
| PUT | `/api/notifications/read-all` | oui |
| DELETE | `/api/notifications/{notification_id}` | oui |

## `participant_tags` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/participant-tags/` | non |
| POST | `/api/participant-tags/` | oui |
| GET | `/api/participant-tags/{tag_id}` | non |
| PUT | `/api/participant-tags/{tag_id}` | oui |
| DELETE | `/api/participant-tags/{tag_id}` | oui |
| GET | `/api/festivals/{festival_id}/participant-tags/` | non |
| POST | `/api/festivals/{festival_id}/participant-tags/` | oui |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | oui |

## `payments` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | oui |
| GET | `/api/payments/` | oui |
| GET | `/api/payments/{payment_id}` | oui |
| POST | `/api/payments/{payment_id}/confirm` | oui |
| POST | `/api/payments/{payment_id}/refund` | oui |
| POST | `/api/payments/webhook/mock` | non |

## `registration_forms` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms/` | oui |
| POST | `/api/festivals/{festival_id}/registration-forms/` | oui |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | oui |
| GET | `/api/registration-forms/{form_id}` | oui |
| PUT | `/api/registration-forms/{form_id}` | oui |
| DELETE | `/api/registration-forms/{form_id}` | oui |
| GET | `/api/registration-forms/{form_id}/registrations/` | oui |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | oui |
| GET | `/api/public/forms/{token}` | non |
| POST | `/api/public/forms/{token}/register` | optionnel |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | oui |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | oui |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | oui |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | oui |
| GET | `/api/registration-forms/{form_id}/links/` | oui |
| POST | `/api/registration-forms/{form_id}/links/` | oui |
| DELETE | `/api/registration-form-links/{link_id}` | oui |
| POST | `/api/registration-form-links/{link_id}/regenerate` | oui |
| GET | `/api/festivals/{festival_id}/registrations/` | oui |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | oui |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | oui |
| GET | `/api/users/{user_id}/registrations/` | oui |
| PUT | `/api/registrations/{registration_id}` | oui |
| POST | `/api/registrations/{registration_id}/approve` | oui |
| POST | `/api/registrations/{registration_id}/reject` | oui |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | oui |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | oui |
| DELETE | `/api/registrations/{registration_id}` | oui |
| POST | `/api/registration-forms/{form_id}/sections/` | oui |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | oui |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | oui |

## `role_groups` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/role-groups/` | non |
| POST | `/api/role-groups/` | oui |
| GET | `/api/role-groups/{group_id}` | non |
| PUT | `/api/role-groups/{group_id}` | oui |
| DELETE | `/api/role-groups/{group_id}` | oui |
| GET | `/api/role-groups/{group_id}/memberships/` | non |
| POST | `/api/role-groups/{group_id}/memberships/` | oui |
| PUT | `/api/role-group-memberships/{membership_id}` | oui |
| DELETE | `/api/role-group-memberships/{membership_id}` | oui |

## `roles` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/roles/` | oui |
| POST | `/api/roles/` | oui |
| GET | `/api/roles/hierarchy/` | optionnel |
| GET | `/api/roles/{role_id}` | optionnel |
| PUT | `/api/roles/{role_id}` | oui |
| DELETE | `/api/roles/{role_id}` | oui |
| GET | `/api/festivals/{festival_id}/roles/` | optionnel |
| POST | `/api/festivals/{festival_id}/roles/` | oui |
| POST | `/api/festivals/{festival_id}/roles/initialize` | oui |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | oui |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | oui |
| GET | `/api/roles/{role_id}/dependencies` | optionnel |
| POST | `/api/role-dependencies/` | oui |
| DELETE | `/api/role-dependencies/{dependency_id}` | oui |
| GET | `/api/roles/{role_id}/conflicts` | optionnel |
| POST | `/api/role-conflicts/` | oui |
| DELETE | `/api/role-conflicts/{conflict_id}` | oui |
| GET | `/api/roles/{role_id}/check-conflicts` | optionnel |

## `search` → `/api/search`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/search/` | oui |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations/` | non |
| POST | `/api/shortfilms/{shortfilm_id}/locations/` | oui |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | oui |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | oui |

## `shortfilms` → `/api/shortfilms`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/shortfilms/` | non |
| POST | `/api/shortfilms/` | oui |
| GET | `/api/shortfilms/{shortfilm_id}` | non |
| PUT | `/api/shortfilms/{shortfilm_id}` | oui |
| DELETE | `/api/shortfilms/{shortfilm_id}` | oui |

## `uploads` → `/api/uploads`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | oui |
| POST | `/api/uploads/thumbnail` | oui |
| POST | `/api/uploads/video` | oui |
| POST | `/api/uploads/chat-image` | oui |

## `user_aliases` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases/` | non |
| POST | `/api/users/{user_id}/aliases/` | oui |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | oui |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | oui |

## `user_festival` → `/api/festivals`

| Méthode | Chemin | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | oui |
| DELETE | `/api/festivals/{festival_id}/leave` | oui |
| GET | `/api/festivals/{festival_id}/members` | oui |
| GET | `/api/festivals/user/{user_id}/festivals` | oui |

## `user_roles` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles/` | oui |
| POST | `/api/users/{user_id}/roles/` | oui |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | oui |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | oui |
| GET | `/api/users/{user_id}/participant-tags/` | oui |
| POST | `/api/users/{user_id}/participant-tags/` | oui |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | oui |

## `users` → `/api/users`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/users/` | oui |
| GET | `/api/users/public` | non |
| GET | `/api/users/me` | oui |
| GET | `/api/users/me/export` | oui |
| DELETE | `/api/users/me` | oui |
| POST | `/api/users/` | oui |
| GET | `/api/users/{user_id}` | oui |
| GET | `/api/users/{user_id}/public` | non |
| PUT | `/api/users/{user_id}` | oui |
| DELETE | `/api/users/{user_id}` | oui |

## `validation_rules` → `/api`

| Méthode | Chemin | Auth |
|---|---|---|
| GET | `/api/validation-rules/` | non |
| POST | `/api/validation-rules/` | oui |
| GET | `/api/validation-rules/{rule_id}` | non |
| PUT | `/api/validation-rules/{rule_id}` | oui |
| DELETE | `/api/validation-rules/{rule_id}` | oui |
| GET | `/api/validation-rule-groups/` | non |
| POST | `/api/validation-rule-groups/` | oui |

Total : 310 endpoints dans 33 routers.