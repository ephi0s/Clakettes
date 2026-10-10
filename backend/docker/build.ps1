<#
.SYNOPSIS
  Builds Clakettes backend distributable packages using Docker.

.EXAMPLE
  .\build.ps1 -Target pyinstaller
  .\build.ps1 -Target all
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [ValidateSet('pyinstaller', 'windows-x64', 'windows-x86', 'all')]
  [string]$Target,

  [string]$OutputDir = (Join-Path -Path $PSScriptRoot -ChildPath '..\..\builds'),

  [switch]$NoCache,

  [switch]$Detach
)

$ErrorActionPreference = 'Stop'

function Write-Color {
  param([string]$Message, [string]$Color = 'White')
  Write-Host $Message -ForegroundColor $Color
}

function Test-DockerAvailable {
  try { $null = docker info --format '{{.ServerVersion}}' 2>&1; return $true }
  catch { return $false }
}

function Test-WindowsContainers {
  try {
    $info = docker info --format '{{.OSType}}' 2>&1
    return $info.Trim() -eq 'windows'
  }
  catch { return $false }
}

function Copy-BuildOutput {
  param([string]$ImageName, [string]$ContainerPath, [string]$LocalPath)
  $id = (docker create $ImageName 2>&1).Trim()
  try {
    if (Test-Path $LocalPath) {
      Remove-Item -Path "$LocalPath\*" -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
    }
    New-Item -ItemType Directory -Path $LocalPath -Force -ErrorAction SilentlyContinue | Out-Null
    docker cp "${id}:${ContainerPath}." "$LocalPath" 2>&1 | Out-Null
    Write-Color "  -> Output copied to: $LocalPath" Green
  }
  finally { docker rm $id 2>&1 | Out-Null }
}

function Invoke-Build {
  param([string]$TargetName)
  Write-Color "`n==> Building backend target: $TargetName" Cyan
  $dockerArgs = @('build')
  if ($NoCache) { $dockerArgs += '--no-cache' }
  $windowsTargets = @('windows-x64', 'windows-x86')
  $dockerfile = if ($TargetName -in $windowsTargets) { 'backend/docker/windows.Dockerfile' } else { 'backend/docker/Dockerfile' }
  $dockerArgs += '--target', $TargetName, '-t', "clakettes-backend-$TargetName", '-f', $dockerfile, '.'
  & docker $dockerArgs 2>&1
  if ($LASTEXITCODE -ne 0) { throw "Docker build failed for target: $TargetName" }
}

function Invoke-BuildWindows {
  param([string]$TargetName)
  if (-not (Test-WindowsContainers)) {
    throw "Windows containers required for target: $TargetName. Switch Docker Desktop to Windows containers mode."
  }
  Invoke-Build -TargetName $TargetName
}

Set-Location (Resolve-Path "$PSScriptRoot\..\..")

Write-Color "Clakettes Backend Docker Build Script" Magenta
Write-Color "Target: $Target" Yellow

if (-not (Test-DockerAvailable)) { throw 'Docker is not available.' }

try {
  switch ($Target) {
    'all' {
      Invoke-Build -TargetName 'pyinstaller-linux'
      Copy-BuildOutput -ImageName 'clakettes-backend-pyinstaller-linux' -ContainerPath '/app/dist' -LocalPath (Join-Path $OutputDir 'backend-linux-x86_64')

      if (Test-WindowsContainers) {
        Invoke-Build -TargetName 'windows-x64'
        Copy-BuildOutput -ImageName 'clakettes-backend-windows-x64' -ContainerPath 'C:\app\dist' -LocalPath (Join-Path $OutputDir 'backend-windows-x86_64')
      } else {
        Write-Color "  -> Skipping windows-x64 (not on Windows containers mode)" Yellow
      }
    }
    'pyinstaller' {
      Invoke-Build -TargetName 'pyinstaller-linux'
      Copy-BuildOutput -ImageName 'clakettes-backend-pyinstaller-linux' -ContainerPath '/app/dist' -LocalPath (Join-Path $OutputDir 'backend-linux-x86_64')
    }
    'windows-x64' {
      Invoke-BuildWindows -TargetName 'windows-x64'
      Copy-BuildOutput -ImageName 'clakettes-backend-windows-x64' -ContainerPath 'C:\app\dist' -LocalPath (Join-Path $OutputDir 'backend-windows-x86_64')
    }
    'windows-x86' {
      Invoke-BuildWindows -TargetName 'windows-x86'
      Copy-BuildOutput -ImageName 'clakettes-backend-windows-x86' -ContainerPath 'C:\app\dist' -LocalPath (Join-Path $OutputDir 'backend-windows-x86')
    }
  }
  Write-Color "`nBackend build completed successfully!" Green
}
catch {
  Write-Color "`nBuild failed: $_" Red
  exit 1
}
