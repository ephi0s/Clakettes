@echo off
chcp 65001 >nul
title Clakettes Launcher

echo ========================================
echo   Clakettes Launcher
echo ========================================
echo.

if /I "%1"=="--help" goto :help
if /I "%1"=="/?" goto :help

set ROOT=%~dp0

:: Detectar Brave/Chrome y establecer CHROME_EXECUTABLE
set BROWSER=
if exist "%ProgramFiles%\BraveSoftware\Brave-Browser-Beta\Application\brave.exe" set BROWSER=%ProgramFiles%\BraveSoftware\Brave-Browser-Beta\Application\brave.exe
if exist "%ProgramFiles%\BraveSoftware\Brave-Browser-Stable\Application\brave.exe" set BROWSER=%ProgramFiles%\BraveSoftware\Brave-Browser-Stable\Application\brave.exe
if not defined BROWSER if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set BROWSER=%ProgramFiles%\Google\Chrome\Application\chrome.exe
if not defined BROWSER if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set BROWSER=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe
if not defined BROWSER if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set BROWSER=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
if defined BROWSER set CHROME_EXECUTABLE=%BROWSER%

:: Flags
set IS_WEB=0
set IS_FINAL=0
set IS_DEV=0
set IS_MIGRATE=0
set IS_TEST_MIGRATION=0
set IS_MARIADB=0
set IS_TEST_BACKEND=0
set IS_TEST_FRONTEND=0
set NO_BACKEND=0
set NO_FRONTEND=0
set IS_KILL=0
set IS_BUILD=0
set IS_BUILD_ALL=0
set IS_BUILD_FRONTEND=0
set IS_BUILD_BACKEND=0

for %%a in (%*) do (
    if /I "%%a"=="--web" set IS_WEB=1
    if /I "%%a"=="--final" set IS_FINAL=1
    if /I "%%a"=="--dev" set IS_DEV=1
    if /I "%%a"=="--migrate" set IS_MIGRATE=1
    if /I "%%a"=="--test-migration" set IS_TEST_MIGRATION=1
    if /I "%%a"=="--mariadb" set IS_MARIADB=1
    if /I "%%a"=="--test-backend" set IS_TEST_BACKEND=1
    if /I "%%a"=="--test-frontend" set IS_TEST_FRONTEND=1
    if /I "%%a"=="--no-backend" set NO_BACKEND=1
    if /I "%%a"=="--no-frontend" set NO_FRONTEND=1
    if /I "%%a"=="--kill" set IS_KILL=1
    if /I "%%a"=="--build" set IS_BUILD=1
    if /I "%%a"=="--build-all" set IS_BUILD_ALL=1
    if /I "%%a"=="--build-frontend" set IS_BUILD_FRONTEND=1
    if /I "%%a"=="--build-backend" set IS_BUILD_BACKEND=1
)

:: --- Docker check ---
if %IS_KILL%==1 goto :kill
if %IS_WEB%==1 goto :local_mode
where docker >nul 2>&1
if errorlevel 1 goto :local_mode
docker info >nul 2>&1
if errorlevel 1 (
    echo [DOCKER] Docker instalado pero el daemon no responde — usando entorno local.
    goto :local_mode
)
goto :docker_mode
:local_mode

:: ============================================
:: LOCAL FALLBACK (Docker no disponible)
:: ============================================
if %IS_WEB%==0 (
    echo.
    echo [DOCKER] Docker no disponible — usando entorno local.
    echo.
)

if %IS_BUILD_ALL%==1 goto :setup_help
if %IS_BUILD%==1 goto :setup_help
if %IS_BUILD_FRONTEND%==1 goto :setup_help
if %IS_BUILD_BACKEND%==1 goto :setup_help
if %IS_TEST_MIGRATION%==1 goto :setup_help

for %%F in ("C:\tools\flutter\bin" "%USERPROFILE%\flutter\bin" "C:\flutter\bin" "C:\src\flutter\bin" "%LOCALAPPDATA%\Flutter\bin") do if exist "%%~F\flutter.bat" set "PATH=%PATH%;%%~F"

