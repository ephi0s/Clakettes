param(
    [switch]$NoFrontend,
    [switch]$NoBackend,
    [switch]$Web,
    [switch]$Dev,
    [switch]$Final,
    [switch]$Migrate,
    [switch]$TestMigration,
    [switch]$MariaDB,
    [switch]$TestBackend,
    [switch]$TestFrontend,
    [switch]$Kill,
    [switch]$Help,
    [switch]$Build,
    [switch]$BuildAll,
    [switch]$BuildFrontend,
    [switch]$BuildBackend
)

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Parse -- prefixed args (compat with bat syntax / -Command invocation)
foreach ($a in $args) {
    switch -Wildcard ($a) {
        '--web'              { $Web = $true }
        '--final'            { $Final = $true }
        '--dev'              { $Dev = $true }
        '--migrate'          { $Migrate = $true }
        '--test-migration'   { $TestMigration = $true }
        '--mariadb'          { $MariaDB = $true }
        '--test-backend'     { $TestBackend = $true }
        '--test-frontend'    { $TestFrontend = $true }
        '--no-backend'       { $NoBackend = $true }
        '--no-frontend'      { $NoFrontend = $true }
        '--build'            { $Build = $true }
        '--build-all'        { $BuildAll = $true }
        '--build-frontend'   { $BuildFrontend = $true }
        '--build-backend'    { $BuildBackend = $true }
        '--help'             { $Help = $true }
        '/?'                 { $Help = $true }
    }
}

function Test-PortInUse {
    param([int]$Port)
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $result = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $result.AsyncWaitHandle.WaitOne(300)) { return $false }
        try { $client.EndConnect($result); return $true } catch { return $false }
    } catch { return $false }
    finally { $client.Close() }
}

function Find-FreePort {
    param([int]$Desired, [string]$Service)
    if (-not (Test-PortInUse $Desired)) {
        Write-Host "[PUERTO] $Service -> $Desired (puerto por defecto libre)" -ForegroundColor Green
        return $Desired
    }
    $owner = "?"
    $conn = netstat -ano 2>$null | Select-String ":$Desired\s"
    if ($conn) {
        $parts = ($conn -split '\s+')
        $ownerPid = $parts[-1]
        if ($ownerPid -match '^\d+$') {
            $proc = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
            $owner = if ($proc) { "$($proc.ProcessName) (PID $ownerPid)" } else { "PID $ownerPid" }
        }
    }
    Write-Host "[PUERTO] $Service necesita puerto $Desired — ocupado por $owner, buscando libre..." -ForegroundColor Yellow
    for ($try = 60000; $try -le 65535; $try++) {
        if (-not (Test-PortInUse $try)) { Write-Host "[PUERTO] $Service -> $try" -ForegroundColor Green; return $try }
    }
    Write-Host "[PUERTO] ERROR: No se encontro puerto libre para $Service" -ForegroundColor Red
    exit 1
}

function New-PortMapping {
    $script:BACKEND_PORT = if (-not $NoBackend) { Find-FreePort 8000 "Backend" } else { 8000 }
    $script:FRONTEND_PORT = if (-not $NoFrontend) { Find-FreePort 3000 "Frontend" } else { 3000 }
    $script:MARIADB_PORT = if ($MariaDB) { Find-FreePort 3306 "MariaDB" } else { 3306 }
    $script:FRONTEND_PROD_PORT = if ($Final -and -not $NoFrontend) { Find-FreePort 80 "Frontend (prod)" } else { 80 }
    Write-Host ""
    Write-Host "[PUERTO] Mapeo final:" -ForegroundColor Cyan
    if (-not $NoBackend) { Write-Host "  Backend       -> http://localhost:$script:BACKEND_PORT" }
    if (-not $NoFrontend) { if (-not $Final) { Write-Host "  Frontend      -> http://localhost:$script:FRONTEND_PORT" } else { Write-Host "  Frontend      -> http://localhost:$script:FRONTEND_PROD_PORT" } }
    if ($MariaDB) { Write-Host "  MariaDB       -> localhost:$script:MARIADB_PORT" }
    Write-Host ""
}

