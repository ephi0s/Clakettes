# Datu-basearen dokumentazioa

## Ikuspegi orokorra

Clakettes-ek bi datu-baseko konfigurazioa erabiltzen du:
- **Garapena**: SQLite (`clakettes.db`) — lehenetsia, konfiguraziorik ez du behar
- **Ekoizpena**: MariaDB — `backend/.env`-ko `DATABASE_URL` bidez konfiguratzen da

Migrazio-tresnak eskuragarri daude inguruneen artean sinkronizatzeko:
- `python export_sqlite_to_mariadb.py` — Garapenetik ekoizpenera
- `python import_mariadb_to_sqlite.py` — Ekoizpenetik garapenera

## Ereduen laburpena (62 konstruktua: 60 entitate + 2 asoziazio-taula)

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

Guztira: 60 entitate-eredu + 2 asoziazio-taula = 62 SQLAlchemy konstruktua

## Oinarrizko eredua

Eredu guztiek `app/models/base.py`-n definitutako `BaseModel`-etik heredatzen dute:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Eremuak:
- `id`: Giltza nagusia, autoincremental osoa
- `created_at`: Sorkuntzan esleitutako denbora-marka
- `updated_at`: Aldaketa bakoitzean eguneratutako denbora-marka

## Ereduak

### Festival
- **Taula:** `festivals`
- **Klasea:** `Festival`
- **Funtsezko eremuak:** name, description, location, latitude, longitude, is_active, website, logo_url, allow_alias_display
- **Erlazioak:** ShortFilm asko ditu, User asko ditu (M2M `user_festival` bidez), FestivalRole asko ditu, FestivalParticipantTag asko ditu, UserRole asko ditu, UserParticipantTag asko ditu, RegistrationForm asko ditu, FestivalRegistration asko ditu, Event asko ditu, Award asko ditu

---

### User
- **Taula:** `users`
- **Klasea:** `User`
- **Funtsezko eremuak:** username, email, password_hash, full_name, role, bio, avatar_url, is_active,
  is_public, is_public_email, is_public_bio, is_public_location (`False` lehenetsiz), latitude, longitude,
  dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Erlazioak:** ShortFilm asko ditu, Festival asko ditu (M2M `user_festival` bidez), UserRole asko ditu, UserParticipantTag asko ditu, UserAlias asko ditu, FestivalRegistration asko ditu, Session asko ditu, Award asko ditu, Event asko ditu (sortuak), EventAttendee asko ditu, EventReservation asko ditu

---

### ShortFilm
- **Taula:** `shortfilms`
- **Klasea:** `ShortFilm`
- **Funtsezko eremuak:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Erlazioak:** Festival-ari dagokio, User-ari dagokio, Award asko ditu

---

### Message
- **Taula:** `messages`
- **Klasea:** `Message`
- **Funtsezko eremuak:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Erlazioak:** User-ari dagokio (igolea), User-ari dagokio (hartzailea), Channel-ari dagokio

---

### User-Festival Association
- **Taula:** `user_festival`
- **Klasea:** None (SQLAlchemy Table)
- **Funtsezko eremuak:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Erlazioak:** User eta Festival arteko M2M zubia; PK konposatua (user_id, festival_id)-n

---

### Award
- **Taula:** `awards`
- **Klasea:** `Award`
- **Funtsezko eremuak:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Erlazioak:** Festival-ari dagokio, Event-ari dagokio, ShortFilm-ari dagokio, User-ari dagokio (hartzailea), User-ari dagokio (egiaztatzailea), User-ari dagokio (sortzailea)

---

### Channel
- **Taula:** `channels`
- **Klasea:** `Channel`
- **Funtsezko eremuak:** name, description, channel_type, max_members, created_by (FK), is_active
- **Erlazioak:** User-ari dagokio (sortzailea), ChannelMember asko ditu, Message asko ditu

#### ChannelMember
- **Taula:** `channel_members`
- **Klasea:** `ChannelMember`
- **Funtsezko eremuak:** channel_id (FK), user_id (FK), role, joined_at, is_active
- **Erlazioak:** Channel-ari dagokio, User-ari dagokio
- **Oharrak:** Role admin, moderator, member-era mugatuta

