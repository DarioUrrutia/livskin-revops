"""
Livskin Embeddings Service
==========================

Servicio HTTP interno que expone un endpoint para generar embeddings
usando el modelo `intfloat/multilingual-e5-small` (384 dims, multilingüe).

E5 models usan prefijos:
  - "query: <texto>"   para queries de búsqueda
  - "passage: <texto>" para documentos que se indexan

Uso desde otros containers en data_net:
  POST http://embeddings-service:8000/embed
  {"text": "hola, quiero info de botox", "type": "query"}

Referencias:
  - ADR-0001 § 6.2 (elección del modelo)
  - ADR-0006 (embeddings self-hosted)
"""

import os
import time
from typing import List, Union, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("MODEL_NAME", "intfloat/multilingual-e5-small")
MODEL_VERSION = os.getenv("MODEL_VERSION", "multilingual-e5-small-v1")
CACHE_DIR = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/app/model_cache")

app = FastAPI(
    title="Livskin Embeddings Service",
    description="Self-hosted embeddings para el segundo cerebro de Livskin.",
    version="1.0.0",
)

print(f"[startup] Cargando modelo {MODEL_NAME}...", flush=True)
_t0 = time.time()
model = SentenceTransformer(MODEL_NAME, cache_folder=CACHE_DIR)
EMBEDDING_DIM = model.get_sentence_embedding_dimension()
print(f"[startup] Modelo cargado en {time.time() - _t0:.1f}s. Dimensión: {EMBEDDING_DIM}", flush=True)


class EmbedRequest(BaseModel):
    text: Union[str, List[str]] = Field(
        ...,
        description="Texto único o lista de textos para embebir",
    )
    type: Literal["query", "passage"] = Field(
        default="passage",
        description='"query" (busqueda) o "passage" (documento a indexar). Afecta el prefijo E5.',
    )


class EmbedResponse(BaseModel):
    embedding: Union[List[float], List[List[float]]]
    model: str
    dim: int
    type: str
    count: int


@app.get("/")
def root():
    return {
        "service": "livskin-embeddings",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "dim": EMBEDDING_DIM,
        "endpoints": {
            "health": "GET /health",
            "embed": "POST /embed"
        },
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "dim": EMBEDDING_DIM,
    }


@app.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    """Genera embedding(s). Retorna vector único o lista según input."""
    is_batch = isinstance(req.text, list)
    raw = req.text if is_batch else [req.text]

    if not raw:
        raise HTTPException(status_code=400, detail="text vacío")
    if any(not isinstance(t, str) or not t.strip() for t in raw):
        raise HTTPException(status_code=400, detail="todos los textos deben ser strings no vacíos")
    if len(raw) > 100:
        raise HTTPException(status_code=400, detail="máximo 100 textos por request")

    prefix = f"{req.type}: "
    prefixed = [prefix + t for t in raw]
    vecs = model.encode(
        prefixed,
        normalize_embeddings=True,   # coseno funciona como producto punto
        convert_to_numpy=True,
    ).tolist()

    return EmbedResponse(
        embedding=vecs if is_batch else vecs[0],
        model=MODEL_VERSION,
        dim=EMBEDDING_DIM,
        type=req.type,
        count=len(raw),
    )
