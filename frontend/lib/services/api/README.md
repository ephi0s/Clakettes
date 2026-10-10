# Plan de split ApiService (E26)

`api_service.dart` ~1460 líneas, singleton con ~32 dominios. Objetivo: modularizar sin romper API pública.

## Estado actual
- `ApiService` intacto, única fuente de verdad.
- `api/festival_api.dart` creado como referencia futura (delegación a `ApiService()`), no integrado.
- `part`/`mixin` no usado aún para evitar regresión.

## Dominios propuestos
| Módulo | Archivo | Métodos |
|---|---|---|
| Festivals | `festival_api.dart` | getFestivals, getFestival, create/update/deleteFestival, upload/deleteFestivalImage |
| Users/Auth | `user_api.dart` | login, getUsers, getMe, create/update/deleteUser, sessions, aliases |
| Shortfilms | `shortfilm_api.dart` | getShortfilms, create/update/deleteShortfilm |
| Messages/Chat | `message_api.dart` | getMessages, sendMessage, channels |
| Channels | `channel_api.dart` | getChannels, createChannel, etc. |
| Forms | `form_api.dart` | getFormDefinitions, registrations, public links |
| Events | `event_api.dart` | getEvents, createEvent, getMyEvents, updateEvent |
| Awards/Locations/FilmLocations | `catalog_api.dart` | awards, locations, tags, film_locations |
| Committees/Roles | `committee_api.dart` | committees, role_groups, delegations, transitions |
| Notifications | `notification_api.dart` | notifications |
| Helpers | `api_client.dart` | _get/_put/request/_paginated/_uploadFile, headers, baseUrl |

## Estrategia (sin breaking change)
1. Fase 1 (actual): helpers por dominio como `FestivalApi(ApiService)` delegando — solo referencia, no wiring.
2. Fase 2: convertir cada helper en `mixin FestivalApi on ApiService` + `part 'api/festival_api.dart'` en `api_service.dart`; mover implementación, re-exportar vía `ApiService` para mantener `ApiService().getFestivals()` funcionando.
3. Fase 3: cuando todos los mixins estén estables, opcionalmente exponer facades `FestivalApi()` standalone para inyección en tests, manteniendo `ApiService` como aggregator `class ApiService with FestivalApi, UserApi, ...`.

## Reglas
- No duplicar lógica: el helper delega hasta el split real.
- `dart analyze` debe pasar en cada paso.
- Tests existentes contra `ApiService` no deben cambiar.
