# Clakettes

La plateforme où les festivals de cinéma vivent toute l'année : appels, courts, équipes, lieux et public au même endroit.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Fonctionne en web, Android, iOS et bureau (Windows, macOS, Linux), en 9 langues et aussi sans connexion.

---

## Pour qui est-ce ?

- **Festivals** : publie ton festival, ouvre des appels, reçois des courts, organise comités et jurys, gère lieux et communique ton palmarès.
- **Professionnels du cinéma** : crée ton profil (réalisation, interprétation, son, scénario, montage, costumes et plus), montre ton palmarès et connecte avec festivals et équipes.
- **Équipes express** : coordonne ton groupe de tournage, géolocalise participants et présente ton court à des concours express.
- **Public** : découvre festivals, suis courts et contacte la communauté.

## Ce que tu peux faire

- **Festivals et appels** : chaque festival peut avoir plusieurs appels ouverts avec leurs propres règles et formulaires d'inscription.
- **Courts** : envoie courts-métrages, lie-les à des appels et à des localisations de tournage.
- **Profils avec palmarès** : palmarès lié aux festivals de la plateforme ou externe via liens, avec contrôle de confidentialité champ par champ.
- **Chat** : messages directs et de groupe ou canal par festival, avec chiffrement de bout en bout.
- **Cartes** : sièges et localisations de tournage sur cartes interactives, avec ouverture dans ton app de cartes favorite.
- **Sans connexion** : l'app continue de fonctionner offline et synchronise tes changements en récupérant la connexion.
- **Dans ta langue** : espagnol, anglais, français, allemand, italien, catalan, basque, galicien et occitan, avec détection automatique.

## Requêtes et démarrage

### Requêtes minimales

- Python 3.12+
- Flutter SDK >= 3.0.0 et < 4.0.0
- Git
- Docker et Docker Compose pour déploiement/environnement productif
- Navigateur avec support pour web (recommandé Chrome/Brave)

### Démarrage rapide

En Windows :

```bat
start.bat --dev
```

En PowerShell :

```powershell
./start.ps1 --dev
```

En Linux/macOS :

```bash
./start.sh --dev
```

Ceci lève le backend sur `http://localhost:8000` et l'app en mode local ; l'API expose Swagger/OpenAPI sur `/docs`. Tu peux désactiver l'une des deux parties avec `--no-backend` ou `--no-frontend`.

### Autres options utiles

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Consulte la référence complète du démarrage et déploiement dans [docs/HERRAMIENTAS.fr.md](docs/HERRAMIENTAS.fr.md) et [docs/USO.fr.md](docs/USO.fr.md).

## Variables d'environnement et configuration

### Backend

Crée ou ajuste `backend/.env` avec au moins :

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Pour environnement productif on utilise MariaDB ; les scripts et la documentation de déploiement le gèrent avec Docker.

### Frontend

L'app réutilise le backend par URL, normalement avec `--dart-define` :

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

Le démarrage automatique du projet configure déjà ceci quand on utilise `start.*`.

## État du projet

🚧 **En développement actif** — Festivals, courts, chat avec E2EE, cartes, mode offline et 9 langues fonctionnant ; avec tests en backend (~1400) et frontend (69 fichiers).

**Roadmap prochaine :**

- [ ] Notificaciones push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Windows MSI installer
- [x] Documentación API OpenAPI exportable (`/openapi.json` sin operationIds duplicados + `docs/API.md` regenerado)

## Documentation du projet

La carte de documentation est dans [docs/README.fr.md](docs/README.fr.md). C'est la meilleure entrée pour chaque type d'utilisateur :

- [docs/USO.fr.md](docs/USO.fr.md) : démarrage, opération, environnement et usage quotidien
- [docs/ADMINISTRACION.fr.md](docs/ADMINISTRACION.fr.md) : administration, comptes et déploiement
- [docs/INFRAESTRUCTURA.fr.md](docs/INFRAESTRUCTURA.fr.md) : Docker, ports, CI et infra
- [docs/SEGURIDAD.fr.md](docs/SEGURIDAD.fr.md) : tokens, politiques et liste de production
- [docs/ARQUITECTURA.fr.md](docs/ARQUITECTURA.fr.md) : architecture backend/frontend et flux clés
- [docs/API.md](docs/API.md) : référence d'endpoints
- [docs/DESARROLLO.fr.md](docs/DESARROLLO.fr.md) : comment ajouter endpoints ou écrans
- [docs/BACKEND.fr.md](docs/BACKEND.fr.md) : guide du backend (couches, config, auth, tests)
- [docs/DATABASE.fr.md](docs/DATABASE.fr.md) : schéma et migrations

