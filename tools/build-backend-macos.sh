#!/usr/bin/env bash
# Build Clakettes backend single-file executable for macOS
# Requires: macOS with Python 3.12+
# Output: builds/backend-macos-x86_64/clakettes-backend-macos

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
BUILDS_DIR="$PROJECT_DIR/builds"

echo "=== Clakettes macOS Backend Build Script ==="

if [[ "$(uname)" != "Darwin" ]]; then
  echo "ERROR: This script must be run on macOS."
  exit 1
fi

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
  PYTHON_CMD="python"
else
  echo "ERROR: Python 3.12+ is not installed."
  exit 1
fi

echo "==> Creating virtual environment..."
cd "$BACKEND_DIR"
$PYTHON_CMD -m venv .venv-build-macos
source .venv-build-macos/bin/activate

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo "==> Creating entry point..."
cat > /tmp/backend-entry.py << 'PYEOF'
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/clakettes.db")
from app.main import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
PYEOF

echo "==> Building macOS single-file executable with PyInstaller..."
cd "$PROJECT_DIR"
.venv-build-macos/bin/pyinstaller --onefile \
    --name clakettes-backend-macos \
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
    /tmp/backend-entry.py

echo "==> Copying build output..."
mkdir -p "$BUILDS_DIR/backend-macos-x86_64"
cp dist/clakettes-backend-macos "$BUILDS_DIR/backend-macos-x86_64/"
echo "  -> Output: $BUILDS_DIR/backend-macos-x86_64/clakettes-backend-macos"

echo "==> Cleaning up..."
rm -rf .venv-build-macos dist build /tmp/backend-entry.py *.spec

echo ""
echo "=== macOS backend build completed! ==="
