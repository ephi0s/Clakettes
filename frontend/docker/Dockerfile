# Build arg for compile-time backend URL
ARG BACKEND_URL

# Stage 1: flutter-sdk base
FROM ubuntu:24.04 AS flutter-sdk

LABEL stage="flutter-sdk"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    clang \
    cmake \
    ninja-build \
    pkg-config \
    libgtk-3-dev \
    liblzma-dev \
    libstdc++-12-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV FLUTTER_HOME=/opt/flutter
ENV PATH=$FLUTTER_HOME/bin:$FLUTTER_HOME/bin/cache/dart-sdk/bin:$PATH

RUN git clone --depth 1 --branch 3.24.0 https://github.com/flutter/flutter.git $FLUTTER_HOME \
    && flutter config --enable-web --enable-linux-desktop \
    && flutter precache

WORKDIR /app

# Stage 2: web
FROM flutter-sdk AS web

ARG BACKEND_URL

LABEL stage="web"

COPY . /app

RUN flutter pub get \
    && flutter build web --release ${BACKEND_URL:+--dart-define=BACKEND_URL=$BACKEND_URL}

# Stage 3: linux-x64
FROM flutter-sdk AS linux-x64

ARG BACKEND_URL

LABEL stage="linux-x64"

COPY . /app

RUN flutter pub get \
    && flutter build linux --release ${BACKEND_URL:+--dart-define=BACKEND_URL=$BACKEND_URL}

# Stage 4: linux-appimage
FROM linux-x64 AS linux-appimage

LABEL stage="linux-appimage"

RUN curl -fsSL -o /tmp/appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    && chmod +x /tmp/appimagetool \
    && cd /tmp \
    && ./appimagetool --appimage-extract > /dev/null 2>&1 \
    && mv /tmp/squashfs-root /opt/appimagetool \
    && ln -s /opt/appimagetool/AppRun /usr/local/bin/appimagetool

RUN mkdir -p /app/AppDir/usr/bin \
    && mkdir -p /app/AppDir/usr/share/applications \
    && mkdir -p /app/AppDir/usr/share/icons/hicolor/256x256/apps \
    && cp -r /app/build/linux/x64/release/bundle/* /app/AppDir/usr/bin/ \
    && printf '#!/bin/bash\nSELF="$(readlink -f "$0")"\nHERE="${SELF%/*}"\nexec "$HERE/usr/bin/clakettes" "$@"\n' > /app/AppDir/AppRun \
    && chmod +x /app/AppDir/AppRun

RUN printf '[Desktop Entry]\nType=Application\nName=Clakettes\nExec=clakettes\nComment=Film Festival Management\nCategories=Utility;\n' > /app/AppDir/usr/share/applications/clakettes.desktop

RUN printf '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><rect fill="#6200ee" width="256" height="256"/><text fill="white" font-size="120" x="50" y="170" font-family="sans-serif">C</text></svg>' > /app/AppDir/usr/share/icons/hicolor/256x256/apps/clakettes.svg

RUN appimagetool /app/AppDir /app/build/Clakettes-x86_64.AppImage

# Stage 5: linux-x86 (experimental)
# EXPERIMENTAL: Flutter does not officially support 32-bit Linux desktop
FROM i386/ubuntu:24.04 AS linux-x86

LABEL stage="linux-x86"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    clang \
    cmake \
    ninja-build \
    pkg-config \
    libgtk-3-dev \
    liblzma-dev \
    libstdc++-12-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV FLUTTER_HOME=/opt/flutter
ENV PATH=$FLUTTER_HOME/bin:$FLUTTER_HOME/bin/cache/dart-sdk/bin:$PATH

RUN git clone --depth 1 --branch 3.24.0 https://github.com/flutter/flutter.git $FLUTTER_HOME \
    && flutter config --enable-linux-desktop \
    && flutter precache

ARG BACKEND_URL

WORKDIR /app

COPY . /app

RUN flutter pub get \
    && flutter build linux --release ${BACKEND_URL:+--dart-define=BACKEND_URL=$BACKEND_URL}

# Stage 6: linux-x86-appimage (experimental)
FROM linux-x86 AS linux-x86-appimage

LABEL stage="linux-x86-appimage"

RUN curl -fsSL -o /tmp/appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    && chmod +x /tmp/appimagetool \
    && cd /tmp \
    && ./appimagetool --appimage-extract > /dev/null 2>&1 \
    && mv /tmp/squashfs-root /opt/appimagetool \
    && ln -s /opt/appimagetool/AppRun /usr/local/bin/appimagetool

RUN mkdir -p /app/AppDir/usr/bin \
    && mkdir -p /app/AppDir/usr/share/applications \
    && mkdir -p /app/AppDir/usr/share/icons/hicolor/256x256/apps \
    && cp -r /app/build/linux/x86/release/bundle/* /app/AppDir/usr/bin/ \
    && printf '#!/bin/bash\nSELF="$(readlink -f "$0")"\nHERE="${SELF%/*}"\nexec "$HERE/usr/bin/clakettes" "$@"\n' > /app/AppDir/AppRun \
    && chmod +x /app/AppDir/AppRun

RUN printf '[Desktop Entry]\nType=Application\nName=Clakettes\nExec=clakettes\nComment=Film Festival Management\nCategories=Utility;\n' > /app/AppDir/usr/share/applications/clakettes.desktop

RUN printf '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><rect fill="#6200ee" width="256" height="256"/><text fill="white" font-size="120" x="50" y="170" font-family="sans-serif">C</text></svg>' > /app/AppDir/usr/share/icons/hicolor/256x256/apps/clakettes.svg

RUN appimagetool /app/AppDir /app/build/Clakettes-i686.AppImage

# Stage 7: android
FROM flutter-sdk AS android

LABEL stage="android"

ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p $ANDROID_HOME/cmdline-tools \
    && curl -fsSL https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -o cmdline-tools.zip \
    && unzip cmdline-tools.zip -d $ANDROID_HOME/cmdline-tools \
    && rm cmdline-tools.zip \
    && mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest \
    && yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses \
    && $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager \
        "platform-tools" \
        "platforms;android-34" \
        "build-tools;34.0.0"

ARG BACKEND_URL

COPY . /app

RUN flutter pub get \
    && flutter build apk --release ${BACKEND_URL:+--dart-define=BACKEND_URL=$BACKEND_URL} \
    && flutter build appbundle --release ${BACKEND_URL:+--dart-define=BACKEND_URL=$BACKEND_URL}

# Stage 8: test
FROM flutter-sdk AS test

LABEL stage="test"

COPY . /app

RUN flutter pub get \
    && flutter test

# Stage 9: analyze
FROM flutter-sdk AS analyze

LABEL stage="analyze"

COPY . /app

RUN flutter pub get \
    && flutter analyze
