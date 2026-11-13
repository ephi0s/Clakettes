# Documentación da base de datos

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [CA](DATABASE.md) · [OC](../oc/DATABASE.md)

## Descripción xeral

Clakettes usa unha configuración con dous bancos de datos:
- **Desenvolvemento**: SQLite (`clakettes.db`) — por defecto, non require configuración
- **Produción**: MariaDB — configurado mediante `DATABASE_URL` en `backend/.env`

Hai ferramentas de migración dispoñibles para sincronizar entre ambientes:
- `python export_sqlite_to_mariadb.py` — Desenvolvemento a produción
- `python import_mariadb_to_sqlite.py` — Produción a desenvolvemento

## Resumo de modelos

| Modelo | Táboa | Tipo |
|--------|-------|------|
| `AppSetting` | `app_settings` | Entidade |
| `AuditLog` | `audit_logs` | Entidade |
| `Award` | `awards` | Entidade |
| `Badge` | `badges` | Entidade |
| `Calendar` | `calendars` | Entidade |
| `Channel` | `channels` | Entidade |
| `Committee` | `committees` | Entidade |
| `Event` | `events` | Entidade |
| `EventScreening` | `event_screenings` | Entidade |
| `Festival` | `festivals` | Entidade |
| `FestivalLocation` | `festival_locations` | Entidade |
| `FestivalRulebook` | `festival_rulebooks` | Entidade |
| `FormDefinition` | `form_definitions` | Entidade |
| `Group` | `groups` | Entidade |
| `JuryVote` | `jury_votes` | Entidade |
| `Location` | `locations` | Entidade |
| `LocationImage` | `location_images` | Entidade |
| `LocationRelation` | `location_relations` | Entidade |
| `LocationTag` | `location_tags` | Entidade |
| `Message` | `messages` | Entidade |
| `ModerationReport` | `moderation_reports` | Entidade |
| `NodePolicy` | `node_policies` | Entidade |
| `Notification` | `notifications` | Entidade |
| `ParticipantTag` | `participant_tags` | Entidade |
| `Payment` | `payments` | Entidade |
| `Post` | `posts` | Entidade |
| `Registration` | `registration_forms` | Entidade |
| `Role` | `roles` | Entidade |
| `RoleDelegation` | `role_delegations` | Entidade |
| `RoleGroup` | `role_groups` | Entidade |
| `RoleTransition` | `role_transitions` | Entidade |
| `ShortFilm` | `shortfilms` | Entidade |
| `ShortFilmLocation` | `shortfilm_locations` | Entidade |
| `User` | `users` | Entidade |
| `UserAlias` | `user_aliases` | Entidade |
| `UserBlock` | `user_blocks` | Entidade |
| `UserFestival` | `user_festival` | Asociación (Táboa) |
| `UserKey` | `user_keys` | Entidade |
| `UserRole` | `user_roles` | Entidade |
| `UserSession` | `user_sessions` | Entidade |
| `ValidationRule` | `validation_rules` | Entidade |
| `ValidationRuleGroup` | `validation_rule_groups` | Entidade |

Táboas de asociación:
- `user_festival` — M2M entre `User` e `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` e `ValidationRule`

Total: 40 modelos de entidad + 2 táboas de asociación = 42 constructos SQLAlchemy.

## Modelo base

Todos os modelos herdan de `BaseModel` definido en `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Campos:
- `id`: Chave primaria, enteiro autoincrementable
- `created_at`: Marca temporal asignada na creación
- `updated_at`: Marca temporal actualizada en cada modificación

## Modelos principais

### Festival
- **Táboa:** `festivals`
- **Clase:** `Festival`
- **Campos chave:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relacións:** Ten moitos ShortFilms, Users (M2M mediante `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Táboa:** `users`
- **Clase:** `User`
- **Campos chave:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relacións:** Ten moitos ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creados), EventAttendees, EventReservations

### Curtametraxe
- **Táboa:** `shortfilms`
- **Clase:** `ShortFilm`
- **Campos chave:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relacións:** Pertence a Festival, pertence a User, ten moitos Awards, ten moitos ShortFilmLocations