set NEED_PY=1
if %NO_BACKEND%==1 set NEED_PY=0
if %IS_MIGRATE%==1 set NEED_PY=1
if %IS_TEST_BACKEND%==1 set NEED_PY=1
set NEED_FLUTTER=1
if %NO_FRONTEND%==1 set NEED_FLUTTER=0
if %IS_TEST_FRONTEND%==1 set NEED_FLUTTER=1
if %IS_FINAL%==1 set NEED_FLUTTER=1
if %IS_FINAL%==1 set NEED_PY=1

call :find_python
if errorlevel 1 (
    if %NEED_PY%==1 (
        echo ========================================
        echo   ERROR: Python 3.12+ no detectado
        echo ========================================
        echo   Descarga: https://www.python.org/downloads/
        echo   Requiere 'py -3', 'python' o 'python3' en PATH.
        pause
        exit /b 1
    )
    echo [SISTEMA] WARNING: Python no detectado ^(solo frontend^).
) else (
    echo [SISTEMA] Python detectado.
)
where flutter >nul 2>&1
if errorlevel 1 (
    if %NEED_FLUTTER%==1 echo [SISTEMA] WARNING: Flutter no detectado. Descarga: https://docs.flutter.dev/get-started/install
)

:: Environment setup
if not exist "%ROOT%backend\.env" (
    if exist "%ROOT%backend\.env.example" (
        echo [ENV] Creando .env desde .env.example...
        copy "%ROOT%backend\.env.example" "%ROOT%backend\.env" >nul
    )
)

set BACKEND_PYTHON=%PYTHON_CMD%
if %NEED_PY%==1 if exist "%ROOT%backend\requirements.txt" (
    call :check_venv
    if errorlevel 1 (
        if exist "%ROOT%backend\.venv\" (
            echo [ENV] Entorno virtual obsoleto (de otro equipo), recreando...
            rmdir /s /q "%ROOT%backend\.venv"
        ) else (
            echo [ENV] Creando entorno virtual para backend...
        )
        cd /d "%ROOT%backend"
        call %PYTHON_CMD% %PYTHON_ARGS% -m venv .venv
        if errorlevel 1 (
            echo [ENV] ERROR: No se pudo crear .venv
            pause
            exit /b 1
        )
        cd /d "%ROOT%"
    )
    if exist "%ROOT%backend\.venv\Scripts\python.exe" (
        call :need_pip
        if errorlevel 1 (
            echo [ENV] Instalando dependencias del backend ^(puede tardar minutos la primera vez^)...
            "%ROOT%backend\.venv\Scripts\pip" install -r "%ROOT%backend\requirements.txt"
            if errorlevel 1 (
                echo [ENV] ERROR en pip install
                pause
                exit /b 1
            )
            if exist "%ROOT%backend\requirements-dev.txt" (
                "%ROOT%backend\.venv\Scripts\pip" install -r "%ROOT%backend\requirements-dev.txt"
                if errorlevel 1 (
                    echo [ENV] ERROR en pip install ^(dev^)
                    pause
                    exit /b 1
                )
            )
            call :save_pip_hash
        ) else (
            echo [ENV] Dependencias del backend al dia, omitiendo pip install.
        )
        set BACKEND_PYTHON=%ROOT%backend\.venv\Scripts\python
    ) else (
        echo [ENV] ERROR: .venv sin python.exe tras crearlo
        pause
        exit /b 1
    )
)

if %NEED_FLUTTER%==1 if exist "%ROOT%frontend\pubspec.yaml" (
    call :check_pubcache
    if errorlevel 1 (
        where flutter >nul 2>&1
        if not errorlevel 1 (
            echo [ENV] Cache de Flutter obsoleta (de otro equipo), regenerando...
            cd /d "%ROOT%frontend"
            call flutter pub get
            if errorlevel 1 call flutter pub get --offline
            cd /d "%ROOT%"
            call :check_pubcache
            if errorlevel 1 echo [ENV] ERROR: no se pudo regenerar la cache de Flutter
        ) else (
            echo [ENV] WARNING: Flutter no encontrado. Instalalo para desarrollo frontend.
        )
    )
)

echo [ENV] Entorno listo.
echo.

