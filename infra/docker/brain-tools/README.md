# brain-tools — Indexer + Query CLI del segundo cerebro

Dos herramientas empaquetadas en un container one-shot:

| Subcomando | Qué hace |
|---|---|
| `index` | Recorre el repo, chunkea todos los `.md`, los embebe, los inserta en `livskin_brain.project_knowledge` (Layer 2) |
| `query "<texto>"` | Embebe la query, busca top N chunks similares por coseno, imprime resultados |

## Uso desde VPS 3

Método largo:
```bash
cd /srv/livskin-revops/infra/docker/brain-tools
docker compose run --rm brain-tools index
docker compose run --rm brain-tools query "como configuramos CI CD"
docker compose run --rm brain-tools query "arquitectura VPS" 10
```

Método corto (scripts wrapper):
```bash
/srv/livskin-revops/infra/scripts/brain-index.sh
/srv/livskin-revops/infra/scripts/brain-query.sh "pregunta" [limit]
```

## Qué se indexa

Por default: todos los `.md` en:
- Raíz (`README.md`, `CLAUDE.md`)
- `docs/**`
- `integrations/**/README.md`
- `agents/**/README.md`
- `analytics/**/README.md`
- `infra/**/README.md`
- `notes/compartido/**`

**NO se indexa:**
- `notes/privado/*` (privacidad por design)
- `.git/`, `node_modules/`, carpetas temporales

Al agregar nuevos tipos de archivos o carpetas al repo, editar `PATTERNS` en `index.py`.

## Chunking

Estrategia: char-based con overlap.
- `CHUNK_SIZE = 700` caracteres
- `CHUNK_OVERLAP = 150` caracteres
- Corta preferentemente en `\n\n`, luego `. `, luego `\n`

Esto balancea: chunks pequeños (retrieval preciso) + suficiente contexto (significado semántico).

**Trade-offs:**
- No es token-aware (puede producir chunks de tamaño variable en tokens reales)
- Ignora headers markdown como boundaries — futuro upgrade
- Más sofisticado: usar `langchain.text_splitter.MarkdownHeaderTextSplitter` en v2

## Idempotencia

Cada run:
1. Para cada archivo, `DELETE FROM project_knowledge WHERE source_path = X`
2. `INSERT` los nuevos chunks

Por lo tanto, correr `index` muchas veces es seguro y refleja el estado actual del repo.

**Apto para cron semanal.** Pendiente: agregar al host crontab o n8n workflow.

## Cómo funciona `query`

```
1. Texto query → embeddings-service (type=query) → vector 384-dim
2. SELECT FROM project_knowledge ORDER BY chunk_embedding <=> query_vec LIMIT N
3. Imprime: similitud coseno + source_path + chunk_index + preview 240 chars
```

El operador `<=>` de pgvector retorna distancia coseno (0 = idéntico, 2 = opuesto). Similitud = `1 - distancia`.

## Conexión

- **DB:** conecta como `brain_user` (owner de `project_knowledge`)
- **Password:** leído de `../postgres-data/.env` (gitignored)
- **Embeddings:** llama a `http://embeddings-service:8000/embed` vía `data_net`

## Referencias

- [ADR-0001 § 7.1.2](../../../docs/decisiones/0001-segundo-cerebro-filosofia-y-alcance.md) — Schema de `project_knowledge` (Layer 2)
- [embeddings-service README](../embeddings-service/README.md) — API del embed service
- [pgvector docs](https://github.com/pgvector/pgvector) — operadores de similitud
