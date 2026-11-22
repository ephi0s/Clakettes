# Évaluation du broker pour le chat et les événements : MQTT 5 contre NATS JetStream

[ES](../es/FEDERATION_CHAT_BROKER.md) · [EN](../en/FEDERATION_CHAT_BROKER.md) · [FR](FEDERATION_CHAT_BROKER.md) · [DE](../de/FEDERATION_CHAT_BROKER.md) · [IT](../it/FEDERATION_CHAT_BROKER.md) · [CA](../ca/FEDERATION_CHAT_BROKER.md) · [EU](../eu/FEDERATION_CHAT_BROKER.md) · [GL](../gl/FEDERATION_CHAT_BROKER.md) · [OC](../oc/FEDERATION_CHAT_BROKER.md)

Ce document clôt l'évaluation en attente sur le transport à utiliser pour le chat et la propagation d'événements entre les nœuds de Clakettes. La décision est contraignante pour la Phase 8 (le chat comme file fédérée) et coexiste avec le backend WebSocket actuel décrit dans `docs/es/ARQUITECTURA.md`.

**État d'implémentation (Phases 6-10) :** la décision adopte NATS JetStream comme cible, mais aujourd'hui le transport durable en production est `DurableQueueBackend` sur la table `chat_outbox` avec délégué WebSocket. Les variables `NATS_*` et le flag `CHAT_BACKEND` du plan de migration **n'existent pas encore** dans `.env.example` ni dans `app/config.py` : `/api/federation/chat/bridge/config` n'indique que la destination prévue (`"transport": "nats-jetstream"`).

## Critères pondérés

Pondérations sur 100, note de 1 (déficient) à 5 (optimal). La contribution est pondération × note / 100.

| Critère | Poids | MQTT 5 | Contrib. | NATS JetStream | Contrib. |
|---|---:|---:|---:|---:|---:|
| Persistance | 15 | 2 | 0,30 | 5 | 0,75 |
| Ordre | 12 | 3 | 0,36 | 5 | 0,60 |
| Déduplication | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Signature des messages | 8 | 3 | 0,24 | 4 | 0,32 |
| Bridges fédérés | 18 | 2 | 0,36 | 5 | 0,90 |
| Empreinte opérationnelle | 10 | 3 | 0,30 | 5 | 0,50 |
| Compatibilité FastAPI/SQLite | 8 | 3 | 0,24 | 4 | 0,32 |
| Coût de déploiement | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Pourquoi ces chiffres

- **Persistance** : MQTT 5 offre des sessions durables et des messages retenus, mais l'historique réel finit dans une base externe ; JetStream fournit des streams avec rétention configurable, relecture et consommateurs durables dans le binaire lui-même.
- **Ordre** : MQTT préserve l'ordre par topic tant que la session vit ; à la reconnexion ou à travers un bridge, l'ordre se dégrade. JetStream fournit un numéro de séquence par subject dans le stream.
- **Déduplication** : le QoS 1 de MQTT duplique après reconnexion et le QoS 2 est coûteux à opérer ; JetStream apporte la déduplication de publication via l'en-tête `Nats-Msg-Id` dans une fenêtre configurable (2 min par défaut).
- **mTLS** : les deux le prennent en charge. MQTT le délègue au broker en place ; NATS l'intègre avec TLS mutuel et, en plus, les identités NKeys/JWT.
- **Signature des messages** : les deux exigent une signature au niveau de l'application avec la clé TLS du nœud ; NATS convient mieux car les en-têtes voyagent sans transformation de bout en bout.
- **Bridges fédérés** : critère au poids le plus élevé. MQTT est en hub-and-spoke et chaque fabricant définit son bridge ; NATS apporte les leaf nodes et les gateways comme primitives de premier niveau, avec subject mapping.
- **Empreinte opérationnelle et coût** : un seul binaire `nats-server` (Apache-2.0, JetStream inclus) contre un broker MQTT qui traîne généralement une base pour persister et des règles d'affinité de session.
- **FastAPI/SQLite** : le client `nats-py` est asynchrone et s'accorde avec les méthodes `async` de `ChatBackend` ; la vérification de signature réutilise `cryptography`, déjà présent dans `backend/requirements.txt`.

## Décision

**NATS JetStream gagne** (4,84 contre 2,65). Ce n'est pas un match nul : le critère au poids le plus élevé, les bridges fédérés, est celui où l'écart est le plus grand et où ce projet a une exigence absolue.

Raisons concrètes pour Clakettes :

