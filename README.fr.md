# Clakettes

La plateforme où les festivals de cinéma vivent toute l'année : appels, courts, équipes, lieux et public au même endroit.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Fonctionne en web, Android, iOS et bureau (Windows, macOS, Linux), dans toutes les langues de la plateforme et aussi sans connexion.

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
- **Sans connexion** : l'app continue de fonctionner offline, conserve la provenance de chaque nœud en cache et synchronise tes changements en récupérant la connexion.
- **Fédération** : nœuds de confiance avec mTLS, portabilité d'identité, chat et événements entre nœuds, modération, métriques et résilience.
- **Dans ta langue** : espagnol, anglais, français, allemand, italien, catalan, basque, galicien et occitan, avec détection automatique du locale du système.

## Requêtes et démarrage

### Requêtes minimales

- Python 3.12+
- Flutter SDK >= 3.0.0 et < 4.0.0
- Git
- Docker et Docker Compose pour déploiement/environnement productif
- Navigateur avec support pour web (recommandé Chrome/Brave)

### Démarrage rapide

En PowerShell :

```powershell
./start.ps1 --dev
```

En Linux/macOS :

```bash
./start.sh --dev
```

Ceci lève le backend sur `http://localhost:8000` et l'app en mode local ; l'API expose Swagger/OpenAPI sur `/docs`. Tu peux désactiver l'une des deux parties avec `--no-backend` ou `--no-frontend`.

## Variables d'environnement et configuration

### Backend

Crée ou ajuste `backend/.env` avec au moins :

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
APP_ENV=development
PUBLIC_BASE_URL=https://tu-dominio.com
# Fédération avec mTLS (production)
MTLS_REQUIRED=false
MTLS_CA_BUNDLE_PATH=
MTLS_CLIENT_CERT_PATH=
MTLS_CLIENT_KEY_PATH=
# Paiements (mock par défaut ; Stripe/Redsys sur demande)
PAYMENTS_PROVIDER=mock
```

Pour environnement productif on utilise MariaDB ; les scripts et la documentation de déploiement le gèrent avec Docker.

### Frontend

L'app réutilise le backend par URL, normalement avec `--dart-define` :

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

Le démarrage automatique du projet configure déjà ceci quand on utilise `start.*`.

## Documentation du projet

La carte de documentation est dans [docs/fr/README.md](docs/fr/README.md). C'est la meilleure entrée pour chaque type d'utilisateur :

- [docs/fr/USO.md](docs/fr/USO.md) : démarrage, opération, environnement et usage quotidien
- [docs/fr/ADMINISTRACION.md](docs/fr/ADMINISTRACION.md) : administration, comptes et déploiement
- [docs/fr/INFRAESTRUCTURA.md](docs/fr/INFRAESTRUCTURA.md) : Docker, ports, CI et infra
- [docs/fr/SEGURIDAD.md](docs/fr/SEGURIDAD.md) : tokens, politiques et liste de production
- [docs/fr/ARQUITECTURA.md](docs/fr/ARQUITECTURA.md) : architecture backend/frontend et flux clés
- [docs/fr/API.md](docs/fr/API.md) : référence d'endpoints
- [docs/fr/DESARROLLO.md](docs/fr/DESARROLLO.md) : comment ajouter endpoints ou écrans
- [docs/fr/BACKEND.md](docs/fr/BACKEND.md) : guide du backend (couches, config, auth, tests)
- [docs/fr/DATABASE.md](docs/fr/DATABASE.md) : schéma et migrations
- [docs/fr/FEDERATION_PROTOCOL.md](docs/fr/FEDERATION_PROTOCOL.md) : protocole entre nœuds (phases 2-10)
- [docs/fr/FEDERATION_SECURITY.md](docs/fr/FEDERATION_SECURITY.md) : confiance, mTLS, portabilité et résilience
- [docs/fr/FEDERATION_SCHEMA.md](docs/fr/FEDERATION_SCHEMA.md) : entités fédérées et checksum
- [docs/fr/FEDERATION_CHAT_BROKER.md](docs/fr/FEDERATION_CHAT_BROKER.md) : décision de transport et état implémenté

En outre, le point de départ pour développement et convention de projet est [AGENTS.md](AGENTS.md).

### Voir aussi

- [docs/fr/README.md](docs/fr/README.md) : index général par audience
- [docs/fr/HERRAMIENTAS.md](docs/fr/HERRAMIENTAS.md) : commandes de build, test et démarrage
- [docs/fr/FUNCIONAL.md](docs/fr/FUNCIONAL.md) : usage réel du produit par rôle

### FAQ rapide

- **Ai-je besoin de Docker pour commencer ?** Non. Le démarrage local avec `start.*` fonctionne sans Docker ; Docker sert pour environnement productif et builds reproductibles.
- **Que faire si l'API ne répond pas ?** Vérifie que le backend tourne sur `http://localhost:8000` et que `/docs` répond.
- **Quel document dois-je lire d'abord ?** Si tu es utilisateur, [docs/fr/USO.md](docs/fr/USO.md) ; si tu es développeur, [docs/fr/ARQUITECTURA.md](docs/fr/ARQUITECTURA.md).
- **Comment savoir si un changement requiert mise à jour documentation ?** S'il change démarrage, API, rôles, permissions, variables d'environnement ou schéma, mets à jour aussi la documentation correspondante.

## Contribuer

1. Fais un fork du dépôt.
2. Crée une branche (`git checkout -b feature/nueva-funcionalidad`).
3. Fais commit avec messages clairs et descriptifs (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Pousse la branche (`git push origin feature/nueva-funcionalidad`).
5. Ouvre une Pull Request avec contexte, changements et validation.

**Conventions de qualité :** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` et `flutter test` doivent passer avant de fusionner. GitHub Actions exécute ces portes en parallèle et Dependabot ouvre des PR hebdomadaires groupées : patch/minor se fusionnent seuls avec une CI verte, major reste à revue manuelle (détail dans [docs/fr/INFRAESTRUCTURA.md](docs/fr/INFRAESTRUCTURA.md)).

## Licence

Ce projet est sous la **Licence MIT**. Consulte [LICENSE](LICENSE).
