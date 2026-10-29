# TASKS.md — Federación Clakettes (progresiva)

Ordenado por estado crítico y complejidad. Cada ítem se elimina al completarse; cuando esté vacío, borrar el archivo.

## Fase 0 — Premios, elegibilidad y cribado (PRIORITARIO)
- [ ] Ampliar modelo Award con criterios de elegibilidad (residente, estudiante, etc.) y verificación del receptor
- [ ] Permitir a la organización verificar el acceso a categorías especiales mediante métodos externos (etiquetas en participantes)
- [ ] Sistema de verificación por el participante en la inscripción (adjuntar certificado de residencia, carnet de estudiante, etc.)
- [ ] Etiquetas de cribado: "descalificado" y categorías especiales para filtrado por el jurado en el visionado
- [ ] Notas y actas por obra, y anotaciones (mención especial, accesit)
- [ ] Soporte en UI y filtrado por elegibilidad/categoría

## Fase 1 — Cumplimiento RGPD y seguridad federada (CRÍTICO)
- [ ] Auditar tratamiento de datos personales por nodo y documentar base legal (consentimiento/interés legítimo) conforme RGPD y LOPDGDD
- [ ] Políticas de federación por instancia: allowlist/blocklist de nodos remotos
- [ ] Federación unidireccional (solo importar, no exportar) para nodos restringidos
- [ ] Permisos por función: deshabilitar chat/DMs, búsqueda o interacciones con nodos específicos
- [ ] Rate limiting y anti-flood en el borde de federación; bloqueo automático de nodos maliciosos
- [ ] Bloqueos de usuario: ocultar contenido, bloquear DMs, silenciar
- [ ] Propagación de reportes de moderación entre nodos
- [ ] Derecho al olvido cross-nodo: borrado propagado y confirmación de eliminación
- [ ] Portabilidad de datos (export) y consentimiento explícito para federar datos
- [ ] Logs de auditoría de accesos y acciones de moderación
- [ ] Minimización de datos en peering (no compartir más de lo necesario)

## Fase 2 — Base y seguridad (CRÍTICO)
- [ ] Auditar endpoints actuales (auth, rate limit, CORS) y documentar amenazas por nodo
- [ ] Diseñar modelo de confianza entre nodos aprovechando certificados TLS de dominio (CA pública o privada) como raíz de identidad
- [ ] Peering mutuo vía mTLS con los certificados de dominio; rotación/revocación gestionada por renovación de cert
- [ ] Definir identidad de nodo = dominio + certificado; verificar manifiesto firmado por la clave del cert
- [ ] Añadir TLS obligatorio entre nodos y validación estricta de certificados en peering (sin self-signed en prod)

## Fase 3 — Identidad federada (FUNDACIONAL)
- [ ] Diseñar handle `usuario@instancia` y resolución vía `.well-known` (WebFinger-like)
- [ ] Implementar ID estable (UUID/DID ligero) desacoplado del handle
- [ ] Adaptar backend para validar tokens de nodos pares (JWKS compartido / clave peered)
- [ ] Migración de usuarios existentes a identidad federada sin pérdida de datos

## Fase 4 — Schema y protocolo abierto (FUNDACIONAL)
- [ ] Definir Clakettes Schema v1 (festival, edición, proyección, usuario, mensaje) versionado
- [ ] Documentar el protocolo de federación para creación de servidores y clientes interoperables (guía paso a paso)
- [ ] Publicar especificación OpenAPI + docs de federación
- [ ] Implementar endpoints `/api/federation/*` en backend actual (nodo primario)
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
