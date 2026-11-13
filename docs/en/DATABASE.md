# Database documentation

[ES](../es/DATABASE.md) · [EN](DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Overview

Clakettes uses a dual database configuration:
- **Development**: SQLite (`clakettes.db`) — default, no configuration required
- **Production**: MariaDB — configured via `DATABASE_URL` in `backend/.env`

Migration tools are available to sync between environments:
- `python export_sqlite_to_mariadb.py` — Development to production
- `python import_mariadb_to_sqlite.py` — Production to development

## Model summary

| Model | Table | Type |
|---|---|---|
| `AppSetting` | `app_settings` | Entity |
| `AuditLog` | `audit_logs` | Entity |
| `Award` | `awards` | Entity |
| `Badge` | `badges` | Entity |
| `Calendar` | `calendars` | Entity |
| `Channel` | `channels` | Entity |
| `Committee` | `committees` | Entity |
| `Event` | `events` | Entity |
| `EventScreening` | `event_screenings` | Entity |
| `Festival` | `festivals` | Entity |
| `FestivalLocation` | `festival_locations` | Entity |
| `FestivalRulebook` | `festival_rulebooks` | Entity |
| `FormDefinition` | `form_definitions` | Entity |
| `Group` | `groups` | Entity |
| `JuryVote` | `jury_votes` | Entity |
| `Location` | `locations` | Entity |
| `LocationImage` | `location_images` | Entity |
| `LocationRelation` | `location_relations` | Entity |
| `LocationTag` | `location_tags` | Entity |
| `Message` | `messages` | Entity |
| `ModerationReport` | `moderation_reports` | Entity |
| `NodePolicy` | `node_policies` | Entity |
| `Notification` | `notifications` | Entity |
| `ParticipantTag` | `participant_tags` | Entity |
| `Payment` | `payments` | Entity |
| `Post` | `posts` | Entity |
| `Registration` | `registration_forms` | Entity |
| `Role` | `roles` | Entity |
| `RoleDelegation` | `role_delegations` | Entity |
| `RoleGroup` | `role_groups` | Entity |
| `RoleTransition` | `role_transitions` | Entity |
| `ShortFilm` | `shortfilms` | Entity |
| `ShortFilmLocation` | `shortfilm_locations` | Entity |
| `User` | `users` | Entity |
| `UserAlias` | `user_aliases` | Entity |
| `UserBlock` | `user_blocks` | Entity |
| `UserFestival` | `user_festival` | Association (Table) |
| `UserKey` | `user_keys` | Entity |
| `UserRole` | `user_roles` | Entity |
| `UserSession` | `user_sessions` | Entity |
| `ValidationRule` | `validation_rules` | Entity |
| `ValidationRuleGroup` | `validation_rule_groups` | Entity |

Association tables:
- `user_festival` — M2M between `User` and `Festival`
- `validation_rule_group_rules` — M2M between `ValidationRuleGroup` and `ValidationRule`

Total: 40 entity models + 2 association tables = 42 SQLAlchemy constructs.

## Base model

All models inherit from `BaseModel` defined in `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Fields:
- `id`: Primary key, auto-increment integer
- `created_at`: Timestamp assigned at creation
- `updated_at`: Timestamp updated on each modification

## Main models

### Festival
- **Table:** `festivals`
- **Class:** `Festival`
- **Key fields:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relationships:** Has many ShortFilms, Users (M2M via `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Table:** `users`
- **Class:** `User`
- **Key fields:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relationships:** Has many ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (created), EventAttendees, EventReservations

### ShortFilm
- **Table:** `shortfilms`
- **Class:** `ShortFilm`
- **Key fields:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relationships:** Belongs to Festival, belongs to User, has many Awards, has many ShortFilmLocations

### Message
- **Table:** `messages`
- **Class:** `Message`
- **Key fields:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relationships:** Belongs to User (sender), belongs to User (recipient), belongs to Channel

### User-Festival Association
- **Table:** `user_festival`
- **Class:** None (SQLAlchemy Table)
- **Key fields:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relationships:** M2M bridge between User and Festival; composite PK on (user_id, festival_id)

### Award
- **Table:** `awards`
- **Class:** `Award`
- **Key fields:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relationships:** Belongs to Festival, belongs to Event, belongs to ShortFilm, belongs to User (recipient), belongs to User (verifier), belongs to User (creator)

### Badge
- **Table:** `badges`
- **Class:** `Badge`
- **Key fields:** name, description, image_url (SVG preferred), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relationships:** Belongs to Festival, has many BadgeAssignments
- **Notes:** Feature in active development and deactivated by default (`badges.enabled`); only the admin team activates it.

### Channel
- **Table:** `channels`
- **Class:** `Channel`
- **Key fields:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relationships:** Belongs to User (creator), has many ChannelMembers, has many Messages

### Committee
- **Table:** `committees`
- **Class:** `Committee`
- **Key fields:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relationships:** Belongs to Festival, belongs to Role, has many CommitteeMembers

### Event
- **Table:** `events`
- **Class:** `Event`
- **Key fields:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relationships:** Belongs to Festival, belongs to User (creator), has many EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Table:** `notifications`
- **Class:** `Notification`
- **Key fields:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relationships:** Belongs to User (recipient), belongs to User (related)

### ParticipantTag
- **Table:** `participant_tags`
- **Class:** `ParticipantTag`
- **Key fields:** name, display_name, description, category, is_global, is_active, sort_order
- **Relationships:** Has many UserParticipantTags, has many FestivalParticipantTags

### Post
- **Table:** `posts`
- **Class:** `Post`
- **Key fields:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relationships:** Belongs to User (author), belongs to User (wall), belongs to Festival (wall), has many replies (Post), belongs to Post (parent)
- **Notes:** Feature in active development.

### Registration
- **Table:** `registration_forms`
- **Class:** `RegistrationForm`
- **Key fields:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relationships:** Belongs to Festival, has many RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Table:** `roles`
- **Class:** `Role`
- **Key fields:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relationships:** Belongs to Role (parent), belongs to RoleGroup, has many UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Table:** `user_aliases`
- **Class:** `UserAlias`
- **Key fields:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relationships:** Belongs to User
- **Notes:** Allows visible names per context (global, festival, shortfilm, chat, public_profile, credits) with visibility control

### UserKey
- **Table:** `user_keys`
- **Class:** `UserKey`
- **Key fields:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relationships:** Belongs to User
- **Notes:** Stores the X25519 public key for E2EE; one active key per user

### UserSession
- **Table:** `user_sessions`
- **Class:** `UserSession`
- **Key fields:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relationships:** Belongs to User

### ValidationRule
- **Table:** `validation_rules`
- **Class:** `ValidationRule`
- **Key fields:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relationships:** M2M with ValidationRuleGroup via `validation_rule_group_rules`

### Payment
- **Table:** `payments`
- **Class:** `Payment`
- **Key fields:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relationships:** Belongs to Registration

### JuryVote
- **Table:** `jury_votes`
- **Class:** `JuryVote`
- **Key fields:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relationships:** Belongs to Festival, belongs to ShortFilm, belongs to User (juror)

### NodePolicy
- **Table:** `node_policies`
- **Class:** `NodePolicy`
- **Key fields:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relationships:** Federation entity

### ModerationReport
- **Table:** `moderation_reports`
- **Class:** `ModerationReport`
- **Key fields:** reporter_node, target_node, target_user_ref, reason, status
- **Relationships:** Federation entity

### Location
- **Table:** `locations`
- **Class:** `Location`
- **Key fields:** name, description, latitude, longitude, address, is_active
- **Relationships:** Belongs to Festival (M2M), has many LocationImages, LocationTags, LocationRelations

### EventScreening
- **Table:** `event_screenings`
- **Class:** `EventScreening`
- **Key fields:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relationships:** Belongs to Event, belongs to ShortFilm

### FestivalRulebook
- **Table:** `festival_rulebooks`
- **Class:** `FestivalRulebook`
- **Key fields:** festival_id (FK), title, content, file_url, is_active
- **Relationships:** Belongs to Festival

### FormDefinition
- **Table:** `form_definitions`
- **Class:** `FormDefinition`
- **Key fields:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relationships:** Belongs to Festival, has many FormPages, FormLinks, FormResponses

### Group
- **Table:** `groups`
- **Class:** `Group`
- **Key fields:** name, display_name, description, sort_order, is_active
- **Relationships:** Has many RoleGroupMemberships, Roles

### AppSetting
- **Table:** `app_settings`
- **Class:** `AppSetting`
- **Key fields:** key, value, description, is_public
- **Relationships:** Configuration entity

### AuditLog
- **Table:** `audit_logs`
- **Class:** `AuditLog`
- **Key fields:** actor_id (FK), action, target, ip, created_at
- **Relationships:** Belongs to User (actor), append-only

### UserBlock
- **Table:** `user_blocks`
- **Class:** `UserBlock`
- **Key fields:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relationships:** Belongs to User (blocker), belongs to User (blocked)

### RoleDelegation
- **Table:** `role_delegations`
- **Class:** `RoleDelegation`
- **Key fields:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relationships:** Belongs to User (delegator), belongs to User (delegate), belongs to Role, belongs to Festival, belongs to User (revoker)

### RoleTransition
- **Table:** `role_transitions`
- **Class:** `RoleTransition`
- **Key fields:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relationships:** Belongs to User, belongs to Role (origin), belongs to Role (destination), belongs to Festival (origin), belongs to Festival (destination), belongs to User (change responsible)

### EventTicketType
- **Table:** `event_ticket_types`
- **Class:** `EventTicketType`
- **Key fields:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relationships:** Belongs to Event

### EventSeat
- **Table:** `event_seats`
- **Class:** `EventSeat`
- **Key fields:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relationships:** Belongs to Event, belongs to EventTicketType

### EventReservation
- **Table:** `event_reservations`
- **Class:** `EventReservation`
- **Key fields:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relationships:** Belongs to Event, belongs to User (reserver), belongs to User (creator)

### EventAttendee
- **Table:** `event_attendees`
- **Class:** `EventAttendee`
- **Key fields:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relationships:** Belongs to Event, belongs to EventReservation, belongs to User, belongs to EventSeat, belongs to EventTicketType, belongs to User (inviter)

## Database sessions

Database sessions are managed via `get_db()` in `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

This is used as a FastAPI dependency for database access from endpoints.

## SQLite to MariaDB migration notes

Schema changes are managed with Alembic (`backend/alembic/versions/`, 36 versions; `alembic upgrade head`). In production only Alembic, never `create_all`.

When migrating from SQLite to MariaDB:
- SQLite `INTEGER PRIMARY KEY` corresponds to MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` corresponds to MariaDB `TEXT` or `VARCHAR`
- SQLite `DATETIME` is stored as text; MariaDB uses native `DATETIME`
- The migration scripts in `export_sqlite_to_mariadb.py` and `import_mariadb_to_sqlite.py` handle type conversions automatically