---

### Committee
- **Taula:** `committees`
- **Klasea:** `Committee`
- **Funtsezko eremuak:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Erlazioak:** Festival-ari dagokio, Role-ari dagokio, CommitteeMember asko ditu

#### CommitteeMember
- **Taula:** `committee_members`
- **Klasea:** `CommitteeMember`
- **Funtsezko eremuak:** committee_id (FK), user_id (FK), role_in_committee, assigned_by (FK), is_active, joined_at, notes
- **Erlazioak:** Committee-ari dagokio, User-ari dagokio, User-ari dagokio (esleitzailea)

---

### Event
- **Taula:** `events`
- **Klasea:** `Event`
- **Funtsezko eremuak:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Erlazioak:** Festival-ari dagokio, User-ari dagokio (sortzailea), EventTicketType asko ditu, EventSeat asko ditu, EventReservation asko ditu, EventAttendee asko ditu, Award asko ditu

#### EventTicketType
- **Taula:** `event_ticket_types`
- **Klasea:** `EventTicketType`
- **Funtsezko eremuak:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Erlazioak:** Event-ari dagokio, EventAttendee asko ditu, EventSeat asko ditu

#### EventSeat
- **Taula:** `event_seats`
- **Klasea:** `EventSeat`
- **Funtsezko eremuak:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Erlazioak:** Event-ari dagokio, EventTicketType-ari dagokio, EventAttendee bat du

#### EventReservation
- **Taula:** `event_reservations`
- **Klasea:** `EventReservation`
- **Funtsezko eremuak:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Erlazioak:** Event-ari dagokio, User-ari dagokio (erreserbatzailea), User-ari dagokio (sortzailea), EventAttendee asko ditu

#### EventAttendee
- **Taula:** `event_attendees`
- **Klasea:** `EventAttendee`
- **Funtsezko eremuak:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Erlazioak:** Event-ari dagokio, EventReservation-ari dagokio, User-ari dagokio, EventSeat-ari dagokio, EventTicketType-ari dagokio, User-ari dagokio (gonbidatzailea)

---

### Notification
- **Taula:** `notifications`
- **Klasea:** `Notification`
- **Funtsezko eremuak:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Erlazioak:** User-ari dagokio (hartzailea), User-ari dagokio (erlazionatua)

---

### ParticipantTag
- **Taula:** `participant_tags`
- **Klasea:** `ParticipantTag`
- **Funtsezko eremuak:** name, display_name, description, category, is_global, is_active, sort_order
- **Erlazioak:** UserParticipantTag asko ditu, FestivalParticipantTag asko ditu

#### FestivalParticipantTag
- **Taula:** `festival_participant_tags`
- **Klasea:** `FestivalParticipantTag`
- **Funtsezko eremuak:** festival_id (FK), tag_id (FK), is_active, is_required, max_selections, can_submit_films, max_film_submissions, requires_approval, allowed_categories, is_exclusive
- **Erlazioak:** Festival-ari dagokio, ParticipantTag-ari dagokio

---

### Registration
- **Taula:** `registration_forms`
- **Klasea:** `RegistrationForm`
- **Funtsezko eremuak:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Erlazioak:** Festival-ari dagokio, RegistrationFormSection asko ditu, RegistrationFormLink asko ditu, FestivalRegistration asko ditu

#### RegistrationFormSection
- **Taula:** `registration_form_sections`
- **Klasea:** `RegistrationFormSection`
- **Funtsezko eremuak:** form_id (FK), title, description, sort_order, allow_multiple_roles, max_selections, is_required
- **Erlazioak:** RegistrationForm-ari dagokio, RegistrationFormSectionRole asko ditu, RegistrationFormSectionTag asko ditu, RegistrationSectionSelection asko ditu

#### RegistrationFormSectionRole
- **Taula:** `registration_form_section_roles`
- **Klasea:** `RegistrationFormSectionRole`
- **Funtsezko eremuak:** section_id (FK), role_id (FK), max_assignees, requires_approval, sort_order
- **Erlazioak:** RegistrationFormSection-ari dagokio, Role-ari dagokio

