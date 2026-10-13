# API — riferimento endpoint

Generato da `app/routers/*.py` + prefissi di `app/main.py`.
Dettaglio interattivo: `/docs` (Swagger) e `/redoc` col backend avviato.

## `admin` → `/api/admin`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/admin/stats` | sì |
| GET | `/api/admin/tables` | sì |
| GET | `/api/admin/audit-log` | sì |
| POST | `/api/admin/reset` | sì |

## `auth` → `/api/users`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/users/login` | no |

## `auth_sessions` → `/api/auth`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/auth/refresh` | no |
| GET | `/api/auth/sessions` | sì |
| DELETE | `/api/auth/sessions/{session_id}` | sì |
| POST | `/api/auth/sessions/revoke-all` | sì |

## `calendar` → `/api/calendar`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/calendar/agenda` | opzionale |
| GET | `/api/calendar/agenda/export/ics` | opzionale |
| GET | `/api/calendar/settings` | no |
| GET | `/api/calendar/admin/settings` | sì |
| PUT | `/api/calendar/admin/settings` | sì |
| POST | `/api/calendar/dav/token` | sì |
| GET | `/api/calendar/dav/token` | sì |
| DELETE | `/api/calendar/dav/token` | sì |

## `channels` → `/api/channels`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/channels` | sì |
| GET | `/api/channels` | sì |
| GET | `/api/channels/public` | sì |
| GET | `/api/channels/{channel_id}` | sì |
| PUT | `/api/channels/{channel_id}` | sì |
| DELETE | `/api/channels/{channel_id}` | sì |
| POST | `/api/channels/{channel_id}/members` | sì |
| GET | `/api/channels/{channel_id}/members` | sì |
| PUT | `/api/channels/{channel_id}/members/{user_id}/role` | sì |
| DELETE | `/api/channels/{channel_id}/members/{user_id}` | sì |

## `chat` → `/api/chat`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/chat/messages` | sì |
| POST | `/api/chat/messages` | sì |
| PUT | `/api/chat/messages/{message_id}/read` | sì |
| DELETE | `/api/chat/messages/{message_id}` | sì |
| GET | `/api/chat/groups` | sì |
| POST | `/api/chat/groups` | sì |
| GET | `/api/chat/groups/{group_id}` | sì |
| DELETE | `/api/chat/groups/{group_id}` | sì |
| GET | `/api/chat/groups/{group_id}/members` | sì |
| POST | `/api/chat/groups/{group_id}/members` | sì |
| DELETE | `/api/chat/groups/{group_id}/members/{user_id}` | sì |
| PUT | `/api/chat/groups/{group_id}/members/{user_id}/role` | sì |
| WEBSOCKET | `/api/chat/ws` | token (query) |

## `committees` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/committees/` | opzionale |
| POST | `/api/festivals/{festival_id}/committees/` | sì |
| GET | `/api/committees/{committee_id}` | opzionale |
| PUT | `/api/committees/{committee_id}` | sì |
| DELETE | `/api/committees/{committee_id}` | sì |
| GET | `/api/committees/{committee_id}/members/` | opzionale |
| POST | `/api/committees/{committee_id}/members/` | sì |
| PUT | `/api/committee-members/{member_id}` | sì |
| DELETE | `/api/committee-members/{member_id}` | sì |

## `dav` → `/dav`

