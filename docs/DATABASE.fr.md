# Documentation de la base de données

[ES](DATABASE.md) · [EN](DATABASE.en.md) · [FR](DATABASE.fr.md) · [DE](DATABASE.de.md) · [IT](DATABASE.it.md) · [CA](DATABASE.ca.md) · [EU](DATABASE.eu.md) · [GL](DATABASE.gl.md) · [OC](DATABASE.oc.md)

## Description générale

Clakettes utilise une configuration avec deux bases de données :
- **Développement** : SQLite (`clakettes.db`) — par défaut, sans configuration requise
- **Production** : MariaDB — configurée via `DATABASE_URL` dans `backend/.env`

Des outils de migration sont disponibles pour synchroniser entre environnements :
- `python export_sqlite_to_mariadb.py` — De développement vers production
- `python import_mariadb_to_sqlite.py` — De production vers développement

## Résumé des modèles (62 construits : 60 entités + 2 tables d'association)

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

Total : 60 modèles d'entité + 2 tables d'association = 62 construits SQLAlchemy

## Modèle de base

Tous les modèles héritent de `BaseModel` défini dans `app/models/base.py` :

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Champs :
- `id` : Clé primaire, entier auto-incrémental
- `created_at` : Horodatage assigné à la création
- `updated_at` : Horodatage actualisé à chaque modification

## Modèles

### Festival
- **Tableau :** `festivals`
- **Classe :** `Festival`
- **Champs clés :** name, description, location, latitude, longitude, is_active, website, logo_url, allow_alias_display
- **Relations :** A beaucoup de ShortFilms, a beaucoup de Users (M2M via `user_festival`), a beaucoup de FestivalRoles, a beaucoup de FestivalParticipantTags, a beaucoup de UserRoles, a beaucoup de UserParticipantTags, a beaucoup de RegistrationForms, a beaucoup de FestivalRegistrations, a beaucoup de Events, a beaucoup de Awards

---

### User
- **Tableau :** `users`
- **Classe :** `User`
- **Champs clés :** username, email, password_hash, full_name, role, bio, avatar_url, is_active,
  is_public, is_public_email, is_public_bio, is_public_location (`False` par défaut), latitude, longitude,
  dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relations :** A beaucoup de ShortFilms, a beaucoup de Festivals (M2M via `user_festival`), a beaucoup de UserRoles, a beaucoup de UserParticipantTags, a beaucoup de UserAliases, a beaucoup de FestivalRegistrations, a beaucoup de Sessions, a beaucoup de Awards, a beaucoup de Events (créés), a beaucoup de EventAttendees, a beaucoup de EventReservations

---

### ShortFilm
- **Tableau :** `shortfilms`
- **Classe :** `ShortFilm`
- **Champs clés :** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relations :** Appartient à Festival, appartient à User, a beaucoup de Awards

---

### Message
- **Tableau :** `messages`
- **Classe :** `Message`
- **Champs clés :** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relations :** Appartient à User (expéditeur), appartient à User (destinataire), appartient à Channel

---

### User-Festival Association
- **Tableau :** `user_festival`
- **Classe :** None (SQLAlchemy Table)
- **Champs clés :** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relations :** Pont M2M entre User et Festival ; PK composée sur (user_id, festival_id)

---

### Award
- **Tableau :** `awards`
- **Classe :** `Award`
- **Champs clés :** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relations :** Appartient à Festival, appartient à Event, appartient à ShortFilm, appartient à User (destinataire), appartient à User (vérificateur), appartient à User (créateur)

---

### Channel
- **Tableau :** `channels`
- **Classe :** `Channel`
- **Champs clés :** name, description, channel_type, max_members, created_by (FK), is_active
- **Relations :** Appartient à User (créateur), a beaucoup de ChannelMembers, a beaucoup de Messages

#### ChannelMember
- **Tableau :** `channel_members`
- **Classe :** `ChannelMember`
- **Champs clés :** channel_id (FK), user_id (FK), role, joined_at, is_active
- **Relations :** Appartient à Channel, appartient à User
- **Notes :** Role limité à admin, moderator, member

---

### Committee
- **Tableau :** `committees`
- **Classe :** `Committee`
- **Champs clés :** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relations :** Appartient à Festival, appartient à Role, a beaucoup de CommitteeMembers

#### CommitteeMember
- **Tableau :** `committee_members`
- **Classe :** `CommitteeMember`
- **Champs clés :** committee_id (FK), user_id (FK), role_in_committee, assigned_by (FK), is_active, joined_at, notes
- **Relations :** Appartient à Committee, appartient à User, appartient à User (assignateur)

---

### Event
- **Tableau :** `events`
- **Classe :** `Event`
- **Champs clés :** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relations :** Appartient à Festival, appartient à User (créateur), a beaucoup de EventTicketTypes, a beaucoup de EventSeats, a beaucoup de EventReservations, a beaucoup de EventAttendees, a beaucoup de Awards

