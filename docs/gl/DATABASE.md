# Documentación da base de datos

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](DATABASE.md) · [OC](../oc/DATABASE.md)

## Descrición xeral

Clakettes utiliza unha configuración con dúas bases de datos:
- **Desenvolvemento**: SQLite (`clakettes.db`) — por defecto, non require configuración
- **Produción**: MariaDB — configúrase mediante `DATABASE_URL` en `backend/.env`

Hai ferramentas de migración dispoñibles para sincronizar entre contornos:
- `python export_sqlite_to_mariadb.py` — De desenvolvemento a produción
- `python import_mariadb_to_sqlite.py` — De produción a desenvolvemento

## Configurar MariaDB (produción)

Por defecto Clakettes usa SQLite (`clakettes.db`), que non require configuración. Para usar MariaDB:

1. Copia `backend/.env.example` a `backend/.env` e descomenta a liña de `DATABASE_URL` para MariaDB:
   ```env
   DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db
   ```
2. Levanta o contedor MariaDB:
   ```bash
   # Desenvolvemento/local con MariaDB
   docker compose --profile db up -d

   # Produción completa (backend + frontend + MariaDB + nginx)
   docker compose --profile prod up -d
   ```
3. Executa as migracións (só Alembic, nunca `create_all` en produción):
   ```bash
   cd backend
   alembic upgrade head
   ```
   Ou cos scripts do proxecto:
   ```bash
   start.* --migrate --mariadb
   ```
4. (Opcional) Copia datos de SQLite a MariaDB:
   ```bash
   cd backend && python tools/export_sqlite_to_mariadb.py
   ```

Variables requiridas en `backend/.env` cando se usa MariaDB:

| Variable | Exemplo | Notas |
|---|---|---|
| `DATABASE_URL` | `mariadb+pymysql://user:pass@host:3306/dbname` | Cadea SQLAlchemy; en Docker Compose o host é `db` |
| `SECRET_KEY` | `cambia-esta-clave-en-produccion` | Chave de sinatura JWT |
| `CORS_ORIGINS` | `https://tu-dominio.com` | Dominios explícitos en produción |
| `PUBLIC_BASE_URL` | `https://tu-dominio.com` | URL pública do nodo (federación) |

En Docker Compose o servizo `db` (MariaDB 11) actívase con `--profile db` ou `--profile prod`; o backend conéctase usando `db` como host e o porto `3306`.

Notas importantes:
- MariaDB en produción esixe TLS: engade `?ssl_ca=...` a `DATABASE_URL`.
- Nunca uses `create_all` en produción; xestiona o esquema só con Alembic (`alembic upgrade head`).
- Para volver de MariaDB a SQLite: `python tools/import_mariadb_to_sqlite.py`.

## Resumo de modelos

| Modelo | Táboa | Tipo |
|---|---|---|
| `AppSetting` | `app_settings` | Entidade |
| `AuditLog` | `audit_logs` | Entidade |
| `Award` | `awards` | Entidade |
| `Badge` | `badges` | Entidade |
| `Calendar` | `calendars` | Entidade |
| `ChatMute` | `chat_mutes` | Entidade (federación) |
| `ChatOutbox` | `chat_outbox` | Entidade (federación) |
| `Channel` | `channels` | Entidade |
| `Committee` | `committees` | Entidade |
| `Event` | `events` | Entidade |
| `EventScreening` | `event_screenings` | Entidade |
| `Festival` | `festivals` | Entidade |
| `FestivalLocation` | `festival_locations` | Entidade |
| `FestivalRulebook` | `festival_rulebooks` | Entidade |
| `FormDefinition` | `form_definitions` | Entidade |
| `Group` | `groups` | Entidade |
| `IdentityRedirect` | `identity_redirects` | Entidade (federación) |
| `JuryVote` | `jury_votes` | Entidade |
| `MessageReport` | `message_reports` | Entidade (federación) |
| `MigrationAudit` | `migration_audits` | Entidade (federación) |
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
| `TrustedNode` | `trusted_nodes` | Entidade (federación) |
| `User` | `users` | Entidade |
| `UserAlias` | `user_aliases` | Entidade |
| `UserBlock` | `user_blocks` | Entidade |
| `UserFollow` | `user_follows` | Entidade |
| `UserFestival` | `user_festival` | Asociación (Táboa) |
| `UserKey` | `user_keys` | Entidade |
| `UserRole` | `user_roles` | Entidade |
| `UserSession` | `user_sessions` | Entidade |
| `ValidationRule` | `validation_rules` | Entidade |
| `ValidationRuleGroup` | `validation_rule_groups` | Entidade |

