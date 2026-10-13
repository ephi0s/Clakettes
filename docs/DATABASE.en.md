# Database documentation

[ES](DATABASE.md) · [EN](DATABASE.en.md) · [FR](DATABASE.fr.md) · [DE](DATABASE.de.md) · [IT](DATABASE.it.md) · [CA](DATABASE.ca.md) · [EU](DATABASE.eu.md) · [GL](DATABASE.gl.md) · [OC](DATABASE.oc.md)

## Overview

Clakettes uses a two-database setup:
- **Development**: SQLite (`clakettes.db`) — default, no setup required
- **Production**: MariaDB — configured via `DATABASE_URL` in `backend/.env`

Migration tools are available to sync between environments:
- `python export_sqlite_to_mariadb.py` — From development to production
- `python import_mariadb_to_sqlite.py` — From production to development

## Model summary (62 constructs: 60 entities + 2 association tables)

| # | Model | Table | Type |
|---|-------|-------|------|
| 1 | Festival | festivals | Entity |
| 2 | User | users | Entity |
| 3 | ShortFilm | shortfilms | Entity |
| 4 | Message | messages | Entity |
| 5 | UserFestival | user_festival | Association (Table) |
| 6 | Award | awards | Entity |
| 7 | Channel | channels | Entity |
| 8 | ChannelMember | channel_members | Entity |
| 9 | Committee | committees | Entity |
| 10 | CommitteeMember | committee_members | Entity |
| 11 | Event | events | Entity |
| 12 | EventTicketType | event_ticket_types | Entity |
| 13 | EventSeat | event_seats | Entity |
| 14 | EventReservation | event_reservations | Entity |
| 15 | EventAttendee | event_attendees | Entity |
| 16 | Notification | notifications | Entity |
| 17 | ParticipantTag | participant_tags | Entity |
| 18 | FestivalParticipantTag | festival_participant_tags | Entity |
| 19 | RegistrationForm | registration_forms | Entity |
| 20 | RegistrationFormSection | registration_form_sections | Entity |
| 21 | RegistrationFormSectionRole | registration_form_section_roles | Entity |
| 22 | RegistrationFormSectionTag | registration_form_section_tags | Entity |
| 23 | RegistrationFormLink | registration_form_links | Entity |
| 24 | FestivalRegistration | festival_registrations | Entity |
| 25 | RegistrationSectionSelection | registration_section_selections | Entity |
| 26 | Role | roles | Entity |
| 27 | FestivalRole | festival_roles | Entity |
| 28 | RoleDependency | role_dependencies | Entity |
| 29 | RoleConflict | role_conflicts | Entity |
| 30 | RoleGroup | role_groups | Entity |
| 31 | RoleGroupMembership | role_group_memberships | Entity |
| 32 | RoleDelegation | role_delegations | Entity |
| 33 | RoleTransition | role_transitions | Entity |
| 34 | UserAlias | user_aliases | Entity |
| 35 | UserKey | user_keys | Entity |
| 36 | UserRole | user_roles | Entity |
| 37 | UserParticipantTag | user_participant_tags | Entity |
| 38 | UserSession | user_sessions | Entity |
| 39 | ValidationRule | validation_rules | Entity |
| 40 | ValidationRuleGroup | validation_rule_groups | Entity |
| 41 | ValidationRuleGroupRules | validation_rule_group_rules | Association (Table) |
| 42 | Group | groups | Entity |
| 42 | GroupMember | group_members | Entity |
| 43 | Location | locations | Entity |
| 44 | LocationTag | location_tags | Entity |
| 45 | ShortFilmLocation | shortfilm_locations | Entity |
| 46 | LocationImage | location_images | Entity |
| 47 | LocationRelation | location_relations | Entity |
| 48 | FestivalLocation | festival_locations | Entity |
| 49 | FormDefinition | form_definitions | Entity |
| 50 | FormPage | form_pages | Entity |
| 51 | FormField | form_fields | Entity |
| 52 | FormFieldOption | form_field_options | Entity |
| 53 | FormResponse | form_responses | Entity |
| 54 | FormFieldResponse | form_field_responses | Entity |
| 55 | FormAccessRule | form_access_rules | Entity |
| 56 | FormLink | form_links | Entity |
| 57 | Payment | payments | Entity |
| 58 | EventScreening | event_screenings | Entity |
| 59 | FestivalRulebook | festival_rulebooks | Entity |
| 60 | AppSetting | app_settings | Entity |
| 61 | AuditLog | audit_logs | Entity |

