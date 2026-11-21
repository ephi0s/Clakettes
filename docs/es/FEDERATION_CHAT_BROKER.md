# Evaluación de broker para chat y eventos: MQTT 5 frente a NATS JetStream

[ES](FEDERATION_CHAT_BROKER.md)

Este documento cierra la evaluación pendiente sobre qué transporte usar para el chat y la propagación de eventos entre nodos de Clakettes. La decisión es vinculante para la Fase 8 (chat como cola federada) y convive con el backend WebSocket actual descrito en `docs/es/ARQUITECTURA.md`.

## Criterios ponderados

Pesos sobre 100, puntuación de 1 (deficiente) a 5 (óptimo). La contribución es peso × puntuación / 100.

| Criterio | Peso | MQTT 5 | Contrib. | NATS JetStream | Contrib. |
|---|---:|---:|---:|---:|---:|
| Persistencia | 15 | 2 | 0,30 | 5 | 0,75 |
| Orden | 12 | 3 | 0,36 | 5 | 0,60 |
| Deduplicación | 12 | 2 | 0,24 | 5 | 0,60 |
| mTLS | 10 | 4 | 0,40 | 5 | 0,50 |
| Firma de mensajes | 8 | 3 | 0,24 | 4 | 0,32 |
| Bridges federados | 18 | 2 | 0,36 | 5 | 0,90 |
| Huella operativa | 10 | 3 | 0,30 | 5 | 0,50 |
| Compatibilidad FastAPI/SQLite | 8 | 3 | 0,24 | 4 | 0,32 |
| Coste de despliegue | 7 | 3 | 0,21 | 5 | 0,35 |
| **Total** | **100** | | **2,65** | | **4,84** |

### Por qué estos números

- **Persistencia**: MQTT 5 ofrece sesiones duraderas y mensajes retenidos, pero el histórico real acaba en una base externa; JetStream da streams con retención configurable, replay y consumidores duraderos en el propio binario.
- **Orden**: MQTT preserva el orden por tópico mientras la sesión vive; al reconectar o cruzar un bridge, el orden se degrada. JetStream da un número de secuencia por subject dentro del stream.
- **Deduplicación**: QoS 1 de MQTT duplica tras reconexión y QoS 2 es costoso de operar; JetStream trae deduplicación de publicación por cabecera `Nats-Msg-Id` dentro de una ventana configurable (2 min por defecto).
- **mTLS**: ambos lo soportan. MQTT lo delega al broker de turno; NATS lo integra con TLS mutuo y, además, identidades NKeys/JWT.
- **Firma de mensajes**: los dos requieren firma a nivel de aplicación con la clave TLS del nodo; NATS encaja mejor porque las cabeceras viajan sin transformación de extremo a extremo.
- **Bridges federados**: criterio de mayor peso. MQTT es hub-and-spoke y cada fabricante define su bridge; NATS trae leaf nodes y gateways como primitivas de primer nivel, con subject mapping.
- **Huella operativa y coste**: un único binario `nats-server` (Apache-2.0, JetStream incluido) frente a un broker MQTT que suele arrastrar una base para persistir y reglas de sesión con afinidad.
- **FastAPI/SQLite**: el cliente `nats-py` es asíncrono y encaja con los métodos `async` de `ChatBackend`; la verificación de firma reutiliza `cryptography`, ya presente en `backend/requirements.txt`.

## Decisión

**Gana NATS JetStream** (4,84 frente a 2,65). No es un empate: el criterio con más peso, bridges federados, es donde la diferencia es mayor y donde este proyecto tiene un requisito duro.

Razones concretas para Clakettes:

1. **El modelo de confianza ya existente encaja sin inventar nada nuevo**: `docs/es/FEDERATION_SECURITY.md` define identidad de nodo como dominio + certificado X.509, mTLS contra una CA y `trusted_nodes` con huella SHA-256. Los leaf nodes de NATS se autentican con ese mismo mTLS, de modo que el bridge entre nodos hereda la rotación y revocación ya documentadas (marcar `allowed = false` y el handshake falla).
2. **Orden + deduplicación + persistencia vienen en el mismo sitio**: el intercambio de entidades de `docs/es/FEDERATION_SCHEMA.md` incluye `message` con `node_origin` y `created_at`. Un stream por sujeto con número de secuencia y deduplicación por `Nats-Msg-Id` (usando el `message_id` persistido como clave de idempotencia) evita reescribir esa lógica en cada consumidor.
3. **Un solo binario para dos necesidades**: el mismo `nats-server` sirve el event bus efímero (Core NATS, wiring de husos y eventos de sala) y el bus duradero (JetStream, mensajería y reportes). Encaja con el despliegue Docker actual (backend 8000, frontend 3000, MariaDB 3306) sin añadir otro servicio con su propia base.
4. **El cliente es asíncrono de nacimiento**: `nats-py` se integra en el `lifespan` de FastAPI junto a la inicialización de Hive y del registry, sin hilos ni puentes extra.

Contras mitigadas:

