# Datenbankdokumentation

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Übersicht

Clakettes verwendet eine duale Datenbankkonfiguration:
- **Entwicklung**: SQLite (`clakettes.db`) — Standard, keine Konfiguration erforderlich
- **Produktion**: MariaDB — konfiguriert über `DATABASE_URL` in `backend/.env`

Migrationswerkzeuge sind verfügbar, um zwischen Umgebungen zu synchronisieren:
- `python export_sqlite_to_mariadb.py` — Entwicklung zu Produktion
- `python import_mariadb_to_sqlite.py` — Produktion zu Entwicklung

## Modellzusammenfassung

| Modell | Tabelle | Typ |
|--------|---------|-----|
| `AppSetting` | `app_settings` | Entität |
| `AuditLog` | `audit_logs` | Entität |
| `Award` | `awards` | Entität |
| `Badge` | `badges` | Entität |
| `Calendar` | `calendars` | Entität |
| `Channel` | `channels` | Entität |
| `Committee` | `committees` | Entität |
| `Event` | `events` | Entität |
| `EventScreening` | `event_screenings` | Entität |
| `Festival` | `festivals` | Entität |
| `FestivalLocation` | `festival_locations` | Entität |
| `FestivalRulebook` | `festival_rulebooks` | Entität |
| `FormDefinition` | `form_definitions` | Entität |
| `Group` | `groups` | Entität |
| `JuryVote` | `jury_votes` | Entität |
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

Gesamt: 40 Entitätsmodelle + 2 Assoziationstabellen = 42 SQLAlchemy-Konstrukte.

## Basismodell

Alle Modelle erben von `BaseModel` definiert in `app/models/base.py`:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Felder:
- `id`: Primärschlüssel, auto-inkrementierte Ganzzahl
- `created_at`: Zeitstempel bei Erstellung zugewiesen
- `updated_at`: Zeitstempel bei jeder Änderung aktualisiert

## Hauptmodelle

