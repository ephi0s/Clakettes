#!/bin/sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUICK=0
RUN_BACKEND=1
RUN_FRONTEND=1
TEST_FILTER=""

for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=1 ;;
    --backend) RUN_FRONTEND=0 ;;
    --frontend) RUN_BACKEND=0 ;;
    --test-filter=*) TEST_FILTER="${arg#--test-filter=}" ;;
    --help|-h)
      echo "Uso: tools/check.sh [--quick] [--backend] [--frontend] [--test-filter=EXPR]"
      exit 0
      ;;
    *)
      echo "Flag desconocido: $arg"
      exit 1
      ;;
  esac
done

FAILED=0

run_step() {
  name="$1"
  dir="$2"
  shift 2
  echo "[CHECK] $name"
  if ! (cd "$dir" && "$@"); then
    echo "[CHECK] FALLÓ: $name"
    FAILED=1
  fi
}

if [ "$RUN_BACKEND" -eq 1 ]; then
  run_step 'ruff check' "$ROOT/backend" ruff check .
  run_step 'ruff format --check' "$ROOT/backend" ruff format --check .
  if [ "$QUICK" -eq 0 ]; then
    if [ -n "$TEST_FILTER" ]; then
      run_step 'pytest' "$ROOT/backend" python -m pytest tests/ -m 'not interop' -x -q --tb=short -k "$TEST_FILTER"
    else
      run_step 'pytest' "$ROOT/backend" python -m pytest tests/ -m 'not interop' -x -q --tb=short
    fi
  fi
fi

if [ "$RUN_FRONTEND" -eq 1 ]; then
  run_step 'flutter analyze' "$ROOT/frontend" flutter analyze
  if [ "$QUICK" -eq 0 ]; then
    if [ -n "$TEST_FILTER" ]; then
      run_step 'flutter test' "$ROOT/frontend" flutter test --plain-name "$TEST_FILTER"
    else
      run_step 'flutter test' "$ROOT/frontend" flutter test
    fi
  fi
fi

if [ "$FAILED" -eq 0 ]; then
  echo '[CHECK] Todo OK.'
else
  exit 1
fi
