# BASE #
FROM python:3.8-slim AS base

ARG VERSION=nover
LABEL product="HydroTwin API"
LABEL maintainer="Vicomtech <v3@vicomtech.org>"
LABEL version=$VERSION
ENV VERSION=$VERSION

RUN apt update && apt install -y curl gnupg2 libpq-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc -o microsoft.asc && apt-key add microsoft.asc && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt update && ACCEPT_EULA=Y apt install -y msodbcsql18 && apt remove -y curl gnupg2 && \
    rm /etc/apt/sources.list.d/mssql-release.list

# Set the working directory in the container
WORKDIR /usr/src/app

# BUILD STAGE #
FROM base AS builder

# Install GCC for compilation
RUN apt install -y -qq gcc

# Copy the dependencies directory to container
COPY ./requirements ./requirements

# Install dependencies
RUN mkdir ./install/ && \
    pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=./install/ -r requirements/prod.txt

# PRODUCTION STAGE #
FROM base

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/usr/lib/python3.8/site-packages/ \
    FLASK_APP=api.py \
    TZ=Europe/Madrid

# Expose a default API port
EXPOSE 5000

# Set a healthcheck
HEALTHCHECK \
    --interval=30s \
    --timeout=30s \
    --retries=5 \
    --start-period=10s \
    CMD python healthcheck.py

# Copy the content of the local API directory to the working directory
COPY . .
# Copy installed dependencies from build stage and set them accessible for Python
COPY --from=builder /usr/src/app/install /usr/

# command to run on container start
CMD gunicorn -c gunicorn.conf.py api:app
