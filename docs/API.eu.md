# API — endpointen erreferentzia

[ES](API.md) · [EN](API.en.md) · [FR](API.fr.md) · [DE](API.de.md) · [IT](API.it.md) · [CA](API.ca.md) · [EU](API.eu.md) · [GL](API.gl.md) · [OC](API.oc.md)

`app/routers/*.py` + `app/main.py`-ko aurrizkietatik sortua.
Xehetasun interaktiboa: `/docs` (Swagger) eta `/redoc` backend-a martxan.

## `admin` → `/api/admin`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/admin/stats` | bai |
| GET | `/api/admin/tables` | bai |
| GET | `/api/admin/audit-log` | bai |
| POST | `/api/admin/reset` | bai |

## `auth` → `/api/users`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| POST | `/api/users/login` | ez |

## `auth_sessions` → `/api/auth`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | ez |
| GET | `/api/auth/sessions` | bai |
| DELETE | `/api/auth/sessions/{session_id}` | bai |
| POST | `/api/auth/sessions/revoke-all` | bai |

## `calendar` → `/api/calendar`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | aukerakoa |
| GET | `/api/calendar/agenda/export/ics` | aukerakoa |
| GET | `/api/calendar/settings` | ez |
| GET | `/api/calendar/admin/settings` | bai |
| PUT | `/api/calendar/admin/settings` | bai |
| POST | `/api/calendar/dav/token` | bai |
| GET | `/api/calendar/dav/token` | bai |
| DELETE | `/api/calendar/dav/token` | bai |

## `channels` → `/api/channels`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| POST | `/api/channels` | bai |
| GET | `/api/channels` | bai |
| GET | `/api/channels/public` | bai |
| GET | `/api/channels/{channel_id}` | bai |
| PUT | `/api/channels/{channel_id}` | bai |
| DELETE | `/api/channels/{channel_id}` | bai |
| POST | `/api/channels/{channel_id}/members` | bai |
| GET | `/api/channels/{channel_id}/members` | bai |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | bai |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | bai |

## `chat` → `/api/chat`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/chat/messages` | bai |
| POST | `/api/chat/messages` | bai |
| PUT | `/api/chat/messages/{message_id}/read` | bai |
| DELETE | `/api/chat/messages/{message_id}` | bai |
| GET | `/api/chat/groups` | bai |
| POST | `/api/chat/groups` | bai |
| GET | `/api/chat/groups/{group_id}` | bai |
| DELETE | `/api/chat/groups/{group_id}` | bai |
| GET | `/api/chat/groups/{group_id}/members` | bai |
| POST | `/api/chat/groups/{group_id}/members` | bai |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | bai |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | bai |
| WEBSOCKET | `/api/chat/ws` | token (query) |

## `committees` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees/` | aukerakoa |
| POST | `/api/festivals/{festival_id}/committees/` | bai |
| GET | `/api/committees/{committee_id}` | aukerakoa |
| PUT | `/api/committees/{committee_id}` | bai |
| DELETE | `/api/committees/{committee_id}` | bai |
| GET | `/api/committees/{committee_id}/members/` | aukerakoa |
| POST | `/api/committees/{committee_id}/members/` | bai |
| PUT | `/api/committee-members/{member_id}` | bai |
| DELETE | `/api/committee-members/{member_id}` | bai |

## `dav` → `/dav`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| OPTIONS | `/dav/` | ez |
| OPTIONS | `/dav/{dav_path:path}` | ez |
| PROPFIND | `/dav/` | ez |
| GET | `/dav/{principal}/calendars/{collection}.ics` | ez |
| HEAD | `/dav/{principal}/calendars/{collection}.ics` | ez |
| GET | `/dav/{principal}/calendars/{collection}/{resource}` | ez |
| HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | ez |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | ez |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | ez |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | ez |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | ez |
| PROPFIND | `/dav/{principal}/calendars/{collection}/` | ez |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | ez |
| REPORT | `/dav/{principal}/calendars/{collection}/` | ez |
| REPORT | `/dav/{principal}/calendars/{collection}` | ez |
| PROPFIND | `/dav/{principal}/calendars/` | ez |
| PROPFIND | `/dav/{principal}/calendars` | ez |
| PROPFIND | `/dav/{principal}/` | ez |
| PROPFIND | `/dav/{principal}` | ez |
| REPORT | `/dav/{principal}/calendars/` | ez |
| REPORT | `/dav/{principal}/calendars` | ez |
| REPORT | `/dav/{principal}/` | ez |
| REPORT | `/dav/{principal}` | ez |
| API_ROUTE | `/dav/{write_path:path}` | ez |

