# API — endpoint reference

Generated from `app/routers/*.py` + prefixes in `app/main.py`.
Interactive detail: `/docs` (Swagger) and `/redoc` with the backend running.

## `admin` → `/api/admin`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/admin/stats` | yes |
| GET | `/api/admin/tables` | yes |
| GET | `/api/admin/audit-log` | yes |
| POST | `/api/admin/reset` | yes |

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

## `calendar` → `/api/calendar`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | optional |
| GET | `/api/calendar/agenda/export/ics` | optional |
| GET | `/api/calendar/settings` | no |
| GET | `/api/calendar/admin/settings` | yes |
| PUT | `/api/calendar/admin/settings` | yes |
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
| WEBSOCKET | `/api/chat/ws` | token (query) |

## `committees` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees/` | optional |
| POST | `/api/festivals/{festival_id}/committees/` | yes |
| GET | `/api/committees/{committee_id}` | optional |
| PUT | `/api/committees/{committee_id}` | yes |
| DELETE | `/api/committees/{committee_id}` | yes |
| GET | `/api/committees/{committee_id}/members/` | optional |
| POST | `/api/committees/{committee_id}/members/` | yes |
| PUT | `/api/committee-members/{member_id}` | yes |
| DELETE | `/api/committee-members/{member_id}` | yes |

## `dav` → `/dav`

| Method | Path | Auth |
|---|---|---|
| OPTIONS | `/dav/` | no |
| OPTIONS | `/dav/{dav_path:path}` | no |
| PROPFIND | `/dav/` | no |
| GET | `/dav/{principal}/calendars/{collection}.ics` | no |
| HEAD | `/dav/{principal}/calendars/{collection}.ics` | no |
| GET | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| HEAD | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | no |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}` | no |
| API_ROUTE | `/dav/{principal}/calendars/{collection}/{resource}/` | no |
| PROPFIND | `/dav/{principal}/calendars/{collection}/` | no |
| PROPFIND | `/dav/{principal}/calendars/{collection}` | no |
| REPORT | `/dav/{principal}/calendars/{collection}/` | no |
| REPORT | `/dav/{principal}/calendars/{collection}` | no |
| PROPFIND | `/dav/{principal}/calendars/` | no |
| PROPFIND | `/dav/{principal}/calendars` | no |
| PROPFIND | `/dav/{principal}/` | no |
| PROPFIND | `/dav/{principal}` | no |
| REPORT | `/dav/{principal}/calendars/` | no |
| REPORT | `/dav/{principal}/calendars` | no |
| REPORT | `/dav/{principal}/` | no |
| REPORT | `/dav/{principal}` | no |
| API_ROUTE | `/dav/{write_path:path}` | no |

## `delegations` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/delegations/` | optional |
| POST | `/api/delegations/` | yes |
| PUT | `/api/delegations/{delegation_id}` | yes |
| POST | `/api/delegations/{delegation_id}/revoke` | yes |
| GET | `/api/users/{user_id}/active-delegations` | optional |
| GET | `/api/role-transitions/` | yes |
| POST | `/api/role-transitions/` | yes |
| GET | `/api/users/{user_id}/role-transitions` | yes |
| GET | `/api/users/{user_id}/role-check` | yes |

