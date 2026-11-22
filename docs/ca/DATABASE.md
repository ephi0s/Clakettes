# Documentació de la base de dades

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Descripció general

Clakettes utilitza una configuració amb dues bases de dades:
- **Desenvolupament**: SQLite (`clakettes.db`) — per defecte, no requereix configuració
- **Producció**: MariaDB — es configura mitjançant `DATABASE_URL` a `backend/.env`

Hi ha eines de migració disponibles per sincronitzar entre entorns:
- `python export_sqlite_to_mariadb.py` — De desenvolupament a producció
- `python import_mariadb_to_sqlite.py` — De producció a desenvolupament

## Configurar MariaDB (producció)

Per defecte Clakettes fa servir SQLite (`clakettes.db`), que no requereix configuració. Per utilitzar MariaDB:

1. Copia `backend/.env.example` a `backend/.env` i descomenta la línia de `DATABASE_URL` per a MariaDB:
   ```env
   DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db
   ```
2. Aixeca el contenidor MariaDB:
   ```bash
   # Desenvolupament/local amb MariaDB
   docker compose --profile db up -d

   # Producció completa (backend + frontend + MariaDB + nginx)
   docker compose --profile prod up -d
   ```
3. Executa les migracions (només Alembic, mai `create_all` en producció):
   ```bash
   cd backend
   alembic upgrade head
   ```
   O amb els scripts del projecte:
   ```bash
   start.* --migrate --mariadb
   ```
4. (Opcional) Copia dades de SQLite a MariaDB:
   ```bash
   cd backend && python tools/export_sqlite_to_mariadb.py
   ```

Variables requerides a `backend/.env` quan s'usa MariaDB:

| Variable | Exemple | Notes |
|---|---|---|
| `DATABASE_URL` | `mariadb+pymysql://user:pass@host:3306/dbname` | Cadena SQLAlchemy; a Docker Compose el host és `db` |
| `SECRET_KEY` | `cambia-esta-clave-en-produccion` | Clau de signatura JWT |
| `CORS_ORIGINS` | `https://tu-dominio.com` | Dominis explícits en producció |
| `PUBLIC_BASE_URL` | `https://tu-dominio.com` | URL pública del node (federació) |

A Docker Compose el servei `db` (MariaDB 11) s'activa amb `--profile db` o `--profile prod`; el backend es connecta fent servir `db` com a host i el port `3306`.

Notes importants:
- MariaDB en producció exigeix TLS: afegeix `?ssl_ca=...` a `DATABASE_URL`.
- No utilitzis mai `create_all` en producció; gestiona l'esquema només amb Alembic (`alembic upgrade head`).
- Per tornar de MariaDB a SQLite: `python tools/import_mariadb_to_sqlite.py`.

## Resum de models

| Model | Taula | Tipus |
|---|---|---|
| `AppSetting` | `app_settings` | Entitat |
| `AuditLog` | `audit_logs` | Entitat |
| `Award` | `awards` | Entitat |
| `Badge` | `badges` | Entitat |
| `Calendar` | `calendars` | Entitat |
| `ChatMute` | `chat_mutes` | Entitat (federació) |
| `ChatOutbox` | `chat_outbox` | Entitat (federació) |
| `Channel` | `channels` | Entitat |
| `Committee` | `committees` | Entitat |
| `Event` | `events` | Entitat |
| `EventScreening` | `event_screenings` | Entitat |
| `Festival` | `festivals` | Entitat |
| `FestivalLocation` | `festival_locations` | Entitat |
| `FestivalRulebook` | `festival_rulebooks` | Entitat |
| `FormDefinition` | `form_definitions` | Entitat |
| `Group` | `groups` | Entitat |
| `IdentityRedirect` | `identity_redirects` | Entitat (federació) |
| `JuryVote` | `jury_votes` | Entitat |
| `MessageReport` | `message_reports` | Entitat (federació) |
| `MigrationAudit` | `migration_audits` | Entitat (federació) |
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
| `UserFestival` | `user_festival` | Associació (Taula) |
| `UserKey` | `user_keys` | Entitat |
| `UserRole` | `user_roles` | Entitat |
| `UserSession` | `user_sessions` | Entitat |
| `ValidationRule` | `validation_rules` | Entitat |
| `ValidationRuleGroup` | `validation_rule_groups` | Entitat |

Taules d'associació:
- `user_festival` — M2M entre `User` i `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` i `ValidationRule`

## Model base

Tots els models hereten de `BaseModel` definit a `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Camps:
- `id`: Clau primària, enter autoincremental
- `created_at`: Marca temporal assignada en la creació
- `updated_at`: Marca temporal actualitzada en cada modificació

## Models principals

### Festival
- **Taula:** `festivals`
- **Classe:** `Festival`
- **Camps clau:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relacions:** Té molts ShortFilms, Users (M2M mitjançant `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Taula:** `users`
- **Classe:** `User`
- **Camps clau:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relacions:** Té molts ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creats), EventAttendees, EventReservations

