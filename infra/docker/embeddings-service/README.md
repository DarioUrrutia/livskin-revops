# embeddings-service — Self-hosted embeddings

Servicio HTTP interno que genera embeddings usando el modelo `intfloat/multilingual-e5-small` (384 dimensiones, multilingüe con soporte excelente de español).

## Decisión

Ver [ADR-0006](../../../docs/decisiones/README.md) (línea 0006). Resumen:
- **Gratis** (cero costo recurrente vs $0.02/1M tokens de OpenAI)
- Multilingüe (español nativo)
- Latencia ~50-100ms en CPU (aceptable para WhatsApp UX)
- 384-dim → índices HNSW livianos
- Reversible si calidad decepciona (columna `embedding_model_version`)

## API

### `GET /health`

```json
{
  "status": "ok",
  "model": "intfloat/multilingual-e5-small",
  "model_version": "multilingual-e5-small-v1",
  "dim": 384
}
```

### `POST /embed`

**Request:**
```json
{
  "text": "hola, quiero info de botox",
  "type": "query"
}
```

O con batch:
```json
{
  "text": ["mensaje 1", "mensaje 2", "mensaje 3"],
  "type": "passage"
}
```

**Response** (texto único):
```json
{
  "embedding": [0.123, -0.456, ...],   // 384 floats
  "model": "multilingual-e5-small-v1",
  "dim": 384,
  "type": "query",
  "count": 1
}
```

### Prefijos `type`

Los modelos E5 requieren prefijo para calidad óptima:
- **`query`** — usar cuando el texto es una **consulta de búsqueda** del usuario
- **`passage`** — usar cuando el texto es un **documento que se indexa** (mensajes históricos, entries del catálogo, etc.)

Mezclar los dos correctamente mejora significativamente el recall.

## Uso desde otros containers (data_net)

```
# Desde el ERP Flask, n8n via VPC, scripts de populacion:
POST http://embeddings-service:8000/embed
```

## Build + deploy

```bash
cd /srv/livskin/embeddings-service
docker compose build           # ~3-5 min primera vez (baja modelo)
docker compose up -d
docker compose logs -f         # ver startup, espera "Modelo cargado"
curl http://localhost:8000/health    # solo funciona DESDE data_net
```

**NO expuesto al host** — para probar desde VPS 3 host, meterse a un container en data_net o usar `docker exec`.

## Smoke test

```bash
# Desde otro container en data_net (o dentro del mismo):
docker exec -it embeddings-service curl -s \
  -X POST http://localhost:8000/embed \
  -H 'Content-Type: application/json' \
  -d '{"text":"hola quiero info de botox","type":"query"}' | jq '.dim, .count'
# → 384, 1
```

## Recursos

- RAM esperada: ~200-400 MB (modelo + FastAPI + runtime)
- CPU: <5% idle, picos 30-60% durante embed
- Disco imagen: ~1.5 GB (modelo + PyTorch + deps)

## Versionado del modelo

Si en el futuro cambiamos a otro modelo:
1. Nuevo build con `MODEL_NAME` actualizado
2. Cambiar `MODEL_VERSION` (ej: `multilingual-e5-large-v1`)
3. Script batch en `infra/scripts/reembed.sh` (pendiente) re-embea tablas afectadas
4. Monitorear `embedding_runs` en `livskin_brain`

Ver ADR-0001 sección "Versionado de embeddings" para el runbook completo.
