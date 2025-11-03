# BUILD STAGE #
FROM node:12-alpine AS builder

ARG VERSION
ARG NO_CAS_AUTH

WORKDIR /app/
COPY package*.json ./
RUN npm install --force --no-optional

ENV NODE_ENV=production \
    VUE_APP_VERSION=$VERSION \
    VUE_APP_NO_CAS_AUTH=$NO_CAS_AUTH

COPY *.js *.json ./
COPY public/ public/
COPY src/ src/
RUN npm run build

# PRODUCTION STAGE #
FROM nginx:alpine

ARG VERSION=nover
LABEL product="HydroTwin Frontend"
LABEL maintainer="Vicomtech <v3@vicomtech.org>"
LABEL version=$VERSION

# Install Certbot
RUN apk add --no-cache certbot-nginx openssl

ENV DNS_RESOLVER=127.0.0.11 \
    SRVC_NAMESPACE="" \
    SSL_ENABLED=False

COPY --from=builder /app/dist/ /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/
COPY nginx/nginx.conf.template /etc/nginx/templates/
COPY nginx/nginx_ssl.conf.template /etc/nginx/templates/
COPY nginx/nginxconfig.io/ /etc/nginx/nginxconfig.io/
COPY nginx/certs/FortiClient_CA.crt /usr/local/share/ca-certificates/
COPY --chmod=0744 nginx/certbot.cron /etc/periodic/daily/certbot
COPY --chmod=0744 nginx/restart_nginx.sh nginx/run.sh /

RUN update-ca-certificates

EXPOSE 80 443

HEALTHCHECK \
    --interval=30s \
    --timeout=30s \
    --retries=5 \
    --start-period=5s \
    CMD curl -fkL --user-agent "HealthChecker" http://localhost/health || exit 1

CMD [ "/bin/sh", "-c", "/run.sh" ]
