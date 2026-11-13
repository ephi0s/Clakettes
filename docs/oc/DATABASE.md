# Documentacio de la base de datos

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [CA](DATABASE.md) · [OC](DATABASE.md)

## Descripciio general

Clakettes usa una configuracion amb dues bases de datos:
- **Desenvolupament**: SQLite (`clakettes.db`) — per defecte, no requeri configuracion
- **Productiu**: MariaDB — configurat mediante `DATABASE_URL` en `backend/.env`

Hi einines de migracio dispoñibles per sincronitzar entorns:
- `python export_sqlite_to_mariadb.py` — Desenvolupament a productiu
- `python import_mariadb_to_sqlite.py` — Productiu a desenvolupament

## Resum de models

| Model | Taula | Tipus |
|-------|-------|-------|
| `AppSetting` | `app_settings` | Entitat |
| `AuditLog` | `audit_logs` | Entitat |
| `Award` | `awards` | Entitat |
| `Badge` | `badges` | Entitat |
| `Calendar` | `calendars` | Entitat |
| `Channel` | `channels` | Entitat |
| `Committee` | `committees` | Entitat |
| `Event` | `events` | Entitat |
| `EventScreening` | `event_screenings` | Entitat |
| `Festival` | `festivals` | Entitat |
| `FestivalLocation` | `festival_locations` | Entitat |
| `FestivalRulebook` | `festival_rulebooks` | Entitat |
| `FormDefinition` | `form_definitions` | Entitat |
| `Group` | `groups` | Entitat |
| `JuryVote` | `jury_votes` | Entitat |
| `Location` | `locations` | Entitat |
| `LocationImage` | `location_images` | Entitat |
| `LocationRelation` | `location_relations` | Entitat |
| `LocationTag` | `location_tags` | Entitat |
| `Message` | `messages` | Entitat |
| `ModerationReport` | `moderation_reports` | Entitat |
| `NodePolicy` | `node_policies` | Entitat |
| `Notification` | `notifications` | Entitat |
| `ParticipantTag` | `participant_tags` | Entitat |
| `Payment` | `payments` | Entitat |
| `Post` | `posts` | Entitat |
| `Registration` | `registration_forms` | Entitat |
| `Role` | `roles` | Entitat |
| `RoleDelegation` | `role_delegations` | Entitat |
| `RoleGroup` | `role_groups` | Entitat |
| `RoleTransition` | `role_transitions` | Entitat |
| `ShortFilm` | `shortfilms` | Entitat |
| `ShortFilmLocation` | `shortfilm_locations` | Entitat |
| `User` | `users` | Entitat |
| `UserAlias` | `user_aliases` | Entitat |
| `UserBlock` | `user_blocks` | Entitat |
| `UserFestival` | `user_festival` | Associacio (Taula) |
| `UserKey` | `user_keys` | Entitat |
| `UserRole` | `user_roles` | Entitat |
| `UserSession` | `user_sessions` | Entitat |
| `ValidationRule` | `validation_rules` | Entitat |
| `ValidationRuleGroup` | `validation_rule_groups` | Entitat |

Taulles d'associacio:
- `user_festival` — M2M entre `User` i `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` i `ValidationRule`

Total: 40 models d'entitat + 2 taules d'associacio = 42 construccions SQLAlchemy.

## Model base

Totes les models heredan de `BaseModel` definit a `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Camps:
- `id`: Clau primaria, enter autoincremental
- `created_at`: Marca temporal assignada a la creacio
- `updated_at`: Marca temporal actualitzada a cada modificacio

## Models principals

### Festival
- **Taula:** `festivals`
- **Classe:** `Festival`
- **Camps clau:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relacions:** Ten molts ShortFilms, Usagis (M2M via `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### Usagi
- **Taula:** `users`
- **Classe:** `User`
- **Camps clau:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relacions:** Ten molts ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creats), EventAttendees, EventReservations

### Curtmetratge
- **Taula:** `shortfilms`
- **Classe:** `ShortFilm`
- **Camps clau:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relacions:** Pertany a Festival, pertany a Usagi, ten molts Awards, ten molts ShortFilmLocations