1. **No hay exactly-once como el QoS 2 de MQTT**: JetStream es at-least-once. Mitigación: deduplicación de publicación por `Nats-Msg-Id` más consumidores idempotentes que usan `message_id` como clave de idempotencia; SQLite sigue siendo la fuente de verdad y el estado del mensaje se escribe antes de publicar.
2. **El navegador no habla el protocolo NATS de forma nativa**: el frontend usa `web_socket_channel` (ver `frontend/pubspec.yaml`). Mitigación: el WebSocket de borde sigue vivo; el backend suscribe un consumidor de JetStream y reenvía al `ConnectionManager` existente. El cambio es interno y la API que ve Flutter no se toca.
3. **El listener MQTT de `nats-server` solo entiende MQTT 3.1.1** (rechaza CONNECT de MQTT 5): si en el futuro aparece un dispositivo que exija MQTT 5, se pondrá un broker MQTT de borde dedicado que publique en el mismo stream. Queda fuera del alcance actual: no hay dispositivos MQTT en el inventario de `frontend/pubspec.yaml`.

## Consecuencias de implementación

### Backend abstracto

La interfaz `ChatBackend` ya existe en `backend/app/chat_backend/base.py` con `start()`, `stop()` y `send_message(...)`, y `backend/app/chat_backend/registry.py` permite sustituir la implementación registrándola una sola vez en el arranque. No hay que tocar ni la interfaz ni los routers: se añade una implementación nueva, `NatsJetStreamChatBackend`, que en `start()` conecta a `NATS_URL`, declara el stream `CLAKETTES_EVENTS` sobre el subject `clakettes.events.>` y crea el consumidor duradero de borde; en `stop()` hace `drain` y cierra la conexión; en `send_message(...)` publica el mismo payload que hoy construye `WebSocketChatBackend`, más cabeceras con `schema_version`, `node_origin`, `message_id`, `event_id` (UUID v4) y `signature`. La firma es RS256 sobre la representación canónica del mensaje con la clave privada del certificado TLS del nodo, la misma que firma el manifiesto (`docs/es/FEDERATION_PROTOCOL.md`). El par la valida contra su JWKS o contra el certificado del manifiesto antes de aplicar el evento.

### Fallback mononodo

Se mantiene tal cual: `WebSocketChatBackend` sigue siendo el backend registrado por defecto en desarrollo y con `TESTING=true`. SQLite conserva la tabla de mensajes como fuente de verdad; el frontend sigue con Hive (`OfflineCacheService`) y la cola FIFO (`SyncQueueService`) para el modo offline. Si el broker no está disponible, `send_message` encola el evento en la cola de sincronización con el mismo `message_id`/`event_id` y se replaya al reconectar, sin duplicados. El WebSocket de borde continúa entregando a las conexiones autenticadas que hoy gestiona `ConnectionManager`.

### Bridge entre nodos

Cada nodo levanta su `nats-server` con JetStream y declara un leaf node (o un gateway entre clústeres) hacia el nodo hub. El leaf se autentica con mTLS usando la CA federada; el certificado del par se valida contra `trusted_nodes.cert_fingerprint_sha256`. El subject mapping separa los eventos por `node_origin`, por canal y por tipo, de modo que las políticas existentes `disable_chat`, `minimize_data`, `import_only`, `consent_required` y `disable_search` se aplican en el consumidor de entrada antes de persistir. La revocación de un par sigue siendo inmediata: al cambiar `allowed = false`, el siguiente handshake mTLS del leaf falla y dejan de entrar sus eventos.

## Plan de migración en 4 pasos

1. **Preparar**: añadir `nats-py` a `backend/requirements.txt` y las variables `NATS_URL`, `NATS_STREAM`, `NATS_TLS_CERT`, `NATS_TLS_KEY`, `NATS_CA` a `.env.example`. Implementar `NatsJetStreamChatBackend` tras el flag `CHAT_BACKEND=nats`. El registry sigue registrando WebSocket por defecto: ningún test existente cambia.
2. **Sombra**: publicar también en NATS sin que nadie consuma para entregar; un consumidor de validación comprueba secuencia, deduplicación y firma entre dos nodos en staging. La entrega real sigue yendo por WebSocket.
3. **Cut-over**: registrar el backend NATS en producción y convertir el endpoint WebSocket en puente: su consumidor de JetStream alimenta `ConnectionManager.broadcast()`. Añadir tests puntuales del bridge con el doble de transporte y `TESTING=true`, sin arrancar un broker real en la suite. Entrega en paralelo: WS sigue activo durante el cambio.
4. **Cerrar**: retirar el broadcast en proceso para mensajería entre nodos, activar los leaf nodes mTLS entre dos nodos reales y dejar el modo mononodo como fallback documentado. Actualizar en el mismo cambio la API (`python tools/gen_api.py --all`), las cifras y el roadmap del README, y replicar esta doc a las ocho hermanas según la norma de `AGENTS.md`.

## Estado

**Decisión adoptada el 2026-11-20: NATS JetStream como broker de chat y eventos**, con WebSocket como borde y fallback mononodo y MQTT 5 descartado para el núcleo federado.

Desbloquea el propio ítem «Evaluar broker (MQTT vs NATS JetStream) para chat y eventos» y, por dependencia directa, los trabajos de chat federado entre nodos, propagación de eventos entre instancias y bridge mTLS con firma de mensajes. No desbloquea ni sustituye el modelo de confianza ni los endpoints de federación ya documentados: los reutiliza tal cual.
