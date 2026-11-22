# Documentazione del database

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Panoramica

Clakettes usa una configurazione a due database:
- **Sviluppo**: SQLite (`clakettes.db`) — predefinito, nessuna configurazione richiesta
- **Produzione**: MariaDB — configurata tramite `DATABASE_URL` in `backend/.env`

Sono disponibili strumenti di migrazione per sincronizzare gli ambienti:
- `python export_sqlite_to_mariadb.py` — Dallo sviluppo alla produzione
- `python import_mariadb_to_sqlite.py` — Dalla produzione allo sviluppo

## Configurare MariaDB (produzione)

Di default Clakettes usa SQLite (`clakettes.db`), che non richiede configurazione. Per usare MariaDB:

1. Copia `backend/.env.example` in `backend/.env` e decommenta la riga `DATABASE_URL` per MariaDB:
   ```env
   DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db
   ```
2. Avvia il container MariaDB:
   ```bash
   # Sviluppo/locale con MariaDB
   docker compose --profile db up -d

   # Produzione completa (backend + frontend + MariaDB + nginx)
   docker compose --profile prod up -d
   ```
3. Esegui le migrazioni (solo Alembic, mai `create_all` in produzione):
   ```bash
   cd backend
   alembic upgrade head
   ```
   Oppure con gli script del progetto:
   ```bash
   start.* --migrate --mariadb
   ```
4. (Opzionale) Copia i dati da SQLite a MariaDB:
   ```bash
   cd backend && python tools/export_sqlite_to_mariadb.py
   ```

Variabili richieste in `backend/.env` quando si usa MariaDB:

| Variabile | Esempio | Note |
|---|---|---|
| `DATABASE_URL` | `mariadb+pymysql://user:pass@host:3306/dbname` | Stringa di connessione SQLAlchemy; in Docker Compose l'host è `db` |
| `SECRET_KEY` | `change-this-in-production` | Chiave di firma JWT |
| `CORS_ORIGINS` | `https://il-tuo-dominio.com` | Domini espliciti in produzione |
| `PUBLIC_BASE_URL` | `https://il-tuo-dominio.com` | URL pubblico del nodo (federazione) |

In Docker Compose il servizio `db` (MariaDB 11) si attiva con `--profile db` o `--profile prod`; il backend si connette usando `db` come host e la porta `3306`.

Note importanti:
- MariaDB in produzione richiede TLS: aggiungi `?ssl_ca=...` a `DATABASE_URL`.
- Non usare mai `create_all` in produzione; gestisci lo schema solo con Alembic (`alembic upgrade head`).
- Per tornare da MariaDB a SQLite: `python tools/import_mariadb_to_sqlite.py`.

## Riepilogo dei modelli

| Modello | Tabella | Tipo |
|---|---|---|
| `AppSetting` | `app_settings` | Entità |
| `AuditLog` | `audit_logs` | Entità |
| `Award` | `awards` | Entità |
| `Badge` | `badges` | Entità |
| `Calendar` | `calendars` | Entità |
| `ChatMute` | `chat_mutes` | Entità (federazione) |
| `ChatOutbox` | `chat_outbox` | Entità (federazione) |
| `Channel` | `channels` | Entità |
| `Committee` | `committees` | Entità |
| `Event` | `events` | Entità |
| `EventScreening` | `event_screenings` | Entità |
| `Festival` | `festivals` | Entità |
| `FestivalLocation` | `festival_locations` | Entità |
| `FestivalRulebook` | `festival_rulebooks` | Entità |
| `FormDefinition` | `form_definitions` | Entità |
| `Group` | `groups` | Entità |
| `IdentityRedirect` | `identity_redirects` | Entità (federazione) |
| `JuryVote` | `jury_votes` | Entità |
| `MessageReport` | `message_reports` | Entità (federazione) |
| `MigrationAudit` | `migration_audits` | Entità (federazione) |
| `Location` | `locations` | Entità |
| `LocationImage` | `location_images` | Entità |
| `LocationRelation` | `location_relations` | Entità |
| `LocationTag` | `location_tags` | Entità |
| `Message` | `messages` | Entità |
| `ModerationReport` | `moderation_reports` | Entità |
| `NodePolicy` | `node_policies` | Entità |
| `Notification` | `notifications` | Entità |
| `ParticipantTag` | `participant_tags` | Entità |
| `Payment` | `payments` | Entità |
| `Post` | `posts` | Entità |
| `Registration` | `registration_forms` | Entità |
| `Role` | `roles` | Entità |
| `RoleDelegation` | `role_delegations` | Entità |
| `RoleGroup` | `role_groups` | Entità |
| `RoleTransition` | `role_transitions` | Entità |
| `ShortFilm` | `shortfilms` | Entità |
| `ShortFilmLocation` | `shortfilm_locations` | Entità |
| `TrustedNode` | `trusted_nodes` | Entità (federazione) |
| `User` | `users` | Entità |
| `UserAlias` | `user_aliases` | Entità |
| `UserBlock` | `user_blocks` | Entità |
| `UserFollow` | `user_follows` | Entità |
| `UserFestival` | `user_festival` | Associazione (Tabella) |
| `UserKey` | `user_keys` | Entità |
| `UserRole` | `user_roles` | Entità |
| `UserSession` | `user_sessions` | Entità |
| `ValidationRule` | `validation_rules` | Entità |
| `ValidationRuleGroup` | `validation_rule_groups` | Entità |

