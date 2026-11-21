# Datenbankdokumentation

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Übersicht

Clakettes verwendet eine doppelte Datenbankkonfiguration:
- **Entwicklung**: SQLite (`clakettes.db`) — Standard, keine Konfiguration erforderlich
- **Produktion**: MariaDB — konfiguriert über `DATABASE_URL` in `backend/.env`

Migrationswerkzeuge stehen zur Synchronisierung zwischen Umgebungen bereit:
- `python export_sqlite_to_mariadb.py` — Entwicklung zu Produktion
- `python import_mariadb_to_sqlite.py` — Produktion zu Entwicklung

## MariaDB konfigurieren (Produktion)

Standardmäßig verwendet Clakettes SQLite (`clakettes.db`), das keine Konfiguration erfordert. Für MariaDB:

1. Kopiere `backend/.env.example` nach `backend/.env` und kommentiere die MariaDB-`DATABASE_URL`-Zeile aus:
   ```env
   DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db
   ```
2. Starte den MariaDB-Container:
   ```bash
   # Entwicklung/lokal mit MariaDB
   docker compose --profile db up -d

   # Vollständige Produktion (Backend + Frontend + MariaDB + nginx)
   docker compose --profile prod up -d
   ```
3. Führe die Migrationen aus (nur Alembic, nie `create_all` in Produktion):
   ```bash
   cd backend
   alembic upgrade head
   ```
   Oder mit den Projekt-Skripten:
   ```bash
   start.* --migrate --mariadb
   ```
4. (Optional) Kopiere Daten von SQLite nach MariaDB:
   ```bash
   cd backend && python tools/export_sqlite_to_mariadb.py
   ```

Erforderliche Variablen in `backend/.env` bei Verwendung von MariaDB:

| Variable | Beispiel | Hinweise |
|---|---|---|
| `DATABASE_URL` | `mariadb+pymysql://user:pass@host:3306/dbname` | SQLAlchemy-Verbindungszeichenfolge; in Docker Compose ist der Host `db` |
| `SECRET_KEY` | `change-this-in-production` | JWT-Signaturschlüssel |
| `CORS_ORIGINS` | `https://your-domain.com` | Explizite Domains in Produktion |
| `PUBLIC_BASE_URL` | `https://your-domain.com` | Öffentliche URL des Knotens (Föderation) |

In Docker Compose wird der Dienst `db` (MariaDB 11) mit `--profile db` oder `--profile prod` aktiviert; das Backend verbindet sich mit `db` als Host und Port `3306`.

Wichtige Hinweise:
- MariaDB in Produktion erfordert TLS: `?ssl_ca=...` zu `DATABASE_URL` hinzufügen.
- Nie `create_all` in Produktion verwenden; das Schema nur mit Alembic verwalten (`alembic upgrade head`).
- Für die Rückkehr von MariaDB zu SQLite: `python tools/import_mariadb_to_sqlite.py`.

## Modellübersicht

| Modell | Tabelle | Typ |
|---|---|---|
| `AppSetting` | `app_settings` | Entität |
| `AuditLog` | `audit_logs` | Entität |
| `Award` | `awards` | Entität |
| `Badge` | `badges` | Entität |
| `Calendar` | `calendars` | Entität |
| `ChatMute` | `chat_mutes` | Entität (Föderation) |
| `ChatOutbox` | `chat_outbox` | Entität (Föderation) |
| `Channel` | `channels` | Entität |
| `Committee` | `committees` | Entität |
| `Event` | `events` | Entität |
| `EventScreening` | `event_screenings` | Entität |
| `Festival` | `festivals` | Entität |
| `FestivalLocation` | `festival_locations` | Entität |
| `FestivalRulebook` | `festival_rulebooks` | Entität |
| `FormDefinition` | `form_definitions` | Entität |
| `Group` | `groups` | Entität |
| `IdentityRedirect` | `identity_redirects` | Entität (Föderation) |
| `JuryVote` | `jury_votes` | Entität |
| `MessageReport` | `message_reports` | Entität (Föderation) |
| `MigrationAudit` | `migration_audits` | Entität (Föderation) |
| `Location` | `locations` | Entität |
| `LocationImage` | `location_images` | Entität |
| `LocationRelation` | `location_relations` | Entität |
| `LocationTag` | `location_tags` | Entität |
| `Message` | `messages` | Entität |
| `ModerationReport` | `moderation_reports` | Entität |
| `NodePolicy` | `node_policies` | Entität |
| `Notification` | `notifications` | Entität |
| `ParticipantTag` | `participant_tags` | Entität |
| `Payment` | `payments` | Entität |
| `Post` | `posts` | Entität |
| `Registration` | `registration_forms` | Entität |
| `Role` | `roles` | Entität |
| `RoleDelegation` | `role_delegations` | Entität |
| `RoleGroup` | `role_groups` | Entität |
| `RoleTransition` | `role_transitions` | Entität |
| `ShortFilm` | `shortfilms` | Entität |
| `ShortFilmLocation` | `shortfilm_locations` | Entität |
| `User` | `users` | Entität |
| `UserAlias` | `user_aliases` | Entität |
| `UserBlock` | `user_blocks` | Entität |
| `UserFestival` | `user_festival` | Assoziation (Tabelle) |
| `UserKey` | `user_keys` | Entität |
| `UserRole` | `user_roles` | Entität |
| `UserSession` | `user_sessions` | Entität |
| `ValidationRule` | `validation_rules` | Entität |
| `ValidationRuleGroup` | `validation_rule_groups` | Entität |

