# Datu-base-ko dokumentazioa

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [CA](DATABASE.md) · [EU](DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Deskripzioa

Clakettes arraya erabiltzen du datu-baseen:

- **Garapena**: SQLite (`clakettes.db`) — default, konfigurazioarik gabe
- **Produktua**: MariaDB — `DATABASE_URL` bidez `backend/.env`-ean

Mutil-ak eskainita:

- `python export_sqlite_to_mariadb.py` — Garapena → Produktua
- `python import_mariadb_to_sqlite.py` — Produktua → Garapena

## Model-ren zerrenda

| Modelo | Taula | Tipus |
|--------|-------|-------|
| `AppSetting` | `app_settings` | Eskura |
| `AuditLog` | `audit_logs` | Eskura |
| `Award` | `awards` | Eskura |
| `Badge` | `badges` | Eskura |
| `Calendar` | `calendars` | Eskura |
| `Channel` | `channels` | Eskura |
| `Committee` | `committees` | Eskura |
| `Event` | `events` | Eskura |
| `EventScreening` | `event_screenings` | Eskura |
| `Festival` | `festivals` | Eskura |
| `FestivalLocation` | `festival_locations` | Eskura |
| `FestivalRulebook` | `festival_rulebooks` | Eskura |
| `FormDefinition` | `form_definitions` | Eskura |
| `Group` | `groups` | Eskura |
| `JuryVote` | `jury_votes` | Eskura |
| `Location` | `locations` | Eskura |
| `LocationImage` | `location_images` | Eskura |
| `LocationRelation` | `location_relations` | Eskura |
| `LocationTag` | `location_tags` | Eskura |
| `Message` | `messages` | Eskura |
| `ModerationReport` | `moderation_reports` | Eskura |
| `NodePolicy` | `node_policies` | Eskura |
| `Notification` | `notifications` | Eskura |
| `ParticipantTag` | `participant_tags` | Eskura |
| `Payment` | `payments` | Eskura |
| `Post` | `posts` | Eskura |
| `Registration` | `registration_forms` | Eskura |
| `Role` | `roles` | Eskura |
| `RoleDelegation` | `role_delegations` | Eskura |
| `RoleGroup` | `role_groups` | Eskura |
| `RoleTransition` | `role_transitions` | Eskura |
| `ShortFilm` | `shortfilms` | Eskura |
| `ShortFilmLocation` | `shortfilm_locations` | Eskura |
| `User` | `users` | Eskura |
| `UserAlias` | `user_aliases` | Eskura |
| `UserBlock` | `user_blocks` | Eskura |
| `UserFestival` | `user_festival` | Erlazioa (taula) |
| `UserKey` | `user_keys` | Eskura |
| `UserRole` | `user_roles` | Eskura |
| `UserSession` | `user_sessions` | Eskura |
| `ValidationRule` | `validation_rules` | Eskura |
| `ValidationRuleGroup` | `validation_rule_groups` | Eskura |

Erlazioa taulak:

- `user_festival` — M2M `User`-en eta `Festival`-en artean
- `validation_rule_group_rules` — M2M `ValidationRuleGroup`-en eta `ValidationRule`-en artean

Guztira: 40 eskura-modeloa + 2 erlazioa-taula = 42 SQLAlchemy-eko eraikina.

## Base Model

Modeloak guztiak `BaseModel`-etik heretan, `app/models/base.py`-ko:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Emetsiak:

- `id`: primary key, automatikoa Izenbakia
- `created_at`: ordu-marka sortzean
- `updated_at`: ordu-marka aldaketan

## Eskura-gabeenak

### Festival

- **Taula:** `festivals`
- **Klasse:** `Festival`
- **Esku-menuak:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Erlazioa:** ShortFilak gehiago, User-ak (M2M `user_festival` bidez), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User

- **Taula:** `users`
- **Klasse:** `User`
- **Esku-menuak:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Erlazioa:** ShortFilm gehiago, Festival gehiago (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (ezkutatak), EventAttendees, EventReservations

### ShortFilm

- **Taula:** `shortfilms`
- **Klasse:** `ShortFilm`
- **Esku-menuak:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Erlazioa:** Festival-koa, User-koa, Awards gehiago, ShortFilmLocations gehiago

### Message

- **Taula:** `messages`
- **Klasse:** `Message`
- **Esku-menuak:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Erlazioa:** User-ko emisarioa, User-ko eplementaria, Channel-koa

### User-Festival Erlazioa

- **Taula:** `user_festival`
- **Klasse:** None (SQLAlchemy taula)
- **Esku-menuak:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Erlazioa:** User eta Festival arteko M2M; PK batera (user_id, festival_id)

### Award

- **Taula:** `awards`
- **Klasse:** `Award`
- **Esku-menuak:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Erlazioa:** Festival-koa, Event-koa, ShortFilm-koa, User-ko jariaria, User-ko argazkilaria, User-ko sortzailea

### Badge

- **Taula:** `badges`
- **Klasse:** `Badge`
- **Esku-menuak:** name, description, image_url (svg-preferita), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Erlazioa:** Festival-koa, BadgeAssignments gehiago
- **Notak:** Garapenean dagoela, default-en ez daaktibatuta (`badges.enabled`); admin-taldea aktibatzea

### Channel

- **Taula:** `channels`
- **Klasse:** `Channel`
- **Esku-menuak:** name, description, channel_type, max_members, created_by (FK), is_active
- **Erlazioa:** User-ko sortzailea, ChannelMember gehiago, Message gehiago

### Committee

- **Taula:** `committees`
- **Klasse:** `Committee`
- **Esku-menuak:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Erlazioa:** Festival-koa, Role-koa, CommitteeMember gehiago

### Event

- **Taula:** `events`
- **Klasse:** `Event`
- **Esku-menuak:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Erlazioa:** Festival-koa, User-ko sortzailea, EventTicketType gehiago, EventSeat gehiago, EventReservation gehiago, EventAttendee gehiago, Awards, EventScreeningak

### Notification

- **Taula:** `notifications`
- **Klasse:** `Notification`
- **Esku-menuak:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Erlazioa:** User-ko eplementaria, User-ko erlatua

### ParticipantTag

- **Taula:** `participant_tags`
- **Klasse:** `ParticipantTag`
- **Esku-menuak:** name, display_name, description, category, is_global, is_active, sort_order
- **Erlazioa:** UserParticipantTag gehiago, FestivalParticipantTag gehiago

### Post

- **Taula:** `posts`
- **Klasse:** `Post`
- **Esku-menuak:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Erlazioa:** User-ko sortzailea, User-ko murua, Festival-ko murua, erantzun gehiago (Post), Post-ko aita
- **Notak:** Garapenean dagoela

### Registration

- **Taula:** `registration_forms`
- **Klasse:** `RegistrationForm`
- **Esku-menuak:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Erlazioa:** Festival-koa, RegistrationFormSection gehiago, RegistrationFormLink gehiago, FestivalRegistration gehiago

### Role

- **Taula:** `roles`
- **Klasse:** `Role`
- **Esku-menuak:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Erlazioa:** Role-ko aita, RoleGroup-a, UserRole gehiago, FestivalRole gehiago, RoleGroupMembershipak, RoleDependencyak, RoleConflictak

### UserAlias

- **Taula:** `user_aliases`
- **Klasse:** `UserAlias`
- **Esku-menuak:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Erlazioa:** User-koa
- **Notak:** Agertzen diren izena kontestuaren arabera (global, festival, shortfilm, chat, public_profile, credits) eta eskutikak bidez

### UserKey

- **Taula:** `user_keys`
- **Klasse:** `UserKey`
- **Esku-menuak:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Erlazioa:** User-koa
- **Notak:** X25519 publikoa gorde, E2EE-ko, bat erabiltzailea

### UserSession

- **Taula:** `user_sessions`
- **Klasse:** `UserSession`
- **Esku-menuak:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Erlazioa:** User-koa

### ValidationRule

- **Taula:** `validation_rules`
- **Klasse:** `ValidationRule`
- **Esku-menuak:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Erlazioa:** ValidationRuleGroup-arekin `validation_rule_group_rules`- bidez

### Payment

- **Taula:** `payments`
- **Klasse:** `Payment`
- **Esku-menuak:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Erlazioa:** Registration-koa

### JuryVote

- **Taula:** `jury_votes`
- **Klasse:** `JuryVote`
- **Esku-menuak:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Erlazioa:** Festival-koa, ShortFilm-koa, User-ko juri

### NodePolicy

- **Taula:** `node_policies`
- **Klasse:** `NodePolicy`
- **Esku-menuak:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Erlazioa:** Federazio-eskura

### ModerationReport

- **Taula:** `moderation_reports`
- **Klasse:** `ModerationReport`
- **Esku-menuak:** reporter_node, target_node, target_user_ref, reason, status
- **Erlazioa:** Federazio-eskura

### Location

- **Taula:** `locations`
- **Klasse:** `Location`
- **Esku-menuak:** name, description, latitude, longitude, address, is_active
- **Erlazioa:** Festival-koa (M2M), LocationImage gehiago, LocationTag gehiago, LocationRelation gehiago

### EventScreening

- **Taula:** `event_screenings`
- **Klasse:** `EventScreening`
- **Esku-menuak:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Erlazioa:** Event-koa, ShortFilm-koa

### FestivalRulebook

- **Taula:** `festival_rulebooks`
- **Klasse:** `FestivalRulebook`
- **Esku-menuak:** festival_id (FK), title, content, file_url, is_active
- **Erlazioa:** Festival-koa

### FormDefinition

- **Taula:** `form_definitions`
- **Klasse:** `FormDefinition`
- **Esku-menuak:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Erlazioa:** Festival-koa, FormPage gehiago, FormLink gehiago, FormResponse gehiago

### Group

- **Taula:** `groups`
- **Klasse:** `Group`
- **Esku-menuak:** name, display_name, description, sort_order, is_active
- **Erlazioa:** RoleGroupMembership gehiago, Role gehiago

### AppSetting

- **Taula:** `app_settings`
- **Klasse:** `AppSetting`
- **Esku-menuak:** key, value, description, is_public
- **Erlazioa:** konfigurazio-eskura

### AuditLog

- **Taula:** `audit_logs`
- **Klasse:** `AuditLog`
- **Esku-menuak:** actor_id (FK), action, target, ip, created_at
- **Erlazioa:** User-ko aktore, append-only

### UserBlock

- **Taula:** `user_blocks`
- **Klasse:** `UserBlock`
- **Esku-menuak:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Erlazioa:** User-ko blokeatzailea, User-ko blokeatua

### RoleDelegation

- **Taula:** `role_delegations`
- **Klasse:** `RoleDelegation`
- **Esku-menuak:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Erlazioa:** User-ko delgatzailea, User-ko delgatua, Role-a, Festival-a, User-ko errebatzailea

### RoleTransition

- **Taula:** `role_transitions`
- **Klasse:** `RoleTransition`
- **Esku-menuak:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Erlazioa:** User-a, Role-a (aurka), Role-a (hurrengoa), Festival-a (aurka), Festival-a (hurrengoa), User-ko aldaketa

### EventTicketType

- **Taula:** `event_ticket_types`
- **Klasse:** `EventTicketType`
- **Esku-menuak:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Erlazioa:** Event-koa

### EventSeat

- **Taula:** `event_seats`
- **Klasse:** `EventSeat`
- **Esku-menuak:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Erlazioa:** Event-koa, EventTicketType-koa

### EventReservation

- **Taula:** `event_reservations`
- **Klasse:** `EventReservation`
- **Esku-menuak:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Erlazioa:** Event-koa, User-ko sortzailea, User-ko sortzailea

### EventAttendee

- **Taula:** `event_attendees`
- **Klasse:** `EventAttendee`
- **Esku-menuak:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Erlazioa:** Event-koa, EventReservation-koa, User-a, EventSeat-a, EventTicketType-a, User-ko deitzailea

## Datutxarra sessioak

Datu-texioak `get_db()` bidez kargatzen da `app/database.py`-ko:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI-ek eskaintzen du endpoints-ko eskura-ko eskaintzaz.

## SQLite → MariaDB-ko mugatu

Eskaerak alembic-eko `backend/alembic/versions/` (36 bertsioa; `alembic upgrade head`). Produktuan alembic-ak, `create_all` bat ez.

SQLite ↔ MariaDB:

- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (testua bezala) → MariaDB `DATETIME` nativo
- `export_sqlite_to_mariadb.py` eta `import_mariadb_to_sqlite.py` eskriptuak tipiru-tzake-app egiten dute