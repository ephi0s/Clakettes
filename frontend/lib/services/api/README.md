# Split de ApiService (E26)

`api_service.dart` conserva `ApiService` como singleton y única fuente de verdad. El split ya está implementado: los dominios viven en extensiones reales en `lib/services/api/` y la API pública no ha cambiado (`ApiService().getFestivals()` sigue funcionando).

## Estado actual
- 13 directivas `part 'api/...'` en `api_service.dart` (líneas 39-51).
- Cada archivo declara `part of '../api_service.dart'` y una extensión `extension XxxApi on ApiService` con los métodos de su dominio: festival, user, channel, form, calendar, catalog, org, event, location, post, badge, participant_tag, jury_votes.
- Los helpers HTTP (`_get`/`_put`/`request`/`_paginated`/`uploadFile`), cabeceras y `rootUrl` permanecen en `api_service.dart`.
- No hay facades standalone: las extensiones se aplican directamente sobre `ApiService`.

## Reglas
- Un único método por endpoint, en su extensión correspondiente; sin duplicar lógica.
- `flutter analyze` debe pasar tras cada cambio.

## Medios

Los endpoints de subida del backend devuelven rutas relativas (`/uploads/...`), nunca URLs absolutas. `resolveMediaUrl()` las completa con el nodo activo y deja intactas las que ya son `http(s)`. Toda imagen debe pasar por ese helper, incluida `ProfileAvatar`.

`uploadFile()` es el único punto de subida: envía `MultipartFile.fromBytes` con el MIME deducido de la extensión, funciona en web mediante `XFile.readAsBytes()`, refresca el token ante 401, reintenta en otros nodos y expone el `detail` del servidor en `ApiException`. `platformFileToXFile()` adapta los archivos de `file_picker`.
- Tests existentes contra `ApiService` no deben cambiar.