Tabelle di associazione:
- `user_festival` — M2M tra `User` e `Festival`
- `validation_rule_group_rules` — M2M tra `ValidationRuleGroup` e `ValidationRule`

## Modello base

Tutti i modelli ereditano da `BaseModel` definito in `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Campi:
- `id`: Chiave primaria, intero autoincrementale
- `created_at`: Timestamp assegnato alla creazione
- `updated_at`: Timestamp aggiornato a ogni modifica

## Modelli principali

### Festival
- **Tabella:** `festivals`
- **Classe:** `Festival`
- **Campi chiave:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relazioni:** Ha molti ShortFilms, Users (M2M tramite `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Tabella:** `users`
- **Classe:** `User`
- **Campi chiave:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relazioni:** Ha molti ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creati), EventAttendees, EventReservations

### ShortFilm
- **Tabella:** `shortfilms`
- **Classe:** `ShortFilm`
- **Campi chiave:** title, description, duration, video_url, thumbnail_url, festival_id (FK, obbligatorio), contest_type (official_section|contest), user_id (FK), is_public, tags
- **Relazioni:** Appartiene a Festival, appartiene a User, ha molti Awards, ha molte ShortFilmLocations. Il concorso express (guerrilla) è `contest`; la sezione ufficiale è `official_section`; `festival_id` è obbligatorio con FK `RESTRICT` e indicizzato, e anche `contest_type` è indicizzato (migrazione `b9c0d1e2f3a4`).

### Message
- **Tabella:** `messages`
- **Classe:** `Message`
- **Campi chiave:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relazioni:** Appartiene a User (mittente), appartiene a User (destinatario), appartiene a Channel

### Associazione User-Festival
- **Tabella:** `user_festival`
- **Classe:** None (SQLAlchemy Table)
- **Campi chiave:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relazioni:** Ponte M2M tra User e Festival; PK composta su (user_id, festival_id)

### Award
- **Tabella:** `awards`
- **Classe:** `Award`
- **Campi chiave:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relazioni:** Appartiene a Festival, appartiene a Event, appartiene a ShortFilm, appartiene a User (destinatario), appartiene a User (verificatore), appartiene a User (creatore)

### Badge
- **Tabella:** `badges`
- **Classe:** `Badge`
- **Campi chiave:** name, description, image_url (SVG preferito), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relazioni:** Appartiene a Festival, ha molte BadgeAssignments
- **Note:** Funzione in sviluppo attivo e disattivata di default (`badges.enabled`); solo il team amministrativo la attiva.

### Channel
- **Tabella:** `channels`
- **Classe:** `Channel`
- **Campi chiave:** name, description, channel_type, max_members, created_by (FK), is_active
- **Relazioni:** Appartiene a User (creatore), ha molti ChannelMembers, ha molti Messages

### Committee
- **Tabella:** `committees`
- **Classe:** `Committee`
- **Campi chiave:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relazioni:** Appartiene a Festival, appartiene a Role, ha molti CommitteeMembers

### Event
- **Tabella:** `events`
- **Classe:** `Event`
- **Campi chiave:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relazioni:** Appartiene a Festival, appartiene a User (creatore), ha molti EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Tabella:** `notifications`
- **Classe:** `Notification`
- **Campi chiave:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relazioni:** Appartiene a User (destinatario), appartiene a User (correlato)

### ParticipantTag
- **Tabella:** `participant_tags`
- **Classe:** `ParticipantTag`
- **Campi chiave:** name, display_name, description, category, is_global, is_active, sort_order
- **Relazioni:** Ha molti UserParticipantTags, ha molti FestivalParticipantTags

### Post
- **Tabella:** `posts`
- **Classe:** `Post`
- **Campi chiave:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relazioni:** Appartiene a User (autore), appartiene a User (muro), appartiene a Festival (muro), ha molte risposte (Post), appartiene a Post (padre)
- **Note:** Funzione in sviluppo attivo.

