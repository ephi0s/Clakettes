#!/usr/bin/env bash
# Build Clakettes frontend for macOS and iOS
# Requires: macOS with Xcode 15+, Flutter SDK installed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILDS_DIR="$PROJECT_DIR/builds"

echo "=== Clakettes macOS/iOS Build Script ==="

# Check for macOS
if [[ "$(uname)" != "Darwin" ]]; then
  echo "ERROR: This script must be run on macOS."
  exit 1
fi

# Check for Flutter
if ! command -v flutter &> /dev/null; then
  echo "ERROR: Flutter is not installed. Install it first."
  exit 1
fi

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
  echo "ERROR: Xcode is not installed."
  exit 1
fi

cd "$PROJECT_DIR/frontend"

echo "==> Installing dependencies..."
flutter pub get

echo "==> Building macOS app..."
BACKEND_URL="${BACKEND_URL:-}"
DART_DEFINE=""
if [ -n "$BACKEND_URL" ]; then
  DART_DEFINE="--dart-define=BACKEND_URL=$BACKEND_URL"
fi
flutter build macos --release $DART_DEFINE
MACOS_APP="$PROJECT_DIR/frontend/build/macos/Build/Products/Release/clakettes.app"
if [ -d "$MACOS_APP" ]; then
  mkdir -p "$BUILDS_DIR/frontend/macos"
  
  # Create DMG
  if command -v create-dmg &> /dev/null; then
    create-dmg --volname "Clakettes" --window-pos 200 120 --window-size 600 450 \
      --icon-size 100 --icon "clakettes.app" 175 120 \
      --hide-extension "clakettes.app" --app-drop-link 425 120 \
      "$BUILDS_DIR/frontend/macos/Clakettes.dmg" "$MACOS_APP"
    echo "  -> DMG created at $BUILDS_DIR/frontend/macos/Clakettes.dmg"
  else
    # Fallback: zip the .app bundle
    ditto -c -k --keepParent "$MACOS_APP" "$BUILDS_DIR/frontend/macos/Clakettes-macos.zip"
    echo "  -> macOS app zipped at $BUILDS_DIR/frontend/macos/Clakettes-macos.zip"
    echo "  -> Install create-dmg for DMG: brew install create-dmg"
  fi
fi

echo "==> Building iOS app (no codesign)..."
flutter build ios --release --no-codesign $DART_DEFINE
IOS_BUILD_DIR="$PROJECT_DIR/frontend/build/ios/iphoneos"
if [ -d "$IOS_BUILD_DIR/Runner.app" ]; then
  mkdir -p "$BUILDS_DIR/frontend/ios"
  
  # Create IPA (without signing)
  mkdir -p /tmp/clakettes-ios/Payload
  cp -r "$IOS_BUILD_DIR/Runner.app" /tmp/clakettes-ios/Payload/
  cd /tmp/clakettes-ios
  zip -r "$BUILDS_DIR/frontend/ios/Clakettes.ipa" Payload/
  cd "$PROJECT_DIR"
  rm -rf /tmp/clakettes-ios
  
  echo "  -> IPA created at $BUILDS_DIR/frontend/ios/Clakettes.ipa"
  echo "  -> NOTE: This IPA is unsigned. Use a distribution certificate to sign."
fi

echo ""
echo "=== macOS/iOS build completed! ==="
echo "Outputs in: $BUILDS_DIR/frontend/macos/ and $BUILDS_DIR/frontend/ios/"
