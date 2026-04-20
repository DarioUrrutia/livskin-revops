"""Indexer para Layer 2 del segundo cerebro (project_knowledge).

Lee todos los .md del repo (excepto notes/privado/ que es local/privado
por design), los chunkea en fragmentos ~700 chars con overlap, los embebe
via embeddings-service y los inserta en livskin_brain.project_knowledge.

Idempotente: en cada run, borra chunks previos de cada archivo y
re-inserta. Apto para cron semanal.

Run con:
  docker compose run --rm brain-tools index

Env vars requeridas (via env_file de docker-compose):
  DATABASE_URL  — postgresql://brain_user:PASS@postgres-data:5432/livskin_brain
  EMBED_URL     — default http://embeddings-service:8000/embed
"""

import glob
import os
import sys
import time
import requests
import psycopg2

REPO_DIR = "/repo"
EMBED_URL = os.environ.get("EMBED_URL", "http://embeddings-service:8000/embed")

# Construir DATABASE_URL desde env vars (evita problemas de interpolacion
# de docker-compose que leeria shell env en vez de env_file)
_password = os.environ.get("BRAIN_USER_PASSWORD")
_db_host = os.environ.get("BRAIN_DB_HOST", "postgres-data")
_db_name = os.environ.get("BRAIN_DB_NAME", "livskin_brain")
if not _password:
    raise RuntimeError(
        "BRAIN_USER_PASSWORD no seteado. Revisar env_file en docker-compose.yml "
        "(../postgres-data/.env)."
    )
DATABASE_URL = f"postgresql://brain_user:{_password}@{_db_host}:5432/{_db_name}"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 150
BATCH_EMBED_SIZE = 50

# Patrones a indexar (glob relativos a REPO_DIR)
PATTERNS = [
    "*.md",                           # README, CLAUDE.md en raiz
    "docs/**/*.md",
    "integrations/**/*.md",
    "agents/**/*.md",
    "analytics/**/*.md",
    "infra/**/*.md",                  # README de cada servicio
    "notes/compartido/**/*.md",
]

# Rutas a excluir (substring match)
SKIP_SUBSTRINGS = [
    ".git/",
    "node_modules/",
    "notes/privado/",                 # privacidad
    "docs/datos_livskin_extract/",    # ya en .gitignore
]


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Chunker simple char-based con overlap. Intenta cortar en
    boundaries naturales (parrafo > oracion > linea)."""
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []

    chunks: list[str] = []
    i = 0
    while i < len(text):
        end = min(i + size, len(text))
        # Intentar cortar en separador natural si no es el final
        if end < len(text):
            for sep in ["\n\n", ". ", "\n"]:
                idx = text.rfind(sep, i + size // 2, end)
                if idx != -1:
                    end = idx + len(sep)
                    break
        chunk = text[i:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        i = max(end - overlap, i + 1)
    return chunks


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Llama a embeddings-service con prefijo 'passage' (docs indexados)."""
    resp = requests.post(
        EMBED_URL,
        json={"text": texts, "type": "passage"},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    # embeddings-service retorna lista de listas cuando batch
    return data["embedding"]


def vec_literal(emb: list[float]) -> str:
    """Formato pgvector literal: '[0.1,0.2,...]'."""
    return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"


def find_markdown_files() -> list[str]:
    found: set[str] = set()
    for pattern in PATTERNS:
        for path in glob.glob(os.path.join(REPO_DIR, pattern), recursive=True):
            if any(skip in path for skip in SKIP_SUBSTRINGS):
                continue
            if os.path.isfile(path):
                found.add(path)
    return sorted(found)


def index_file(conn, abspath: str) -> int:
    """Borra chunks viejos del archivo + inserta los nuevos. Retorna # chunks."""
    relpath = os.path.relpath(abspath, REPO_DIR)
    with open(abspath, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = chunk_text(content)
    if not chunks:
        # Archivo vacio o solo whitespace — borra chunks previos y sale
        with conn.cursor() as c:
            c.execute("DELETE FROM project_knowledge WHERE source_path = %s", (relpath,))
        conn.commit()
        return 0

    # Embed en batches para eficiencia
    embeddings: list[list[float]] = []
    for i in range(0, len(chunks), BATCH_EMBED_SIZE):
        batch = chunks[i:i + BATCH_EMBED_SIZE]
        embeddings.extend(embed_batch(batch))

    # DELETE + INSERT en una transaccion
    with conn.cursor() as c:
        c.execute("DELETE FROM project_knowledge WHERE source_path = %s", (relpath,))
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            c.execute(
                """INSERT INTO project_knowledge
                   (source_path, chunk_index, chunk_text, chunk_embedding, metadata)
                   VALUES (%s, %s, %s, %s::vector, %s::jsonb)""",
                (relpath, idx, chunk, vec_literal(emb), "{}"),
            )
    conn.commit()
    return len(chunks)


def main() -> int:
    print(f"=== Indexer L2 — start {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"REPO_DIR: {REPO_DIR}")
    print(f"EMBED_URL: {EMBED_URL}")

    files = find_markdown_files()
    print(f"Archivos markdown encontrados: {len(files)}\n")

    if not files:
        print("WARN: ningun archivo encontrado. Verificar bind mount /repo.")
        return 1

    conn = psycopg2.connect(DATABASE_URL)
    total_chunks = 0
    total_files = 0
    started = time.time()

    try:
        for abspath in files:
            relpath = os.path.relpath(abspath, REPO_DIR)
            try:
                n = index_file(conn, abspath)
                total_chunks += n
                total_files += 1
                print(f"  [{n:4d} chunks] {relpath}")
            except Exception as e:
                print(f"  [ERROR] {relpath}: {e}", file=sys.stderr)
    finally:
        conn.close()

    elapsed = time.time() - started
    print(f"\n=== Indexer L2 — done")
    print(f"Files indexed: {total_files}/{len(files)}")
    print(f"Chunks total:  {total_chunks}")
    print(f"Tiempo:        {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
