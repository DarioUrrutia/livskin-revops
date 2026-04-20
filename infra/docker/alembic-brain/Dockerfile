# Alembic runner para livskin_brain
# Imagen pequeña: python + alembic + psycopg2 + sqlalchemy.
# Se corre on-demand con `docker compose run --rm alembic-brain <comando>`
# (no como servicio permanente — profile "oneshot").

FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    alembic==1.14.0 \
    psycopg2-binary==2.9.10 \
    sqlalchemy==2.0.35

# alembic.ini y migrations/ se montan como volumes desde docker-compose.
# ENTRYPOINT a alembic + CMD default a --help.
ENTRYPOINT ["alembic"]
CMD ["--help"]
