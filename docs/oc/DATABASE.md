# Documentacion de la basa de donadas

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](DATABASE.md)

## Vista generala

Clakettes utiliza una configuracion amb doas basas de donadas:
- **Desvolopament**: SQLite (`clakettes.db`) — per defaut, demanda pas de configuracion
- **Produccion**: MariaDB — se configura mejans `DATABASE_URL` dins `backend/.env`

D'aisinas de migracion son disponiblas per sincronizar entre environaments:
- `python export_sqlite_to_mariadb.py` — Del desvolopament a la produccion
- `python import_mariadb_to_sqlite.py` — De la produccion al desvolopament

## Configurar MariaDB (produccion)

Per defaut Clakettes utilizes SQLite (`clakettes.db`), que demanda pas de configuracion. Per utilizar MariaDB:

1. Copiatz `backend/.env.example` a `backend/.env` e descomentatz la linha de `DATABASE_URL` per MariaDB:
   ```env
   DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db
   ```
2. Levatz lo contenidor MariaDB:
   ```bash
   # Desvolopament/local amb MariaDB
   docker compose --profile db up -d

   # Produccion completa (backend + frontend + MariaDB + nginx)
   docker compose --profile prod up -d
   ```
3. Executatz las migracions (solament Alembic, jamai `create_all` en produccion):
   ```bash
   cd backend
   alembic upgrade head
   ```
   O amb los scripts del projècte:
   ```bash
   start.* --migrate --mariadb
   ```
4. (Opcional) Copiatz las donadas de SQLite a MariaDB:
   ```bash
   cd backend && python tools/export_sqlite_to_mariadb.py
   ```

Variablas requeridas dins `backend/.env` quand s'utiliza MariaDB:

| Variabla | Exemple | Notas |
|---|---|---|
| `DATABASE_URL` | `mariadb+pymysql://user:pass@host:3306/dbname` | Cadena SQLAlchemy; dins Docker Compose l'ost es `db` |
| `SECRET_KEY` | `cambia-esta-clave-en-produccion` | Clau de signatura JWT |
| `CORS_ORIGINS` | `https://tu-dominio.com` | Domenis explicitas en produccion |
| `PUBLIC_BASE_URL` | `https://tu-dominio.com` | URL publica del nose (federacion) |

Dins Docker Compose lo servici `db` (MariaDB 11) s'activa amb `--profile db` o `--profile prod`; lo backend se connecta en utilizant `db` coma ost e lo pòrt `3306`.

Notas importantas:
- MariaDB en produccion exegís TLS: apondetz `?ssl_ca=...` a `DATABASE_URL`.
- Jamai utilizetz `create_all` en produccion; gestionatz l'esquèma solament amb Alembic (`alembic upgrade head`).
- Per tornar de MariaDB a SQLite: `python tools/import_mariadb_to_sqlite.py`.

## Resumit dels modèls

| Modèl | Taula | Tipe |
|---|---|---|
| `AppSetting` | `app_settings` | Entitat |
| `AuditLog` | `audit_logs` | Entitat |
| `Award` | `awards` | Entitat |
| `Badge` | `badges` | Entitat |
| `Calendar` | `calendars` | Entitat |
| `ChatMute` | `chat_mutes` | Entitat (federacion) |
| `ChatOutbox` | `chat_outbox` | Entitat (federacion) |
| `Channel` | `channels` | Entitat |
| `Committee` | `committees` | Entitat |
| `Event` | `events` | Entitat |
| `EventScreening` | `event_screenings` | Entitat |
| `Festival` | `festivals` | Entitat |
| `FestivalLocation` | `festival_locations` | Entitat |
| `FestivalRulebook` | `festival_rulebooks` | Entitat |
| `FormDefinition` | `form_definitions` | Entitat |
| `Group` | `groups` | Entitat |
| `IdentityRedirect` | `identity_redirects` | Entitat (federacion) |
| `JuryVote` | `jury_votes` | Entitat |
| `MessageReport` | `message_reports` | Entitat (federacion) |
| `MigrationAudit` | `migration_audits` | Entitat (federacion) |
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
| `TrustedNode` | `trusted_nodes` | Entitat (federacion) |
| `User` | `users` | Entitat |
| `UserAlias` | `user_aliases` | Entitat |
| `UserBlock` | `user_blocks` | Entitat |
| `UserFollow` | `user_follows` | Entitat |
| `UserFestival` | `user_festival` | Associacion (Taula) |
| `UserKey` | `user_keys` | Entitat |
| `UserRole` | `user_roles` | Entitat |
| `UserSession` | `user_sessions` | Entitat |
| `ValidationRule` | `validation_rules` | Entitat |
| `ValidationRuleGroup` | `validation_rule_groups` | Entitat |

