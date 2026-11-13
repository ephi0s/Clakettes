# Documentation de la base de données

[ES](../es/DATABASE.md) · [EN](../en/DATABASE.md) · [FR](DATABASE.md) · [DE](../de/DATABASE.md) · [IT](../it/DATABASE.md) · [CA](../ca/DATABASE.md) · [EU](../eu/DATABASE.md) · [GL](../gl/DATABASE.md) · [OC](../oc/DATABASE.md)

## Vue d'ensemble

Clakettes utilise une configuration à deux bases de données :
- **Développement** : SQLite (`clakettes.db`) — par défaut, aucune configuration requise
- **Production** : MariaDB — configuré via `DATABASE_URL` dans `backend/.env`

Des outils de migration sont disponibles pour synchroniser entre les environnements :
- `python export_sqlite_to_mariadb.py` — Développement vers production
- `python import_mariadb_to_sqlite.py` — Production vers développement

## Résumé des modèles

| Modèle | Table | Type |
|--------|-------|------|
| `AppSetting` | `app_settings` | Entité |
| `AuditLog` | `audit_logs` | Entité |
| `Award` | `awards` | Entité |
| `Badge` | `badges` | Entité |
| `Calendar` | `calendars` | Entité |
| `Channel` | `channels` | Entité |
| `Committee` | `committees` | Entité |
| `Event` | `events` | Entité |
| `EventScreening` | `event_screenings` | Entité |
| `Festival` | `festivals` | Entité |
| `FestivalLocation` | `festival_locations` | Entité |
| `FestivalRulebook` | `festival_rulebooks` | Entité |
| `FormDefinition` | `form_definitions` | Entité |
| `Group` | `groups` | Entité |
| `JuryVote` | `jury_votes` | Entité |
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
| `User` | `users` | Entité |
| `UserAlias` | `user_aliases` | Entité |
| `UserBlock` | `user_blocks` | Entité |
| `UserFestival` | `user_festival` | Association (Table) |
| `UserKey` | `user_keys` | Entité |
| `UserRole` | `user_roles` | Entité |
| `UserSession` | `user_sessions` | Entité |
| `ValidationRule` | `validation_rules` | Entité |
| `ValidationRuleGroup` | `validation_rule_groups` | Entité |

Tables d'association :
- `user_festival` — M2M entre `User` et `Festival`
- `validation_rule_group_rules` — M2M entre `ValidationRuleGroup` et `ValidationRule`

Total : 40 modèles d'entité + 2 tables d'association = 42 constructions SQLAlchemy.

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
- `created_at` : Horodatage assigné à la création
- `updated_at` : Horodatage mis à jour à chaque modification

## Modèles principaux

### Festival
- **Table :** `festivals`
- **Classe :** `Festival`
- **Champs clés :** name, description, location, latitude, longitude, is_active, website, logo_url, banner_url, tagline, social_links, allow_alias_display
- **Relations :** A plusieurs ShortFilms, Utilisateurs (M2M via `user_festival`), FestivalRoles, FestivalParticipantTags, UserRoles, UserParticipantTags, RegistrationForms, FestivalRegistrations, Events, Awards

### Utilisateur
- **Table :** `users`
- **Classe :** `User`
- **Champs clés :** username, email, password_hash, full_name, role, bio, avatar_url, banner_url, tagline, social_links, is_active, is_public, is_public_email, is_public_bio, is_public_location, latitude, longitude, dav_token_hash, dav_token_expires_at, privacy_policy_version, privacy_accepted_at
- **Relations :** A plusieurs ShortFilms, Festivals (M2M), UserRoles, UserParticipantTags, UserAliases, FestivalRegistrations, Sessions, Awards, Events (créés), EventAttendees, EventReservations

### Court-métrage
- **Table :** `shortfilms`
- **Classe :** `ShortFilm`
- **Champs clés :** title, description, duration, video_url, thumbnail_url, festival_id (FK), user_id (FK), is_public, tags
- **Relations :** Appartient à Festival, appartient à Utilisateur, a plusieurs Awards, a plusieurs ShortFilmLocations

