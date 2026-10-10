# escape=`

# Build arg for compile-time backend URL
ARG BACKEND_URL

FROM mcr.microsoft.com/windows:ltsc2022 AS windows-sdk

LABEL stage="windows-sdk"

# Install Chocolatey
RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; `
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Visual Studio Build Tools with C++ workload (required for Flutter Windows)
RUN choco install -y visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.20348 --quiet --wait"

# Install Git
RUN choco install -y git

# Install Flutter SDK
RUN powershell -Command `
    $url = 'https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.24.0-stable.zip'; `
    $zip = 'C:\flutter.zip'; `
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor 3072; `
    Invoke-WebRequest -Uri $url -OutFile $zip; `
    Expand-Archive -Path $zip -DestinationPath C:\; `
    Remove-Item $zip

ENV FLUTTER_HOME=C:\flutter
ENV PATH=C:\flutter\bin;C:\flutter\bin\cache\dart-sdk\bin;${PATH}

RUN flutter config --enable-windows-desktop
RUN flutter precache

WORKDIR C:\app

# Windows x86_64 build
FROM windows-sdk AS windows-x64

ARG BACKEND_URL

LABEL stage="windows-x64"

COPY . C:\app

RUN flutter pub get
RUN if defined BACKEND_URL (flutter build windows --release --dart-define=BACKEND_URL=%BACKEND_URL%) else (flutter build windows --release)

# Output: C:\app\build\windows\runner\Release\

# =============================================================================
# Stage: windows-installer — Create InnoSetup installer for Windows x64
# =============================================================================
FROM windows-x64 AS windows-installer

LABEL stage="windows-installer"

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install InnoSetup
ADD https://jrsoftware.org/download.php/is.exe C:\innosetup-installer.exe
RUN Start-Process C:\innosetup-installer.exe -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR=C:\InnoSetup' -Wait; `
    Remove-Item C:\innosetup-installer.exe -Force

# Create InnoSetup script
RUN @"
#define MyAppName "Clakettes"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Clakettes"
#define MyAppURL "https://clakettes.app"
#define MyAppExeName "clakettes.exe"

[Setup]
AppId={{B8A4B5C6-D7E8-4F90-A1B2-C3D4E5F67890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=C:\app\build\installer
OutputBaseFilename=Clakettes-{#MyAppVersion}-windows-x64
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "C:\app\build\windows\runner\Release\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
"@ | Out-File -FilePath C:\app\setup.iss -Encoding ASCII

RUN & 'C:\InnoSetup\ISCC.exe' C:\app\setup.iss

# Output: C:\app\build\installer\Clakettes-*-windows-x64.exe
