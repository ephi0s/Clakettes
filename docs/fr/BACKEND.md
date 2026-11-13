# Clakettes Backend — Documentation technique

[ES](../es/BACKEND.md) · [EN](../en/BACKEND.md) · [FR](BACKEND.md) · [DE](../de/BACKEND.md) · [IT](../it/BACKEND.md) · [CA](../ca/BACKEND.md) · [EU](../eu/BACKEND.md) · [GL](../gl/BACKEND.md) · [OC](../oc/BACKEND.md)

Backend FastAPI pour la plateforme de gestion de festivals de cinéma Clakettes.

## Démarrage rapide

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API** : http://localhost:8000
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## Architecture

### Structure par couches

```
Routers (FastAPI) → Services (Logique métier) → Models (SQLAlchemy)
```

| Couche | Emplacement | Responsabilité |
|--------|-------------|----------------|
| **Routers** | `app/routers/` | Endpoints HTTP, validation requête/réponse, pagination |
| **Services** | `app/services/` | Logique métier, opérations CRUD, préoccupations transversales |
| **Models** | `app/models/` | Modèles ORM SQLAlchemy, schéma DB |
| **Schemas** | `app/schemas/` | Modèles Pydantic pour requête/réponse |
| **Auth** | `app/auth.py` | JWT, sessions, hashage des mots de passe |
| **Config** | `app/config.py` | Pydantic Settings depuis `.env` |
| **Database** | `app/database.py` | Moteur, fabrique de sessions, dépendance `get_db()` |

### Principes de conception clés

1. **Routers légers** — délèguent aux services
2. **Services sans état** — reçoivent `db: Session` via injection de dépendances
3. **Les modèles héritent de `BaseModel`** — `id`, `created_at`, `updated_at` sur toutes les entités
4. **Enums centralisés** — `app/enums.py` partagé entre modèles et schémas
5. **Base CRUD générique** — `BaseService` dans `app/services/base_service.py`

---

## Configuration

Toute la configuration se fait via `backend/.env` (chargé par `pydantic-settings`) :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `sqlite:///./clakettes.db` | Chaîne de connexion SQLAlchemy |
| `SECRET_KEY` | (requis, sans défaut) | Clé de signature JWT |
| `JWT_ISSUER` | `clakettes` | Revendication émetteur JWT |
| `JWT_AUDIENCE` | `clakettes-api` | Revendication audience JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Durée de vie du token d'accès |
| `CORS_ORIGINS` | `None` (→ `["*"]`) | Origines autorisées séparées par des virgules |
| `PORT_BACKEND` | `8000` | Port du serveur (utilisé par Docker/scripts de démarrage) |

**Exemple de `.env` pour la production :**

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=super-secret-64-char-urlsafe-string
JWT_ISSUER=clakettes
JWT_AUDIENCE=clakettes-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

Générez une clé `SECRET_KEY` robuste :

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Base de données

### Compatibilité double base de données

| Environnement | Base de données | Chaîne de connexion |
|-------------|-----------------|---------------------|
| Développement | SQLite | `sqlite:///./data/clakettes.db` |
| Production | MariaDB | `mariadb+pymysql://user:pass@host:3306/db` |

### Modèle de base

Tous les modèles héritent de `BaseModel` (`app/models/base.py`) :

```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Migrations (Alembic)

```bash
cd backend

# Créer une nouvelle migration après des changements de modèle
alembic revision --autogenerate -m "description"

# Appliquer les migrations
alembic upgrade head

# Retour arrière
alembic downgrade -1

# Révision actuelle
alembic current
```

**Notes de migration (SQLite ↔ MariaDB) :**
- SQLite `INTEGER PRIMARY KEY` → MariaDB `INT AUTO_INCREMENT`
- SQLite `TEXT` → MariaDB `TEXT`/`VARCHAR`
- SQLite `DATETIME` (stocké en texte) → MariaDB `DATETIME` natif
- Les scripts d'exportation/importation dans `backend/tools/` gèrent les conversions de types automatiquement

Consultez [DATABASE.md](DATABASE.md) pour la documentation complète du schéma avec diagrammes ER.

---

## Authentification

### JWT + Suivi des sessions

| Type de token | Format | TTL | Stockage |
|---------------|--------|-----|----------|
| **Token d'accès** | JWT (HS256) | 30 min (configurable) | Mémoire client |
| **Token de rafraîchissement** | Opaque (hash SHA-256 en DB) | 30 jours | `UserSession.refresh_token_hash` |

### Flux de connexion

```
POST /api/users/login
  {username, password}