### Message
- **Table :** `messages`
- **Classe :** `Message`
- **Champs clés :** content, sender_id (FK), receiver_id (FK), group_id, channel_id (FK), is_read, message_type, media_url, latitude, longitude, vcard_data, ical_data
- **Relations :** Appartient à Utilisateur (expéditeur), appartient à Utilisateur (destinataire), appartient à Channel

### Association Utilisateur-Festival
- **Table :** `user_festival`
- **Classe :** None (Table SQLAlchemy)
- **Champs clés :** user_id (FK, PK), festival_id (FK, PK), role, joined_at
- **Relations :** Pont M2M entre Utilisateur et Festival ; PK composite sur (user_id, festival_id)

### Récompense
- **Table :** `awards`
- **Classe :** `Award`
- **Champs clés :** festival_id (FK), event_id (FK), shortfilm_id (FK), user_id (FK), award_name, award_category, description, position, is_winner, prize_amount, currency, year, is_public, is_verified, verified_by (FK), created_by (FK)
- **Relations :** Appartient à Festival, appartient à Événement, appartient à Court-métrage, appartient à Utilisateur (destinataire), appartient à Utilisateur (vérificateur), appartient à Utilisateur (créateur)

### Insigne
- **Table :** `badges`
- **Classe :** `Badge`
- **Champs clés :** name, description, image_url (SVG préféré), scope (platform, festival), category (merit, veteran, popular, role, special), festival_id (FK), conditions (JSON), require_conditions, is_active, created_by (FK)
- **Relations :** Appartient à Festival, a plusieurs BadgeAssignments
- **Notes :** Fonction en développement actif et désactivée par défaut (`badges.enabled`) ; seule l'équipe administrative l'active.

### Canal
- **Table :** `channels`
- **Classe :** `Channel`
- **Champs clés :** name, description, channel_type, max_members, created_by (FK), is_active
- **Relations :** Appartient à Utilisateur (créateur), a plusieurs ChannelMembers, a plusieurs Messages

### Comité
- **Table :** `committees`
- **Classe :** `Committee`
- **Champs clés :** festival_id (FK), name, description, role_id (FK), is_active, max_members, external_visible
- **Relations :** Appartient à Festival, appartient à Role, a plusieurs CommitteeMembers

### Événement
- **Table :** `events`
- **Classe :** `Event`
- **Champs clés :** festival_id (FK), title, description, short_description, event_type, start_date, end_date, location, venue, venue_latitude, venue_longitude, has_external_page, external_url, internal_page_enabled, capacity, show_seat_map, is_public, is_active, image_url, color, created_by (FK), sort_order
- **Relations :** Appartient à Festival, appartient à Utilisateur (créateur), a plusieurs EventTicketTypes, EventSeats, EventReservations, EventAttendees, Awards, EventScreenings

### Notification
- **Table :** `notifications`
- **Classe :** `Notification`
- **Champs clés :** user_id (FK), title, message, notification_type, is_read, related_user_id (FK)
- **Relations :** Appartient à Utilisateur (destinataire), appartient à Utilisateur (lié)

### Tag de participant
- **Table :** `participant_tags`
- **Classe :** `ParticipantTag`
- **Champs clés :** name, display_name, description, category, is_global, is_active, sort_order
- **Relations :** A plusieurs UserParticipantTags, a plusieurs FestivalParticipantTags

### Publication
- **Table :** `posts`
- **Classe :** `Post`
- **Champs clés :** author_id (FK), target_user_id (FK), festival_id (FK), parent_post_id (FK), content (markdown), embed_url, embed_type, allow_replies, is_pinned, is_hidden
- **Relations :** Appartient à Utilisateur (auteur), appartient à Utilisateur (mur), appartient à Festival (mur), a plusieurs réponses (Post), appartient à Publication (parent)
- **Notes :** Fonction en développement actif.

### Inscription
- **Table :** `registration_forms`
- **Classe :** `RegistrationForm`
- **Champs clés :** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations, require_existing_account, allow_role_selection, allow_tag_selection, created_by (FK)
- **Relations :** Appartient à Festival, a plusieurs RegistrationFormSections, RegistrationFormLinks, FestivalRegistrations

