<#
.SYNOPSIS
  Master build orchestrator for Clakettes.
  Builds frontend and backend for all supported platforms.

.EXAMPLE
  .\build-all.ps1                          # Run all builds interactively
  .\build-all.ps1 -Frontend                # Frontend only (Docker builds)
  .\build-all.ps1 -Backend                 # Backend only
  .\build-all.ps1 -SkipMacOS -SkipiOS      # Skip macOS/iOS (no macOS host)
#>

[CmdletBinding()]
param(
  [switch]$Frontend,
  [switch]$Backend,
  [switch]$All = $true,
  [switch]$NoCache,
  [switch]$SkipMacOS,
  [switch]$SkipiOS
)

$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot

function Write-Color { param([string]$M, [string]$C = 'White'); Write-Host $M -ForegroundColor $C }

function Step { param([string]$Name)
  Write-Color "`n========================================" Cyan
  Write-Color "  $Name" Cyan
  Write-Color "========================================" Cyan
}

# Propagate BACKEND_URL to sub-scripts
if ($env:BACKEND_URL) {
  Write-Color "  BACKEND_URL=$($env:BACKEND_URL)" Yellow
}

# Default: run everything
if (-not $Frontend -and -not $Backend) { $Frontend = $Backend = $true }

# ---- FRONTEND ----
if ($Frontend) {
  Step "Building Frontend (Docker)"
  & "$ROOT\frontend\docker\build.ps1" -Target all -NoCache:$NoCache
  if (-not $?) { throw "Frontend build failed" }
  
  # macOS (if on macOS)  
  if (-not $SkipMacOS) {
    Step "Building Frontend for macOS"
    Write-Color "  -> Run tools/build-macos.sh on a macOS machine" Yellow
    }
    
    # iOS (if on macOS)
    if (-not $SkipiOS) {
      Step "Building Frontend for iOS"
      Write-Color "  -> Run tools/build-ios.sh on a macOS machine" Yellow
  }
}

# ---- BACKEND ----
if ($Backend) {
  Step "Building Backend (Docker)"
  & "$ROOT\backend\docker\build.ps1" -Target all -NoCache:$NoCache
  if (-not $?) { throw "Backend build failed" }

  # macOS backend (if on macOS)
  if (-not $SkipMacOS) {
    Step "Building Backend for macOS"
    Write-Color "  -> Run tools/build-backend-macos.sh on a macOS machine" Yellow
  }

  # Windows backend (if Docker is in Windows containers mode)
  Step "Building Backend for Windows (PyInstaller)"
  & "$ROOT\backend\docker\build.ps1" -Target windows-x64 -NoCache:$NoCache
  if (-not $?) { Write-Color "  -> Windows backend build skipped or failed (not on Windows containers mode?)" Yellow }
}

Write-Color "`n========================================" Green
Write-Color "  ALL BUILDS COMPLETED" Green
Write-Color "========================================" Green
Write-Color "Output directory: $ROOT\builds\" Green
