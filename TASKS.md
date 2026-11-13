# TASKS.md — Federación Clakettes (progresiva)

Ordenado por estado crítico y complejidad. Cada ítem se elimina al completarse; cuando esté vacío, borrar el archivo.

## Fase 2 — Base y seguridad (CRÍTICO)
- [ ] Instalador/paquete para federar una instancia (infra)
- [ ] Auditar endpoints actuales (auth, rate limit, CORS) y documentar amenazas por nodo
- [ ] Diseñar modelo de confianza entre nodos aprovechando certificados TLS de dominio (CA pública o privada) como raíz de identidad
- [ ] Peering mutuo vía mTLS con los certificados de dominio; rotación/revocación gestionada por renovación de cert
- [ ] Definir identidad de nodo = dominio + certificado; verificar manifiesto firmado por la clave del cert
- [ ] Añadir TLS obligatorio entre nodos y validación estricta de certificados en peering (sin self-signed en prod)

## Fase 3 — Identidad federada (FUNDACIONAL)
- [ ] Adaptar backend para validar tokens de nodos pares (JWKS compartido / clave peered)
- [ ] Adaptar backend para validar tokens de nodos pares (JWKS compartido / clave peered)


## Fase 4 — Schema y protocolo abierto (FUNDACIONAL)
- [ ] Definir Clakettes Schema v1 (festival, edición, proyección, usuario, mensaje) versionado
- [ ] Documentar el protocolo de federación para creación de servidores y clientes interoperables (guía paso a paso)
- [ ] Publicar especificación OpenAPI + docs de federación

- [ ] Crear SDK ligero (Dart/Python) con modelos y cliente federation

## Fase 5 — Votación del jurado (FEATURE)
- [ ] Diseñar sistema de votación por jurado (puntuación por obra, agregación, anonimato opcional)
- [ ] Endpoints backend para emitir y consultar votos por jurado/festival
- [ ] UI de votación para jurados y resultados agregados para organizadores
- [ ] Integración con etiquetas de cribado y elegibilidad (Fase 0)

## Fase 6 — Descubrimiento y multi-nodo en la app (INFRA)
- [ ] Implementar directorio de nodos (registro, capacidades, versión de schema)
- [ ] App: soporte de múltiples `BACKEND_URL` y agregación de resultados
- [ ] Selección de nodo / fallback cuando un nodo cae
- [ ] Cache local (Hive) con origen por nodo y reconciliación

## Fase 7 — Portabilidad de datos (INFRA)
- [ ] Export/import de bundles de usuario (datos + referencias a festivales)
- [ ] Migración de festival entre nodos (proveedor) con verificación de integridad y reasignación de propiedad
- [ ] Migración de usuario entre nodos (perfil, datos, handle) con verificación de integridad y redirección de identidad
- [ ] Tests de conformidad para nodos de terceros

## Fase 8 — Chat como cola federada (COMPLEJO)
- [ ] Evaluar broker (MQTT vs NATS JetStream) para chat y eventos
- [ ] Reimplementar backend de chat sobre cola de mensajes con persistencia
- [ ] Peering de claves entre brokers (mTLS + firma de mensajes)
- [ ] Bridges entre nodos para propagación cross-instancia
- [ ] Historial, búsqueda, presencia, read receipts sobre persistencia local
- [ ] E2EE opcional en cliente; moderación y rate limiting por nodo
- [ ] Deduplicación y orden (IDs únicos + timestamps) en federación

## Fase 9 — Eventos y tiempo real (COMPLEJO)
- [ ] WebSocket/SSE por nodo para notificaciones
- [ ] Pub/sub inter-nodo para invalidación de caché y nuevos festivales
- [ ] Reintentos y entrega diferida ante nodos caídos

## Fase 10 — Resiliencia y observabilidad (POLISH)
- [ ] Health checks por nodo y degradación elegante en la app
- [ ] Métricas y logs de peering (latencia, fallos, reintentos)
- [ ] Plan de recuperación ante compromiso de un nodo (revocación de claves)
