# Documentation — Clakettes

Toute la documentation existe dans les 9 langues de la plateforme. L'espagnol est canonique :
[ES](../es/README.md) · [EN](../en/README.md) · [FR](README.md) · [DE](../de/README.md) · [IT](../it/README.md) · [CA](../ca/README.md) · [EU](../eu/README.md) · [GL](../gl/README.md) · [OC](../oc/README.md)

Cet index est l'entrée principale de la documentation du projet. Il est pensé pour qu'un utilisateur, un administrateur ou un développeur trouve le bon guide sans lire des fichiers au hasard.

## Comment naviguer dans la documentation

- **Je veux utiliser l'app** → [USO.md](USO.md) + [FUNCIONAL.md](FUNCIONAL.md)
- **J'administre un déploiement** → [ADMINISTRACION.md](ADMINISTRACION.md) + [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) + [SEGURIDAD.md](SEGURIDAD.md)
- **Développement** → [ARQUITECTURA.md](ARQUITECTURA.md) + [DESARROLLO.md](DESARROLLO.md) + [API.md](../es/API.md) + [DATABASE.md](DATABASE.md)
- **IA / agent** → [ARQUITECTURA.md](ARQUITECTURA.md) et le document de la tâche ; les commandes et conventions obligatoires sont dans [../AGENTS.md](../../AGENTS.md)

## Principes de la documentation

- **Un seul document canonique par sujet** : [SEGURIDAD.md](SEGURIDAD.md), [USO.md](USO.md), [DATABASE.md](DATABASE.md) et [API.md](../es/API.md) sont la référence officielle de leur domaine.
- **Documentation par audience** : chaque guide est écrit pour un type de lecteur, pas pour un seul ensemble de commandes.
- **Liens directs** : depuis ici on peut arriver au contenu pertinent en moins d'un clic.
- **Sans duplication inutile** : les documents secondaires lient vers le canonique au lieu de le répéter.

## Index par document

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.md](FUNCIONAL.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.md](USO.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.md](ADMINISTRACION.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.md](INFRAESTRUCTURA.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.md](SEGURIDAD.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](../es/API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.md](DESARROLLO.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.md](HERRAMIENTAS.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.md](PUSH.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.md](DATABASE.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.md](BACKEND.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.md](AUDITORIA.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

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
4. [API.md](../es/API.md)
5. [DATABASE.md](DATABASE.md)

## Conventions pour maintenir la documentation

- Mettez à jour le document canonique avant tout résumé ou index.
- Si vous changez un flux de démarrage, synchronisez [README.fr.md](../../README.fr.md), [USO.md](USO.md) et [HERRAMIENTAS.md](HERRAMIENTAS.md).
- Si vous changez une API publique, mettez à jour [API.md](../es/API.md) et, s'il y a lieu, [DESARROLLO.md](DESARROLLO.md).
- Si vous changez le schéma ou la persistance, révisez [DATABASE.md](DATABASE.md) et les migrations.

## FAQ rapide

- **Par où commencer ?** Lisez [USO.md](USO.md) si vous allez exploiter l'app ; lisez [ARQUITECTURA.md](ARQUITECTURA.md) si vous allez développer.
- **Qu'est-ce qui est canonique et quoi non ?** [USO.md](USO.md), [SEGURIDAD.md](SEGURIDAD.md), [API.md](../es/API.md) et [DATABASE.md](DATABASE.md) sont la référence officielle pour ces sujets.
- **Où trouver une commande ou script ?** Révisez [HERRAMIENTAS.md](HERRAMIENTAS.md) et [../README.fr.md](../../README.fr.md).
- **Comment savoir si un changement requiert documentation ?** S'il affecte démarrage, permissions, infrastructure, API, ou modèle de données, il doit se refléter dans la documentation pertinente.

## Voir aussi

- [../README.fr.md](../../README.fr.md) : vue générale du projet
- [USO.md](USO.md) : opération et configuration locale
- [ADMINISTRACION.md](ADMINISTRACION.md) : périmètre de déploiement et administration
- [ARQUITECTURA.md](ARQUITECTURA.md) : carte technique du système
- [API.md](../es/API.md) : référence d'endpoints

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