### Rôle
- **Table :** `roles`
- **Classe :** `Role`
- **Champs clés :** name, display_name, description, scope, hierarchy_level, parent_role_id (FK), group_id (FK), is_assignable_by_admin, requires_approval, is_active, permissions
- **Relations :** Appartient à Role (parent), appartient à RoleGroup, a plusieurs UserRoles, FestivalRoles, RoleGroupMemberships, RoleDependencies, RoleConflicts

### Alias d'utilisateur
- **Table :** `user_aliases`
- **Classe :** `UserAlias`
- **Champs clés :** user_id (FK), alias, context, context_id, is_primary, is_public, show_awards, profile_token, visibility_scope, notes
- **Relations :** Appartient à Utilisateur
- **Notes :** Permet des noms visibles par contexte (global, festival, shortfilm, chat, public_profile, credits) avec contrôle de visibilité

### Clé utilisateur
- **Table :** `user_keys`
- **Classe :** `UserKey`
- **Champs clés :** user_id (FK, unique), public_key_x25519, key_identifier (unique), is_active, rotated_at
- **Relations :** Appartient à Utilisateur
- **Notes :** Stocke la clé publique X25519 pour l'E2EE ; une clé active par utilisateur

### Session utilisateur
- **Table :** `user_sessions`
- **Classe :** `UserSession`
- **Champs clés :** user_id (FK), token_hash, refresh_token_hash, device_name, ip_address, user_agent, last_used_at, expires_at, revoked_at, is_active
- **Relations :** Appartient à Utilisateur

### Règle de validation
- **Table :** `validation_rules`
- **Classe :** `ValidationRule`
- **Champs clés :** name, description, scope, scope_id, field_name, field_label, field_type, is_required, is_visible, is_editable_by_user, min_length, max_length, regex_pattern, allowed_values (JSON), default_value, help_text, display_order, depends_on_field, depends_on_value, error_message
- **Relations :** M2M avec ValidationRuleGroup via `validation_rule_group_rules`

### Paiement
- **Table :** `payments`
- **Classe :** `Payment`
- **Champs clés :** amount, currency, provider_ref, status, provider, registration_id (FK)
- **Relations :** Appartient à Registration

### Vote du jury
- **Table :** `jury_votes`
- **Classe :** `JuryVote`
- **Champs clés :** festival_id (FK), shortfilm_id (FK), user_id (FK), score, is_anonymous, comment
- **Relations :** Appartient à Festival, appartient à Court-métrage, appartient à Utilisateur (juré)

### Politique de nœud
- **Table :** `node_policies`
- **Classe :** `NodePolicy`
- **Champs clés :** node_id, allowlist, blocklist, rate_limit, minimize_data, consent_required, import_only
- **Relations :** Entité de fédération

### Rapport de modération
- **Table :** `moderation_reports`
- **Classe :** `ModerationReport`
- **Champs clés :** reporter_node, target_node, target_user_ref, reason, status
- **Relations :** Entité de fédération

### Localisation
- **Table :** `locations`
- **Classe :** `Location`
- **Champs clés :** name, description, latitude, longitude, address, is_active
- **Relations :** Appartient à Festival (M2M), a plusieurs LocationImages, LocationTags, LocationRelations

### Séance d'événement
- **Table :** `event_screenings`
- **Classe :** `EventScreening`
- **Champs clés :** event_id (FK), shortfilm_id (FK), start_date, end_date, venue, notes, status
- **Relations :** Appartient à Événement, appartient à Court-métrage

### Livre de règles du festival
- **Table :** `festival_rulebooks`
- **Classe :** `FestivalRulebook`
- **Champs clés :** festival_id (FK), title, content, file_url, is_active
- **Relations :** Appartient à Festival

### Définition de formulaire
- **Table :** `form_definitions`
- **Classe :** `FormDefinition`
- **Champs clés :** festival_id (FK), title, description, is_active, starts_at, ends_at, max_registrations
- **Relations :** Appartient à Festival, a plusieurs FormPages, FormLinks, FormResponses

