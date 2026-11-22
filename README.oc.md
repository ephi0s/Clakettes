# Clakettes

La plataforma ont los festivals de cinèma vivon tota l'annada: convocatòrias, corts, equipas, sèts e public dins un meteis luòc.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Fonciona en web, Android, iOS e escritòri (Windows, macOS, Linux), en 9 lengas e tanben sens connexion.

---

## Per qui es?

- **Festivals**: publica ton festivau, dubrís convocatòrias, recep corts, organiza comitats e jurats, gerís sèts e comunica ton palmarés.
- **Professionaus del cinèma**: crea ton perfil (direccion, interpretacion, son, guion, montatge, vestuari e mai), mòstra ton palmarés e connecta amb festivals e equipas.
- **Equipas exprèss**: coordina ton grop de rodatge, geolocaliza los participants e presenta ton cort als concorses exprèss.
- **Public**: descobrís festivals, seguís corts e contacta amb la comunitat.

## Çò que pòdes far

- **Festivals e convocatòrias**: cada festivau pòt aver mantas convocatòrias dubèrtas amb sas règulas pròprias e formularis d'inscripcion.
- **Corts**: puja cortmetratges, liga-los a convocatòrias e a localizacions de rodatge.
- **Perfils amb palmarés**: palmarés ligat a festivals de la plataforma o extèrne mejançant ligams, amb contraròtle de privacitat camp per camp.
- **Chat**: messatges dirèctes e de grop o canau per festivau, amb chiframent d'extrèm a extrèm.
- **Mapas**: sèts e localizacions de rodatge en mapas interactius, amb dubertura dins ta app de mapas favorita.
- **Sens connexion**: l'app contunha de foncionar offline, garda la provenança de cada nose dins la cach e sincroniza tos cambiaments en tornar trobar la connexion.
- **Federacion**: noses de fisança amb mTLS, portabilitat d'identitat, chat e eveniments entre noses, moderacion, metricas e resiliéncia.
- **Dins ta lenga**: espanhòu, anglés, francés, alemand, italian, catalan, euskara, galician e occitan (823 claus per lenga), amb deteccion automatica del locale del sistèma.

## Requesits e aviada

### Requesits minims

- Python 3.12+
- Flutter SDK >= 3.0.0 e < 4.0.0
- Git
- Docker e Docker Compose per desplegament/environa productiva
- Navegador amb suport per al web (recomandat Chrome/Brave)

### Aviada rapida

En PowerShell:

```powershell
./start.ps1 --dev
```

En Linux/macOS:

```bash
./start.sh --dev
```

Aquò quilha lo backend en `http://localhost:8000` e l'app en mòde locau; l'API expausa Swagger/OpenAPI en `/docs`. Pòdes desactivar qual que siá de las doas partidas amb `--no-backend` o `--no-frontend`.

## Variablas d'environa e configuracion

### Backend

Crea o ajusta `backend/.env` amb almens:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
APP_ENV=development
PUBLIC_BASE_URL=https://tu-dominio.com
# Federacion amb mTLS (produccion)
MTLS_REQUIRED=false
MTLS_CA_BUNDLE_PATH=
MTLS_CLIENT_CERT_PATH=
MTLS_CLIENT_KEY_PATH=
# Pagaments (mock per defaut; Stripe/Redsys a demanda)
PAYMENTS_PROVIDER=mock
```

Per environa productiva s'utiliza MariaDB; los scripts e la documentacion de desplegament o gerisson amb Docker.

### Frontend

L'app reutiliza lo backend per URL, normalament amb `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

L'aviada automatica del projècte ja configura aquò quand s'utiliza `start.*`.

## Documentacion del projècte

Lo mapa de documentacion es en [docs/oc/README.md](docs/oc/README.md). Es la melhor intrada per cada tipe d'utilizaire:

- [docs/oc/USO.md](docs/oc/USO.md): aviada, operacion, environa e usatge vidant
- [docs/oc/ADMINISTRACION.md](docs/oc/ADMINISTRACION.md): administracion, comptes e desplegament
- [docs/oc/INFRAESTRUCTURA.md](docs/oc/INFRAESTRUCTURA.md): Docker, pòrts, CI e infraestrutura
- [docs/oc/SEGURIDAD.md](docs/oc/SEGURIDAD.md): tokens, politicas e checklist de produccion
- [docs/oc/ARQUITECTURA.md](docs/oc/ARQUITECTURA.md): arquitectura backend/frontend e fluxes claus
- [docs/oc/API.md](docs/oc/API.md): referéncia d'endpoints
- [docs/oc/DESARROLLO.md](docs/oc/DESARROLLO.md): cossí apondre endpoints o ecrans
- [docs/oc/BACKEND.md](docs/oc/BACKEND.md): guida del backend (capas, configuracion, auth, tèsts)
- [docs/oc/DATABASE.md](docs/oc/DATABASE.md): esquèma e migracions
- [docs/oc/FEDERATION_PROTOCOL.md](docs/oc/FEDERATION_PROTOCOL.md): protocòl entre noses (fasas 2-10)
- [docs/oc/FEDERATION_SECURITY.md](docs/oc/FEDERATION_SECURITY.md): fisança, mTLS, portabilitat e resiliéncia
- [docs/oc/FEDERATION_SCHEMA.md](docs/oc/FEDERATION_SCHEMA.md): entitats federadas e checksum
- [docs/oc/FEDERATION_CHAT_BROKER.md](docs/oc/FEDERATION_CHAT_BROKER.md): decision de transpòrt e estat implementat

En mai, lo punt de partença per desvolopament e convencion de projècte es [AGENTS.md](AGENTS.md).

### Veire tanben

- [docs/oc/README.md](docs/oc/README.md): indici generau per audiéncia
- [docs/oc/HERRAMIENTAS.md](docs/oc/HERRAMIENTAS.md): comandas de build, tèst e aviada
- [docs/oc/FUNCIONAL.md](docs/oc/FUNCIONAL.md): usatge reau del produch per ròtle

### FAQ rapida

- **Ai besoin de Docker per començar ?** Non. L'aviada locala amb `start.*` fonciona sens Docker ; Docker servís per environa productiva e builds reproduzibles.
- **Que fas se l'API respond pas ?** Verifica que lo backend corra en `http://localhost:8000` e que `/docs` responde.
- **Qual document dei legir en primier ?** Se sès utilizaire, [docs/oc/USO.md](docs/oc/USO.md) ; se sès desvolopaire, [docs/oc/ARQUITECTURA.md](docs/oc/ARQUITECTURA.md).
- **Cossí saber se un cambiament demanda actualizar la documentacion ?** Se cambia aviada, API, ròtles, permissions, variablas d'environa o esquèma, actualiza tanben la documentacion que corresponda.

## Contribuir

1. Fai un fork del depaus.
2. Crea una branca (`git checkout -b feature/nov-funcionalitat`).
3. Fai commit amb messatges clars e descriptius (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Possa la branca (`git push origin feature/nov-funcionalitat`).
5. Dubrís un Pull Request amb contexte, cambiaments e validacion.

**Convencions de qualitat:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` e `flutter test` devon passar abans de fusionar. GitHub Actions executa aquelas pòrtas en parallèl e Dependabot dubrís de PRs setmanals gropats: patch/minor se fusionan sols amb CI verda, major demora a revision manuala (detalh dins [docs/oc/INFRAESTRUCTURA.md](docs/oc/INFRAESTRUCTURA.md)).

## Licéncia

Aqueste projècte es jos la **Licéncia MIT**. Consulta [LICENSE](LICENSE).