#### EventTicketType
- **Tableau :** `event_ticket_types`
- **Classe :** `EventTicketType`
- **Champs clés :** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relations :** Appartient à Event, a beaucoup de EventAttendees, a beaucoup de EventSeats

#### EventSeat
- **Tableau :** `event_seats`
- **Classe :** `EventSeat`
- **Champs clés :** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relations :** Appartient à Event, appartient à EventTicketType, a un EventAttendee

#### EventReservation
- **Tableau :** `event_reservations`
- **Classe :** `EventReservation`
- **Champs clés :** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relations :** Appartient à Event, appartient à User (réservant), appartient à User (créateur), a beaucoup de EventAttendees

#### EventAttendee
- **Tableau :** `event_attendees`
- **Classe :** `EventAttendee`
- **Champs clés :** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relations :** Appartient à Event, appartient à EventReservation, appartient à User, appartient à EventSeat, appartient à EventTicketType, appartient à User (inviteur)

---

### Notification
- **Tableau :** `notifications`
- **Classe :** `Notification`
- **Champs clés :** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relations :** Appartient à User (destinataire), appartient à User (lié)

---

### ParticipantTag
- **Tableau :** `participant_tags`
- **Classe :** `ParticipantTag`
- **Champs clés :** name, display_name, description, category, is_global, is_active, sort_order
- **Relations :** A beaucoup de UserParticipantTags, a beaucoup de FestivalParticipantTags

#### FestivalParticipantTag
- **Tableau :** `festival_participant_tags`
- **Classe :** `FestivalParticipantTag`
- **Champs clés :** festival_id (FK), tag_id (FK), is_active, is_required, max_selections, can_submit_films, max_film_submissions, requires_approval, allowed_categories, is_exclusive
- **Relations :** Appartient à Festival, appartient à ParticipantTag

---

### Registration
- **Tableau :** `registration_forms`
- **Classe :** `RegistrationForm`
- **Champs clés :** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relations :** Appartient à Festival, a beaucoup de RegistrationFormSections, a beaucoup de RegistrationFormLinks, a beaucoup de FestivalRegistrations

#### RegistrationFormSection
- **Tableau :** `registration_form_sections`
- **Classe :** `RegistrationFormSection`
- **Champs clés :** form_id (FK), title, description, sort_order, allow_multiple_roles, max_selections, is_required
- **Relations :** Appartient à RegistrationForm, a beaucoup de RegistrationFormSectionRoles, a beaucoup de RegistrationFormSectionTags, a beaucoup de RegistrationSectionSelections

#### RegistrationFormSectionRole
- **Tableau :** `registration_form_section_roles`
- **Classe :** `RegistrationFormSectionRole`
- **Champs clés :** section_id (FK), role_id (FK), max_assignees, requires_approval, sort_order
- **Relations :** Appartient à RegistrationFormSection, appartient à Role

#### RegistrationFormSectionTag
- **Tableau :** `registration_form_section_tags`
- **Classe :** `RegistrationFormSectionTag`
- **Champs clés :** section_id (FK), tag_id (FK), is_required, max_selections, sort_order
- **Relations :** Appartient à RegistrationFormSection, appartient à ParticipantTag

#### RegistrationFormLink
- **Tableau :** `registration_form_links`
- **Classe :** `RegistrationFormLink`
- **Champs clés :** form_id (FK), token, is_unique, is_public, is_active, expires_at, max_uses, use_count, assigned_user_id (FK), notes
- **Relations :** Appartient à RegistrationForm, appartient à User (assigné), a beaucoup de FestivalRegistrations

#### FestivalRegistration
- **Tableau :** `festival_registrations`
- **Classe :** `FestivalRegistration`
- **Champs clés :** user_id (FK), festival_id (FK), form_id (FK), link_id (FK), status, assigned_by (FK), approved_by (FK), approved_at, notes, is_hidden
- **Relations :** Appartient à User, appartient à Festival, appartient à RegistrationForm, appartient à RegistrationFormLink, appartient à User (assignateur), appartient à User (approbateur), a beaucoup de RegistrationSectionSelections

#### RegistrationSectionSelection
- **Tableau :** `registration_section_selections`
- **Classe :** `RegistrationSectionSelection`
- **Champs clés :** registration_id (FK), section_id (FK), role_id (FK), additional_tags (JSON), notes
- **Relations :** Appartient à FestivalRegistration, appartient à RegistrationFormSection, appartient à Role

---

### Role
- **Tableau :** `roles`
- **Classe :** `Role`
- **Champs clés :** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relations :** Appartient à Role (parent), appartient à RoleGroup, a beaucoup de UserRoles, a beaucoup de FestivalRoles, a beaucoup de RoleGroupMemberships, a beaucoup de RoleDependencies, a beaucoup de RoleConflicts

#### FestivalRole
- **Tableau :** `festival_roles`
- **Classe :** `FestivalRole`
- **Champs clés :** festival_id (FK), role_id (FK), is_active, custom_permissions, max_assignees
- **Relations :** Appartient à Festival, appartient à Role