→ 200 {access_token, refresh_token, token_type: "bearer", user: {...}}
```

### Utilisation du token

```http
Authorization: Bearer <access_token>
```

### Flux de rafraîchissement

```
POST /api/auth/refresh
  {refresh_token}
→ 200 {access_token, refresh_token, token_type: "bearer"}
```

### Gestion des sessions

- `GET /api/auth/sessions` — Lister les sessions actives
- `DELETE /api/auth/sessions/{session_id}` — Révoquer la session
- La session est créée à la connexion avec les infos de l'appareil (IP, UA, nom)
- Les tokens sont rotés au rafraîchissement ; les anciens tokens sont invalidés

### Hashage des mots de passe

- **bcrypt** via `passlib` (rounds=12)
- Hash stocké dans `User.password_hash`
- Vérifié via `pwd_context.verify(plain, hash)`

### Limite de requêtes

- **100 requêtes / 60 secondes** par IP (sauvegarde SQLite)
- Appliqué via `RateLimitMiddleware` dans `main.py`
- Désactivé quand la variable d'environnement `TESTING=true` est définie

---

## Endpoints de l'API

### Enregistrement des routers (`app/main.py`)

| Router | Préfixe | Tags | Description |
|--------|---------|------|-------------|
| `festivals` | `/api/festivals` | festivals | CRUD, recherche, membres |
| `users` | `/api/users` | users | CRUD, profil, upload avatar |
| `auth` | `/api/users` | auth | Connexion, rafraîchissement, inscription |
| `auth_sessions` | `/api/auth` | auth | Liste/révocation des sessions |
| `shortfilms` | `/api/shortfilms` | shortfilms | CRUD, lien festival |
| `chat` | `/api/chat` | chat | Messages, endpoint WS |
| `user_festival` | `/api/festivals` | user-festival | Rejoindre/quitter, membres |
| `uploads` | `/api/uploads` | uploads | Upload avatar |
| `search` | `/api/search` | search | Recherche globale |
| `admin` | `/api/admin` | admin | Stats, tables, audit-log, reset |
| `notifications` | `/api/notifications` | notifications | CRUD, non lus count |
| `roles` | `/api` | roles | Rôles, groupes, dépendances, conflits |
| `participant_tags` | `/api` | participant-tags | Tags, config festival |
| `user_roles` | `/api` | user-roles | Attributions de rôles |
| `user_aliases` | `/api` | user-aliases | Alias d'affichage |
| `validation_rules` | `/api` | validation-rules | Validation dynamique de formulaires |
| `registration_forms` | `/api` | registration-forms | Flux d'inscription festival |
| `role_groups` | `/api` | role-groups | Groupement de rôles |
| `committees` | `/api` | committees | Comités de festival |
| `delegations` | `/api` | delegations | Délégations de rôles |
| `events` | `/api` | events | Événements, tickets, sièges, réservations |
| `channels` | `/api/channels` | channels | Canaux de chat |
| `keys` | `/api/users` | e2ee | Gestion clés publiques E2EE |
| `locations` | `/api/locations` | locations | Géolocalisation, cartes |
| `location_tags` | `/api/locations/{location_id}/tags` | location-tags | Tags de localisation |
| `location_images` | `/api/locations/{location_id}/images` | location-images | Images de localisation |
| `location_relations` | `/api/locations/{location_id}/relations` | location-relations | Relations de localisation |
| `shortfilm_locations` | `/api/shortfilms/{shortfilm_id}/locations` | shortfilm-locations | Localisations de court-métrage |
| `form_definitions` | `/api` | forms | Constructeur de formulaires |
| `federation` | `/api/federation` | federation | manifest, répertoire, nœuds, rapports, webfinger |
| `jury_votes` | `/api` | jury-votes | Vote du jury (phase 5) |
| `calendar` | `/api/calendar` | calendar | Agenda, CalDAV, paramètres |
| `badges` | `/api` | badges | Insignes, affectations, éligibilité |
| `posts` | `/api` | posts | Publications sociales, réponses, modération |
| `payments` | `/api` | payments | Paiement, confirmation, remboursement, webhook |
| `festival_rulebooks` | `/api/festivals/{festival_id}/rulebooks` | rulebooks | Livre de règles du festival |
| `user_blocks` | `/api` | user-blocks | Blocage d'utilisateur |
| `moderation_reports` | `/api` | moderation-reports | Rapports de modération |
| `node_policies` | `/api` | node-policies | Politiques de nœuds de fédération |

Total : 38 routers avec `APIRouter` (40 fichiers de router, 2 helpers sans router).

### Pagination et filtrage

Paramètres de requête standards sur les endpoints de liste :

```
GET /api/festivals/?page=1&size=20&search=cannes&is_active=true
```

Enveloppe de réponse :

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

---

## Chat en temps réel

### Backend WebSocket (`app/chat_backend/`)

| Composant | Description |
|-----------|-------------|
| `WebSocketChatBackend` | Implémentation par défaut (connexions en mémoire) |
| `chat_backend_registry` | Registre singleton pour l'échange de backend |
| `ConnectionManager` | Gère les mappings utilisateur↔WebSocket |

### Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/chat/ws` | Connexion WebSocket (auth via query `token`) |
| `POST` | `/api/chat/messages` | Envoyer un message (fallback REST) |
| `GET` | `/api/chat/messages` | Historique paginé |
| `PATCH` | `/api/chat/messages/{id}/read` | Marquer comme lu |

