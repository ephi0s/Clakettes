# Audit de code — Clakettes (rev. 10/10/2026, ampl. multiplateforme 09/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

> **Addendum 11/10/2026** (chiffres vérifiés) : backend 1439 `def test_` dans 47 fichiers ; routeurs 40 fichiers (38 avec `APIRouter`) ; services 43 ; modèles 40 ; schémas 37 ; migrations Alembic 36 versions ; `docs/fr/API.md` 339 endpoints dans 38 routeurs (operationIds uniques). RGPD : vie privée par défaut, consentement, suppression/exportation, purge des sessions, audit append-only, nettoyage des métadonnées, TLS MariaDB en prod, DAV avec expiration, CSP/HSTS. Fournisseurs de paiement mock/stripe/redsys.

## 0. Résumé exécutif (10/10/2026, chiffres vérifiés)

| Domaine | État | Détail |
| --- | --- | --- |
| Tests backend | 1439 `def test_` dans 47 fichiers | `Get-ChildItem backend/tests -Recurse -Filter "test_*.py" \| Select-String "def test_"` |
| Tests frontend | 75 fichiers `*_test.dart` | `Get-ChildItem frontend/test -Recurse -Filter "*_test.dart"` |
| Routeurs/Services/Modèles/Schémas | 40/43/40/37 fichiers (38 routeurs avec `APIRouter`) | `dependencies.py`/`permissions.py` sont des helpers sans routeur ; `base.py`/`__init__.py` ne sont pas des entités |
| Migrations | 36 versions | `alembic/versions/` |
| Endpoints | 339 dans 38 routeurs (`docs/fr/API.md` via AST) | `python tools/gen_api.py` idempotent ; simple grep donne ~290 (ne compte pas `propfind/report/options/websocket`) |
| Lint | `ruff check` + `ruff format --check` propres | `AGENTS.md` et CI (GH + GitLab) avec porte de formatage |
| Docs | Backend consolidé dans `docs/` | `docs/fr/BACKEND.md` + `docs/fr/DATABASE.md` ; index dans `docs/fr/README.md` |
| Dette principale | `get_or_404` partiel, `paginate_filtered` sans utilisations, `python-jose` non migré, 24 `AlertDialog` / 115 `ScaffoldMessenger` restants | Voir §5 avec comptages et vérification |

Comment revérifier : `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` et `cd frontend; flutter analyze; flutter test`.

## 1. Dépendances externes : ce qui peut être supprimé et ce qui ne peut pas

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dépendance | Verdict | Motif |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Conserver | Noyau de la pile |
| python-jose[cryptography] | Conserver pour l'instant, migrer vers PyJWT à l'avenir | Abandonné depuis 2016, mais le changement touche `app/auth.py` + `routers/dependencies.py` + tests ; à faire dans une PR séparée avec tests de tokens |
| python-dotenv | Conserver | Requis par `pydantic-settings>=2` et `uvicorn[standard]` (`--env-file`) ; seulement 2 scripts l'importent directement, mais le supprimer casserait le chargement de `.env` |
| pymysql | Conserver comme pilote prod | Utilisé seulement avec MariaDB ; ne pas le charger en dev n'économise rien (import paresseux déjà dans SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Conserver | Uploads, validation email, hashage des mots de passe |
| reportlab 5.1.0 | Conserver, mais avec import paresseux (fait) | Seulement `export_service._build_pdf` ; auparavant importé au niveau du module (~200 ms + mémoire par travailleur). Maintenant importé à l'intérieur de la fonction. De plus `pyproject.toml` synchronisé (manquait) et épinglé `==5.1.0` |

### Frontend (`frontend/pubspec.yaml`)

Toutes les dépendances sont en usage réel ; aucune n'a pu être supprimée sans casser une fonctionnalité :