Táboas de asociación:
- `user_festival` — M2M entre `User` e `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` e `ValidationRule`

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
- `id`: Chave primaria, enteiro autoincremental
- `created_at`: Marca temporal asignada na creación
- `updated_at`: Marca temporal actualizada en cada modificación

## Modelos principais

### Festival
- **Táboa:** `festivals`
- **Clase:** `Festival`
- **Campos clave:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relacións:** Ten moitos ShortFilms, Users (M2M mediante `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Táboa:** `users`
- **Clase:** `User`
- **Campos clave:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relacións:** Ten moitos ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creados), EventAttendees, EventReservations

### ShortFilm
- **Táboa:** `shortfilms`
- **Clase:** `ShortFilm`
- **Campos clave:** title, description, duration, video_url, thumbnail_url, festival_id (FK, obrigatorio), contest_type (official_section|contest), user_id (FK), is_public, tags
- **Relacións:** Pertence a Festival, pertence a User, ten moitos Awards, ten moitas ShortFilmLocations. O concurso express (guerrilla) é `contest`; a sección oficial é `official_section`; `festival_id` é obrigatorio con FK `RESTRICT` e indexado, e `contest_type` tamén está indexado (migración `b9c0d1e2f3a4`).

### Message
- **Táboa:** `messages`
- **Clase:** `Message`
- **Campos clave:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relacións:** Pertence a User (remitente), pertence a User (destinatario), pertence a Channel

### User-Festival Association
- **Táboa:** `user_festival`
- **Clase:** None (SQLAlchemy Table)
- **Campos clave:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relacións:** Ponte M2M entre User e Festival; PK composta en (user_id, festival_id)

### Award
- **Táboa:** `awards`
- **Clase:** `Award`
- **Campos clave:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relacións:** Pertence a Festival, pertence a Event, pertence a ShortFilm, pertence a User (destinatario), pertence a User (verificador), pertence a User (creador)

### Badge
- **Táboa:** `badges`
- **Clase:** `Badge`
- **Campos clave:** name, description, image_url (SVG preferido), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relacións:** Pertence a Festival, ten moitas BadgeAssignments
- **Notas:** Función en desenvolvemento activo e desactivada por defecto (`badges.enabled`); só o equipo administrativo a activa.

### Channel
- **Táboa:** `channels`
- **Clase:** `Channel`
- **Campos clave:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relacións:** Pertence a User (creador), ten moitos ChannelMembers, ten moitos Messages

### Committee
- **Táboa:** `committees`
- **Clase:** `Committee`
- **Campos clave:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relacións:** Pertence a Festival, pertence a Role, ten moitos CommitteeMembers

### Event
- **Táboa:** `events`
- **Clase:** `Event`
- **Campos clave:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relacións:** Pertence a Festival, pertence a User (creador), ten moitos EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Táboa:** `notifications`
- **Clase:** `Notification`
- **Campos clave:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relacións:** Pertence a User (destinatario), pertence a User (relacionado)

### ParticipantTag
- **Táboa:** `participant_tags`
- **Clase:** `ParticipantTag`
- **Campos clave:** name, display_name, description, category, is_global, is_active, sort_order
- **Relacións:** Ten moitos UserParticipantTags, ten moitos FestivalParticipantTags

### Post
- **Táboa:** `posts`
- **Clase:** `Post`
- **Campos clave:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relacións:** Pertence a User (autor), pertence a User (muro), pertence a Festival (muro), ten moitas respostas (Post), pertence a Post (pai)
- **Notas:** Función en desenvolvemento activo.

### Registration
- **Táboa:** `registration_forms`
- **Clase:** `RegistrationForm`
- **Campos clave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relacións:** Pertence a Festival, ten moitos RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Táboa:** `roles`
- **Clase:** `Role`
- **Campos clave:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relacións:** Pertence a Role (pai), pertence a RoleGroup, ten moitos UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Táboa:** `user_aliases`
- **Clase:** `UserAlias`
- **Campos clave:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relacións:** Pertence a User
- **Notas:** Admite nomes visibles por contexto (global, festival, shortfilm, chat, public_profile, credits) con control de visibilidade

### UserKey
- **Táboa:** `user_keys`
- **Clase:** `UserKey`
- **Campos clave:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relacións:** Pertence a User
- **Notas:** Almacena a clave pública ECDH P-256 para E2EE; unha clave activa por usuario

### UserSession
- **Táboa:** `user_sessions`
- **Clase:** `UserSession`
- **Campos clave:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relacións:** Pertence a User

### ValidationRule
- **Táboa:** `validation_rules`
- **Clase:** `ValidationRule`
- **Campos clave:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relacións:** M2M con ValidationRuleGroup mediante `validation_rule_group_rules`

### Payment
- **Táboa:** `payments`
- **Clase:** `Payment`
- **Campos clave:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relacións:** Pertence a Registration

### JuryVote
- **Táboa:** `jury_votes`
- **Clase:** `JuryVote`
- **Campos clave:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relacións:** Pertence a Festival, pertence a ShortFilm, pertence a User (xurado)

### NodePolicy
- **Táboa:** `node_policies`
- **Clase:** `NodePolicy`
- **Campos clave:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relacións:** Entidade de federación

### ModerationReport
- **Táboa:** `moderation_reports`
- **Clase:** `ModerationReport`
- **Campos clave:** reporter_node, target_node, target_user_ref, reason, status
- **Relacións:** Entidade de federación

### IdentityRedirect
- **Táboa:** `identity_redirects`
- **Clase:** `IdentityRedirect`
- **Campos clave:** old_ref (índice único), new_ref, target_domain, created_at
- **Relacións:** Entidade de federación; resolve a ref antiga tras unha migración de identidade

### MigrationAudit
- **Táboa:** `migration_audits`
- **Clase:** `MigrationAudit`
- **Campos clave:** entity_type, entity_id, action, source_domain, target_domain, details (texto JSON), created_at
- **Relacións:** Entidade de federación; rastrexa cada migración de festival ou usuario

### ChatOutbox
- **Táboa:** `chat_outbox`
- **Clase:** `ChatOutbox`
- **Campos clave:** message_id (único), node_origin, subject, payload (JSON), signature, status, attempts, last_error, created_at
- **Relacións:** Cola durable do chat federado (`DurableQueueBackend`); a unicidade de `message_id` dá deduplicación e `attempts`/`last_error` xestionan reintentos

### MessageReport
- **Táboa:** `message_reports`
- **Clase:** `MessageReport`
- **Campos clave:** reporter_id (FK), message_id (FK), reason, status
- **Relacións:** Pertence a User (reportador) e a Message

### ChatMute
- **Táboa:** `chat_mutes`
- **Clase:** `ChatMute`
- **Campos clave:** user_id (FK), channel_id (FK), node_domain, until, reason
- **Relacións:** Pertence a User e a Channel; o silenciamento pode aplicarse a un canal ou a un nodo federado

### TrustedNode
- **Táboa:** `trusted_nodes`
- **Clase:** `TrustedNode`
- **Campos clave:** node_domain (único, índice), cert_fingerprint_sha256 (único, índice), allowed, revoked_at (DateTime, nullable), revocation_reason (Text, nullable), revoked_by (String(255), nullable)
- **Relacións:** Entidade de federación; `revoked_at`, `revocation_reason` e `revoked_by` rexistran a revogación do nodo (migración `c0d1e2f3a4b5`)

### Location
- **Táboa:** `locations`
- **Clase:** `Location`
- **Campos clave:** name, description, latitude, longitude, address, is_active
- **Relacións:** Pertence a Festival (M2M), ten moitos LocationImages, LocationTags, LocationRelations

### EventScreening
- **Táboa:** `event_screenings`
- **Clase:** `EventScreening`
- **Campos clave:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relacións:** Pertence a Event, pertence a ShortFilm

### FestivalRulebook
- **Táboa:** `festival_rulebooks`
- **Clase:** `FestivalRulebook`
- **Campos clave:** festival_id (FK), title, content, file_url, is_active
- **Relacións:** Pertence a Festival

### FormDefinition
- **Táboa:** `form_definitions`
- **Clase:** `FormDefinition`
- **Campos clave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relacións:** Pertence a Festival, ten moitos FormPages, FormLinks, FormResponses

### Group
- **Táboa:** `groups`
- **Clase:** `Group`
- **Campos clave:** name, display_name, description, sort_order, is_active
- **Relacións:** Ten moitos RoleGroupMemberships, Roles

### AppSetting
- **Táboa:** `app_settings`
- **Clase:** `AppSetting`
- **Campos clave:** key, value, description, is_public
- **Relacións:** Entidade de configuración

### AuditLog
- **Táboa:** `audit_logs`
- **Clase:** `AuditLog`
- **Campos clave:** actor_id (FK), action, target, ip, created_at
- **Relacións:** Pertence a User (actor), append-only

### UserBlock
- **Táboa:** `user_blocks`
- **Clase:** `UserBlock`
- **Campos clave:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relacións:** Pertence a User (bloqueador), pertence a User (bloqueado)

### UserFollow
- **Táboa:** `user_follows`
- **Clase:** `UserFollow`
- **Campos clave:** `follower_id` (FK), `followed_id` (FK), created_at, updated_at

### RoleDelegation
- **Táboa:** `role_delegations`
- **Clase:** `RoleDelegation`
- **Campos clave:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relacións:** Pertence a User (delegador), pertence a User (delegado), pertence a Role, pertence a Festival, pertence a User (revocador)

### RoleTransition
- **Táboa:** `role_transitions`
- **Clase:** `RoleTransition`
- **Campos clave:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relacións:** Pertence a User, pertence a Role (orixe), pertence a Role (destino), pertence a Festival (orixe), pertence a Festival (destino), pertence a User (responsable do cambio)

### EventTicketType
- **Táboa:** `event_ticket_types`
- **Clase:** `EventTicketType`
- **Campos clave:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relacións:** Pertence a Event

### EventSeat
- **Táboa:** `event_seats`
- **Clase:** `EventSeat`
- **Campos clave:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relacións:** Pertence a Event, pertence a EventTicketType
- **Restrición:** `UNIQUE (event_id, section, row_label, number)` → `uq_event_seat_location` (migración `a8b9c0d1e2f3`; substitúe ao `Meta.unique_together` inoperante de SQLAlchemy)

### EventReservation
- **Táboa:** `event_reservations`
- **Clase:** `EventReservation`
- **Campos clave:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relacións:** Pertence a Event, pertence a User (reservador), pertence a User (creador)

### EventAttendee
- **Táboa:** `event_attendees`
- **Clase:** `EventAttendee`
- **Campos clave:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relacións:** Pertence a Event, pertence a EventReservation, pertence a User, pertence a EventSeat, pertence a EventTicketType, pertence a User (invitador)

## Sesións de base de datos

As sesións de base de datos xestiónanse mediante `get_db()` en `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Isto utilízase como dependencia de FastAPI para o acceso á base de datos desde os endpoints.

## Notas de migración de SQLite a MariaDB

Os cambios de esquema xestiónanse con Alembic (`backend/alembic/versions/`; `alembic upgrade head`). Hai 45 revisións e o head é `d1e2f3a4b5c6`; as sete últimas (`a8b9c0d1e2f3`, `a9b0c1d2e3f4`, `b0c1d2e3f4a5`, `c1d2e3f4a5b6`, `b9c0d1e2f3a4`, `c0d1e2f3a4b5`, `d1e2f3a4b5c6`) engaden a unicidade de asento, as táboas de portabilidade, a cola durable de chat, a moderación, `contest_type` en `shortfilms` con índice e `festival_id` obrigatorio con FK `RESTRICT`, e metadatos de revogación en `trusted_nodes` (`revoked_at`, `revocation_reason`, `revoked_by`). En produción só Alembic, nunca `create_all`.
A revisión `d1e2f3a4b5c6` engade a táboa `user_follows` (par único `follower_id`, `followed_id`).

Ao migrar de SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` correspóndese con MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` correspóndese con MariaDB `TEXT` ou `VARCHAR`
- SQLite `DATETIME` almacénase como texto; MariaDB usa `DATETIME` nativo
- Os scripts de migración en `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` xestionan as conversións de tipos automaticamente
