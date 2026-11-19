# Clakettes

A plataforma onde os festivais de cine viven todo o ano: convocatorias, curtas, equipos, sedes e público nun mesmo lugar.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Funciona en web, Android, iOS e escritorio (Windows, macOS, Linux), en 9 idiomas e tamén sen conexión.

---

## Para quen é?

- **Festivais**: publica o teu festival, abre convocatorias, recibe curtas, organiza comités e xurados, xestiona sedes e comunica o teu palmarés.
- **Profesionais do cine**: crea o teu perfil (dirección, interpretación, son, guión, montaxe, vestiario e máis), mostra o teu palmarés e conecta con festivais e equipos.
- **Equipos express**: coordina o teu grupo de rodaxe, xeolocaliza a participantes e presenta a túa curta a concursos express.
- **Público**: descobre festivais, segue curtas e contacta coa comunidade.

## Que podes facer

- **Festivais e convocatorias**: cada festival pode ter varias convocatorias abertas coas súas propias regras e formularios de inscrición.
- **Curtas**: sube curtametraxes, vincúlaas a convocatorias e a localizacións de rodaxe.
- **Perfís con palmarés**: palmarés vinculado a festivais da plataforma ou externo mediante ligazóns, con control de privacidade campo por campo.
- **Chat**: mensaxes directas e de grupo ou canal por festival, con cifrado de extremo a extremo.
- **Mapas**: sedes e localizacións de rodaxe en mapas interactivos, con apertura na túa app de mapas favorita.
- **Sen conexión**: a app segue funcionando offline e sincroniza os teus cambios ao recuperar a conexión.
- **No teu idioma**: español, inglés, francés, alemán, italiano, catalán, éuscaro, galego e occitano, con detección automática.

## Requisitos e arranque

### Requisitos mínimos

- Python 3.12+
- Flutter SDK >= 3.0.0 y < 4.0.0
- Git
- Docker y Docker Compose para despliegue/entorno productivo
- Navegador con soporte para web (recomendado Chrome/Brave)

### Inicio rápido

En Windows:

```bat
start.bat --dev
```

En PowerShell:

```powershell
./start.ps1 --dev
```

En Linux/macOS:

```bash
./start.sh --dev
```

Isto levanta o backend en `http://localhost:8000` e a app en modo local; a API expón Swagger/OpenAPI en `/docs`. Podes desactivar calquera das dúas partes con `--no-backend` ou `--no-frontend`.

### Outras opcións útiles

```bash
start.bat --help
start.bat --migrate
start.bat --build
start.bat --build-all
```

Consulta a referencia completa do arranque e despregamento en [docs/gl/HERRAMIENTAS.md](docs/gl/HERRAMIENTAS.md) e [docs/gl/USO.md](docs/gl/USO.md).

## Variables de entorno e configuración

### Backend

Crea ou axusta `backend/.env` con polo menos:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
```

Para entorno produtivo úsase MariaDB; os scripts e a documentación de despregamento xestiónano con Docker.

### Frontend

A app reutiliza o backend por URL, normalmente con `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

O arranque automático do proxecto xa configura isto cando se usa `start.*`.

## Estado do proxecto

🚧 **En desenvolvemento activo** — Festivais, curtas, chateo con E2EE, mapas, modo sen liña e 9 idiomas funcionando.

**Roadmap seguinte:**

- [ ] Notificacións push (Firebase/APNs)
- [ ] AppImage Linux firmado
- [ ] Instalador Windows MSI
- [x] Documentación API OpenAPI exportable (`/openapi.json` sen operationIds duplicados + `docs/gl/API.md` regenerado)

## Documentación do proxecto

O mapa de documentación está en [docs/gl/README.md](docs/gl/README.md). É a mellor entrada para cada tipo de usuario:

- [docs/gl/USO.md](docs/gl/USO.md): arranque, operación, entorno e uso diario
- [docs/gl/ADMINISTRACION.md](docs/gl/ADMINISTRACION.md): administración, contas e despregamento
- [docs/gl/INFRAESTRUCTURA.md](docs/gl/INFRAESTRUCTURA.md): Docker, portos, CI e infraestrutura
- [docs/gl/SEGURIDAD.md](docs/gl/SEGURIDAD.md): tokens, políticas e checklist de produción
- [docs/gl/ARQUITECTURA.md](docs/gl/ARQUITECTURA.md): arquitectura backend/frontend e fluxos clave
- [docs/gl/API.md](docs/gl/API.md): referencia de endpoints
- [docs/gl/DESARROLLO.md](docs/gl/DESARROLLO.md): como engadir endpoints ou pantallas
- [docs/gl/BACKEND.md](docs/gl/BACKEND.md): guía do backend (capas, configuración, auth, tests)
- [docs/gl/DATABASE.md](docs/gl/DATABASE.md): esquema e migracións
- [docs/gl/FEDERATION_PROTOCOL.md](docs/gl/FEDERATION_PROTOCOL.md): protocolo de federación (fase 4)
- [docs/gl/FEDERATION_SCHEMA.md](docs/gl/FEDERATION_SCHEMA.md): Clakettes Schema v1
- [docs/gl/FEDERATION_SECURITY.md](docs/gl/FEDERATION_SECURITY.md): modelo de confianza federado
- [docs/gl/PUSH.md](docs/gl/PUSH.md): decisión de notificación push

Ademais, o punto de partida para desenvolvemento e convención de proxecto é [AGENTS.md](AGENTS.md).

### Ver tamén

- [docs/gl/README.md](docs/gl/README.md): índice xeral por audiencia
- [docs/gl/HERRAMIENTAS.md](docs/gl/HERRAMIENTAS.md): comandos de build, test e arranque
- [docs/gl/FUNCIONAL.md](docs/gl/FUNCIONAL.md): uso real do produto por rol

### FAQ rápida

- **Necesito Docker para empezar?** Non. O arranque local con `start.*` funciona sen Docker; Docker serve para entorno produtivo e builds reproducibles.
- **Que fago se a API non responde?** Comproba que o backend está correndo en `http://localhost:8000` e que `/docs` responde.
- **Que documento debo ler primeiro?** Se es usuario, [docs/gl/USO.md](docs/gl/USO.md); se es desenvolvedor, [docs/gl/ARQUITECTURA.md](docs/gl/ARQUITECTURA.md).
- **Como sei se un cambio require actualizar documentación?** Se cambia arranque, API, roles, permisos, variables de entorno ou esquema, actualiza tamén a documentación que corresponda.

## Contribuír

1. Fai un fork do repositorio.
2. Crea unha rama (`git checkout -b feature/nova-funcionalidade`).
3. Fai commit con mensaxes claras e descritivas (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empuxa a rama (`git push origin feature/nova-funcionalidade`).
5. Abre un Pull Request con contexto, cambios e validación.

**Convencións de calidade:** [Conventional Commits](https://www.conventionalcommits.org/).

## Licenza

Este proxecto está baixo a **Licenza MIT**. Consulta [LICENSE](LICENSE).
