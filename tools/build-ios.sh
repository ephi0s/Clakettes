#!/usr/bin/env bash
# Build Clakettes iOS IPA for distribution
# Requires: macOS with Xcode 15+, Apple Developer account, Flutter SDK

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILDS_DIR="$PROJECT_DIR/builds"

echo "=== Clakettes iOS Build Script ==="

if [[ "$(uname)" != "Darwin" ]]; then
  echo "ERROR: This script must be run on macOS."
  exit 1
fi

if ! command -v flutter &> /dev/null; then
  echo "ERROR: Flutter is not installed."
  exit 1
fi

cd "$PROJECT_DIR/frontend"

echo "==> Installing dependencies..."
flutter pub get

BACKEND_URL="${BACKEND_URL:-}"
DART_DEFINE=""
if [ -n "$BACKEND_URL" ]; then
  DART_DEFINE="--dart-define=BACKEND_URL=$BACKEND_URL"
fi

echo "==> Building iOS for distribution..."
flutter build ios --release $DART_DEFINE

IOS_BUILD_DIR="build/ios/iphoneos"
if [ -d "$IOS_BUILD_DIR/Runner.app" ]; then
  mkdir -p "$BUILDS_DIR/frontend/ios"
  
  mkdir -p /tmp/clakettes-ios/Payload
  cp -r "$IOS_BUILD_DIR/Runner.app" /tmp/clakettes-ios/Payload/
  cd /tmp/clakettes-ios
  zip -r "$BUILDS_DIR/frontend/ios/Clakettes.ipa" Payload/
  cd "$PROJECT_DIR"
  rm -rf /tmp/clakettes-ios
  
  echo "  -> IPA created at $BUILDS_DIR/frontend/ios/Clakettes.ipa"
fi

echo "=== iOS build completed! ==="
