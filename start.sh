#!/bin/sh
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"
BROWSER=""
chmod +x "$0" "$ROOT"/tools/*.sh 2>/dev/null || true

NO_BACKEND=0
NO_FRONTEND=0
IS_WEB=0
IS_FINAL=0
IS_DEV=0
IS_MIGRATE=0
IS_TEST_MIGRATION=0
IS_MARIADB=0
IS_TEST_BACKEND=0
IS_TEST_FRONTEND=0
IS_KILL=0
IS_BUILD=0
IS_BUILD_ALL=0
IS_BUILD_FRONTEND=0
IS_BUILD_BACKEND=0
IS_INSTALL_MISSING=0
IS_CHECK=0

# ── OS detection ────────────────────────────────────────────────
OS=""
OS_FAMILY=""
OS_ID=""
PKG_MANAGER=""
INSTALL_CMD=""
PYTHON_CMD=""
UNAME_S=""

detect_os() {
  UNAME_S="$(uname -s)"
  case "$UNAME_S" in
    Darwin)
      OS="macos"
      OS_FAMILY="macos"
      PKG_MANAGER="brew"
      INSTALL_CMD="brew install"
      ;;
    FreeBSD)
      OS="freebsd"
      OS_FAMILY="freebsd"
      PKG_MANAGER="pkg"
      INSTALL_CMD="pkg install -y"
      ;;
    Linux)
      OS="linux"
      if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID="${ID:-}"
        case "$ID" in
          debian|ubuntu|linuxmint|pop|elementary|zorin)
            OS_FAMILY="debian"; PKG_MANAGER="apt"; INSTALL_CMD="apt install -y" ;;
          fedora|rhel|centos|rocky|almalinux)
            OS_FAMILY="fedora"; PKG_MANAGER="dnf"; INSTALL_CMD="dnf install -y" ;;
          alpine)
            OS_FAMILY="alpine"; PKG_MANAGER="apk"; INSTALL_CMD="apk add" ;;
          opensuse*|sles|suse*)
            OS_FAMILY="suse"; PKG_MANAGER="zypper"; INSTALL_CMD="zypper install -y" ;;
          arch|manjaro|endeavouros|artix)
            OS_FAMILY="arch"; PKG_MANAGER="pacman"; INSTALL_CMD="pacman -S --noconfirm" ;;
          *)
            OS_FAMILY="unknown"
            PKG_MANAGER=""
            INSTALL_CMD=""
            ;;
        esac
      elif [ -f /etc/debian_version ]; then
        OS_FAMILY="debian"; PKG_MANAGER="apt"; INSTALL_CMD="apt install -y"
      elif [ -f /etc/fedora-release ]; then
        OS_FAMILY="fedora"; PKG_MANAGER="dnf"; INSTALL_CMD="dnf install -y"
      elif [ -f /etc/alpine-release ]; then
        OS_FAMILY="alpine"; PKG_MANAGER="apk"; INSTALL_CMD="apk add"
      elif [ -f /etc/SuSE-release ]; then
        OS_FAMILY="suse"; PKG_MANAGER="zypper"; INSTALL_CMD="zypper install -y"
      else
        OS_FAMILY="unknown"
      fi
      ;;
    *)
      OS="unknown"
      OS_FAMILY="unknown"
      ;;
  esac
}

detect_python() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
  elif command -v python >/dev/null 2>&1; then
    pyver="$(python --version 2>&1 | sed 's/.* \([0-9]*\)\..*/\1/')"
    if [ "$pyver" -ge 3 ] 2>/dev/null; then
      PYTHON_CMD="python"
    fi
  fi
}

detect_flutter() {
  if command -v flutter >/dev/null 2>&1; then return 0; fi
  for p in /opt/flutter/bin/flutter "$HOME/flutter/bin/flutter" /usr/local/flutter/bin/flutter /snap/bin/flutter; do
    if [ -x "$p" ]; then
      PATH="$(dirname "$p"):$PATH"
      export PATH
      return 0
    fi
  done
  return 1
}

detect_browser() {
  case "$OS" in
    macos)
      for app in "Google Chrome" "Brave Browser" "Firefox" "Safari"; do
        if [ -d "/Applications/$app.app" ] || [ -d "$HOME/Applications/$app.app" ]; then
          BROWSER="open -a '$app'"
          return 0
        fi
      done
      if command -v open >/dev/null 2>&1; then BROWSER="open"; fi
      ;;
    linux)
      for b in brave-browser brave google-chrome google-chrome-stable chromium chromium-browser firefox firefox-esr opera vivaldi-stable microsoft-edge-stable; do
        if command -v "$b" >/dev/null 2>&1; then
          BROWSER="$b"
          return 0
        fi
      done
      if command -v flatpak >/dev/null 2>&1; then
        flatpak list --app 2>/dev/null | grep -qi "chrome\|brave\|firefox\|chromium" && BROWSER="flatpak run com.google.Chrome" && return 0
      fi
      ;;
  esac
}

detect_os
detect_python
detect_flutter
detect_browser

