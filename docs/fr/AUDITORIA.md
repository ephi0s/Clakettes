# Audit de code — Clakettes (09/10/2026, ampl. multiplateforme 09/10/2026, rév. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](../it/AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

> **Addendum 11/10/2026** (chiffres vérifiés) : backend 1402 tests dans 37 fichiers ;
> routers 36 fichiers (33 avec `APIRouter`) ; services 36 ; models 34 ; schemas 33 ;
> Alembic 18 versions ; `docs/es/API.md` 310 endpoints (operationIds uniques).
> RGPD : confidentialité par défaut, consentement, suppression/exportation, purge des
> sessions, audit append-only, nettoyage des métadonnées, TLS MariaDB en prod,
> DAV avec expiration, CSP/HSTS. Fournisseurs de paiement mock/stripe/redsys.

## 0. Résumé exécutif (10/10/2026, chiffres vérifiés)

| Área | Estado | Detalle |
| --- | --- | --- |
| Backend tests | 1321 `def test_` en 33 archivos | `Get-ChildItem backend/tests -Recurse -Filter "test_*.py" \| Select-String "def test_"` |
| Frontend tests | 347 bloques en 69 archivos | `Get-ChildItem frontend/test -Recurse -Filter "*_test.dart" \| Select-String "testWidgets\(|test\("` |
| Routers/Services/Models/Schemas | 35/33/33/32 archivos (33 routers con `APIRouter`) | `permissions.py`/`dependencies.py` son helpers sin router; `base.py`/`__init__.py` no son entidades |
| Migraciones | 15 + `__init__.py` | `alembic/versions/` |
| Endpoints | 294 en 33 routers (`docs/es/API.md` por AST) | `python tools/gen_api.py` idempotente; grep simple da 272 (no cuenta `propfind/report/options/websocket`) |
| Lint | `ruff check` + `ruff format --check` limpios (216 archivos) | `AGENTS.md` y CI (GH + GitLab) con gate de formato |
| Docs | Backend consolidado en `docs/` | `docs/es/BACKEND.md` + `docs/es/DATABASE.md`; índice en `docs/es/README.md` |
| Deuda principal | `get_or_404` parcial, `paginate_filtered` sin usos, `python-jose` sin migrar, 24 `AlertDialog` / 115 `ScaffoldMessenger` restantes | Ver §5 con conteos y verificación |

Comment revérifier : `cd backend; python -m ruff check .; python -m pytest tests/ -x -q --tb=short` et `cd frontend; flutter analyze; flutter test`.