### Festival
- **Tabelle**: `festivals`
- **Klasse**: `Festival`
- **Wichtige Felder**: name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Beziehungen**: Hat viele ShortFilms, Nutzer (M2M über `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### Nutzer
- **Tabelle**: `users`
- **Klasse**: `User`
- **Wichtige Felder**: username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Beziehungen**: Hat viele ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (erstellt), EventAttendees, EventReservations

### Kurzfilm
- **Tabelle**: `shortfilms`
- **Klasse**: `ShortFilm`
- **Wichtige Felder**: title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Beziehungen**: Gehört zu Festival, gehört zu Nutzer, hat viele Awards, hat viele ShortFilmLocations

### Nachricht
- **Tabelle**: `messages`
- **Klasse**: `Message`
- **Wichtige Felder**: content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Beziehungen**: Gehört zu Nutzer (Absender), gehört zu Nutzer (Empfänger), gehört zu Channel

### Nutzer-Festival-Assoziation
- **Tabelle**: `user_festival`
- **Klasse**: None (SQLAlchemy-Tabelle)
- **Wichtige Felder**: user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Beziehungen**: M2M-Brücke zwischen Nutzer und Festival; zusammengesetzter PK auf (user_id, festival_id)

### Auszeichnung
- **Tabelle**: `awards`
- **Klasse**: `Award`
- **Wichtige Felder**: festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Beziehungen**: Gehört zu Festival, gehört zu Event, gehört zu ShortFilm, gehört zu Nutzer (Empfänger), gehört zu Nutzer (Verifier), gehört zu Nutzer (Ersteller)

### Badge
- **Tabelle**: `badges`
- **Klasse**: `Badge`
- **Wichtige Felder**: name, description, image_url (SVG bevorzugt), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Beziehungen**: Gehört zu Festival, hat viele BadgeAssignments
- **Hinweise**: Funktion in aktiver Entwicklung und standardmäßig deaktiviert (`badges.enabled`); nur das Admin-Team aktiviert sie.

### Kanal
- **Tabelle**: `channels`
- **Klasse**: `Channel`
- **Wichtige Felder**: name, description, channel_type, max_members, created_by (FK), is_active
- **Beziehungen**: Gehört zu Nutzer (Ersteller), hat viele ChannelMembers, hat viele Messages

### Komitee
- **Tabelle**: `committees`
- **Klasse**: `Committee`
- **Wichtige Felder**: festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Beziehungen**: Gehört zu Festival, gehört zu Role, hat viele CommitteeMembers

### Event
- **Tabelle**: `events`
- **Klasse**: `Event`
- **Wichtige Felder**: festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Beziehungen**: Gehört zu Festival, gehört zu Nutzer (Ersteller), hat viele EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Benachrichtigung
- **Tabelle**: `notifications`
- **Klasse**: `Notification`
- **Wichtige Felder**: user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Beziehungen**: Gehört zu Nutzer (Empfänger), gehört zu Nutzer (verbunden)

### Teilnehmer-Tag
- **Tabelle**: `participant_tags`
- **Klasse**: `ParticipantTag`
- **Wichtige Felder**: name, display_name, description, category, is_global, is_active, sort_order
- **Beziehungen**: Hat viele UserParticipantTags, hat viele FestivalParticipantTags

### Post
- **Tabelle**: `posts`
- **Klasse**: `Post`
- **Wichtige Felder**: author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Beziehungen**: Gehört zu Nutzer (Autor), gehört zu Nutzer (Wand), gehört zu Festival (Wand), hat viele Antworten (Post), gehört zu Post (Elternteil)
- **Hinweise**: Funktion in aktiver Entwicklung.

### Registrierung
- **Tabelle**: `registration_forms`
- **Klasse**: `RegistrationForm`
- **Wichtige Felder**: festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Beziehungen**: Gehört zu Festival, hat viele RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Rolle
- **Tabelle**: `roles`
- **Klasse**: `Role`
- **Wichtige Felder**: name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Beziehungen**: Gehört zu Role (Elternteil), gehört zu RoleGroup, hat viele UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### Nutzer-Alias
- **Tabelle**: `user_aliases`
- **Klasse**: `UserAlias`
- **Wichtige Felder**: user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Beziehungen**: Gehört zu Nutzer
- **Hinweise**: Erlaubt sichtbare Namen pro Kontext (global, festival, shortfilm, chat, public_profile, credits) mit Sichtbarkeitskontrolle

### Nutzer-Schlüssel
- **Tabelle**: `user_keys`
- **Klasse**: `UserKey`
- **Wichtige Felder**: user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Beziehungen**: Gehört zu Nutzer
- **Hinweise**: Speichert den X25519-Öffentlichen Schlüssel für E2EE; ein aktiver Schlüssel pro Nutzer

### Nutzer-Session
- **Tabelle**: `user_sessions`
- **Klasse**: `UserSession`
- **Wichtige Felder**: user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Beziehungen**: Gehört zu Nutzer

### Validierungsregel
- **Tabelle**: `validation_rules`
- **Klasse**: `ValidationRule`
- **Wichtige Felder**: name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Beziehungen**: M2M mit ValidationRuleGroup über `validation_rule_group_rules`

### Zahlung
- **Tabelle**: `payments`
- **Klasse**: `Payment`
- **Wichtige Felder**: amount, currency, provider_ref, status, provider, registration_id (FK)
- **Beziehungen**: Gehört zu Registration

### Jury-Stimme
- **Tabelle**: `jury_votes`
- **Klasse**: `JuryVote`
- **Wichtige Felder**: festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Beziehungen**: Gehört zu Festival, gehört zu ShortFilm, gehört zu Nutzer (Juror)

### Knotenrichtlinie
- **Tabelle**: `node_policies`
- **Klasse**: `NodePolicy`
- **Wichtige Felder**: node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Beziehungen**: Föderations-Entität

### Moderationsbericht
- **Tabelle**: `moderation_reports`
- **Klasse**: `ModerationReport`
- **Wichtige Felder**: reporter_node, target_node, target_user_ref, reason, status
- **Beziehungen**: Föderations-Entität

### Standort
- **Tabelle**: `locations`
- **Klasse**: `Location`
- **Wichtige Felder**: name, description, latitude, longitude, address, is_active
- **Beziehungen**: Gehört zu Festival (M2M), hat viele LocationImages, LocationTags, LocationRelations

### Event-Vorführung
- **Tabelle**: `event_screenings`
- **Klasse**: `EventScreening`
- **Wichtige Felder**: event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Beziehungen**: Gehört zu Event, gehört zu ShortFilm

### Festival-Regelwerk
- **Tabelle**: `festival_rulebooks`
- **Klasse**: `FestivalRulebook`
- **Wichtige Felder**: festival_id (FK), title, content, file_url, is_active
- **Beziehungen**: Gehört zu Festival

### Formulardefinition
- **Tabelle**: `form_definitions`
- **Klasse**: `FormDefinition`
- **Wichtige Felder**: festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Beziehungen**: Gehört zu Festival, hat viele FormPages, FormLinks, FormResponses

### Gruppe
- **Tabelle**: `groups`
- **Klasse**: `Group`
- **Wichtige Felder**: name, display_name, description, sort_order, is_active
- **Beziehungen**: Hat viele RoleGroupMemberships, Roles

### App-Einstellung
- **Tabelle**: `app_settings`
- **Klasse**: `AppSetting`
- **Wichtige Felder**: key, value, description, is_public
- **Beziehungen**: Konfigurations-Entität

### Audit-Log
- **Tabelle**: `audit_logs`
- **Klasse**: `AuditLog`
- **Wichtige Felder**: actor_id (FK), action, target, ip, created_at
- **Beziehungen**: Gehört zu Nutzer (Akteur), append-only

### Nutzer-Blockierung
- **Tabelle**: `user_blocks`
- **Klasse**: `UserBlock`
- **Wichtige Felder**: blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Beziehungen**: Gehört zu Nutzer (Blocker), gehört zu Nutzer (blockiert)

### Rollendelegation
- **Tabelle**: `role_delegations`
- **Klasse**: `RoleDelegation`
- **Wichtige Felder**: delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Beziehungen**: Gehört zu Nutzer (Delegator), gehört zu Nutzer (Delegierter), gehört zu Role, gehört zu Festival, gehört zu Nutzer (Widerrufer)

### Rollen-Übergang
- **Tabelle**: `role_transitions`
- **Klasse**: `RoleTransition`
- **Wichtige Felder**: user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Beziehungen**: Gehört zu Nutzer, gehört zu Role (Ursprung), gehört zu Role (Ziel), gehört zu Festival (Ursprung), gehört zu Festival (Ziel), gehört zu Nutzer (Verantwortlich für Änderung)

### Event-Tickettyp
- **Tabelle**: `event_ticket_types`
- **Klasse**: `EventTicketType`
- **Wichtige Felder**: event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Beziehungen**: Gehört zu Event

### Event-Sitz
- **Tabelle**: `event_seats`
- **Klasse**: `EventSeat`
- **Wichtige Felder**: event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Beziehungen**: Gehört zu Event, gehört zu EventTicketType

### Event-Reservierung
- **Tabelle**: `event_reservations`
- **Klasse**: `EventReservation`
- **Wichtige Felder**: event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Beziehungen**: Gehört zu Event, gehört zu Nutzer (Reservierender), gehört zu Nutzer (Ersteller)

### Event-Teilnehmer
- **Tabelle**: `event_attendees`
- **Klasse**: `EventAttendee`
- **Wichtige Felder**: event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Beziehungen**: Gehört zu Event, gehört zu EventReservation, gehört zu Nutzer, gehört zu EventSeat, gehört zu EventTicketType, gehört zu Nutzer (Einladender)

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

Dies wird als FastAPI-Dependency für den Datenbankzugriff aus Endpunkten verwendet.

## Hinweise zur Migration von SQLite nach MariaDB

Schemaänderungen werden mit Alembic verwaltet (`backend/alembic/versions/`, 36 Versionen; `alembic upgrade head`). In Produktion nur Alembic, niemals `create_all`.

Beim Migrieren von SQLite nach MariaDB:
- SQLite `INTEGER PRIMARY KEY` entspricht MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` entspricht MariaDB `TEXT` oder `VARCHAR`
- SQLite `DATETIME` wird als Text gespeichert; MariaDB verwendet nativen `DATETIME`
- Die Migrationsskripte in `export_sqlite_to_mariadb.py` und `import_mariadb_to_sqlite.py` übernehmen die Typkonvertierungen automatisch