install_guide() {
  echo ""
  echo "Como instalar un entorno bare-metal (sin Docker) en ${OS:-?} / ${OS_FAMILY:-?}:"
  case "$OS_FAMILY" in
    debian)
      echo "  Python 3.12+: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
      echo "  Flutter:      sudo snap install flutter --classic   (o ./start.sh --install-missing)"
      echo "  Docker:       curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker \$USER"
      ;;
    fedora)
      echo "  Python 3.12+: sudo dnf install -y python3 python3-pip"
      echo "  Flutter:      ./start.sh --install-missing   (clona el SDK en ~/flutter)"
      echo "  Docker:       sudo dnf install -y docker-ce docker-ce-cli containerd.io && sudo systemctl start docker"
      ;;
    arch)
      echo "  Python 3.12+: sudo pacman -S --noconfirm python python-pip"
      echo "  Flutter:      ./start.sh --install-missing   (clona el SDK en ~/flutter)"
      echo "  Docker:       sudo pacman -S docker docker-compose && sudo systemctl start docker"
      ;;
    alpine)
      echo "  Python 3.12+: sudo apk add python3 py3-pip"
      echo "  Flutter:      ./start.sh --install-missing   (clona el SDK en ~/flutter)"
      echo "  Docker:       sudo apk add docker docker-compose && sudo service docker start"
      ;;
    suse)
      echo "  Python 3.12+: sudo zypper install -y python3 python3-pip"
      echo "  Flutter:      ./start.sh --install-missing   (clona el SDK en ~/flutter)"
      echo "  Docker:       sudo zypper install -y docker docker-compose && sudo systemctl start docker"
      ;;
    macos)
      echo "  Python 3.12+: brew install python@3.12"
      echo "  Flutter:      ./start.sh --install-missing   (clona el SDK en ~/flutter)"
      echo "  Docker:       brew install --cask docker   (o https://docs.docker.com/desktop/install/mac/)"
      ;;
    freebsd)
      echo "  Python:  sudo pkg install -y python3 py3-pip py3-venv"
      echo "  Flutter: ./start.sh --install-missing   (clona el SDK en ~/flutter)"
      echo "  Docker:  sudo pkg install docker docker-compose"
      ;;
    *)
      echo "  Python 3.12+: https://www.python.org/downloads/"
      echo "  Flutter:      https://docs.flutter.dev/get-started/install"
      echo "  Docker:       https://docs.docker.com/engine/install/"
      ;;
  esac
  echo "  Re-ejecuta con --install-missing para intentarlo automatico."
  echo ""
}

install_missing() {
  need_py=$1; need_fl=$2
  if [ "$need_py" -eq 1 ] && [ -z "$PYTHON_CMD" ]; then
    echo "[INSTALL] Instalando Python..."
    case "$OS_FAMILY" in
      debian) sudo apt update && sudo apt install -y python3 python3-venv python3-pip ;;
      fedora) sudo dnf install -y python3 python3-pip ;;
      arch) sudo pacman -S --noconfirm python python-pip ;;
      alpine) sudo apk add python3 py3-pip ;;
      suse) sudo zypper install -y python3 python3-pip ;;
      macos) brew install python@3.12 ;;
      freebsd) sudo pkg install -y python3 py3-pip ;;
      *) echo "[INSTALL] ERROR: instala Python manual: https://www.python.org/downloads/"; return 1 ;;
    esac
    detect_python
    if [ -n "$PYTHON_CMD" ]; then echo "[INSTALL] Python OK ($PYTHON_CMD)"
    else echo "[INSTALL] ERROR: Python sigue sin detectarse"; fi
  fi
  if [ "$need_fl" -eq 1 ] && ! command -v flutter >/dev/null 2>&1; then
    if ! command -v git >/dev/null 2>&1; then
      echo "[INSTALL] Instalando git..."
      case "$OS_FAMILY" in
        debian) sudo apt update && sudo apt install -y git ;;
        fedora) sudo dnf install -y git ;;
        arch) sudo pacman -S --noconfirm git ;;
        alpine) sudo apk add git ;;
        suse) sudo zypper install -y git ;;
        macos) brew install git ;;
        freebsd) sudo pkg install -y git ;;
        *) echo "[INSTALL] ERROR: se necesita git: https://git-scm.com/downloads"; return 1 ;;
      esac
    fi
    if [ ! -x "$HOME/flutter/bin/flutter" ]; then
      echo "[INSTALL] Clonando Flutter estable en $HOME/flutter (puede tardar)..."
      git clone --depth 1 -b stable https://github.com/flutter/flutter.git "$HOME/flutter"
    fi
    PATH="$HOME/flutter/bin:$PATH"; export PATH
    if command -v flutter >/dev/null 2>&1; then
      echo "[INSTALL] Comprobando Flutter..."
      flutter --version 2>&1 | tr -d '\r' | sed 's/\x1b\[[0-9;]*m//g' | head -8
      echo "[INSTALL] Flutter OK"
    else
      echo "[INSTALL] ERROR: Flutter sigue sin detectarse"
    fi
  fi
}

if [ -n "$BROWSER" ]; then
  echo "[DETECTADO] Navegador: $BROWSER"
  case "$OS" in
    macos) ;;
    *) CHROME_EXECUTABLE="$BROWSER"; export CHROME_EXECUTABLE ;;
  esac
fi

echo "[SISTEMA] ${OS:-desconocido} / ${OS_FAMILY:-desconocido} | Python: ${PYTHON_CMD:-no} | Flutter: $(command -v flutter >/dev/null 2>&1 && echo si || echo no)"

