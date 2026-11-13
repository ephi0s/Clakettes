# Documentation — Clakettes

Cet index est l'entrée principale de la documentation du projet. Il est pensé pour qu'un utilisateur, un administrateur ou un développeur trouve le bon guide sans lire des fichiers au hasard.

## Langues

Toute la documentation existe dans les 9 langues de la plateforme. L'espagnol (canarien) est canonique :
[ES](../es/README.md) · [EN](../en/README.md) · [FR](README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Comment naviguer dans la documentation

- **Je veux utiliser l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **J'administre un déploiement** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Développement** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md)
- **IA / agent** → [ARQUITECTURA.md](ARQUITECTURA.md) et le document de la tâche ; les commandes et conventions obligatoires sont dans [../AGENTS.md](../../AGENTS.md)

## Principes de la documentation

- **Un seul document canonique par sujet** : [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) et [API.md](API.md) sont la référence officielle de leur domaine.
- **Documentation par audience** : chaque guide est écrit pour un type de lecteur, pas pour un seul ensemble de commandes.
- **Liens directs** : depuis ici on peut arriver au contenu pertinent en moins d'un clic.
- **Sans duplication inutile** : les documents secondaires lient vers le canonique au lieu de le répéter.

## Index par document

| Document | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Valeur réelle par rôle et flux (festival, inscription, comités, récompenses, chat/E2EE, vote jury) | utilisateur, admin, IA |
| [USO.md](USO.md) | Démarrage, variables, migration SQLite↔MariaDB, sauvegardes, rôles et opération | utilisateur, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, compte initial, rotation de secrets, limites, dépannage | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Profils Docker, ports, volumes, Nginx, santé, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matrice `require_*`, périmètre, checklist production | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Carte du système + règles backend/frontend + flux clés | dev, IA |
| [API.md](API.md) | Référence des endpoints (regénérable avec `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convention pour ajouter un endpoint/écran + portes CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuables, Docker, corrections CI | dev |
| [PUSH.md](PUSH.md) | Décision de notification sans Firebase | dev |
| [DATABASE.md](DATABASE.md) | Schéma dual SQLite/MariaDB, fiches par modèle, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guide du backend (couches, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Rapport d'audit (rev. 10/10/2026) | référence |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocole de fédération entre nœuds (phase 4) | dev, IA |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entités fédérées minimales) | dev, IA |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Modèle de confiance fédéré, mTLS, rotation de certificats | dev, IA |

## Parcours recommandé par profil

### Utilisateur final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) seulement s'ils doivent revoir permissions ou environnement productif

### Administrateur de déploiement

1. [ADMINISTRACION.md](ADMINISTRACION.md)
2. [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md)
3. [SEGURIDAD.md](SEGURIDAD.md)
4. [USO.md](USO.md)

### Développeur

1. [../AGENTS.md](../../AGENTS.md)
2. [ARQUITECTURA.md](ARQUITECTURA.md)
3. [DESARROLLO.md](DESARROLLO.md)
4. [API.md](API.md)
5. [DATABASE.md](DATABASE.md)
6. [BACKEND.md](BACKEND.md)

## Conventions pour maintenir la documentation

- Mettez à jour le document canonique avant tout résumé ou index.
- Si vous changez un flux de démarrage, synchronisez [README.fr.md](../../README.fr.md), [USO.md](USO.md) et [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si vous changez une API publique, mettez à jour [API.md](API.md) et, s'il y a lieu, [DESARROLLO.md](DESARROLLO.md).
- Si vous changez le schéma ou la persistance, révisez [DATABASE.md](DATABASE.md) et les migrations.
- Chaque fois que vous éditez un document dans `docs/es/`, répliquez le changement aux 8 sœurs (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ rapide

- **Par où commencer ?** Lisez [USO.md](USO.md) si vous allez exploiter l'app ; lisez [ARQUITECTURA.md](ARQUITECTURA.md) si vous allez développer.
- **Qu'est-ce qui est canonique et quoi non ?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) et [DATABASE.md](DATABASE.md) sont la référence officielle pour ces sujets.
- **Où trouver une commande ou script ?** Révisez [HERRAMIENTAS.md](HERRAMIENTAS.md) et [../README.fr.md](../../README.fr.md).
- **Comment savoir si un changement requiert documentation ?** S'il affecte démarrage, permissions, infrastructure, API, ou modèle de données, il doit se refléter dans la documentation pertinente.

## Voir aussi

- [../README.fr.md](../../README.fr.md) : vue générale du projet
- [USO.md](USO.md) : opération et configuration locale
- [ADMINISTRACION.md](ADMINISTRACION.md) : périmètre de déploiement et administration
- [ARQUITECTURA.md](ARQUITECTURA.md) : carte technique du système
- [API.md](API.md) : référence d'endpoints

## Démarrage recommandé

Pour commencer dans un environnement local :

```bash
cd backend && python -m uvicorn app.main:app --reload
cd frontend && flutter run
```

Ou, en utilisant les scripts du projet :

```bat
start.bat --dev
```

La référence complète de commandes et profils du projet est dans [HERRAMIENTAS.md](HERRAMIENTAS.md) et dans [../README.fr.md](../../README.fr.md).