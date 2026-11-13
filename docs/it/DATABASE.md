# Documentazione del database

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Panoramica

Clakettes utilizza una configurazione a doppio database:
- **Sviluppo**: SQLite (`clakettes.db`) — default, nessuna configurazione richiesta
- **Produzione**: MariaDB — configurato tramite `DATABASE_URL` in `backend/.env`

Sono disponibili strumenti di migrazione per sincronizzare tra ambienti:
- `python export_sqlite_to_mariadb.py` — Sviluppo → Produzione
- `python import_mariadb_to_sqlite.py` — Produzione → Sviluppo

## Riepilogo modelli

| Modello | Tabella | Tipo |
|---------|---------|------|
| `AppSetting` | `app_settings` | Entità |
| `AuditLog` | `audit_logs` | Entità |
| `Award` | `awards` | Entità |
| `Badge` | `badges` | Entità |
| `Calendar` | `calendars` | Entità |
| `Channel` | `channels` | Entità |
| `Committee` | `committees` | Entità |
| `Event` | `events` | Entità |
| `EventScreening` | `event_screenings` | Entità |
| `Festival` | `festivals` | Entità |
| `FestivalLocation` | `festival_locations` | Entità |
| `FestivalRulebook` | `festival_rulebooks` | Entità |
| `FormDefinition` | `form_definitions` | Entità |
| `Group` | `groups` | Entità |
| `JuryVote` | `jury_votes` | Entità |
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
| `User` | `users` | Entità |
| `UserAlias` | `user_aliases` | Entità |
| `UserBlock` | `user_blocks` | Entità |
| `UserFestival` | `user_festival` | Associazione (Tabella) |
| `UserKey` | `user_keys` | Entità |
| `UserRole` | `user_roles` | Entità |
| `UserSession` | `user_sessions` | Entità |
| `ValidationRule` | `validation_rules` | Entità |
| `ValidationRuleGroup` | `validation_rule_groups` | Entità |

Tabelle di associazione:
- `user_festival` — M2M tra `User` e `Festival`
- `validation_rule_group_rules` — M2M tra `ValidationRuleGroup` e `ValidationRule`

Totale: 40 modelli di entità + 2 tabelle di associazione = 42 costruiti SQLAlchemy.

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
- `id`: Chiave primaria, intero auto-incrementale
- `created_at`: Marca temporale assegnata alla creazione
- `updated_at`: Marca temporale aggiornata a ogni modifica

## Modelli principali