:: Tests (ajustan NO_BACKEND/NO_FRONTEND antes del mapeo de puertos)
if %IS_TEST_BACKEND%==1 if %NO_BACKEND%==0 set NO_BACKEND=1
if %IS_TEST_FRONTEND%==1 if %NO_FRONTEND%==0 set NO_FRONTEND=1

:: Port auto-assignment (antes de DATABASE_URL y del encabezado)
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set MARIADB_PORT=3306
set FRONTEND_PROD_PORT=80

if %NO_BACKEND%==0 call :find_free_port 8000 Backend BACKEND_PORT
if %NO_FRONTEND%==0 call :find_free_port 3000 Frontend FRONTEND_PORT
if %IS_MARIADB%==1 call :find_free_port 3306 MariaDB MARIADB_PORT
if %IS_FINAL%==1 if %NO_FRONTEND%==0 call :find_free_port 80 Frontend^(prod^) FRONTEND_PROD_PORT

echo.
echo [PUERTO] Mapeo final:
if %NO_BACKEND%==0 echo   Backend       -^> http://localhost:%BACKEND_PORT%
if %NO_FRONTEND%==0 if %IS_FINAL%==0 echo   Frontend      -^> http://localhost:%FRONTEND_PORT%
if %NO_FRONTEND%==0 if %IS_FINAL%==1 echo   Frontend      -^> http://localhost:%FRONTEND_PROD_PORT%
if %IS_MARIADB%==1 echo   MariaDB       -^> localhost:%MARIADB_PORT%
echo.

:: Database URL
if %IS_MARIADB%==1 (
    set DATABASE_URL=mariadb+pymysql://clakettes_user:clakettes_password@localhost:%MARIADB_PORT%/clakettes_db
    echo [MARIADB] Usando MariaDB: %DATABASE_URL%
)

:: Migraciones
if %IS_MIGRATE%==1 (
    echo [MIGRATE] Ejecutando migraciones de base de datos...
    cd /d "%ROOT%backend"
    call "%BACKEND_PYTHON%" -m alembic upgrade head
    if errorlevel 1 (
        echo [MIGRATE] ERROR en migraciones
        pause
        exit /b 1
    )
)

:: Tests
if %IS_TEST_BACKEND%==1 (
    echo [TEST:BACKEND] Ejecutando pytest...
    cd /d "%ROOT%backend"
    call "%BACKEND_PYTHON%" -m pytest tests/ -x -q --tb=short
    if errorlevel 1 (echo [TEST:BACKEND] Fallaron algunos tests) else (echo [TEST:BACKEND] Todos los tests pasaron)
    goto :eof
)

if %IS_TEST_FRONTEND%==1 (
    echo [TEST:FRONTEND] Ejecutando flutter test...
    cd /d "%ROOT%frontend"
    call flutter test
    if errorlevel 1 (echo [TEST:FRONTEND] Fallaron algunos tests) else (echo [TEST:FRONTEND] Todos los tests pasaron)
    goto :eof
)

:: Backend (local)
if %NO_BACKEND%==0 (
    echo [BACKEND] Iniciando uvicorn en http://localhost:%BACKEND_PORT% ...
    if defined DATABASE_URL (
        start "Clakettes Backend" cmd /c "set DATABASE_URL=%DATABASE_URL% && cd /d ""%ROOT%backend"" && "%BACKEND_PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"
    ) else (
        start "Clakettes Backend" cmd /c "cd /d ""%ROOT%backend"" && "%BACKEND_PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"
    )
    call :wait_backend
)

