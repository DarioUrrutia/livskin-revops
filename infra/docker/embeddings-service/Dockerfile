# Embeddings service para Livskin segundo cerebro
# Modelo: intfloat/multilingual-e5-small (384-dim, multilingual, español excelente)
# Se baja el modelo en build time -> primer run es rápido

FROM python:3.11-slim-bookworm

WORKDIR /app

# System deps: curl para healthcheck + build-essential si sentence-transformers necesita compilar
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-descargar modelo en build (bakeado en la imagen)
ENV HF_HOME=/app/model_cache \
    TRANSFORMERS_OFFLINE=0 \
    SENTENCE_TRANSFORMERS_HOME=/app/model_cache
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('intfloat/multilingual-e5-small', cache_folder='/app/model_cache')" \
    && echo "Modelo descargado en /app/model_cache"

# App
COPY app.py .

# Non-root user
RUN useradd --create-home --shell /bin/bash embed && chown -R embed:embed /app
USER embed

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