## `events` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events/` | no |
| GET | `/api/festivals/{festival_id}/events/export/ics` | yes |
| POST | `/api/festivals/{festival_id}/events/` | yes |
| GET | `/api/events/{event_id}` | no |
| PUT | `/api/events/{event_id}` | yes |
| DELETE | `/api/events/{event_id}` | yes |
| GET | `/api/festivals/{festival_id}/events/programacion` | no |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | yes |
| GET | `/api/events/{event_id}/screenings` | no |
| PUT | `/api/events/{event_id}/screenings` | yes |
| GET | `/api/events/{event_id}/occupancy` | no |
| GET | `/api/events/{event_id}/ticket-types/` | no |
| POST | `/api/events/{event_id}/ticket-types/` | yes |
| PUT | `/api/ticket-types/{tt_id}` | yes |
| DELETE | `/api/ticket-types/{tt_id}` | yes |
| GET | `/api/events/{event_id}/seats/` | no |
| POST | `/api/events/{event_id}/seats/bulk` | yes |
| GET | `/api/events/{event_id}/seats/sections` | no |
| GET | `/api/events/{event_id}/seats/counts` | no |
| PUT | `/api/seats/{seat_id}` | yes |
| POST | `/api/seats/{seat_id}/release` | yes |
| DELETE | `/api/seats/{seat_id}` | yes |
| GET | `/api/events/{event_id}/reservations/` | yes |
| POST | `/api/events/{event_id}/reservations/` | yes |
| PUT | `/api/reservations/{reservation_id}` | yes |
| POST | `/api/reservations/{reservation_id}/confirm` | yes |
| POST | `/api/reservations/{reservation_id}/cancel` | yes |
| DELETE | `/api/reservations/{reservation_id}` | yes |
| GET | `/api/events/{event_id}/attendees/` | yes |
| POST | `/api/events/{event_id}/attendees/` | yes |
| GET | `/api/attendees/{attendee_id}` | no |
| PUT | `/api/attendees/{attendee_id}` | yes |
| POST | `/api/attendees/{attendee_id}/check-in` | yes |
| GET | `/api/events/{event_id}/attendees/counts` | no |
| GET | `/api/events/{event_id}/attendees/export/csv` | yes |
| DELETE | `/api/attendees/{attendee_id}` | yes |
| POST | `/api/events/{event_id}/assign-vip` | yes |
| GET | `/api/users/me/events/` | yes |
| GET | `/api/users/me/events/{event_id}/reservation` | yes |
| GET | `/api/festivals/{festival_id}/awards/` | no |
| POST | `/api/festivals/{festival_id}/awards/` | yes |
| PUT | `/api/awards/{award_id}` | yes |
| DELETE | `/api/awards/{award_id}` | yes |
| GET | `/api/users/{user_id}/awards/` | no |
| GET | `/api/public/profile/{token}` | no |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | no |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks/` | no |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | no |
| POST | `/api/festivals/{festival_id}/rulebooks/` | yes |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | yes |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | yes |

## `festivals` → `/api/festivals`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/` | no |
| POST | `/api/festivals/` | yes |
| GET | `/api/festivals/{festival_id}` | no |
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
| GET | `/api/forms/` | yes |
| POST | `/api/forms/` | yes |
| GET | `/api/forms/{form_id}` | yes |
| PUT | `/api/forms/{form_id}` | yes |
| DELETE | `/api/forms/{form_id}` | yes |
| POST | `/api/forms/{form_id}/clone` | yes |
| POST | `/api/forms/{form_id}/pages/` | yes |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | yes |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | yes |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields/` | yes |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | yes |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | yes |
| GET | `/api/forms/{form_id}/links/` | yes |
| POST | `/api/forms/{form_id}/links/` | yes |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | yes |
| GET | `/api/forms/public/{token}` | no |
| POST | `/api/forms/public/{token}/submit` | optional |
| GET | `/api/forms/{form_id}/responses/` | yes |
| GET | `/api/forms/{form_id}/responses/export/csv` | yes |
| PUT | `/api/forms/responses/{response_id}` | yes |
| POST | `/api/forms/responses/{response_id}/approve` | yes |
| POST | `/api/forms/responses/{response_id}/reject` | yes |

## `keys` → `/api/users`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | yes |
| GET | `/api/users/{user_id}/public-key` | yes |

## `location_images` → `/api/locations/{location_id}/images`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images/` | no |
| POST | `/api/locations/{location_id}/images/upload` | yes |
| POST | `/api/locations/{location_id}/images/url` | yes |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | yes |

## `location_relations` → `/api/locations/{location_id}/relations`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations/` | no |
| POST | `/api/locations/{location_id}/relations/` | yes |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | yes |
| POST | `/api/locations/{location_id}/relations/suggest` | yes |

## `location_tags` → `/api/locations/{location_id}/tags`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags/` | no |
| POST | `/api/locations/{location_id}/tags/` | yes |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | yes |

## `locations` → `/api/locations`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/locations/` | no |
| POST | `/api/locations/` | yes |
| GET | `/api/locations/{location_id}` | no |
| PUT | `/api/locations/{location_id}` | yes |
| PUT | `/api/locations/{location_id}/badge` | yes |
| DELETE | `/api/locations/{location_id}` | yes |

## `notifications` → `/api/notifications`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/notifications/` | yes |
| GET | `/api/notifications/unread-count` | yes |
| PUT | `/api/notifications/{notification_id}/read` | yes |
| PUT | `/api/notifications/read-all` | yes |
| DELETE | `/api/notifications/{notification_id}` | yes |

## `participant_tags` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/participant-tags/` | no |
| POST | `/api/participant-tags/` | yes |
| GET | `/api/participant-tags/{tag_id}` | no |
| PUT | `/api/participant-tags/{tag_id}` | yes |
| DELETE | `/api/participant-tags/{tag_id}` | yes |
| GET | `/api/festivals/{festival_id}/participant-tags/` | no |
| POST | `/api/festivals/{festival_id}/participant-tags/` | yes |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | yes |

## `payments` → `/api`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | yes |
| GET | `/api/payments/` | yes |
| GET | `/api/payments/{payment_id}` | yes |
| POST | `/api/payments/{payment_id}/confirm` | yes |
| POST | `/api/payments/{payment_id}/refund` | yes |
| POST | `/api/payments/webhook/mock` | no |

