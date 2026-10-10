# =============================================================================
# Stage 1: venv-linux — Build a portable virtualenv for Linux
# =============================================================================
FROM python:3.12-slim-bookworm AS venv-linux

RUN pip install --upgrade pip && \
    python -m venv /venv

COPY backend/requirements.txt /tmp/requirements.txt
RUN /venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    /venv/bin/pip install pyinstaller

# =============================================================================
# Stage 2: dist-linux — Create distributable tarball
# =============================================================================
FROM python:3.12-slim-bookworm AS dist-linux

COPY --from=venv-linux /venv /venv
COPY backend/ /app/backend/
COPY backend/run.sh /app/backend/run.sh
COPY backend/alembic.ini /app/backend/alembic.ini
COPY backend/alembic/ /app/backend/alembic/

WORKDIR /app

RUN echo '#!/bin/sh' > /app/run.sh && \
    echo 'set -e' >> /app/run.sh && \
    echo 'export PYTHONPATH=/app/backend:${PYTHONPATH:-}' >> /app/run.sh && \
    echo 'export DATABASE_URL="${DATABASE_URL:-sqlite:///./data/clakettes.db}"' >> /app/run.sh && \
    echo 'cd /app/backend' >> /app/run.sh && \
    echo '/venv/bin/alembic upgrade head' >> /app/run.sh && \
    echo 'exec /venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000' >> /app/run.sh && \
    chmod +x /app/run.sh

RUN mkdir -p /app/build && \
    tar czf /app/build/clakettes-backend-linux-x86_64.tar.gz \
        --transform 's,^,clakettes-backend/,' \
        /venv /app/backend /app/run.sh

# =============================================================================
# Stage 3: pyinstaller-linux — Create single-file PyInstaller binary (best-effort)
# =============================================================================
FROM python:3.12-slim-bookworm AS pyinstaller-linux

COPY --from=venv-linux /venv /venv
COPY backend/ /app/backend/

WORKDIR /app

RUN printf 'import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))\nos.environ.setdefault("DATABASE_URL", "sqlite:///./data/clakettes.db")\nfrom app.main import app\nimport uvicorn\nuvicorn.run(app, host="0.0.0.0", port=8000)\n' > /app/entry.py

RUN /venv/bin/pyinstaller --onefile \
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