### Groupe
- **Table :** `groups`
- **Classe :** `Group`
- **Champs clés :** name, display_name, description, sort_order, is_active
- **Relations :** A plusieurs RoleGroupMemberships, Roles

### Réglage d'application
- **Table :** `app_settings`
- **Classe :** `AppSetting`
- **Champs clés :** key, value, description, is_public
- **Relations :** Entité de configuration

### Journal d'audit
- **Table :** `audit_logs`
- **Classe :** `AuditLog`
- **Champs clés :** actor_id (FK), action, target, ip, created_at
- **Relations :** Appartient à Utilisateur (acteur), append-only

### Blocage utilisateur
- **Table :** `user_blocks`
- **Classe :** `UserBlock`
- **Champs clés :** blocker_id (FK), blocked_id (FK), reason, starts_at, expires_at
- **Relations :** Appartient à Utilisateur (bloqueur), appartient à Utilisateur (bloqué)

### Délégation de rôle
- **Table :** `role_delegations`
- **Classe :** `RoleDelegation`
- **Champs clés :** delegator_id (FK), delegate_id (FK), role_id (FK), festival_id (FK), status, starts_at, expires_at, reason, scope_limitations, revoked_by (FK), revoked_at, revoked_reason
- **Relations :** Appartient à Utilisateur (délégateur), appartient à Utilisateur (délégué), appartient à Role, appartient à Festival, appartient à Utilisateur (révocateur)

### Transition de rôle
- **Table :** `role_transitions`
- **Classe :** `RoleTransition`
- **Champs clés :** user_id (FK), from_role_id (FK), to_role_id (FK), from_festival_id (FK), to_festival_id (FK), transition_type, changed_by (FK), reason, transitioned_at
- **Relations :** Appartient à Utilisateur, appartient à Role (origine), appartient à Role (destination), appartient à Festival (origine), appartient à Festival (destination), appartient à Utilisateur (responsable du changement)

### Type de billet d'événement
- **Table :** `event_ticket_types`
- **Classe :** `EventTicketType`
- **Champs clés :** event_id (FK), name, description, price, currency, capacity, sold_count, reserved_count, assigned_count, is_active, is_hidden, sort_order, color
- **Relations :** Appartient à Événement

### Siège d'événement
- **Table :** `event_seats`
- **Classe :** `EventSeat`
- **Champs clés :** event_id (FK), ticket_type_id (FK), section, row_label, number, label, status, x_position, y_position, is_accessible, notes
- **Relations :** Appartient à Événement, appartient à EventTicketType

### Réservation d'événement
- **Table :** `event_reservations`
- **Classe :** `EventReservation`
- **Champs clés :** event_id (FK), user_id (FK), status, total_quantity, notes, created_by (FK), is_hidden, confirmed_at, cancelled_at
- **Relations :** Appartient à Événement, appartient à Utilisateur (réservateur), appartient à Utilisateur (créateur)

### Participant à l'événement
- **Table :** `event_attendees`
- **Classe :** `EventAttendee`
- **Champs clés :** event_id (FK), reservation_id (FK), user_id (FK), seat_id (FK), ticket_type_id (FK), status, invited_by (FK), is_guest, is_hidden, guest_name, guest_email, guest_phone, checked_in_at, notes
- **Relations :** Appartient à Événement, appartient à EventReservation, appartient à Utilisateur, appartient à EventSeat, appartient à EventTicketType, appartient à Utilisateur (inviteur)

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

Ceci est utilisé comme dépendance FastAPI pour l'accès à la base de données depuis les endpoints.

## Notes de migration de SQLite vers MariaDB

Les changements de schéma sont gérés avec Alembic (`backend/alembic/versions/`, 36 versions ; `alembic upgrade head`). En production seulement Alembic, jamais `create_all`.

Lors de la migration de SQLite vers MariaDB :
- SQLite `INTEGER PRIMARY KEY` correspond à MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` correspond à MariaDB `TEXT` ou `VARCHAR`
- SQLite `DATETIME` est stocké en texte ; MariaDB utilise `DATETIME` natif
- Les scripts de migration dans `export_sqlite_to_mariadb.py` et `import_mariadb_to_sqlite.py` gèrent les conversions de types automatiquement