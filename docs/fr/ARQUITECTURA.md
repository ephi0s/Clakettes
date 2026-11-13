# Architecture — Clakettes

[ES](../es/ARQUITECTURA.md) · [EN](../en/ARQUITECTURA.md) · [FR](ARQUITECTURA.md) · [DE](../de/ARQUITECTURA.md) · [IT](../it/ARQUITECTURA.md) · [CA](../ca/ARQUITECTURA.md) · [EU](../eu/ARQUITECTURA.md) · [GL](../gl/ARQUITECTURA.md) · [OC](../oc/ARQUITECTURA.md)

## Carte

```
Flutter (web/bureau/Android/iOS) ──HTTPS──► FastAPI ──► SQLite (dev) / MariaDB (prod)
  offline-first (Hive)                    JWT 30 min + refresh 30 d
                                          rate limit 100/60s (?page=&size=)
```

Ports (Docker) : backend `8000`, frontend `3000` (dev) / `80` (prod), MariaDB `3306`.

## Backend (`backend/`, détail dans [BACKEND.md](BACKEND.md) et [DATABASE.md](DATABASE.md))

Couches : Routers → Services → Models, types via `app.enums`.

| Pièce | Où | Règle |
|---|---|---|
| CRUD + `paginate` (size≤100) + `paginate_filtered` | `services/base_service.py` | Les routers ne consultent pas ; les services ne lèvent pas 404 (sauf 3 hérités) |
| 404 uniforme | `routers/dependencies.py:get_or_404` | fetch → 404 en une ligne |
| Auth | `app/auth.py:validate_access_token` | Signature + `type=access` + session active/non révoquée/non expirée ; `last_used_at` lazy (5 min) |
| Auth optionnel | `routers/dependencies.py:get_current_user_optional` | Endpoints publics sans 401 |
| Permissions | `routers/permissions.py` | `require_festival_admin`, `require_channel_admin/member`, `require_form_admin`, `can_manage_*` |
| Rate limit | `RateLimitMiddleware` + `RateLimiter` (SQLite, buckets `middleware:`/`dav:` ; instances dans `main`/`admin`/`auth`) | Désactivé avec `TESTING=true` |
| Chat temps réel | `app/chat_backend/` (WebSocket) + REST dans `routers/chat.py` | WS valide session via `validate_access_token` |
| CalDAV | `app/dav/` + `routers/dav.py` (préfixe `/dav`, bucket propre 600/60s) | Token bearer dans l'URL ; TLS obligatoire en prod |
| Export | `services/export_service.py` | CSV/ICS en stdlib ; PDF avec reportlab en import paresseux |
| Migrations | `alembic/` (36 versions) | Prod seulement Alembic ; dev aussi `create_all` |
| Fédération | `routers/federation.py`, `services/jwks_service.py`, `services/node_policy_service.py` | manifest, répertoire, nœuds, rapports, webfinger, ref users |

Comptes réels (vérifiés sur disque) :

| Composant | Fichiers | Note |
|---|---|---|
| Routers | 40 (38 avec `APIRouter`) | `dependencies.py` et `permissions.py` sont des helpers sans router |
| Services | 43 | + `__init__.py` |
| Modèles d'entité | 40 | + `base.py` et `__init__.py` |
| Schémas | 37 | |
| Migrations Alembic | 36 | + `__init__.py` |
| Fichiers de test | 47 | `test_*.py` |
| Lignes `def test_` | 1439 | |

## Frontend (`frontend/`)

Services singleton + `setState()` + Streams (sans Provider). Démarrage dans `main()` :
`DatabaseService` → `OfflineCache` → `SyncQueue` → `ConnectivityMonitor` → `LocaleService` → `NotificationService`.

| Pièce | Où | Règle |
|---|---|---|
| API | `services/api_service.dart` (noyau) + `services/api/` (9 domaines) | Base `BACKEND_URL` (sauvegardée > dart-define > défaut par plateforme ; émulateur Android `10.0.2.2`) |
| Hors ligne | `offline_cache_service.dart` (Hive) + `sync_queue_service.dart` (FIFO, retry 3 + backoff, anti-renvoi) | À la reconnexion, sync avec confirmation |
| Chat | `screens/chat_screen.dart` + `widgets/chat_bubble.dart` + `widgets/chat_input_bar.dart` | WS en direct, REST pour l'historique ; E2EE ECDH P-256 + AES-GCM dans les isolats |
| Notifications | `notification_service.dart` | Bureau : plugin OS ; web : Notification API ; mobile : no-op (voir [PUSH.md](PUSH.md)) |
| Navigation | `main_scaffold.dart` | Rail >800px, Bar <800px, Drawer toujours ; 10 écrans mis en cache |
| i18n | `l10n/` + `assets/l10n/` (9 locales) | `en.arb` est le fallback ; 0 clés manquantes (vérifié avec script) |
| Permissions OS | `AndroidManifest.xml` / `Info.plist` | Réseau, localisation, caméra, photothèque, alarmes exactes |

Comptes réels (vérifiés sur disque) :

| Composant | Fichiers | Note |
|---|---|---|
| Widgets réutilisables | 32 | dans `lib/widgets/` |
| Écrans | 36 | dans `lib/screens/` |
| Fichiers de test | 75 | `*_test.dart` dans `test/` et sous-dossiers |

## Flux clés

1. **Réservation** : festival → événement → sièges en bloc (1 commit) → réservation → occupation (épinglé dans `tests/integration/test_flows.py`).
2. **Message** : canal → membre → DM → lecture → suppression (seul l'expéditeur/admin).
3. **Délégation** : créer → lister les actives → révoquer (seul le délégué/admin).
4. **Inscription publique** : lien avec token → formulaire sans auth → approbation.