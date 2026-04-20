"""Query CLI para el segundo cerebro — busca chunks similares a una pregunta.

Uso:
  docker compose run --rm brain-tools query "como se hace CI CD"
  docker compose run --rm brain-tools query "arquitectura VPS" 3

El segundo argumento opcional es el LIMIT (default 5).

Funcionamiento:
  1. Embebe la query con prefijo 'query:' (importante para modelos E5)
  2. Busca top N chunks por similitud coseno en project_knowledge
  3. Imprime: similitud + source_path + chunk_index + preview
"""

import os
import sys
import textwrap
import requests
import psycopg2

EMBED_URL = os.environ.get("EMBED_URL", "http://embeddings-service:8000/embed")

# Construir DATABASE_URL desde env vars (como el indexer)
_password = os.environ.get("BRAIN_USER_PASSWORD")
_db_host = os.environ.get("BRAIN_DB_HOST", "postgres-data")
_db_name = os.environ.get("BRAIN_DB_NAME", "livskin_brain")
if not _password:
    raise RuntimeError(
        "BRAIN_USER_PASSWORD no seteado. Revisar env_file en docker-compose.yml "
        "(../postgres-data/.env)."
    )
DATABASE_URL = f"postgresql://brain_user:{_password}@{_db_host}:5432/{_db_name}"
DEFAULT_LIMIT = 5


def embed_query(text: str) -> list[float]:
    resp = requests.post(
        EMBED_URL,
        json={"text": text, "type": "query"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def vec_literal(emb: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"


def search(query: str, limit: int) -> list[tuple]:
    emb = embed_query(query)
    vec = vec_literal(emb)

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as c:
            c.execute(
                """SELECT source_path, chunk_index, chunk_text,
                          1 - (chunk_embedding <=> %s::vector) AS similarity
                   FROM project_knowledge
                   ORDER BY chunk_embedding <=> %s::vector
                   LIMIT %s""",
                (vec, vec, limit),
            )
            return c.fetchall()
    finally:
        conn.close()


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: query.py '<texto>' [limit]", file=sys.stderr)
        return 2
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LIMIT

    rows = search(query, limit)
    if not rows:
        print(f"\nQuery: \"{query}\"\n\n(no results — project_knowledge vacio? corre 'brain-tools index' primero)")
        return 0

    print(f"\nQuery: \"{query}\"")
    print(f"Top {len(rows)} chunks por similitud coseno:\n")
    for i, (path, idx, text, sim) in enumerate(rows, start=1):
        preview = " ".join(text.split())  # normalize whitespace
        preview = textwrap.shorten(preview, width=240, placeholder="...")
        print(f"{i}. [sim={sim:.3f}]  {path}  (chunk #{idx})")
        print(f"   {preview}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
