# Documentación de la base de datos

[ES](DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Descripción general

Clakettes utiliza una configuración con dos bases de datos:
- **Desarrollo**: SQLite (`clakettes.db`) — por defecto, no requiere configuración
- **Producción**: MariaDB — se configura mediante `DATABASE_URL` en `backend/.env`

Hay herramientas de migración disponibles para sincronizar entre entornos:
- `python export_sqlite_to_mariadb.py` — De desarrollo a producción
- `python import_mariadb_to_sqlite.py` — De producción a desarrollo

## Resumen de modelos

| Modelo | Tabla | Tipo |
|---|---|---|
| `AppSetting` | `app_settings` | Entidad |
| `AuditLog` | `audit_logs` | Entidad |
| `Award` | `awards` | Entidad |
| `Badge` | `badges` | Entidad |
| `Calendar` | `calendars` | Entidad |
| `Channel` | `channels` | Entidad |
| `Committee` | `committees` | Entidad |
| `Event` | `events` | Entidad |
| `EventScreening` | `event_screenings` | Entidad |
| `Festival` | `festivals` | Entidad |
| `FestivalLocation` | `festival_locations` | Entidad |
| `FestivalRulebook` | `festival_rulebooks` | Entidad |
| `FormDefinition` | `form_definitions` | Entidad |
| `Group` | `groups` | Entidad |
| `JuryVote` | `jury_votes` | Entidad |
| `Location` | `locations` | Entidad |
| `LocationImage` | `location_images` | Entidad |
| `LocationRelation` | `location_relations` | Entidad |
| `LocationTag` | `location_tags` | Entidad |
| `Message` | `messages` | Entidad |
| `ModerationReport` | `moderation_reports` | Entidad |
| `NodePolicy` | `node_policies` | Entidad |
| `Notification` | `notifications` | Entidad |
| `ParticipantTag` | `participant_tags` | Entidad |
| `Payment` | `payments` | Entidad |
| `Post` | `posts` | Entidad |
| `Registration` | `registration_forms` | Entidad |
| `Role` | `roles` | Entidad |
| `RoleDelegation` | `role_delegations` | Entidad |
| `RoleGroup` | `role_groups` | Entidad |
| `RoleTransition` | `role_transitions` | Entidad |
| `ShortFilm` | `shortfilms` | Entidad |
| `ShortFilmLocation` | `shortfilm_locations` | Entidad |
| `User` | `users` | Entidad |
| `UserAlias` | `user_aliases` | Entidad |
| `UserBlock` | `user_blocks` | Entidad |
| `UserFestival` | `user_festival` | Asociación (Tabla) |
| `UserKey` | `user_keys` | Entidad |
| `UserRole` | `user_roles` | Entidad |
| `UserSession` | `user_sessions` | Entidad |
| `ValidationRule` | `validation_rules` | Entidad |
| `ValidationRuleGroup` | `validation_rule_groups` | Entidad |

Tablas de asociación:
- `user_festival` — M2M entre `User` y `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` y `ValidationRule`

Total: 40 modelos de entidad + 2 tablas de asociación = 42 constructos de SQLAlchemy.

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

## Modelos principales

### Festival
- **Tabla:** `festivals`
- **Clase:** `Festival`
- **Campos clave:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relaciones:** Tiene muchos ShortFilms, Users (M2M mediante `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Tabla:** `users`
- **Clase:** `User`
- **Campos clave:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relaciones:** Tiene muchos ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creados), EventAttendees, EventReservations

### ShortFilm
- **Tabla:** `shortfilms`
- **Clase:** `ShortFilm`
- **Campos clave:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relaciones:** Pertenece a Festival, pertenece a User, tiene muchos Awards, tiene muchas ShortFilmLocations

### Message
- **Tabla:** `messages`
- **Clase:** `Message`
- **Campos clave:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relaciones:** Pertenece a User (remitente), pertenece a User (destinatario), pertenece a Channel

### User-Festival Association
- **Tabla:** `user_festival`
- **Clase:** None (SQLAlchemy Table)
- **Campos clave:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relaciones:** Puente M2M entre User y Festival; PK compuesta en (user_id, festival_id)

### Award
- **Tabla:** `awards`
- **Clase:** `Award`
- **Campos clave:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relaciones:** Pertenece a Festival, pertenece a Event, pertenece a ShortFilm, pertenece a User (destinatario), pertenece a User (verificador), pertenece a User (creador)

### Badge
- **Tabla:** `badges`
- **Clase:** `Badge`
- **Campos clave:** name, description, image_url (SVG preferido), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relaciones:** Pertenece a Festival, tiene muchas BadgeAssignments
- **Notas:** Función en desarrollo activo y desactivada por defecto (`badges.enabled`); solo el equipo administrativo la activa.

### Channel
- **Tabla:** `channels`
- **Clase:** `Channel`
- **Campos clave:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relaciones:** Pertenece a User (creador), tiene muchos ChannelMembers, tiene muchos Messages

### Committee
- **Tabla:** `committees`
- **Clase:** `Committee`
- **Campos clave:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relaciones:** Pertenece a Festival, pertenece a Role, tiene muchos CommitteeMembers

### Event
- **Tabla:** `events`
- **Clase:** `Event`
- **Campos clave:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relaciones:** Pertenece a Festival, pertenece a User (creador), tiene muchos EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Tabla:** `notifications`
- **Clase:** `Notification`
- **Campos clave:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relaciones:** Pertenece a User (destinatario), pertenece a User (relacionado)

### ParticipantTag
- **Tabla:** `participant_tags`
- **Clase:** `ParticipantTag`
- **Campos clave:** name, display_name, description, category, is_global, is_active, sort_order
- **Relaciones:** Tiene muchos UserParticipantTags, tiene muchos FestivalParticipantTags

### Post
- **Tabla:** `posts`
- **Clase:** `Post`
- **Campos clave:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relaciones:** Pertenece a User (autor), pertenece a User (muro), pertenece a Festival (muro), tiene muchas respuestas (Post), pertenece a Post (padre)
- **Notas:** Función en desarrollo activo.

### Registration
- **Tabla:** `registration_forms`
- **Clase:** `RegistrationForm`
- **Campos clave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relaciones:** Pertenece a Festival, tiene muchos RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Tabla:** `roles`
- **Clase:** `Role`
- **Campos clave:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relaciones:** Pertenece a Role (padre), pertenece a RoleGroup, tiene muchos UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Tabla:** `user_aliases`
- **Clase:** `UserAlias`
- **Campos clave:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relaciones:** Pertenece a User
- **Notas:** Admite nombres visibles por contexto (global, festival, shortfilm, chat, public_profile, credits) con control de visibilidad

### UserKey
- **Tabla:** `user_keys`
- **Clase:** `UserKey`
- **Campos clave:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relaciones:** Pertenece a User
- **Notas:** Almacena la clave pública X25519 para E2EE; una clave activa por usuario

### UserSession
- **Tabla:** `user_sessions`
- **Clase:** `UserSession`
- **Campos clave:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relaciones:** Pertenece a User

### ValidationRule
- **Tabla:** `validation_rules`
- **Clase:** `ValidationRule`
- **Campos clave:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relaciones:** M2M con ValidationRuleGroup mediante `validation_rule_group_rules`

### Payment
- **Tabla:** `payments`
- **Clase:** `Payment`
- **Campos clave:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relaciones:** Pertenece a Registration

### JuryVote
- **Tabla:** `jury_votes`
- **Clase:** `JuryVote`
- **Campos clave:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relaciones:** Pertenece a Festival, pertenece a ShortFilm, pertenece a User (jurado)

### NodePolicy
- **Tabla:** `node_policies`
- **Clase:** `NodePolicy`
- **Campos clave:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relaciones:** Entidad de federación

### ModerationReport
- **Tabla:** `moderation_reports`
- **Clase:** `ModerationReport`
- **Campos clave:** reporter_node, target_node, target_user_ref, reason, status
- **Relaciones:** Entidad de federación

### Location
- **Tabla:** `locations`
- **Clase:** `Location`
- **Campos clave:** name, description, latitude, longitude, address, is_active
- **Relaciones:** Pertenece a Festival (M2M), tiene muchos LocationImages, LocationTags, LocationRelations

### EventScreening
- **Tabla:** `event_screenings`
- **Clase:** `EventScreening`
- **Campos clave:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relaciones:** Pertenece a Event, pertenece a ShortFilm

### FestivalRulebook
- **Tabla:** `festival_rulebooks`
- **Clase:** `FestivalRulebook`
- **Campos clave:** festival_id (FK), title, content, file_url, is_active
- **Relaciones:** Pertenece a Festival

### FormDefinition
- **Tabla:** `form_definitions`
- **Clase:** `FormDefinition`
- **Campos clave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relaciones:** Pertenece a Festival, tiene muchos FormPages, FormLinks, FormResponses

### Group
- **Tabla:** `groups`
- **Clase:** `Group`
- **Campos clave:** name, display_name, description, sort_order, is_active
- **Relaciones:** Tiene muchos RoleGroupMemberships, Roles

### AppSetting
- **Tabla:** `app_settings`
- **Clase:** `AppSetting`
- **Campos clave:** key, value, description, is_public
- **Relaciones:** Entidad de configuración

### AuditLog
- **Tabla:** `audit_logs`
- **Clase:** `AuditLog`
- **Campos clave:** actor_id (FK), action, target, ip, created_at
- **Relaciones:** Pertenece a User (actor), append-only

### UserBlock
- **Tabla:** `user_blocks`
- **Clase:** `UserBlock`
- **Campos clave:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relaciones:** Pertenece a User (bloqueador), pertenece a User (bloqueado)

### RoleDelegation
- **Tabla:** `role_delegations`
- **Clase:** `RoleDelegation`
- **Campos clave:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relaciones:** Pertenece a User (delegador), pertenece a User (delegado), pertenece a Role, pertenece a Festival, pertenece a User (revocador)

### RoleTransition
- **Tabla:** `role_transitions`
- **Clase:** `RoleTransition`
- **Campos clave:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relaciones:** Pertenece a User, pertenece a Role (origen), pertenece a Role (destino), pertenece a Festival (origen), pertenece a Festival (destino), pertenece a User (responsable del cambio)

### EventTicketType
- **Tabla:** `event_ticket_types`
- **Clase:** `EventTicketType`
- **Campos clave:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relaciones:** Pertenece a Event

### EventSeat
- **Tabla:** `event_seats`
- **Clase:** `EventSeat`
- **Campos clave:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relaciones:** Pertenece a Event, pertenece a EventTicketType

### EventReservation
- **Tabla:** `event_reservations`
- **Clase:** `EventReservation`
- **Campos clave:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relaciones:** Pertenece a Event, pertenece a User (reservador), pertenece a User (creador)

### EventAttendee
- **Tabla:** `event_attendees`
- **Clase:** `EventAttendee`
- **Campos clave:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relaciones:** Pertenece a Event, pertenece a EventReservation, pertenece a User, pertenece a EventSeat, pertenece a EventTicketType, pertenece a User (invitador)

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

Los cambios de esquema se gestionan con Alembic (`backend/alembic/versions/`, 36 versiones; `alembic upgrade head`). En producción solo Alembic, nunca `create_all`.

Al migrar de SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` se corresponde con MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` se corresponde con MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` se almacena como texto; MariaDB utiliza `DATETIME` nativo
- Los scripts de migración en `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` gestionan las conversiones de tipos automáticamente