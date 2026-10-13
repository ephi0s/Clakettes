# Funcional — que se pode facer en Clakettes

[ES](../es/FUNCIONAL.md) · [EN](../en/FUNCIONAL.md) · [FR](../fr/FUNCIONAL.md) · [DE](../de/FUNCIONAL.md) · [IT](../it/FUNCIONAL.md) · [CA](../ca/FUNCIONAL.md) · [EU](../eu/FUNCIONAL.md) · [GL](FUNCIONAL.md) · [OC](../oc/FUNCIONAL.md)

Utilidade real do proxecto por rol, co fluxo que a sostén. Detalle operativo en [USO.md](USO.md), referencia de endpoints en [API.md](API.md).

## Festival (organizer)

1. Crea o festival (`POST /api/festivals/`) con descrición, web, sede e logo.
2. Abre convocatorias: formularios de inscrición con seccións, roles e etiquetas (`RegistrationForm + Sections + Links`), expostos por ligazón pública que calquera pode cubrir sen conta.
3. Recibe curtas vinculadas ás túas convocatorias e localizacións de rodaxe.
4. Monta a programación: eventos (gala, proxección, taller, mesa, networking, premios, festa, masterclass, Q&A) con tipos de entrada, asentos (dispoñible/reservada/vendida/asignada/bloqueada), reservas e check-in de asistentes; exporta asistentes a CSV e eventos a ICS.
5. Nomea comités con membros e publica premios (verificados ou non, públicos ou non) por festival, curta ou usuario.
6. Comunica: canles do festival (admin/moderator/member), mensaxes e imaxes no perfil, rulebooks.

Só edita/borra os seus festivais e xestiona os seus usuarios (`require_festival_admin`). Os membros únense sós como `attendee`; o resto de roles asígnaos un admin (409 se xa é membro).

## Profesional (user, jury, resto de oficios)

- Perfil con oficio (dirección, interpretación, son, guión, montaxe, vestiario, maquillaxe, figuración, dobraxe, foley, prensa, produción, distribución…), bio e palmarés vinculado a festivais da plataforma ou externo por ligazón.
- Privacidade campo por campo (email, bio, localización) e perfís públicos/privados.
- Cada usuario edita o seu perfil e as súas curtas; o xurado consulta e vota segundo o seu festival.
- Chat directo e de grupo/canal con cifrado de extremo a extremo: as claves públicas publícanse en `POST /api/users/me/public-key`, o servidor só garda e retransmite cifrado, o cifrado real ocorre na app.

## Equipo express (attendee)

- Auto-join ao festival (`POST /api/festivals/{id}/join`, rol `attendee`) e saída libre (`leave`).
- Xeolocaliza participantes, coordina o grupo por chat e presenta a curta ao concurso express.
- Reserva asento en eventos e envía inscricións por ligazón pública (estados: pendente/aprobada/rexeita/en espera/cancelada; pagos: impagado/pendente/pagado/reembolsado/cancelado).

## Público

Descobre festivais (`GET /api/festivals/` paxinado e público), segue curtas e palmarés, contacta por chat e consulta sedes no mapa.

## Administrador global (admin)

Veo e edítao todo (usuarios, festivais, curtas, canles, formularios). Operativa en [ADMINISTRACION.md](ADMINISTRACION.md) (stats, táboas, reset, backups, segredos).

## Estados que debes coñecer

- Membro de festival: `proposed → invited → under_review → pending → active → approved / rejected / revoked / expired / cancelled`.
- Inscrición: `draft → submitted → approved / rejected`; envío: `pending / approved / rejected / waitlisted / cancelled`.
- Asistente a evento: `registered / attended / no_show / cancelled`.
- Alcance de visibilidade de eventos: `public / festival_members / roles / attendees_only`.