## 1. Dépendances externes : ce qui peut être supprimé et ce qui ne le peut pas

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Mantener | Núcleo del stack |
| python-jose[cryptography] | Mantener por ahora, migrar a PyJWT en el futuro | Abandonado desde 2016, pero el cambio toca `app/auth.py` + `routers/dependencies.py` + tests; hacerlo en PR separado con tests de tokens |
| python-dotenv | Mantener | Requerido por `pydantic-settings>=2` y `uvicorn[standard]` (`--env-file`); solo 2 scripts lo importan directamente, pero quitarlo rompería la carga de `.env` |
| pymysql | Mantener como driver prod | Solo se usa con MariaDB; no cargarlo en dev no ahorra nada (import perezoso ya en SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Mantener | Uploads, validación email, hash passwords |
| reportlab 5.0.1 | Mantener, pero con import perezoso (hecho) | Solo `export_service._build_pdf`; antes se importaba a nivel de módulo (~200 ms + memoria en cada worker). Ahora import dentro de la función. Además se sincronizó `pyproject.toml` (faltaba) y se pineó `==5.0.1` |

### Frontend (`frontend/pubspec.yaml`)

Toutes les dépendances sont en usage réel ; aucune n'a pu être supprimée sans casser de fonctionnalité :

- `archive` : utilisé dans `crypto_utils.dart` (ZLib/GZip). `dart:io` ne vaut pas car il casse web.
- `path_provider` : utilisé dans `file_downloader_io.dart` (mobile/desktop).
- `web` : utilisé dans `file_downloader_web.dart`.
- `pointycastle` + `crypto` + `uuid` : E2EE du chat (X25519/ECDH P-256 + AES-GCM).
- `flutter_map` + `cancellable_tile` + `latlong2` + `geolocator` + `url_launcher` : cartes.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker` : chacun avec 1-2 usages, mais les supprimer retirerait de la fonctionnalité.

## 2. Optimisations appliquées

1. `export_service.py` : import reportlab paresseux dans `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` : 3 instances `RateLimiter` (buckets `middleware:`/`dav:` + limiters de `reset` 3/300s et `login`) ; ne pas unifier sans perdre des limites distinctes.
3. `base_service.py` : `paginate` fixe `page>=1`, `size` dans `[1,100]` ; nouveau `paginate_filtered()` défini avec 0 usages (en attente de migrer les `get_all_paginated` clonés).
4. `routers/dependencies.py` : `get_current_user_optional` réutilise `validate_access_token` (élimine ~30 lignes dupliquées JWT+session) ; fix `__import__("datetime")` → import normal ; nouveau `get_or_404()` pour remplacer ~100 `HTTPException(404)` inline.
5. `dav/auth.py` : documentée la relation avec `app.auth._hash_token`.
6. `pyproject.toml`/`requirements.txt` synchronisés (reportlab).
7. `reusable_widgets.dart` : nouveau `showAppSnack()` (1 def + 8 usages ; restent 115 `ScaffoldMessenger` directs).

## 3. Améliorations multiplateformes appliquées (bureau + web + Android + iOS/iPad)

1. `BackendConfig` : défaut par plateforme — émulateur Android utilise `10.0.2.2:8000`
   (localhost de l'émulateur est le virtuel lui-même, pas l'hôte) ; reste `localhost:8000`.
   Priorité : URL sauvegardée > `--dart-define=BACKEND_URL` > défaut par plateforme.
   `ApiService` utilise le même défaut dans constructeur et getters.
2. `NotificationService` : en web (`kIsWeb`) `init` ne touche ni plugin ni timezone
   (sans notifications locales en navigateur) et `scheduleReminder` ne fait rien ;
   documenté dans le docstring. Sans branches par plateforme dans les écrans.
3. `file_downloader.dart` : vérifié l'import conditionnel
   (`web` par défaut, `io` si `dart.library.io`) — couvre navigateur, bureau,
   Android et iOS sans changements.
4. `main_scaffold.dart` : ajouté Cortos à la navigation (existait l'écran
   `screenIndex 3` mais sans item — inaccessible). Rail >800px (bureau/web),
   Bar <800px (mobile), Drawer partout.
5. `AndroidManifest.xml` : ajoutés INTERNET, ACCESS_NETWORK_STATE, localisation
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM.
   Sans INTERNET explicite les builds release n'ont pas de réseau.
6. `ios/Runner/Info.plist` : ajoutés NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add). Sans ceux-ci le système refuse ou l'App Store rejette.
7. Backend `routers/festivals.py` : pilote `get_or_404(db, Festival/Location, ...)`
   — 9 blocs `if not → 404` éliminés ; étendu à `shortfilms.py` (3) et
   `users.py` (4). Motif à étendre au reste des routers.
8. Frontend `awards_screen.dart` : erreur SnackBar migrée vers `showAppSnack()`
   (pilote). Note : les 24 `AlertDialog` restants sont des dialogues de *formulaire*
   (créer/éditer), pas de confirmation — ne migrent pas vers `showConfirmDialog`
   (19 usages dans 18 écrans) ; ils requerraient un `CreateEntityDialog` commun.
9. CI : gate `ruff format --check` ajouté (GH + GitLab) après vérification
   `216 files already formatted`.
10. Sécurité (pilote `channels.py`, bloc sécurité) : nouveau
    `require_channel_member`/`is_channel_member` dans `permissions.py` et usage dans
    `channels.py` + `chat.py` (élimine 3 blocs inline avec imports différés) ;
    `channels.py` migré vers `get_or_404` (7 blocs en moins) ; whitelist de rôle
    `Literal[admin,moderator,member]` dans schemas (avant : string libre → 500
    par CheckConstraint ; maintenant : 422) ; 4 tests 403/422 nouveaux dans
    `TestChannelAuthorization`.
11. Sécurité : `POST /delegations/{id}/revoke` exigeait seulement auth — n'importe qui
    révoquait des délégations d'autrui. Maintenant vérifie délégateur ou admin + test 403.
    Vérifiés déjà OK (sans changements) : `user_roles`/`user_festival` (whitelist
    attendee), DMs (ownership), formulaires publics (auth optionnelle), WS
    (valide session), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 clés manquantes), `locations` (didChangeDependencies avec garde).
12. `get_or_404` étendu à `committees.py` (10), `events.py` (58, via script
    avec révision + 17 existences sans assigner pour éviter F841), `delegations`
    (2) et 5 routers de localisations (12). Sans changements de schéma : il n'y a pas
    de migration Alembic en attente pour ce lot.
13. Performance : filtre `venue` de programación descendu en SQL (avant filtrait
    la page en Python et cassait `total`/`pages`).
14. Frontend : gardes anti-double-envoi en créer festival/utilisateur/court +
    3 SnackBars migrés vers `showAppSnack`.
15. Chat : E2EE hors du UI thread — `_prepareContent`/`_unpackContent` utilisent
    `encryptAsync`/`decryptAsync` (isolates) ; nouveaux `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` utilisés en diffusion et réception de sender keys.
    `RestChatBackend` est conservé : `chat_service_test` l'utilise comme fake
    (ce n'était pas du code mort).
16. Chat : `chat_screen.dart` 1038 → 767 lignes ; bulles vers
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` avec image,
    localisation, vCard, iCal) et barre vers `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 tests async nouveaux dans `crypto_utils_test`.
17. `locations_screen` 1144 → 680 lignes : cartes et formulaire vers
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`) ; suppression
    avec `showConfirmDialog` + `showAppSnack` (un AlertDialog en moins).