:: Frontend (local)
set DART_DEFINE=--dart-define=BACKEND_URL=http://localhost:%BACKEND_PORT%
if %NO_FRONTEND%==0 (
    if %IS_FINAL%==1 (
        echo [FRONTEND] Build produccion ...
        cd /d "%ROOT%frontend"
        call flutter build web %DART_DEFINE%
        if errorlevel 1 (
            echo [FRONTEND] ERROR en build
            pause
            exit /b 1
        )
        echo [FRONTEND] Sirviendo en http://localhost:%FRONTEND_PROD_PORT% ...
        start "Clakettes Frontend" cmd /c "cd /d ""%ROOT%frontend\build\web"" && "%BACKEND_PYTHON%" -m http.server %FRONTEND_PROD_PORT% --bind 0.0.0.0"
        if defined BROWSER (
            timeout /t 3 /nobreak >nul
            start "" "%BROWSER%" "http://localhost:%FRONTEND_PROD_PORT%"
        )
    ) else if %IS_WEB%==1 (
        if not "%BROWSER%"=="" echo [FRONTEND] Usando navegador: %BROWSER%
        echo [FRONTEND] Iniciando Flutter web en http://localhost:%FRONTEND_PORT% con CHROME_EXECUTABLE ...
        start "Clakettes Frontend" cmd /c "set CHROME_EXECUTABLE=%CHROME_EXECUTABLE% && cd /d ""%ROOT%frontend"" && flutter run -d chrome --web-port %FRONTEND_PORT% %DART_DEFINE%"
    ) else (
        echo [FRONTEND] Iniciando Flutter web-server en http://localhost:%FRONTEND_PORT% ...
        start "Clakettes Frontend" cmd /c "cd /d ""%ROOT%frontend"" && flutter run -d web-server --web-port %FRONTEND_PORT% %DART_DEFINE%"
        if defined BROWSER (
            timeout /t 15 /nobreak >nul
            start "" "%BROWSER%" "http://localhost:%FRONTEND_PORT%"
        )
    )
)

echo Procesos lanzados. Cierra las ventanas para detener.
echo.
goto :eof

:: ============================================
:: DOCKER MODE
:: ============================================
:docker_mode
cd /d "%ROOT%"
if not defined SECRET_KEY set SECRET_KEY=dev-secret-change-in-production

:: Docker port check (only when launching services)
if not %IS_BUILD_ALL%==1 if not %IS_BUILD%==1 if not %IS_BUILD_FRONTEND%==1 if not %IS_BUILD_BACKEND%==1 if not %IS_MIGRATE%==1 if not %IS_TEST_BACKEND%==1 if not %IS_TEST_FRONTEND%==1 (
    goto :docker_port_check
)
goto :docker_port_skip
:docker_port_check
set DOCKER_BCK=8000
set DOCKER_FNT=3000
call :find_free_port 8000 Backend DOCKER_BCK
call :find_free_port 3000 Frontend DOCKER_FNT
if %IS_MARIADB%==1 call :find_free_port 3306 MariaDB DOCKER_MDB
if defined DOCKER_MDB set PORT_DB=%DOCKER_MDB%
if %IS_FINAL%==1 call :find_free_port 80 "Frontend prod" DOCKER_FEP
set PORT_BACKEND=%DOCKER_BCK%
set PORT_FRONTEND=%DOCKER_FNT%
set BACKEND_URL=http://localhost:%DOCKER_BCK%
echo [DOCKER] Usando puertos: BACKEND=%PORT_BACKEND% FRONTEND=%PORT_FRONTEND%
if %IS_FINAL%==1 set PORT_FRONTEND_PROD=%DOCKER_FEP% & echo [DOCKER]   Frontend prod: %DOCKER_FEP%
:docker_port_skip

if %IS_BUILD_ALL%==1 (
    echo [BUILD-ALL] Construyendo paquetes distribubles...
    powershell -ExecutionPolicy Bypass -File "%ROOT%tools\build-all.ps1"
    echo [BUILD-ALL] Listo. Los paquetes estan en %ROOT%builds\
    pause
    goto :eof
)

if %IS_BUILD%==1 (
    echo [BUILD] Construyendo imagenes Docker...
    docker compose build
    echo [BUILD] Listo.
    pause
    goto :eof
)

if %IS_BUILD_FRONTEND%==1 (
    docker compose build frontend
    goto :eof
)

if %IS_BUILD_BACKEND%==1 (
    docker compose build backend
    goto :eof
)

if %IS_MIGRATE%==1 (
    echo [MIGRATE] Ejecutando migraciones...
    docker compose run --rm backend alembic upgrade head
    goto :eof
)

if %IS_TEST_MIGRATION%==1 goto :run_test_migration

if %IS_TEST_BACKEND%==1 (
    echo [TEST:BACKEND] Ejecutando pytest en Docker...
    docker compose run --rm backend python -m pytest tests/ -x -q --tb=short
    goto :eof
)