Total: 60 entity models + 2 association tables = 62 SQLAlchemy constructs

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
- `created_at`: Timestamp set at creation
- `updated_at`: Timestamp updated on every modification

## Models

### Festival
- **Table:** `festivals`
- **Class:** `Festival`
- **Key fields:** name, description, location, latitude, longitude, is_active, website, logo_url, allow_alias_display
- **Relations:** Has many ShortFilms, has many Users (M2M via `user_festival`), has many FestivalRoles, has many FestivalParticipantTags, has many UserRoles, has many UserParticipantTags, has many RegistrationForms, has many FestivalRegistrations, has many Events, has many Awards

---

### User
- **Table:** `users`
- **Class:** `User`
- **Key fields:** username, email, password_hash, full_name, role, bio, avatar_url, is_active,
  is_public, is_public_email, is_public_bio, is_public_location (`False` by default), latitude, longitude,
  dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relations:** Has many ShortFilms, has many Festivals (M2M via `user_festival`), has many UserRoles, has many UserParticipantTags, has many UserAliases, has many FestivalRegistrations, has many Sessions, has many Awards, has many Events (created), has many EventAttendees, has many EventReservations

---

### ShortFilm
- **Table:** `shortfilms`
- **Class:** `ShortFilm`
- **Key fields:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relations:** Belongs to Festival, belongs to User, has many Awards

---

### Message
- **Table:** `messages`
- **Class:** `Message`
- **Key fields:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relations:** Belongs to User (sender), belongs to User (recipient), belongs to Channel

---

### User-Festival Association
- **Table:** `user_festival`
- **Class:** None (SQLAlchemy Table)
- **Key fields:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relations:** M2M bridge between User and Festival; composite PK on (user_id, festival_id)

---

### Award
- **Table:** `awards`
- **Class:** `Award`
- **Key fields:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relations:** Belongs to Festival, belongs to Event, belongs to ShortFilm, belongs to User (recipient), belongs to User (verifier), belongs to User (creator)

---

### Channel
- **Table:** `channels`
- **Class:** `Channel`
- **Key fields:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relations:** Belongs to User (creator), has many ChannelMembers, has many Messages

#### ChannelMember
- **Table:** `channel_members`
- **Class:** `ChannelMember`
- **Key fields:** channel_id (FK), user_id (FK), role, joined_at, is_active
- **Relations:** Belongs to Channel, belongs to User
- **Notes:** Role limited to admin, moderator, member

---

### Committee
- **Table:** `committees`
- **Class:** `Committee`
- **Key fields:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relations:** Belongs to Festival, belongs to Role, has many CommitteeMembers

#### CommitteeMember
- **Table:** `committee_members`
- **Class:** `CommitteeMember`
- **Key fields:** committee_id (FK), user_id (FK), role_in_committee, assigned_by (FK), is_active, joined_at, notes
- **Relations:** Belongs to Committee, belongs to User, belongs to User (assigner)

---

### Event
- **Table:** `events`
- **Class:** `Event`
- **Key fields:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relations:** Belongs to Festival, belongs to User (creator), has many EventTicketTypes, has many EventSeats, has many EventReservations, has many EventAttendees, has many Awards

#### EventTicketType
- **Table:** `event_ticket_types`
- **Class:** `EventTicketType`
- **Key fields:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relations:** Belongs to Event, has many EventAttendees, has many EventSeats