#### RegistrationFormSectionTag
- **Taula:** `registration_form_section_tags`
- **Klasea:** `RegistrationFormSectionTag`
- **Funtsezko eremuak:** section_id (FK), tag_id (FK), is_required, max_selections, sort_order
- **Erlazioak:** RegistrationFormSection-ari dagokio, ParticipantTag-ari dagokio

#### RegistrationFormLink
- **Taula:** `registration_form_links`
- **Klasea:** `RegistrationFormLink`
- **Funtsezko eremuak:** form_id (FK), token, is_unique, is_public, is_active, expires_at, max_uses, use_count, assigned_user_id (FK), notes
- **Erlazioak:** RegistrationForm-ari dagokio, User-ari dagokio (esleitua), FestivalRegistration asko ditu

#### FestivalRegistration
- **Taula:** `festival_registrations`
- **Klasea:** `FestivalRegistration`
- **Funtsezko eremuak:** user_id (FK), festival_id (FK), form_id (FK), link_id (FK), status, assigned_by (FK), approved_by (FK), approved_at, notes, is_hidden
- **Erlazioak:** User-ari dagokio, Festival-ari dagokio, RegistrationForm-ari dagokio, RegistrationFormLink-ari dagokio, User-ari dagokio (esleitzailea), User-ari dagokio (onartzailea), RegistrationSectionSelection asko ditu

#### RegistrationSectionSelection
- **Taula:** `registration_section_selections`
- **Klasea:** `RegistrationSectionSelection`
- **Funtsezko eremuak:** registration_id (FK), section_id (FK), role_id (FK), additional_tags (JSON), notes
- **Erlazioak:** FestivalRegistration-ari dagokio, RegistrationFormSection-ari dagokio, Role-ari dagokio

---

### Role
- **Taula:** `roles`
- **Klasea:** `Role`
- **Funtsezko eremuak:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Erlazioak:** Role-ari dagokio (aita), RoleGroup-ari dagokio, UserRole asko ditu, FestivalRole asko ditu, RoleGroupMembership asko ditu, RoleDependency asko ditu, RoleConflict asko ditu

#### FestivalRole
- **Taula:** `festival_roles`
- **Klasea:** `FestivalRole`
- **Funtsezko eremuak:** festival_id (FK), role_id (FK), is_active, custom_permissions, max_assignees
- **Erlazioak:** Festival-ari dagokio, Role-ari dagokio

#### RoleDependency
- **Taula:** `role_dependencies`
- **Klasea:** `RoleDependency`
- **Funtsezko eremuak:** role_id (FK), depends_on_role_id (FK), dependency_type, festival_id (FK), notes
- **Erlazioak:** Role-ari dagokio (menpekoa), Role-ari dagokio (baldintza), Festival-ari dagokio

#### RoleConflict
- **Taula:** `role_conflicts`
- **Klasea:** `RoleConflict`
- **Funtsezko eremuak:** role_id (FK), conflicts_with_role_id (FK), conflict_type, festival_id (FK), notes
- **Erlazioak:** Role-ari dagokio, Role-ari dagokio (gatazkan), Festival-ari dagokio

---

### RoleDelegation
- **Taula:** `role_delegations`
- **Klasea:** `RoleDelegation`
- **Funtsezko eremuak:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Erlazioak:** User-ari dagokio (delegatzailea), User-ari dagokio (delegatua), Role-ari dagokio, Festival-ari dagokio, User-ari dagokio (ezeztatzailea)

---

### RoleGroup
- **Taula:** `role_groups`
- **Klasea:** `RoleGroup`
- **Funtsezko eremuak:** name, display_name, description, sort_order, is_active
- **Erlazioak:** RoleGroupMembership asko ditu, Role asko ditu

#### RoleGroupMembership
- **Taula:** `role_group_memberships`
- **Klasea:** `RoleGroupMembership`
- **Funtsezko eremuak:** group_id (FK), role_id (FK), level, is_leader, is_active
- **Erlazioak:** RoleGroup-ari dagokio, Role-ari dagokio

---