#### RoleDependency
- **Tableau :** `role_dependencies`
- **Classe :** `RoleDependency`
- **Champs clés :** role_id (FK), depends_on_role_id (FK), dependency_type, festival_id (FK), notes
- **Relations :** Appartient à Role (dépendant), appartient à Role (requis), appartient à Festival

#### RoleConflict
- **Tableau :** `role_conflicts`
- **Classe :** `RoleConflict`
- **Champs clés :** role_id (FK), conflicts_with_role_id (FK), conflict_type, festival_id (FK), notes
- **Relations :** Appartient à Role, appartient à Role (en conflit), appartient à Festival

---

### RoleDelegation
- **Tableau :** `role_delegations`
- **Classe :** `RoleDelegation`
- **Champs clés :** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relations :** Appartient à User (délégateur), appartient à User (délégué), appartient à Role, appartient à Festival, appartient à User (révocateur)

---

### RoleGroup
- **Tableau :** `role_groups`
- **Classe :** `RoleGroup`
- **Champs clés :** name, display_name, description, sort_order, is_active
- **Relations :** A beaucoup de RoleGroupMemberships, a beaucoup de Roles

#### RoleGroupMembership
- **Tableau :** `role_group_memberships`
- **Classe :** `RoleGroupMembership`
- **Champs clés :** group_id (FK), role_id (FK), level, is_leader, is_active
- **Relations :** Appartient à RoleGroup, appartient à Role

---

### RoleTransition
- **Tableau :** `role_transitions`
- **Classe :** `RoleTransition`
- **Champs clés :** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relations :** Appartient à User, appartient à Role (origine), appartient à Role (destination), appartient à Festival (origine), appartient à Festival (destination), appartient à User (responsable du changement)

---

### UserAlias
- **Tableau :** `user_aliases`
- **Classe :** `UserAlias`
- **Champs clés :** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relations :** Appartient à User
- **Notes :** Admet des noms visibles par contexte (global, festival, shortfilm, chat, public_profile, credits) avec contrôle de visibilité

---

### UserKey
- **Tableau :** `user_keys`
- **Classe :** `UserKey`
- **Champs clés :** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relations :** Appartient à User
- **Notes :** Stocke la clé publique X25519 pour E2EE ; une clé active par utilisateur

---

### UserRole
- **Tableau :** `user_roles`
- **Classe :** `UserRole`
- **Champs clés :** user_id (FK), role_id (FK), festival_id (FK), status, visibility, is_primary, is_hidden, assigned_by (FK), approved_by (FK), approved_at, start_date, expires_at, invitation_note, notes
- **Relations :** Appartient à User, appartient à Role, appartient à Festival, appartient à User (assignateur), appartient à User (approbateur)

#### UserParticipantTag
- **Tableau :** `user_participant_tags`
- **Classe :** `UserParticipantTag`
- **Champs clés :** user_id (FK), tag_id (FK), festival_id (FK), is_primary, is_hidden, assigned_by (FK), notes
- **Relations :** Appartient à User, appartient à ParticipantTag, appartient à Festival, appartient à User (assignateur)

---

### UserSession
- **Tableau :** `user_sessions`
- **Classe :** `UserSession`
- **Champs clés :** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relations :** Appartient à User

---

### ValidationRule
- **Tableau :** `validation_rules`
- **Classe :** `ValidationRule`
- **Champs clés :** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relations :** M2M avec ValidationRuleGroup via `validation_rule_group_rules`

#### ValidationRuleGroup
- **Tableau :** `validation_rule_groups`
- **Classe :** `ValidationRuleGroup`
- **Champs clés :** name, description, scope, scope_id, is_active
- **Relations :** M2M avec ValidationRule via `validation_rule_group_rules`

#### ValidationRuleGroupRules (association)
- **Tableau :** `validation_rule_group_rules`
- **Classe :** None (SQLAlchemy Table)
- **Champs clés :** group_id (FK, PK), rule_id (FK, PK)
- **Relations :** Pont M2M entre ValidationRuleGroup et ValidationRule

---

## Diagramme de relations entre entités (simplifié)

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

## Sessions de base de données

Les sessions de base de données sont gérées via `get_db()` dans `app/database.py` :

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Ceci est utilisé comme dépendance FastAPI pour l'accès à la base de données depuis les endpoints.

## Notes de migration de SQLite vers MariaDB

Les changements de schéma sont gérés avec Alembic (`backend/alembic/versions/`, 18 versions ;
`alembic upgrade head`). En production uniquement Alembic, jamais `create_all`.

En migrant de SQLite vers MariaDB :
- SQLite `INTEGER PRIMARY KEY` correspond à MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` correspond à MariaDB `TEXT` ou `VARCHAR`
- SQLite `DATETIME` est stocké comme texte ; MariaDB utilise `DATETIME` natif
- Les scripts de migration dans `export_sqlite_to_mariadb.py` et `import_mariadb_to_sqlite.py` gèrent les conversions de types automatiquement
