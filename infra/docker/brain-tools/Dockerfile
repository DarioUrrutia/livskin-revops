# brain-tools — container con indexer + query CLI para el segundo cerebro.
# Se usa con docker compose run (one-shot), no como servicio permanente.

FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.10 \
    requests==2.32.3

COPY index.py query.py entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["help"]