En outre, le point de départ pour développement et convention de projet est [AGENTS.md](AGENTS.md).

### Voir aussi

- [docs/README.fr.md](docs/README.fr.md) : index général par audience
- [docs/HERRAMIENTAS.fr.md](docs/HERRAMIENTAS.fr.md) : commandes de build, test et démarrage
- [docs/FUNCIONAL.fr.md](docs/FUNCIONAL.fr.md) : usage réel du produit par rôle

### FAQ rapide

- **Ai-je besoin de Docker pour commencer ?** Non. Le démarrage local avec `start.*` fonctionne sans Docker ; Docker sert pour environnement productif et builds reproductibles.
- **Que faire si l'API ne répond pas ?** Vérifie que le backend tourne sur `http://localhost:8000` et que `/docs` répond.
- **Quel document dois-je lire d'abord ?** Si tu es utilisateur, [docs/USO.fr.md](docs/USO.fr.md) ; si tu es développeur, [docs/ARQUITECTURA.fr.md](docs/ARQUITECTURA.fr.md).
- **Comment savoir si un changement requiert mise à jour documentation ?** S'il change démarrage, API, rôles, permissions, variables d'environnement ou schéma, mets à jour aussi la documentation correspondante.

## Pour développeurs

> Détail complet dans [`AGENTS.md`](AGENTS.md) (architecture, commandes et conventions) et dans l'index de [`docs/`](docs/README.fr.md) (guides par rôle : fonctionnel, usage, administration, infrastructure, sécurité, architecture, API).

**En un coup d'œil** : backend FastAPI en couches (routers → services → modèles SQLAlchemy, SQLite en dev / MariaDB en prod, JWT + refresh, 18 migrations Alembic) ; frontend Flutter Material 3 avec dark mode (singletons + `setState()` + streams, Hive offline, 24 widgets réutilisables).

```bash
# Tests
cd backend && python -m pytest tests/ -x -q --tb=short
cd frontend && flutter test

# Lint
cd backend && ruff check . && ruff format --check .
cd frontend && flutter analyze

# Migraciones
cd backend && alembic upgrade head
```

## Développement local

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
flutter run
```

## Déploiement

```bash
docker compose --profile prod up -d
```

Backend + frontend (nginx) + MariaDB. Les builds distribués (web, Windows, Linux, Android) se gèrent avec `start.bat --build-all` et l'ensemble de scripts de [docs/HERRAMIENTAS.fr.md](docs/HERRAMIENTAS.fr.md).

## Solution de problèmes

### Le backend ne démarre pas

- Vérifie que Python 3.12+ est installé.
- Vérifie que `backend/.env` existe et est valide.
- Exécute `cd backend && python -m uvicorn app.main:app --reload` pour voir l'erreur réelle.

### L'app ne connecte pas avec l'API

- Assure-toi que le backend est sur `http://localhost:8000`.
- Révise si `BACKEND_URL` est passé avec `--dart-define`.
- Vérifie que l'API répond sur `/docs`.

### Problèmes avec bases de données ou migrations

- Utilise `cd backend && alembic upgrade head`.
- Si tu changes de SQLite à MariaDB, révise [docs/USO.fr.md](docs/USO.fr.md) et [docs/DATABASE.fr.md](docs/DATABASE.fr.md).

### Frontend avec erreurs de Flutter

- Exécute `cd frontend && flutter pub get`.
- S'il y a problèmes de génération de code, suis la documentation de Hive et build_runner dans [docs/ARQUITECTURA.fr.md](docs/ARQUITECTURA.fr.md).

## Contribuer

1. Fais un fork du dépôt.
2. Crée une branche (`git checkout -b feature/nueva-funcionalidad`).
3. Fais commit avec messages clairs et descriptifs (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Pousse la branche (`git push origin feature/nueva-funcionalidad`).
5. Ouvre une Pull Request avec contexte, changements et validation.

**Conventions de qualité :** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` et `flutter test` doivent passer avant de fusionner.

## Licence

Ce projet est sous la **Licence MIT**. Consulte [LICENSE](LICENSE).
