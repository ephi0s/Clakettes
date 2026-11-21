# Avaliación de broker para chat e eventos: MQTT 5 fronte a NATS JetStream

[GL](FEDERATION_CHAT_BROKER.md)

Este documento pecha a avaliación pendente sobre que transporte usar para o chat e a propagación de eventos entre nodos de Clakettes. A decisión é vinculante para a Fase 8 (chat como cola federada) e convive co backend WebSocket actual descrito en `docs/es/ARQUITECTURA.md`.

## Criterios ponderados

Pesos sobre 100, puntuación de 1 (deficiente) a 5 (óptimo). A contribución é peso × puntuación / 100.

| Criterio | Peso | MQTT 5 | Contrib. | NATS JetStream | Contrib. |
|---|---:|---:|---:|---:|---:|
| Persistencia | 15 | 2 | 0,30 | 5 | 0,75 |
| Orde | 12 | 3 | 0,36 | 5 | 0,60 |
| Deduplicación | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Sinatura de mensaxes | 8 | 3 | 0,24 | 4 | 0,32 |
| Bridges federados | 18 | 2 | 0,36 | 5 | 0,90 |
| Pegada operativa | 10 | 3 | 0,30 | 5 | 0,50 |
| Compatibilidade FastAPI/SQLite | 8 | 3 | 0,24 | 4 | 0,32 |
| Custo de despregue | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Por que estas cifras

- **Persistencia**: MQTT 5 ofrece sesións duradeiras e mensaxes retidas, pero o historial real acaba nunha base externa; JetStream dá streams con retención configurable, replay e consumidores duradeiros no propio binario.
- **Orde**: MQTT preserva a orde por tópico mentres a sesión vive; ao reconectar ou cruzar un bridge, a orde degrádase. JetStream dá un número de secuencia por subject dentro do stream.
- **Deduplicación**: o QoS 1 de MQTT duplica tras reconectar e o QoS 2 é custoso de operar; JetStream trae a deduplicación de publicación pola cabeceira `Nats-Msg-Id` nunha xanela configurable (2 min por defecto).
- **mTLS**: ambos o soportan. MQTT delegao ao broker de turno; NATS intégrao con TLS mutuo e, ademais, identidades NKeys/JWT.
- **Sinatura de mensaxes**: ambos requiren sinatura a nivel de aplicación coa chave TLS do nodo; NATS encaixa mellor porque as cabeceiras viaxan sen transformación de extremo a extremo.
- **Bridges federados**: criterio de maior peso. MQTT é hub-and-spoke e cada fabricante define o seu bridge; NATS trae leaf nodes e gateways como primitivas de primeira liña, con subject mapping.
- **Pegada operativa e custo**: un único binario `nats-server` (Apache-2.0, JetStream incluído) fronte a un broker MQTT que adoita arrastrar unha base para persistir e regras de afinidade de sesión.
- **FastAPI/SQLite**: o cliente `nats-py` é asíncrono e encaixa cos métodos `async` de `ChatBackend`; a verificación de sinatura reutiliza `cryptography`, xa presente en `backend/requirements.txt`.

## Decisión

**Gaña NATS JetStream** (4,84 fronte a 2,65). Non é un empate: o criterio con máis peso, os bridges federados, é onde a diferenza é maior e onde este proxecto ten un requisito duro.

Razóns concretas para Clakettes:

1. **O modelo de confianza existente encaixa sen inventar nada novo**: `docs/es/FEDERATION_SECURITY.md` define a identidade de nodo como dominio + certificado X.509, mTLS contra unha CA e `trusted_nodes` con pegada SHA-256. Os leaf nodes de NATS autentícanse con ese mesmo mTLS, de modo que o bridge entre nodos herda a rotación e a revogación xa documentadas (marcar `allowed = false` e o handshake falla).
2. **Orde + deduplicación + persistencia veñen do mesmo sitio**: o intercambio de entidades de `docs/es/FEDERATION_SCHEMA.md` inclúe `message` con `node_origin` e `created_at`. Un stream por subject con número de secuencia e deduplicación por `Nats-Msg-Id` (usando o `message_id` persistido como chave de idempotencia) evita reescribir esa lóxica en cada consumidor.
3. **Un só binario para dúas necesidades**: o mesmo `nats-server` serve o bus de eventos efémero (Core NATS, cableado de hubs e eventos de sala) e o bus duradeiro (JetStream, mensaxería e informes). Encaixa co despregue Docker actual (backend 8000, frontend 3000, MariaDB 3306) sen engadir outro servizo coa súa base.
4. **O cliente é asíncrono por natureza**: `nats-py` intégrase no `lifespan` de FastAPI xunto á inicialización de Hive e do registry, sen fíos nin bridges extra.

Inconvenientes mitigados:

