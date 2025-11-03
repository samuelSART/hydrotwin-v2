FROM opendatacube/ows:1.8.29

ARG VERSION=nover
LABEL product="HydroTwin OWS"
LABEL maintainer="Vicomtech <v3@vicomtech.org>"
LABEL version=$VERSION
ENV VERSION=$VERSION

# Cleanup
USER root
RUN rm -rf /code/.[a-zA-Z]* /code/*test* /code/*.y*ml /code/*.sh /code/Dockerfile
USER ows

ENV WMS_CONFIG_PATH=/code/datacube_ows/ows_cfg.py \
    PYTHONPATH=/code/ \
    FLASK_APP=/code/datacube_ows/ogc.py \
    FLASK_DEBUG=production

COPY *.py /code/datacube_ows/

EXPOSE 8000

# Set a healthcheck
HEALTHCHECK \
    --interval=30s \
    --timeout=30s \
    --retries=5 \
    --start-period=10s \
    CMD curl -fkL --user-agent "HealthChecker" http://localhost:8000/ping || exit 1

CMD ["bash", "-c", "datacube system init && datacube-ows-update --schema --role agdc_admin && datacube-ows-update --views && datacube-ows-update || true && exec gunicorn --config python:datacube_ows.gunicorn_config datacube_ows.wsgi"]