Assoziationstabellen:
- `user_festival` — M2M zwischen `User` und `Festival`
- `validation_rule_group_rules` — M2M zwischen `ValidationRuleGroup` und `ValidationRule`

## Basismodell

Alle Modelle erben von `BaseModel` in `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Felder:
- `id`: Primärschlüssel, automatisch inkrementierende Ganzzahl
- `created_at`: Zeitstempel bei der Erstellung
- `updated_at`: Zeitstempel, bei jeder Änderung aktualisiert

## Hauptmodelle

### Festival
- **Tabelle:** `festivals`
- **Klasse:** `Festival`
- **Schlüsselfelder:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Beziehungen:** Hat viele ShortFilms, Users (M2M über `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Tabelle:** `users`
- **Klasse:** `User`
- **Schlüsselfelder:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Beziehungen:** Hat viele ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (erstellt), EventAttendees, EventReservations

### ShortFilm
- **Tabelle:** `shortfilms`
- **Klasse:** `ShortFilm`
- **Schlüsselfelder:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Beziehungen:** Gehört zu Festival, gehört zu User, hat viele Awards, hat viele ShortFilmLocations

### Message
- **Tabelle:** `messages`
- **Klasse:** `Message`
- **Schlüsselfelder:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Beziehungen:** Gehört zu User (Absender), gehört zu User (Empfänger), gehört zu Channel

### User-Festival-Assoziation
- **Tabelle:** `user_festival`
- **Klasse:** None (SQLAlchemy Table)
- **Schlüsselfelder:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Beziehungen:** M2M-Brücke zwischen User und Festival; zusammengesetzter PK auf (user_id, festival_id)

### Award
- **Tabelle:** `awards`
- **Klasse:** `Award`
- **Schlüsselfelder:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Beziehungen:** Gehört zu Festival, gehört zu Event, gehört zu ShortFilm, gehört zu User (Empfänger), gehört zu User (Verifizierer), gehört zu User (Ersteller)

### Badge
- **Tabelle:** `badges`
- **Klasse:** `Badge`
- **Schlüsselfelder:** name, description, image_url (SVG bevorzugt), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Beziehungen:** Gehört zu Festival, hat viele BadgeAssignments
- **Hinweise:** Funktion in aktiver Entwicklung und standardmäßig deaktiviert (`badges.enabled`); nur das Admin-Team aktiviert sie.

### Channel
- **Tabelle:** `channels`
- **Klasse:** `Channel`
- **Schlüsselfelder:** name, description, channel_type, max_members, created_by (FK), is_active
- **Beziehungen:** Gehört zu User (Ersteller), hat viele ChannelMembers, hat viele Messages

### Committee
- **Tabelle:** `committees`
- **Klasse:** `Committee`
- **Schlüsselfelder:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Beziehungen:** Gehört zu Festival, gehört zu Role, hat viele CommitteeMembers

### Event
- **Tabelle:** `events`
- **Klasse:** `Event`
- **Schlüsselfelder:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Beziehungen:** Gehört zu Festival, gehört zu User (Ersteller), hat viele EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Tabelle:** `notifications`
- **Klasse:** `Notification`
- **Schlüsselfelder:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Beziehungen:** Gehört zu User (Empfänger), gehört zu User (bezogen)

### ParticipantTag
- **Tabelle:** `participant_tags`
- **Klasse:** `ParticipantTag`
- **Schlüsselfelder:** name, display_name, description, category, is_global, is_active, sort_order
- **Beziehungen:** Hat viele UserParticipantTags, hat viele FestivalParticipantTags