#### EventSeat
- **Table:** `event_seats`
- **Class:** `EventSeat`
- **Key fields:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relations:** Belongs to Event, belongs to EventTicketType, has one EventAttendee

#### EventReservation
- **Table:** `event_reservations`
- **Class:** `EventReservation`
- **Key fields:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relations:** Belongs to Event, belongs to User (booker), belongs to User (creator), has many EventAttendees

#### EventAttendee
- **Table:** `event_attendees`
- **Class:** `EventAttendee`
- **Key fields:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relations:** Belongs to Event, belongs to EventReservation, belongs to User, belongs to EventSeat, belongs to EventTicketType, belongs to User (inviter)

---

### Notification
- **Table:** `notifications`
- **Class:** `Notification`
- **Key fields:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relations:** Belongs to User (recipient), belongs to User (related)

---

### ParticipantTag
- **Table:** `participant_tags`
- **Class:** `ParticipantTag`
- **Key fields:** name, display_name, description, category, is_global, is_active, sort_order
- **Relations:** Has many UserParticipantTags, has many FestivalParticipantTags

#### FestivalParticipantTag
- **Table:** `festival_participant_tags`
- **Class:** `FestivalParticipantTag`
- **Key fields:** festival_id (FK), tag_id (FK), is_active, is_required, max_selections, can_submit_films, max_film_submissions, requires_approval, allowed_categories, is_exclusive
- **Relations:** Belongs to Festival, belongs to ParticipantTag

---

### Registration
- **Table:** `registration_forms`
- **Class:** `RegistrationForm`
- **Key fields:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relations:** Belongs to Festival, has many RegistrationFormSections, has many RegistrationFormLinks, has many FestivalRegistrations

#### RegistrationFormSection
- **Table:** `registration_form_sections`
- **Class:** `RegistrationFormSection`
- **Key fields:** form_id (FK), title, description, sort_order, allow_multiple_roles, max_selections, is_required
- **Relations:** Belongs to RegistrationForm, has many RegistrationFormSectionRoles, has many RegistrationFormSectionTags, has many RegistrationSectionSelections

#### RegistrationFormSectionRole
- **Table:** `registration_form_section_roles`
- **Class:** `RegistrationFormSectionRole`
- **Key fields:** section_id (FK), role_id (FK), max_assignees, requires_approval, sort_order
- **Relations:** Belongs to RegistrationFormSection, belongs to Role

#### RegistrationFormSectionTag
- **Table:** `registration_form_section_tags`
- **Class:** `RegistrationFormSectionTag`
- **Key fields:** section_id (FK), tag_id (FK), is_required, max_selections, sort_order
- **Relations:** Belongs to RegistrationFormSection, belongs to ParticipantTag

#### RegistrationFormLink
- **Table:** `registration_form_links`
- **Class:** `RegistrationFormLink`
- **Key fields:** form_id (FK), token, is_unique, is_public, is_active, expires_at, max_uses, use_count, assigned_user_id (FK), notes
- **Relations:** Belongs to RegistrationForm, belongs to User (assigned), has many FestivalRegistrations

#### FestivalRegistration
- **Table:** `festival_registrations`
- **Class:** `FestivalRegistration`
- **Key fields:** user_id (FK), festival_id (FK), form_id (FK), link_id (FK), status, assigned_by (FK), approved_by (FK), approved_at, notes, is_hidden
- **Relations:** Belongs to User, belongs to Festival, belongs to RegistrationForm, belongs to RegistrationFormLink, belongs to User (assigner), belongs to User (approver), has many RegistrationSectionSelections

#### RegistrationSectionSelection
- **Table:** `registration_section_selections`
- **Class:** `RegistrationSectionSelection`
- **Key fields:** registration_id (FK), section_id (FK), role_id (FK), additional_tags (JSON), notes
- **Relations:** Belongs to FestivalRegistration, belongs to RegistrationFormSection, belongs to Role

