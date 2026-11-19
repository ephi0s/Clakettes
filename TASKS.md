# TASKS.md — Federación Clakettes (progresiva)

Ordenado por estado crítico y complejidad. Cada ítem se elimina al completarse; cuando esté vacío, borrar el archivo.

## Fase 6 — Descubrimiento y multi-nodo en la app (INFRA)
- [x] Implementar directorio de nodos (registro, capacidades, versión de schema)
- [x] App: soporte de múltiples `BACKEND_URL` y agregación de resultados
- [x] Selección de nodo / fallback cuando un nodo cae
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