### Registration
- **Tabella:** `registration_forms`
- **Classe:** `RegistrationForm`
- **Campi chiave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relazioni:** Appartiene a Festival, ha molti RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Tabella:** `roles`
- **Classe:** `Role`
- **Campi chiave:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relazioni:** Appartiene a Role (padre), appartiene a RoleGroup, ha molti UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Tabella:** `user_aliases`
- **Classe:** `UserAlias`
- **Campi chiave:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relazioni:** Appartiene a User
- **Note:** Supporta nomi visibili per contesto (global, festival, shortfilm, chat, public_profile, credits) con controllo di visibilità

### UserKey
- **Tabella:** `user_keys`
- **Classe:** `UserKey`
- **Campi chiave:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relazioni:** Appartiene a User
- **Note:** Memorizza la chiave pubblica ECDH P-256 per E2EE; una chiave attiva per utente

### UserSession
- **Tabella:** `user_sessions`
- **Classe:** `UserSession`
- **Campi chiave:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relazioni:** Appartiene a User

### ValidationRule
- **Tabella:** `validation_rules`
- **Classe:** `ValidationRule`
- **Campi chiave:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relazioni:** M2M con ValidationRuleGroup tramite `validation_rule_group_rules`

### Payment
- **Tabella:** `payments`
- **Classe:** `Payment`
- **Campi chiave:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relazioni:** Appartiene a Registration

### JuryVote
- **Tabella:** `jury_votes`
- **Classe:** `JuryVote`
- **Campi chiave:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relazioni:** Appartiene a Festival, appartiene a ShortFilm, appartiene a User (giurato)

### NodePolicy
- **Tabella:** `node_policies`
- **Classe:** `NodePolicy`
- **Campi chiave:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relazioni:** Entità di federazione

### ModerationReport
- **Tabella:** `moderation_reports`
- **Classe:** `ModerationReport`
- **Campi chiave:** reporter_node, target_node, target_user_ref, reason, status
- **Relazioni:** Entità di federazione

### IdentityRedirect
- **Tabella:** `identity_redirects`
- **Classe:** `IdentityRedirect`
- **Campi chiave:** old_ref (indice unico), new_ref, target_domain, created_at
- **Relazioni:** Entità di federazione; risolve la vecchia ref dopo una migrazione di identità

### MigrationAudit
- **Tabella:** `migration_audits`
- **Classe:** `MigrationAudit`
- **Campi chiave:** entity_type, entity_id, action, source_domain, target_domain, details (testo JSON), created_at
- **Relazioni:** Entità di federazione; traccia ogni migrazione di festival o utente

### ChatOutbox
- **Tabella:** `chat_outbox`
- **Classe:** `ChatOutbox`
- **Campi chiave:** message_id (unico), node_origin, subject, payload (JSON), signature, status, attempts, last_error, created_at
- **Relazioni:** Coda durable della chat federata (`DurableQueueBackend`); l'unicità di `message_id` dà la deduplicazione e `attempts`/`last_error` gestiscono i tentativi

### MessageReport
- **Tabella:** `message_reports`
- **Classe:** `MessageReport`
- **Campi chiave:** reporter_id (FK), message_id (FK), reason, status
- **Relazioni:** Appartiene a User (segnalante) e a Message

### ChatMute
- **Tabella:** `chat_mutes`
- **Classe:** `ChatMute`
- **Campi chiave:** user_id (FK), channel_id (FK), node_domain, until, reason
- **Relazioni:** Appartiene a User e a Channel; il mute può applicarsi a un canale o a un nodo federato

### TrustedNode
- **Tabella:** `trusted_nodes`
- **Classe:** `TrustedNode`
- **Campi chiave:** node_domain (unico, indice), cert_fingerprint_sha256 (unico, indice), allowed, revoked_at (DateTime, nullable), revocation_reason (Text, nullable), revoked_by (String(255), nullable)
- **Relazioni:** Entità di federazione; `revoked_at`, `revocation_reason` e `revoked_by` registrano la revoca del nodo (migrazione `c0d1e2f3a4b5`)

### Location
- **Tabella:** `locations`
- **Classe:** `Location`
- **Campi chiave:** name, description, latitude, longitude, address, is_active
- **Relazioni:** Appartiene a Festival (M2M), ha molti LocationImages, LocationTags, LocationRelations

### EventScreening
- **Tabella:** `event_screenings`
- **Classe:** `EventScreening`
- **Campi chiave:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relazioni:** Appartiene a Event, appartiene a ShortFilm