### Mensaxe
- **Táboa:** `messages`
- **Clase:** `Message`
- **Campos chave:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relacións:** Pertence a User (remitente), pertence a User (destinatario), pertence a Channel

### Asociación User-Festival
- **Táboa:** `user_festival`
- **Clase:** None (Táboa SQLAlchemy)
- **Campos chave:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relacións:** Ponte M2M entre User e Festival; PK compuesta en (user_id, festival_id)

### Premio
- **Táboa:** `awards`
- **Clase:** `Award`
- **Campos chave:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relacións:** Pertence a Festival, pertence a Event, pertence a ShortFilm, pertence a User (destinatario), pertence a User (verificador), pertence a User (creador)

### Insignia
- **Táboa:** `badges`
- **Clase:** `Badge`
- **Campos chave:** name, description, image_url (SVG preferido), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relacións:** Pertence a Festival, ten moitos BadgeAssignments
- **Notas:** Función en desenvolvemento activo e desactivada por defecto (`badges.enabled`); solo o equipo administrativo a activa.

### Canle
- **Táboa:** `channels`
- **Clase:** `Channel`
- **Campos chave:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relacións:** Pertence a User (creador), ten moitos ChannelMembers, ten moitos Messages

### Comité
- **Táboa:** `committees`
- **Clase:** `Committee`
- **Campos chave:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relacións:** Pertence a Festival, pertence a Role, ten moitos CommitteeMembers

### Evento
- **Táboa:** `events`
- **Clase:** `Event`
- **Campos chave:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relacións:** Pertence a Festival, pertence a User (creador), ten moitos EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notificación
- **Táboa:** `notifications`
- **Clase:** `Notification`
- **Campos chave:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relacións:** Pertence a User (destinatario), pertence a User (relacionado)

### Etiqueta de participante
- **Táboa:** `participant_tags`
- **Clase:** `ParticipantTag`
- **Campos chave:** name, display_name, description, category, is_global, is_active, sort_order
- **Relacións:** Ten moitos UserParticipantTags, ten moitos FestivalParticipantTags

### Publicación
- **Táboa:** `posts`
- **Clase:** `Post`
- **Campos chave:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relacións:** Pertence a User (autor), pertence a User (muro), pertence a Festival (muro), ten moitos resposta (Post), pertence a Post (pai)
- **Notas:** Función en desenvolvemento activo.

### Rexistro
- **Táboa:** `registration_forms`
- **Clase:** `RegistrationForm`
- **Campos chave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relacións:** Pertence a Festival, ten moitos RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Rol
- **Táboa:** `roles`
- **Clase:** `Role`
- **Campos chave:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relacións:** Pertence a Role (pai), pertence a RoleGroup, ten moitos UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### Alias de usuario
- **Táboa:** `user_aliases`
- **Clase:** `UserAlias`
- **Campos chave:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relacións:** Pertence a User
- **Notas:** Admite nomes visibles por contexto (global, festival, shortfilm, chat, public_profile, credits) con control de visibilidade

### Chave de usuario
- **Táboa:** `user_keys`
- **Clase:** `UserKey`
- **Campos chave:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relacións:** Pertence a User
- **Notas:** Almacena a chave pública X25519 para E2EE; unha chave activa por usuario

### Sesión de usuario
- **Táboa:** `user_sessions`
- **Clase:** `UserSession`
- **Campos chave:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relacións:** Pertence a User

### Regra de validación
- **Táboa:** `validation_rules`
- **Clase:** `ValidationRule`
- **Campos chave:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relacións:** M2M con ValidationRuleGroup mediante `validation_rule_group_rules`

### Pago
- **Táboa:** `payments`
- **Clase:** `Payment`
- **Campos chave:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relacións:** Pertence a Registration

### Voto do xurado
- **Táboa:** `jury_votes`
- **Clase:** `JuryVote`
- **Campos chave:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relacións:** Pertence a Festival, pertence a ShortFilm, pertence a User (xurado)

### Política de nodo
- **Táboa:** `node_policies`
- **Clase:** `NodePolicy`
- **Campos chave:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relacións:** Entidade de federación