### Missatge
- **Taula:** `messages`
- **Classe:** `Message`
- **Camps clau:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relacions:** Pertany a Usagi (remitent), pertany a Usagi (destinatari), pertany a Channel

### Associacio Usagi-Festival
- **Taula:** `user_festival`
- **Classe:** None (Taula SQLAlchemy)
- **Camps clau:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relacions:** Pont M2M entre Usagi i Festival; PK composta en (user_id, festival_id)

### Premi
- **Taula:** `awards`
- **Classe:** `Award`
- **Camps clau:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relacions:** Pertany a Festival, pertany a Event, pertany a Curtmetratge, pertany a Usagi (destinatari), pertany a Usagi (verificador), pertany a Usagi (creador)

### Insignia
- **Taula:** `badges`
- **Classe:** `Badge`
- **Camps clau:** name, description, image_url (SVG preferit), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relacions:** Pertany a Festival, ten moltes BadgeAssignments
- **Notes:** Funcio en desenvolupament activ e desactivada per defecte (`badges.enabled`); solament l'equip administratiu la activa.

### Canal
- **Taula:** `channels`
- **Classe:** `Channel`
- **Camps clau:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relacions:** Pertany a Usagi (creador), ten moltes ChannelMembers, ten moltes Messages

### Comitat
- **Taula:** `committees`
- **Classe:** `Committee`
- **Camps clau:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relacions:** Pertany a Festival, pertany a Role, ten moltes CommitteeMembers

### Esdeveniment
- **Taula:** `events`
- **Classe:** `Event`
- **Camps clau:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relacions:** Pertany a Festival, pertany a Usagi (creador), ten moltes EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notificacio
- **Taula:** `notifications`
- **Classe:** `Notification`
- **Camps clau:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relacions:** Pertany a Usagi (destinatari), pertany a Usagi (relacionat)

### Etiqueta de participant
- **Taula:** `participant_tags`
- **Classe:** `ParticipantTag`
- **Camps clau:** name, display_name, description, category, is_global, is_active, sort_order
- **Relacions:** Ten moltes UserParticipantTags, ten moltes FestivalParticipantTags

### Publicacio
- **Taula:** `posts`
- **Classe:** `Post`
- **Camps clau:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relacions:** Pertany a Usagi (autor), pertany a Usagi (mur), pertany a Festival (mur), ten moltes respostes (Post), pertany a Post (pare)
- **Notes:** Funcio en desenvolupament activ.

### Rexistro
- **Taula:** `registration_forms`
- **Classe:** `RegistrationForm`
- **Camps clau:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relacions:** Pertany a Festival, ten moltes RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Rol
- **Taula:** `roles`
- **Classe:** `Role`
- **Camps clau:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relacions:** Pertany a Role (pare), pertany a RoleGroup, ten moltes UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### Alias d'usagi
- **Taula:** `user_aliases`
- **Classe:** `UserAlias`
- **Camps clau:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relacions:** Pertany a Usagi
- **Notes:** Admet noms visibles per contexto (global, festival, shortfilm, chat, public_profile, credits) amb control de visibilitat

### Clau d'usagi
- **Taula:** `user_keys`
- **Classe:** `UserKey`
- **Camps clau:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relacions:** Pertany a Usagi
- **Notes:** Emmagatzema la clau publica X25519 per E2EE; una clau activa per usagi

### Sessio d'usagi
- **Taula:** `user_sessions`
- **Classe:** `UserSession`
- **Camps clau:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relacions:** Pertany a Usagi

### Regla de validacio
- **Taula:** `validation_rules`
- **Classe:** `ValidationRule`
- **Camps clau:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relacions:** M2M amb ValidationRuleGroup via `validation_rule_group_rules`

### Pagament
- **Taula:** `payments`
- **Classe:** `Payment`
- **Camps clau:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relacions:** Pertany a Registration

### Vot del jurat
- **Taula:** `jury_votes`
- **Classe:** `JuryVote`
- **Camps clau:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relacions:** Pertany a Festival, pertany a Curtmetratge, pertany a Usagi (jurat)

### Politica de node
- **Taula:** `node_policies`
- **Classe:** `NodePolicy`
- **Camps clau:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relacions:** Entitat de federacio