- `archive` : utilisé dans `crypto_utils.dart` (ZLib/GZip). `dart:io` ne convient pas car il casse le web.
- `path_provider` : utilisé dans `file_downloader_io.dart` (mobile/bureau).
- `web` : utilisé dans `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid` : E2EE du chat (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher` : cartes.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker` : chacun avec 1-2 utilisations, mais les supprimer enlèverait des fonctionnalités.

## 2. Optimisations appliquées

1. `export_service.py` : import reportlab paresseux dans `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` : 3 instances `RateLimiter` (seaux `middleware:`/`dav:` + limiteurs pour `reset` 3/300s et `login`) ; ne pas unifier sans perdre des limites distinctes.
3. `base_service.py` : `paginate` fixe `page>=1`, `size` dans `[1,100]` ; nouveau `paginate_filtered()` défini avec 0 utilisations (en attente de migration des `get_all_paginated` clonés).
4. `routers/dependencies.py` : `get_current_user_optional` réutilise `validate_access_token` (élimine ~30 lignes JWT+session dupliquées) ; fix `__import__("datetime")` → import normal ; nouveau `get_or_404()` pour remplacer ~100 `HTTPException(404)` inline.
5. `dav/auth.py` : documenté la relation avec `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` synchronisés (reportlab).
7. `reusable_widgets.dart` : nouveau `showAppSnack()` (1 définition + 8 utilisations ; 115 `ScaffoldMessenger` directs restent).

## 3. Améliorations multiplateforme appliquées (bureau + web + Android + iOS/iPad)

1. `BackendConfig` : défaut par plateforme — émulateur Android utilise `10.0.2.2:8000` (localhost de l'émulateur est le virtuel lui-même, pas l'hôte) ; reste `localhost:8000`. Priorité : URL sauvegardée > `--dart-define=BACKEND_URL` > défaut par plateforme. `ApiService` utilise le même défaut dans le constructeur et les getters.
2. `NotificationService` : sur web (`kIsWeb`) `init` ne touche pas au plugin ni au fuseau horaire (pas de notifications locales dans le navigateur) et `scheduleReminder` ne fait rien ; documenté dans la docstring. Aucune branche par plateforme sur les écrans.
3. `file_downloader.dart` : import conditionnel vérifié (`web` par défaut, `io` si `dart.library.io`) — couvre navigateur, bureau, Android et iOS sans changements.
4. `main_scaffold.dart` : ajout des Courts à la navigation (l'écran `screenIndex 3` existait mais sans élément — inaccessible). Rail >800px (bureau/web), Bar <800px (mobile), Drawer sur tous.
5. `AndroidManifest.xml` : ajout INTERNET, ACCESS_NETWORK_STATE, localisation (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM. Sans INTERNET explicite les builds release n'ont pas de réseau.
6. `ios/Runner/Info.plist` : ajout NSLocationWhenInUse, NSCamera, NSPhotoLibrary (+Add). Sans ces éléments le système refuse ou l'App Store rejette.
7. Backend `routers/festivals.py` : pilote `get_or_404(db, Festival/Location, ...)` — 9 blocs `if not → 404` supprimés ; étendu à `shortfilms.py` (3) et `users.py` (4). Motif à étendre au reste des routeurs.
8. Frontend `awards_screen.dart` : erreur SnackBar migrée vers `showAppSnack()` (pilote). Note : les 24 `AlertDialog` restants sont des dialogues de *formulaire* (créer/éditer), pas de confirmation — ils ne migrent pas vers `showConfirmDialog` (19 utilisations dans 18 écrans) ; nécessiteraient un `CreateEntityDialog` commun.
9. CI : porte `ruff format --check` ajoutée (GH + GitLab) après vérification de `216 files already formatted`.
10. Sécurité (pilote `channels.py`, bloc sécurité) : nouveau `require_channel_member`/`is_channel_member` dans `permissions.py` et utilisation dans `channels.py` + `chat.py` (élimine 3 blocs inline avec imports différés) ; `channels.py` migré vers `get_or_404` (7 blocs de moins) ; liste blanche de rôle `Literal[admin,moderator,member]` dans les schémas (avant : chaîne libre → 500 par CheckConstraint ; maintenant : 422) ; 4 nouveaux tests 403/422 dans `TestChannelAuthorization`.
11. Sécurité : `POST /delegations/{id}/revoke` exigeait seulement l'auth — n'importe qui pouvait révoquer les délégations d'autrui. Maintenant vérifie le délégateur ou admin + test 403. Vérifiés déjà OK (sans changements) : `user_roles`/`user_festival` (liste blanche attendee), DMs (propriété), formulaires publics (auth optionnel), WS (valide la session), `bulk_create` (single commit), SyncQueue (retry+backoff), i18n (0 clés manquantes), `locations` (didChangeDependencies avec garde).
12. `get_or_404` étendu à `committees.py` (10), `events.py` (58, via script avec révision + 17 affectations non assignées pour éviter F841), `delegations` (2) et 5 routeurs de localisations (12). Pas de changement de schéma : pas de migration Alembic en attente pour ce lot.
13. Performance : filtre `venue` de la programmation abaissé à SQL (avant il filtrait la page en Python et cassait `total`/`pages`).
14. Frontend : gardes anti-double-envoi sur création festival/utilisateur/court-métrage + 3 SnackBars migrés vers `showAppSnack`.
15. Chat : E2EE hors du fil UI — `_prepareContent`/`_unpackContent` utilisent `encryptAsync`/`decryptAsync` (isolats) ; nouveaux `encryptSenderKeyAsync`/`decryptSenderKeyAsync` utilisés dans la diffusion et la réception des clés de l'expéditeur. `RestChatBackend` est conservé : utilisé par `chat_service_test` comme faux (n'était pas du code mort).
16. Chat : `chat_screen.dart` 1038 → 709 lignes ; bulles vers `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` avec image, localisation, vCard, iCal) et barre vers `widgets/chat_input_bar.dart` (`ChatInputBar`). 2 nouveaux tests async dans `crypto_utils_test`.
17. `locations_screen` 1144 → 645 lignes : cartes et formulaire vers `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`, `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`) ; suppression avec `showConfirmDialog` + `showAppSnack` (un `AlertDialog` de moins).
18. `festival_profile_screen` 1276 → 1173 lignes : `RulebooksSection` et `FestivalLocationsSection` (+ carte et fiches) vers `widgets/festival_sections.dart`. L'écran conserve l'état, la lecture, l'édition et les callbacks.
19. `api_service.dart` 1134 → 464 lignes : 95 méthodes déplacées vers `lib/services/api/` (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13, reste vers `user_api` + `calendar/channel/festival/form`). Le cœur conserve config, auth, transport et admin/recherche. API publique intacte.
20. `user_profile_screen` 996 → 1391 lignes : `SessionsCard` et `AliasesCard` vers `widgets/user_profile_cards.dart`. Corrigés 4 `if` sans accolades hérités dans `catalog_api`.
21. Tests de flux (`tests/integration/test_flows.py`) : réservation complète (festival → événement → sièges → réservation → occupation), messagerie (canal → membre → DM → lecture → suppression) et délégation (créer → lister → révoquer).
22. Tests de widgets des widgets extraits (13) : `chat_bubble`, `chat_input_bar`, `user_profile_cards`, `location_cards`. Note : les widgets sous `wrapWithLocalization` nécessitent un `pump()` supplémentaire (le Builder de localisation résout dans la deuxième frame).
23. Push natif sans Firebase (`docs/fr/PUSH.md`) : Notification API du navigateur sur web (`notification_web.dart` + stub avec export conditionnel, sans nouvelles dépendances), `flutter_local_notifications` sur bureau + permission macOS au démarrage, mobile en no-op explicite (`_supported`). `flutter build web` vérifié.
24. Documentation : `docs/fr/API.md` (339 endpoints dans 38 routeurs, générée par AST avec `tools/gen_api.py` — régénérable), `docs/fr/ARQUITECTURA.md` (couches, flux, décisions multiplateforme), `docs/fr/USO.md` (démarrage, env, opération, rôles), `docs/fr/DESARROLLO.md` (conventions + portes CI), `docs/fr/SEGURIDAD.md` (tokens, matrice de permissions, checklist prod), `docs/fr/BACKEND.md` + `docs/fr/DATABASE.md` (déplacées depuis `backend/` le 10/10/2026). READMEs et `AGENTS.md` avec chiffres réels ; admin dev `admin`/`setup` (sans `ADMIN_PASSWORD` dans `backend/.env.example` ; seed seulement non-prod dans `app/main.py:257`).
État : 1439 tests backend (47 fichiers) + 75 frontend (75 fichiers) verts, ruff + analyze propres.