18. `festival_profile_screen` 1276 → 956 lignes : `RulebooksSection` et
    `FestivalLocationsSection` (+ carte et fiches) vers
    `widgets/festival_sections.dart`. L'écran conserve état,
    lecture, édition et callbacks.
19. `api_service.dart` 1134 → 511 lignes : 95 méthodes déplacées vers `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    reste vers `user_api` + `calendar/channel/festival/form`). Le noyau conserve config, auth, transport et
    admin/recherche. API publique intacte.
20. `user_profile_screen` 996 → 803 lignes : `SessionsCard` et `AliasesCard`
    vers `widgets/user_profile_cards.dart`. Corrigés 4 `if` sans accolades
    hérités dans `catalog_api`.
21. Tests de flux (`tests/integration/test_flows.py`) : réservation complète
    (festival → événement → sièges → réservation → occupation), messagerie
    (canal → membre → DM → lecture → suppression) et délégation (créer →
    lister → révoquer).
22. Tests widget des widgets extraits (13) : `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Note : les
    widgets sous `wrapWithLocalization` ont besoin d'un `pump()` supplémentaire
    (le Builder de localisation résout au deuxième frame).
23. Push natif sans Firebase (`docs/fr/PUSH.md`) : Notification API du navigateur
    en web (`notification_web.dart` + stub avec export conditionnel, sans deps
    nouvelles), `flutter_local_notifications` en bureau + permission macOS au
    démarrage, mobile en no-op explicite (`_supported`). `flutter build web`
    vérifié.
24. Documentation : `docs/es/API.md` (294 endpoints dans 33 routers, générée par
    AST avec `tools/gen_api.py` — régénérable), `docs/fr/ARQUITECTURA.md`
    (couches, flux, décisions multiplateformes), `docs/fr/USO.md` (démarrage,
    env, opération, rôles), `docs/fr/DESARROLLO.md` (conventions + portes
    CI), `docs/fr/SEGURIDAD.md` (tokens, matrice de permissions, liste prod),
    `docs/fr/BACKEND.md` + `docs/fr/DATABASE.md` (déplacées depuis `backend/` le 10/10/2026).
    READMEs et `AGENTS.md` avec chiffres réels ; admin dev `admin`/`setup`
    (sans `ADMIN_PASSWORD` dans `.env.example` ; seed seulement non-prod dans `app/main.py:257`).