---

### Role
- **Table:** `roles`
- **Class:** `Role`
- **Key fields:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relations:** Belongs to Role (parent), belongs to RoleGroup, has many UserRoles, has many FestivalRoles, has many RoleGroupMemberships, has many RoleDependencies, has many RoleConflicts

#### FestivalRole
- **Table:** `festival_roles`
- **Class:** `FestivalRole`
- **Key fields:** festival_id (FK), role_id (FK), is_active, custom_permissions, max_assignees
- **Relations:** Belongs to Festival, belongs to Role

#### RoleDependency
- **Table:** `role_dependencies`
- **Class:** `RoleDependency`
- **Key fields:** role_id (FK), depends_on_role_id (FK), dependency_type, festival_id (FK), notes
- **Relations:** Belongs to Role (dependent), belongs to Role (requirement), belongs to Festival

#### RoleConflict
- **Table:** `role_conflicts`
- **Class:** `RoleConflict`
- **Key fields:** role_id (FK), conflicts_with_role_id (FK), conflict_type, festival_id (FK), notes
- **Relations:** Belongs to Role, belongs to Role (conflicting), belongs to Festival

---

### RoleDelegation
- **Table:** `role_delegations`
- **Class:** `RoleDelegation`
- **Key fields:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relations:** Belongs to User (delegator), belongs to User (delegate), belongs to Role, belongs to Festival, belongs to User (revoker)

---

### RoleGroup
- **Table:** `role_groups`
- **Class:** `RoleGroup`
- **Key fields:** name, display_name, description, sort_order, is_active
- **Relations:** Has many RoleGroupMemberships, has many Roles

#### RoleGroupMembership
- **Table:** `role_group_memberships`
- **Class:** `RoleGroupMembership`
- **Key fields:** group_id (FK), role_id (FK), level, is_leader, is_active
- **Relations:** Belongs to RoleGroup, belongs to Role

---

### RoleTransition
- **Table:** `role_transitions`
- **Class:** `RoleTransition`
- **Key fields:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relations:** Belongs to User, belongs to Role (source), belongs to Role (target), belongs to Festival (source), belongs to Festival (target), belongs to User (changer)

---

### UserAlias
- **Table:** `user_aliases`
- **Class:** `UserAlias`
- **Key fields:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relations:** Belongs to User
- **Notes:** Supports per-context display names (global, festival, shortfilm, chat, public_profile, credits) with visibility control

---

### UserKey
- **Table:** `user_keys`
- **Class:** `UserKey`
- **Key fields:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relations:** Belongs to User
- **Notes:** Stores the X25519 public key for E2EE; one active key per user

---

### UserRole
- **Table:** `user_roles`
- **Class:** `UserRole`
- **Key fields:** user_id (FK), role_id (FK), festival_id (FK), status, visibility, is_primary, is_hidden, assigned_by (FK), approved_by (FK), approved_at, start_date, expires_at, invitation_note, notes
- **Relations:** Belongs to User, belongs to Role, belongs to Festival, belongs to User (assigner), belongs to User (approver)

#### UserParticipantTag
- **Table:** `user_participant_tags`
- **Class:** `UserParticipantTag`
- **Key fields:** user_id (FK), tag_id (FK), festival_id (FK), is_primary, is_hidden, assigned_by (FK), notes
- **Relations:** Belongs to User, belongs to ParticipantTag, belongs to Festival, belongs to User (assigner)

---

### UserSession
- **Table:** `user_sessions`
- **Class:** `UserSession`
- **Key fields:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relations:** Belongs to User

---

### ValidationRule
- **Table:** `validation_rules`
- **Class:** `ValidationRule`
- **Key fields:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relations:** M2M with ValidationRuleGroup via `validation_rule_group_rules`