### Post
- **Tabelle:** `posts`
- **Klasse:** `Post`
- **Schlüsselfelder:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Beziehungen:** Gehört zu User (Autor), gehört zu User (Pinnwand), gehört zu Festival (Pinnwand), hat viele Antworten (Post), gehört zu Post (Eltern)
- **Hinweise:** Funktion in aktiver Entwicklung.

### Registration
- **Tabelle:** `registration_forms`
- **Klasse:** `RegistrationForm`
- **Schlüsselfelder:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Beziehungen:** Gehört zu Festival, hat viele RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Tabelle:** `roles`
- **Klasse:** `Role`
- **Schlüsselfelder:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Beziehungen:** Gehört zu Role (Eltern), gehört zu RoleGroup, hat viele UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Tabelle:** `user_aliases`
- **Klasse:** `UserAlias`
- **Schlüsselfelder:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Beziehungen:** Gehört zu User
- **Hinweise:** Unterstützt sichtbare Namen je Kontext (global, festival, shortfilm, chat, public_profile, credits) mit Sichtbarkeitssteuerung

### UserKey
- **Tabelle:** `user_keys`
- **Klasse:** `UserKey`
- **Schlüsselfelder:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Beziehungen:** Gehört zu User
- **Hinweise:** Speichert den X25519-Öffentlichen Schlüssel für E2EE; ein aktiver Schlüssel pro Nutzer

### UserSession
- **Tabelle:** `user_sessions`
- **Klasse:** `UserSession`
- **Schlüsselfelder:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Beziehungen:** Gehört zu User

### ValidationRule
- **Tabelle:** `validation_rules`
- **Klasse:** `ValidationRule`
- **Schlüsselfelder:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Beziehungen:** M2M mit ValidationRuleGroup über `validation_rule_group_rules`

### Payment
- **Tabelle:** `payments`
- **Klasse:** `Payment`
- **Schlüsselfelder:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Beziehungen:** Gehört zu Registration

### JuryVote
- **Tabelle:** `jury_votes`
- **Klasse:** `JuryVote`
- **Schlüsselfelder:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Beziehungen:** Gehört zu Festival, gehört zu ShortFilm, gehört zu User (Juror)

### NodePolicy
- **Tabelle:** `node_policies`
- **Klasse:** `NodePolicy`
- **Schlüsselfelder:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Beziehungen:** Föderationsentität

### ModerationReport
- **Tabelle:** `moderation_reports`
- **Klasse:** `ModerationReport`
- **Schlüsselfelder:** reporter_node, target_node, target_user_ref, reason, status
- **Beziehungen:** Föderationsentität

### IdentityRedirect
- **Tabelle:** `identity_redirects`
- **Klasse:** `IdentityRedirect`
- **Schlüsselfelder:** old_ref (eindeutiger Index), new_ref, target_domain, created_at
- **Beziehungen:** Föderationsentität; löst die alte Ref nach einer Identitätsmigration auf

### MigrationAudit
- **Tabelle:** `migration_audits`
- **Klasse:** `MigrationAudit`
- **Schlüsselfelder:** entity_type, entity_id, action, source_domain, target_domain, details (JSON), created_at
- **Beziehungen:** Föderationsentität; protokolliert jede Festival- oder Nutzer-Migration

### ChatOutbox
- **Tabelle:** `chat_outbox`
- **Klasse:** `ChatOutbox`
- **Schlüsselfelder:** message_id (eindeutig), node_origin, subject, payload (JSON), signature, status, attempts, last_error, created_at
- **Beziehungen:** Durable Queue des föderierten Chats (`DurableQueueBackend`); die Eindeutigkeit von `message_id` liefert Deduplizierung und `attempts`/`last_error` steuern Wiederholungen

### MessageReport
- **Tabelle:** `message_reports`
- **Klasse:** `MessageReport`
- **Schlüsselfelder:** reporter_id (FK), message_id (FK), reason, status
- **Beziehungen:** Gehört zu User (Meldender) und Message

### ChatMute
- **Tabelle:** `chat_mutes`
- **Klasse:** `ChatMute`
- **Schlüsselfelder:** user_id (FK), channel_id (FK), node_domain, until, reason
- **Beziehungen:** Gehört zu User und Channel; der Mute kann auf einen Kanal oder einen föderierten Knoten angewendet werden

### Location
- **Tabelle:** `locations`
- **Klasse:** `Location`
- **Schlüsselfelder:** name, description, latitude, longitude, address, is_active
- **Beziehungen:** Gehört zu Festival (M2M), hat viele LocationImages, LocationTags, LocationRelations