if ($Help) {
    @"
Clakettes Launcher (portable mode)

USO:
    .\start.ps1                        Backend + frontend (Docker dev, o local si no hay Docker)
    .\start.ps1 -Dev                   Igual que default
    .\start.ps1 -Final                 Backend + frontend (Docker produccion, o build local)
    .\start.ps1 -Web                   Frontend con navegador (solo modo local)
    .\start.ps1 -NoFrontend            Solo backend
    .\start.ps1 -NoBackend             Solo frontend
    .\start.ps1 -MariaDB               Incluye MariaDB (Docker: perfil db / local: variable)
    .\start.ps1 -Migrate               Ejecuta migraciones (Docker: docker compose run)
    .\start.ps1 -TestMigration          Prueba migracion completa con MariaDB
    .\start.ps1 -TestBackend           Ejecuta tests del backend
    .\start.ps1 -TestFrontend          Ejecuta tests del frontend
    .\start.ps1 -Build                 Construye imagenes Docker (desarrollo)
    .\start.ps1 -BuildAll              Construye paquetes distribubles (final)
    .\start.ps1 -BuildFrontend         Construye solo frontend (Docker)
    .\start.ps1 -BuildBackend          Construye solo backend (Docker)
    .\start.ps1 -Kill                  Para contenedores Docker y procesos locales
    .\start.ps1 -Help                  Muestra esta ayuda

REQUISITOS (Docker):
    - Docker Desktop (https://docs.docker.com/desktop/)
    - Docker levanta automaticamente pip install + flutter pub get

REQUISITOS (local, si no hay Docker):
    - Python 3.12+ con pip
    - Flutter SDK en PATH
    - Los scripts crean .venv y ejecutan flutter pub get automaticamente
"@
    return
}

# ---- Detect browser ----
function Get-Browser {
    $bravePaths = @(
        "$env:ProgramFiles\BraveSoftware\Brave-Browser-Beta\Application\brave.exe",
        "$env:ProgramFiles\BraveSoftware\Brave-Browser-Stable\Application\brave.exe"
    )
    foreach ($bp in $bravePaths) { if (Test-Path $bp) { return $bp } }
    $chromePaths = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    )
    foreach ($cp in $chromePaths) { if (Test-Path $cp) { return $cp } }
    return $null
}

$browser = Get-Browser
if ($browser) {
    $env:CHROME_EXECUTABLE = $browser
    Write-Host "[DETECTADO] CHROME_EXECUTABLE = $browser" -ForegroundColor Green
}

# ============================================================
# DOCKER MODE
# ============================================================
$dockerAvailable = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)

