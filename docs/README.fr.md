# Documentation — Clakettes

Toute la documentation existe dans les 9 langues de la plateforme. L'espagnol est canonique :
[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Cet index est l'entrée principale de la documentation du projet. Il est pensé pour qu'un utilisateur, un administrateur ou un développeur trouve le bon guide sans lire des fichiers au hasard.

## Comment naviguer dans la documentation

- **Je veux utiliser l'app** → [USO.fr.md](USO.fr.md) + [FUNCIONAL.fr.md](FUNCIONAL.fr.md)
- **J'administre un déploiement** → [ADMINISTRACION.fr.md](ADMINISTRACION.fr.md) + [INFRAESTRUCTURA.fr.md](INFRAESTRUCTURA.fr.md) + [SEGURIDAD.fr.md](SEGURIDAD.fr.md)
- **Développement** → [ARQUITECTURA.fr.md](ARQUITECTURA.fr.md) + [DESARROLLO.fr.md](DESARROLLO.fr.md) + [API.md](API.md) + [DATABASE.fr.md](DATABASE.fr.md)
- **IA / agent** → [ARQUITECTURA.fr.md](ARQUITECTURA.fr.md) et le document de la tâche ; les commandes et conventions obligatoires sont dans [../AGENTS.md](../AGENTS.md)

## Principes de la documentation

- **Un seul document canonique par sujet** : [SEGURIDAD.fr.md](SEGURIDAD.fr.md), [USO.fr.md](USO.fr.md), [DATABASE.fr.md](DATABASE.fr.md) et [API.md](API.md) sont la référence officielle de leur domaine.
- **Documentation par audience** : chaque guide est écrit pour un type de lecteur, pas pour un seul ensemble de commandes.
- **Liens directs** : depuis ici on peut arriver au contenu pertinent en moins d'un clic.
- **Sans duplication inutile** : les documents secondaires lient vers le canonique au lieu de le répéter.

## Index par document

| Documento | Qué cubre | Audiencia |
|---|---|---|
| [FUNCIONAL.fr.md](FUNCIONAL.fr.md) | Utilidad real por rol y flujos (festival, inscripción, comités, premios, chat/E2EE) | usuario, admin, IA |
| [USO.fr.md](USO.fr.md) | Arranque, variables, migración SQLite↔MariaDB, backups, roles y operación | usuario, admin |
| [ADMINISTRACION.fr.md](ADMINISTRACION.fr.md) | Endpoints `/api/admin`, cuenta inicial, rotación de secretos, límites, troubleshooting | admin |
| [INFRAESTRUCTURA.fr.md](INFRAESTRUCTURA.fr.md) | Perfiles Docker, puertos, volúmenes, Nginx, health, CI (GitHub + GitLab) | admin, dev |
| [SEGURIDAD.fr.md](SEGURIDAD.fr.md) | Tokens, matriz `require_*`, perímetro, checklist producción | admin, dev |
| [ARQUITECTURA.fr.md](ARQUITECTURA.fr.md) | Mapa sistema + reglas backend/frontend + flujos clave | dev, IA |
| [API.md](API.md) | Referencia de endpoints (regenerable con `tools/gen_api.py`) | dev, IA |
| [DESARROLLO.fr.md](DESARROLLO.fr.md) | Convención para añadir endpoint/pantalla + puertas CI | dev, IA |
| [HERRAMIENTAS.fr.md](HERRAMIENTAS.fr.md) | Scripts `start.*`, builds distribuibles, Docker, fixes CI | dev |
| [PUSH.fr.md](PUSH.fr.md) | Decisión de notificaciones sin Firebase | dev |
| [DATABASE.fr.md](DATABASE.fr.md) | Esquema dual SQLite/MariaDB, fichas por modelo, ER | dev, IA |
| [BACKEND.fr.md](BACKEND.fr.md) | Guía del backend (capas, config, auth, tests) | dev |
| [AUDITORIA.fr.md](AUDITORIA.fr.md) | Informe de auditoría (rev. 10/10/2026) | referencia |

## Parcours recommandé par profil

### Utilisateur final

1. [USO.fr.md](USO.fr.md)
2. [FUNCIONAL.fr.md](FUNCIONAL.fr.md)
3. [SEGURIDAD.fr.md](SEGURIDAD.fr.md) seulement s'ils doivent revoir permissions ou environnement productif

### Administrateur de déploiement

1. [ADMINISTRACION.fr.md](ADMINISTRACION.fr.md)
2. [INFRAESTRUCTURA.fr.md](INFRAESTRUCTURA.fr.md)
3. [SEGURIDAD.fr.md](SEGURIDAD.fr.md)
4. [USO.fr.md](USO.fr.md)

### Développeur

1. [../AGENTS.md](../AGENTS.md)
2. [ARQUITECTURA.fr.md](ARQUITECTURA.fr.md)
3. [DESARROLLO.fr.md](DESARROLLO.fr.md)
4. [API.md](API.md)
5. [DATABASE.fr.md](DATABASE.fr.md)

## Conventions pour maintenir la documentation

- Mettez à jour le document canonique avant tout résumé ou index.
- Si vous changez un flux de démarrage, synchronisez [README.fr.md](../README.fr.md), [USO.fr.md](USO.fr.md) et [HERRAMIENTAS.fr.md](HERRAMIENTAS.fr.md).
- Si vous changez une API publique, mettez à jour [API.md](API.md) et, s'il y a lieu, [DESARROLLO.fr.md](DESARROLLO.fr.md).
- Si vous changez le schéma ou la persistance, révisez [DATABASE.fr.md](DATABASE.fr.md) et les migrations.

## FAQ rapide

- **Par où commencer ?** Lisez [USO.fr.md](USO.fr.md) si vous allez exploiter l'app ; lisez [ARQUITECTURA.fr.md](ARQUITECTURA.fr.md) si vous allez développer.
- **Qu'est-ce qui est canonique et quoi non ?** [USO.fr.md](USO.fr.md), [SEGURIDAD.fr.md](SEGURIDAD.fr.md), [API.md](API.md) et [DATABASE.fr.md](DATABASE.fr.md) sont la référence officielle pour ces sujets.
- **Où trouver une commande ou script ?** Révisez [HERRAMIENTAS.fr.md](HERRAMIENTAS.fr.md) et [../README.fr.md](../README.fr.md).
- **Comment savoir si un changement requiert documentation ?** S'il affecte démarrage, permissions, infrastructure, API, ou modèle de données, il doit se refléter dans la documentation pertinente.

## Voir aussi

- [../README.fr.md](../README.fr.md) : vue générale du projet
- [USO.fr.md](USO.fr.md) : opération et configuration locale
- [ADMINISTRACION.fr.md](ADMINISTRACION.fr.md) : périmètre de déploiement et administration
- [ARQUITECTURA.fr.md](ARQUITECTURA.fr.md) : carte technique du système
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

La référence complète de commandes et profils du projet est dans [HERRAMIENTAS.fr.md](HERRAMIENTAS.fr.md) et dans [../README.fr.md](../README.fr.md).
