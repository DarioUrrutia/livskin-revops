FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY sensor.py .

EXPOSE 9100

# Bind a 0.0.0.0:9100 — la seguridad la maneja UFW del host
# (whitelist DO VPC 10.114.0.0/20 para conexiones a 9100)
CMD ["gunicorn", "--bind", "0.0.0.0:9100", "--workers", "1", \
     "--access-logfile", "-", "--error-logfile", "-", "sensor:app"]