if ($Web) {
    # --web siempre usa modo local (como start.bat)
} elseif ($dockerAvailable) {
    Write-Host "[DOCKER] Usando Docker..." -ForegroundColor Cyan
    Set-Location $root

    if (-not $env:SECRET_KEY) { $env:SECRET_KEY = "dev-secret-change-in-production" }

    # Check host ports that Docker will bind
    if (-not ($BuildAll -or $Build -or $BuildFrontend -or $BuildBackend -or $Migrate -or $TestBackend -or $TestFrontend)) {
        $dcBackend = Find-FreePort 8000 "Backend (Docker)"
        $dcFrontend = Find-FreePort 3000 "Frontend (Docker)"
        if ($MariaDB -or $TestMigration) { $dcMaria = Find-FreePort 3306 "MariaDB (Docker)"; $env:PORT_DB = "$dcMaria" }
        if ($Final) { $dcFeProd = Find-FreePort 80 "Frontend prod (Docker)" }
        $env:PORT_BACKEND = "$dcBackend"
        $env:PORT_FRONTEND = "$dcFrontend"
        Write-Host "[DOCKER] Usando puertos: BACKEND=$dcBackend FRONTEND=$dcFrontend" -ForegroundColor Cyan
        if ($Final) { $env:PORT_FRONTEND_PROD = "$dcFeProd"; Write-Host "[DOCKER]   Frontend prod: $dcFeProd" -ForegroundColor Cyan }
    }

    if ($BuildAll) {
        Write-Host "[BUILD-ALL] Construyendo paquetes distribubles..." -ForegroundColor Cyan
        & "$root\tools\build-all.ps1"
        if ($LASTEXITCODE -eq 0) { Write-Host "[BUILD-ALL] Listo. Los paquetes estan en $root\builds\" -ForegroundColor Green }
        return
    }
    if ($Build) {
        Write-Host "[BUILD] Construyendo imagenes Docker..." -ForegroundColor Cyan
        docker compose build
        if ($LASTEXITCODE -eq 0) { Write-Host "[BUILD] Listo." -ForegroundColor Green }
        return
    }
    if ($BuildFrontend) {
        docker compose build frontend
        return
    }
    if ($BuildBackend) {
        docker compose build backend
        return
    }
    if ($Migrate) {
        Write-Host "[MIGRATE] Ejecutando migraciones..." -ForegroundColor Magenta
        docker compose run --rm backend alembic upgrade head
        return
    }

    if ($TestMigration) {
        Write-Host "[TEST-MIGRATION] Iniciando MariaDB..." -ForegroundColor Cyan
        docker compose --profile db up -d db

        Write-Host "[TEST-MIGRATION] Esperando a que MariaDB este lista..." -ForegroundColor Yellow
        $maxRetries = 20
        for ($i = 0; $i -lt $maxRetries; $i++) {
            Start-Sleep -Seconds 3
            $result = docker compose exec -T db mariadb -u root -prootpassword -e "SELECT 1" 2>&1
            if ($LASTEXITCODE -eq 0) { break }
            if ($i -eq $maxRetries - 1) {
                Write-Host "[TEST-MIGRATION] ERROR: MariaDB no respondio tras 60s" -ForegroundColor Red
                docker compose down
                exit 1
            }
        }

        $dbUrl = "mariadb+pymysql://clakettes_user:clakettes_password@db:3306/clakettes_db"

        Write-Host "[TEST-MIGRATION] MariaDB lista. Ejecutando migraciones..." -ForegroundColor Cyan
        docker compose run --rm -e "DATABASE_URL=$dbUrl" backend alembic upgrade head
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[TEST-MIGRATION] ERROR en migraciones" -ForegroundColor Red
            docker compose down
            exit 1
        }

        Write-Host "[TEST-MIGRATION] Validando tablas creadas..." -ForegroundColor Cyan
        docker compose run --rm -e "DATABASE_URL=$dbUrl" backend python -c "import os; from sqlalchemy import create_engine, text; e=create_engine(os.environ['DATABASE_URL']); c=e.connect(); r=c.execute(text('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()')); n=r.scalar(); print(f'TABLAS CREADAS: {n}'); c.close()"

        Write-Host "[TEST-MIGRATION] Migracion completada correctamente." -ForegroundColor Green
        Write-Host "[TEST-MIGRATION] Limpiando contenedores..." -ForegroundColor Yellow
        docker compose down
        return
    }
    if ($TestBackend) {
        Write-Host "[TEST:BACKEND] Ejecutando pytest en Docker..." -ForegroundColor Cyan
        docker compose run --rm backend python -m pytest tests/ -x -q --tb=short
        if ($LASTEXITCODE -eq 0) { Write-Host "[TEST:BACKEND] Todos los tests pasaron" -ForegroundColor Green }
        else { Write-Host "[TEST:BACKEND] Fallaron algunos tests" -ForegroundColor Red }
        return
    }
    if ($TestFrontend) {
        Write-Host "[TEST:FRONTEND] Ejecutando flutter test en Docker..." -ForegroundColor Cyan
        docker compose run --rm frontend flutter test
        if ($LASTEXITCODE -eq 0) { Write-Host "[TEST:FRONTEND] Todos los tests pasaron" -ForegroundColor Green }
        else { Write-Host "[TEST:FRONTEND] Fallaron algunos tests" -ForegroundColor Red }
        return
    }
    if ($Final) {
        $fpBe = $env:PORT_BACKEND
        $fpFe = $env:PORT_FRONTEND_PROD
        if (-not $fpBe) { $fpBe = "8000" }
        if (-not $fpFe) { $fpFe = "80" }
        Write-Host "[DOCKER] Iniciando en modo produccion..." -ForegroundColor Cyan
        docker compose --profile prod up -d
        Write-Host "[DOCKER] Backend: http://localhost:$fpBe  |  Frontend: http://localhost:$fpFe" -ForegroundColor Green
        return
    }

    # Dev mode
    if (-not (Test-ContainerPubCache (Join-Path $root "frontend"))) {
        Clear-FlutterGenerated (Join-Path $root "frontend")
    }
    if (-not $env:PORT_BACKEND) { $env:PORT_BACKEND = "8000" }
    if (-not $env:PORT_FRONTEND) { $env:PORT_FRONTEND = "3000" }
    Write-Host "[DOCKER] Iniciando servicios de desarrollo en http://localhost:$($env:PORT_BACKEND) y http://localhost:$($env:PORT_FRONTEND) ..." -ForegroundColor Cyan
    if ($NoBackend) {
        docker compose up frontend
    } elseif ($NoFrontend) {
        docker compose up backend
    } elseif ($MariaDB) {
        docker compose --profile db up
    } else {
        docker compose up
    }
    return
}

# ============================================================
# LOCAL FALLBACK
# ============================================================
if (-not $Web) {
    Write-Host "`n[DOCKER] Docker no disponible — usando entorno local.`n" -ForegroundColor Yellow
}

function Show-SetupHelp {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ERROR: Docker no disponible" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "`nLos comandos -Build, -BuildAll, -BuildFrontend y -BuildBackend"
    Write-Host "requieren Docker para funcionar.`n"
    Write-Host "Para configurar el entorno de desarrollo:`n"
    Write-Host "  Opcion 1 — Instalar Docker Desktop:"
    Write-Host "    https://docs.docker.com/desktop/`n"
    Write-Host "  Opcion 2 — Entorno local (sin Docker):"
    Write-Host "    - Python 3.12+ con pip"
    Write-Host "    - Flutter SDK en PATH"
    Write-Host "    - Ejecuta el script sin flags para que configure .venv y flutter pub get`n"
    Write-Host "  Ejecuta 'start.ps1 -Help' para mas detalles.`n"
}

    if ($BuildAll -or $Build -or $BuildFrontend -or $BuildBackend -or $TestMigration) { Show-SetupHelp; exit 1 }

$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"

# Flutter en PATH
$flutterPaths = @("C:\tools\flutter\bin")
foreach ($fp in $flutterPaths) {
    if ((Test-Path "$fp\flutter.bat") -and ($env:Path -notlike "*$fp*")) { $env:Path += ";$fp" }
}

# ── Local environment setup ──
$script:BackendPython = "python"

function Test-BackendVenv {
    param([string]$BackendDir)
    $venvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
    $cfg = Join-Path $BackendDir ".venv\pyvenv.cfg"
    if (-not (Test-Path $venvPython)) { return $false }
    if (-not (Test-Path $cfg)) { return $false }
    $homeLine = Select-String -Path $cfg -Pattern '^\s*home\s*=\s*(.+?)\s*$' | Select-Object -First 1
    if ($homeLine -and -not (Test-Path $homeLine.Matches[0].Groups[1].Value)) { return $false }
    try {
        & $venvPython --version 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { return $false }
    } catch { return $false }
    return $true
}

function Test-FlutterPubCache {
    param([string]$FrontendDir)
    $cfg = Join-Path $FrontendDir ".dart_tool\package_config.json"
    if (-not (Test-Path $cfg)) { return $false }
    try {
        $json = Get-Content $cfg -Raw | ConvertFrom-Json
        if (-not $json.packages) { return $false }
        $checked = 0
        foreach ($p in $json.packages) {
            $u = "$($p.rootUri)"
            if ($u -match '^file:///') {
                $local = [System.Uri]::UnescapeDataString($u.Substring(8)) -replace '/', '\'
                if (-not (Test-Path $local)) { return $false }
                $checked++
                if ($checked -ge 8) { break }
            } elseif ($u -match '^file:') {
                $rel = ($u.Substring(5) -replace '/', '\')
                if (-not (Test-Path (Join-Path (Split-Path $cfg -Parent) $rel))) { return $false }
            }
        }
        if ($checked -eq 0) { return $false }
    } catch { return $false }
    return $true
}

function Test-ContainerPubCache {
    param([string]$FrontendDir)
    $cfg = Join-Path $FrontendDir ".dart_tool\package_config.json"
    if (-not (Test-Path $cfg)) { return $true }
    foreach ($m in [regex]::Matches((Get-Content $cfg -Raw), '"rootUri":\s*"([^"]+)"')) {
        $u = $m.Groups[1].Value
        if ($u -match '^file:///') {
            if ($u.Substring(8) -notmatch '^(app|root|tmp)/') { return $false }
        } elseif ($u -match '^[a-zA-Z][a-zA-Z0-9+.-]*:') {
            return $false
        }
    }
    return $true
}

function Clear-FlutterGenerated {
    param([string]$FrontendDir)
    Write-Host "[ENV] Caché de Flutter de otro entorno, regenerando..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force (Join-Path $FrontendDir ".dart_tool") -ErrorAction SilentlyContinue
    Remove-Item -Force (Join-Path $FrontendDir ".flutter-plugins") -ErrorAction SilentlyContinue
    Remove-Item -Force (Join-Path $FrontendDir ".flutter-plugins-dependencies") -ErrorAction SilentlyContinue
}

function Invoke-LocalSetup {
    $envFile = Join-Path $backendDir ".env"
    $envExample = Join-Path $backendDir ".env.example"
    if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
        Write-Host "[ENV] Creando .env desde .env.example..." -ForegroundColor Yellow
        Copy-Item $envExample $envFile
    }

    $reqFile = Join-Path $backendDir "requirements.txt"
    $venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"

    if (Test-Path $reqFile) {
        if (-not (Test-BackendVenv $backendDir)) {
            $oldVenv = Join-Path $backendDir ".venv"
            if (Test-Path $oldVenv) {
                Write-Host "[ENV] Entorno virtual obsoleto (de otro equipo), recreando..." -ForegroundColor Yellow
                Remove-Item -Recurse -Force $oldVenv
            } else {
                Write-Host "[ENV] Creando entorno virtual para backend..." -ForegroundColor Yellow
            }
            Push-Location $backendDir
            python -m venv .venv
            if ($LASTEXITCODE -ne 0) { Write-Host "[ENV] ERROR: No se pudo crear .venv" -ForegroundColor Red; Pop-Location; exit 1 }
            Pop-Location
        }
        if (Test-Path $venvPython) {
            Write-Host "[ENV] Instalando/actualizando dependencias del backend..." -ForegroundColor Yellow
            $pip = Join-Path $backendDir ".venv\Scripts\pip"
            & $pip install -r $reqFile -q 2>&1 | Out-Null
            $devReq = Join-Path $backendDir "requirements-dev.txt"
            if (Test-Path $devReq) { & $pip install -r $devReq -q 2>&1 | Out-Null }
            $script:BackendPython = $venvPython
        }
    }

    $pubspec = Join-Path $frontendDir "pubspec.yaml"
    if ((Test-Path $pubspec) -and -not (Test-FlutterPubCache $frontendDir)) {
        if (Get-Command flutter -ErrorAction SilentlyContinue) {
            Write-Host "[ENV] Caché de Flutter obsoleta (de otro equipo), regenerando..." -ForegroundColor Yellow
            Push-Location $frontendDir
            flutter pub get 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[ENV] Reintentando sin red (offline)..." -ForegroundColor Yellow
                flutter pub get --offline 2>&1 | Out-Null
            }
            Pop-Location
            if (-not (Test-FlutterPubCache $frontendDir)) { Write-Host "[ENV] WARNING: No se pudo regenerar la caché de Flutter" -ForegroundColor Yellow }
        } else {
            Write-Host "[ENV] WARNING: Flutter no encontrado. Instalalo para desarrollo frontend." -ForegroundColor Yellow
        }
    }

    Write-Host "[ENV] Entorno listo." -ForegroundColor Green
}

Invoke-LocalSetup

New-PortMapping

$dbUrl = ""
if ($MariaDB) {
    $dbUrl = "mariadb+pymysql://clakettes_user:clakettes_password@localhost:$MARIADB_PORT/clakettes_db"
    $env:DATABASE_URL = $dbUrl
    Write-Host "[MARIADB] Usando MariaDB: $dbUrl" -ForegroundColor Cyan
}

if ($Migrate) {
    Write-Host "[MIGRATE] Ejecutando migraciones de base de datos..." -ForegroundColor Magenta
    Push-Location $backendDir
    & $script:BackendPython -m alembic upgrade head 2>&1
    Pop-Location
}

if ($TestBackend) {
    if (-not $PSBoundParameters.ContainsKey('NoBackend')) { $NoBackend = $true }
    Write-Host "[TEST:BACKEND] Ejecutando pytest..." -ForegroundColor Cyan
    Push-Location $backendDir
    & $script:BackendPython -m pytest tests/ -x -q --tb=short 2>&1
    $exitCode = $LASTEXITCODE
    Pop-Location
    if ($exitCode -ne 0) { Write-Host "[TEST:BACKEND] Fallaron algunos tests (exit code: $exitCode)" -ForegroundColor Red }
    else { Write-Host "[TEST:BACKEND] Todos los tests pasaron" -ForegroundColor Green }
    return
}

if ($TestFrontend) {
    if (-not $PSBoundParameters.ContainsKey('NoFrontend')) { $NoFrontend = $true }
    Write-Host "[TEST:FRONTEND] Ejecutando flutter test..." -ForegroundColor Cyan
    Push-Location $frontendDir
    flutter test 2>&1
    $exitCode = $LASTEXITCODE
    Pop-Location
    if ($exitCode -ne 0) { Write-Host "[TEST:FRONTEND] Fallaron algunos tests (exit code: $exitCode)" -ForegroundColor Red }
    else { Write-Host "[TEST:FRONTEND] Todos los tests pasaron" -ForegroundColor Green }
    return
}

$jobs = @()

if (-not $NoBackend) {
    Write-Host "[BACKEND] Iniciando uvicorn en http://localhost:$BACKEND_PORT ..." -ForegroundColor Green
    $jobs += Start-Job -Name "backend" -ScriptBlock {
        param($dir, $dbUrl, $pythonPath, $port)
        if ($dbUrl) { $env:DATABASE_URL = $dbUrl }
        Set-Location $dir
        & $pythonPath -m uvicorn app.main:app --host 0.0.0.0 --port $port --reload
    } -ArgumentList $backendDir, $dbUrl, $script:BackendPython, $BACKEND_PORT
}

if (-not $NoFrontend) {
    $dartDefine = "--dart-define=BACKEND_URL=http://localhost:$BACKEND_PORT"
    if ($Final) {
        Write-Host "[FRONTEND] Build produccion..." -ForegroundColor Cyan
        $buildOk = $true
        try {
            $buildOutput = & flutter build web $dartDefine 2>&1
            if ($LASTEXITCODE -ne 0) { $buildOk = $false; Write-Host "[FRONTEND] ERROR en build: $buildOutput" -ForegroundColor Red }
        } catch { $buildOk = $false; Write-Host "[FRONTEND] ERROR: $_" -ForegroundColor Red }
        if ($buildOk) {
            Write-Host "[FRONTEND] Sirviendo build/web en http://localhost:$FRONTEND_PROD_PORT ..." -ForegroundColor Cyan
            $jobs += Start-Job -Name "frontend" -ScriptBlock {
                param($dir, $pythonPath, $port)
                Set-Location "$dir\build\web"
                & $pythonPath -m http.server $port --bind 0.0.0.0
            } -ArgumentList $frontendDir, $script:BackendPython, $FRONTEND_PROD_PORT
            Start-Sleep -Seconds 2
            if ($browser) { Start-Process -FilePath $browser -ArgumentList "http://localhost:$FRONTEND_PROD_PORT" }
        }
    } elseif ($Web) {
        Write-Host "[FRONTEND] Iniciando Flutter web en http://localhost:$FRONTEND_PORT con CHROME_EXECUTABLE ..." -ForegroundColor Cyan
        $jobs += Start-Job -Name "frontend" -ScriptBlock {
            param($dir, $dde, $port)
            Set-Location $dir
            flutter run -d chrome --web-port $port $dde
        } -ArgumentList $frontendDir, $dartDefine, $FRONTEND_PORT
    } else {
        Write-Host "[FRONTEND] Iniciando Flutter web-server en http://localhost:$FRONTEND_PORT ..." -ForegroundColor Cyan
        $jobs += Start-Job -Name "frontend" -ScriptBlock {
            param($dir, $dde, $port)
            Set-Location $dir
            flutter run -d web-server --web-port $port $dde
        } -ArgumentList $frontendDir, $dartDefine, $FRONTEND_PORT
        Start-Sleep -Seconds 15
        if ($browser) { Start-Process -FilePath $browser -ArgumentList "http://localhost:$FRONTEND_PORT" }
    }
}

if ($jobs.Count -eq 0) {
    Write-Host "No hay nada que iniciar." -ForegroundColor Yellow
    return
}

Write-Host "`nPresiona Ctrl+C para detener todo.`n" -ForegroundColor Magenta

try {
    while ($true) {
        $running = $jobs | Where-Object { $_.State -eq 'Running' }
        if ($running.Count -eq 0) { Write-Host "`nTodos los procesos han terminado." -ForegroundColor Yellow; break }
        foreach ($job in $running) {
            $msg = Receive-Job -Job $job -ErrorAction SilentlyContinue
            if ($msg) { Write-Host "[$($job.Name)] $msg" }
        }
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "`nDeteniendo procesos..." -ForegroundColor Red
    $jobs | Stop-Job -PassThru | Remove-Job
    Write-Host "Detenido." -ForegroundColor Green
}