## `delegations` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/delegations/` | aukerakoa |
| POST | `/api/delegations/` | bai |
| PUT | `/api/delegations/{delegation_id}` | bai |
| POST | `/api/delegations/{delegation_id}/revoke` | bai |
| GET | `/api/users/{user_id}/active-delegations` | aukerakoa |
| GET | `/api/role-transitions/` | bai |
| POST | `/api/role-transitions/` | bai |
| GET | `/api/users/{user_id}/role-transitions` | bai |
| GET | `/api/users/{user_id}/role-check` | bai |

## `events` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events/` | ez |
| GET | `/api/festivals/{festival_id}/events/export/ics` | bai |
| POST | `/api/festivals/{festival_id}/events/` | bai |
| GET | `/api/events/{event_id}` | ez |
| PUT | `/api/events/{event_id}` | bai |
| DELETE | `/api/events/{event_id}` | bai |
| GET | `/api/festivals/{festival_id}/events/programacion` | ez |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | bai |
| GET | `/api/events/{event_id}/screenings` | ez |
| PUT | `/api/events/{event_id}/screenings` | bai |
| GET | `/api/events/{event_id}/occupancy` | ez |
| GET | `/api/events/{event_id}/ticket-types/` | ez |
| POST | `/api/events/{event_id}/ticket-types/` | bai |
| PUT | `/api/ticket-types/{tt_id}` | bai |
| DELETE | `/api/ticket-types/{tt_id}` | bai |
| GET | `/api/events/{event_id}/seats/` | ez |
| POST | `/api/events/{event_id}/seats/bulk` | bai |
| GET | `/api/events/{event_id}/seats/sections` | ez |
| GET | `/api/events/{event_id}/seats/counts` | ez |
| PUT | `/api/seats/{seat_id}` | bai |
| POST | `/api/seats/{seat_id}/release` | bai |
| DELETE | `/api/seats/{seat_id}` | bai |
| GET | `/api/events/{event_id}/reservations/` | bai |
| POST | `/api/events/{event_id}/reservations/` | bai |
| PUT | `/api/reservations/{reservation_id}` | bai |
| POST | `/api/reservations/{reservation_id}/confirm` | bai |
| POST | `/api/reservations/{reservation_id}/cancel` | bai |
| DELETE | `/api/reservations/{reservation_id}` | bai |
| GET | `/api/events/{event_id}/attendees/` | bai |
| POST | `/api/events/{event_id}/attendees/` | bai |
| GET | `/api/attendees/{attendee_id}` | ez |
| PUT | `/api/attendees/{attendee_id}` | bai |
| POST | `/api/attendees/{attendee_id}/check-in` | bai |
| GET | `/api/events/{event_id}/attendees/counts` | ez |
| GET | `/api/events/{event_id}/attendees/export/csv` | bai |
| DELETE | `/api/attendees/{attendee_id}` | bai |
| POST | `/api/events/{event_id}/assign-vip` | bai |
| GET | `/api/users/me/events/` | bai |
| GET | `/api/users/me/events/{event_id}/reservation` | bai |
| GET | `/api/festivals/{festival_id}/awards/` | ez |
| POST | `/api/festivals/{festival_id}/awards/` | bai |
| PUT | `/api/awards/{award_id}` | bai |
| DELETE | `/api/awards/{award_id}` | bai |
| GET | `/api/users/{user_id}/awards/` | ez |
| GET | `/api/public/profile/{token}` | ez |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | ez |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks/` | ez |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | ez |
| POST | `/api/festivals/{festival_id}/rulebooks/` | bai |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | bai |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | bai |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | bai |

## `festivals` → `/api/festivals`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/festivals/` | ez |
| POST | `/api/festivals/` | bai |
| GET | `/api/festivals/{festival_id}` | ez |
| PUT | `/api/festivals/{festival_id}` | bai |
| DELETE | `/api/festivals/{festival_id}` | bai |
| POST | `/api/festivals/{festival_id}/images` | bai |
| DELETE | `/api/festivals/{festival_id}/images` | bai |
| GET | `/api/festivals/{festival_id}/locations` | ez |
| POST | `/api/festivals/{festival_id}/locations` | bai |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | bai |

