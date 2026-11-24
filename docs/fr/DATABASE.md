# Documentation de la base de données

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Vue d'ensemble

Clakettes utilise une configuration à deux bases de données :
- **Développement** : SQLite (`clakettes.db`) — par défaut, aucune configuration requise
- **Production** : MariaDB — configurée via `DATABASE_URL` dans `backend/.env`

Des outils de migration sont disponibles pour synchroniser entre environnements :
- `python export_sqlite_to_mariadb.py` — Du développement à la production
- `python import_mariadb_to_sqlite.py` — De la production au développement

## Configurer MariaDB (production)

Par défaut Clakettes utilise SQLite (`clakettes.db`), qui ne requiert aucune configuration. Pour utiliser MariaDB :

1. Copiez `backend/.env.example` vers `backend/.env` et décommentez la ligne `DATABASE_URL` pour MariaDB :
   ```env
   DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db
   ```
2. Lancez le conteneur MariaDB :
   ```bash
   # Développement/local avec MariaDB
   docker compose --profile db up -d

   # Production complète (backend + frontend + MariaDB + nginx)
   docker compose --profile prod up -d
   ```
3. Exécutez les migrations (Alembic seulement, jamais `create_all` en production) :
   ```bash
   cd backend
   alembic upgrade head
   ```
   Ou avec les scripts du projet :
   ```bash
   start.* --migrate --mariadb
   ```
4. (Facultatif) Copiez les données de SQLite vers MariaDB :
   ```bash
   cd backend && python tools/export_sqlite_to_mariadb.py
   ```

Variables requises dans `backend/.env` lors de l'utilisation de MariaDB :

| Variable | Exemple | Notes |
|---|---|---|
| `DATABASE_URL` | `mariadb+pymysql://user:pass@host:3306/dbname` | Chaîne SQLAlchemy ; dans Docker Compose l'hôte est `db` |
| `SECRET_KEY` | `change-this-in-production` | Clé de signature JWT |
| `CORS_ORIGINS` | `https://votre-domaine.com` | Domaines explicites en production |
| `PUBLIC_BASE_URL` | `https://votre-domaine.com` | URL publique du nœud (fédération) |

Dans Docker Compose, le service `db` (MariaDB 11) est activé avec `--profile db` ou `--profile prod` ; le backend se connecte en utilisant `db` comme hôte et le port `3306`.

Notes importantes :
- MariaDB en production exige TLS : ajoutez `?ssl_ca=...` à `DATABASE_URL`.
- N'utilisez jamais `create_all` en production ; gérez le schéma uniquement avec Alembic (`alembic upgrade head`).
- Pour revenir de MariaDB à SQLite : `python tools/import_mariadb_to_sqlite.py`.

## Résumé des modèles

| Modèle | Table | Type |
|---|---|---|
| `AppSetting` | `app_settings` | Entité |
| `AuditLog` | `audit_logs` | Entité |
| `Award` | `awards` | Entité |
| `Badge` | `badges` | Entité |
| `Calendar` | `calendars` | Entité |
| `ChatMute` | `chat_mutes` | Entité (fédération) |
| `ChatOutbox` | `chat_outbox` | Entité (fédération) |
| `Channel` | `channels` | Entité |
| `Committee` | `committees` | Entité |
| `Event` | `events` | Entité |
| `EventScreening` | `event_screenings` | Entité |
| `Festival` | `festivals` | Entité |
| `FestivalLocation` | `festival_locations` | Entité |
| `FestivalRulebook` | `festival_rulebooks` | Entité |
| `FormDefinition` | `form_definitions` | Entité |
| `Group` | `groups` | Entité |
| `IdentityRedirect` | `identity_redirects` | Entité (fédération) |
| `JuryVote` | `jury_votes` | Entité |
| `MessageReport` | `message_reports` | Entité (fédération) |
| `MigrationAudit` | `migration_audits` | Entité (fédération) |
| `Location` | `locations` | Entité |
| `LocationImage` | `location_images` | Entité |
| `LocationRelation` | `location_relations` | Entité |
| `LocationTag` | `location_tags` | Entité |
| `Message` | `messages` | Entité |
| `ModerationReport` | `moderation_reports` | Entité |
| `NodePolicy` | `node_policies` | Entité |
| `Notification` | `notifications` | Entité |
| `ParticipantTag` | `participant_tags` | Entité |
| `Payment` | `payments` | Entité |
| `Post` | `posts` | Entité |
| `Registration` | `registration_forms` | Entité |
| `Role` | `roles` | Entité |
| `RoleDelegation` | `role_delegations` | Entité |
| `RoleGroup` | `role_groups` | Entité |
| `RoleTransition` | `role_transitions` | Entité |
| `ShortFilm` | `shortfilms` | Entité |
| `ShortFilmLocation` | `shortfilm_locations` | Entité |
| `TrustedNode` | `trusted_nodes` | Entité (fédération) |
| `User` | `users` | Entité |
| `UserAlias` | `user_aliases` | Entité |
| `UserBlock` | `user_blocks` | Entité |
| `UserFollow` | `user_follows` | Entité |
| `UserFestival` | `user_festival` | Association (Table) |
| `UserKey` | `user_keys` | Entité |
| `UserRole` | `user_roles` | Entité |
| `UserSession` | `user_sessions` | Entité |
| `ValidationRule` | `validation_rules` | Entité |
| `ValidationRuleGroup` | `validation_rule_groups` | Entité |

