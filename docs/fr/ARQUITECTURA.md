# Architecture — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Carte

```
Flutter (web/Desktop/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                           rate limit 100/60s (?page=&size=)
```

Ports (Docker) : backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, détail dans [BACKEND.md](BACKEND.md) et [DATABASE.md](DATABASE.md))

Couches : Routers → Services → Models, types via `app.enums`.

| Élément | Où | Règle |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Les routers ne requêtent pas ; les services ne lèvent pas de 404 (sauf 3 hérités) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 en une ligne |
| Auth | `app/auth.py:validate_access_token` | Signature + `type=access` + session active/non révoquée/non expirée ; helpers `hash_token()`, `is_expired()` (naive = UTC), `get_user_with_roles()` et `touch_session()` (`last_used_at` paresseux, 5 min) |
| Auth optionnelle | `routers/dependencies.py:get_current_user_optional` | Endpoints publics sans 401 |
| Permissions | `routers/permissions.py` | `require_admin(user, db)` unifié (rôle legacy `admin` ou `UserRole` `ACTIVE`/`APPROVED`), `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*`, `require_self_or_admin` (alias) et `require_owner_or_admin` (blocages) |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, buckets `middleware:`/`dav:` ; instances dans `main`/`admin`/`auth`/`auth_sessions`/`federation`) | 100/60 s global, 600/60 s `/dav`, 5/300 s login, 20/60 s refresh, 3/300 s reset, federation 60/60 s ; bypass centralisé dans `app.config.is_testing()` (`1/true/yes/on`) |
| Chat temps réel | `app/chat_backend/` (WebSocket) + REST dans `routers/chat.py` | Le WS valide la session via `validate_access_token` |
| Chat fédéré | `routers/federation_chat_bridge.py`, `services/message_queue_service.py` (`chat_outbox`), `chat_backend/durable_queue_backend.py` (`DurableQueueBackend`), `services/message_federation_service.py` | Bridge signé RS256, dédup par `message_id`, tri par `timestamp`, transport interchangeable |
| Modération du chat | `routers/chat_moderation.py`, `services/chat_moderation_service.py`, `services/chat_rate_limit_service.py` | Signalements, mutes, filtre de mots, `disable_chat` et 10 messages/60 s par nœud et utilisateur (off avec `TESTING` ∈ {1,true,yes,on}) |
| Bus d'événements | `routers/federation_events.py`, `services/event_bus_service.py` | SSE avec `since`, battement et replay (200) ; publication signée et 3 relances (300 ms → 1,5 s → 5 s) |
| CalDAV | `app/dav/` + `routers/dav.py` (préfixe `/dav`, bucket propre 600/60s) | Token bearer dans l'URL ; TLS obligatoire en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib ; PDF avec reportlab en import paresseux |
| Migrations | `alembic/` (45 versions, head `d1e2f3a4b5c6`) | Prod seulement Alembic ; dev aussi `create_all` |
| Fédération | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py`, `services/node_peering_service.py`, `services/federation_token_service.py`, `app/mtls.py` | manifeste signé RSA-SHA256, répertoire, nœuds, signalements, webfinger, users ref, JWKS, `whoami`, token fédéré, peers/verify, peers/revoke, mTLS par CN/PEM |
| Portabilité | `routers/federation_portability.py`, `services/portability_service.py`, modèles `identity_redirect`/`migration_audit` | Bundles signés, imports, migration de festivals/utilisateurs et redirects |
| Résilience | `routers/federation_resilience.py`, `services/federation_metrics_service.py` | Health, heartbeat, métriques p50/p95, révocation de clés et plan d'incident |
| Conformité | `tools/federation_conformance.py`, `services/federation_conformance_service.py` | CLI qui vérifie manifeste, JWKS, token, répertoire, portabilité, bridge et SSE |

API générée : `python tools/gen_api.py --all` produit 446 endpoints dans 43 routers (39 avec préfixe dans `main.py` ; le générateur combine en outre le préfixe de chaque `APIRouter` et détecte les dépendances d'auth, voir [API.md](API.md)).

## Frontend (`frontend/`)

Services singleton + `setState()` + Streams (pas de Provider). Démarrage dans `main()` :
`DatabaseService` → `OfflineCache` → `SyncQueue` → `NodeService` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Élément | Où | Règle |
|---|---|---|
| API | `services/api_service.dart` (noyau) + `services/api/` (13 domaines, scission implémentée, voir leur README) | Base `BACKEND_URL` (enregistrée > dart-define > défaut par plateforme ; émulateur Android `10.0.2.2`) ; `resolveMediaUrl()` préfixe le nœud actif sur `/uploads/...` ; `uploadFile()` utilise le MIME par extension, Bearer, retry 401/refresh et bascule entre nœuds ; le WS du chat dérive son URL du même `rootUrl` |
| Offline | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-renvoi) | Cache étiqueté par nœud (`putWithOrigin`, `getOrigin`, `getEnvelope`, `listOrigins`, `clearOrigin`, `reconcile`) ; `ConnectivityMonitor` expose `NodeHealth`, `nodeHealth`, `offlineNodeCount`, `isDegraded` et les sondes `ApiService.testNode()` ; à la reconnexion, sync avec confirmation |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en direct, REST pour l'historique et l'historique fédéré ; E2EE ECDH P-256 + AES-GCM dans des isolates ; `ChatPresenceBackend` fournit l'indicateur de frappe, la latence et les accusés de lecture ; recherche locale, dédup et tri par `(created_at,id)` ; messages hors ligne mis en file de façon durable avec le même `message_id` |
| Avis | `notification_service.dart` | Bureau : plugin OS ; web : Notification API ; mobile : no-op (voir [PUSH.md](PUSH.md)) |
| Navigation | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer toujours ; 11 écrans mis en cache ; `DegradedNodesBanner` avertit des nœuds sans réponse avec le décompte et une relance (`checkNow()`) |
| i18n | `l10n/` + `assets/l10n/` (9 locales, 823 clés par ARB) | `app_en.arb` est le fallback ; parité des clés et des placeholders dans `test/l10n/arb_parity_test.dart` (référence `es`) ; `LocaleService.load()` détecte le locale du système et persiste le résolu |
| Permissions OS | `AndroidManifest.xml` / `Info.plist` | Réseau, localisation, caméra, photothèque, alarmes exactes |

## Flux clés

1. **Réservation** : festival → événement → sièges en lot (1 commit) → réservation → occupation (pin dans `tests/integration/test_flows.py`).
2. **Message** : canal → membre → DM → lecture → suppression (seulement expéditeur/admin).
3. **Délégation** : créer → lister actives → révoquer (seulement délégateur/admin).
4. **Inscription publique** : lien avec token → formulaire sans auth → approbation.
5. **Portabilité** : bundle signé → import avec politique d'origine → migration de festival/utilisateur → redirect de l'ancienne ref.
6. **Chat fédéré** : enveloppe signée → vérification de signature et dédup → persistance dans `chat_outbox` → diffusion et tri par `timestamp`.
7. **Événements** : publication sur le bus → SSE avec `since` et battement → relance avec backoff si le pair échoue.
8. **Courts dans un festival** : ajout dans `/api/festivals/{id}/shortfilms` avec `contest_type` (`official_section` par défaut ou `contest`) → `FestivalDetailResponse` avec compte et résumé → filtre dans l'app → projections uniquement avec les courts du même festival.
9. **Médias** : upload multipart → chemin relatif `/uploads/...` (MIME par magic bytes, métadonnées nettoyées) → `resolveMediaUrl()` le résout contre le nœud actif → cache Hive par nœud.
