# escape=`

# =============================================================================
# Stage 1: install-python — Windows Server Core + Python 3.12 + venv
# =============================================================================
FROM mcr.microsoft.com/windows/servercore:ltsc2022 AS install-python

LABEL stage="install-python"

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

ADD https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe C:\python-installer.exe
RUN Start-Process C:\python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; `
    Remove-Item C:\python-installer.exe -Force

RUN python -m venv C:\venv

COPY backend/requirements.txt C:\tmp\requirements.txt
RUN C:\venv\Scripts\pip install --no-cache-dir -r C:\tmp\requirements.txt
RUN C:\venv\Scripts\pip install pyinstaller

# =============================================================================
# Stage 2: windows-x64 — Single-file PyInstaller binary (x86_64)
# =============================================================================
FROM install-python AS windows-x64

LABEL stage="windows-x64"

COPY backend C:\app\backend

WORKDIR C:\app

RUN @"
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/clakettes.db")
from app.main import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
"@ | Out-File -FilePath C:\app\entry.py -Encoding ASCII

RUN C:\venv\Scripts\pyinstaller --onefile `
    --name clakettes-backend `
    --add-data "backend;backend" `
    --hidden-import=uvicorn `
    --hidden-import=uvicorn.logging `
    --hidden-import=uvicorn.loops `
    --hidden-import=uvicorn.loops.auto `
    --hidden-import=uvicorn.protocols `
    --hidden-import=uvicorn.protocols.http `
    --hidden-import=uvicorn.protocols.http.auto `
    --hidden-import=uvicorn.protocols.websockets `
    --hidden-import=uvicorn.protocols.websockets.auto `
    --hidden-import=sqlalchemy `
    --hidden-import=alembic `
    --collect-all app `
    entry.py

# =============================================================================
# Stage 3: windows-x86 — Single-file PyInstaller binary (32-bit, experimental)
# =============================================================================
FROM install-python AS windows-x86

LABEL stage="windows-x86"

# Reinstall Python 32-bit
ADD https://www.python.org/ftp/python/3.12.0/python-3.12.0.exe C:\python-installer.exe
RUN Start-Process C:\python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python312-32' -Wait; `
    Remove-Item C:\python-installer.exe -Force

RUN C:\Python312-32\python.exe -m venv C:\venv-32
COPY backend/requirements.txt C:\tmp\requirements.txt
RUN C:\venv-32\Scripts\pip install --no-cache-dir -r C:\tmp\requirements.txt
RUN C:\venv-32\Scripts\pip install pyinstaller

COPY backend C:\app\backend

WORKDIR C:\app

RUN @"
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/clakettes.db")
from app.main import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
"@ | Out-File -FilePath C:\app\entry.py -Encoding ASCII

RUN C:\venv-32\Scripts\pyinstaller --onefile `
    --name clakettes-backend `
    --add-data "backend;backend" `
    --hidden-import=uvicorn `
    --hidden-import=uvicorn.logging `
    --hidden-import=uvicorn.loops `
    --hidden-import=uvicorn.loops.auto `
    --hidden-import=uvicorn.protocols `
    --hidden-import=uvicorn.protocols.http `
    --hidden-import=uvicorn.protocols.http.auto `
    --hidden-import=uvicorn.protocols.websockets `
    --hidden-import=uvicorn.protocols.websockets.auto `
    --hidden-import=sqlalchemy `
    --hidden-import=alembic `
    --collect-all app `
    entry.py