if %IS_TEST_FRONTEND%==1 (
    echo [TEST:FRONTEND] Ejecutando flutter test en Docker...
    docker compose run --rm frontend flutter test
    goto :eof
)

if %IS_FINAL%==1 (
    echo [DOCKER] Iniciando en modo produccion...
    docker compose --profile prod up -d
    if not defined PORT_BACKEND set PORT_BACKEND=8000
    if not defined PORT_FRONTEND_PROD set PORT_FRONTEND_PROD=80
    echo [DOCKER] Backend: http://localhost:%PORT_BACKEND%  |  Frontend: http://localhost:%PORT_FRONTEND_PROD%
    goto :eof
)

:: Default: dev mode
powershell -NoProfile -Command "$t=Get-Content '%ROOT%frontend\.dart_tool\package_config.json' -Raw -ErrorAction SilentlyContinue; if (-not $t) { exit 0 }; foreach ($m in [regex]::Matches($t,'(file://\S+)')) { $u=$m.Groups[1].Value; if ($u -match '^file:///') { if ($u.Substring(8) -notmatch '^(app|root|tmp)/') { exit 1 } } elseif ($u -match '^[a-zA-Z][a-zA-Z0-9+.-]*:') { exit 1 } }; exit 0" >nul 2>&1
if errorlevel 1 (
    echo [ENV] Cache de Flutter de otro entorno, regenerando en contenedor...
    if exist "%ROOT%frontend\.dart_tool\" rmdir /s /q "%ROOT%frontend\.dart_tool"
    if exist "%ROOT%frontend\.flutter-plugins" del "%ROOT%frontend\.flutter-plugins"
    if exist "%ROOT%frontend\.flutter-plugins-dependencies" del "%ROOT%frontend\.flutter-plugins-dependencies"
)
if not defined PORT_BACKEND set PORT_BACKEND=8000
if not defined PORT_FRONTEND set PORT_FRONTEND=3000
echo [DOCKER] Iniciando servicios de desarrollo en http://localhost:%PORT_BACKEND% y http://localhost:%PORT_FRONTEND% ...
if %NO_BACKEND%==1 (
    docker compose up --no-deps frontend
) else if %NO_FRONTEND%==1 (
    docker compose up --no-deps backend
) else if %IS_MARIADB%==1 (
    docker compose --profile db up
) else (
    docker compose up
)
goto :eof

:: ============================================
:: TEST MIGRATION
:: ============================================
:run_test_migration
setlocal enabledelayedexpansion
echo [TEST-MIGRATION] Iniciando MariaDB...
docker compose --profile db up -d db

echo [TEST-MIGRATION] Esperando a que MariaDB este lista...
set RETRIES=0
:test_mig_wait
timeout /t 3 /nobreak >nul
docker compose exec -T db mariadb -u root -prootpassword -e "SELECT 1" >nul 2>&1
if errorlevel 1 (
    set /a RETRIES+=1
    if !RETRIES! geq 20 (
        echo [TEST-MIGRATION] ERROR: MariaDB no respondio tras 60s
        docker compose down
        pause
        exit /b 1
    )
    goto test_mig_wait
)

set DB_URL=mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db

echo [TEST-MIGRATION] MariaDB lista. Ejecutando migraciones...
docker compose run --rm -e DATABASE_URL=!DB_URL! backend alembic upgrade head
if errorlevel 1 (
    echo [TEST-MIGRATION] ERROR en migraciones
    docker compose down
    pause
    exit /b 1
)

echo [TEST-MIGRATION] Validando tablas creadas...
docker compose run --rm -e DATABASE_URL=!DB_URL! backend python -c "import os; from sqlalchemy import create_engine, text; e=create_engine(os.environ['DATABASE_URL']); c=e.connect(); r=c.execute(text('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()')); n=r.scalar(); print(f'TABLAS CREADAS: {n}'); c.close()"

echo [TEST-MIGRATION] Migracion completada correctamente.
echo [TEST-MIGRATION] Limpiando contenedores...
docker compose down
pause
goto :eof