| Metodo | Percorso | Auth |
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

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/delegations/` | opzionale |
| POST | `/api/delegations/` | sì |
| PUT | `/api/delegations/{delegation_id}` | sì |
| POST | `/api/delegations/{delegation_id}/revoke` | sì |
| GET | `/api/users/{user_id}/active-delegations` | opzionale |
| GET | `/api/role-transitions/` | sì |
| POST | `/api/role-transitions/` | sì |
| GET | `/api/users/{user_id}/role-transitions` | sì |
| GET | `/api/users/{user_id}/role-check` | sì |

## `events` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/events/` | no |
| GET | `/api/festivals/{festival_id}/events/export/ics` | sì |
| POST | `/api/festivals/{festival_id}/events/` | sì |
| GET | `/api/events/{event_id}` | no |
| PUT | `/api/events/{event_id}` | sì |
| DELETE | `/api/events/{event_id}` | sì |
| GET | `/api/festivals/{festival_id}/events/programacion` | no |
| GET | `/api/festivals/{festival_id}/events/check-conflict` | sì |
| GET | `/api/events/{event_id}/screenings` | no |
| PUT | `/api/events/{event_id}/screenings` | sì |
| GET | `/api/events/{event_id}/occupancy` | no |
| GET | `/api/events/{event_id}/ticket-types/` | no |
| POST | `/api/events/{event_id}/ticket-types/` | sì |
| PUT | `/api/ticket-types/{tt_id}` | sì |
| DELETE | `/api/ticket-types/{tt_id}` | sì |
| GET | `/api/events/{event_id}/seats/` | no |
| POST | `/api/events/{event_id}/seats/bulk` | sì |
| GET | `/api/events/{event_id}/seats/sections` | no |
| GET | `/api/events/{event_id}/seats/counts` | no |
| PUT | `/api/seats/{seat_id}` | sì |
| POST | `/api/seats/{seat_id}/release` | sì |
| DELETE | `/api/seats/{seat_id}` | sì |
| GET | `/api/events/{event_id}/reservations/` | sì |
| POST | `/api/events/{event_id}/reservations/` | sì |
| PUT | `/api/reservations/{reservation_id}` | sì |
| POST | `/api/reservations/{reservation_id}/confirm` | sì |
| POST | `/api/reservations/{reservation_id}/cancel` | sì |
| DELETE | `/api/reservations/{reservation_id}` | sì |
| GET | `/api/events/{event_id}/attendees/` | sì |
| POST | `/api/events/{event_id}/attendees/` | sì |
| GET | `/api/attendees/{attendee_id}` | no |
| PUT | `/api/attendees/{attendee_id}` | sì |
| POST | `/api/attendees/{attendee_id}/check-in` | sì |
| GET | `/api/events/{event_id}/attendees/counts` | no |
| GET | `/api/events/{event_id}/attendees/export/csv` | sì |
| DELETE | `/api/attendees/{attendee_id}` | sì |
| POST | `/api/events/{event_id}/assign-vip` | sì |
| GET | `/api/users/me/events/` | sì |
| GET | `/api/users/me/events/{event_id}/reservation` | sì |
| GET | `/api/festivals/{festival_id}/awards/` | no |
| POST | `/api/festivals/{festival_id}/awards/` | sì |
| PUT | `/api/awards/{award_id}` | sì |
| DELETE | `/api/awards/{award_id}` | sì |
| GET | `/api/users/{user_id}/awards/` | no |
| GET | `/api/public/profile/{token}` | no |
| GET | `/api/festivals/{festival_id}/users/{user_id}/profile` | no |

## `festival_rulebooks` → `/api/festivals/{festival_id}/rulebooks`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/rulebooks/` | no |
| GET | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | no |
| POST | `/api/festivals/{festival_id}/rulebooks/` | sì |
| POST | `/api/festivals/{festival_id}/rulebooks/upload` | sì |
| PUT | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/rulebooks/{rulebook_id}` | sì |

## `festivals` → `/api/festivals`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/` | no |
| POST | `/api/festivals/` | sì |
| GET | `/api/festivals/{festival_id}` | no |
| PUT | `/api/festivals/{festival_id}` | sì |
| DELETE | `/api/festivals/{festival_id}` | sì |
| POST | `/api/festivals/{festival_id}/images` | sì |
| DELETE | `/api/festivals/{festival_id}/images` | sì |
| GET | `/api/festivals/{festival_id}/locations` | no |
| POST | `/api/festivals/{festival_id}/locations` | sì |
| DELETE | `/api/festivals/{festival_id}/locations/{location_id}` | sì |

## `form_definitions` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/forms/` | sì |
| POST | `/api/forms/` | sì |
| GET | `/api/forms/{form_id}` | sì |
| PUT | `/api/forms/{form_id}` | sì |
| DELETE | `/api/forms/{form_id}` | sì |
| POST | `/api/forms/{form_id}/clone` | sì |
| POST | `/api/forms/{form_id}/pages/` | sì |
| PUT | `/api/forms/{form_id}/pages/{page_id}` | sì |
| DELETE | `/api/forms/{form_id}/pages/{page_id}` | sì |
| POST | `/api/forms/{form_id}/pages/{page_id}/fields/` | sì |
| PUT | `/api/forms/{form_id}/fields/{field_id}` | sì |
| DELETE | `/api/forms/{form_id}/fields/{field_id}` | sì |
| GET | `/api/forms/{form_id}/links/` | sì |
| POST | `/api/forms/{form_id}/links/` | sì |
| DELETE | `/api/forms/{form_id}/links/{link_id}` | sì |
| GET | `/api/forms/public/{token}` | no |
| POST | `/api/forms/public/{token}/submit` | opzionale |
| GET | `/api/forms/{form_id}/responses/` | sì |
| GET | `/api/forms/{form_id}/responses/export/csv` | sì |
| PUT | `/api/forms/responses/{response_id}` | sì |
| POST | `/api/forms/responses/{response_id}/approve` | sì |
| POST | `/api/forms/responses/{response_id}/reject` | sì |

## `keys` → `/api/users`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/users/me/public-key` | sì |
| GET | `/api/users/{user_id}/public-key` | sì |