Taulas d'associacion:
- `user_festival` — M2M entre `User` e `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` e `ValidationRule`

## Modèl de base

Totes los modèls eretan de `BaseModel` definit dins `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Camps:
- `id`: Clau primària, entièr autoincremental
- `created_at`: Marca temporala atribuida a la creacion
- `updated_at`: Marca temporala actualizada a cada modificacion

## Modèls principals

### Festival
- **Taula:** `festivals`
- **Classe:** `Festival`
- **Camps claus:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relacions:** A fòrça ShortFilms, Users (M2M mejans `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Taula:** `users`
- **Classe:** `User`
- **Camps claus:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relacions:** A fòrça ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creats), EventAttendees, EventReservations

### ShortFilm
- **Taula:** `shortfilms`
- **Classe:** `ShortFilm`
- **Camps claus:** title, description, duration, video_url, thumbnail_url, festival_id (FK, obligatòri), contest_type (official_section|contest), user_id (FK), is_public, tags
- **Relacions:** Apartén a Festival, apartén a User, a fòrça Awards, a fòrça ShortFilmLocations. Lo concors express (guerrilla) es `contest`; la seccion oficiala es `official_section`; `festival_id` es obligatòri amb FK `RESTRICT` e indexat, e `contest_type` tanben es indexat (migracion `b9c0d1e2f3a4`).

### Message
- **Taula:** `messages`
- **Classe:** `Message`
- **Camps claus:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relacions:** Apartén a User (emeteire), apartén a User (destinatari), apartén a Channel

### User-Festival Association
- **Taula:** `user_festival`
- **Classe:** None (SQLAlchemy Table)
- **Camps claus:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relacions:** Pont M2M entre User e Festival; PK compausada sus (user_id, festival_id)

### Award
- **Taula:** `awards`
- **Classe:** `Award`
- **Camps claus:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relacions:** Apartén a Festival, apartén a Event, apartén a ShortFilm, apartén a User (destinatari), apartén a User (verificaire), apartén a User (creator)

### Badge
- **Taula:** `badges`
- **Classe:** `Badge`
- **Camps claus:** name, description, image_url (SVG de preferéncia), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relacions:** Apartén a Festival, a fòrça BadgeAssignments
- **Notas:** Fonction en desvolopament actiu e desactivada per defaut (`badges.enabled`); solament l'equipa administrativa l'activa.

### Channel
- **Taula:** `channels`
- **Classe:** `Channel`
- **Camps claus:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relacions:** Apartén a User (creator), a fòrça ChannelMembers, a fòrça Messages

### Committee
- **Taula:** `committees`
- **Classe:** `Committee`
- **Camps claus:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relacions:** Apartén a Festival, apartén a Role, a fòrça CommitteeMembers

### Event
- **Taula:** `events`
- **Classe:** `Event`
- **Camps claus:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relacions:** Apartén a Festival, apartén a User (creator), a fòrça EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Taula:** `notifications`
- **Classe:** `Notification`
- **Camps claus:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relacions:** Apartén a User (destinatari), apartén a User (relacionat)

### ParticipantTag
- **Taula:** `participant_tags`
- **Classe:** `ParticipantTag`
- **Camps claus:** name, display_name, description, category, is_global, is_active, sort_order
- **Relacions:** A fòrça UserParticipantTags, a fòrça FestivalParticipantTags

### Post
- **Taula:** `posts`
- **Classe:** `Post`
- **Camps claus:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relacions:** Apartén a User (autor), apartén a User (mur), apartén a Festival (mur), a fòrça responsas (Post), apartén a Post (pair)
- **Notas:** Fonction en desvolopament actiu.

