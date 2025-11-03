FROM postgis/postgis:14-3.2-alpine

ARG VERSION=nover
LABEL product="HydroTwin RDB"
LABEL maintainer="Vicomtech <v3@vicomtech.org>"
LABEL version=$VERSION

COPY ./docker-entrypoint-initdb.d/ /docker-entrypoint-initdb.d/

ENV POSTGRES_USER=admin \
    POSTGRES_PASSWORD=4dm1n_p4ss \
    CHS_DB_NAME=hydrotwin \
    ODC_DB_NAME=opendatacube \
    CHS_DB_PASSWORD=chs-db_p4ss \
    ODC_DB_PASSWORD=odc-db_p4ss

EXPOSE 5432
VOLUME [ "/var/lib/postgresql/data" ]

HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --retries=5 \
    --start-period=10s \
    CMD pg_isready -U "$POSTGRES_USER"
