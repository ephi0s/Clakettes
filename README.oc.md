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
- **Sens connexion**: l'app contunha de foncionar offline e sincroniza tos cambiaments en tornar trobar la connexion.
- **Dins ta lenga**: espanhòu, anglés, francés, alemand, italian, catalan, euskara, galician e occitan, amb deteccion automatica.

## Requesits e aviada

### Requesits minims

- Python 3.12+
- Flutter SDK >= 3.0.0 y < 4.0.0
- Git
- Docker y Docker Compose para despliegue/entorno productivo
- Navegador con soporte para web (recomendado Chrome/Brave)

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

### Autras opcions utilas

```bash
./start.ps1 --help
./start.ps1 --migrate
./start.ps1 --build
./start.ps1 --build-all
```

Consulta la referéncia completa de l'aviada e desplegament en [docs/oc/HERRAMIENTAS.md](docs/oc/HERRAMIENTAS.md) e [docs/oc/USO.md](docs/oc/USO.md).

## Variablas d'environa e configuracion

### Backend

Crea o ajusta `backend/.env` amb almens:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Per environa productiva s'utiliza MariaDB; los scripts e la documentacion de desplegament o gerisson amb Docker.

### Frontend

L'app reutiliza lo backend per URL, normalament amb `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

L'aviada automatica del projècte ja configura aquò quand s'utiliza `start.*`.

## Estat del projècte

🚧 **En desvolopament actiu** — Festivals, corts, chat amb E2EE, mapas, mòde offline e 9 lengas que foncionan.

**Roadmap pròche:**

- [ ] Notificacions push (Firebase/APNs)
- [ ] AppImage Linux firmat
- [ ] Windows MSI instalador
- [x] Documentacion API OpenAPI exportable (`/openapi.json` sens operationIds duplicats + `docs/oc/API.md` regenerat)

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
- [docs/oc/FEDERATION_PROTOCOL.md](docs/oc/FEDERATION_PROTOCOL.md): protocolo de federacion (fasa 4)
- [docs/oc/FEDERATION_SCHEMA.md](docs/oc/FEDERATION_SCHEMA.md): Clakettes Schema v1
- [docs/oc/FEDERATION_SECURITY.md](docs/oc/FEDERATION_SECURITY.md): model de confianza federat
- [docs/oc/PUSH.md](docs/oc/PUSH.md): decisio de notificacion push

En mai, lo punt de partença per desvolopament e convencion de projècte es [AGENTS.md](AGENTS.md).

### Veire tanben

- [docs/oc/README.md](docs/oc/README.md): indici generau per audiéncia
- [docs/oc/HERRAMIENTAS.md](docs/oc/HERRAMIENTAS.md): comandas de build, tèst e aviada
- [docs/oc/FUNCIONAL.md](docs/oc/FUNCIONAL.md): usatge reau del produch per ròtle

### FAQ rapida

- **¿Necesito Docker para empezar?** No. El arranque local con `start.*` funciona sin Docker; Docker sirve para entorno productivo y builds reproducibles.
- **¿Qué hago si la API no responde?** Comprueba que el backend está corriendo en `http://localhost:8000` y que `/docs` responde.
- **¿Qué documento debo leer primero?** Si eres usuario, [docs/oc/USO.md](docs/oc/USO.md); si eres desarrollador, [docs/oc/ARQUITECTURA.md](docs/oc/ARQUITECTURA.md).
- **¿Cómo sé si un cambio requiere actualizar documentación?** Si cambia arranque, API, roles, permisos, variables de entorno o esquema, actualiza también la documentación que corresponda.



## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nov-funcionalitat`).
3. Haz commit con mensajes claros y descriptivos (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empuja la rama (`git push origin feature/nov-funcionalitat`).
5. Abre un Pull Request con contexto, cambios y validación.

**Convencions de qualitat:** [Conventional Commits](https://www.conventionalcommits.org/).

## Licéncia

Aqueste projècte es jos la **Licéncia MIT**. Consulta [LICENSE](LICENSE).