### Registration
- **Taula:** `registration_forms`
- **Classe:** `RegistrationForm`
- **Camps claus:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relacions:** Apartén a Festival, a fòrça RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Taula:** `roles`
- **Classe:** `Role`
- **Camps claus:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relacions:** Apartén a Role (pair), apartén a RoleGroup, a fòrça UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Taula:** `user_aliases`
- **Classe:** `UserAlias`
- **Camps claus:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relacions:** Apartén a User
- **Notas:** Permet de noms visibles per contexte (global, festival, shortfilm, chat, public_profile, credits) amb contròl de visibilitat

### UserKey
- **Taula:** `user_keys`
- **Classe:** `UserKey`
- **Camps claus:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relacions:** Apartén a User
- **Notas:** Serva la clau publica ECDH P-256 per E2EE; una clau activa per usagi

### UserSession
- **Taula:** `user_sessions`
- **Classe:** `UserSession`
- **Camps claus:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relacions:** Apartén a User

### ValidationRule
- **Taula:** `validation_rules`
- **Classe:** `ValidationRule`
- **Camps claus:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relacions:** M2M amb ValidationRuleGroup mejans `validation_rule_group_rules`

### Payment
- **Taula:** `payments`
- **Classe:** `Payment`
- **Camps claus:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relacions:** Apartén a Registration

### JuryVote
- **Taula:** `jury_votes`
- **Classe:** `JuryVote`
- **Camps claus:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relacions:** Apartén a Festival, apartén a ShortFilm, apartén a User (jurat)

### NodePolicy
- **Taula:** `node_policies`
- **Classe:** `NodePolicy`
- **Camps claus:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relacions:** Entitat de federacion

### ModerationReport
- **Taula:** `moderation_reports`
- **Classe:** `ModerationReport`
- **Camps claus:** reporter_node, target_node, target_user_ref, reason, status
- **Relacions:** Entitat de federacion

### IdentityRedirect
- **Taula:** `identity_redirects`
- **Classe:** `IdentityRedirect`
- **Camps claus:** old_ref (indèx unic), new_ref, target_domain, created_at
- **Relacions:** Entitat de federacion; resòlv la ref anciana aprèp una migracion d'identitat

### MigrationAudit
- **Taula:** `migration_audits`
- **Classe:** `MigrationAudit`
- **Camps claus:** entity_type, entity_id, action, source_domain, target_domain, details (tèxte JSON), created_at
- **Relacions:** Entitat de federacion; traça cada migracion de festival o d'usagi

### ChatOutbox
- **Taula:** `chat_outbox`
- **Classe:** `ChatOutbox`
- **Camps claus:** message_id (unic), node_origin, subject, payload (JSON), signature, status, attempts, last_error, created_at
- **Relacions:** Còda durabla del chat federat (`DurableQueueBackend`); l'unicitat de `message_id` dona la deduplicacion e `attempts`/`last_error` gestionan los reensajos

### MessageReport
- **Taula:** `message_reports`
- **Classe:** `MessageReport`
- **Camps claus:** reporter_id (FK), message_id (FK), reason, status
- **Relacions:** Apartén a User (senhalaire) e a Message

### ChatMute
- **Taula:** `chat_mutes`
- **Classe:** `ChatMute`
- **Camps claus:** user_id (FK), channel_id (FK), node_domain, until, reason
- **Relacions:** Apartén a User e a Channel; lo silenci pòt s'aplicar a un canal o a un nose federat

### TrustedNode
- **Taula:** `trusted_nodes`
- **Classe:** `TrustedNode`
- **Camps claus:** node_domain (unic, indèx), cert_fingerprint_sha256 (unic, indèx), allowed, revoked_at (DateTime, nullable), revocation_reason (Text, nullable), revoked_by (String(255), nullable)
- **Relacions:** Entitat de federacion; `revoked_at`, `revocation_reason` e `revoked_by` servan la revocacion del nose (migracion `c0d1e2f3a4b5`)

### Location
- **Taula:** `locations`
- **Classe:** `Location`
- **Camps claus:** name, description, latitude, longitude, address, is_active
- **Relacions:** Apartén a Festival (M2M), a fòrça LocationImages, LocationTags, LocationRelations

### EventScreening
- **Taula:** `event_screenings`
- **Classe:** `EventScreening`
- **Camps claus:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relacions:** Apartén a Event, apartén a ShortFilm

### FestivalRulebook
- **Taula:** `festival_rulebooks`
- **Classe:** `FestivalRulebook`
- **Camps claus:** festival_id (FK), title, content, file_url, is_active
- **Relacions:** Apartén a Festival

