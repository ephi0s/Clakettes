# Clakettes

La plataforma on els festivals de cinema viuen tot l'any: convocatòries, curts, equips, seus i públic en un mateix lloc.

[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE)
[![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WCAG](https://img.shields.io/badge/Accessibility-WCAG%202.1-success)](https://www.w3.org/WAI/WCAG21/quickref/)
[![i18n](https://img.shields.io/badge/i18n-9%20idiomas-blue)](frontend/assets/l10n/)

[ES](README.md) · [EN](README.en.md) · [FR](README.fr.md) · [DE](README.de.md) · [IT](README.it.md) · [CA](README.ca.md) · [EU](README.eu.md) · [GL](README.gl.md) · [OC](README.oc.md)

Funciona en web, Android, iOS i escriptori (Windows, macOS, Linux), en 9 idiomes i també sense connexió.

---

## Per a qui és?

- **Festivals**: publica el teu festival, obre convocatòries, rep curts, organitza comitès i jurats, gestiona seus i comunica el teu palmarès.
- **Professionals del cinema**: crea el teu perfil (direcció, interpretació, so, guió, muntatge, vestuari i més), mostra el teu palmarès i connecta amb festivals i equips.
- **Equips express**: coordina el teu grup de rodatge, geolocalitza participants i presenta el teu curt a concursos express.
- **Públic**: descobreix festivals, segueix curts i contacta amb la comunitat.

## Què pots fer

- **Festivals i convocatòries**: cada festival pot tenir diverses convocatòries obertes amb les seves pròpies regles i formularis d'inscripció.
- **Curts**: puja curtmetratges, vincula'ls a convocatòries i a localitzacions de rodatge.
- **Perfils amb palmarès**: palmarès vinculat a festivals de la plataforma o extern mitjançant enllaços, amb control de privacitat camp per camp.
- **Xat**: missatges directes i de grup o canal per festival, amb xifrat d'extrem a extrem.
- **Mapes**: seus i localitzacions de rodatge en mapes interactius, amb obertura a la teva app de mapes preferida.
- **Sense connexió**: l'app continua funcionant offline, guarda la procedència de cada node a la caché i sincronitza els teus canvis en recuperar la connexió.
- **Federació**: nodes de confiança amb mTLS, portabilitat d'identitat, xat i esdeveniments entre nodes, moderació, mètriques i resiliència.
- **En el teu idioma**: espanyol, anglès, francès, alemany, italià, català, euskera, gallec i occità (823 claus per idioma), amb detecció automàtica del locale del sistema.

## Requisits i arrencada

### Requisits mínims

- Python 3.12+
- Flutter SDK >= 3.0.0 i < 4.0.0
- Git
- Docker i Docker Compose per a desplegament/entorn productiu
- Navegador amb suport per a web (recomanat Chrome/Brave)

### Inici ràpid

En PowerShell:

```powershell
./start.ps1 --dev
```

En Linux/macOS:

```bash
./start.sh --dev
```

Això aixeca el backend a `http://localhost:8000` i l'app en mode local; l'API exposa Swagger/OpenAPI a `/docs`. Pots desactivar qualsevol de les dues parts amb `--no-backend` o `--no-frontend`.

## Variables d'entorn i configuració

### Backend

Crea o ajusta `backend/.env` amb almenys:

```env
DATABASE_URL=sqlite:///./clakettes.db
SECRET_KEY=tu-secret-key
CORS_ORIGINS=https://tu-dominio.com
APP_ENV=development
PUBLIC_BASE_URL=https://tu-dominio.com
# Federació amb mTLS (producció)
MTLS_REQUIRED=false
MTLS_CA_BUNDLE_PATH=
MTLS_CLIENT_CERT_PATH=
MTLS_CLIENT_KEY_PATH=
# Pagaments (mock per defecte; Stripe/Redsys sota demanda)
PAYMENTS_PROVIDER=mock
```

Per a entorn productiu s'utilitza MariaDB; els scripts i la documentació de desplegament ho gestionen amb Docker.

### Frontend

L'app reutilitza el backend per URL, normalment amb `--dart-define`:

```bash
flutter run --dart-define=BACKEND_URL=http://localhost:8000
```

L'arrencada automàtica del projecte ja configura això quan s'utilitza `start.*`.

## Documentació del projecte

El mapa de documentació és a [docs/ca/README.md](docs/ca/README.md). És la millor entrada per a cada tipus d'usuari:

- [docs/ca/USO.md](docs/ca/USO.md): arrencada, operació, entorn i ús diari
- [docs/ca/ADMINISTRACION.md](docs/ca/ADMINISTRACION.md): administració, comptes i desplegament
- [docs/ca/INFRAESTRUCTURA.md](docs/ca/INFRAESTRUCTURA.md): Docker, ports, CI i infraestructura
- [docs/ca/SEGURIDAD.md](docs/ca/SEGURIDAD.md): tokens, polítiques i checklist de producció
- [docs/ca/ARQUITECTURA.md](docs/ca/ARQUITECTURA.md): arquitectura backend/frontend i fluxos clau
- [docs/ca/API.md](docs/ca/API.md): referència d'endpoints
- [docs/ca/DESARROLLO.md](docs/ca/DESARROLLO.md): com afegir endpoints o pantalles
- [docs/ca/BACKEND.md](docs/ca/BACKEND.md): guia del backend (capes, configuració, auth, proves)
- [docs/ca/DATABASE.md](docs/ca/DATABASE.md): esquema i migracions
- [docs/ca/FEDERATION_PROTOCOL.md](docs/ca/FEDERATION_PROTOCOL.md): protocol de federació (fases 2-10)
- [docs/ca/FEDERATION_SECURITY.md](docs/ca/FEDERATION_SECURITY.md): confiança, mTLS, portabilitat i resiliència
- [docs/ca/FEDERATION_SCHEMA.md](docs/ca/FEDERATION_SCHEMA.md): entitats federades i checksum
- [docs/ca/FEDERATION_CHAT_BROKER.md](docs/ca/FEDERATION_CHAT_BROKER.md): decisió de transport i estat implementat

A més, el punt de partida per a desenvolupament i convenció de projecte és [AGENTS.md](AGENTS.md).

### Vegeu també

- [docs/ca/README.md](docs/ca/README.md): índex general per audiència
- [docs/ca/HERRAMIENTAS.md](docs/ca/HERRAMIENTAS.md): ordres de build, test i arrencada
- [docs/ca/FUNCIONAL.md](docs/ca/FUNCIONAL.md): ús real del producte per rol

### FAQ ràpida

- **Necessito Docker per començar?** No. L'arrencada local amb `start.*` funciona sense Docker; Docker serveix per a entorn productiu i builds reproduïbles.
- **Què faig si l'API no respon?** Comprova que el backend és executant-se a `http://localhost:8000` i que `/docs` respon.
- **Quin document he de llegir primer?** Si ets usuari, [docs/ca/USO.md](docs/ca/USO.md); si ets desenvolupador, [docs/ca/ARQUITECTURA.md](docs/ca/ARQUITECTURA.md).
- **Com sé si un canvi requereix actualitzar documentació?** Si canvia arrencada, API, rols, permisos, variables d'entorn o esquema, actualitza també la documentació que correspongui.

## Contribuir

1. Fes un fork del repositori.
2. Crea una branca (`git checkout -b feature/nova-funcionalitat`).
3. Fes commit amb missatges clars i descriptius (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. Empeny la branca (`git push origin feature/nova-funcionalitat`).
5. Obre un Pull Request amb context, canvis i validació.

**Convencions de qualitat:** [Conventional Commits](https://www.conventionalcommits.org/), `ruff check .`, `ruff format --check .`, `flutter analyze`, `pytest` i `flutter test` han de passar abans de fusionar. GitHub Actions executa aquestes portes en paral·lel i Dependabot obre PRs setmanals agrupats: patch/minor es fusionen sols amb CI verda, major queda a revisió manual (detall a [docs/ca/INFRAESTRUCTURA.md](docs/ca/INFRAESTRUCTURA.md)).

## Llicència

Aquest projecte és sota la **Llicència MIT**. Consulta [LICENSE](LICENSE).