# ── Help ────────────────────────────────────────────────────────
show_help() {
  cat <<EOF
Clakettes Launcher (portable mode)

USO:
    ./start.sh                        Backend + frontend (Docker dev, o local si no hay Docker)
    ./start.sh --dev                  Igual que default
    ./start.sh --final                Backend + frontend (Docker produccion, o build local)
    ./start.sh --web                  Frontend con navegador (solo modo local)
    ./start.sh --no-frontend          Solo backend
    ./start.sh --no-backend           Solo frontend
    ./start.sh --mariadb              Incluye MariaDB (Docker: perfil db / local: variable)
    ./start.sh --migrate              Ejecuta migraciones (Docker: docker compose run)
    ./start.sh --test-migration       Prueba migracion completa con MariaDB
    ./start.sh --test-backend         Ejecuta tests del backend
    ./start.sh --test-frontend        Ejecuta tests del frontend
    ./start.sh --build                Construye imagenes Docker (desarrollo)
    ./start.sh --build-all            Construye paquetes distribubles (final)
    ./start.sh --build-frontend       Construye solo frontend (Docker)
    ./start.sh --build-backend        Construye solo backend (Docker)
    ./start.sh --kill                 Para contenedores Docker y procesos locales
    ./start.sh --install-missing       Instala lo que falte (gestor del SO + git clone)
    ./start.sh --check                 Revisa el entorno sin arrancar nada
    ./start.sh --help                 Muestra esta ayuda

SISTEMA DETECTADO: ${OS:-desconocido} / ${OS_FAMILY:-desconocido}
PYTHON: ${PYTHON_CMD:-no detectado}

REQUISITOS (Docker):
    - Docker Engine (https://docs.docker.com/engine/install/)
    - Docker levanta automaticamente pip install + flutter pub get

REQUISITOS (local, si no hay Docker):
    - Python 3.12+ con pip ($([ -n "$PYTHON_CMD" ] && echo "detectado: $PYTHON_CMD" || echo "NO DETECTADO"))
    - Flutter SDK en PATH ($(command -v flutter >/dev/null 2>&1 && echo "detectado" || echo "NO DETECTADO"))
    - Los scripts crean .venv y ejecutan flutter pub get automaticamente
EOF
}

# ── Parse flags ─────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --no-backend)    NO_BACKEND=1 ;;
    --no-frontend)   NO_FRONTEND=1 ;;
    --web)           IS_WEB=1 ;;
    --final)         IS_FINAL=1 ;;
    --dev)           IS_DEV=1 ;;
    --migrate)       IS_MIGRATE=1 ;;
    --test-migration) IS_TEST_MIGRATION=1 ;;
    --mariadb)       IS_MARIADB=1 ;;
    --test-backend)  IS_TEST_BACKEND=1 ;;
    --test-frontend) IS_TEST_FRONTEND=1 ;;
    --kill)          IS_KILL=1 ;;
    --build)         IS_BUILD=1 ;;
    --build-all)     IS_BUILD_ALL=1 ;;
    --build-frontend) IS_BUILD_FRONTEND=1 ;;
    --build-backend)  IS_BUILD_BACKEND=1 ;;
    --install-missing) IS_INSTALL_MISSING=1 ;;
    --check) IS_CHECK=1 ;;
    --help|-h|/?)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown flag: $arg"
      show_help
      exit 1
      ;;
  esac
done

NEED_PY=1; [ "$NO_BACKEND" -eq 1 ] && NEED_PY=0
[ "$IS_MIGRATE" -eq 1 ] && NEED_PY=1
[ "$IS_TEST_BACKEND" -eq 1 ] && NEED_PY=1
[ "$IS_FINAL" -eq 1 ] && NEED_PY=1
NEED_FL=1; [ "$NO_FRONTEND" -eq 1 ] && NEED_FL=0
[ "$IS_TEST_FRONTEND" -eq 1 ] && NEED_FL=1
[ "$IS_FINAL" -eq 1 ] && NEED_FL=1
export NEED_PY NEED_FL

# ---- Port auto-assignment ----
port_in_use() {
  port=$1
  case "$UNAME_S" in
    Darwin) lsof -i :"$port" >/dev/null 2>&1 ;;
    FreeBSD) sockstat -l 2>/dev/null | grep -q ":$port " ;;
    Linux)
      if command -v ss >/dev/null 2>&1; then ss -tlnp 2>/dev/null | grep -q ":$port "
      else netstat -tlnp 2>/dev/null | grep -q ":$port "
      fi
      ;;
    *) false ;;
  esac
}

find_free_port() {
  desired=$1; service=$2
  if ! port_in_use "$desired"; then
    echo "[PUERTO] $service -> $desired (puerto por defecto libre)"
    eval "$service=$desired"
    return 0
  fi
  owner="?"
  case "$UNAME_S" in
    Darwin)
      opid=$(lsof -i :"$desired" -F p 2>/dev/null | head -1 | tr -d p)
      [ -n "$opid" ] && owner=$(ps -p "$opid" -o comm= 2>/dev/null || echo "PID $opid")
      ;;
    FreeBSD)
      owner=$(sockstat -l 2>/dev/null | grep ":$desired " | awk '{print $3}' | head -1)
      ;;
    Linux)
      if command -v ss >/dev/null 2>&1; then
        opid=$(ss -tlnp 2>/dev/null | grep ":$desired " | sed 's/.*pid=\([0-9]*\).*/\1/' | head -1)
      else
        opid=$(netstat -tlnp 2>/dev/null | grep ":$desired " | sed 's/.* \([0-9]*\)\/.*/\1/' | head -1)
      fi
      [ -n "$opid" ] && owner=$(ps -p "$opid" -o comm= 2>/dev/null || echo "PID $opid")
      ;;
  esac
  echo "[PUERTO] $service necesita puerto $desired — ocupado por $owner, buscando libre..."
  try=60000
  while [ "$try" -le 65535 ]; do
    if ! port_in_use "$try"; then
      echo "[PUERTO] $service -> $try"
      eval "$service=$try"
      return 0
    fi
    try=$((try + 1))
  done
  echo "[PUERTO] ERROR: No se encontro puerto libre para $service"
  exit 1
}

venv_ok() {
  [ -x "$BACKEND_DIR/.venv/bin/python" ] || return 1
  [ -f "$BACKEND_DIR/.venv/pyvenv.cfg" ] || return 1
  venv_home="$(sed -n 's/^home *= *//p' "$BACKEND_DIR/.venv/pyvenv.cfg" | head -1 | sed 's/ *$//')"
  if [ -n "$venv_home" ] && [ ! -d "$venv_home" ]; then return 1; fi
  "$BACKEND_DIR/.venv/bin/python" --version >/dev/null 2>&1 || return 1
  return 0
}