1. **Le modèle de confiance existant convient sans rien inventer de nouveau** : `docs/es/FEDERATION_SECURITY.md` définit l'identité d'un nœud comme domaine + certificat X.509, mTLS contre une CA et `trusted_nodes` avec empreinte SHA-256. Les leaf nodes de NATS s'authentifient avec ce même mTLS, si bien que le bridge entre nœuds hérite de la rotation et de la révocation déjà documentées (mettre `allowed = false` et le handshake échoue).
2. **Ordre + déduplication + persistance viennent du même endroit** : l'échange d'entités de `docs/es/FEDERATION_SCHEMA.md` inclut `message` avec `node_origin` et `created_at`. Un stream par subject avec numéro de séquence et déduplication via `Nats-Msg-Id` (en utilisant le `message_id` persisté comme clé d'idempotence) évite de réécrire cette logique dans chaque consommateur.
3. **Un seul binaire pour deux besoins** : le même `nats-server` sert le bus d'événements éphémère (Core NATS, câblage des hubs et événements de salle) et le bus durable (JetStream, messagerie et rapports). Cela s'accorde avec le déploiement Docker actuel (backend 8000, frontend 3000, MariaDB 3306) sans ajouter un autre service avec sa propre base.
4. **Le client est asynchrone par nature** : `nats-py` s'intègre dans le `lifespan` de FastAPI aux côtés de l'initialisation de Hive et du registry, sans fils ni ponts supplémentaires.

Inconvénients atténués :

1. **Pas d'exactly-once comme le QoS 2 de MQTT** : JetStream est at-least-once. Atténuation : déduplication de publication via `Nats-Msg-Id` plus des consommateurs idempotents qui utilisent `message_id` comme clé d'idempotence ; SQLite reste la source de vérité et l'état du message est écrit avant la publication.
2. **Le navigateur ne parle pas nativement le protocole NATS** : le frontend utilise `web_socket_channel` (voir `frontend/pubspec.yaml`). Atténuation : le WebSocket de bord reste en vie ; le backend abonne un consommateur JetStream et relaie vers le `ConnectionManager` existant. Le changement est interne et l'API que voit Flutter n'est pas touchée.
3. **Le listener MQTT de `nats-server` ne comprend que MQTT 3.1.1** (il rejette les CONNECT MQTT 5) : si à l'avenir apparaît un appareil exigeant MQTT 5, on mettra en place un broker MQTT de bord dédié qui publiera dans le même stream. Cela reste hors du périmètre actuel : il n'y a pas d'appareils MQTT dans l'inventaire de `frontend/pubspec.yaml`.

## Conséquences d'implémentation

### Backend abstrait

L'interface `ChatBackend` existe déjà dans `backend/app/chat_backend/base.py` avec `start()`, `stop()` et `send_message(...)`, et `backend/app/chat_backend/registry.py` permet de remplacer l'implémentation en l'enregistrant une seule fois au démarrage. Il n'y a rien à toucher ni à l'interface ni aux routers : on ajoute une nouvelle implémentation, `NatsJetStreamChatBackend`, qui dans `start()` se connecte à `NATS_URL`, déclare le stream `CLAKETTES_EVENTS` sur le subject `clakettes.events.>` et crée le consommateur durable de bord ; dans `stop()` il fait un `drain` et ferme la connexion ; dans `send_message(...)` il publie la même charge utile que construit aujourd'hui `WebSocketChatBackend`, plus des en-têtes avec `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) et `signature`. La signature est RS256 sur la représentation canonique du message avec la clé privée du certificat TLS du nœud, la même qui signe le manifeste (`docs/es/FEDERATION_PROTOCOL.md`). Le pair la valide contre son JWKS ou contre le certificat du manifeste avant d'appliquer l'événement.

### Fallback mononœud

Il est conservé tel quel : `WebSocketChatBackend` reste le backend enregistré par défaut en développement et avec `TESTING=true`. SQLite conserve la table des messages comme source de vérité ; le frontend continue avec Hive (`OfflineCacheService`) et la file FIFO (`SyncQueueService`) pour le mode hors ligne. Si le broker n'est pas disponible, `send_message` met l'événement en file dans la file de synchronisation avec le même `message_id`/`event_id` et il est rejoué à la reconnexion, sans doublons. Le WebSocket de bord continue de livrer aux connexions authentifiées gérées aujourd'hui par `ConnectionManager`.

### Bridge entre nœuds

Chaque nœud démarre son `nats-server` avec JetStream et déclare un leaf node (ou un gateway entre clusters) vers le nœud hub. Le leaf s'authentifie avec mTLS en utilisant la CA fédérée ; le certificat du pair est validé contre `trusted_nodes.cert_fingerprint_sha256`. Le subject mapping sépare les événements par `node_origin`, par canal et par type, de sorte que les politiques existantes `disable_chat`, `minimize_data`, `import_only`, `consent_required` et `disable_search` sont appliquées dans le consommateur entrant avant persistance. La révocation d'un pair reste immédiate : en passant `allowed = false`, le prochain handshake mTLS du leaf échoue et ses événements cessent d'arriver.

## Plan de migration en 4 étapes

1. **Préparer** : ajouter `nats-py` à `backend/requirements.txt` et les variables `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` à `.env.example`. Implémenter `NatsJetStreamChatBackend` derrière le flag `CHAT_BACKEND=nats`. Le registry continue d'enregistrer WebSocket par défaut : aucun test existant ne change.
2. **Ombre** : publier aussi dans NATS sans que personne ne consomme pour la livraison ; un consommateur de validation vérifie séquence, déduplication et signature entre deux nœuds en staging. La livraison réelle passe toujours par WebSocket.
3. **Bascule** : enregistrer le backend NATS en production et convertir l'endpoint WebSocket en bridge : son consommateur JetStream alimente `ConnectionManager.broadcast()`. Ajouter des tests ponctuels du bridge avec le double de transport et `TESTING=true`, sans démarrer de broker réel dans la suite. Livraison en parallèle : WS reste actif pendant le changement.
4. **Clore** : retirer la diffusion en processus pour la messagerie entre nœuds, activer les leaf nodes mTLS entre deux nœuds réels et laisser le mode mononœud comme fallback documenté. Mettre à jour dans le même changement l'API (`python tools/gen_api.py --all`), les chiffres et la roadmap du README, et répliquer cette doc dans les huit sœurs selon la règle de `AGENTS.md`.

## État

**Décision adoptée le 2026-11-20 : NATS JetStream comme broker de chat et d'événements**, avec WebSocket comme bord et fallback mononœud, et MQTT 5 écarté pour le cœur fédéré.

Cela débloque l'item « Évaluer le broker (MQTT vs NATS JetStream) pour le chat et les événements » lui-même et, par dépendance directe, les travaux de chat fédéré entre nœuds, de propagation d'événements entre instances et de bridge mTLS avec signature des messages. Cela ne débloque ni ne remplace le modèle de confiance ni les endpoints de fédération déjà documentés : ils sont réutilisés tels quels.