### Types de message

```python
class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LOCATION = "location"
    VCARD = "vcard"
    ICAL = "ical"
    SYSTEM = "system"
```

### E2EE

- Échange de clés X25519 via `/api/users/{id}/keys`
- Clés publiques stockées dans `UserKey` (une clé active par utilisateur)
- Chiffrement/déchiffrement dans le frontend (`e2ee_service.dart`)

---

## Uploads de fichiers

### Upload d'avatar

```
POST /api/uploads/avatar
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image/*>
```

- Sauvegardé dans `backend/uploads/avatars/{user_id}_{uuid}.{ext}`
- Servi de manière statique à `/uploads/avatars/...`
- Taille maximale : 10 Mo (appliqué par `RequestSizeLimitMiddleware`)

---

## Endpoints d'administration

Nécessite `role=admin` (vérifié dans `admin_service.py`) :

| Endpoint | Description |
|----------|-------------|
| `GET /api/admin/stats` | Statistiques de la plateforme |
| `GET /api/admin/tables` | Nombre de lignes par table |
| `GET /api/admin/audit-log` | Piste d'audit (filtres `action`, `actor_user_id`) |
| `POST /api/admin/reset` | `drop_all + create_all` (non-prod uniquement) |

---

## Tests

```bash
cd backend

# Exécuter tous les tests
python -m pytest tests/ -x -q --tb=short

# Exécuter avec couverture
python -m pytest tests/ --cov=app --cov-report=term-missing

# Fichier de test spécifique
python -m pytest tests/test_festivals.py -v
```

**Configuration des tests** (`pyproject.toml` / `pytest.ini`) :

```ini
[tool.pytest.ini_options]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

**Fixtures** (`tests/conftest.py`) :
- `db_session` — session SQLite en mémoire
- `client` — `AsyncClient` (httpx) contre l'app de test
- `auth_headers` — en-têtes déjà authentifiées

---

## Lint et formatage

```bash
# Vérifier
ruff check .

# Corriger auto-réparable
ruff check . --fix

# Formater
ruff format .
```

**Configuration** (`pyproject.toml`) :

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "PTH", "T20", "SIM", "ARG"]
ignore = ["E501", "SIM102", "SIM103"]
```

---

## Flux de développement

### Développement local

```bash
# Terminal 1 : Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 : Frontend (si nécessaire)
cd frontend
flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=http://localhost:8000/api
```

### Développement avec Docker

```bash
# Depuis la racine du projet
docker compose up        # Backend:8000, Frontend:3000
docker compose --profile db up  # + MariaDB:3306
```

### Chargement initial de la base de données

Aucun script de seed : en développement l'app crée l'admin initial (`admin` /
`setup`, changez le mot de passe à la première connexion) et les tables via `create_all`. En production
les données arrivent via l'API et le schéma uniquement via Alembic.

### Commandes courantes

```bash
# Générer les adaptateurs Hive (frontend)
cd frontend && flutter pub run build_runner build --delete-conflicting-outputs

# Exécuter les migrations
cd backend && alembic upgrade head

# Créer une migration
cd backend && alembic revision --autogenerate -m "add column x"

# Exporter SQLite → MariaDB
cd backend && python tools/export_sqlite_to_mariadb.py

# Importer MariaDB → SQLite
cd backend && python tools/import_mariadb_to_sqlite.py
```