:: ============================================
:: KILL
:: ============================================
:kill
cd /d "%ROOT%"
echo [KILL] Deteniendo servicios...
docker compose down 2>nul || echo [KILL] Docker no disponible, usando comandos locales...
taskkill /f /im python.exe /t >nul 2>&1 && echo   Matados procesos python.exe
taskkill /f /im dart.exe /t >nul 2>&1 && echo   Matados procesos dart.exe
taskkill /f /im flutter.exe /t >nul 2>&1 && echo   Matados procesos flutter.exe
echo [KILL] Hecho.
goto :eof

:: ============================================
:: HELP
:: ============================================
:help
echo Clakettes Launcher (portable mode)
echo.
echo USO:
echo   start.bat                       Backend + frontend (Docker dev, o local si no hay Docker)
echo   start.bat --dev                 Igual que default
echo   start.bat --final               Backend + frontend (Docker produccion, o build local)
echo   start.bat --web                 Frontend con navegador (solo modo local)
echo   start.bat --no-backend          Solo frontend
echo   start.bat --no-frontend         Solo backend
echo   start.bat --mariadb             Incluye MariaDB (Docker: --profile db / local: variable)
echo   start.bat --migrate             Ejecuta migraciones (Docker: docker compose run)
echo   start.bat --test-migration      Prueba migracion completa con MariaDB
echo   start.bat --test-backend        Ejecuta tests del backend
echo   start.bat --test-frontend       Ejecuta tests del frontend
echo   start.bat --build               Construye imagenes Docker (desarrollo)
echo   start.bat --build-all           Construye paquetes distribubles (final)
echo   start.bat --build-frontend      Construye solo frontend (Docker)
echo   start.bat --build-backend       Construye solo backend (Docker)
echo   start.bat --kill                Para contenedores Docker y procesos locales
echo   start.bat --help                Muestra esta ayuda
echo.
echo REQUISITOS (Docker):
echo   - Docker Desktop (https://docs.docker.com/desktop/)
echo   - Docker automaticamente crea pip install + flutter pub get
echo.
echo REQUISITOS (local, si no hay Docker):
echo   - Python 3.12+ con pip ^(se detecta py -3 / python / python3; error si falta^)
echo   - Flutter SDK en PATH o rutas habituales ^(aviso si falta^)
echo   - .venv se crea solo si es invalido; pip install solo si cambian requirements
echo.
pause
goto :eof

:: ============================================
:: FIND FREE PORT
:: ============================================
:find_free_port
set DESIRED=%~1
set SERVICE=%~2
set VAR_NAME=%~3
netstat -ano | findstr ":%DESIRED% " >nul 2>&1
if errorlevel 1 (
    echo [PUERTO] %SERVICE% -^> %DESIRED% (puerto por defecto libre)
    set "%VAR_NAME%=%DESIRED%"
    goto :eof
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%DESIRED% "') do (
    for /f "tokens=1 delims= " %%b in ('tasklist /fi "PID eq %%a" /nh 2^>nul') do (
        echo [PUERTO] %SERVICE% necesita puerto %DESIRED% — ocupado por %%b (PID %%a), buscando libre...
        goto :ffp_owner
    )
)
echo [PUERTO] %SERVICE% necesita puerto %DESIRED% — esta en uso, buscando libre...
:ffp_owner
set TRY=60000
:ffp_loop
netstat -ano | findstr ":%TRY% " >nul 2>&1
if errorlevel 1 (
    echo [PUERTO] %SERVICE% -^> %TRY%
    set "%VAR_NAME%=%TRY%"
    goto :eof
)
set /a TRY+=1
if %TRY% gtr 65535 (
    echo [PUERTO] ERROR: No se encontro puerto libre para %SERVICE%
    pause
    exit /b 1
)
goto ffp_loop

:: ============================================
:: CHECK VENV / PUBCACHE / PYTHON / PIP HASH
:: ============================================
:check_venv
if not exist "%ROOT%backend\.venv\Scripts\python.exe" exit /b 1
if not exist "%ROOT%backend\.venv\pyvenv.cfg" exit /b 1
for /f "tokens=1* delims==" %%a in ('findstr /b /c:"home" "%ROOT%backend\.venv\pyvenv.cfg" 2^>nul') do (
    for /f "tokens=*" %%c in ("%%b") do if not exist "%%~c" exit /b 1
)
"%ROOT%backend\.venv\Scripts\python.exe" --version >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:find_python
set PYTHON_CMD=
set PYTHON_ARGS=
set PYVER=
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    set PYTHON_ARGS=-3
)
if not defined PYTHON_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 set PYTHON_CMD=python
)
if not defined PYTHON_CMD (
    python3 --version >nul 2>&1
    if not errorlevel 1 set PYTHON_CMD=python3
)
if not defined PYTHON_CMD exit /b 1
for /f "tokens=2 delims= " %%v in ('%PYTHON_CMD% %PYTHON_ARGS% --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set PYMAJ=%%a
    set PYMIN=%%b
)
if not "%PYMAJ%"=="3" exit /b 1
if %PYMIN% lss 12 echo [SISTEMA] WARNING: Python %PYVER% detectado — se requiere 3.12+.
exit /b 0

