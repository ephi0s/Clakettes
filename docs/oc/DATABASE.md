# Documentacion de la banca de donadas

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](DATABASE.md)

## Descripcion generala

Clakettes utiliza una configuracion amb doas bancas de donadas:
- **Desvolopament**: SQLite (`clakettes.db`) — per defaut, sens configuracion requerida
- **Produccion**: MariaDB — se configura mejançant `DATABASE_URL` en `backend/.env`

I a aisinas de migracion disponiblas per sincronizar entre environas:
- `python export_sqlite_to_mariadb.py` — De desarrollo a producción
- `python import_mariadb_to_sqlite.py` — De producción a desarrollo

## Resumit de modèls (62 constructes: 60 entitats + 2 taulas d'associacion)

| # | Modèl | Taula | Tipe |
|---|---|-------|------|
| 1 | Festival | festivals | Entitat |
| 2 | User | users | Entitat |
| 3 | ShortFilm | shortfilms | Entitat |
| 4 | Message | messages | Entitat |
| 5 | UserFestival | user_festival | Associacion (Taula) |
| 6 | Award | awards | Entitat |
| 7 | Channel | channels | Entitat |
| 8 | ChannelMember | channel_members | Entitat |
| 9 | Committee | committees | Entitat |
| 10 | CommitteeMember | committee_members | Entitat |
| 11 | Event | events | Entitat |
| 12 | EventTicketType | event_ticket_types | Entitat |
| 13 | EventSeat | event_seats | Entitat |
| 14 | EventReservation | event_reservations | Entitat |
| 15 | EventAttendee | event_attendees | Entitat |
| 16 | Notification | notifications | Entitat |
| 17 | ParticipantTag | participant_tags | Entitat |
| 18 | FestivalParticipantTag | festival_participant_tags | Entitat |
| 19 | RegistrationForm | registration_forms | Entitat |
| 20 | RegistrationFormSection | registration_form_sections | Entitat |
| 21 | RegistrationFormSectionRole | registration_form_section_roles | Entitat |
| 22 | RegistrationFormSectionTag | registration_form_section_tags | Entitat |
| 23 | RegistrationFormLink | registration_form_links | Entitat |
| 24 | FestivalRegistration | festival_registrations | Entitat |
| 25 | RegistrationSectionSelection | registration_section_selections | Entitat |
| 26 | Role | roles | Entitat |
| 27 | FestivalRole | festival_roles | Entitat |
| 28 | RoleDependency | role_dependencies | Entitat |
| 29 | RoleConflict | role_conflicts | Entitat |
| 30 | RoleGroup | role_groups | Entitat |
| 31 | RoleGroupMembership | role_group_memberships | Entitat |
| 32 | RoleDelegation | role_delegations | Entitat |
| 33 | RoleTransition | role_transitions | Entitat |
| 34 | UserAlias | user_aliases | Entitat |
| 35 | UserKey | user_keys | Entitat |
| 36 | UserRole | user_roles | Entitat |
| 37 | UserParticipantTag | user_participant_tags | Entitat |
| 38 | UserSession | user_sessions | Entitat |
| 39 | ValidationRule | validation_rules | Entitat |
| 40 | ValidationRuleGroup | validation_rule_groups | Entitat |
| 41 | ValidationRuleGroupRules | validation_rule_group_rules | Associacion (Taula) |
| 42 | Group | groups | Entitat |
| 42 | GroupMember | group_members | Entitat |
| 43 | Location | locations | Entitat |
| 44 | LocationTag | location_tags | Entitat |
| 45 | ShortFilmLocation | shortfilm_locations | Entitat |
| 46 | LocationImage | location_images | Entitat |
| 47 | LocationRelation | location_relations | Entitat |
| 48 | FestivalLocation | festival_locations | Entitat |
| 49 | FormDefinition | form_definitions | Entitat |
| 50 | FormPage | form_pages | Entitat |
| 51 | FormField | form_fields | Entitat |
| 52 | FormFieldOption | form_field_options | Entitat |
| 53 | FormResponse | form_responses | Entitat |
| 54 | FormFieldResponse | form_field_responses | Entitat |
| 55 | FormAccessRule | form_access_rules | Entitat |
| 56 | FormLink | form_links | Entitat |
| 57 | Payment | payments | Entitat |
| 58 | EventScreening | event_screenings | Entitat |
| 59 | FestivalRulebook | festival_rulebooks | Entitat |
| 60 | AppSetting | app_settings | Entitat |
| 61 | AuditLog | audit_logs | Entitat |