## `location_images` → `/api/locations/{location_id}/images`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/images/` | no |
| POST | `/api/locations/{location_id}/images/upload` | sì |
| POST | `/api/locations/{location_id}/images/url` | sì |
| DELETE | `/api/locations/{location_id}/images/{image_id}` | sì |

## `location_relations` → `/api/locations/{location_id}/relations`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/relations/` | no |
| POST | `/api/locations/{location_id}/relations/` | sì |
| DELETE | `/api/locations/{location_id}/relations/{relation_id}` | sì |
| POST | `/api/locations/{location_id}/relations/suggest` | sì |

## `location_tags` → `/api/locations/{location_id}/tags`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations/{location_id}/tags/` | no |
| POST | `/api/locations/{location_id}/tags/` | sì |
| DELETE | `/api/locations/{location_id}/tags/{tag_id}` | sì |

## `locations` → `/api/locations`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/locations/` | no |
| POST | `/api/locations/` | sì |
| GET | `/api/locations/{location_id}` | no |
| PUT | `/api/locations/{location_id}` | sì |
| PUT | `/api/locations/{location_id}/badge` | sì |
| DELETE | `/api/locations/{location_id}` | sì |

## `notifications` → `/api/notifications`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/notifications/` | sì |
| GET | `/api/notifications/unread-count` | sì |
| PUT | `/api/notifications/{notification_id}/read` | sì |
| PUT | `/api/notifications/read-all` | sì |
| DELETE | `/api/notifications/{notification_id}` | sì |

## `participant_tags` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/participant-tags/` | no |
| POST | `/api/participant-tags/` | sì |
| GET | `/api/participant-tags/{tag_id}` | no |
| PUT | `/api/participant-tags/{tag_id}` | sì |
| DELETE | `/api/participant-tags/{tag_id}` | sì |
| GET | `/api/festivals/{festival_id}/participant-tags/` | no |
| POST | `/api/festivals/{festival_id}/participant-tags/` | sì |
| PUT | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/participant-tags/{fpt_id}` | sì |

## `payments` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/payments/checkout` | sì |
| GET | `/api/payments/` | sì |
| GET | `/api/payments/{payment_id}` | sì |
| POST | `/api/payments/{payment_id}/confirm` | sì |
| POST | `/api/payments/{payment_id}/refund` | sì |
| POST | `/api/payments/webhook/mock` | no |

## `registration_forms` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/festivals/{festival_id}/registration-forms/` | sì |
| POST | `/api/festivals/{festival_id}/registration-forms/` | sì |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sì |
| GET | `/api/registration-forms/{form_id}` | sì |
| PUT | `/api/registration-forms/{form_id}` | sì |
| DELETE | `/api/registration-forms/{form_id}` | sì |
| GET | `/api/registration-forms/{form_id}/registrations/` | sì |
| PUT | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}` | sì |
| GET | `/api/public/forms/{token}` | no |
| POST | `/api/public/forms/{token}/register` | opzionale |
| GET | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | sì |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/` | sì |
| DELETE | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}` | sì |
| POST | `/api/festivals/{festival_id}/registration-forms/{form_id}/links/{link_id}/regenerate` | sì |
| GET | `/api/registration-forms/{form_id}/links/` | sì |
| POST | `/api/registration-forms/{form_id}/links/` | sì |
| DELETE | `/api/registration-form-links/{link_id}` | sì |
| POST | `/api/registration-form-links/{link_id}/regenerate` | sì |
| GET | `/api/festivals/{festival_id}/registrations/` | sì |
| GET | `/api/festivals/{festival_id}/registrations/export/csv` | sì |
| GET | `/api/festivals/{festival_id}/registrations/export/pdf` | sì |
| GET | `/api/users/{user_id}/registrations/` | sì |
| PUT | `/api/registrations/{registration_id}` | sì |
| POST | `/api/registrations/{registration_id}/approve` | sì |
| POST | `/api/registrations/{registration_id}/reject` | sì |
| POST | `/api/registrations/{registration_id}/payment/mark-paid` | sì |
| POST | `/api/registrations/{registration_id}/payment/mark-refunded` | sì |
| DELETE | `/api/registrations/{registration_id}` | sì |
| POST | `/api/registration-forms/{form_id}/sections/` | sì |
| PUT | `/api/registration-forms/{form_id}/sections/{section_id}` | sì |
| DELETE | `/api/registration-forms/{form_id}/sections/{section_id}` | sì |

## `role_groups` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/role-groups/` | no |
| POST | `/api/role-groups/` | sì |
| GET | `/api/role-groups/{group_id}` | no |
| PUT | `/api/role-groups/{group_id}` | sì |
| DELETE | `/api/role-groups/{group_id}` | sì |
| GET | `/api/role-groups/{group_id}/memberships/` | no |
| POST | `/api/role-groups/{group_id}/memberships/` | sì |
| PUT | `/api/role-group-memberships/{membership_id}` | sì |
| DELETE | `/api/role-group-memberships/{membership_id}` | sì |

