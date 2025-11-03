# BASE #
FROM python:3.10-slim AS base

LABEL product="HydroTwin Ingestor"
LABEL maintainer="Vicomtech <v3@vicomtech.org>"

# Set the working directory in the container
WORKDIR /usr/src/app

# BUILD STAGE #
FROM base AS builder

# Install build deps
RUN apt update -qq && apt install -y -qq gcc

# Copy & install requirements
COPY requirements.txt .
RUN mkdir ./install/ && \
    pip install --no-cache-dir --prefix=./install/ -r requirements.txt

# PRODUCTION STAGE #
FROM base

# Install cron & tzdata silently
RUN apt update -qq && apt install cron tzdata -y -qq && \
    rm -rf /etc/cron.*/* && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set envs
ENV PYTHONPATH=/usr/lib/python3.10/site-packages/ \
    PYTHONUNBUFFERED=True

# Copy scripts
COPY *.py .
# Add crontab file in the cron directory
COPY --chmod=0744 data_sync.cron /etc/cron.d/data_sync.cron
# Copy installed requirements from build stage and set them accessible for Python
COPY --from=builder /usr/src/app/install /usr/

# Run cron in foreground at container startup
# (printenv is used to pass env vars to crontab's own environment)
CMD printenv >> /etc/environment && crontab /etc/cron.d/* && cron -f -l 2