### Informe de moderacio
- **Taula:** `moderation_reports`
- **Classe:** `ModerationReport`
- **Camps clau:** reporter_node, target_node, target_user_ref, reason, status
- **Relacions:** Entitat de federacio

### Ubicacio
- **Taula:** `locations`
- **Classe:** `Location`
- **Camps clau:** name, description, latitude, longitude, address, is_active
- **Relacions:** Pertany a Festival (M2M), ten moltes LocationImages, LocationTags, LocationRelations

### Projeccio d'esdeveniment
- **Taula:** `event_screenings`
- **Classe:** `EventScreening`
- **Camps clau:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relacions:** Pertany a Esdeveniment, pertany a Curtmetratge

### Regulador del festival
- **Taula:** `festival_rulebooks`
- **Classe:** `FestivalRulebook`
- **Camps clau:** festival_id (FK), title, content, file_url, is_active
- **Relacions:** Pertany a Festival

### Definicio de formulari
- **Taula:** `form_definitions`
- **Classe:** `FormDefinition`
- **Camps clau:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relacions:** Pertany a Festival, ten moltes FormPages, FormLinks, FormResponses

### Grup
- **Taula:** `groups`
- **Classe:** `Group`
- **Camps clau:** name, display_name, description, sort_order, is_active
- **Relacions:** Ten moltes RoleGroupMemberships, Rols

### Configuracio de l'aplicacio
- **Taula:** `app_settings`
- **Classe:** `AppSetting`
- **Camps clau:** key, value, description, is_public
- **Relacions:** Entitat de configuracio

### Registre d'auditoria
- **Taula:** `audit_logs`
- **Classe:** `AuditLog`
- **Camps clau:** actor_id (FK), action, target, ip, created_at
- **Relacions:** Pertany a Usagi (actor), append-only

### Bloc d'usagi
- **Taula:** `user_blocks`
- **Classe:** `UserBlock`
- **Camps clau:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relacions:** Pertany a Usagi (blocador), pertany a Usagi (blocat)

### Delegacio de rol
- **Taula:** `role_delegations`
- **Classe:** `RoleDelegation`
- **Camps clau:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relacions:** Pertany a Usagi (delegant), pertany a Usagi (delegat), pertany a Role, pertany a Festival, pertany a Usagi (revocant)

### Transicio de rol
- **Taula:** `role_transitions`
- **Classe:** `RoleTransition`
- **Camps clau:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relacions:** Pertany a Usagi, pertany a Role (origen), pertany a Role (destinacio), pertany a Festival (origen), pertany a Festival (destinacio), pertany a Usagi (responsable del canvi)

### Tipus d'entrada d'esdeveniment
- **Taula:** `event_ticket_types`
- **Classe:** `EventTicketType`
- **Camps clau:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relacions:** Pertany a Esdeveniment

### Seient d'esdeveniment
- **Taula:** `event_seats`
- **Classe:** `EventSeat`
- **Camps clau:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relacions:** Pertany a Esdeveniment, pertany a EventTicketType

### Reserva d'esdeveniment
- **Taula:** `event_reservations`
- **Classe:** `EventReservation`
- **Camps clau:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relacions:** Pertany a Esdeveniment, pertany a Usagi (reservador), pertany a Usagi (creador)

### Asistents d'esdeveniment
- **Taula:** `event_attendees`
- **Classe:** `EventAttendee`
- **Camps clau:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relacions:** Pertany a Esdeveniment, pertany a EventReserva, pertany a Usagi, pertany a EventSeat, pertany a EventTicketType, pertany a Usagi (invitant)

## Sessios de base de datos

Les sessios de base de datos es gestionen mediante `get_db()` en `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Aixo s'usat com a dependencia de FastAPI per l'accés a la base de datos des dels endpoints.

## Notes de migracio de SQLite a MariaDB

Los cambis d'esquema es gestionen amb Alembic (`backend/alembic/versions/`, 36 versions; `alembic upgrade head`). En productiu solament Alembic, mai `create_all`.

Al migrar de SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` correspon a MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` correspon a MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` es emmagatzema com a text; MariaDB usa `DATETIME` natiu
- Los scripts de migracio en `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` gestionan les conversions de tipus automaticament