## `roles` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/roles/` | sì |
| POST | `/api/roles/` | sì |
| GET | `/api/roles/hierarchy/` | opzionale |
| GET | `/api/roles/{role_id}` | opzionale |
| PUT | `/api/roles/{role_id}` | sì |
| DELETE | `/api/roles/{role_id}` | sì |
| GET | `/api/festivals/{festival_id}/roles/` | opzionale |
| POST | `/api/festivals/{festival_id}/roles/` | sì |
| POST | `/api/festivals/{festival_id}/roles/initialize` | sì |
| PUT | `/api/festivals/{festival_id}/roles/{fr_id}` | sì |
| DELETE | `/api/festivals/{festival_id}/roles/{fr_id}` | sì |
| GET | `/api/roles/{role_id}/dependencies` | opzionale |
| POST | `/api/role-dependencies/` | sì |
| DELETE | `/api/role-dependencies/{dependency_id}` | sì |
| GET | `/api/roles/{role_id}/conflicts` | opzionale |
| POST | `/api/role-conflicts/` | sì |
| DELETE | `/api/role-conflicts/{conflict_id}` | sì |
| GET | `/api/roles/{role_id}/check-conflicts` | opzionale |

## `search` → `/api/search`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/search/` | sì |

## `shortfilm_locations` → `/api/shortfilms/{shortfilm_id}/locations`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/shortfilms/{shortfilm_id}/locations/` | no |
| POST | `/api/shortfilms/{shortfilm_id}/locations/` | sì |
| PUT | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | sì |
| DELETE | `/api/shortfilms/{shortfilm_id}/locations/{sfloc_id}` | sì |

## `shortfilms` → `/api/shortfilms`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/shortfilms/` | no |
| POST | `/api/shortfilms/` | sì |
| GET | `/api/shortfilms/{shortfilm_id}` | no |
| PUT | `/api/shortfilms/{shortfilm_id}` | sì |
| DELETE | `/api/shortfilms/{shortfilm_id}` | sì |

## `uploads` → `/api/uploads`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/uploads/avatar` | sì |
| POST | `/api/uploads/thumbnail` | sì |
| POST | `/api/uploads/video` | sì |
| POST | `/api/uploads/chat-image` | sì |

## `user_aliases` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/aliases/` | no |
| POST | `/api/users/{user_id}/aliases/` | sì |
| PUT | `/api/users/{user_id}/aliases/{alias_id}` | sì |
| DELETE | `/api/users/{user_id}/aliases/{alias_id}` | sì |

## `user_festival` → `/api/festivals`

| Metodo | Percorso | Auth |
|---|---|---|
| POST | `/api/festivals/{festival_id}/join` | sì |
| DELETE | `/api/festivals/{festival_id}/leave` | sì |
| GET | `/api/festivals/{festival_id}/members` | sì |
| GET | `/api/festivals/user/{user_id}/festivals` | sì |

## `user_roles` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/users/{user_id}/roles/` | sì |
| POST | `/api/users/{user_id}/roles/` | sì |
| PUT | `/api/users/{user_id}/roles/{ur_id}` | sì |
| DELETE | `/api/users/{user_id}/roles/{ur_id}` | sì |
| GET | `/api/users/{user_id}/participant-tags/` | sì |
| POST | `/api/users/{user_id}/participant-tags/` | sì |
| DELETE | `/api/users/{user_id}/participant-tags/{upt_id}` | sì |

## `users` → `/api/users`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/users/` | sì |
| GET | `/api/users/public` | no |
| GET | `/api/users/me` | sì |
| GET | `/api/users/me/export` | sì |
| DELETE | `/api/users/me` | sì |
| POST | `/api/users/` | sì |
| GET | `/api/users/{user_id}` | sì |
| GET | `/api/users/{user_id}/public` | no |
| PUT | `/api/users/{user_id}` | sì |
| DELETE | `/api/users/{user_id}` | sì |

## `validation_rules` → `/api`

| Metodo | Percorso | Auth |
|---|---|---|
| GET | `/api/validation-rules/` | no |
| POST | `/api/validation-rules/` | sì |
| GET | `/api/validation-rules/{rule_id}` | no |
| PUT | `/api/validation-rules/{rule_id}` | sì |
| DELETE | `/api/validation-rules/{rule_id}` | sì |
| GET | `/api/validation-rule-groups/` | no |
| POST | `/api/validation-rule-groups/` | sì |

Totale: 310 endpoint in 33 router.