# Documentación de la base de datos

[ES](DATABASE.md) · [EN](DATABASE.en.md) · [FR](DATABASE.fr.md) · [DE](DATABASE.de.md) · [IT](DATABASE.it.md) · [CA](DATABASE.ca.md) · [EU](DATABASE.eu.md) · [GL](DATABASE.gl.md) · [OC](DATABASE.oc.md)

## Descripción general

Clakettes utiliza una configuración con dos bases de datos:
- **Desarrollo**: SQLite (`clakettes.db`) — por defecto, no requiere configuración
- **Producción**: MariaDB — se configura mediante `DATABASE_URL` en `backend/.env`

Hay herramientas de migración disponibles para sincronizar entre entornos:
- `python export_sqlite_to_mariadb.py` — De desarrollo a producción
- `python import_mariadb_to_sqlite.py` — De producción a desarrollo

## Resumen de modelos (62 constructos: 60 entidades + 2 tablas de asociación)

| # | Modelo | Tabla | Tipo |
|---|-------|-------|------|
| 1 | Festival | festivals | Entidad |
| 2 | User | users | Entidad |
| 3 | ShortFilm | shortfilms | Entidad |
| 4 | Message | messages | Entidad |
| 5 | UserFestival | user_festival | Asociación (Tabla) |
| 6 | Award | awards | Entidad |
| 7 | Channel | channels | Entidad |
| 8 | ChannelMember | channel_members | Entidad |
| 9 | Committee | committees | Entidad |
| 10 | CommitteeMember | committee_members | Entidad |
| 11 | Event | events | Entidad |
| 12 | EventTicketType | event_ticket_types | Entidad |
| 13 | EventSeat | event_seats | Entidad |
| 14 | EventReservation | event_reservations | Entidad |
| 15 | EventAttendee | event_attendees | Entidad |
| 16 | Notification | notifications | Entidad |
| 17 | ParticipantTag | participant_tags | Entidad |
| 18 | FestivalParticipantTag | festival_participant_tags | Entidad |
| 19 | RegistrationForm | registration_forms | Entidad |
| 20 | RegistrationFormSection | registration_form_sections | Entidad |
| 21 | RegistrationFormSectionRole | registration_form_section_roles | Entidad |
| 22 | RegistrationFormSectionTag | registration_form_section_tags | Entidad |
| 23 | RegistrationFormLink | registration_form_links | Entidad |
| 24 | FestivalRegistration | festival_registrations | Entidad |
| 25 | RegistrationSectionSelection | registration_section_selections | Entidad |
| 26 | Role | roles | Entidad |
| 27 | FestivalRole | festival_roles | Entidad |
| 28 | RoleDependency | role_dependencies | Entidad |
| 29 | RoleConflict | role_conflicts | Entidad |
| 30 | RoleGroup | role_groups | Entidad |
| 31 | RoleGroupMembership | role_group_memberships | Entidad |
| 32 | RoleDelegation | role_delegations | Entidad |
| 33 | RoleTransition | role_transitions | Entidad |
| 34 | UserAlias | user_aliases | Entidad |
| 35 | UserKey | user_keys | Entidad |
| 36 | UserRole | user_roles | Entidad |
| 37 | UserParticipantTag | user_participant_tags | Entidad |
| 38 | UserSession | user_sessions | Entidad |
| 39 | ValidationRule | validation_rules | Entidad |
| 40 | ValidationRuleGroup | validation_rule_groups | Entidad |
| 41 | ValidationRuleGroupRules | validation_rule_group_rules | Asociación (Tabla) |
| 42 | Group | groups | Entidad |
| 42 | GroupMember | group_members | Entidad |
| 43 | Location | locations | Entidad |
| 44 | LocationTag | location_tags | Entidad |
| 45 | ShortFilmLocation | shortfilm_locations | Entidad |
| 46 | LocationImage | location_images | Entidad |
| 47 | LocationRelation | location_relations | Entidad |
| 48 | FestivalLocation | festival_locations | Entidad |
| 49 | FormDefinition | form_definitions | Entidad |
| 50 | FormPage | form_pages | Entidad |
| 51 | FormField | form_fields | Entidad |
| 52 | FormFieldOption | form_field_options | Entidad |
| 53 | FormResponse | form_responses | Entidad |
| 54 | FormFieldResponse | form_field_responses | Entidad |
| 55 | FormAccessRule | form_access_rules | Entidad |
| 56 | FormLink | form_links | Entidad |
| 57 | Payment | payments | Entidad |
| 58 | EventScreening | event_screenings | Entidad |
| 59 | FestivalRulebook | festival_rulebooks | Entidad |
| 60 | AppSetting | app_settings | Entidad |
| 61 | AuditLog | audit_logs | Entidad |

