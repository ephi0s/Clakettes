# =============================================================================
# Stage 1: pyinstaller-linux — Create single-file PyInstaller binary (best-effort)
#
# Self-contained executable for Linux x86_64 (glibc). Needs no Python or
# Docker on the target machine.
# =============================================================================
FROM python:3.12-slim-bookworm AS pyinstaller-linux

RUN pip install --no-cache-dir --upgrade pip

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt pyinstaller

COPY backend/ /app/backend/

WORKDIR /app

RUN printf 'import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))\nos.environ.setdefault("DATABASE_URL", "sqlite:///./data/clakettes.db")\nfrom app.main import app\nimport uvicorn\nuvicorn.run(app, host="0.0.0.0", port=8000)\n' > /app/entry.py

RUN pyinstaller --onefile \
    --name clakettes-backend \
    --add-data "backend:backend" \
    --hidden-import=uvicorn \
    --hidden-import=uvicorn.logging \
    --hidden-import=uvicorn.loops \
    --hidden-import=uvicorn.loops.auto \
    --hidden-import=uvicorn.protocols \
    --hidden-import=uvicorn.protocols.http \
    --hidden-import=uvicorn.protocols.http.auto \
    --hidden-import=uvicorn.protocols.websockets \
    --hidden-import=uvicorn.protocols.websockets.auto \
    --hidden-import=sqlalchemy \
    --hidden-import=alembic \
    --collect-all app \
    entry.py && echo "PyInstaller stage completed"