## `registration_forms` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms/` | yes |
| POST | `/api/festivals/{festival_id}/registration-forms/` | yes |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | yes |
| GET | `/api/registration-forms/{form_id}` | yes |
| PUT | `/api/registration-forms/{form_id}` | yes |
| DELETE | `/api/registration-forms/{form_id}` | yes |
| GET | `/api/registration-forms/{form_id}/registrations/` | yes |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | yes |
| GET | `/api/public/forms/{token}` | no |
| POST | `/api/public/forms/{token}/register` | optional |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | yes |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | yes |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | yes |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | yes |
| GET | `/api/registration-forms/{form_id}/links/` | yes |
| POST | `/api/registration-forms/{form_id}/links/` | yes |
| DELETE | `/api/registration-form-links/{link_id}` | yes |
| POST | `/api/registration-form-links/{link_id}/regenerate` | yes |
| GET | `/api/festivals/{festival_id}/registrations/` | yes |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | yes |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | yes |
| GET | `/api/users/{user_id}/registrations/` | yes |
| PUT | `/api/registrations/{registration_id}` | yes |
| POST | `/api/registrations/{registration_id}/approve` | yes |
| POST | `/api/registrations/{registration_id}/reject` | yes |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | yes |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | yes |
| DELETE | `/api/registrations/{registration_id}` | yes |
| POST | `/api/registration-forms/{form_id}/sections/` | yes |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | yes |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | yes |

## `role_groups` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/role-groups/` | no |
| POST | `/api/role-groups/` | yes |
| GET | `/api/role-groups/{group_id}` | no |
| PUT | `/api/role-groups/{group_id}` | yes |
| DELETE | `/api/role-groups/{group_id}` | yes |
| GET | `/api/role-groups/{group_id}/memberships/` | no |
| POST | `/api/role-groups/{group_id}/memberships/` | yes |
| PUT | `/api/role-group-memberships/{membership_id}` | yes |
| DELETE | `/api/role-group-memberships/{membership_id}` | yes |

## `roles` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/roles/` | yes |
| POST | `/api/roles/` | yes |
| GET | `/api/roles/hierarchy/` | optional |
| GET | `/api/roles/{role_id}` | optional |
| PUT | `/api/roles/{role_id}` | yes |
| DELETE | `/api/roles/{role_id}` | yes |
| GET | `/api/festivals/{festival_id}/roles/` | optional |
| POST | `/api/festivals/{festival_id}/roles/` | yes |
| POST | `/api/festivals/{festival_id}/roles/initialize` | yes |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | yes |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | yes |
| GET | `/api/roles/{role_id}/dependencies` | optional |
| POST | `/api/role-dependencies/` | yes |
| DELETE | `/api/role-dependencies/{dependency_id}` | yes |
| GET | `/api/roles/{role_id}/conflicts` | optional |
| POST | `/api/role-conflicts/` | yes |
| DELETE | `/api/role-conflicts/{conflict_id}` | yes |
| GET | `/api/roles/{role_id}/check-conflicts` | optional |

## `search` → `/api/search`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/search/` | yes |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations/` | no |
| POST | `/api/shortfilms/{shortfilm_id}/locations/` | yes |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | yes |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | yes |

## `shortfilms` → `/api/shortfilms`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/shortfilms/` | no |
| POST | `/api/shortfilms/` | yes |
| GET | `/api/shortfilms/{shortfilm_id}` | no |
| PUT | `/api/shortfilms/{shortfilm_id}` | yes |
| DELETE | `/api/shortfilms/{shortfilm_id}` | yes |

## `uploads` → `/api/uploads`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | yes |
| POST | `/api/uploads/thumbnail` | yes |
| POST | `/api/uploads/video` | yes |
| POST | `/api/uploads/chat-image` | yes |

## `user_aliases` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases/` | no |
| POST | `/api/users/{user_id}/aliases/` | yes |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | yes |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | yes |

## `user_festival` → `/api/festivals`

| Method | Path | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | yes |
| DELETE | `/api/festivals/{festival_id}/leave` | yes |
| GET | `/api/festivals/{festival_id}/members` | yes |
| GET | `/api/festivals/user/{user_id}/festivals` | yes |

## `user_roles` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles/` | yes |
| POST | `/api/users/{user_id}/roles/` | yes |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | yes |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | yes |
| GET | `/api/users/{user_id}/participant-tags/` | yes |
| POST | `/api/users/{user_id}/participant-tags/` | yes |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | yes |

## `users` → `/api/users`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/users/` | yes |
| GET | `/api/users/public` | no |
| GET | `/api/users/me` | yes |
| GET | `/api/users/me/export` | yes |
| DELETE | `/api/users/me` | yes |
| POST | `/api/users/` | yes |
| GET | `/api/users/{user_id}` | yes |
| GET | `/api/users/{user_id}/public` | no |
| PUT | `/api/users/{user_id}` | yes |
| DELETE | `/api/users/{user_id}` | yes |

## `validation_rules` → `/api`

| Method | Path | Auth |
|---|---|---|
| GET | `/api/validation-rules/` | no |
| POST | `/api/validation-rules/` | yes |
| GET | `/api/validation-rules/{rule_id}` | no |
| PUT | `/api/validation-rules/{rule_id}` | yes |
| DELETE | `/api/validation-rules/{rule_id}` | yes |
| GET | `/api/validation-rule-groups/` | no |
| POST | `/api/validation-rule-groups/` | yes |

Total: 310 endpoints in 33 routers.