### Festival
- **Tabella**: `festivals`
- **Classe**: `Festival`
- **Campi chiave**: name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relazioni**: Ha molti ShortFilms, Utenti (M2M tramite `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### Utente
- **Tabella**: `users`
- **Classe**: `User`
- **Campi chiave**: username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relazioni**: Ha molti ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (creati), EventAttendees, EventReservations

### Cortometraggio
- **Tabella**: `shortfilms`
- **Classe**: `ShortFilm`
- **Campi chiave**: title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relazioni**: Appartiene a Festival, appartiene a Utente, ha molti Awards, ha molti ShortFilmLocations

### Messaggio
- **Tabella**: `messages`
- **Classe**: `Message`
- **Campi chiave**: content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relazioni**: Appartiene a Utente (mittente), appartiene a Utente (destinatario), appartiene a Channel

### Associazione Utente-Festival
- **Tabella**: `user_festival`
- **Classe**: None (Tabella SQLAlchemy)
- **Campi chiave**: user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relazioni**: Ponte M2M tra Utente e Festival; PK composita su (user_id, festival_id)

### Premio
- **Tabella**: `awards`
- **Classe**: `Award`
- **Campi chiave**: festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relazioni**: Appartiene a Festival, appartiene a Event, appartiene a ShortFilm, appartiene a Utente (destinatario), appartiene a Utente (verificatore), appartiene a Utente (creatore)

### Badge
- **Tabella**: `badges`
- **Classe**: `Badge`
- **Campi chiave**: name, description, image_url (SVG preferito), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relazioni**: Appartiene a Festival, ha molti BadgeAssignments
- **Note**: Funzione in sviluppo attivo e disattivata per default (`badges.enabled`); solo il team amministrativo la attiva.

### Canale
- **Tabella**: `channels`
- **Classe**: `Channel`
- **Campi chiave**: name, description, channel_type, max_members, created_by (FK), is_active
- **Relazioni**: Appartiene a Utente (creatore), ha molti ChannelMembers, ha molti Messages

### Comitato
- **Tabella**: `committees`
- **Classe**: `Committee`
- **Campi chiave**: festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relazioni**: Appartiene a Festival, appartiene a Role, ha molti CommitteeMembers

### Evento
- **Tabella**: `events`
- **Classe**: `Event`
- **Campi chiave**: festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relazioni**: Appartiene a Festival, appartiene a Utente (creatore), ha molti EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notifica
- **Tabella**: `notifications`
- **Classe**: `Notification`
- **Campi chiave**: user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relazioni**: Appartiene a Utente (destinatario), appartiene a Utente (relazionato)

### Tag partecipante
- **Tabella**: `participant_tags`
- **Classe**: `ParticipantTag`
- **Campi chiave**: name, display_name, description, category, is_global, is_active, sort_order
- **Relazioni**: Ha molti UserParticipantTags, ha molti FestivalParticipantTags

### Post
- **Tabella**: `posts`
- **Classe**: `Post`
- **Campi chiave**: author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relazioni**: Appartiene a Utente (autore), appartiene a Utente (bacheca), appartiene a Festival (bacheca), ha molte risposte (Post), appartiene a Post (genitore)
- **Note**: Funzione in sviluppo attivo.

### Registrazione
- **Tabella**: `registration_forms`
- **Classe**: `RegistrationForm`
- **Campi chiave**: festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relazioni**: Appartiene a Festival, ha molti RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Ruolo
- **Tabella**: `roles`
- **Classe**: `Role`
- **Campi chiave**: name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relazioni**: Appartiene a Role (genitore), appartiene a RoleGroup, ha molti UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### Alias utente
- **Tabella**: `user_aliases`
- **Classe**: `UserAlias`
- **Campi chiave**: user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relazioni**: Appartiene a Utente
- **Note**: Permette nomi visibili per contesto (global, festival, shortfilm, chat, public_profile, credits) con controllo di visibilità

### Chiave utente
- **Tabella**: `user_keys`
- **Classe**: `UserKey`
- **Campi chiave**: user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relazioni**: Appartiene a Utente
- **Note**: Memorizza la chiave pubblica X25519 per E2EE; una chiave attiva per utente

### Sessione utente
- **Tabella**: `user_sessions`
- **Classe**: `UserSession`
- **Campi chiave**: user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relazioni**: Appartiene a Utente

### Regola di validazione
- **Tabella**: `validation_rules`
- **Classe**: `ValidationRule`
- **Campi chiave**: name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relazioni**: M2M con ValidationRuleGroup tramite `validation_rule_group_rules`

### Pagamento
- **Tabella**: `payments`
- **Classe**: `Payment`
- **Campi chiave**: amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relazioni**: Appartiene a Registration

### Voto giuria
- **Tabella**: `jury_votes`
- **Classe**: `JuryVote`
- **Campi chiave**: festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relazioni**: Appartiene a Festival, appartiene a ShortFilm, appartiene a Utente (giurato)

### Politica nodo
- **Tabella**: `node_policies`
- **Classe**: `NodePolicy`
- **Campi chiave**: node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relazioni**: Entità federazione

### Rapporto moderazione
- **Tabella**: `moderation_reports`
- **Classe**: `ModerationReport`
- **Campi chiave**: reporter_node, target_node, target_user_ref, reason, status
- **Relazioni**: Entità federazione

### Località
- **Tabella**: `locations`
- **Classe**: `Location`
- **Campi chiave**: name, description, latitude, longitude, address, is_active
- **Relazioni**: Appartiene a Festival (M2M), ha molti LocationImages, LocationTags, LocationRelations

### Proiezione evento
- **Tabella**: `event_screenings`
- **Classe**: `EventScreening`
- **Campi chiave**: event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relazioni**: Appartiene a Event, appartiene a ShortFilm

### Regolamento festival
- **Tabella**: `festival_rulebooks`
- **Classe**: `FestivalRulebook`
- **Campi chiave**: festival_id (FK), title, content, file_url, is_active
- **Relazioni**: Appartiene a Festival

### Definizione form
- **Tabella**: `form_definitions`
- **Classe**: `FormDefinition`
- **Campi chiave**: festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relazioni**: Appartiene a Festival, ha molti FormPages, FormLinks, FormResponses

### Gruppo
- **Tabella**: `groups`
- **Classe**: `Group`
- **Campi chiave**: name, display_name, description, sort_order, is_active
- **Relazioni**: Ha molti RoleGroupMemberships, Roles

### Impostazione app
- **Tabella**: `app_settings`
- **Classe**: `AppSetting`
- **Campi chiave**: key, value, description, is_public
- **Relazioni**: Entità configurazione

### Log audit
- **Tabella**: `audit_logs`
- **Classe**: `AuditLog`
- **Campi chiave**: actor_id (FK), action, target, ip, created_at
- **Relazioni**: Appartiene a Utente (attore), append-only

### Blocco utente
- **Tabella**: `user_blocks`
- **Classe**: `UserBlock`
- **Campi chiave**: blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relazioni**: Appartiene a Utente (bloccante), appartiene a Utente (bloccato)

### Delegazione ruolo
- **Tabella**: `role_delegations`
- **Classe**: `RoleDelegation`
- **Campi chiave**: delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relazioni**: Appartiene a Utente (delegante), appartiene a Utente (delegato), appartiene a Role, appartiene a Festival, appartiene a Utente (revocatore)

### Transizione ruolo
- **Tabella**: `role_transitions`
- **Classe**: `RoleTransition`
- **Campi chiave**: user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relazioni**: Appartiene a Utente, appartiene a Role (origine), appartiene a Role (destinazione), appartiene a Festival (origine), appartiene a Festival (destinazione), appartiene a Utente (responsabile del cambiamento)

### Tipo biglietto evento
- **Tabella**: `event_ticket_types`
- **Classe**: `EventTicketType`
- **Campi chiave**: event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relazioni**: Appartiene a Event

### Posto evento
- **Tabella**: `event_seats`
- **Classe**: `EventSeat`
- **Campi chiave**: event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relazioni**: Appartiene a Event, appartiene a EventTicketType

### Prenotazione evento
- **Tabella**: `event_reservations`
- **Classe**: `EventReservation`
- **Campi chiave**: event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relazioni**: Appartiene a Event, appartiene a Utente (prenotatore), appartiene a Utente (creatore)

### Partecipante evento
- **Tabella**: `event_attendees`
- **Classe**: `EventAttendee`
- **Campi chiave**: event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relazioni**: Appartiene a Event, appartiene a EventReservation, appartiene a Utente, appartiene a EventSeat, appartiene a EventTicketType, appartiene a Utente (invitante)

## Sessioni di database

Le sessioni di database sono gestite tramite `get_db()` in `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Questo è usato come dipendenza di FastAPI per l'accesso al database dagli endpoint.

## Note di migrazione da SQLite a MariaDB

Le modifiche allo schema sono gestite con Alembic (`backend/alembic/versions/`, 36 versioni; `alembic upgrade head`). In produzione solo Alembic, mai `create_all`.

Durante la migrazione da SQLite a MariaDB:
- SQLite `INTEGER PRIMARY KEY` corrisponde a MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` corrisponde a MariaDB `TEXT` o `VARCHAR`
- SQLite `DATETIME` è memorizzato come testo; MariaDB usa `DATETIME` nativo
- Gli script di migrazione in `export_sqlite_to_mariadb.py` e `import_mariadb_to_sqlite.py` gestiscono le conversioni di tipo automaticamente