État : 1321 tests backend (33 fichiers) + 347 frontend (69 fichiers) au vert, ruff + analyze propres.

## 4. Révision 10/10/2026 (corrections à §2–§3)

1. Docs backend consolidées : `backend/BACKEND.md` + `backend/DATABASE.md` → `docs/fr/BACKEND.md` + `docs/fr/DATABASE.md` ; liens mis à jour dans `README.fr.md`, `AGENTS.md`, `docs/fr/README.md`, `ARQUITECTURA.md`, `USO.md`, `ADMINISTRACION.md`.
2. Compte réel : routers 35 fichiers (33 avec `APIRouter` ; `permissions.py`/`dependencies.py` sont helpers), services 33 modules (+`__init__`), models 33 entités (+`base.py`+`__init__`), schemas 32, Alembic 15, `API.md` 294 endpoints/33 routers (AST compte `propfind/report/options/websocket` ; grep simple donne 272).
3. Tests : backend 1321 `def test_` dans 33 fichiers (pas 1366/38) ; frontend 347 blocs dans 69 fichiers (pas 313/70). Widgets 24 OK. Écrans : `festival_profile` 956L, `locations` 680L, `chat` 767L, `api_service` 511L, `user_profile` 803L.
4. Corrections à §2 : `RateLimiter` sont 3 instances (`main.py`, `admin.py`, `auth.py`), pas 1 ; `ADMIN_PASSWORD` n'existe pas dans `backend/.env.example` (seulement commentaire `admin/setup`) ; `ruff format` couvre 216 fichiers (pas 215).
5. `tools/gen_api.py` régénère `API.md` idempotent mais avec chemin absolu codé en dur et sans shebang (non portable).

## 5. Maintenabilité en attente (ordre suggéré, avec vérification)

| # | Tarea | Estado 10/10/2026 | Cómo verificar |
| --- | --- | --- | --- |
| 1 | Migrar routers a `get_or_404` y servicios a `paginate_filtered` | `get_or_404` en 13 routers (110 usos), 186 `404` inline restantes; `paginate_filtered` con 0 usos | `Select-String "get_or_404\(" backend/app/routers; Select-String "404" backend/app/routers; Select-String "paginate_filtered" backend/app/services` |
| 2 | Migrar `python-jose` → `PyJWT` (PR aislado con tests de expiración/tipo/rotación) | Sin migrar (`app/auth.py` usa `jose`) | `Select-String "from jose\|import jose" backend/app; Select-String "import jwt" backend/app` |
| 3 | Troceo de pantallas grandes | Hecho: `festival_profile` 956L, `locations` 680L, `api_service` 511L, `chat` 767L, `user_profile` 803L (widgets extraídos en `lib/widgets/`) | `(Get-Content frontend/lib/screens/<pantalla>).Count` |
| 4 | Migrar `AlertDialog` → `ConfirmDialog` y `ScaffoldMessenger` → `showAppSnack` | 24 `AlertDialog` vs 19 usos `showConfirmDialog`; 115 `ScaffoldMessenger` vs 8 usos `showAppSnack` (los `AlertDialog` restantes son formularios: requieren `CreateEntityDialog` común) | `Select-String "AlertDialog|showConfirmDialog|ScaffoldMessenger|showAppSnack" frontend/lib` |
| 5 | Higiene formato + `.gitignore` | `ruff format --check` + `ruff check` limpios y con gate en CI (GH + GitLab); `.gitignore` cubre `*.db*`, `*.hive`, `*.lock`, `uploads/` (no el glob `*.hive*`) | `ruff format --check .; ruff check .; Get-Content .gitignore` |
