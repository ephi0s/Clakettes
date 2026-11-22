# Documentation — Clakettes

Cet index est l'entrée principale de la documentation du projet. Il est pensé pour qu'un utilisateur, un administrateur ou un développeur trouve le bon guide sans lire des fichiers au hasard.

## Langues

Les 18 documents communs existent dans les 9 langues de la plateforme ; `docs/es/` contient en outre deux analyses spécifiques (`AMENAZAS_NODOS_FEDERACION.md` et `MODELO_CONFIANZA_NODOS.md`). L'espagnol (canarien) est canonique :
[ES](../es/README.md) · [EN](../en/README.md) · [FR](README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

## Comment naviguer dans la documentation

- **Je veux utiliser l'application** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **J'administre un déploiement** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Développement** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](API.md) + [DATABASE.md](DATABASE.md) + [BACKEND.md](BACKEND.md) + [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
- **Référence pour les agents** → les commandes et conventions de développement sont dans [../AGENTS.md](../../AGENTS.md)

## Principes de la documentation

- **Un seul document canonique par sujet** : [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) et [API.md](API.md) sont la référence officielle de leur domaine.
- **Documentation par public** : chaque guide est écrit pour un type de lecteur, pas pour un seul jeu de commandes.
- **Liens directs** : depuis ici, le contenu pertinent est à moins d'un clic.
- **Pas de duplication inutile** : les documents secondaires renvoient au canonique au lieu de le répéter.

## Index des documents

| Document | Ce qu'il couvre | Public |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilité réelle par rôle et flux (festival, inscription, comités, prix, chat/E2EE, vote du jury) | utilisateur, admin |
| [USO.md](USO.md) | Démarrage, variables, migration SQLite↔MariaDB, sauvegardes, rôles et exploitation | utilisateur, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, compte initial, rotation des secrets, limites, dépannage | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Profils Docker, ports, volumes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matrice `require_*`, périmètre, checklist production | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Carte du système + règles backend/frontend + flux clés | dev |
| [API.md](API.md) | Référence des endpoints | dev |
| [DESARROLLO.md](DESARROLLO.md) | Convention pour ajouter endpoint/écran + portes CI | dev |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuables, Docker, correctifs CI | dev |
| [PUSH.md](PUSH.md) | Décision de notification sans Firebase | dev |
| [DATABASE.md](DATABASE.md) | Schéma dual SQLite/MariaDB, fiches par modèle, ER | dev |
| [BACKEND.md](BACKEND.md) | Guide du backend (couches, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Rapport d'audit (rév. 10/10/2026) | référence |
| [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md) | Protocole de fédération entre nœuds (phases 2 à 10) | dev |
| [FEDERATION_SCHEMA.md](FEDERATION_SCHEMA.md) | Clakettes Schema v1 (entités minimales fédérées) | dev |
| [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md) | Modèle de confiance fédéré, mTLS, manifeste signé, portabilité, chat et résilience | dev |
| [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md) | Décision de broker (NATS JetStream) pour le chat et les événements entre nœuds ; transport aujourd'hui implémenté : `DurableQueueBackend` sur `chat_outbox` avec WebSocket de bord | dev |
| [AMENAZAS_NODOS_FEDERACION.md](../es/AMENAZAS_NODOS_FEDERACION.md) | Modèle de menaces des nœuds fédérés (uniquement en espagnol) | dev |
| [MODELO_CONFIANZA_NODOS.md](../es/MODELO_CONFIANZA_NODOS.md) | Modèle de confiance entre nœuds (uniquement en espagnol) | dev |

## Parcours recommandé par profil

### Utilisateur final

1. [USO.md](USO.md)
2. [FUNCIONAL.md](FUNCIONAL.md)
3. [SEGURIDAD.md](SEGURIDAD.md) seulement s'il doit vérifier les permissions ou l'environnement de production

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
7. [FEDERATION_PROTOCOL.md](FEDERATION_PROTOCOL.md)
8. [FEDERATION_SECURITY.md](FEDERATION_SECURITY.md)
9. [FEDERATION_CHAT_BROKER.md](FEDERATION_CHAT_BROKER.md)

## Conventions pour maintenir la documentation

- Mettez à jour le document canonique avant tout résumé ou index.
- Si vous changez un flux de démarrage, synchronisez [README.md](../../README.md), [USO.md](USO.md) et [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si vous changez une API publique, mettez à jour [API.md](API.md) et, le cas échéant, [DESARROLLO.md](DESARROLLO.md).
- Si vous changez le schéma ou la persistance, vérifiez [DATABASE.md](DATABASE.md) et les migrations.
- Chaque fois que vous modifiez un document dans `docs/es/`, répliquez le changement dans les 8 sœurs (`docs/<idioma>/X.md`, `README.<lang>.md`, `frontend/README.<lang>.md`).

## FAQ rapide

- **Par où commencer ?** Lisez [USO.md](USO.md) si vous allez exploiter l'application ; lisez [ARQUITECTURA.md](ARQUITECTURA.md) si vous allez développer.
- **Qu'est-ce qui est canonique et qu'est-ce qui ne l'est pas ?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](API.md) et [DATABASE.md](DATABASE.md) sont la référence officielle pour ces sujets.
- **Où trouver une commande ou un script ?** Consultez [HERRAMIENTAS.md](HERRAMIENTAS.md) et [../README.md](../../README.md).
- **Comment savoir si un changement nécessite de la documentation ?** S'il affecte le démarrage, les permissions, l'infrastructure, l'API ou le modèle de données, il doit être reflété dans la documentation pertinente.

## Voir aussi

- [../README.md](../../README.md) : vue d'ensemble du projet
- [USO.md](USO.md) : exploitation et configuration locale
- [ADMINISTRACION.md](ADMINISTRACION.md) : périmètre de déploiement et administration
- [ARQUITECTURA.md](ARQUITECTURA.md) : carte technique du système
- [API.md](API.md) : référence des endpoints