### EventScreening
- **Tabelle:** `event_screenings`
- **Klasse:** `EventScreening`
- **Schlüsselfelder:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Beziehungen:** Gehört zu Event, gehört zu ShortFilm

### FestivalRulebook
- **Tabelle:** `festival_rulebooks`
- **Klasse:** `FestivalRulebook`
- **Schlüsselfelder:** festival_id (FK), title, content, file_url, is_active
- **Beziehungen:** Gehört zu Festival

### FormDefinition
- **Tabelle:** `form_definitions`
- **Klasse:** `FormDefinition`
- **Schlüsselfelder:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Beziehungen:** Gehört zu Festival, hat viele FormPages, FormLinks, FormResponses

### Group
- **Tabelle:** `groups`
- **Klasse:** `Group`
- **Schlüsselfelder:** name, display_name, description, sort_order, is_active
- **Beziehungen:** Hat viele RoleGroupMemberships, Roles

### AppSetting
- **Tabelle:** `app_settings`
- **Klasse:** `AppSetting`
- **Schlüsselfelder:** key, value, description, is_public
- **Beziehungen:** Konfigurationsentität

### AuditLog
- **Tabelle:** `audit_logs`
- **Klasse:** `AuditLog`
- **Schlüsselfelder:** actor_id (FK), action, target, ip, created_at
- **Beziehungen:** Gehört zu User (Akteur), append-only

### UserBlock
- **Tabelle:** `user_blocks`
- **Klasse:** `UserBlock`
- **Schlüsselfelder:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Beziehungen:** Gehört zu User (Blockierender), gehört zu User (Blockierter)

### RoleDelegation
- **Tabelle:** `role_delegations`
- **Klasse:** `RoleDelegation`
- **Schlüsselfelder:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Beziehungen:** Gehört zu User (Delegierender), gehört zu User (Bevollmächtigter), gehört zu Role, gehört zu Festival, gehört zu User (Widerrufer)

### RoleTransition
- **Tabelle:** `role_transitions`
- **Klasse:** `RoleTransition`
- **Schlüsselfelder:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Beziehungen:** Gehört zu User, gehört zu Role (Ursprung), gehört zu Role (Ziel), gehört zu Festival (Ursprung), gehört zu Festival (Ziel), gehört zu User (Verantwortlicher der Änderung)

### EventTicketType
- **Tabelle:** `event_ticket_types`
- **Klasse:** `EventTicketType`
- **Schlüsselfelder:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Beziehungen:** Gehört zu Event

### EventSeat
- **Tabelle:** `event_seats`
- **Klasse:** `EventSeat`
- **Schlüsselfelder:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Beziehungen:** Gehört zu Event, gehört zu EventTicketType

### EventReservation
- **Tabelle:** `event_reservations`
- **Klasse:** `EventReservation`
- **Schlüsselfelder:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Beziehungen:** Gehört zu Event, gehört zu User (Reservierender), gehört zu User (Ersteller)

### EventAttendee
- **Tabelle:** `event_attendees`
- **Klasse:** `EventAttendee`
- **Schlüsselfelder:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Beziehungen:** Gehört zu Event, gehört zu EventReservation, gehört zu User, gehört zu EventSeat, gehört zu EventTicketType, gehört zu User (Einladender)

## Datenbanksitzungen

Datenbanksitzungen werden über `get_db()` in `app/database.py` verwaltet:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Dies wird als FastAPI-Abhängigkeit für den Datenbankzugriff aus Endpoints verwendet.

## Hinweise zur Migration von SQLite nach MariaDB

Schemaänderungen werden mit Alembic verwaltet (`backend/alembic/versions/`; `alembic upgrade head`). Es gibt 42 Revisionen und der Head ist `c1d2e3f4a5b6`; die drei letzten (`a9b0c1d2e3f4`, `b0c1d2e3f4a5`, `c1d2e3f4a5b6`) fügen die Portabilitätstabellen, die durable Chat-Queue und die Moderation hinzu. In Produktion nur Alembic, nie `create_all`.

Bei der Migration von SQLite nach MariaDB:
- SQLite `INTEGER PRIMARY KEY` entspricht MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` entspricht MariaDB `TEXT` oder `VARCHAR`
- SQLite `DATETIME` wird als Text gespeichert; MariaDB nutzt natives `DATETIME`
- Die Migrationsskripte in `export_sqlite_to_mariadb.py` und `import_mariadb_to_sqlite.py` übernehmen die Typkonvertierungen automatisch
