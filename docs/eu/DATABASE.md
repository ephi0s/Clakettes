# Datu-basearen dokumentazioa

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](../fr/DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Ikuspegi orokorra

Clakettes-ek bi datu-baseko konfigurazioa erabiltzen du:
- **Garapena**: SQLite (`clakettes.db`) — lehenespenez, konfiguraziorik behar ez duena
- **Ekoizpena**: MariaDB — `backend/.env` fitxategian `DATABASE_URL` bidez konfiguratuta

Inguruen artean sinkronizatzeko migrazio-tresnak daude:
- `python export_sqlite_to_mariadb.py` — Garapenetik ekoizpenera
- `python import_mariadb_to_sqlite.py` — Ekoizpenetik garapenera

## MariaDB konfiguratu (ekoizpena)

Lehenespenez Clakettes-ek SQLite (`clakettes.db`) erabiltzen du, konfiguraziorik behar ez duena. MariaDB erabiltzeko:

1. Kopiatu `backend/.env.example` `backend/.env`-ra eta deskomentatu MariaDBaren `DATABASE_URL` lerroa:
   ```env
   DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db
   ```
2. Abiarazi MariaDB edukiontzia:
   ```bash
   # Garapena/tokikoa MariaDBrekin
   docker compose --profile db up -d

   # Ekoizpen osoa (backend + frontend + MariaDB + nginx)
   docker compose --profile prod up -d
   ```
3. Exekutatu migrazioak (soilik Alembic, inoiz ez `create_all` ekoizpenean):
   ```bash
   cd backend
   alembic upgrade head
   ```
   Edo proiektuaren script-ekin:
   ```bash
   start.* --migrate --mariadb
   ```
4. (Aukerakoa) Kopiatu datuak SQLite-tik MariaDB-ra:
   ```bash
   cd backend && python tools/export_sqlite_to_mariadb.py
   ```

MariaDB erabiltzean `backend/.env`-n beharrezko aldagaiak:

| Aldagaia | Adibidea | Oharrak |
|---|---|---|
| `DATABASE_URL` | `mariadb+pymysql://user:pass@host:3306/dbname` | SQLAlchemy katea; Docker Compose-n host-a `db` da |
| `SECRET_KEY` | `cambia-esta-clave-en-produccion` | JWT sinadura-gakoa |
| `CORS_ORIGINS` | `https://tu-dominio.com` | Domeinu esplizituak ekoizpenean |
| `PUBLIC_BASE_URL` | `https://tu-dominio.com` | Nodoaren URL publikoa (federazioa) |

Docker Compose-n `db` zerbitzuak (MariaDB 11) `--profile db` edo `--profile prod` bidez aktibatzen da; backend-a `db` host gisa eta `3306` ataka erabiliz konektatzen da.

Ohar garrantzitsuak:
- MariaDBk ekoizpenean TLS eskatzen du: gehitu `?ssl_ca=...` `DATABASE_URL`-ri.
- Inoiz ez erabili `create_all` ekoizpenean; kudeatu eskema soilik Alembic bidez (`alembic upgrade head`).
- MariaDBtik SQLite-ra itzultzeko: `python tools/import_mariadb_to_sqlite.py`.

## Modeloen laburpena

| Modeloa | Taula | Mota |
|---|---|---|
| `AppSetting` | `app_settings` | Entitatea |
| `AuditLog` | `audit_logs` | Entitatea |
| `Award` | `awards` | Entitatea |
| `Badge` | `badges` | Entitatea |
| `Calendar` | `calendars` | Entitatea |
| `ChatMute` | `chat_mutes` | Entitatea (federazioa) |
| `ChatOutbox` | `chat_outbox` | Entitatea (federazioa) |
| `Channel` | `channels` | Entitatea |
| `Committee` | `committees` | Entitatea |
| `Event` | `events` | Entitatea |
| `EventScreening` | `event_screenings` | Entitatea |
| `Festival` | `festivals` | Entitatea |
| `FestivalLocation` | `festival_locations` | Entitatea |
| `FestivalRulebook` | `festival_rulebooks` | Entitatea |
| `FormDefinition` | `form_definitions` | Entitatea |
| `Group` | `groups` | Entitatea |
| `IdentityRedirect` | `identity_redirects` | Entitatea (federazioa) |
| `JuryVote` | `jury_votes` | Entitatea |
| `MessageReport` | `message_reports` | Entitatea (federazioa) |
| `MigrationAudit` | `migration_audits` | Entitatea (federazioa) |
| `Location` | `locations` | Entitatea |
| `LocationImage` | `location_images` | Entitatea |
| `LocationRelation` | `location_relations` | Entitatea |
| `LocationTag` | `location_tags` | Entitatea |
| `Message` | `messages` | Entitatea |
| `ModerationReport` | `moderation_reports` | Entitatea |
| `NodePolicy` | `node_policies` | Entitatea |
| `Notification` | `notifications` | Entitatea |
| `ParticipantTag` | `participant_tags` | Entitatea |
| `Payment` | `payments` | Entitatea |
| `Post` | `posts` | Entitatea |
| `Registration` | `registration_forms` | Entitatea |
| `Role` | `roles` | Entitatea |
| `RoleDelegation` | `role_delegations` | Entitatea |
| `RoleGroup` | `role_groups` | Entitatea |
| `RoleTransition` | `role_transitions` | Entitatea |
| `ShortFilm` | `shortfilms` | Entitatea |
| `ShortFilmLocation` | `shortfilm_locations` | Entitatea |
| `User` | `users` | Entitatea |
| `UserAlias` | `user_aliases` | Entitatea |
| `UserBlock` | `user_blocks` | Entitatea |
| `UserFestival` | `user_festival` | Elkartea (Taula) |
| `UserKey` | `user_keys` | Entitatea |
| `UserRole` | `user_roles` | Entitatea |
| `UserSession` | `user_sessions` | Entitatea |
| `ValidationRule` | `validation_rules` | Entitatea |
| `ValidationRuleGroup` | `validation_rule_groups` | Entitatea |

Elkarte-taulak:
- `user_festival` — M2M `User` eta `Festival` artean
- `validation_rule_group_rules` — M2M `ValidationRuleGroup` eta `ValidationRule` artean

## Oinarrizko modeloa

Modelo guztiek `app/models/base.py`-n definitutako `BaseModel`-etik heredatzen dute:

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Eremuak:
- `id`: Gako primarioa, automatikoki handitzen den osokoa
- `created_at`: Sortzean esleitutako denbora-marka
- `updated_at`: Aldaketa bakoitzean eguneratzen den denbora-marka

## Modelo nagusiak

### Festival
- **Taula:** `festivals`
- **Klasea:** `Festival`
- **Gako-eremuak:** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Erlazioak:** ShortFilm, User (M2M `user_festival` bidez), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards ditu

### User
- **Taula:** `users`
- **Klasea:** `User`
- **Gako-eremuak:** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Errelazioak:** ShortFilm, Festival (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (sortuak), EventAttendees, EventReservations ditu

### ShortFilm
- **Taula:** `shortfilms`
- **Klasea:** `ShortFilm`
- **Gako-eremuak:** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Errelazioak:** Festival-i dagokio, User-i dagokio, Awards ditu, ShortFilmLocations ditu

### Message
- **Taula:** `messages`
- **Klasea:** `Message`
- **Gako-eremuak:** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Errelazioak:** User-i (igortzailea), User-i (hartzailea), Channel-i dagokio

### User-Festival Association
- **Taula:** `user_festival`
- **Klasea:** None (SQLAlchemy Table)
- **Gako-eremuak:** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Errelazioak:** User eta Festival arteko M2M zubia; PK konposatua (user_id, festival_id)-n

### Award
- **Taula:** `awards`
- **Klasea:** `Award`
- **Gako-eremuak:** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Errelazioak:** Festival-i, Event-i, ShortFilm-i, User-i (hartzailea), User-i (egiaztatzailea), User-i (sortzailea) dagokio

### Badge
- **Taula:** `badges`
- **Klasea:** `Badge`
- **Gako-eremuak:** name, description, image_url (SVG hobetsia), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Errelazioak:** Festival-i dagokio, BadgeAssignments ditu
- **Oharrak:** Garapen aktiboko funtzioa, lehenespenez desaktibatuta (`badges.enabled`); soilik administrazio-taldeak aktibatzen du.

### Channel
- **Taula:** `channels`
- **Klasea:** `Channel`
- **Gako-eremuak:** name, description, channel_type, max_members, created_by (FK), is_active
- **Errelazioak:** User-i (sortzailea) dagokio, ChannelMembers ditu, Messages ditu

### Committee
- **Taula:** `committees`
- **Klasea:** `Committee`
- **Gako-eremuak:** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Errelazioak:** Festival-i, Role-i dagokio, CommitteeMembers ditu

### Event
- **Taula:** `events`
- **Klasea:** `Event`
- **Gako-eremuak:** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Errelazioak:** Festival-i, User-i (sortzailea) dagokio, EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings ditu

### Notification
- **Taula:** `notifications`
- **Klasea:** `Notification`
- **Gako-eremuak:** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Errelazioak:** User-i (hartzailea), User-i (erlazionatua) dagokio

### ParticipantTag
- **Taula:** `participant_tags`
- **Klasea:** `ParticipantTag`
- **Gako-eremuak:** name, display_name, description, category, is_global, is_active, sort_order
- **Errelazioak:** UserParticipantTags ditu, FestivalParticipantTags ditu

### Post
- **Taula:** `posts`
- **Klasea:** `Post`
- **Gako-eremuak:** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Errelazioak:** User-i (autorea), User-i (horma), Festival-i (horma) dagokio, erantzunak (Post) ditu, Post-i (gurasoa) dagokio
- **Oharrak:** Garapen aktiboko funtzioa.

### Registration
- **Taula:** `registration_forms`
- **Klasea:** `RegistrationForm`
- **Gako-eremuak:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Errelazioak:** Festival-i dagokio, RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations ditu

### Role
- **Taula:** `roles`
- **Klasea:** `Role`
- **Gako-eremuak:** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Errelazioak:** Role-i (gurasoa), RoleGroup-i dagokio, UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts ditu

### UserAlias
- **Taula:** `user_aliases`
- **Klasea:** `UserAlias`
- **Gako-eremuak:** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Errelazioak:** User-i dagokio
- **Oharrak:** Testuinguru bakoitzeko ikusgai diren izenak onartzen ditu (global, festival, shortfilm, chat, public_profile, credits) ikusgarritasun-kontrolarekin

### UserKey
- **Taula:** `user_keys`
- **Klasea:** `UserKey`
- **Gako-eremuak:** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Errelazioak:** User-i dagokio
- **Oharrak:** E2EErako X25519 gako publikoa gordetzen du; erabiltzaile bakoitzeko gako aktibo bat

### UserSession
- **Taula:** `user_sessions`
- **Klasea:** `UserSession`
- **Gako-eremuak:** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Errelazioak:** User-i dagokio

### ValidationRule
- **Taula:** `validation_rules`
- **Klasea:** `ValidationRule`
- **Gako-eremuak:** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Errelazioak:** M2M ValidationRuleGroup-ekin `validation_rule_group_rules` bidez

### Payment
- **Taula:** `payments`
- **Klasea:** `Payment`
- **Gako-eremuak:** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Errelazioak:** Registration-i dagokio

### JuryVote
- **Taula:** `jury_votes`
- **Klasea:** `JuryVote`
- **Gako-eremuak:** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Errelazioak:** Festival-i, ShortFilm-i, User-i (epaimahaia) dagokio

### NodePolicy
- **Taula:** `node_policies`
- **Klasea:** `NodePolicy`
- **Gako-eremuak:** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Errelazioak:** Federazio-entitatea

### ModerationReport
- **Taula:** `moderation_reports`
- **Klasea:** `ModerationReport`
- **Gako-eremuak:** reporter_node, target_node, target_user_ref, reason, status
- **Errelazioak:** Federazio-entitatea

### IdentityRedirect
- **Taula:** `identity_redirects`
- **Klasea:** `IdentityRedirect`
- **Gako-eremuak:** old_ref (indize bakarra), new_ref, target_domain, created_at
- **Errelazioak:** Federazio-entitatea; identitate-migrazio baten ondoren erreferentzia zaharra ebazten du

### MigrationAudit
- **Taula:** `migration_audits`
- **Klasea:** `MigrationAudit`
- **Gako-eremuak:** entity_type, entity_id, action, source_domain, target_domain, details (JSON), created_at
- **Errelazioak:** Federazio-entitatea; jaialdi edo erabiltzaile bakoitzeko migrazioa jarraitzen du

### ChatOutbox
- **Taula:** `chat_outbox`
- **Klasea:** `ChatOutbox`
- **Gako-eremuak:** message_id (bakarrak), node_origin, subject, payload (JSON), signature, status, attempts, last_error, created_at
- **Errelazioak:** Txat federatuaren ilara iraunkorra (`DurableQueueBackend`); `message_id`-ren bakartasunak deduplikazioa ematen du eta `attempts`/`last_error` bidez birsaioak kudeatzen dira

### MessageReport
- **Taula:** `message_reports`
- **Klasea:** `MessageReport`
- **Gako-eremuak:** reporter_id (FK), message_id (FK), reason, status
- **Errelazioak:** User-i (salatzailea) eta Message-i dagokio

### ChatMute
- **Taula:** `chat_mutes`
- **Klasea:** `ChatMute`
- **Gako-eremuak:** user_id (FK), channel_id (FK), node_domain, until, reason
- **Errelazioak:** User-i eta Channel-i dagokio; isiltzea kanal bati edo federazio-nodo bati aplika dakioke

### Location
- **Taula:** `locations`
- **Klasea:** `Location`
- **Gako-eremuak:** name, description, latitude, longitude, address, is_active
- **Errelazioak:** Festival-i (M2M) dagokio, LocationImages, LocationTags, LocationRelations ditu

### EventScreening
- **Taula:** `event_screenings`
- **Klasea:** `EventScreening`
- **Gako-eremuak:** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Errelazioak:** Event-i, ShortFilm-i dagokio

### FestivalRulebook
- **Taula:** `festival_rulebooks`
- **Klasea:** `FestivalRulebook`
- **Gako-eremuak:** festival_id (FK), title, content, file_url, is_active
- **Errelazioak:** Festival-i dagokio

### FormDefinition
- **Taula:** `form_definitions`
- **Klasea:** `FormDefinition`
- **Gako-eremuak:** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Errelazioak:** Festival-i dagokio, FormPages, FormLinks, FormResponses ditu

### Group
- **Taula:** `groups`
- **Klasea:** `Group`
- **Gako-eremuak:** name, display_name, description, sort_order, is_active
- **Errelazioak:** RoleGroupMemberships, Roles ditu

### AppSetting
- **Taula:** `app_settings`
- **Klasea:** `AppSetting`
- **Gako-eremuak:** key, value, description, is_public
- **Errelazioak:** Konfigurazio-entitatea

### AuditLog
- **Taula:** `audit_logs`
- **Klasea:** `AuditLog`
- **Gako-eremuak:** actor_id (FK), action, target, ip, created_at
- **Errelazioak:** User-i (egilea) dagokio, append-only

### UserBlock
- **Taula:** `user_blocks`
- **Klasea:** `UserBlock`
- **Gako-eremuak:** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Errelazioak:** User-i (blokeatzailea), User-i (blokeatua) dagokio

### RoleDelegation
- **Taula:** `role_delegations`
- **Klasea:** `RoleDelegation`
- **Gako-eremuak:** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Errelazioak:** User-i (ordezkatzailea), User-i (ordezkatua), Role-i, Festival-i, User-i (errebokatzailea) dagokio

### RoleTransition
- **Taula:** `role_transitions`
- **Klasea:** `RoleTransition`
- **Gako-eremuak:** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Errelazioak:** User-i, Role-i (jatorria), Role-i (helmuga), Festival-i (jatorria), Festival-i (helmuga), User-i (aldaketaren arduraduna) dagokio

### EventTicketType
- **Taula:** `event_ticket_types`
- **Klasea:** `EventTicketType`
- **Gako-eremuak:** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Errelazioak:** Event-i dagokio

### EventSeat
- **Taula:** `event_seats`
- **Klasea:** `EventSeat`
- **Gako-eremuak:** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Errelazioak:** Event-i, EventTicketType-i dagokio

### EventReservation
- **Taula:** `event_reservations`
- **Klasea:** `EventReservation`
- **Gako-eremuak:** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Errelazioak:** Event-i, User-i (erreserbatzailea), User-i (sortzailea) dagokio

### EventAttendee
- **Taula:** `event_attendees`
- **Klasea:** `EventAttendee`
- **Gako-eremuak:** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Errelazioak:** Event-i, EventReservation-i, User-i, EventSeat-i, EventTicketType-i, User-i (gonbidatzailea) dagokio

## Datu-base-saioak

Datu-base-saioak `app/database.py`-n `get_db()` bidez kudeatzen dira:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Hau FastAPI mendekotasun gisa erabiltzen da endpoint-etatik datu-basea atzitzeko.

## SQLite-tik MariaDB-ra migrazio-oharrak

Eskema-aldaketak Alembic bidez kudeatzen dira (`backend/alembic/versions/`; `alembic upgrade head`). 42 berrikuspen daude eta head-a `c1d2e3f4a5b6` da; azken hirurek (`a9b0c1d2e3f4`, `b0c1d2e3f4a5`, `c1d2e3f4a5b6`) portabilitate-taulak, txat-ilara iraunkorra eta moderazioa gehitzen dituzte. Ekoizpenean soilik Alembic, inoiz ez `create_all`.

SQLite-tik MariaDB-ra migratzean:
- SQLite `INTEGER PRIMARY KEY` MariaDB `INT AUTO_INCREMENT`-ekin bat dator
- SQLite `TEXT` MariaDB `TEXT` edo `VARCHAR`-ekin bat dator
- SQLite `DATETIME` testu gisa gordetzen da; MariaDBk `DATETIME` natiboa erabiltzen du
- `export_sqlite_to_mariadb.py` eta `import_mariadb_to_sqlite.py` migrazio-script-ek moten bihurketa automatikoki kudeatzen dute