#### ValidationRuleGroup
- **Table:** `validation_rule_groups`
- **Class:** `ValidationRuleGroup`
- **Key fields:** name, description, scope, scope_id, is_active
- **Relations:** M2M with ValidationRule via `validation_rule_group_rules`

#### ValidationRuleGroupRules (association)
- **Table:** `validation_rule_group_rules`
- **Class:** None (SQLAlchemy Table)
- **Key fields:** group_id (FK, PK), rule_id (FK, PK)
- **Relations:** M2M bridge between ValidationRuleGroup and ValidationRule

---

## Simplified entity-relationship diagram

```
+---------------------------+       +------------------+       +----------------------+
|         Users            |       |  user_festival    |       |      Festivals       |
+---------------------------+       +------------------+       +----------------------+
| id (PK)                  |<----->| user_id (FK)      |<----->| id (PK)              |
| username                 |       | festival_id (FK)  |       | name                 |
| email                    |       | role              |       | location             |
| password_hash            |       | joined_at         |       | latitude, longitude  |
| full_name, bio           |       +------------------+       | is_active            |
| avatar_url               |                                  | website, logo_url    |
| role, is_active          |                                  | allow_alias_display  |
| is_public* (4 flags)     |                                  +----------------------+
| latitude, longitude      |                                        |    |    |
+---------------------------+                                        |    |    |
    |    |    |    |       |                                         |    |    |
    |    |    |    |       |     +-----------------------+          |    |    |
    |    |    |    |       |     |    UserRoles          |<---------+    |    |
    |    |    |    |       +---->|    UserParticipantTags|               |    |
    |    |    |    |             +-----------------------+               |    |
    |    |    |    |                                                     |    |
    |    |    |    +---------->+-----------------------+                 |    |
    |    |    |                |    UserAliases        |                 |    |
    |    |    |                +-----------------------+                 |    |
    |    |    |                                                          |    |
    |    |    +---------->+----------------------+     +-----------------+    |
    |    |                |    UserSessions      |     |                      |
    |    |                +----------------------+     v                      |
    |    |                                          +----------------------+  |
    |    +---------->+----------------------+       |      Events          |  |
    |                 |   UserKeys (E2EE)   |       +----------------------+  |
    |                 +----------------------+       | id (PK)              |  |
    |                                                | festival_id (FK)    +--+
    |    +---------->+----------------------+       | title, event_type   |
    |    |           |   ShortFilms         |       | start_date, end_date|
    |    |           +----------------------+       | location, venue     |
    |    |           | id (PK)              |       | capacity, is_public |
    v    v           | user_id (FK)         |       | image_url, color    |
+-----------+       | festival_id (FK)     |       +----------------------+
| Messages  |       | title, duration      |            |    |    |    |
+-----------+       | video_url, thumbnail |            |    |    |    |
| id (PK)   |       | is_public, tags      |            v    v    v    v
| sender_id |       +----------------------+       +--+  +--+  +--+  +---+
| receiver  |               |                      |E.TicketType|Seat|Resv|
| group_id  |               v                      +--+  +--+  +--+  +---+
| channel   |       +----------------------+       |   |  |   |  |
| content   |       |      Awards          |       v   v  v   v  v
| msg_type  |       +----------------------+    +----------------------+
| media_url |       | festival_id (FK)     |    |   EventAttendees     |
| vcard/ical|       | event_id (FK)        |    +----------------------+
+-----------+       | shortfilm_id (FK)    |
                    | user_id (FK)         |
                    | award_name, category |
                    | position, is_winner  |
                    | prize_amount, year   |
                    +----------------------+

+----------------------+      +----------------------+
|     Committees       |      |      Channels        |
+----------------------+      +----------------------+
| id (PK)              |      | id (PK)              |
| festival_id (FK)     |      | name, description    |
| name, description    |      | channel_type          |
| role_id (FK)         |      | max_members           |
| is_active            |      | created_by (FK)       |
+----------------------+      +----------------------+
         |                            |
         v                            v
+----------------------+      +----------------------+
|  CommitteeMembers    |      |   ChannelMembers     |
+----------------------+      +----------------------+

+----------------------+      +----------------------+
|  ParticipantTags     |      | FestivalParticipant  |
+----------------------+      | Tags                 |
| id (PK)              |      +----------------------+
| name, display_name   |<-----| festival_id (FK)     |
| category, is_global  |      | tag_id (FK)          |
| sort_order           |      +----------------------+
+----------------------+
         |
         v
+----------------------+      +----------------------+
|UserParticipantTags   |      |   Notifications      |
+----------------------+      +----------------------+
| user_id (FK)         |      | user_id (FK)         |
| tag_id (FK)          |      | title, message       |
| festival_id (FK)     |      | notification_type    |
+----------------------+      | related_user_id (FK) |
                               +----------------------+

+------------------------------+     +------------------------------+
|        Roles                 |     |     RoleGroups               |
+------------------------------+     +------------------------------+
| id (PK)                      |     | id (PK)                      |
| name, display_name           |<----| group_id (FK)                |
| scope (global|festival)      |     | name, display_name           |
| hierarchy_level              |     +------------------------------+
| parent_role_id (FK)          |              |
| group_id (FK)                |              v
| permissions                  |     +------------------------------+
+------------------------------+     | RoleGroupMemberships         |
    |         |         |            | group_id (FK)                |
    |         |         |            | role_id (FK)                 |
    v         v         v            | level, is_leader             |
+----------+ +-------+ +----------+  +------------------------------+
|Festival  | |Role   | |Role      |
|Roles     | |Deps   | |Conflicts |
+----------+ +-------+ +----------+

+------------------------------+     +------------------------------+
|     RegistrationForms        |     |    RoleDelegations           |
+------------------------------+     +------------------------------+
| id (PK)                      |     | delegator_id (FK)            |
| festival_id (FK)             |     | delegate_id (FK)             |
| title, is_active             |     | role_id (FK)                 |
| starts_at, ends_at           |     | festival_id (FK)             |
+------------------------------+     | status, reason               |
    |         |         |            | scope_limitations            |
    v         v         v            | expires_at                   |
+----------+ +-------+ +----------+  +------------------------------+
|Sections  | |Links  | |Registrat |
+----------+ +-------+ |ions      |
|id (PK)   | |token  | +----------+  +------------------------------+
|form_id   | |unique | |user_id   |  |   RoleTransitions           |
|title     | |public | |festival  |  +------------------------------+
+----------+ |expires| |status    |  | user_id (FK)                 |
    |        +-------+ |assigned  |  | from_role_id (FK)            |
    v                  |approved  |  | to_role_id (FK)              |
+----------+           +----------+  | transition_type              |
|SecRoles  |                |        | changed_by (FK)              |
|SecTags   |                v        +------------------------------+
|Selections|        +---------------+
+----------+        |SectionSelect  |
                     +---------------+

+------------------------------+
|   ValidationRules            |
+------------------------------+       +------------------------------+
| id (PK)                      |       |   ValidationRuleGroups      |
| name, scope, scope_id        |       +------------------------------+
| field_name, field_label      |<----->| id (PK)                      |
| field_type, is_required      |       | name, scope, scope_id        |
| regex, allowed_values (JSON) |       | is_active                    |
| min/max_length, depends_on   |       +------------------------------+
+------------------------------+
```

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

Schema changes are managed with Alembic (`backend/alembic/versions/`, 18 versions;
`alembic upgrade head`). In production Alembic only, never `create_all`.

When migrating from SQLite to MariaDB:
- SQLite `INTEGER PRIMARY KEY` maps to MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` maps to MariaDB `TEXT` or `VARCHAR`
- SQLite `DATETIME` is stored as text; MariaDB uses native `DATETIME`
- The migration scripts in `export_sqlite_to_mariadb.py` and `import_mariadb_to_sqlite.py` handle type conversions automatically