Total: 60 modelos de entidad + 2 tablas de asociación = 62 constructos de SQLAlchemy

## Modelo base

Todos los modelos heredan de `BaseModel` definido en `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Campos:
- `id`: Clave primaria, entero autoincremental
- `created_at`: Marca temporal asignada en la creación
- `updated_at`: Marca temporal actualizada en cada modificación

## Modelos

### Festival
- **Tabla:** `festivals`
- **Clase:** `Festival`
- **Campos clave:** name, description, location, latitude, longitude, is_active, website, logo_url, allow_alias_display
- **Relaciones:** Tiene muchos ShortFilms, tiene muchos Users (M2M mediante `user_festival`), tiene muchos FestivalRoles, tiene muchos FestivalParticipantTags, tiene muchos UserRoles, tiene muchos UserParticipantTags, tiene muchos RegistrationForms, tiene muchos FestivalRegistrations, tiene muchos Events, tiene muchos Awards

---

### User
- **Tabla:** `users`
- **Clase:** `User`
- **Campos clave:** username, email, password_hash, full_name, role, bio, avatar_url, is_active,
  is_public, is_public_email, is_public_bio, is_public_location (`False` por defecto), latitude, longitude,
  dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relaciones:** Tiene muchos ShortFilms, tiene muchos Festivals (M2M mediante `user_festival`), tiene muchos UserRoles, tiene muchos UserParticipantTags, tiene muchos UserAliases, tiene muchos FestivalRegistrations, tiene muchos Sessions, tiene muchos Awards, tiene muchos Events (creados), tiene muchos EventAttendees, tiene muchos EventReservations

---

### ShortFilm
- **Tabla:** `shortfilms`
- **Clase:** `ShortFilm`
- **Campos clave:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relaciones:** Pertenece a Festival, pertenece a User, tiene muchos Awards

---

### Message
- **Tabla:** `messages`
- **Clase:** `Message`
- **Campos clave:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relaciones:** Pertenece a User (remitente), pertenece a User (destinatario), pertenece a Channel

---

### User-Festival Association
- **Tabla:** `user_festival`
- **Clase:** None (SQLAlchemy Table)
- **Campos clave:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relaciones:** Puente M2M entre User y Festival; PK compuesta en (user_id, festival_id)

---

### Award
- **Tabla:** `awards`
- **Clase:** `Award`
- **Campos clave:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relaciones:** Pertenece a Festival, pertenece a Event, pertenece a ShortFilm, pertenece a User (destinatario), pertenece a User (verificador), pertenece a User (creador)

---

### Channel
- **Tabla:** `channels`
- **Clase:** `Channel`
- **Campos clave:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relaciones:** Pertenece a User (creador), tiene muchos ChannelMembers, tiene muchos Messages

#### ChannelMember
- **Tabla:** `channel_members`
- **Clase:** `ChannelMember`
- **Campos clave:** channel_id (FK), user_id (FK), role, joined_at, is_active
- **Relaciones:** Pertenece a Channel, pertenece a User
- **Notas:** Role limitado a admin, moderator, member

---

### Committee
- **Tabla:** `committees`
- **Clase:** `Committee`
- **Campos clave:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relaciones:** Pertenece a Festival, pertenece a Role, tiene muchos CommitteeMembers

#### CommitteeMember
- **Tabla:** `committee_members`
- **Clase:** `CommitteeMember`
- **Campos clave:** committee_id (FK), user_id (FK), role_in_committee, assigned_by (FK), is_active, joined_at, notes
- **Relaciones:** Pertenece a Committee, pertenece a User, pertenece a User (asignador)

---

### Event
- **Tabla:** `events`
- **Clase:** `Event`
- **Campos clave:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relaciones:** Pertenece a Festival, pertenece a User (creador), tiene muchos EventTicketTypes, tiene muchos EventSeats, tiene muchos EventReservations, tiene muchos EventAttendees, tiene muchos Awards

#### EventTicketType
- **Tabla:** `event_ticket_types`
- **Clase:** `EventTicketType`
- **Campos clave:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relaciones:** Pertenece a Event, tiene muchos EventAttendees, tiene muchos EventSeats

#### EventSeat
- **Tabla:** `event_seats`
- **Clase:** `EventSeat`
- **Campos clave:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relaciones:** Pertenece a Event, pertenece a EventTicketType, tiene un EventAttendee

#### EventReservation
- **Tabla:** `event_reservations`
- **Clase:** `EventReservation`
- **Campos clave:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relaciones:** Pertenece a Event, pertenece a User (reservador), pertenece a User (creador), tiene muchos EventAttendees

#### EventAttendee
- **Tabla:** `event_attendees`
- **Clase:** `EventAttendee`
- **Campos clave:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relaciones:** Pertenece a Event, pertenece a EventReservation, pertenece a User, pertenece a EventSeat, pertenece a EventTicketType, pertenece a User (invitador)

---

### Notification
- **Tabla:** `notifications`
- **Clase:** `Notification`
- **Campos clave:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relaciones:** Pertenece a User (destinatario), pertenece a User (relacionado)

---

### ParticipantTag
- **Tabla:** `participant_tags`
- **Clase:** `ParticipantTag`
- **Campos clave:** name, display_name, description, category, is_global, is_active, sort_order
- **Relaciones:** Tiene muchos UserParticipantTags, tiene muchos FestivalParticipantTags

#### FestivalParticipantTag
- **Tabla:** `festival_participant_tags`
- **Clase:** `FestivalParticipantTag`
- **Campos clave:** festival_id (FK), tag_id (FK), is_active, is_required, max_selections, can_submit_films, max_film_submissions, requires_approval, allowed_categories, is_exclusive
- **Relaciones:** Pertenece a Festival, pertenece a ParticipantTag

---

### Registration
- **Tabla:** `registration_forms`
- **Clase:** `RegistrationForm`
- **Campos clave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relaciones:** Pertenece a Festival, tiene muchos RegistrationFormSections, tiene muchos RegistrationFormLinks, tiene muchos FestivalRegistrations

#### RegistrationFormSection
- **Tabla:** `registration_form_sections`
- **Clase:** `RegistrationFormSection`
- **Campos clave:** form_id (FK), title, description, sort_order, allow_multiple_roles, max_selections, is_required
- **Relaciones:** Pertenece a RegistrationForm, tiene muchos RegistrationFormSectionRoles, tiene muchos RegistrationFormSectionTags, tiene muchos RegistrationSectionSelections

#### RegistrationFormSectionRole
- **Tabla:** `registration_form_section_roles`
- **Clase:** `RegistrationFormSectionRole`
- **Campos clave:** section_id (FK), role_id (FK), max_assignees, requires_approval, sort_order
- **Relaciones:** Pertenece a RegistrationFormSection, pertenece a Role

#### RegistrationFormSectionTag
- **Tabla:** `registration_form_section_tags`
- **Clase:** `RegistrationFormSectionTag`
- **Campos clave:** section_id (FK), tag_id (FK), is_required, max_selections, sort_order
- **Relaciones:** Pertenece a RegistrationFormSection, pertenece a ParticipantTag

#### RegistrationFormLink
- **Tabla:** `registration_form_links`
- **Clase:** `RegistrationFormLink`
- **Campos clave:** form_id (FK), token, is_unique, is_public, is_active, expires_at, max_uses, use_count, assigned_user_id (FK), notes
- **Relaciones:** Pertenece a RegistrationForm, pertenece a User (asignado), tiene muchos FestivalRegistrations

#### FestivalRegistration
- **Tabla:** `festival_registrations`
- **Clase:** `FestivalRegistration`
- **Campos clave:** user_id (FK), festival_id (FK), form_id (FK), link_id (FK), status, assigned_by (FK), approved_by (FK), approved_at, notes, is_hidden
- **Relaciones:** Pertenece a User, pertenece a Festival, pertenece a RegistrationForm, pertenece a RegistrationFormLink, pertenece a User (asignador), pertenece a User (aprobador), tiene muchos RegistrationSectionSelections

#### RegistrationSectionSelection
- **Tabla:** `registration_section_selections`
- **Clase:** `RegistrationSectionSelection`
- **Campos clave:** registration_id (FK), section_id (FK), role_id (FK), additional_tags (JSON), notes
- **Relaciones:** Pertenece a FestivalRegistration, pertenece a RegistrationFormSection, pertenece a Role

---

### Role
- **Tabla:** `roles`
- **Clase:** `Role`
- **Campos clave:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relaciones:** Pertenece a Role (padre), pertenece a RoleGroup, tiene muchos UserRoles, tiene muchos FestivalRoles, tiene muchos RoleGroupMemberships, tiene muchos RoleDependencies, tiene muchos RoleConflicts

#### FestivalRole
- **Tabla:** `festival_roles`
- **Clase:** `FestivalRole`
- **Campos clave:** festival_id (FK), role_id (FK), is_active, custom_permissions, max_assignees
- **Relaciones:** Pertenece a Festival, pertenece a Role

#### RoleDependency
- **Tabla:** `role_dependencies`
- **Clase:** `RoleDependency`
- **Campos clave:** role_id (FK), depends_on_role_id (FK), dependency_type, festival_id (FK), notes
- **Relaciones:** Pertenece a Role (dependiente), pertenece a Role (requisito), pertenece a Festival

#### RoleConflict
- **Tabla:** `role_conflicts`
- **Clase:** `RoleConflict`
- **Campos clave:** role_id (FK), conflicts_with_role_id (FK), conflict_type, festival_id (FK), notes
- **Relaciones:** Pertenece a Role, pertenece a Role (en conflicto), pertenece a Festival

---

### RoleDelegation
- **Tabla:** `role_delegations`
- **Clase:** `RoleDelegation`
- **Campos clave:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relaciones:** Pertenece a User (delegador), pertenece a User (delegado), pertenece a Role, pertenece a Festival, pertenece a User (revocador)

---

### RoleGroup
- **Tabla:** `role_groups`
- **Clase:** `RoleGroup`
- **Campos clave:** name, display_name, description, sort_order, is_active
- **Relaciones:** Tiene muchos RoleGroupMemberships, tiene muchos Roles

#### RoleGroupMembership
- **Tabla:** `role_group_memberships`
- **Clase:** `RoleGroupMembership`
- **Campos clave:** group_id (FK), role_id (FK), level, is_leader, is_active
- **Relaciones:** Pertenece a RoleGroup, pertenece a Role

---

### RoleTransition
- **Tabla:** `role_transitions`
- **Clase:** `RoleTransition`
- **Campos clave:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relaciones:** Pertenece a User, pertenece a Role (origen), pertenece a Role (destino), pertenece a Festival (origen), pertenece a Festival (destino), pertenece a User (responsable del cambio)

---

### UserAlias
- **Tabla:** `user_aliases`
- **Clase:** `UserAlias`
- **Campos clave:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relaciones:** Pertenece a User
- **Notas:** Admite nombres visibles por contexto (global, festival, shortfilm, chat, public_profile, credits) con control de visibilidad

---

### UserKey
- **Tabla:** `user_keys`
- **Clase:** `UserKey`
- **Campos clave:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relaciones:** Pertenece a User
- **Notas:** Almacena la clave pública X25519 para E2EE; una clave activa por usuario

---

### UserRole
- **Tabla:** `user_roles`
- **Clase:** `UserRole`
- **Campos clave:** user_id (FK), role_id (FK), festival_id (FK), status, visibility, is_primary, is_hidden, assigned_by (FK), approved_by (FK), approved_at, start_date, expires_at, invitation_note, notes
- **Relaciones:** Pertenece a User, pertenece a Role, pertenece a Festival, pertenece a User (asignador), pertenece a User (aprobador)

#### UserParticipantTag
- **Tabla:** `user_participant_tags`
- **Clase:** `UserParticipantTag`
- **Campos clave:** user_id (FK), tag_id (FK), festival_id (FK), is_primary, is_hidden, assigned_by (FK), notes
- **Relaciones:** Pertenece a User, pertenece a ParticipantTag, pertenece a Festival, pertenece a User (asignador)

---

### UserSession
- **Tabla:** `user_sessions`
- **Clase:** `UserSession`
- **Campos clave:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relaciones:** Pertenece a User

---

### ValidationRule
- **Tabla:** `validation_rules`
- **Clase:** `ValidationRule`
- **Campos clave:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relaciones:** M2M con ValidationRuleGroup mediante `validation_rule_group_rules`

#### ValidationRuleGroup
- **Tabla:** `validation_rule_groups`
- **Clase:** `ValidationRuleGroup`
- **Campos clave:** name, description, scope, scope_id, is_active
- **Relaciones:** M2M con ValidationRule mediante `validation_rule_group_rules`

#### ValidationRuleGroupRules (association)
- **Tabla:** `validation_rule_group_rules`
- **Clase:** None (SQLAlchemy Table)
- **Campos clave:** group_id (FK, PK), rule_id (FK, PK)
- **Relaciones:** Puente M2M entre ValidationRuleGroup y ValidationRule

---

## Diagrama de relaciones entre entidades (simplificado)

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

## Sesiones de base de datos

Las sesiones de base de datos se gestionan mediante `get_db()` en `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Esto se utiliza como dependencia de FastAPI para el acceso a la base de datos desde los endpoints.

## Notas de migración de SQLite a MariaDB

Los cambios de esquema se gestionan con Alembic (`backend/alembic/versions/`, 18 versiones;
`alembic upgrade head`). En producción solo Alembic, nunca `create_all`.

Al migrar de SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` se corresponde con MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` se corresponde con MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` se almacena como texto; MariaDB utiliza `DATETIME` nativo
- Los scripts de migración en `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` gestionan las conversiones de tipos automáticamente