pub_cache_ok() {
  pub_cfg="$FRONTEND_DIR/.dart_tool/package_config.json"
  [ -f "$pub_cfg" ] || return 1
  "$PYTHON_CMD" -c 'import json,os,sys,urllib.parse
cfg=sys.argv[1]
try:
    pkgs=json.load(open(cfg,encoding="utf-8"))["packages"]
except Exception:
    sys.exit(1)
base=os.path.dirname(cfg)
n=0
for p in pkgs:
    u=p.get("rootUri","")
    if u.startswith("file:///"):
        if not os.path.exists("/"+urllib.parse.unquote(u[8:]).lstrip("/")):
            sys.exit(1)
        n+=1
        if n>=8:
            break
    elif u.startswith("file:"):
        if not os.path.exists(os.path.join(base,urllib.parse.unquote(u[5:]))):
            sys.exit(1)
if n==0:
    sys.exit(1)' "$pub_cfg" || return 1
  return 0
}

container_pub_cache_ok() {
  pub_cfg="$FRONTEND_DIR/.dart_tool/package_config.json"
  [ -f "$pub_cfg" ] || return 0
  uris="$(grep -o '"rootUri": *"file://[^"]*"' "$pub_cfg" 2>/dev/null | sed -e 's/^"rootUri": *"file:\/\/*//' -e 's/"$//')" || true
  [ -n "$uris" ] || return 0
  while IFS= read -r uri; do
    [ -n "$uri" ] || continue
    case "$uri" in
      [A-Za-z]:*) return 1;;
      app/*|root/*|tmp/*) ;;
      *) return 1;;
    esac
  done <<URIS
$uris
URIS
  return 0
}

# ================================================================
# DOCKER MODE
# ================================================================
if [ "$IS_CHECK" -eq 1 ]; then
  fail=0
  echo "[CHECK] Revisando entorno (sin cambios)..."
  if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then echo "[CHECK] Docker: OK."
    else echo "[CHECK] Docker: daemon parado — se usara modo local."; fi
  else
    echo "[CHECK] Docker: ausente — se usara modo local."
  fi
  if [ "$NEED_PY" -eq 1 ]; then
    if [ -n "$PYTHON_CMD" ]; then echo "[CHECK] Python: OK ($PYTHON_CMD)."
    else echo "[CHECK] Python 3.12+: NO DETECTADO."; fail=1; fi
    if venv_ok; then echo "[CHECK] .venv: OK."
    else echo "[CHECK] .venv: se creara o recreara al arrancar."; fi
    if [ -f "$BACKEND_DIR/.env" ]; then echo "[CHECK] backend/.env: OK."
    else echo "[CHECK] backend/.env: se creara desde .env.example."; fi
  fi
  if [ "$NEED_FL" -eq 1 ]; then
    if command -v flutter >/dev/null 2>&1; then echo "[CHECK] Flutter: OK."
    else echo "[CHECK] Flutter: NO DETECTADO."; fail=1; fi
    if [ -n "$PYTHON_CMD" ] && pub_cache_ok; then echo "[CHECK] Flutter pub cache: OK."
    else echo "[CHECK] Flutter pub cache: se regenerara al arrancar."; fi
  fi
  for p in 8000 3000; do
    if port_in_use "$p"; then echo "[CHECK] Puerto $p ocupado — se reasignara solo."
    else echo "[CHECK] Puerto $p libre."; fi
  done
  if [ "$fail" -eq 0 ]; then echo "[CHECK] Entorno listo para arrancar."; exit 0; fi
  echo "[CHECK] Faltan requisitos — ver arriba."
  exit 1
fi

DOCKER_DAEMON=0
if command -v docker >/dev/null 2>&1 && [ "$IS_WEB" -eq 0 ]; then
  if docker info >/dev/null 2>&1; then
    DOCKER_DAEMON=1
  else
    echo "[DOCKER] Docker instalado pero el daemon no responde — usando entorno local."
  fi
fi
if [ "$DOCKER_DAEMON" -eq 1 ]; then
  echo "[DOCKER] Usando Docker..."
  cd "$ROOT"

  # Docker port check (only when launching services)
  if [ "$IS_BUILD_ALL" -eq 0 ] && [ "$IS_BUILD" -eq 0 ] && [ "$IS_BUILD_FRONTEND" -eq 0 ] && [ "$IS_BUILD_BACKEND" -eq 0 ] && [ "$IS_MIGRATE" -eq 0 ] && [ "$IS_TEST_BACKEND" -eq 0 ] && [ "$IS_TEST_FRONTEND" -eq 0 ]; then
    DOCKER_BACKEND_PORT=8000; DOCKER_FRONTEND_PORT=3000
    find_free_port 8000 DOCKER_BACKEND_PORT
    find_free_port 3000 DOCKER_FRONTEND_PORT
    if [ "$IS_MARIADB" -eq 1 ] || [ "$IS_TEST_MIGRATION" -eq 1 ]; then
      find_free_port 3306 DOCKER_MARIADB_PORT
      export PORT_DB="$DOCKER_MARIADB_PORT"
    fi
    if [ "$IS_FINAL" -eq 1 ]; then
      DOCKER_FRONTEND_PROD=80
      find_free_port 80 DOCKER_FRONTEND_PROD
    fi
    export PORT_BACKEND="$DOCKER_BACKEND_PORT"
    export PORT_FRONTEND="$DOCKER_FRONTEND_PORT"
    export BACKEND_URL="http://localhost:$DOCKER_BACKEND_PORT"
    echo "[DOCKER] Usando puertos: BACKEND=$DOCKER_BACKEND_PORT FRONTEND=$DOCKER_FRONTEND_PORT"
    if [ "$IS_FINAL" -eq 1 ]; then
      export PORT_FRONTEND_PROD="$DOCKER_FRONTEND_PROD"
      echo "[DOCKER]   Frontend prod: $DOCKER_FRONTEND_PROD"
    fi
    if [ "$DOCKER_BACKEND_PORT" -ne 8000 ] || [ "$DOCKER_FRONTEND_PORT" -ne 3000 ]; then
      echo "[DOCKER] Nota: exporta PORT_BACKEND / PORT_FRONTEND si docker-compose.yml los soporta."
    fi
  fi

  if [ "$IS_BUILD_ALL" -eq 1 ]; then
    echo "[BUILD-ALL] Construyendo paquetes distribubles..."
    if command -v pwsh >/dev/null 2>&1; then
      pwsh -ExecutionPolicy Bypass -File "$ROOT/tools/build-all.ps1"
    elif command -v powershell >/dev/null 2>&1; then
      powershell -ExecutionPolicy Bypass -File "$ROOT/tools/build-all.ps1"
    else
      echo "[BUILD-ALL] ERROR: Se requiere PowerShell (pwsh) para --build-all"
      echo "  Instala PowerShell Core: https://github.com/PowerShell/PowerShell"
      echo ""
      case "$OS_FAMILY" in
        debian) echo "  sudo apt install -y powershell" ;;
        fedora) echo "  sudo dnf install -y powershell" ;;
        alpine) echo "  sudo apk add powershell" ;;
        suse)   echo "  sudo zypper install -y powershell" ;;
        macos)  echo "  brew install --cask powershell" ;;
        *)      echo "  O via snap: sudo snap install powershell --classic" ;;
      esac
      exit 1
    fi
    echo "[BUILD-ALL] Listo. Los paquetes estan en $ROOT/builds/"
    exit 0
  fi

  if [ "$IS_BUILD" -eq 1 ]; then
    echo "[BUILD] Construyendo imagenes Docker..."
    docker compose build
    echo "[BUILD] Listo."
    exit 0
  fi

  if [ "$IS_BUILD_FRONTEND" -eq 1 ]; then
    docker compose build frontend
    exit 0
  fi

  if [ "$IS_BUILD_BACKEND" -eq 1 ]; then
    docker compose build backend
    exit 0
  fi

  if [ "$IS_MIGRATE" -eq 1 ]; then
    echo "[MIGRATE] Ejecutando migraciones..."
    docker compose run --rm backend alembic upgrade head
    exit 0
  fi

  if [ "$IS_TEST_MIGRATION" -eq 1 ]; then
    echo "[TEST-MIGRATION] Iniciando MariaDB..."
    docker compose --profile db up -d db

    echo "[TEST-MIGRATION] Esperando a que MariaDB este lista..."
    RETRIES=0
    while [ "$RETRIES" -lt 20 ]; do
      sleep 3
      docker compose exec -T db mariadb -u root -prootpassword -e "SELECT 1" >/dev/null 2>&1 && break
      RETRIES=$((RETRIES + 1))
      if [ "$RETRIES" -ge 20 ]; then
        echo "[TEST-MIGRATION] ERROR: MariaDB no respondio tras 60s"
        docker compose down
        exit 1
      fi
    done

    DB_URL="mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db"

    echo "[TEST-MIGRATION] MariaDB lista. Ejecutando migraciones..."
    docker compose run --rm -e DATABASE_URL="$DB_URL" backend alembic upgrade head
    if [ $? -ne 0 ]; then
      echo "[TEST-MIGRATION] ERROR en migraciones"
      docker compose down
      exit 1
    fi

    echo "[TEST-MIGRATION] Validando tablas creadas..."
    docker compose run --rm -e DATABASE_URL="$DB_URL" backend python -c "import os; from sqlalchemy import create_engine, text; e=create_engine(os.environ['DATABASE_URL']); c=e.connect(); r=c.execute(text('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()')); n=r.scalar(); print(f'TABLAS CREADAS: {n}'); c.close()"

    echo "[TEST-MIGRATION] Migracion completada correctamente."
    echo "[TEST-MIGRATION] Limpiando contenedores..."
    docker compose down
    exit 0
  fi

  if [ "$IS_TEST_BACKEND" -eq 1 ]; then
    echo "[TEST:BACKEND] Ejecutando pytest en Docker..."
    docker compose run --rm backend python -m pytest tests/ -x -q --tb=short
    exit $?
  fi

  if [ "$IS_TEST_FRONTEND" -eq 1 ]; then
    echo "[TEST:FRONTEND] Ejecutando flutter test en Docker..."
    docker compose run --rm frontend flutter test
    exit $?
  fi

  if [ "$IS_FINAL" -eq 1 ]; then
    echo "[DOCKER] Iniciando en modo produccion..."
    docker compose --profile prod up -d
    : ${PORT_BACKEND:=8000}
    : ${PORT_FRONTEND_PROD:=80}
    echo "[DOCKER] Backend: http://localhost:$PORT_BACKEND  |  Frontend: http://localhost:$PORT_FRONTEND_PROD"
    exit 0
  fi

  if [ "$IS_KILL" -eq 1 ]; then
    echo "[KILL] Deteniendo contenedores Docker..."
    docker compose down
    exit 0
  fi

  if ! container_pub_cache_ok; then
    echo "[ENV] Caché de Flutter de otro entorno, regenerando en contenedor..."
    rm -rf "$FRONTEND_DIR/.dart_tool" "$FRONTEND_DIR/.flutter-plugins" "$FRONTEND_DIR/.flutter-plugins-dependencies"
  fi
  : ${PORT_BACKEND:=8000}; : ${PORT_FRONTEND:=3000}
  echo "[DOCKER] Iniciando servicios de desarrollo en http://localhost:$PORT_BACKEND y http://localhost:$PORT_FRONTEND ..."
  if [ "$NO_BACKEND" -eq 1 ]; then
    docker compose up --no-deps frontend
  elif [ "$NO_FRONTEND" -eq 1 ]; then
    docker compose up --no-deps backend
  elif [ "$IS_MARIADB" -eq 1 ]; then
    docker compose --profile db up
  else
    docker compose up
  fi
  exit 0
fi

# ================================================================
# LOCAL FALLBACK
# ================================================================
echo ""
echo "[DOCKER] Docker no disponible — usando entorno local."
echo ""

show_setup_help() {
  echo "========================================"
  echo "  ERROR: Docker no disponible"
  echo "========================================"
  echo ""
  echo "Los comandos --build, --build-all, --build-frontend,"
  echo "--build-backend y --test-migration requieren Docker."
  echo ""
  echo "Para instalar Docker en este sistema:"
  echo ""
  case "$OS_FAMILY" in
    debian)
      echo "  curl -fsSL https://get.docker.com | sh"
      echo "  sudo usermod -aG docker \$USER"
      ;;
    fedora)
      echo "  sudo dnf install -y dnf-plugins-core"
      echo "  sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo"
      echo "  sudo dnf install -y docker-ce docker-ce-cli containerd.io"
      echo "  sudo systemctl start docker"
      ;;
    alpine)
      echo "  sudo apk add docker docker-compose"
      echo "  sudo rc-update add docker boot"
      echo "  sudo service docker start"
      ;;
    suse)
      echo "  sudo zypper install -y docker docker-compose"
      echo "  sudo systemctl start docker"
      ;;
    macos)
      echo "  brew install --cask docker"
      echo "  O descargar de: https://docs.docker.com/desktop/install/mac/"
      ;;
    freebsd)
      echo "  sudo pkg install docker docker-compose"
      echo "  sudo sysrc docker_enable=YES"
      echo "  sudo service docker start"
      ;;
    arch)
      echo "  sudo pacman -S docker docker-compose"
      echo "  sudo systemctl start docker"
      ;;
    freebsd)
      echo "  Solucion: sudo pkg install python3 py3-pip py3-venv"
      ;;
    *)
      echo "  Descarga Python 3.12+ desde https://www.python.org/downloads/"
      ;;
  esac
  echo "  $PYTHON_CMD -m venv .venv  (en backend/)"
  echo "  $PYTHON_CMD -m pip install -r requirements.txt"
  echo "  flutter pub get  (en frontend/)"

  if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "  [!] Python 3.12+ no detectado."
    case "$OS_FAMILY" in
      debian) echo "  Instalar: sudo apt install -y python3 python3-venv python3-pip" ;;
      fedora) echo "  Instalar: sudo dnf install -y python3 python3-pip" ;;
      alpine) echo "  Instalar: sudo apk add python3 py3-pip" ;;
      suse)   echo "  Instalar: sudo zypper install -y python3 python3-pip" ;;
      macos)  echo "  Instalar: brew install python@3.12" ;;
      freebsd) echo "  Instalar: sudo pkg install python3 py3-pip" ;;
      *)      echo "  Descargar: https://www.python.org/downloads/" ;;
    esac
  fi

  if ! command -v flutter >/dev/null 2>&1; then
    echo ""
    echo "  [!] Flutter SDK no detectado."
    echo "  Instalar:"
    case "$OS_FAMILY" in
      debian) echo "    sudo snap install flutter --classic" ;;
      *)      echo "    git clone https://github.com/flutter/flutter.git -b stable /opt/flutter"
              echo "    export PATH=\$PATH:/opt/flutter/bin" ;;
    esac
  fi

  echo ""
  echo "  O re-ejecuta con --install-missing para intentarlo automatico."
  echo ""
  echo "  Ejecuta './start.sh --help' para mas detalles."
  echo ""
  exit 1
}
if [ "$IS_BUILD_FRONTEND" -eq 1 ] || [ "$IS_BUILD_BACKEND" -eq 1 ] || \
   [ "$IS_TEST_MIGRATION" -eq 1 ]; then
  show_setup_help
fi

if [ "$OS_FAMILY" = "unknown" ] && [ "$OS" = "linux" ]; then
  echo "[WARN] No se pudo identificar la distribucion Linux."
  echo "  El script intentara continuar, pero si encuentras errores"
  echo "  asegurate de tener Python 3.12+ y Flutter SDK instalados."
  echo ""
fi

# ---- Kill (local) ----
if [ "$IS_KILL" -eq 1 ]; then
  echo "[KILL] Buscando procesos de backend y frontend..."
  for proc in python python3 dart flutter; do
    pkill -f "$proc" 2>/dev/null && echo "  Matados procesos de $proc" || true
  done
  exit 0
fi

# ---- Environment setup ----
setup_env() {
  if [ ! -f "$BACKEND_DIR/.env" ] && [ -f "$BACKEND_DIR/.env.example" ]; then
    echo "[ENV] Creando .env desde .env.example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
  fi

  BACKEND_PYTHON="$PYTHON_CMD"

  if [ -z "$PYTHON_CMD" ] && [ "$NEED_PY" -eq 1 ]; then
    echo "[ENV] ERROR: Python 3 no encontrado (o re-ejecuta con --install-missing)."
    case "$OS_FAMILY" in
      freebsd) echo "  Solucion: sudo pkg install python3 py3-pip" ;;
      debian) echo "  Solucion: sudo apt install -y python3 python3-venv python3-pip" ;;
      fedora) echo "  Solucion: sudo dnf install -y python3 python3-pip" ;;
      alpine) echo "  Solucion: sudo apk add python3 py3-pip" ;;
      suse)   echo "  Solucion: sudo zypper install -y python3 python3-pip" ;;
      macos)  echo "  Solucion: brew install python@3.12" ;;
      *)      echo "  Descarga Python 3.12+ desde https://www.python.org/downloads/" ;;
    esac
    exit 1
  elif [ -z "$PYTHON_CMD" ]; then
    echo "[SISTEMA] WARNING: Python no detectado (solo frontend)."
  fi

  pyver_full="$($PYTHON_CMD --version 2>&1 | awk '{print $2}')"
  case "$pyver_full" in
    3.1[2-9]*|3.[2-9][0-9]*|[4-9]*) ;;
    *) echo "[SISTEMA] WARNING: Python $pyver_full detectado — se requiere 3.12+." ;;
  esac

  if [ "$NEED_PY" -eq 1 ] && [ -f "$BACKEND_DIR/requirements.txt" ]; then
    if ! venv_ok; then
      if [ -d "$BACKEND_DIR/.venv" ]; then
        echo "[ENV] Entorno virtual obsoleto (de otro equipo), recreando..."
        rm -rf "$BACKEND_DIR/.venv"
      else
        echo "[ENV] Creando entorno virtual para backend..."
      fi
      (cd "$BACKEND_DIR" && $PYTHON_CMD -m venv .venv) || {
        echo "[ENV] ERROR: No se pudo crear .venv"
        echo "  Asegurate de tener python3-venv instalado."
        case "$OS_FAMILY" in
          debian) echo "  sudo apt install -y python3-venv" ;;
          fedora) echo "  sudo dnf install -y python3-pip" ;;
        esac
        exit 1
      }
    fi
    if [ -f "$BACKEND_DIR/.venv/bin/python" ]; then
      hash_file() {
        if command -v sha256sum >/dev/null 2>&1; then
          sha256sum "$1" | cut -d' ' -f1 | tr 'a-f' 'A-F'
        else
          shasum -a 256 "$1" | cut -d' ' -f1 | tr 'a-f' 'A-F'
        fi
      }
      new_hash="$(hash_file "$BACKEND_DIR/requirements.txt")"
      if [ -f "$BACKEND_DIR/requirements-dev.txt" ]; then
        new_hash="$new_hash$(hash_file "$BACKEND_DIR/requirements-dev.txt")"
      fi
      saved_hash=""
      [ -f "$BACKEND_DIR/.venv/.req_hash" ] && saved_hash="$(cat "$BACKEND_DIR/.venv/.req_hash")"
      if [ -n "$new_hash" ] && [ "$new_hash" = "$saved_hash" ] && "$BACKEND_DIR/.venv/bin/python" -c "import uvicorn, fastapi" >/dev/null 2>&1; then
        echo "[ENV] Dependencias del backend al dia, omitiendo pip install."
      else
        echo "[ENV] Instalando dependencias del backend (puede tardar minutos la primera vez)..."
        "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt" || { echo "[ENV] ERROR en pip install"; exit 1; }
        if [ -f "$BACKEND_DIR/requirements-dev.txt" ]; then
          "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements-dev.txt" || { echo "[ENV] ERROR en pip install (dev)"; exit 1; }
        fi
        [ -n "$new_hash" ] && printf '%s' "$new_hash" > "$BACKEND_DIR/.venv/.req_hash"
      fi
      BACKEND_PYTHON="$BACKEND_DIR/.venv/bin/python"
    fi
  fi

  if [ "$NEED_FL" -eq 1 ] && [ -f "$FRONTEND_DIR/pubspec.yaml" ] && ! pub_cache_ok; then
    if command -v flutter >/dev/null 2>&1; then
      echo "[ENV] Caché de Flutter obsoleta (de otro equipo), regenerando..."
      (cd "$FRONTEND_DIR" && flutter pub get) || (cd "$FRONTEND_DIR" && flutter pub get --offline) || {
        echo "[ENV] WARNING: No se pudo regenerar la caché de Flutter"
      }
    else
      echo "[ENV] WARNING: Flutter no encontrado. Instalalo para desarrollo frontend."
      echo "  https://docs.flutter.dev/get-started/install"
    fi
  fi

  echo "[ENV] Entorno listo."
  export BACKEND_PYTHON
}

if { [ "$NEED_PY" -eq 1 ] && [ -z "$PYTHON_CMD" ]; } || { [ "$NEED_FL" -eq 1 ] && ! command -v flutter >/dev/null 2>&1; }; then
  install_guide
  do_install="$IS_INSTALL_MISSING"
  if [ "$do_install" -eq 0 ] && [ -t 0 ]; then
    printf "¿Intentar instalacion automatica de lo que falta? (s/N): "
    read -r ans || true
    case "$ans" in [sSyY]*) do_install=1 ;; esac
  fi
  if [ "$do_install" -eq 1 ]; then
    install_missing "$NEED_PY" "$NEED_FL"
    detect_python
    detect_flutter
  fi
fi

setup_env

if [ "$IS_TEST_BACKEND" -eq 1 ] || [ "$IS_TEST_FRONTEND" -eq 1 ]; then
  [ "$IS_TEST_BACKEND" -eq 1 ] && NO_BACKEND=1
  [ "$IS_TEST_FRONTEND" -eq 1 ] && NO_FRONTEND=1
fi

BACKEND_PORT=8000; FRONTEND_PORT=3000; MARIADB_PORT=3306; FRONTEND_PROD_PORT=80
[ "$NO_BACKEND" -eq 0 ] && find_free_port 8000 BACKEND_PORT
[ "$NO_FRONTEND" -eq 0 ] && find_free_port 3000 FRONTEND_PORT
[ "$IS_MARIADB" -eq 1 ] && find_free_port 3306 MARIADB_PORT
[ "$IS_FINAL" -eq 1 ] && [ "$NO_FRONTEND" -eq 0 ] && find_free_port 80 FRONTEND_PROD_PORT
echo ""
echo "[PUERTO] Mapeo final:"
[ "$NO_BACKEND" -eq 0 ] && echo "  Backend       -> http://localhost:$BACKEND_PORT"
if [ "$NO_FRONTEND" -eq 0 ]; then
  if [ "$IS_FINAL" -eq 1 ]; then echo "  Frontend      -> http://localhost:$FRONTEND_PROD_PORT"
  else echo "  Frontend      -> http://localhost:$FRONTEND_PORT"
  fi
fi
[ "$IS_MARIADB" -eq 1 ] && echo "  MariaDB       -> localhost:$MARIADB_PORT"
echo ""

# ---- MariaDB ----
DB_URL=""
if [ "$IS_MARIADB" -eq 1 ]; then
  DB_URL="mariadb+pymysql://clakettes_user:clakettes_password@localhost:$MARIADB_PORT/clakettes_db"
  export DATABASE_URL="$DB_URL"
  echo "[MARIADB] Usando MariaDB: $DB_URL"
fi

# ---- Migrate ----
if [ "$IS_MIGRATE" -eq 1 ]; then
  echo "[MIGRATE] Ejecutando migraciones de base de datos..."
  (cd "$BACKEND_DIR" && "$BACKEND_PYTHON" -m alembic upgrade head)
fi

# ---- Tests ----
if [ "$IS_TEST_BACKEND" -eq 1 ]; then
  echo "[TEST:BACKEND] Ejecutando pytest..."
  (cd "$BACKEND_DIR" && "$BACKEND_PYTHON" -m pytest tests/ -x -q --tb=short)
  if [ $? -eq 0 ]; then echo "[TEST:BACKEND] Todos los tests pasaron"
  else echo "[TEST:BACKEND] Fallaron algunos tests"; fi
fi

if [ "$IS_TEST_FRONTEND" -eq 1 ]; then
  echo "[TEST:FRONTEND] Ejecutando flutter test..."
  (cd "$FRONTEND_DIR" && flutter test)
  if [ $? -eq 0 ]; then echo "[TEST:FRONTEND] Todos los tests pasaron"
  else echo "[TEST:FRONTEND] Fallaron algunos tests"; fi
fi

ONLY_TESTS=0
[ "$IS_TEST_BACKEND" -eq 1 ] || [ "$IS_TEST_FRONTEND" -eq 1 ] && ONLY_TESTS=1
if [ "$ONLY_TESTS" -eq 1 ]; then exit 0; fi

PID_FILE="$(mktemp)"
cleanup() {
  echo ""; echo "Deteniendo procesos..."
  if [ -f "$PID_FILE" ]; then
    while IFS= read -r pid; do kill "$pid" 2>/dev/null || true; done < "$PID_FILE"
    rm -f "$PID_FILE"
  fi
  echo "Detenido."
}
trap cleanup EXIT INT TERM

# ---- Backend (local) ----
DART_DEFINE="--dart-define=BACKEND_URL=http://localhost:$BACKEND_PORT"
if [ "$NO_BACKEND" -eq 0 ]; then
  echo "[BACKEND] Iniciando uvicorn en http://localhost:$BACKEND_PORT ..."
  (cd "$BACKEND_DIR" && "$BACKEND_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload) &
  echo $! >> "$PID_FILE"
  echo "[BACKEND] Esperando respuesta en http://localhost:$BACKEND_PORT/health ..."
  backend_pid="$(tail -n 1 "$PID_FILE")"
  healthy=0
  for i in $(seq 1 30); do
    sleep 2
    if ! kill -0 "$backend_pid" 2>/dev/null; then
      echo "[BACKEND] ERROR: el proceso termino al arrancar."
      break
    fi
    if "$BACKEND_PYTHON" -c "import urllib.request; urllib.request.urlopen('http://localhost:$BACKEND_PORT/health',timeout=3)" >/dev/null 2>&1; then
      healthy=1
      break
    fi
  done
  if [ "$healthy" -eq 1 ]; then echo "[BACKEND] OK (200 /health)"
  else echo "[BACKEND] WARNING: sin respuesta tras 60s."; fi
fi

# ---- Frontend (local) ----
if [ "$NO_FRONTEND" -eq 0 ]; then
  if [ "$IS_FINAL" -eq 1 ]; then
    echo "[FRONTEND] Build produccion..."
    (cd "$FRONTEND_DIR" && flutter build web "$DART_DEFINE") || { echo "[FRONTEND] ERROR en build"; exit 1; }
    echo "[FRONTEND] Sirviendo build/web en http://localhost:$FRONTEND_PROD_PORT ..."
    (cd "$FRONTEND_DIR/build/web" && "$BACKEND_PYTHON" -m http.server "$FRONTEND_PROD_PORT" --bind 0.0.0.0) &
    echo $! >> "$PID_FILE"
    sleep 2
    if [ -n "$BROWSER" ]; then
      eval "$BROWSER" "http://localhost:$FRONTEND_PROD_PORT" &
    fi
  elif [ "$IS_WEB" -eq 1 ]; then
    echo "[FRONTEND] Iniciando Flutter web en http://localhost:$FRONTEND_PORT con navegador..."
    (cd "$FRONTEND_DIR" && flutter run -d chrome --web-port "$FRONTEND_PORT" "$DART_DEFINE") &
    echo $! >> "$PID_FILE"
  else
    echo "[FRONTEND] Iniciando Flutter web-server en http://localhost:$FRONTEND_PORT ..."
    (cd "$FRONTEND_DIR" && flutter run -d web-server --web-port "$FRONTEND_PORT" "$DART_DEFINE") &
    echo $! >> "$PID_FILE"
    sleep 15
    if [ -n "$BROWSER" ]; then
      eval "$BROWSER" "http://localhost:$FRONTEND_PORT" &
    fi
  fi
fi

echo ""; echo "Presiona Ctrl+C para detener todo."; echo ""
wait
