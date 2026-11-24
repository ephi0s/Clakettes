# Audit del codice — Clakettes (09/10/2026, ampl. multipiattaforma 09/10/2026, rev. 10/10/2026)

[ES](../es/AUDITORIA.md) · [EN](../en/AUDITORIA.md) · [FR](../fr/AUDITORIA.md) · [DE](../de/AUDITORIA.md) · [IT](AUDITORIA.md) · [CA](../ca/AUDITORIA.md) · [EU](../eu/AUDITORIA.md) · [GL](../gl/AUDITORIA.md) · [OC](../oc/AUDITORIA.md)

## 0. Riassunto esecutivo

Revisione delle dipendenze, delle ottimizzazioni applicate e del debito tecnico in sospeso del progetto Clakettes.

## 1. Dipendenze esterne: cosa si può eliminare e cosa no

### Backend (`backend/requirements.txt` + `pyproject.toml`)

| Dep | Veredicto | Motivo |
| --- | --- | --- |
| fastapi, uvicorn[standard], sqlalchemy, pydantic(+settings), alembic | Mantenere | Nucleo dello stack |
| PyJWT==2.15.1 | Migrazione completata | `python-jose` rimosso; `app/auth.py` e `routers/dependencies.py` usano PyJWT (bump 2.10.1 → 2.15.0 → 2.15.1) |
| python-dotenv | Non inclusa | Non compare in `pyproject.toml`/`requirements*.txt` né viene importata in `backend/`; `pydantic-settings` carica `.env` direttamente |
| pymysql | Mantenere come driver prod | Usato solo con MariaDB; non caricarlo in dev non risparmia nulla (import pigro già in SQLAlchemy) |
| python-multipart, email-validator, bcrypt | Mantenere | Upload, validazione email, hashing delle password |
| reportlab 5.1.0 | Mantenere, ma con import pigro (fatto) | Solo `export_service._build_pdf`; prima importato a livello di modulo (~200 ms + memoria per ogni worker). Ora importato dentro la funzione. Inoltre è stato sincronizzato `pyproject.toml` (mancava) e fissato `==5.1.0` |

**Versioni fissate in `backend/pyproject.toml` / `requirements*.txt`:** `fastapi==0.163.1`, `uvicorn[standard]==0.54.0`, `sqlalchemy==2.1.9`, `pydantic==2.14.3`, `pydantic-settings==2.16.3`, `email-validator==2.4.0`, `pymysql==1.2.4`, `python-multipart==0.0.34`, `PyJWT==2.15.1`, `cryptography==50.0.2`, `bcrypt>=4.3.0`, `alembic==1.20.1`, `reportlab==5.1.0`, `Pillow==13.0.0`, `mutagen==1.48.1`, `pypdf==7.1.0` (major da 6.21.x); sviluppo: `pytest>=9.2.0`, `ruff==0.17.6`, `httpx==0.28.1`, `caldav==3.7.0`, `icalendar==7.3.0`.

### Frontend (`frontend/pubspec.yaml`)

Tutte le dipendenze sono in uso reale; nessuna si è potuta eliminare senza rompere funzionalità:

- `archive`: usato in `crypto_utils.dart` (ZLib/GZip). `dart:io` non vale perché rompe web.
- `path_provider`: usato in `file_downloader_io.dart` (mobile/desktop).
- `web`: usato in `file_downloader_web.dart`.
- `pointycastle` + `crypto`: E2EE della chat (ECDH P-256 + AES-GCM; il nome `X25519` compare solo in un campo ereditato).
- `flutter_map` + `latlong2` + `geolocator` + `url_launcher`: mappe.
- `table_calendar`, `flutter_local_notifications` + `timezone` + `flutter_timezone`, `image_picker` + `file_picker`: ciascuno con 1-2 usi, ma eliminarli toglierebbe funzionalità.

## 2. Ottimizzazioni applicate