## `form_definitions` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/forms/` | bai |
| POST | `/api/forms/` | bai |
| GET | `/api/forms/{form_id}` | bai |
| PUT | `/api/forms/{form_id}` | bai |
| DELETE | `/api/forms/{form_id}` | bai |
| POST | `/api/forms/{form_id}/clone` | bai |
| POST | `/api/forms/{form_id}/pages/` | bai |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | bai |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | bai |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields/` | bai |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | bai |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | bai |
| GET | `/api/forms/{form_id}/links/` | bai |
| POST | `/api/forms/{form_id}/links/` | bai |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | bai |
| GET | `/api/forms/public/{token}` | ez |
| POST | `/api/forms/public/{token}/submit` | aukerakoa |
| GET | `/api/forms/{form_id}/responses/` | bai |
| GET | `/api/forms/{form_id}/responses/export/csv` | bai |
| PUT | `/api/forms/responses/{response_id}` | bai |
| POST | `/api/forms/responses/{response_id}/approve` | bai |
| POST | `/api/forms/responses/{response_id}/reject` | bai |

## `keys` → `/api/users`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | bai |
| GET | `/api/users/{user_id}/public-key` | bai |

## `location_images` → `/api/locations/{location_id}/images`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images/` | ez |
| POST | `/api/locations/{location_id}/images/upload` | bai |
| POST | `/api/locations/{location_id}/images/url` | bai |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | bai |

## `location_relations` → `/api/locations/{location_id}/relations`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations/` | ez |
| POST | `/api/locations/{location_id}/relations/` | bai |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | bai |
| POST | `/api/locations/{location_id}/relations/suggest` | bai |

## `location_tags` → `/api/locations/{location_id}/tags`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags/` | ez |
| POST | `/api/locations/{location_id}/tags/` | bai |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | bai |

## `locations` → `/api/locations`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/locations/` | ez |
| POST | `/api/locations/` | bai |
| GET | `/api/locations/{location_id}` | ez |
| PUT | `/api/locations/{location_id}` | bai |
| PUT | `/api/locations/{location_id}/badge` | bai |
| DELETE | `/api/locations/{location_id}` | bai |

## `notifications` → `/api/notifications`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/notifications/` | bai |
| GET | `/api/notifications/unread-count` | bai |
| PUT | `/api/notifications/{notification_id}/read` | bai |
| PUT | `/api/notifications/read-all` | bai |
| DELETE | `/api/notifications/{notification_id}` | bai |

## `participant_tags` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/participant-tags/` | ez |
| POST | `/api/participant-tags/` | bai |
| GET | `/api/participant-tags/{tag_id}` | ez |
| PUT | `/api/participant-tags/{tag_id}` | bai |
| DELETE | `/api/participant-tags/{tag_id}` | bai |
| GET | `/api/festivals/{festival_id}/participant-tags/` | ez |
| POST | `/api/festivals/{festival_id}/participant-tags/` | bai |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | bai |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | bai |

## `payments` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | bai |
| GET | `/api/payments/` | bai |
| GET | `/api/payments/{payment_id}` | bai |
| POST | `/api/payments/{payment_id}/confirm` | bai |
| POST | `/api/payments/{payment_id}/refund` | bai |
| POST | `/api/payments/webhook/mock` | ez |

## `registration_forms` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms/` | bai |
| POST | `/api/festivals/{festival_id}/registration-forms/` | bai |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | bai |
| GET | `/api/registration-forms/{form_id}` | bai |
| PUT | `/api/registration-forms/{form_id}` | bai |
| DELETE | `/api/registration-forms/{form_id}` | bai |
| GET | `/api/registration-forms/{form_id}/registrations/` | bai |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | bai |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | bai |
| GET | `/api/public/forms/{token}` | ez |
| POST | `/api/public/forms/{token}/register` | aukerakoa |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | bai |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | bai |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | bai |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | bai |
| GET | `/api/registration-forms/{form_id}/links/` | bai |
| POST | `/api/registration-forms/{form_id}/links/` | bai |
| DELETE | `/api/registration-form-links/{link_id}` | bai |
| POST | `/api/registration-form-links/{link_id}/regenerate` | bai |
| GET | `/api/festivals/{festival_id}/registrations/` | bai |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | bai |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | bai |
| GET | `/api/users/{user_id}/registrations/` | bai |
| PUT | `/api/registrations/{registration_id}` | bai |
| POST | `/api/registrations/{registration_id}/approve` | bai |
| POST | `/api/registrations/{registration_id}/reject` | bai |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | bai |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | bai |
| DELETE | `/api/registrations/{registration_id}` | bai |
| POST | `/api/registration-forms/{form_id}/sections/` | bai |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | bai |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | bai |