### RoleTransition
- **Taula:** `role_transitions`
- **Klasea:** `RoleTransition`
- **Funtsezko eremuak:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Erlazioak:** User-ari dagokio, Role-ari dagokio (jatorria), Role-ari dagokio (helmuga), Festival-ari dagokio (jatorria), Festival-ari dagokio (helmuga), User-ari dagokio (aldaketaren arduraduna)

---

### UserAlias
- **Taula:** `user_aliases`
- **Klasea:** `UserAlias`
- **Funtsezko eremuak:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Erlazioak:** User-ari dagokio
- **Oharrak:** Testuinguruaren araberako izen ikusgaiak onartzen ditu (global, festival, shortfilm, chat, public_profile, credits) ikusgarritasun-kontrolarekin

---

### UserKey
- **Taula:** `user_keys`
- **Klasea:** `UserKey`
- **Funtsezko eremuak:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Erlazioak:** User-ari dagokio
- **Oharrak:** E2EE-rako X25519 giltza publikoa gordetzen du; giltza aktibo bat erabiltzaileko

---

### UserRole
- **Taula:** `user_roles`
- **Klasea:** `UserRole`
- **Funtsezko eremuak:** user_id (FK), role_id (FK), festival_id (FK), status, visibility, is_primary, is_hidden, assigned_by (FK), approved_by (FK), approved_at, start_date, expires_at, invitation_note, notes
- **Erlazioak:** User-ari dagokio, Role-ari dagokio, Festival-ari dagokio, User-ari dagokio (esleitzailea), User-ari dagokio (onartzailea)

#### UserParticipantTag
- **Taula:** `user_participant_tags`
- **Klasea:** `UserParticipantTag`
- **Funtsezko eremuak:** user_id (FK), tag_id (FK), festival_id (FK), is_primary, is_hidden, assigned_by (FK), notes
- **Erlazioak:** User-ari dagokio, ParticipantTag-ari dagokio, Festival-ari dagokio, User-ari dagokio (esleitzailea)

---

### UserSession
- **Taula:** `user_sessions`
- **Klasea:** `UserSession`
- **Funtsezko eremuak:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Erlazioak:** User-ari dagokio

---

### ValidationRule
- **Taula:** `validation_rules`
- **Klasea:** `ValidationRule`
- **Funtsezko eremuak:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Erlazioak:** M2M ValidationRuleGroup-ekin `validation_rule_group_rules` bidez

#### ValidationRuleGroup
- **Taula:** `validation_rule_groups`
- **Klasea:** `ValidationRuleGroup`
- **Funtsezko eremuak:** name, description, scope, scope_id, is_active
- **Erlazioak:** M2M ValidationRule-ekin `validation_rule_group_rules` bidez

#### ValidationRuleGroupRules (association)
- **Taula:** `validation_rule_group_rules`
- **Klasea:** None (SQLAlchemy Table)
- **Funtsezko eremuak:** group_id (FK, PK), rule_id (FK, PK)
- **Erlazioak:** ValidationRuleGroup eta ValidationRule arteko M2M zubia

---

## Entitateen arteko erlazio-diagrama (sinplifikatua)

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

## Datu-baseko saioak

Datu-baseko saioak `app/database.py`-ko `get_db()` bidez kudeatzen dira:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI mendekotasun gisa erabiltzen da endpoint-etatik datu-basera sartzeko.

## SQLite-tik MariaDB-ra migrazio-oharrak

Eskema-aldaketak Alembic-ekin kudeatzen dira (`backend/alembic/versions/`, 18 bertsio;
`alembic upgrade head`). Ekoizpenean Alembic soilik, inoiz ez `create_all`.

SQLite-tik MariaDB-ra migratzean:
- SQLite `INTEGER PRIMARY KEY` MariaDB `INT AUTO_INCREMENT`-ri dagokio
- SQLite `TEXT` MariaDB `TEXT` edo `VARCHAR`-ri dagokio
- SQLite `DATETIME` testu gisa gordetzen da; MariaDB-k `DATETIME` natiboa erabiltzen du
- `export_sqlite_to_mariadb.py` eta `import_mariadb_to_sqlite.py` migrazio-script-ek mota-bihurketak automatikoki kudeatzen dituzte