Tables d'association :
- `user_festival` — M2M entre `User` et `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` et `ValidationRule`

## Modèle de base

Tous les modèles héritent de `BaseModel` défini dans `app/models/base.py` :

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

Champs :
- `id` : Clé primaire, entier auto-incrémenté
- `created_at` : Horodatage attribué à la création
- `updated_at` : Horodatage mis à jour à chaque modification

## Modèles principaux

### Festival
- **Table :** `festivals`
- **Classe :** `Festival`
- **Champs clés :** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relations :** Possède de nombreux ShortFilms, Users (M2M via `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### User
- **Table :** `users`
- **Classe :** `User`
- **Champs clés :** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relations :** Possède de nombreux ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (créés), EventAttendees, EventReservations

### ShortFilm
- **Table :** `shortfilms`
- **Classe :** `ShortFilm`
- **Champs clés :** title, description, duration, video_url, thumbnail_url, festival_id (FK, obligatoire), contest_type (official_section|contest), user_id (FK), is_public, tags
- **Relations :** Appartient à Festival, appartient à User, possède de nombreux Awards, possède de nombreuses ShortFilmLocations. Le concours express (guerrilla) est `contest` ; la section officielle est `official_section` ; `festival_id` est obligatoire avec FK `RESTRICT` et indexé, et `contest_type` est également indexé (migration Alembic).

### Message
- **Table :** `messages`
- **Classe :** `Message`
- **Champs clés :** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relations :** Appartient à User (expéditeur), appartient à User (destinataire), appartient à Channel

### Association User-Festival
- **Table :** `user_festival`
- **Classe :** None (Table SQLAlchemy)
- **Champs clés :** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relations :** Pont M2M entre User et Festival ; PK composite sur (user_id, festival_id)

### Award
- **Table :** `awards`
- **Classe :** `Award`
- **Champs clés :** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relations :** Appartient à Festival, appartient à Event, appartient à ShortFilm, appartient à User (destinataire), appartient à User (vérificateur), appartient à User (créateur)

### Badge
- **Table :** `badges`
- **Classe :** `Badge`
- **Champs clés :** name, description, image_url (SVG préféré), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relations :** Appartient à Festival, possède de nombreuses BadgeAssignments
- **Notes :** Fonction en développement actif et désactivée par défaut (`badges.enabled`) ; seule l'équipe administrative l'active.

### Channel
- **Table :** `channels`
- **Classe :** `Channel`
- **Champs clés :** name, description, channel_type, max_members, created_by (FK), is_active
- **Relations :** Appartient à User (créateur), possède de nombreux ChannelMembers, possède de nombreux Messages

### Committee
- **Table :** `committees`
- **Classe :** `Committee`
- **Champs clés :** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relations :** Appartient à Festival, appartient à Role, possède de nombreux CommitteeMembers

### Event
- **Table :** `events`
- **Classe :** `Event`
- **Champs clés :** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relations :** Appartient à Festival, appartient à User (créateur), possède de nombreux EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Table :** `notifications`
- **Classe :** `Notification`
- **Champs clés :** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relations :** Appartient à User (destinataire), appartient à User (associé)

### ParticipantTag
- **Table :** `participant_tags`
- **Classe :** `ParticipantTag`
- **Champs clés :** name, display_name, description, category, is_global, is_active, sort_order
- **Relations :** Possède de nombreux UserParticipantTags, possède de nombreux FestivalParticipantTags

### Post
- **Table :** `posts`
- **Classe :** `Post`
- **Champs clés :** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relations :** Appartient à User (auteur), appartient à User (mur), appartient à Festival (mur), possède de nombreuses réponses (Post), appartient à Post (parent)
- **Notes :** Fonction en développement actif.

### Registration
- **Table :** `registration_forms`
- **Classe :** `RegistrationForm`
- **Champs clés :** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relations :** Appartient à Festival, possède de nombreux RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Role
- **Table :** `roles`
- **Classe :** `Role`
- **Champs clés :** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relations :** Appartient à Role (parent), appartient à RoleGroup, possède de nombreux UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### UserAlias
- **Table :** `user_aliases`
- **Classe :** `UserAlias`
- **Champs clés :** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relations :** Appartient à User
- **Notes :** Prend en charge les noms visibles par contexte (global, festival, shortfilm, chat, public_profile, credits) avec contrôle de visibilité

### UserKey
- **Table :** `user_keys`
- **Classe :** `UserKey`
- **Champs clés :** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relations :** Appartient à User
- **Notes :** Stocke la clé publique ECDH P-256 pour E2EE ; une clé active par utilisateur

### UserSession
- **Table :** `user_sessions`
- **Classe :** `UserSession`
- **Champs clés :** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relations :** Appartient à User

### ValidationRule
- **Table :** `validation_rules`
- **Classe :** `ValidationRule`
- **Champs clés :** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relations :** M2M avec ValidationRuleGroup via `validation_rule_group_rules`

### Payment
- **Table :** `payments`
- **Classe :** `Payment`
- **Champs clés :** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relations :** Appartient à Registration

### JuryVote
- **Table :** `jury_votes`
- **Classe :** `JuryVote`
- **Champs clés :** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relations :** Appartient à Festival, appartient à ShortFilm, appartient à User (juré)

### NodePolicy
- **Table :** `node_policies`
- **Classe :** `NodePolicy`
- **Champs clés :** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relations :** Entité de fédération

### ModerationReport
- **Table :** `moderation_reports`
- **Classe :** `ModerationReport`
- **Champs clés :** reporter_node, target_node, target_user_ref, reason, status
- **Relations :** Entité de fédération

### IdentityRedirect
- **Table :** `identity_redirects`
- **Classe :** `IdentityRedirect`
- **Champs clés :** old_ref (index unique), new_ref, target_domain, created_at
- **Relations :** Entité de fédération ; résout l'ancienne ref après une migration d'identité

### MigrationAudit
- **Table :** `migration_audits`
- **Classe :** `MigrationAudit`
- **Champs clés :** entity_type, entity_id, action, source_domain, target_domain, details (texte JSON), created_at
- **Relations :** Entité de fédération ; trace chaque migration de festival ou d'utilisateur

### ChatOutbox
- **Table :** `chat_outbox`
- **Classe :** `ChatOutbox`
- **Champs clés :** message_id (unique), node_origin, subject, payload (JSON), signature, status, attempts, last_error, created_at
- **Relations :** File durable du chat fédéré (`DurableQueueBackend`) ; l'unicité de `message_id` assure la déduplication et `attempts`/`last_error` gèrent les relances

### MessageReport
- **Table :** `message_reports`
- **Classe :** `MessageReport`
- **Champs clés :** reporter_id (FK), message_id (FK), reason, status
- **Relations :** Appartient à User (signalant) et à Message

### ChatMute
- **Table :** `chat_mutes`
- **Classe :** `ChatMute`
- **Champs clés :** user_id (FK), channel_id (FK), node_domain, until, reason
- **Relations :** Appartient à User et à Channel ; le mute peut s'appliquer à un canal ou à un nœud fédéré

### TrustedNode
- **Table :** `trusted_nodes`
- **Classe :** `TrustedNode`
- **Champs clés :** node_domain (unique, index), cert_fingerprint_sha256 (unique, index), allowed, revoked_at (DateTime, nullable), revocation_reason (Text, nullable), revoked_by (String(255), nullable)
- **Relations :** Entité de fédération ; `revoked_at`, `revocation_reason` et `revoked_by` enregistrent la révocation du nœud (migration Alembic)

### Location
- **Table :** `locations`
- **Classe :** `Location`
- **Champs clés :** name, description, latitude, longitude, address, is_active
- **Relations :** Appartient à Festival (M2M), possède de nombreux LocationImages, LocationTags, LocationRelations

### EventScreening
- **Table :** `event_screenings`
- **Classe :** `EventScreening`
- **Champs clés :** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relations :** Appartient à Event, appartient à ShortFilm

### FestivalRulebook
- **Table :** `festival_rulebooks`
- **Classe :** `FestivalRulebook`
- **Champs clés :** festival_id (FK), title, content, file_url, is_active
- **Relations :** Appartient à Festival

### FormDefinition
- **Table :** `form_definitions`
- **Classe :** `FormDefinition`
- **Champs clés :** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relations :** Appartient à Festival, possède de nombreux FormPages, FormLinks, FormResponses

### Group
- **Table :** `groups`
- **Classe :** `Group`
- **Champs clés :** name, display_name, description, sort_order, is_active
- **Relations :** Possède de nombreux RoleGroupMemberships, Roles

### AppSetting
- **Table :** `app_settings`
- **Classe :** `AppSetting`
- **Champs clés :** key, value, description, is_public
- **Relations :** Entité de configuration

### AuditLog
- **Table :** `audit_logs`
- **Classe :** `AuditLog`
- **Champs clés :** actor_id (FK), action, target, ip, created_at
- **Relations :** Appartient à User (acteur), append-only

### UserBlock
- **Table :** `user_blocks`
- **Classe :** `UserBlock`
- **Champs clés :** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relations :** Appartient à User (bloqueur), appartient à User (bloqué)

### UserFollow
- **Table :** `user_follows`
- **Classe :** `UserFollow`
- **Champs clés :** `follower_id` (FK), `followed_id` (FK), created_at, updated_at

### RoleDelegation
- **Table :** `role_delegations`
- **Classe :** `RoleDelegation`
- **Champs clés :** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relations :** Appartient à User (délégateur), appartient à User (délégué), appartient à Role, appartient à Festival, appartient à User (révocateur)

### RoleTransition
- **Table :** `role_transitions`
- **Classe :** `RoleTransition`
- **Champs clés :** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relations :** Appartient à User, appartient à Role (origine), appartient à Role (destination), appartient à Festival (origine), appartient à Festival (destination), appartient à User (responsable du changement)

### EventTicketType
- **Table :** `event_ticket_types`
- **Classe :** `EventTicketType`
- **Champs clés :** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relations :** Appartient à Event

### EventSeat
- **Table :** `event_seats`
- **Classe :** `EventSeat`
- **Champs clés :** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relations :** Appartient à Event, appartient à EventTicketType
- **Contrainte :** `UNIQUE (event_id, section, row_label, number)` → `uq_event_seat_location` (migration Alembic ; remplace le `Meta.unique_together` inopérant de SQLAlchemy)

### EventReservation
- **Table :** `event_reservations`
- **Classe :** `EventReservation`
- **Champs clés :** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relations :** Appartient à Event, appartient à User (réserveur), appartient à User (créateur)

### EventAttendee
- **Table :** `event_attendees`
- **Classe :** `EventAttendee`
- **Champs clés :** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relations :** Appartient à Event, appartient à EventReservation, appartient à User, appartient à EventSeat, appartient à EventTicketType, appartient à User (inviteur)

## Sessions de base de données

Les sessions de base de données sont gérées via `get_db()` dans `app/database.py` :

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Cela sert de dépendance FastAPI pour l'accès à la base de données depuis les endpoints.

## Notes de migration de SQLite vers MariaDB

Les changements de schéma sont gérés avec Alembic (`backend/alembic/versions/` ; `alembic upgrade head`). Les migrations ajoutent l'unicité du siège, les tables de portabilité, la file durable de chat, la modération, `contest_type` dans `shortfilms` avec index et `festival_id` obligatoire avec FK `RESTRICT`, ainsi que les métadonnées de révocation dans `trusted_nodes` (`revoked_at`, `revocation_reason`, `revoked_by`). En production, seulement Alembic, jamais `create_all`.
La table `user_follows` (paire unique `follower_id`, `followed_id`) est gérée avec Alembic.

Lors de la migration de SQLite vers MariaDB :
- SQLite `INTEGER PRIMARY KEY` correspond à MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` correspond à MariaDB `TEXT` ou `VARCHAR`
- SQLite `DATETIME` est stocké en texte ; MariaDB utilise `DATETIME` natif
- Les scripts de migration dans `export_sqlite_to_mariadb.py` et `import_mariadb_to_sqlite.py` gèrent automatiquement les conversions de types