1. `export_service.py`: import reportlab pigro in `_build_pdf` + docstring.
2. `main.py` RateLimitMiddleware + `routers/admin.py` + `routers/auth.py` + `routers/auth_sessions.py` + `routers/federation.py`: 5 istanze `RateLimiter` (buckets `middleware:`/`dav:` + limiters di `reset` 3/300 s, `login` 5/300 s, `refresh` 20/60 s e federazione 60/60 s); non unificare senza perdere limiti diversi. Il bypass passa da `app.config.is_testing()` (`1/true/yes/on`).
3. `base_service.py`: `paginate` fissa `page>=1`, `size` in `[1,100]`; nuovo `paginate_filtered()` definito con 0 usi (pendente migrare i `get_all_paginated` clonati).
4. `routers/dependencies.py`: `get_current_user_optional` riusa `validate_access_token` (elimina ~30 righe duplicate JWT+sessione); fix `__import__("datetime")` → import normale; nuovo `get_or_404()` per rimpiazzare ~100 `HTTPException(404)` inline.
5. `dav/auth.py`: documentata la relazione con `app.auth.hash_token` (prima `_hash_token`; l'alias è conservato per compatibilità).
6. `pyproject.toml`/`requirements.txt` sincronizzati (reportlab).
7. `reusable_widgets.dart`: nuovo `showAppSnack()` (1 def + 8 usi; restano 115 `ScaffoldMessenger` diretti).

## 3. Migliorie multipiattaforma applicate (desktop + web + Android + iOS/iPad)

1. `BackendConfig`: default per piattaforma — emulatore Android usa `10.0.2.2:8000`
   (localhost dell'emulatore è il virtuale stesso, non l'host); resto `localhost:8000`.
   Priorità: URL salvata > `--dart-define=BACKEND_URL` > default per piattaforma.
   `ApiService` usa lo stesso default in costruttore e getter.
2. `NotificationService`: su web (`kIsWeb`) `init` non tocca plugin né timezone
   (senza notifiche locali nel browser) e `scheduleReminder` non fa nulla;
   documentato nel docstring. Senza rami per piattaforma nelle schermate.
3. `file_downloader.dart`: verificato l'import condizionale
   (`web` di default, `io` se `dart.library.io`) — copre browser, desktop,
   Android e iOS senza modifiche.
4. `main_scaffold.dart`: aggiunto Corti alla navigazione (esisteva la schermata
   `screenIndex 3` ma senza item — inaccessibile). Rail >800px (desktop/web),
   Bar <800px (mobile), Drawer in tutti.
5. `AndroidManifest.xml`: aggiunti INTERNET, ACCESS_NETWORK_STATE, posizione
   (FINE+COARSE), CAMERA, READ_MEDIA_IMAGES/VIDEO, SCHEDULE/USE_EXACT_ALARM.
   Senza INTERNET esplicito le build release non hanno rete.
6. `ios/Runner/Info.plist`: aggiunti NSLocationWhenInUse, NSCamera,
   NSPhotoLibrary (+Add). Senza questi il sistema nega o l'App Store rifiuta.
7. Backend `routers/festivals.py`: pilota `get_or_404(db, Festival/Location, ...)`
   — 9 blocchi `if not → 404` eliminati; esteso a `shortfilms.py` (3) e
   `users.py` (4). Pattern da estendere al resto dei router.
8. Frontend `awards_screen.dart`: errore SnackBar migrato a `showAppSnack()`
   (pilota). Nota: i 24 `AlertDialog` restanti sono dialoghi di *form*
   (crea/modifica), non di conferma — non migrano a `showConfirmDialog`
   (19 usi in 18 schermate); richiederebbero un `CreateEntityDialog` comune.
9. CI: gate `ruff format --check` aggiunto (GH + GitLab) dopo verifica
   `216 files already formatted`.
10. Sicurezza (pilota `channels.py`, blocco sicurezza): nuovo
    `require_channel_member`/`is_channel_member` in `permissions.py` e uso in
    `channels.py` + `chat.py` (elimina 3 blocchi inline con import differiti);
    `channels.py` migrato a `get_or_404` (7 blocchi in meno); whitelist di ruolo
    `Literal[admin,moderator,member]` negli schema (prima: stringa libera → 500
    per CheckConstraint; ora: 422); 4 test 403/422 nuovi in
    `TestChannelAuthorization`.
11. Sicurezza: `POST /delegations/{id}/revoke` esigeva solo auth — chiunque
    revocava deleghe altrui. Ora verifica delegante o admin + test 403.
    Verificati già OK (senza modifiche): `user_roles`/`user_festival` (whitelist
    attendee), DM (ownership), form pubblici (auth opzionale), WS
    (valida sessione), `bulk_create` (single commit), SyncQueue (retry+backoff),
    i18n (0 chiavi mancanti), `locations` (didChangeDependencies con guardia).
12. `get_or_404` esteso a `committees.py` (10), `events.py` (58, via script
    con revisione + 17 esistenze senza assegnare per evitare F841), `delegations`
    (2) e 5 router di location (12). Questo lotto non ha introdotto migrazioni;
    revisioni successive hanno invece aggiunto `a8b9c0d1e2f3` (unicità del posto)
    e `b9c0d1e2f3a4` (`contest_type` nei corti), entrambe già applicate nell'head `b9c0d1e2f3a4`.
13. Performance: filtro `venue` di programmazione abbassato a SQL (prima filtrava
    la pagina in Python e rompeva `total`/`pages`).
14. Frontend: guardie anti-doppio-invio in crea festival/utente/corto +
    3 SnackBar migrati a `showAppSnack`.
15. Chat: E2EE fuori dall'UI thread — `_prepareContent`/`_unpackContent` usano
    `encryptAsync`/`decryptAsync` (isolates); nuovi `encryptSenderKeyAsync`/
    `decryptSenderKeyAsync` usati in diffusione e ricezione di sender keys.
    `RestChatBackend` si conserva: lo usa `chat_service_test` come fake
    (non era codice morto).
16. Chat: `chat_screen.dart` 1038 → 767 righe; fumetti a
    `widgets/chat_bubble.dart` (`ChatBubble` + `ChatBubbleWidget` con immagine,
    posizione, vCard, iCal) e barra a `widgets/chat_input_bar.dart`
    (`ChatInputBar`). 2 test async nuovi in `crypto_utils_test`.
17. `locations_screen` 1144 → 680 righe: schede e form a
    `widgets/location_cards.dart` (`LocationCard`, `LegacyCard`,
    `LegacyLocation`, `LocationFormScreen`, `LocationFormResult`); cancellazione
    con `showConfirmDialog` + `showAppSnack` (un AlertDialog in meno).
18. `festival_profile_screen` 1276 → 956 righe: `RulebooksSection` e
    `FestivalLocationsSection` (+ mappa e schede) a
    `widgets/festival_sections.dart`. La schermata conserva stato,
    lettura, modifica e callback.
19. `api_service.dart` 1134 → 511 righe: 95 metodi spostati in `lib/services/api/`
    (`event_api` 31, `location_api` 25, `org_api` 17, `catalog_api` 13,
    resto a `user_api` + `calendar/channel/festival/form`). Il nucleo conserva config, auth, trasporto e
    admin/ricerca. API pubblica intatta.
20. `user_profile_screen` 996 → 803 righe: `SessionsCard` e `AliasesCard`
    in `widgets/user_profile_cards.dart`. Corretti 4 `if` senza graffe
    ereditati in `catalog_api`.
21. Test di flusso (`tests/integration/test_flows.py`): prenotazione completa
    (festival → evento → posti → prenotazione → occupazione), messaggistica
    (canale → membro → DM → lettura → cancellazione) e delega (creare →
    elencare → revocare).
22. Widget test dei widget estratti (13): `chat_bubble`,
    `chat_input_bar`, `user_profile_cards`, `location_cards`. Nota: i
    widget sotto `wrapWithLocalization` necessitano di un `pump()` extra
    (il Builder di localizzazione risolve al secondo frame).
23. Push nativo senza Firebase (`docs/it/PUSH.md`): Notification API del browser
    su web (`notification_web.dart` + stub con export condizionale, senza dip.
    nuove), `flutter_local_notifications` su desktop + permesso macOS
    all'avvio, mobile in no-op esplicito (`_supported`). `flutter build web`
    verificato.
24. Documentazione: `docs/es/API.md`, `docs/it/ARQUITECTURA.md`
    (livelli, flussi, decisioni multipiattaforma), `docs/it/USO.md` (avvio,
    env, gestione, ruoli), `docs/it/DESARROLLO.md` (convenzioni + cancelli
    CI), `docs/it/SEGURIDAD.md` (token, matrice dei permessi, checklist prod),
    `docs/it/BACKEND.md` + `docs/it/DATABASE.md` (spostati da `backend/` il 10/10/2026).
    README e `AGENTS.md` con cifre reali; admin dev `admin`/`setup`
    (senza `ADMIN_PASSWORD` in `.env.example`; seed solo non-prod in `app/main.py:257`).
Stato: 1544 test backend (54 file) + frontend in 77 file in verde, ruff + analyze puliti.