1. **Non hai exactly-once como o QoS 2 de MQTT**: JetStream é at-least-once. Mitigación: deduplicación de publicación por `Nats-Msg-Id` máis consumidores idempotentes que usan `message_id` como chave de idempotencia; SQLite segue a ser a fonte de verdade e o estado da mensaxe escríbese antes de publicar.
2. **O navegador non fala o protocolo NATS de forma nativa**: o frontend usa `web_socket_channel` (ver `frontend/pubspec.yaml`). Mitigación: o WebSocket de borde segue vivo; o backend subscribe un consumidor de JetStream e reenvía ao `ConnectionManager` existente. O cambio é interno e a API que ve Flutter non se toca.
3. **O listener MQTT de `nats-server` só entende MQTT 3.1.1** (rexeita o CONNECT de MQTT 5): se no futuro aparece un dispositivo que esixa MQTT 5, montarase un broker MQTT de borde dedicado que publique no mesmo stream. Queda fóra do alcance actual: non hai dispositivos MQTT no inventario de `frontend/pubspec.yaml`.

## Consecuencias de implementación

### Backend abstracto

A interface `ChatBackend` xa existe en `backend/app/chat_backend/base.py` con `start()`, `stop()` e `send_message(...)`, e `backend/app/chat_backend/registry.py` permite substituír a implementación rexistrándoa unha soa vez no arranque. Non hai que tocar nin a interface nin os routers: engádese unha implementación nova, `NatsJetStreamChatBackend`, que en `start()` conecta con `NATS_URL`, declara o stream `CLAKETTES_EVENTS` sobre o subject `clakettes.events.>` e crea o consumidor duradeiro de borde; en `stop()` fai `drain` e pecha a conexión; en `send_message(...)` publica o mesmo payload que hoxe constrúe `WebSocketChatBackend`, máis cabeceiras con `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) e `signature`. A sinatura é RS256 sobre a representación canónica da mensaxe coa chave privada do certificado TLS do nodo, a mesma que asina o manifesto (`docs/es/FEDERATION_PROTOCOL.md`). O par validaa contra o seu JWKS ou contra o certificado do manifesto antes de aplicar o evento.

### Fallback mononodo

Mantense tal cal: `WebSocketChatBackend` segue a ser o backend rexistrado por defecto en desenvolvemento e con `TESTING=true`. SQLite conserva a táboa de mensaxes como fonte de verdade; o frontend segue con Hive (`OfflineCacheService`) e a cola FIFO (`SyncQueueService`) para o modo offline. Se o broker non está dispoñible, `send_message` encola o evento na cola de sincronización co mesmo `message_id`/`event_id` e réplayase ao reconectar, sen duplicados. O WebSocket de borde segue entregando ás conexións autenticadas que hoxe xestiona `ConnectionManager`.

### Bridge entre nodos

Cada nodo levanta o seu `nats-server` con JetStream e declara un leaf node (ou un gateway entre clústeres) cara ao nodo hub. O leaf autentícase con mTLS usando a CA federada; o certificado do par valídase contra `trusted_nodes.cert_fingerprint_sha256`. O subject mapping separa os eventos por `node_origin`, por canle e por tipo, de modo que as políticas existentes `disable_chat`, `minimize_data`, `import_only`, `consent_required` e `disable_search` se aplican no consumidor de entrada antes de persistir. A revogación dun par segue sendo inmediata: ao cambiar `allowed = false`, o seguinte handshake mTLS do leaf falla e os seus eventos deixan de entrar.

## Plan de migración en 4 pasos

1. **Preparar**: engadir `nats-py` a `backend/requirements.txt` e as variables `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` a `.env.example`. Implementar `NatsJetStreamChatBackend` tras a bandeira `CHAT_BACKEND=nats`. O registry segue rexistrando WebSocket por defecto: ningún test existente cambia.
2. **Sombra**: publicar tamén en NATS sen que ninguén consuma para entregar; un consumidor de validación comproba secuencia, deduplicación e sinatura entre dous nodos en staging. A entrega real segue a ir por WebSocket.
3. **Cut-over**: rexistrar o backend NATS en produción e converter o endpoint WebSocket en bridge: o seu consumidor de JetStream alimenta `ConnectionManager.broadcast()`. Engadir probas puntuais do bridge co dobre de transporte e `TESTING=true`, sen arrancar un broker real na suite. Entrega en paralelo: WS segue activo durante o cambio.
4. **Pechar**: retirar a difusión en proceso para a mensaxería entre nodos, activar os leaf nodes mTLS entre dous nodos reais e deixar o modo mononodo como fallback documentado. Actualizar no mesmo cambio a API (`python tools/gen_api.py --all`), as cifras e o roadmap do README, e replicar este doc nas oito irmás segundo a norma de `AGENTS.md`.

## Estado

**Decisión adoptada o 2026-11-20: NATS JetStream como broker de chat e eventos**, con WebSocket como borde e fallback mononodo, e MQTT 5 descartado para o núcleo federado.

Desbloquea o propio ítem «Avaliar broker (MQTT vs NATS JetStream) para chat e eventos» e, por dependencia directa, os traballos de chat federado entre nodos, propagación de eventos entre instancias e bridge mTLS con sinatura de mensaxes. Non desbloquea nin substitúe o modelo de confianza nin os endpoints de federación xa documentados: reutilízaos tal cal.