## 4. Révision 10/10/2026 (corrections de §2–§3)

1. Docs backend consolidées : `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/fr/BACKEND.md` + `docs/fr/DATABASE.md` ; liens mis à jour dans `README.fr.md`, `AGENTS.md`, `docs/fr/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Comptage réel : routeurs 40 fichiers (38 avec `APIRouter` ; `permissions.py`/`dependencies.py` sont des helpers), services 43 modules (+`__init__`), modèles 40 entités (+`base.py`+`__init__`), schémas 37, Alembic 36, `API.md` 339 endpoints/38 routeurs (AST compte `propfind/report/options/websocket` ; simple grep donne ~290).
3. Tests : backend 1439 `def test_` dans 47 fichiers ; frontend 75 blocs `*_test.dart`. Widgets 32 OK. Écrans : `festival_profile` 1173L, `locations` 645L, `chat` 709L, `api_service` 464L, `user_profile` 1391L.
4. Corrections à §2 : `RateLimiter` sont 3 instances (`main.py`, `admin.py`, `auth.py`), pas 1 ; `ADMIN_PASSWORD` n'existe pas dans `backend/.env.example` (seulement commentaire `admin/setup`) ; `ruff format` couvre 216 fichiers (pas 215).
5. `tools/gen_api.py` régénère `API.md` de manière idempotente mais avec chemin absolu hardcodé et sans shebang (non portable).

## 5. Maintenabilité en attente (ordre suggéré, avec vérification)

| # | Tâche | État 10/10/2026 | Comment vérifier |
|---|---|---|---|
| 1 | Migrer les routeurs vers `get_or_404` et les services vers `paginate_filtered` | `get_or_404` dans 13 routeurs (110 utilisations), 186 `404` inline restants ; `paginate_filtered` avec 0 utilisations | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrer `python-jose` → `PyJWT` (PR isolé avec tests d'expiration/type/rotation) | Non migré (`app/auth.py` utilise `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Découpage des grands écrans | Fait : `festival_profile` 1173L, `locations` 645L, `api_service` 464L, `chat` 709L, `user_profile` 1391L (widgets extraits dans `lib/widgets/`) | `(Get-Content frontend/lib/screens/<écran>).Count` |
| 4 | Migrer `AlertDialog` → `ConfirmDialog` et `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 utilisations `showConfirmDialog` ; 115 `ScaffoldMessenger` vs 8 utilisations `showAppSnack` (les `AlertDialog` restants sont des formulaires : nécessitent un `CreateEntityDialog` commun) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Hygiène de formatage + `.gitignore` | `ruff format --check` + `ruff check` propres et avec porte dans CI (GH + GitLab) ; `.gitignore` couvre `*.db*`, `*.hive`, `*.lock`, `uploads/` (pas le glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |