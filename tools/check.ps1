param(
    [switch]$Quick,
    [switch]$Backend,
    [switch]$Frontend,
    [string]$TestFilter = ''
)

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$failed = 0

function Invoke-Step {
    param([string]$Name, [string]$WorkDir, [string]$Exe, [string[]]$Arguments)
    Write-Host "[CHECK] $Name" -ForegroundColor Cyan
    Push-Location $WorkDir
    try {
        & $Exe @Arguments
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[CHECK] FALLÓ: $Name (exit $LASTEXITCODE)" -ForegroundColor Red
            $script:failed = 1
        }
    }
    finally {
        Pop-Location
    }
}

$runBackend = -not $Frontend
$runFrontend = -not $Backend
$backendDir = Join-Path $root 'backend'
$frontendDir = Join-Path $root 'frontend'
$python = Join-Path $backendDir '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }

if ($runBackend) {
    Invoke-Step 'ruff check' $backendDir 'ruff' @('check', '.')
    Invoke-Step 'ruff format --check' $backendDir 'ruff' @('format', '--check', '.')
    if (-not $Quick) {
        $pytestArgs = @('-m', 'not interop', '-x', '-q', '--tb=short')
        if ($TestFilter) { $pytestArgs += @('-k', $TestFilter) }
        Invoke-Step 'pytest' $backendDir $python (@('-m', 'pytest', 'tests/') + $pytestArgs)
    }
}

if ($runFrontend) {
    Invoke-Step 'flutter analyze' $frontendDir 'flutter' @('analyze')
    if (-not $Quick) {
        $testArgs = @()
        if ($TestFilter) { $testArgs = @('--plain-name', $TestFilter) }
        Invoke-Step 'flutter test' $frontendDir 'flutter' (@('test') + $testArgs)
    }
}

if ($failed -eq 0) { Write-Host '[CHECK] Todo OK.' -ForegroundColor Green }
exit $failed