### FormDefinition
- **Taula:** `form_definitions`
- **Classe:** `FormDefinition`
- **Camps claus:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relacions:** Apartén a Festival, a fòrça FormPages, FormLinks, FormResponses

### Group
- **Taula:** `groups`
- **Classe:** `Group`
- **Camps claus:** name, display_name, description, sort_order, is_active
- **Relacions:** A fòrça RoleGroupMemberships, Roles

### AppSetting
- **Taula:** `app_settings`
- **Classe:** `AppSetting`
- **Camps claus:** key, value, description, is_public
- **Relacions:** Entitat de configuracion

### AuditLog
- **Taula:** `audit_logs`
- **Classe:** `AuditLog`
- **Camps claus:** actor_id (FK), action, target, ip, created_at
- **Relacions:** Apartén a User (actor), append-only

### UserBlock
- **Taula:** `user_blocks`
- **Classe:** `UserBlock`
- **Camps claus:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relacions:** Apartén a User (blocaire), apartén a User (blocat)

### UserFollow
- **Taula:** `user_follows`
- **Classe:** `UserFollow`
- **Camps claus:** `follower_id` (FK), `followed_id` (FK), created_at, updated_at

### RoleDelegation
- **Taula:** `role_delegations`
- **Classe:** `RoleDelegation`
- **Camps claus:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relacions:** Apartén a User (delegaire), apartén a User (delegat), apartén a Role, apartén a Festival, apartén a User (revocaire)

### RoleTransition
- **Taula:** `role_transitions`
- **Classe:** `RoleTransition`
- **Camps claus:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relacions:** Apartén a User, apartén a Role (origina), apartén a Role (destinacion), apartén a Festival (origina), apartén a Festival (destinacion), apartén a User (responsable del cambiament)

### EventTicketType
- **Taula:** `event_ticket_types`
- **Classe:** `EventTicketType`
- **Camps claus:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relacions:** Apartén a Event

### EventSeat
- **Taula:** `event_seats`
- **Classe:** `EventSeat`
- **Camps claus:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relacions:** Apartén a Event, apartén a EventTicketType
- **Restriccion:** `UNIQUE (event_id, section, row_label, number)` → `uq_event_seat_location` (migracion `a8b9c0d1e2f3`; remplaça lo `Meta.unique_together` inoperant de SQLAlchemy)

### EventReservation
- **Taula:** `event_reservations`
- **Classe:** `EventReservation`
- **Camps claus:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relacions:** Apartén a Event, apartén a User (reservaire), apartén a User (creator)

### EventAttendee
- **Taula:** `event_attendees`
- **Classe:** `EventAttendee`
- **Camps claus:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relacions:** Apartén a Event, apartén a EventReservation, apartén a User, apartén a EventSeat, apartén a EventTicketType, apartén a User (invitaire)

## Sessions de basa de donadas

Las sessions de basa de donadas son gestionadas mejans `get_db()` dins `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Aquò s'utiliza coma dependéncia de FastAPI per l'accès a la basa de donadas dempuèi los endpoints.

## Notas de migracion de SQLite a MariaDB

Los cambiaments d'esquèma son gestionats amb Alembic (`backend/alembic/versions/`; `alembic upgrade head`). I a 45 revisions e lo head es `d1e2f3a4b5c6`; las sèt darrièras (`a8b9c0d1e2f3`, `a9b0c1d2e3f4`, `b0c1d2e3f4a5`, `c1d2e3f4a5b6`, `b9c0d1e2f3a4`, `c0d1e2f3a4b5`, `d1e2f3a4b5c6`) apondon l'unicitat de sètge, las taulas de portabilitat, la còda durabla de chat, la moderacion, `contest_type` dins `shortfilms` amb indèx e `festival_id` obligatòri amb FK `RESTRICT`, e las metadadas de revocacion dins `trusted_nodes` (`revoked_at`, `revocation_reason`, `revoked_by`). En produccion solament Alembic, jamai `create_all`.
La revision `d1e2f3a4b5c6` apondon la taula `user_follows` (pareu unic `follower_id`, `followed_id`).

En migrant de SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` correspond a MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` correspond a MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` es servat coma tèxte; MariaDB utiliza `DATETIME` nadiu
- Los scripts de migracion dins `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` gestionan automaticament las conversions de tipes