---

## Structure du projet

```
backend/
├── app/
│   ├── models/              # 40 modèles SQLAlchemy (+ base.py)
│   ├── schemas/             # 37 schémas Pydantic
│   ├── services/            # 43 services de logique métier
│   ├── routers/             # 40 routers API (38 avec APIRouter)
│   ├── chat_backend/        # Implémentation WebSocket du chat
│   ├── auth.py              # Auth JWT + session
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Moteur, SessionLocal, get_db()
│   ├── main.py              # App FastAPI, middleware, routers
│   ├── rate_limiter.py      # Limiteur de taux SQLite
│   ├── enums.py             # Enums partagés
│   └── scripts/             # Scripts de seed/migration
├── alembic/                 # Migrations (36 versions)
├── tools/                   # Scripts d'export/import
├── tests/                   # Tests pytest (47 fichiers, 1439 fonctions de test)
├── uploads/                 # Fichiers statiques uploadés
├── .env.example             # Modèle de configuration
├── requirements.txt         # Déps de production
├── requirements-dev.txt     # Déps de dev (pytest, ruff)
├── pyproject.toml           # Config Ruff, pytest
└── pytest.ini               # Config pytest
```

Docs dans `docs/fr/BACKEND.md` (ce fichier) et `docs/fr/DATABASE.md`.

---

## Déploiement

### Docker (Production)

```yaml
# docker-compose.yml utilise --profile prod
docker compose --profile prod up -d
```

Services :
- `backend-prod` — FastAPI (workers Uvicorn) sur :8000
- `frontend-prod` — Nginx + Flutter web sur :80
- `db` — MariaDB 11 (vérification de santé)

Profils disponibles :
- `dev` (par défaut) : serveurs de développement backend et frontend
- `db` : ajoute le conteneur MariaDB
- `prod` : pile de production avec nginx

### Variables d'environnement (Production)

```env
DATABASE_URL=mariadb+pymysql://user:pass@db:3306/clakettes_db
SECRET_KEY=<64-char-urlsafe>
CORS_ORIGINS=https://app.example.com
```

### Vérification de santé

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Checklist de sécurité

- [ ] Changez `SECRET_KEY` en production
- [ ] Définissez `CORS_ORIGINS` sur des domaines spécifiques
- [ ] Utilisez MariaDB (pas SQLite) en production
- [ ] Activez HTTPS (proxy inverse : nginx/Traefik)
- [ ] Configurez les hôtes autorisés dans `TrustedHostMiddleware`
- [ ] Rottez les clés JWT périodiquement
- [ ] Surveillez les logs du limiteur de taux
- [ ] Vérifiez le mot de passe de l'utilisateur admin après la première connexion

---

## Étendre l'API

### Ajouter une nouvelle ressource

1. **Modèle** — `app/models/new_resource.py` (hérite de `BaseModel`)
2. **Schéma** — `app/schemas/new_resource.py` (Pydantic)
3. **Service** — `app/services/new_resource_service.py` (étend `BaseService`)
4. **Router** — `app/routers/new_resource.py` (inclure dans `main.py`)
5. **Migration** — `alembic revision --autogenerate -m "add new_resource"`
6. **Tests** — `tests/test_new_resource.py`

### Ajouter un endpoint personnalisé à un router existant

```python
# Dans le fichier du router
@router.post("/{festival_id}/custom-action", response_model=CustomResponse)
async def custom_action(
    festival_id: int,
    payload: CustomRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.custom_action(db, festival_id, payload, current_user)
```

---

## Résolution de problèmes

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: app` | Exécutez depuis le dossier `backend/` ou `PYTHONPATH=backend` |
| `sqlite3.OperationalError: database is locked` | Seul un écrivain ; assurez-vous qu'aucun processus résiduel |
| `alembic: Can't locate revision` | Supprimez `alembic/versions/`, exécutez `alembic revision --autogenerate -m "init"` |
| `JWTError: Signature verification failed` | Incompatibilité `SECRET_KEY` entre env et processus en cours |
| `429 Too Many Requests` | Limite de taux atteinte ; attendez 60s ou définissez `TESTING=true` |
| WebSocket 403 | Token expiré ; utilisez un token d'accès valide dans `?token=` |
| Erreur CORS | Vérifiez `CORS_ORIGINS` dans `.env` correspond à l'origine du frontend |

---

## Références

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://github.com/mpdavis/python-jose)
- [passlib](https://passlib.readthedocs.io/)