### Informe de moderación
- **Táboa:** `moderation_reports`
- **Clase:** `ModerationReport`
- **Campos chave:** reporter_node, target_node, target_user_ref, reason, status
- **Relacións:** Entidade de federación

### Ubicación
- **Táboa:** `locations`
- **Clase:** `Location`
- **Campos chave:** name, description, latitude, longitude, address, is_active
- **Relacións:** Pertence a Festival (M2M), ten moitos LocationImages, LocationTags, LocationRelations

### Proxección de evento
- **Táboa:** `event_screenings`
- **Clase:** `EventScreening`
- **Campos chave:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relacións:** Pertence a Evento, pertence a Curtametraxe

### Reglamento do festival
- **Táboa:** `festival_rulebooks`
- **Clase:** `FestivalRulebook`
- **Campos chave:** festival_id (FK), title, content, file_url, is_active
- **Relacións:** Pertence a Festival

### Definición de formulario
- **Táboa:** `form_definitions`
- **Clase:** `FormDefinition`
- **Campos chave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relacións:** Pertence a Festival, ten moitos FormPages, FormLinks, FormResponses

### Grupo
- **Táboa:** `groups`
- **Clase:** `Group`
- **Campos chave:** name, display_name, description, sort_order, is_active
- **Relacións:** Ten moitos RoleGroupMemberships, Roles

### Configuración da app
- **Táboa:** `app_settings`
- **Clase:** `AppSetting`
- **Campos chave:** key, value, description, is_public
- **Relacións:** Entidade de configuración

### Registro de auditoría
- **Táboa:** `audit_logs`
- **Clase:** `AuditLog`
- **Campos chave:** actor_id (FK), action, target, ip, created_at
- **Relacións:** Pertence a User (actor), append-only

### Bloqueo de usuario
- **Táboa:** `user_blocks`
- **Clase:** `UserBlock`
- **Campos chave:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relacións:** Pertence a User (bloqueador), pertence a User (bloqueado)

### Delegación de rol
- **Táboa:** `role_delegations`
- **Clase:** `RoleDelegation`
- **Campos chave:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relacións:** Pertence a User (delegador), pertence a User (delegado), pertence a Role, pertence a Festival, pertence a User (revocador)

### Transición de rol
- **Táboa:** `role_transitions`
- **Clase:** `RoleTransition`
- **Campos chave:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relacións:** Pertence a User, pertence a Role (orixe), pertence a Role (destino), pertence a Festival (orixe), pertence a Festival (destino), pertence a User (responsable do cambio)

### Tipo de entrada de evento
- **Táboa:** `event_ticket_types`
- **Clase:** `EventTicketType`
- **Campos chave:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relacións:** Pertence a Evento

### Asiento de evento
- **Táboa:** `event_seats`
- **Clase:** `EventSeat`
- **Campos chave:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relacións:** Pertence a Evento, pertence a EventTicketType

### Reserva de evento
- **Táboa:** `event_reservations`
- **Clase:** `EventReservation`
- **Campos chave:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relacións:** Pertence a Evento, pertence a User (reservador), pertence a User (creador)

### Asistente a evento
- **Táboa:** `event_attendees`
- **Clase:** `EventAttendee`
- **Campos chave:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relacións:** Pertence a Evento, pertence a EventReserva, pertence a User, pertence a EventSeat, pertence a EventTicketType, pertence a User (invitador)

## Sesións de base de datos

As sesións de base de datos xestionanse mediante `get_db()` en `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Iso úsase como dependencia de FastAPI para o acceso á base de datos desde os endpoints.

## Notas de migración de SQLite a MariaDB

Los cambios de esquema xéstananse con Alembic (`backend/alembic/versions/`, 36 versións; `alembic upgrade head`). En produción só Alembic, nunca `create_all`.

Al migrar de SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` corresponde a MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` corresponde a MariaDB `TEXT` ou `VARCHAR`
- SQLite `DATETIME` almacénase como texto; MariaDB usa `DATETIME` nativo
- Os scripts de migración en `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` xestionan as conversións de tipos automáticamente