## `role_groups` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/role-groups/` | ez |
| POST | `/api/role-groups/` | bai |
| GET | `/api/role-groups/{group_id}` | ez |
| PUT | `/api/role-groups/{group_id}` | bai |
| DELETE | `/api/role-groups/{group_id}` | bai |
| GET | `/api/role-groups/{group_id}/memberships/` | ez |
| POST | `/api/role-groups/{group_id}/memberships/` | bai |
| PUT | `/api/role-group-memberships/{membership_id}` | bai |
| DELETE | `/api/role-group-memberships/{membership_id}` | bai |

## `roles` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/roles/` | bai |
| POST | `/api/roles/` | bai |
| GET | `/api/roles/hierarchy/` | aukerakoa |
| GET | `/api/roles/{role_id}` | aukerakoa |
| PUT | `/api/roles/{role_id}` | bai |
| DELETE | `/api/roles/{role_id}` | bai |
| GET | `/api/festivals/{festival_id}/roles/` | aukerakoa |
| POST | `/api/festivals/{festival_id}/roles/` | bai |
| POST | `/api/festivals/{festival_id}/roles/initialize` | bai |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | bai |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | bai |
| GET | `/api/roles/{role_id}/dependencies` | aukerakoa |
| POST | `/api/role-dependencies/` | bai |
| DELETE | `/api/role-dependencies/{dependency_id}` | bai |
| GET | `/api/roles/{role_id}/conflicts` | aukerakoa |
| POST | `/api/role-conflicts/` | bai |
| DELETE | `/api/role-conflicts/{conflict_id}` | bai |
| GET | `/api/roles/{role_id}/check-conflicts` | aukerakoa |

## `search` → `/api/search`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/search/` | bai |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations/` | ez |
| POST | `/api/shortfilms/{shortfilm_id}/locations/` | bai |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | bai |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | bai |

## `shortfilms` → `/api/shortfilms`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/shortfilms/` | ez |
| POST | `/api/shortfilms/` | bai |
| GET | `/api/shortfilms/{shortfilm_id}` | ez |
| PUT | `/api/shortfilms/{shortfilm_id}` | bai |
| DELETE | `/api/shortfilms/{shortfilm_id}` | bai |

## `uploads` → `/api/uploads`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | bai |
| POST | `/api/uploads/thumbnail` | bai |
| POST | `/api/uploads/video` | bai |
| POST | `/api/uploads/chat-image` | bai |

## `user_aliases` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases/` | ez |
| POST | `/api/users/{user_id}/aliases/` | bai |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | bai |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | bai |

## `user_festival` → `/api/festivals`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | bai |
| DELETE | `/api/festivals/{festival_id}/leave` | bai |
| GET | `/api/festivals/{festival_id}/members` | bai |
| GET | `/api/festivals/user/{user_id}/festivals` | bai |

## `user_roles` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles/` | bai |
| POST | `/api/users/{user_id}/roles/` | bai |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | bai |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | bai |
| GET | `/api/users/{user_id}/participant-tags/` | bai |
| POST | `/api/users/{user_id}/participant-tags/` | bai |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | bai |

## `users` → `/api/users`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/users/` | bai |
| GET | `/api/users/public` | ez |
| GET | `/api/users/me` | bai |
| GET | `/api/users/me/export` | bai |
| DELETE | `/api/users/me` | bai |
| POST | `/api/users/` | bai |
| GET | `/api/users/{user_id}` | bai |
| GET | `/api/users/{user_id}/public` | ez |
| PUT | `/api/users/{user_id}` | bai |
| DELETE | `/api/users/{user_id}` | bai |

## `validation_rules` → `/api`

| Metodoa | Ibilbidea | Auth |
|---|---|---|
| GET | `/api/validation-rules/` | ez |
| POST | `/api/validation-rules/` | bai |
| GET | `/api/validation-rules/{rule_id}` | ez |
| PUT | `/api/validation-rules/{rule_id}` | bai |
| DELETE | `/api/validation-rules/{rule_id}` | bai |
| GET | `/api/validation-rule-groups/` | ez |
| POST | `/api/validation-rule-groups/` | bai |

Guztira: 310 endpoint 33 routerretan.