### FestivalRulebook
- **Tabella:** `festival_rulebooks`
- **Classe:** `FestivalRulebook`
- **Campi chiave:** festival_id (FK), title, content, file_url, is_active
- **Relazioni:** Appartiene a Festival

### FormDefinition
- **Tabella:** `form_definitions`
- **Classe:** `FormDefinition`
- **Campi chiave:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relazioni:** Appartiene a Festival, ha molti FormPages, FormLinks, FormResponses

### Group
- **Tabella:** `groups`
- **Classe:** `Group`
- **Campi chiave:** name, display_name, description, sort_order, is_active
- **Relazioni:** Ha molti RoleGroupMemberships, Roles

### AppSetting
- **Tabella:** `app_settings`
- **Classe:** `AppSetting`
- **Campi chiave:** key, value, description, is_public
- **Relazioni:** Entità di configurazione

### AuditLog
- **Tabella:** `audit_logs`
- **Classe:** `AuditLog`
- **Campi chiave:** actor_id (FK), action, target, ip, created_at
- **Relazioni:** Appartiene a User (attore), append-only

### UserBlock
- **Tabella:** `user_blocks`
- **Classe:** `UserBlock`
- **Campi chiave:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relazioni:** Appartiene a User (bloccante), appartiene a User (bloccato)

### UserFollow
- **Tabella:** `user_follows`
- **Classe:** `UserFollow`
- **Campi chiave:** `follower_id` (FK), `followed_id` (FK), created_at, updated_at

### RoleDelegation
- **Tabella:** `role_delegations`
- **Classe:** `RoleDelegation`
- **Campi chiave:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relazioni:** Appartiene a User (delegante), appartiene a User (delegato), appartiene a Role, appartiene a Festival, appartiene a User (revocatore)

### RoleTransition
- **Tabella:** `role_transitions`
- **Classe:** `RoleTransition`
- **Campi chiave:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relazioni:** Appartiene a User, appartiene a Role (origine), appartiene a Role (destinazione), appartiene a Festival (origine), appartiene a Festival (destinazione), appartiene a User (responsabile del cambiamento)

### EventTicketType
- **Tabella:** `event_ticket_types`
- **Classe:** `EventTicketType`
- **Campi chiave:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relazioni:** Appartiene a Event

### EventSeat
- **Tabella:** `event_seats`
- **Classe:** `EventSeat`
- **Campi chiave:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relazioni:** Appartiene a Event, appartiene a EventTicketType
- **Vincolo:** `UNIQUE (event_id, section, row_label, number)` → `uq_event_seat_location` (migrazione `a8b9c0d1e2f3`; sostituisce l'inoperante `Meta.unique_together` di SQLAlchemy)

### EventReservation
- **Tabella:** `event_reservations`
- **Classe:** `EventReservation`
- **Campi chiave:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relazioni:** Appartiene a Event, appartiene a User (prenotante), appartiene a User (creatore)

### EventAttendee
- **Tabella:** `event_attendees`
- **Classe:** `EventAttendee`
- **Campi chiave:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relazioni:** Appartiene a Event, appartiene a EventReservation, appartiene a User, appartiene a EventSeat, appartiene a EventTicketType, appartiene a User (invitante)

## Sessioni del database

Le sessioni del database sono gestite tramite `get_db()` in `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Questo viene usato come dipendenza FastAPI per l'accesso al database dagli endpoint.

## Note sulla migrazione da SQLite a MariaDB

Le modifiche dello schema sono gestite con Alembic (`backend/alembic/versions/`; `alembic upgrade head`). Ci sono 45 revisioni e l'head è `d1e2f3a4b5c6`; le ultime sette (`a8b9c0d1e2f3`, `a9b0c1d2e3f4`, `b0c1d2e3f4a5`, `c1d2e3f4a5b6`, `b9c0d1e2f3a4`, `c0d1e2f3a4b5`, `d1e2f3a4b5c6`) aggiungono l'unicità del posto, le tabelle di portabilità, la coda durable della chat, la moderazione, `contest_type` in `shortfilms` con indice e `festival_id` obbligatorio con FK `RESTRICT`, e i metadati di revoca in `trusted_nodes` (`revoked_at`, `revocation_reason`, `revoked_by`). In produzione solo Alembic, mai `create_all`.
La revisione `d1e2f3a4b5c6` aggiunge la tabella `user_follows` (coppia univoca `follower_id`, `followed_id`).

Quando si migra da SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` corrisponde a MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` corrisponde a MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` è memorizzato come testo; MariaDB usa `DATETIME` nativo
- Gli script di migrazione in `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` gestiscono automaticamente le conversioni di tipo