### ShortFilm
- **Taula:** `shortfilms`
- **Classe:** `ShortFilm`
- **Camps clau:** title, description, duration, video_url, thumbnail_url, festival_id (FK, obligatorio), contest_type (official_section|contest), user_id (FK), is_public, tags
- **Relacions:** Pertany a Festival, pertany a User, té molts Awards, té moltes ShortFilmLocations El concurs express (guerrilla) és `contest`; la secció oficial és `official_section`.

### Message
- **Taula:** `messages`
- **Classe:** `Message`
- **Camps clau:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relacions:** Pertany a User (remitent), pertany a User (destinatari), pertany a Channel

### User-Festival Association
- **Taula:** `user_festival`
- **Classe:** None (SQLAlchemy Table)
- **Camps clau:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relacions:** Pont M2M entre User i Festival; PK composta en (user_id, festival_id)

### Award
- **Taula:** `awards`
- **Classe:** `Award`
- **Camps clau:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relacions:** Pertany a Festival, pertany a Event, pertany a ShortFilm, pertany a User (destinatari), pertany a User (verificador), pertany a User (creador)

### Badge
- **Taula:** `badges`
- **Classe:** `Badge`
- **Camps clau:** name, description, image_url (SVG preferit), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relacions:** Pertany a Festival, té moltes BadgeAssignments
- **Notes:** Funció en desenvolupament actiu i desactivada per defecte (`badges.enabled`); només l'equip administratiu l'activa.

### Channel
- **Taula:** `channels`
- **Classe:** `Channel`
- **Camps clau:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relacions:** Pertany a User (creador), té molts ChannelMembers, té molts Messages

### Committee
- **Taula:** `committees`
- **Classe:** `Committee`
- **Camps clau:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relacions:** Pertany a Festival, pertany a Role, té molts CommitteeMembers

### Event
- **Taula:** `events`
- **Classe:** `Event`
- **Camps clau:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relacions:** Pertany a Festival, pertany a User (creador), té molts EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Taula:** `notifications`
- **Classe:** `Notification`
- **Camps clau:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relacions:** Pertany a User (destinatari), pertany a User (relacionat)

### ParticipantTag
- **Taula:** `participant_tags`
- **Classe:** `ParticipantTag`
- **Camps clau:** name, display_name, description, category, is_global, is_active, sort_order
- **Relacions:** Té molts UserParticipantTags, té molts FestivalParticipantTags

### Post
- **Taula:** `posts`
- **Classe:** `Post`
- **Camps clau:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relacions:** Pertany a User (autor), pertany a User (mur), pertany a Festival (mur), té moltes respostes (Post), pertany a Post (pare)
- **Notes:** Funció en desenvolupament actiu.

### Registration
- **Taula:** `registration_forms`
- **Classe:** `RegistrationForm`
- **Camps clau:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relacions:** Pertany a Festival, té molts RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Taula:** `roles`
- **Classe:** `Role`
- **Camps clau:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relacions:** Pertany a Role (pare), pertany a RoleGroup, té molts UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Taula:** `user_aliases`
- **Classe:** `UserAlias`
- **Camps clau:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relacions:** Pertany a User
- **Notes:** Admet noms visibles per context (global, festival, shortfilm, chat, public_profile, credits) amb control de visibilitat

### UserKey
- **Taula:** `user_keys`
- **Classe:** `UserKey`
- **Camps clau:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relacions:** Pertany a User
- **Notes:** Desa la clau pública X25519 per a E2EE; una clau activa per usuari

### UserSession
- **Taula:** `user_sessions`
- **Classe:** `UserSession`
- **Camps clau:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relacions:** Pertany a User

### ValidationRule
- **Taula:** `validation_rules`
- **Classe:** `ValidationRule`
- **Camps clau:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relacions:** M2M amb ValidationRuleGroup mitjançant `validation_rule_group_rules`

### Payment
- **Taula:** `payments`
- **Classe:** `Payment`
- **Camps clau:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relacions:** Pertany a Registration

### JuryVote
- **Taula:** `jury_votes`
- **Classe:** `JuryVote`
- **Camps clau:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relacions:** Pertany a Festival, pertany a ShortFilm, pertany a User (jurat)

### NodePolicy
- **Taula:** `node_policies`
- **Classe:** `NodePolicy`
- **Camps clau:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relacions:** Entitat de federació

### ModerationReport
- **Taula:** `moderation_reports`
- **Classe:** `ModerationReport`
- **Camps clau:** reporter_node, target_node, target_user_ref, reason, status
- **Relacions:** Entitat de federació

### IdentityRedirect
- **Taula:** `identity_redirects`
- **Classe:** `IdentityRedirect`
- **Camps clau:** old_ref (índex únic), new_ref, target_domain, created_at
- **Relacions:** Entitat de federació; resol la ref antiga després d'una migració d'identitat

### MigrationAudit
- **Taula:** `migration_audits`
- **Classe:** `MigrationAudit`
- **Camps clau:** entity_type, entity_id, action, source_domain, target_domain, details (JSON), created_at
- **Relacions:** Entitat de federació; traça cada migració de festival o usuari

