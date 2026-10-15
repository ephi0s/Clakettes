# Datenbankdokumentation

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Überblick

Clakettes nutzt ein Zwei-Datenbank-Setup:
- **Entwicklung**: SQLite (`clakettes.db`) — Standard, keine Konfiguration nötig
- **Produktion**: MariaDB — konfiguriert via `DATABASE_URL` in `backend/.env`

Migrationswerkzeuge zum Synchronisieren zwischen Umgebungen sind verfügbar:
- `python export_sqlite_to_mariadb.py` — Von Entwicklung nach Produktion
- `python import_mariadb_to_sqlite.py` — Von Produktion nach Entwicklung

## Modellübersicht (62 Konstrukte: 60 Entitäten + 2 Assoziationstabellen)

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

## Basismodell

Alle Modelle erben von `BaseModel`, definiert in `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Felder:
- `id`: Primärschlüssel, autoinkrementelle Ganzzahl
- `created_at`: Zeitstempel der Erstellung
- `updated_at`: Zeitstempel jeder Änderung

## Modelle

### Festival
- **Tabelle:** `festivals`
- **Klasse:** `Festival`
- **Schlüsselfelder:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Beziehungen:** Tiene muchos ShortFilms, tiene muchos Users (M2M mediante `user_festival`), tiene muchos FestivalRoles, tiene muchos FestivalParticipantTags, tiene muchos UserRoles, tiene muchos UserParticipantTags, tiene muchos RegistrationForms, tiene muchos FestivalRegistrations, tiene muchos Events, tiene muchos Awards

---

### User
- **Tabelle:** `users`
- **Klasse:** `User`
- **Schlüsselfelder:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active,
  is_public, is_public_email, is_public_bio, is_public_location (`False` por defecto), latitude, longitude,
  dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Beziehungen:** Tiene muchos ShortFilms, tiene muchos Festivals (M2M mediante `user_festival`), tiene muchos UserRoles, tiene muchos UserParticipantTags, tiene muchos UserAliases, tiene muchos FestivalRegistrations, tiene muchos Sessions, tiene muchos Awards, tiene muchos Events (creados), tiene muchos EventAttendees, tiene muchos EventReservations

---

### ShortFilm
- **Tabelle:** `shortfilms`
- **Klasse:** `ShortFilm`
- **Schlüsselfelder:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Beziehungen:** Pertenece a Festival, pertenece a User, tiene muchos Awards

---

### Message
- **Tabelle:** `messages`
- **Klasse:** `Message`
- **Schlüsselfelder:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Beziehungen:** Pertenece a User (remitente), pertenece a User (destinatario), pertenece a Channel

---

### User-Festival Association
- **Tabelle:** `user_festival`
- **Klasse:** None (SQLAlchemy Table)
- **Schlüsselfelder:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Beziehungen:** Puente M2M entre User y Festival; PK compuesta en (user_id, festival_id)

---

### Award
- **Tabelle:** `awards`
- **Klasse:** `Award`
- **Schlüsselfelder:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Beziehungen:** Pertenece a Festival, pertenece a Event, pertenece a ShortFilm, pertenece a User (destinatario), pertenece a User (verificador), pertenece a User (creador)

---

### Badge
- **Tabelle:** `badges`
- **Klasse:** `Badge`
- **Schlüsselfelder:** name, description, image_url (SVG bevorzugt), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Beziehungen:** Gehört zu Festival, hat viele BadgeAssignments
- **Hinweise:** Funktion in aktiver Entwicklung und standardmäßig deaktiviert (`badges.enabled`); nur das Admin-Team aktiviert sie. Festival-Abzeichen vergeben die Festivalleitung oder Admins.

#### BadgeAssignment
- **Tabelle:** `badge_assignments`
- **Klasse:** `BadgeAssignment`
- **Schlüsselfelder:** badge_id (FK), target_user_id (FK), target_festival_id (FK), granted_by (FK), grant_festival_id, reason
- **Beziehungen:** Gehört zu Badge, gehört zu User (Empfänger), gehört zu Festival (Empfänger)

---

### Channel
- **Tabelle:** `channels`
- **Klasse:** `Channel`
- **Schlüsselfelder:** name, description, channel_type, max_members, created_by (FK), is_active
- **Beziehungen:** Pertenece a User (creador), tiene muchos ChannelMembers, tiene muchos Messages

#### ChannelMember
- **Tabelle:** `channel_members`
- **Klasse:** `ChannelMember`
- **Schlüsselfelder:** channel_id (FK), user_id (FK), role, joined_at, is_active
- **Beziehungen:** Pertenece a Channel, pertenece a User
- **Hinweise:** Role limitado a admin, moderator, member

---

### Committee
- **Tabelle:** `committees`
- **Klasse:** `Committee`
- **Schlüsselfelder:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Beziehungen:** Pertenece a Festival, pertenece a Role, tiene muchos CommitteeMembers

#### CommitteeMember
- **Tabelle:** `committee_members`
- **Klasse:** `CommitteeMember`
- **Schlüsselfelder:** committee_id (FK), user_id (FK), role_in_committee, assigned_by (FK), is_active, joined_at, notes
- **Beziehungen:** Pertenece a Committee, pertenece a User, pertenece a User (asignador)

---

### Event
- **Tabelle:** `events`
- **Klasse:** `Event`
- **Schlüsselfelder:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Beziehungen:** Pertenece a Festival, pertenece a User (creador), tiene muchos EventTicketTypes, tiene muchos EventSeats, tiene muchos EventReservations, tiene muchos EventAttendees, tiene muchos Awards

#### EventTicketType
- **Tabelle:** `event_ticket_types`
- **Klasse:** `EventTicketType`
- **Schlüsselfelder:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Beziehungen:** Pertenece a Event, tiene muchos EventAttendees, tiene muchos EventSeats

#### EventSeat
- **Tabelle:** `event_seats`
- **Klasse:** `EventSeat`
- **Schlüsselfelder:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Beziehungen:** Pertenece a Event, pertenece a EventTicketType, tiene un EventAttendee

#### EventReservation
- **Tabelle:** `event_reservations`
- **Klasse:** `EventReservation`
- **Schlüsselfelder:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Beziehungen:** Pertenece a Event, pertenece a User (reservador), pertenece a User (creador), tiene muchos EventAttendees

#### EventAttendee
- **Tabelle:** `event_attendees`
- **Klasse:** `EventAttendee`
- **Schlüsselfelder:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Beziehungen:** Pertenece a Event, pertenece a EventReservation, pertenece a User, pertenece a EventSeat, pertenece a EventTicketType, pertenece a User (invitador)

---

### Notification
- **Tabelle:** `notifications`
- **Klasse:** `Notification`
- **Schlüsselfelder:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Beziehungen:** Pertenece a User (destinatario), pertenece a User (relacionado)

---

### ParticipantTag
- **Tabelle:** `participant_tags`
- **Klasse:** `ParticipantTag`
- **Schlüsselfelder:** name, display_name, description, category, is_global, is_active, sort_order
- **Beziehungen:** Tiene muchos UserParticipantTags, tiene muchos FestivalParticipantTags

#### FestivalParticipantTag
- **Tabelle:** `festival_participant_tags`
- **Klasse:** `FestivalParticipantTag`
- **Schlüsselfelder:** festival_id (FK), tag_id (FK), is_active, is_required, max_selections, can_submit_films, max_film_submissions, requires_approval, allowed_categories, is_exclusive
- **Beziehungen:** Pertenece a Festival, pertenece a ParticipantTag

---

### Post
- **Tabelle:** `posts`
- **Klasse:** `Post`
- **Schlüsselfelder:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type (youtube, vimeo, dailymotion, odysee, ivoox, podimo, generic), allow_replies, is_pinned, is_hidden
- **Beziehungen:** Gehört zu User (Autor), gehört zu User (Pinnwand), gehört zu Festival (Pinnwand), hat viele Antworten (Post), gehört zu Post (Elternbeitrag)
- **Hinweise:** Funktion in aktiver Entwicklung. Beiträge der obersten Ebene hängen an einer Benutzer- oder Festival-Pinnwand; Antworten erben den Bereich des Elternbeitrags und erfordern `allow_replies`. Moderation (anheften, verbergen, Antworten sperren) obliegt zentralen Admins, der Festivalleitung und Moderationsrollen des Festivals.

---

### Registration
- **Tabelle:** `registration_forms`
- **Klasse:** `RegistrationForm`
- **Schlüsselfelder:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Beziehungen:** Pertenece a Festival, tiene muchos RegistrationFormSections, tiene muchos RegistrationFormLinks, tiene muchos FestivalRegistrations

#### RegistrationFormSection
- **Tabelle:** `registration_form_sections`
- **Klasse:** `RegistrationFormSection`
- **Schlüsselfelder:** form_id (FK), title, description, sort_order, allow_multiple_roles, max_selections, is_required
- **Beziehungen:** Pertenece a RegistrationForm, tiene muchos RegistrationFormSectionRoles, tiene muchos RegistrationFormSectionTags, tiene muchos RegistrationSectionSelections

#### RegistrationFormSectionRole
- **Tabelle:** `registration_form_section_roles`
- **Klasse:** `RegistrationFormSectionRole`
- **Schlüsselfelder:** section_id (FK), role_id (FK), max_assignees, requires_approval, sort_order
- **Beziehungen:** Pertenece a RegistrationFormSection, pertenece a Role

#### RegistrationFormSectionTag
- **Tabelle:** `registration_form_section_tags`
- **Klasse:** `RegistrationFormSectionTag`
- **Schlüsselfelder:** section_id (FK), tag_id (FK), is_required, max_selections, sort_order
- **Beziehungen:** Pertenece a RegistrationFormSection, pertenece a ParticipantTag

#### RegistrationFormLink
- **Tabelle:** `registration_form_links`
- **Klasse:** `RegistrationFormLink`
- **Schlüsselfelder:** form_id (FK), token, is_unique, is_public, is_active, expires_at, max_uses, use_count, assigned_user_id (FK), notes
- **Beziehungen:** Pertenece a RegistrationForm, pertenece a User (asignado), tiene muchos FestivalRegistrations

#### FestivalRegistration
- **Tabelle:** `festival_registrations`
- **Klasse:** `FestivalRegistration`
- **Schlüsselfelder:** user_id (FK), festival_id (FK), form_id (FK), link_id (FK), status, assigned_by (FK), approved_by (FK), approved_at, notes, is_hidden
- **Beziehungen:** Pertenece a User, pertenece a Festival, pertenece a RegistrationForm, pertenece a RegistrationFormLink, pertenece a User (asignador), pertenece a User (aprobador), tiene muchos RegistrationSectionSelections

#### RegistrationSectionSelection
- **Tabelle:** `registration_section_selections`
- **Klasse:** `RegistrationSectionSelection`
- **Schlüsselfelder:** registration_id (FK), section_id (FK), role_id (FK), additional_tags (JSON), notes
- **Beziehungen:** Pertenece a FestivalRegistration, pertenece a RegistrationFormSection, pertenece a Role

---

### Role
- **Tabelle:** `roles`
- **Klasse:** `Role`
- **Schlüsselfelder:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Beziehungen:** Pertenece a Role (padre), pertenece a RoleGroup, tiene muchos UserRoles, tiene muchos FestivalRoles, tiene muchos RoleGroupMemberships, tiene muchos RoleDependencies, tiene muchos RoleConflicts

#### FestivalRole
- **Tabelle:** `festival_roles`
- **Klasse:** `FestivalRole`
- **Schlüsselfelder:** festival_id (FK), role_id (FK), is_active, custom_permissions, max_assignees
- **Beziehungen:** Pertenece a Festival, pertenece a Role

#### RoleDependency
- **Tabelle:** `role_dependencies`
- **Klasse:** `RoleDependency`
- **Schlüsselfelder:** role_id (FK), depends_on_role_id (FK), dependency_type, festival_id (FK), notes
- **Beziehungen:** Pertenece a Role (dependiente), pertenece a Role (requisito), pertenece a Festival

#### RoleConflict
- **Tabelle:** `role_conflicts`
- **Klasse:** `RoleConflict`
- **Schlüsselfelder:** role_id (FK), conflicts_with_role_id (FK), conflict_type, festival_id (FK), notes
- **Beziehungen:** Pertenece a Role, pertenece a Role (en conflicto), pertenece a Festival

---

### RoleDelegation
- **Tabelle:** `role_delegations`
- **Klasse:** `RoleDelegation`
- **Schlüsselfelder:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Beziehungen:** Pertenece a User (delegador), pertenece a User (delegado), pertenece a Role, pertenece a Festival, pertenece a User (revocador)

---

### RoleGroup
- **Tabelle:** `role_groups`
- **Klasse:** `RoleGroup`
- **Schlüsselfelder:** name, display_name, description, sort_order, is_active
- **Beziehungen:** Tiene muchos RoleGroupMemberships, tiene muchos Roles

#### RoleGroupMembership
- **Tabelle:** `role_group_memberships`
- **Klasse:** `RoleGroupMembership`
- **Schlüsselfelder:** group_id (FK), role_id (FK), level, is_leader, is_active
- **Beziehungen:** Pertenece a RoleGroup, pertenece a Role

---

### RoleTransition
- **Tabelle:** `role_transitions`
- **Klasse:** `RoleTransition`
- **Schlüsselfelder:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Beziehungen:** Pertenece a User, pertenece a Role (origen), pertenece a Role (destino), pertenece a Festival (origen), pertenece a Festival (destino), pertenece a User (responsable del cambio)

---

### UserAlias
- **Tabelle:** `user_aliases`
- **Klasse:** `UserAlias`
- **Schlüsselfelder:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Beziehungen:** Pertenece a User
- **Hinweise:** Unterstützt sichtbare Namen pro Kontext (global, festival, shortfilm, chat, public_profile, credits) mit Sichtbarkeitssteuerung

---

### UserKey
- **Tabelle:** `user_keys`
- **Klasse:** `UserKey`
- **Schlüsselfelder:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Beziehungen:** Pertenece a User
- **Hinweise:** Speichert den öffentlichen X25519-Schlüssel für E2EE; ein aktiver Schlüssel pro Nutzer

---

### UserRole
- **Tabelle:** `user_roles`
- **Klasse:** `UserRole`
- **Schlüsselfelder:** user_id (FK), role_id (FK), festival_id (FK), status, visibility, is_primary, is_hidden, assigned_by (FK), approved_by (FK), approved_at, start_date, expires_at, invitation_note, notes
- **Beziehungen:** Pertenece a User, pertenece a Role, pertenece a Festival, pertenece a User (asignador), pertenece a User (aprobador)

#### UserParticipantTag
- **Tabelle:** `user_participant_tags`
- **Klasse:** `UserParticipantTag`
- **Schlüsselfelder:** user_id (FK), tag_id (FK), festival_id (FK), is_primary, is_hidden, assigned_by (FK), notes
- **Beziehungen:** Pertenece a User, pertenece a ParticipantTag, pertenece a Festival, pertenece a User (asignador)

---

### UserSession
- **Tabelle:** `user_sessions`
- **Klasse:** `UserSession`
- **Schlüsselfelder:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Beziehungen:** Pertenece a User

---

### ValidationRule
- **Tabelle:** `validation_rules`
- **Klasse:** `ValidationRule`
- **Schlüsselfelder:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Beziehungen:** M2M con ValidationRuleGroup mediante `validation_rule_group_rules`

#### ValidationRuleGroup
- **Tabelle:** `validation_rule_groups`
- **Klasse:** `ValidationRuleGroup`
- **Schlüsselfelder:** name, description, scope, scope_id, is_active
- **Beziehungen:** M2M con ValidationRule mediante `validation_rule_group_rules`

#### ValidationRuleGroupRules (association)
- **Tabelle:** `validation_rule_group_rules`
- **Klasse:** None (SQLAlchemy Table)
- **Schlüsselfelder:** group_id (FK, PK), rule_id (FK, PK)
- **Beziehungen:** Puente M2M entre ValidationRuleGroup y ValidationRule

---

## Diagramm der Entitätsbeziehungen (vereinfacht)

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

## Datenbanksitzungen

Datenbanksitzungen werden via `get_db()` in `app/database.py` verwaltet:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Dies wird als FastAPI-Dependency für den DB-Zugriff aus den Endpunkten verwendet.

## Migrationshinweise von SQLite zu MariaDB

Schemaänderungen werden mit Alembic verwaltet (`backend/alembic/versions/`, 21 Versionen;
`alembic upgrade head`). In Produktion nur Alembic, niemals `create_all`.

Bei Migration von SQLite zu MariaDB:
- SQLite `INTEGER PRIMARY KEY` entspricht MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` entspricht MariaDB `TEXT` oder `VARCHAR`
- SQLite `DATETIME` wird als Text gespeichert; MariaDB nutzt natives `DATETIME`
- Die Migrationsskripte in `export_sqlite_to_mariadb.py` und `import_mariadb_to_sqlite.py` behandeln die Typkonvertierungen automatisch