Totau: 60 modèls d'entitat + 2 taulas d'associacion = 62 constructes de SQLAlchemy

## Modèl de basa

Totes los modèls eiretan de `BaseModel` definit en `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Camps:
- `id`: Clau primària, entièr autoincrementau
- `created_at`: Marca temporala assignada en la creacion
- `updated_at`: Marca temporala actualizada en cada modificacion

## Modèls

### Festival
- **Taula:** `festivals`
- **Classa:** `Festival`
- **Camps claus:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relacions:** A fòrça ShortFilms, a fòrça Users (M2M mejançant `user_festival`), a fòrça FestivalRoles, a fòrça FestivalParticipantTags, a fòrça UserRoles, a fòrça UserParticipantTags, a fòrça RegistrationForms, a fòrça FestivalRegistrations, a fòrça Events, a fòrça Awards

---

### User
- **Taula:** `users`
- **Classa:** `User`
- **Camps claus:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active,
  is_public, is_public_email, is_public_bio, is_public_location (`False` per defaut), latitude, longitude,
  dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relacions:** A fòrça ShortFilms, a fòrça Festivals (M2M mejançant `user_festival`), a fòrça UserRoles, a fòrça UserParticipantTags, a fòrça UserAliases, a fòrça FestivalRegistrations, a fòrça Sessions, a fòrça Awards, a fòrça Events (creats), a fòrça EventAttendees, a fòrça EventReservations

---

### ShortFilm
- **Taula:** `shortfilms`
- **Classa:** `ShortFilm`
- **Camps claus:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relacions:** Aperten a Festival, aperten a User, a fòrça Awards

---

### Message
- **Taula:** `messages`
- **Classa:** `Message`
- **Camps claus:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relacions:** Aperten a User (remetent), aperten a User (destinatari), aperten a Channel

---

### User-Festival Association
- **Taula:** `user_festival`
- **Classa:** None (SQLAlchemy Table)
- **Camps claus:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relacions:** Pònt M2M entre User e Festival; PK compausada en (user_id, festival_id)

---

### Award
- **Taula:** `awards`
- **Classa:** `Award`
- **Camps claus:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relacions:** Aperten a Festival, aperten a Event, aperten a ShortFilm, aperten a User (destinatari), aperten a User (verificador), aperten a User (creador)

---

### Badge
- **Taula:** `badges`
- **Classa:** `Badge`
- **Camps claus:** name, description, image_url (SVG preferit), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relacions:** Aperten a Festival, a mantas BadgeAssignments
- **Nòtas:** Foncion en desvolopament actiu e desactivada per defaut (`badges.enabled`); sonque l'equipa admin l'activa. Los badges de festenal son autrejats per la gestion del festenal o los admins.

#### BadgeAssignment
- **Taula:** `badge_assignments`
- **Classa:** `BadgeAssignment`
- **Camps claus:** badge_id (FK), target_user_id (FK), target_festival_id (FK), granted_by (FK), grant_festival_id, reason
- **Relacions:** Aperten a Badge, aperten a User (destinatari), aperten a Festival (destinatari)

---

### Channel
- **Taula:** `channels`
- **Classa:** `Channel`
- **Camps claus:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relacions:** Aperten a User (creador), a fòrça ChannelMembers, a fòrça Messages

#### ChannelMember
- **Taula:** `channel_members`
- **Classa:** `ChannelMember`
- **Camps claus:** channel_id (FK), user_id (FK), role, joined_at, is_active
- **Relacions:** Aperten a Channel, aperten a User
- **Nòtas:** Role limitat a admin, moderator, member

---

### Committee
- **Taula:** `committees`
- **Classa:** `Committee`
- **Camps claus:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relacions:** Aperten a Festival, aperten a Role, a fòrça CommitteeMembers

#### CommitteeMember
- **Taula:** `committee_members`
- **Classa:** `CommitteeMember`
- **Camps claus:** committee_id (FK), user_id (FK), role_in_committee, assigned_by (FK), is_active, joined_at, notes
- **Relacions:** Aperten a Committee, aperten a User, aperten a User (assignador)

---

### Event
- **Taula:** `events`
- **Classa:** `Event`
- **Camps claus:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relacions:** Aperten a Festival, aperten a User (creador), a fòrça EventTicketTypes, a fòrça EventSeats, a fòrça EventReservations, a fòrça EventAttendees, a fòrça Awards

#### EventTicketType
- **Taula:** `event_ticket_types`
- **Classa:** `EventTicketType`
- **Camps claus:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relacions:** Aperten a Event, a fòrça EventAttendees, a fòrça EventSeats

#### EventSeat
- **Taula:** `event_seats`
- **Classa:** `EventSeat`
- **Camps claus:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relacions:** Aperten a Event, aperten a EventTicketType, a un EventAttendee

#### EventReservation
- **Taula:** `event_reservations`
- **Classa:** `EventReservation`
- **Camps claus:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relacions:** Aperten a Event, aperten a User (reservador), aperten a User (creador), a fòrça EventAttendees

#### EventAttendee
- **Taula:** `event_attendees`
- **Classa:** `EventAttendee`
- **Camps claus:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relacions:** Aperten a Event, aperten a EventReservation, aperten a User, aperten a EventSeat, aperten a EventTicketType, aperten a User (invitador)

---

### Notification
- **Taula:** `notifications`
- **Classa:** `Notification`
- **Camps claus:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relacions:** Aperten a User (destinatari), aperten a User (relacionat)

---

### ParticipantTag
- **Taula:** `participant_tags`
- **Classa:** `ParticipantTag`
- **Camps claus:** name, display_name, description, category, is_global, is_active, sort_order
- **Relacions:** A fòrça UserParticipantTags, a fòrça FestivalParticipantTags

#### FestivalParticipantTag
- **Taula:** `festival_participant_tags`
- **Classa:** `FestivalParticipantTag`
- **Camps claus:** festival_id (FK), tag_id (FK), is_active, is_required, max_selections, can_submit_films, max_film_submissions, requires_approval, allowed_categories, is_exclusive
- **Relacions:** Aperten a Festival, aperten a ParticipantTag

---

### Post
- **Taula:** `posts`
- **Classa:** `Post`
- **Camps claus:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type (youtube, vimeo, dailymotion, odysee, ivoox, podimo, generic), allow_replies, is_pinned, is_hidden
- **Relacions:** Aperten a User (autor), aperten a User (mur), aperten a Festival (mur), a mantas responsas (Post), aperten a Post (paire)
- **Nòtas:** Foncion en desvolopament actiu. Las publicacions de primièr nivèl apuntan a un mur d’utilizaire o de festenal; las responsas eretan l’encastre del paire e exigisson `allow_replies`. La moderacion (penjar, escondre, blocar las responsas) reven als admins centrals, a la gestion del festenal e als ròtles moderators del festenal.

---

### Registration
- **Taula:** `registration_forms`
- **Classa:** `RegistrationForm`
- **Camps claus:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relacions:** Aperten a Festival, a fòrça RegistrationFormSections, a fòrça RegistrationFormLinks, a fòrça FestivalRegistrations

#### RegistrationFormSection
- **Taula:** `registration_form_sections`
- **Classa:** `RegistrationFormSection`
- **Camps claus:** form_id (FK), title, description, sort_order, allow_multiple_roles, max_selections, is_required
- **Relacions:** Aperten a RegistrationForm, a fòrça RegistrationFormSectionRoles, a fòrça RegistrationFormSectionTags, a fòrça RegistrationSectionSelections

#### RegistrationFormSectionRole
- **Taula:** `registration_form_section_roles`
- **Classa:** `RegistrationFormSectionRole`
- **Camps claus:** section_id (FK), role_id (FK), max_assignees, requires_approval, sort_order
- **Relacions:** Aperten a RegistrationFormSection, aperten a Role

#### RegistrationFormSectionTag
- **Taula:** `registration_form_section_tags`
- **Classa:** `RegistrationFormSectionTag`
- **Camps claus:** section_id (FK), tag_id (FK), is_required, max_selections, sort_order
- **Relacions:** Aperten a RegistrationFormSection, aperten a ParticipantTag

#### RegistrationFormLink
- **Taula:** `registration_form_links`
- **Classa:** `RegistrationFormLink`
- **Camps claus:** form_id (FK), token, is_unique, is_public, is_active, expires_at, max_uses, use_count, assigned_user_id (FK), notes
- **Relacions:** Aperten a RegistrationForm, aperten a User (assignat), a fòrça FestivalRegistrations

#### FestivalRegistration
- **Taula:** `festival_registrations`
- **Classa:** `FestivalRegistration`
- **Camps claus:** user_id (FK), festival_id (FK), form_id (FK), link_id (FK), status, assigned_by (FK), approved_by (FK), approved_at, notes, is_hidden
- **Relacions:** Aperten a User, aperten a Festival, aperten a RegistrationForm, aperten a RegistrationFormLink, aperten a User (assignador), aperten a User (aprobador), a fòrça RegistrationSectionSelections

#### RegistrationSectionSelection
- **Taula:** `registration_section_selections`
- **Classa:** `RegistrationSectionSelection`
- **Camps claus:** registration_id (FK), section_id (FK), role_id (FK), additional_tags (JSON), notes
- **Relacions:** Aperten a FestivalRegistration, aperten a RegistrationFormSection, aperten a Role

---

### Role
- **Taula:** `roles`
- **Classa:** `Role`
- **Camps claus:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relacions:** Aperten a Role (paire), aperten a RoleGroup, a fòrça UserRoles, a fòrça FestivalRoles, a fòrça RoleGroupMemberships, a fòrça RoleDependencies, a fòrça RoleConflicts

#### FestivalRole
- **Taula:** `festival_roles`
- **Classa:** `FestivalRole`
- **Camps claus:** festival_id (FK), role_id (FK), is_active, custom_permissions, max_assignees
- **Relacions:** Aperten a Festival, aperten a Role

#### RoleDependency
- **Taula:** `role_dependencies`
- **Classa:** `RoleDependency`
- **Camps claus:** role_id (FK), depends_on_role_id (FK), dependency_type, festival_id (FK), notes
- **Relacions:** Aperten a Role (dependenta), aperten a Role (requesit), aperten a Festival

#### RoleConflict
- **Taula:** `role_conflicts`
- **Classa:** `RoleConflict`
- **Camps claus:** role_id (FK), conflicts_with_role_id (FK), conflict_type, festival_id (FK), notes
- **Relacions:** Aperten a Role, aperten a Role (en conflicte), aperten a Festival

---

### RoleDelegation
- **Taula:** `role_delegations`
- **Classa:** `RoleDelegation`
- **Camps claus:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relacions:** Aperten a User (delegador), aperten a User (delegat), aperten a Role, aperten a Festival, aperten a User (revocador)

---

### RoleGroup
- **Taula:** `role_groups`
- **Classa:** `RoleGroup`
- **Camps claus:** name, display_name, description, sort_order, is_active
- **Relacions:** A fòrça RoleGroupMemberships, a fòrça Roles

#### RoleGroupMembership
- **Taula:** `role_group_memberships`
- **Classa:** `RoleGroupMembership`
- **Camps claus:** group_id (FK), role_id (FK), level, is_leader, is_active
- **Relacions:** Aperten a RoleGroup, aperten a Role

---

### RoleTransition
- **Taula:** `role_transitions`
- **Classa:** `RoleTransition`
- **Camps claus:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relacions:** Aperten a User, aperten a Role (origen), aperten a Role (destin), aperten a Festival (origen), aperten a Festival (destin), aperten a User (responsable del cambi)

---

### UserAlias
- **Taula:** `user_aliases`
- **Classa:** `UserAlias`
- **Camps claus:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relacions:** Aperten a User
- **Nòtas:** Admet noms visibles per contèxte (global, festival, shortfilm, chat, public_profile, credits) amb contraròtle de visibilitat

---

### UserKey
- **Taula:** `user_keys`
- **Classa:** `UserKey`
- **Camps claus:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relacions:** Aperten a User
- **Nòtas:** Estòca la clau publica X25519 per E2EE; una clau activa per utilizaire

---

### UserRole
- **Taula:** `user_roles`
- **Classa:** `UserRole`
- **Camps claus:** user_id (FK), role_id (FK), festival_id (FK), status, visibility, is_primary, is_hidden, assigned_by (FK), approved_by (FK), approved_at, start_date, expires_at, invitation_note, notes
- **Relacions:** Aperten a User, aperten a Role, aperten a Festival, aperten a User (assignador), aperten a User (aprobador)

#### UserParticipantTag
- **Taula:** `user_participant_tags`
- **Classa:** `UserParticipantTag`
- **Camps claus:** user_id (FK), tag_id (FK), festival_id (FK), is_primary, is_hidden, assigned_by (FK), notes
- **Relacions:** Aperten a User, aperten a ParticipantTag, aperten a Festival, aperten a User (assignador)

---

### UserSession
- **Taula:** `user_sessions`
- **Classa:** `UserSession`
- **Camps claus:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relacions:** Aperten a User

---

### ValidationRule
- **Taula:** `validation_rules`
- **Classa:** `ValidationRule`
- **Camps claus:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relacions:** M2M amb ValidationRuleGroup mejançant `validation_rule_group_rules`

#### ValidationRuleGroup
- **Taula:** `validation_rule_groups`
- **Classa:** `ValidationRuleGroup`
- **Camps claus:** name, description, scope, scope_id, is_active
- **Relacions:** M2M amb ValidationRule mejançant `validation_rule_group_rules`

#### ValidationRuleGroupRules (association)
- **Taula:** `validation_rule_group_rules`
- **Classa:** None (SQLAlchemy Table)
- **Camps claus:** group_id (FK, PK), rule_id (FK, PK)
- **Relacions:** Pònt M2M entre ValidationRuleGroup e ValidationRule

---

## Diagrama de relacions entre entitats (simplificat)

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

## Sessions de banca de donadas

Las sessions de banca de donadas se gerisson mejançant `get_db()` en `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Aquò s'utiliza coma dependéncia de FastAPI per l'accès a la banca de donadas dempuèi los endpoints.

## Nòtas de migracion de SQLite cap a MariaDB

Los cambiaments d'esquèma se gerisson amb Alembic (`backend/alembic/versions/`, 21 versions;
`alembic upgrade head`). En produccion sonque Alembic, jamai `create_all`.

En migrant de SQLite cap a MariaDB:
- SQLite `INTEGER PRIMARY KEY` se correspònd amb MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` se correspònd amb MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` s'estòca coma tèxte; MariaDB utiliza `DATETIME` natiu
- Los scripts de migracion en `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` gerisson las conversions de tipes automaticament