### ChatOutbox
- **Taula:** `chat_outbox`
- **Classe:** `ChatOutbox`
- **Camps clau:** message_id (únic), node_origin, subject, payload (JSON), signature, status, attempts, last_error, created_at
- **Relacions:** Cua durable del xat federat (`DurableQueueBackend`); la unicitat de `message_id` dona deduplicació i `attempts`/`last_error` gestionen reintents

### MessageReport
- **Taula:** `message_reports`
- **Classe:** `MessageReport`
- **Camps clau:** reporter_id (FK), message_id (FK), reason, status
- **Relacions:** Pertany a User (reportador) i a Message

### ChatMute
- **Taula:** `chat_mutes`
- **Classe:** `ChatMute`
- **Camps clau:** user_id (FK), channel_id (FK), node_domain, until, reason
- **Relacions:** Pertany a User i a Channel; el silenciament pot aplicar-se a un canal o a un node federat

### Location
- **Taula:** `locations`
- **Classe:** `Location`
- **Camps clau:** name, description, latitude, longitude, address, is_active
- **Relacions:** Pertany a Festival (M2M), té molts LocationImages, LocationTags, LocationRelations

### EventScreening
- **Taula:** `event_screenings`
- **Classe:** `EventScreening`
- **Camps clau:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relacions:** Pertany a Event, pertany a ShortFilm

### FestivalRulebook
- **Taula:** `festival_rulebooks`
- **Classe:** `FestivalRulebook`
- **Camps clau:** festival_id (FK), title, content, file_url, is_active
- **Relacions:** Pertany a Festival

### FormDefinition
- **Taula:** `form_definitions`
- **Classe:** `FormDefinition`
- **Camps clau:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relacions:** Pertany a Festival, té molts FormPages, FormLinks, FormResponses

### Group
- **Taula:** `groups`
- **Classe:** `Group`
- **Camps clau:** name, display_name, description, sort_order, is_active
- **Relacions:** Té molts RoleGroupMemberships, Roles

### AppSetting
- **Taula:** `app_settings`
- **Classe:** `AppSetting`
- **Camps clau:** key, value, description, is_public
- **Relacions:** Entitat de configuració

### AuditLog
- **Taula:** `audit_logs`
- **Classe:** `AuditLog`
- **Camps clau:** actor_id (FK), action, target, ip, created_at
- **Relacions:** Pertany a User (actor), append-only

### UserBlock
- **Taula:** `user_blocks`
- **Classe:** `UserBlock`
- **Camps clau:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relacions:** Pertany a User (bloquejador), pertany a User (bloquejat)

### RoleDelegation
- **Taula:** `role_delegations`
- **Classe:** `RoleDelegation`
- **Camps clau:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relacions:** Pertany a User (delegador), pertany a User (delegat), pertany a Role, pertany a Festival, pertany a User (revocador)

### RoleTransition
- **Taula:** `role_transitions`
- **Classe:** `RoleTransition`
- **Camps clau:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relacions:** Pertany a User, pertany a Role (origen), pertany a Role (destí), pertany a Festival (origen), pertany a Festival (destí), pertany a User (responsable del canvi)

### EventTicketType
- **Taula:** `event_ticket_types`
- **Classe:** `EventTicketType`
- **Camps clau:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relacions:** Pertany a Event

### EventSeat
- **Taula:** `event_seats`
- **Classe:** `EventSeat`
- **Camps clau:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relacions:** Pertany a Event, pertany a EventTicketType

### EventReservation
- **Taula:** `event_reservations`
- **Classe:** `EventReservation`
- **Camps clau:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relacions:** Pertany a Event, pertany a User (reservador), pertany a User (creador)

### EventAttendee
- **Taula:** `event_attendees`
- **Classe:** `EventAttendee`
- **Camps clau:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relacions:** Pertany a Event, pertany a EventReservation, pertany a User, pertany a EventSeat, pertany a EventTicketType, pertany a User (invitador)

## Sessions de base de dades

Les sessions de base de dades es gestionen mitjançant `get_db()` a `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Això s'utilitza com a dependència de FastAPI per a l'accés a la base de dades des dels endpoints.

## Notes de migració de SQLite a MariaDB

Els canvis d'esquema es gestionen amb Alembic (`backend/alembic/versions/`; `alembic upgrade head`). Hi ha 42 revisions i el head és `c1d2e3f4a5b6`; les tres últimes (`a9b0c1d2e3f4`, `b0c1d2e3f4a5`, `c1d2e3f4a5b6`) afegeixen les taules de portabilitat, la cua durable de xat i la moderació. En producció només Alembic, mai `create_all`.

En migrar de SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` es correspon amb MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` es correspon amb MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` es desa com a text; MariaDB utilitza `DATETIME` natiu
- Els scripts de migració a `export_sqlite_to_mariadb.py` i `import_mariadb_to_sqlite.py` gestionen les conversions de tipus automàticament