:need_pip
set REQ_HASH=
for /f %%h in ('powershell -NoProfile -Command "$h=(Get-FileHash '%ROOT%backend\requirements.txt' -Algorithm SHA256).Hash; if (Test-Path '%ROOT%backend\requirements-dev.txt') { $h+=(Get-FileHash '%ROOT%backend\requirements-dev.txt' -Algorithm SHA256).Hash }; Write-Output ($h -join '')"') do set REQ_HASH=%%h
set SAVED_HASH=
if exist "%ROOT%backend\.venv\.req_hash" set /p SAVED_HASH=<"%ROOT%backend\.venv\.req_hash"
if not "%REQ_HASH%"=="%SAVED_HASH%" exit /b 1
"%ROOT%backend\.venv\Scripts\python.exe" -c "import uvicorn, fastapi" >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:save_pip_hash
echo %REQ_HASH%>"%ROOT%backend\.venv\.req_hash"
goto :eof

:wait_backend
echo [BACKEND] Esperando respuesta en http://localhost:%BACKEND_PORT%/health ...
powershell -NoProfile -Command "$ok=$false; for ($i=0;$i -lt 30;$i++) { try { $c=[Net.Sockets.TcpClient]::new(); $r=$c.BeginConnect('127.0.0.1',%BACKEND_PORT%,$null,$null); if ($r.AsyncWaitHandle.WaitOne(1000)) { $c.EndConnect($r); $ok=$true; $c.Close(); break }; $c.Close() } catch {}; Start-Sleep -Seconds 2 }; if (-not $ok) { exit 1 }"
if errorlevel 1 echo [BACKEND] WARNING: sin respuesta tras 60s — revisa la ventana "Clakettes Backend".
goto :eof

:check_pubcache
powershell -NoProfile -Command "$c='%ROOT%frontend\.dart_tool\package_config.json'; if (-not (Test-Path $c)) { exit 1 }; try { $j=Get-Content $c -Raw | ConvertFrom-Json; if (-not $j.packages) { exit 1 }; $n=0; foreach ($p in $j.packages) { $u=''+$p.rootUri; if ($u -match '^file:///') { $l=$u.Substring(8) -replace '/','\'; if (-not (Test-Path $l)) { exit 1 }; $n++; if ($n -ge 8) { break } } elseif ($u -match '^file:') { $r=Join-Path (Split-Path $c -Parent) ($u.Substring(5) -replace '/','\'); if (-not (Test-Path $r)) { exit 1 } } }; if ($n -eq 0) { exit 1 }; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:: ============================================
:: SETUP HELP
:: ============================================
:setup_help
echo.
echo ========================================
echo   ERROR: Docker no disponible
echo ========================================
echo.
echo Los comandos --build, --build-all, --build-frontend y --build-backend
echo requieren Docker para funcionar.
echo.
echo Para configurar el entorno de desarrollo:
echo.
echo   Opcion 1 — Instalar Docker Desktop:
echo     https://docs.docker.com/desktop/
echo.
echo   Opcion 2 — Entorno local (sin Docker):
echo     - Python 3.12+ con pip
echo     - Flutter SDK en PATH o rutas habituales
echo     - Ejecuta el script sin flags para que configure .venv y flutter pub get
echo.
echo   Ejecuta "start.bat --help" para mas detalles.
echo.
pause
exit /b 1
