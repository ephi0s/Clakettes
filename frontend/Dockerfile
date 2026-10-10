ARG BACKEND_URL

FROM ubuntu:24.04 AS flutter-sdk

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git unzip xz-utils zip \
    libglu1-mesa clang cmake ninja-build \
    pkg-config libgtk-3-dev liblzma-dev libstdc++-12-dev \
    && rm -rf /var/lib/apt/lists/*

ENV FLUTTER_HOME=/opt/flutter
ENV PATH=$FLUTTER_HOME/bin:$FLUTTER_HOME/bin/cache/dart-sdk/bin:$PATH

RUN git clone --depth 1 --branch 3.24.0 https://github.com/flutter/flutter.git $FLUTTER_HOME \
    && flutter config --enable-web \
    && dart --version

WORKDIR /app

FROM flutter-sdk AS dev
ARG BACKEND_URL
ENV BACKEND_URL=${BACKEND_URL:-http://localhost:8000}
EXPOSE 3000
CMD flutter run -d web-server --web-port 3000 --dart-define=BACKEND_URL=$BACKEND_URL

FROM flutter-sdk AS build
ARG BACKEND_URL
COPY . .
RUN flutter pub get && flutter build web --release ${BACKEND_URL:+--dart-define=BACKEND_URL=$BACKEND_URL}

FROM nginx:alpine AS prod
COPY --from=build /app/build/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
