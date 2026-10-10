<#
.SYNOPSIS
  Builds Clakettes Flutter app for different platforms using Docker.

.EXAMPLE
  .\build.ps1 -Target web
  .\build.ps1 -Target linux-appimage
  .\build.ps1 -Target all -NoCache
  .\build.ps1 -Target dev -Detach
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [ValidateSet(
    'web', 'linux-x64', 'linux-appimage',
    'android', 'windows-x64', 'windows-installer',
    'test', 'analyze', 'dev', 'all'
  )]
  [string]$Target,

  [string]$OutputDir = (Join-Path -Path $PSScriptRoot -ChildPath '..\..\builds'),

  [switch]$NoCache,

  [switch]$Detach
)

$ErrorActionPreference = 'Stop'

function Write-Color {
  param([string]$Message, [string]$Color = 'White')
  Write-Host -Object $Message -ForegroundColor $Color
}

function Test-DockerAvailable {
  try {
    $null = docker info --format '{{.ServerVersion}}' 2>&1
    return $true
  }
  catch {
    return $false
  }
}

function Copy-BuildOutput {
  param(
    [string]$ImageName,
    [string]$ContainerPath,
    [string]$LocalPath
  )

  $containerId = docker create $ImageName 2>&1 | Out-String
  $containerId = $containerId.Trim()

  try {
    if (Test-Path $LocalPath) {
      Remove-Item -Path "$LocalPath\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    $null = New-Item -ItemType Directory -Path $LocalPath -Force -ErrorAction SilentlyContinue
    docker cp "${containerId}:${ContainerPath}." "$LocalPath" 2>&1 | Out-Null
    Write-Color -Message "  -> Output copied to: $LocalPath" -Color Green
  }
  finally {
    docker rm $containerId 2>&1 | Out-Null
  }
}

function Invoke-Build {
  param([string]$TargetName)

  $buildTargets   = @('web', 'linux-x64', 'linux-appimage', 'android')
  $ciTargets      = @('test', 'analyze')
  $windowsTargets = @('windows-x64', 'windows-installer')

  $profileFlag = if ($TargetName -in $buildTargets) { '--profile build' }
                 elseif ($TargetName -in $ciTargets) { '--profile ci' }
                 elseif ($TargetName -in $windowsTargets) { '--profile windows' }
                 else { '' }

  Write-Color -Message "`n==> Building target: $TargetName" -Color Cyan

  if ($NoCache) {
    Write-Color -Message "  -> NoCache: rebuilding image without cache" -Color Yellow
    $buildArgs = @('compose')
    if ($profileFlag) { $buildArgs += $profileFlag }
    $buildArgs += 'build', '--no-cache', $TargetName
    & docker $buildArgs 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Docker build --no-cache failed for target: $TargetName" }
  }

  $dockerArgs = @('compose')
  if ($profileFlag) { $dockerArgs += $profileFlag }
  $dockerArgs += 'up', $TargetName

  & docker $dockerArgs 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "Docker build failed for target: $TargetName"
  }
}

function Invoke-BuildAndCopy {
  param([string]$TargetName)

  $imageName = "clakettes-${TargetName}"

  Invoke-Build -TargetName $TargetName

  $outputMap = @{
    'web'             = @{ ContainerPath = '/app/build/web';                          LocalDir = 'frontend-web' }
    'linux-x64'       = @{ ContainerPath = '/app/build/linux/x64/release/bundle';     LocalDir = 'frontend-linux-x86_64' }
    'linux-appimage'  = @{ ContainerPath = '/app/build';                              LocalDir = 'frontend-linux-x86_64' }
    'android'         = @{ ContainerPath = '/app/build/app/outputs';                   LocalDir = 'frontend-android' }
    'windows-x64'         = @{ ContainerPath = 'C:\app\build\windows\runner\Release';     LocalDir = 'frontend-windows-x86_64' }
    'windows-installer'   = @{ ContainerPath = 'C:\app\build\installer';                     LocalDir = 'frontend-windows-x86_64' }
  }

  $info = $outputMap[$TargetName]
  $localPath = Join-Path -Path $OutputDir -ChildPath $info.LocalDir

  Copy-BuildOutput -ImageName $imageName -ContainerPath $info.ContainerPath -LocalPath $localPath
}

# ---- Main ----

Set-Location -LiteralPath $PSScriptRoot

Write-Color -Message "Clakettes Docker Build Script" -Color Magenta
Write-Color -Message "Target: $Target" -Color Yellow
if ($env:BACKEND_URL) {
  Write-Color -Message "  BACKEND_URL=$($env:BACKEND_URL)" -Color Yellow
}

if (-not (Test-DockerAvailable)) {
  throw 'Docker is not available or not running. Please start Docker and try again.'
}

  $BuildTargets = @('web', 'linux-x64', 'linux-appimage', 'android')
  $CiTargets    = @('test', 'analyze')
  $WindowsTargets = @('windows-x64', 'windows-installer')

try {
  switch ($Target) {
    'all' {
      foreach ($t in $BuildTargets) {
        Invoke-BuildAndCopy -TargetName $t
      }
      foreach ($t in $WindowsTargets) {
        Invoke-BuildAndCopy -TargetName $t
      }
    }
    'web'             { Invoke-BuildAndCopy -TargetName 'web' }
    'linux-x64'       { Invoke-BuildAndCopy -TargetName 'linux-x64' }
    'linux-appimage' { Invoke-BuildAndCopy -TargetName 'linux-appimage' }
    'android'         { Invoke-BuildAndCopy -TargetName 'android' }
    'windows-x64'         { Invoke-BuildAndCopy -TargetName 'windows-x64' }
    'windows-installer'   { Invoke-BuildAndCopy -TargetName 'windows-installer' }
    'test'            { Invoke-Build -TargetName 'test' }
    'analyze'         { Invoke-Build -TargetName 'analyze' }
    'dev' {
      Write-Color -Message "`n==> Building target: dev" -Color Cyan
      $detachFlag = if ($Detach) { '-d' } else { '' }
      $dockerArgs = @('compose', '--profile', 'dev', 'up', '--build')
      if ($detachFlag) { $dockerArgs += $detachFlag }
      $dockerArgs += 'dev'
      & docker $dockerArgs 2>&1
      if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed for target: dev"
      }
    }
  }

  Write-Color -Message "`nBuild completed successfully!" -Color Green
}
catch {
  Write-Color -Message "`nBuild failed: $_" -Color Red
  exit 1
}
