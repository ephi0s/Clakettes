# Funcional — qué se puede hacer en Clakettes

[ES](FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](../gl/FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Utilidad real del proyecto por rol, con el flujo que la sostiene. Detalle operativo en [USO.md](USO.md), referencia de endpoints en [API.md](API.md).

## Festival (organizer)

1. Crea el festival (`POST /api/festivals/`) con descripción, web, sede y logo.
2. Abre convocatorias: formularios de inscripción con secciones, roles y etiquetas (`RegistrationForm + Sections + Links`), expuestos por enlace público que cualquiera puede rellenar sin cuenta.
3. Recibe cortos vinculados a tus convocatorias y localizaciones de rodaje.
4. Monta la programación: eventos (gala, proyección, taller, mesa, networking, premios, fiesta, masterclass, Q&A) con tipos de entrada, asientos (disponible/reservada/vendida/asignada/bloqueada), reservas y check-in de asistentes; exporta asistentes a CSV y eventos a ICS.
5. Nombra comités con miembros y publica premios (verificados o no, públicos o no) por festival, corto o usuario.
6. Comunica: canales del festival (admin/moderator/member), mensajes e imágenes en el perfil, rulebooks.

Solo edita/borra sus festivales y gestiona sus usuarios (`require_festival_admin`). Los miembros se unen solos como `attendee`; el resto de roles los asigna un admin (409 si ya es miembro).

## Profesional (user, jury, resto de oficios)

- Perfil con oficio (dirección, interpretación, sonido, guion, montaje, vestuario, maquillaje, figuración, doblaje, foley, prensa, producción, distribución…), bio y palmarés vinculado a festivales de la plataforma o externo por enlace.
- Privacidad campo por campo (email, bio, ubicación) y perfiles públicos/privados.
- Cada usuario edita su perfil y sus cortos; el jurado consulta y vota según su festival.
- Chat directo y de grupo/canal con cifrado de extremo a extremo: las claves públicas se publican en `POST /api/users/me/public-key`, el servidor solo guarda y retransmite cifrado, el cifrado real ocurre en la app.

## Equipo express (attendee)

- Auto-join al festival (`POST /api/festivals/{id}/join`, rol `attendee`) y salida libre (`leave`).
- Geolocaliza participantes, coordina el grupo por chat y presenta el corto al concurso express.
- Reserva asiento en eventos y envía inscripciones por enlace público (estados: pendiente/aprobada/rechazada/en espera/cancelada; pagos: impagado/pendiente/pagado/reembolsado/cancelado).

## Público

Descubre festivales (`GET /api/festivals/` paginado y público), sigue cortos y palmarés, contacta por chat y consulta sedes en el mapa.

## Administrador global (admin)

Lo ve y lo edita todo (usuarios, festivales, cortos, canales, formularios). Operativa en [ADMINISTRACION.md](ADMINISTRACION.md) (stats, tablas, reset, backups, secretos).

## Estados que debes conocer

- Miembro de festival: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscripción: `draft → submitted → approved / rejected`; envío: `pending / approved / rejected / waitlisted / cancelled`.
- Asistente a evento: `registered / attended / no_show / cancelled`.
- Alcance de visibilidad de eventos: `public / festival_members / roles / attendees_only`.
