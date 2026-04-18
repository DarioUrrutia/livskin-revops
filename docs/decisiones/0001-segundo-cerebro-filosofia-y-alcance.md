# ADR-0001 — Segundo cerebro: filosofía, alcance y arquitectura

**Estado:** ✅ Aprobada  
**Fecha:** 2026-04-18  
**Autor propuesta:** Claude Code  
**Decisor final:** Dario  
**Fase del roadmap:** Fase 0 (fundación)  
**Workstream:** Cerebro

---

## 1. Contexto

El blueprint original menciona **memoria vectorial con pgvector** como pieza de la arquitectura de clase mundial. En las discusiones iniciales se trató este componente como "fase 2, después de meses 4-6 con historial de conversaciones".

Durante la sesión estratégica del 2026-04-18 la decisora argumentó (correctamente) que esta visión "diferida" traicionaba el valor estratégico real del componente. El segundo cerebro **NO es una optimización tardía** — es el diferenciador competitivo del sistema Livskin versus cualquier otra clínica con CRM básico, y su valor como **pieza de portfolio** es central.

Esta ADR define:
- Qué ES y qué NO es el segundo cerebro
- Las 6 capas que lo componen y sus responsabilidades
- Las tecnologías elegidas y su justificación
- El cronograma de activación capa por capa (no "todo en fase 2")
- Cómo se expone a los consumidores (agentes, Claude Code, usuaria)

**Referencias:**
- Plan maestro § 7
- Blueprint § "Memoria vectorial y capas del ideal técnico"
- ADR-0002 (arquitectura de datos) — define dónde vive físicamente

---

## 2. Problema que resuelve

Un sistema RevOps sin memoria acumulada tiene los siguientes síntomas:

1. **Cada conversación arranca en frío.** El Conversation Agent saluda al paciente como si fuera la primera vez aunque sea la quinta.
2. **El equipo no aprende de sí mismo.** Si una frase específica convirtió 10 leads la semana pasada, no hay forma de que el agente la replique sistemáticamente.
3. **Los creativos ganadores no se heredan.** El hook de "desde S/.280 botox" ganó el mes pasado; el próximo mes el agente no lo sabe.
4. **Las decisiones se olvidan.** En tres meses nadie recuerda por qué se eligió last-touch attribution; se debate de nuevo.
5. **El conocimiento clínico vive solo en la doctora.** Si responde 100 veces "el botox no se aplica en embarazadas", debe seguir escribiéndolo a mano la vez 101.

El segundo cerebro **resuelve los 5** siendo la memoria **semántica + estructurada + versionada** del sistema completo.

---

## 3. Qué ES el segundo cerebro

### 3.1 Definición operativa

> Base de conocimiento del proyecto Livskin, estructurada en 6 capas, almacenada en Postgres + pgvector, consultable por búsqueda semántica y SQL, accesible a humanos (vía Metabase / Claude Code con MCP) y a los 4 agentes IA (vía tool-calling en n8n).

### 3.2 Las 6 capas

| # | Capa | Qué contiene | Volumen esperado |
|---|---|---|---|
| L1 | **Conocimiento clínico** | Catálogo tratamientos + productos + protocolos + brand voice + FAQs | ~100-300 registros, estable |
| L2 | **Conocimiento del proyecto** | Todos los documentos del repo (ADRs, sesiones, runbooks, master plan) indexados | ~50-500 chunks, crece lento |
| L3 | **Data operativa (vistas)** | Vistas SQL consolidadas sobre Vtiger + ERP + analytics | Deriva (no almacena) |
| L4 | **Conversaciones** | Cada mensaje WhatsApp entrante y saliente con embedding | ~50-500/día, crece rápido |
| L5 | **Memoria creativa** | Cada brief generado + creativo producido + performance del ad | ~12-50/semana |
| L6 | **Learnings** | Insights destilados por Growth Agent (patrones, hipótesis validadas) | ~5-20/semana |

### 3.3 Lo que el segundo cerebro HABILITA

**Para el Conversation Agent:**
- "Esta paciente ya me compró botox hace 5 meses — ofrezco refresh"
- "5 pacientes preguntaron lo mismo la semana pasada, la respuesta que mejor convirtió fue esta"
- "Detecto objeción por precio — el manual dice escalar con paquete por volumen"

**Para el Content Agent:**
- "Los últimos 4 creativos con hook de precio convirtieron 2.3× mejor que los de beneficio"
- "Los visuales con fondo azul performaron 40% mejor en clínica estética"
- "La frase 'resultados naturales' aparece en 80% de los ads ganadores"

**Para el Growth Agent:**
- "El CAC del canal orgánico bajó 30% desde que el Conversation Agent mejoró su prompt v1.2"
- "Las pacientes de FB ads con UTM content='ojeras' tienen LTV 2× mayor que las de 'botox'"
- "Hipótesis refutada: responder en <30s no convierte más que en <60s"

**Para Claude Code (yo):**
- "¿Por qué decidimos DO VPC en vez de Tailscale?"
- "¿Cuáles fueron las objeciones de la usuaria durante el diseño del ERP?"
- "¿Qué sabemos del comportamiento del pixel de Meta en este proyecto?"

**Para la usuaria:**
- Dashboards Metabase con métricas derivadas de las capas
- Queries ad-hoc contra el cerebro para análisis puntual

---

## 4. Qué NO es el segundo cerebro

Delimitar el alcance es tan importante como definirlo. Para evitar scope creep:

- ❌ **No es un reemplazo de Vtiger.** Vtiger sigue siendo el CRM master de identidad del cliente. El cerebro contiene información *sobre* conversaciones y *sobre* creativos, pero la tabla `clientes` vive en Vtiger.
- ❌ **No es un reemplazo del ERP.** Ventas, pagos y gastos viven en `livskin_erp`. El cerebro puede *consultar* pero no escribe transacciones.
- ❌ **No es un search engine generalista.** Está especializado al dominio de Livskin y sus conversaciones.
- ❌ **No reemplaza a Metabase.** Metabase visualiza métricas agregadas sobre OLAP. El cerebro habilita búsqueda semántica y contexto para agentes.
- ❌ **No es un chatbot externo.** Es infraestructura interna que los agentes consumen. Los usuarios finales no interactúan con el cerebro directamente.
- ❌ **No reemplaza memoria de Claude Code.** Mi memoria persistente en `~/.claude/.../memory/` es para mi comportamiento entre sesiones conmigo. El cerebro es de los agentes operativos y del proyecto.
- ❌ **No incluye imágenes clínicas** en el MVP. Computer vision clínica (fotos antes/después) es un dossier diferido (0105).

---

## 5. Opciones consideradas

### 5.1 Opción A — Todo en la misma instancia Postgres de analytics (rechazada)

Meter `livskin_brain` dentro del Postgres que ya corre en VPS 2 (junto a `analytics` y `metabase`).

**Pros:** un solo Postgres que mantener.

**Contras:** mezcla carga OLAP pesada (queries de Metabase sobre 500k filas) con carga vectorial (pgvector similarity search en 100k embeddings). Contención de recursos. Un query pesado de Metabase asfixia al Conversation Agent en pleno mensaje del paciente.

**Descartada.**

### 5.2 Opción B — Vector DB dedicado (Weaviate, Qdrant, Milvus) (rechazada)

Desplegar una DB vectorial especializada separada.

**Pros:** performance óptimo en búsqueda vectorial pura. Features avanzadas (hybrid search, filtering metadata).

**Contras:** un motor más que aprender, operar, respaldar. No podemos hacer JOIN con Postgres. Complejidad desproporcionada al volumen. Pgvector ya soporta >1M vectores con buen rendimiento.

**Descartada** por complejidad injustificada.

### 5.3 Opción C — Postgres + pgvector en VPS 3 dedicado (elegida)

Postgres 16 con extensión pgvector en el nuevo VPS 3, compartido con `livskin_erp` pero en DB separada `livskin_brain`.

**Pros:**
- Una sola instancia Postgres en VPS 3 (eficiente en RAM)
- Separación lógica por DB (`livskin_erp` transaccional, `livskin_brain` vectorial)
- JOIN entre DBs posible si se necesita (con postgres_fdw)
- pgvector es la solución más usada en producción para RAG medium-scale
- ACID garantizado (backups, consistencia)
- Self-hosted, gratis

**Contras:**
- Instancia compartida con ERP = si ERP hace DDOS accidental, afecta al cerebro
- Mitigación: pool de conexiones separado, query timeouts, resource limits

**Elegida.** Mejor balance simplicidad/capacidad/costo para el volumen proyectado.

### 5.4 Opción D — Tercera instancia Postgres separada (deferida)

Un container Postgres propio solo para el cerebro, separado del ERP.

**Pros:** aislamiento total.

**Contras:** +150 MB RAM. No justificable al volumen inicial. Reevaluar si el cerebro crece a >1M vectores.

**Registrada como escalamiento futuro.**

---

## 6. Tecnología elegida — decisiones componente por componente

### 6.1 Motor de DB

**Elección:** PostgreSQL 16 + extensión pgvector (última estable)

**Justificación:**
- Postgres 16 es la versión LTS actual, soporta JSONB + vectores + FTS nativamente
- pgvector soporta índices HNSW (mejor que IVFFlat para recall), acceso SQL nativo, filtros combinados
- Compatible con Alembic (migrations versionadas)
- Backups estándar de Postgres funcionan sin modificación

### 6.2 Modelo de embeddings

**Opciones evaluadas:**

| Modelo | Dim | Costo | Calidad español | RAM requerida | Latencia |
|---|---|---|---|---|---|
| OpenAI `text-embedding-3-small` | 1536 | $0.02/1M tokens | Excelente | 0 (API) | 100-300ms |
| OpenAI `text-embedding-3-large` | 3072 | $0.13/1M tokens | Excelente+ | 0 (API) | 100-300ms |
| Voyage `voyage-3` | 1024 | $0.06/1M tokens | Muy bueno | 0 (API) | 100-300ms |
| Cohere `embed-multilingual-v3` | 1024 | $0.10/1M tokens | Muy bueno | 0 (API) | 100-300ms |
| **Self-hosted `intfloat/multilingual-e5-small`** | **384** | **$0** | **Bueno** | **~200 MB** | **~50-100ms CPU** |
| Self-hosted `intfloat/multilingual-e5-large` | 1024 | $0 | Muy bueno | ~800 MB | ~200-400ms CPU |

**Elección:** `multilingual-e5-small` self-hosted.

**Justificación:**
- **Cero costo** recurrente (principio 8)
- Latencia aceptable para UX de WhatsApp (agente responde en 60s total, embedding es <10% del tiempo)
- Calidad suficiente para el volumen y dominio inicial (~100k conversaciones primer año)
- Multi-idioma nativo (español funciona perfecto)
- 384 dimensiones = índices más livianos
- Reversibilidad: si decepciona, cambiamos a OpenAI con re-embedding batch (columna `embedding_model_version` por fila)
- Footprint RAM razonable (~200 MB) en VPS 3 de 2 GB

**Container dedicado:** `embeddings-service` corriendo como microservicio HTTP interno:
```
POST http://embeddings-service:8000/embed
Body: {"text": "hola, quiero info de botox"}
Response: {"embedding": [0.1, 0.2, ...], "model": "multilingual-e5-small-v1"}
```

Permite escalar o reemplazar el modelo sin tocar los agentes.

### 6.3 Estrategia de chunking

Para L2 (conocimiento del proyecto — docs markdown) se chunkean en fragmentos de ~500-1000 tokens con overlap de ~100 tokens. Preserva contexto semántico.

Para L1 (conocimiento clínico) se chunkea por entidad (1 tratamiento = 1 o 2 chunks).

Para L4 (conversaciones) un mensaje = un chunk (no chunking). Típicamente <200 tokens.

### 6.4 Índices

Índice HNSW en cada columna `embedding`:
```sql
CREATE INDEX idx_conv_embedding ON conversations 
    USING hnsw (content_embedding vector_cosine_ops) 
    WITH (m = 16, ef_construction = 64);
```

Parámetros elegidos son el default recomendado para datasets <1M vectores.

### 6.5 Métrica de similitud

Cosine similarity (no L2). Razón: los embeddings e5 están normalizados, cosine es lo que entienden naturalmente.

### 6.6 Exposición como MCP server

Se desarrolla un MCP server propio (`livskin-brain-mcp`) que expone al segundo cerebro como herramienta a Claude Code. Se ejecuta localmente en la laptop de Dario cuando Claude Code está activo.

**Herramientas expuestas vía MCP:**
- `brain_search(query, layer, limit)` — búsqueda semántica en cualquier capa
- `brain_get_patient_history(patient_id)` — recupera historial específico
- `brain_get_clinic_knowledge(topic)` — info autoritativa sobre tratamientos
- `brain_get_project_decision(topic)` — busca ADRs relevantes al tema
- `brain_get_similar_conversations(message_embedding, limit)` — precedentes similares

**Autenticación:** conexión local via túnel SSH a VPS 3 con el token interno del cerebro. Nunca expuesto a internet público.

---

## 7. Schemas iniciales

### 7.1 Capa 1 — Conocimiento clínico

```sql
CREATE TABLE clinic_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,  -- 'tratamiento' | 'producto' | 'faq' | 'protocolo' | 'brand_voice'
    entity_key VARCHAR(100) NOT NULL,  -- 'botox', 'hialuronico_ojeras', etc.
    content TEXT NOT NULL,
    content_embedding vector(384),
    metadata JSONB DEFAULT '{}'::jsonb,
    language VARCHAR(5) DEFAULT 'es',
    embedding_model_version VARCHAR(50) DEFAULT 'multilingual-e5-small-v1',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ck_entity ON clinic_knowledge(entity_type, entity_key);
CREATE INDEX idx_ck_embedding ON clinic_knowledge 
    USING hnsw (content_embedding vector_cosine_ops);
```

### 7.2 Capa 2 — Conocimiento del proyecto

```sql
CREATE TABLE project_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_path VARCHAR(500) NOT NULL,  -- 'docs/decisiones/0001-...md'
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(384),
    metadata JSONB,  -- {title, tags, last_modified, git_sha}
    embedding_model_version VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pk_source ON project_knowledge(source_path);
CREATE INDEX idx_pk_embedding ON project_knowledge 
    USING hnsw (chunk_embedding vector_cosine_ops);
```

### 7.3 Capa 4 — Conversaciones

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(100),  -- referencia a Vtiger
    session_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL,  -- 'whatsapp' | 'web' | 'walkin'
    direction VARCHAR(10) NOT NULL,  -- 'inbound' | 'outbound'
    role VARCHAR(20) NOT NULL,  -- 'patient' | 'agent' | 'doctor' | 'system'
    content TEXT NOT NULL,
    content_embedding vector(384),
    message_metadata JSONB,  -- {agent_version, tool_calls, tokens_used, cost_usd}
    agent_prompt_version VARCHAR(20),
    escalated BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    embedding_model_version VARCHAR(50)
);

CREATE INDEX idx_conv_patient ON conversations(patient_id, created_at DESC);
CREATE INDEX idx_conv_session ON conversations(session_id, created_at);
CREATE INDEX idx_conv_embedding ON conversations 
    USING hnsw (content_embedding vector_cosine_ops);
```

### 7.4 Capa 5 — Memoria creativa

```sql
CREATE TABLE creative_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(100),
    creative_type VARCHAR(20),  -- 'image' | 'video' | 'carousel' | 'landing'
    treatment_category VARCHAR(50),  -- 'botox', 'hialuronico', ...
    format VARCHAR(20),  -- 'feed_square' | 'story' | 'reel' | 'web_banner'
    headline TEXT,
    body TEXT,
    cta VARCHAR(100),
    visual_description TEXT,
    visual_url VARCHAR(500),
    visual_embedding vector(512),  -- futuro: CLIP embedding, dim distinta
    text_embedding vector(384),
    performance JSONB,  -- {ctr, cvr, cpl, spend, leads, sales, roi}
    status VARCHAR(20),  -- 'draft' | 'testing' | 'winner' | 'loser' | 'paused'
    learnings TEXT,
    brief_source_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cm_status ON creative_memory(status, treatment_category);
CREATE INDEX idx_cm_text_embedding ON creative_memory 
    USING hnsw (text_embedding vector_cosine_ops);
```

### 7.5 Capa 6 — Learnings

```sql
CREATE TABLE learnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50),  -- 'conversion', 'creative', 'timing', 'pricing', 'channel'
    hypothesis TEXT NOT NULL,
    evidence TEXT NOT NULL,
    outcome VARCHAR(20),  -- 'confirmed' | 'refuted' | 'inconclusive'
    confidence_score NUMERIC(3,2),  -- 0.00 - 1.00
    source_data JSONB,  -- queries usados, métricas observadas
    embedding vector(384),
    author VARCHAR(50) DEFAULT 'growth_agent',
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,  -- learnings caducan
    superseded_by UUID REFERENCES learnings(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_learn_category ON learnings(category, outcome);
CREATE INDEX idx_learn_validity ON learnings(valid_from, valid_until);
CREATE INDEX idx_learn_embedding ON learnings 
    USING hnsw (embedding vector_cosine_ops);
```

### 7.6 Capa 3 — vistas sobre data operativa

No hay tablas nuevas. Se crean **vistas** que unifican queries típicos:

```sql
-- Ejemplo: contexto completo de un lead
CREATE VIEW v_lead_full_context AS
SELECT 
    l.id AS lead_id,
    l.phone, l.email, l.name,
    l.source, l.campaign, l.utm_content,
    l.created_at AS first_contact,
    (SELECT COUNT(*) FROM conversations c WHERE c.patient_id = l.id) AS total_messages,
    (SELECT MAX(created_at) FROM conversations c WHERE c.patient_id = l.id) AS last_message_at,
    (SELECT SUM(monto) FROM livskin_erp.ventas v WHERE v.cod_cliente = l.id) AS total_revenue,
    (SELECT COUNT(*) FROM livskin_erp.ventas v WHERE v.cod_cliente = l.id) AS total_sales
FROM vtiger_leads l;
```

(La referencia cross-DB se implementa con `postgres_fdw` o en la aplicación con dos conexiones.)

---

## 8. Cronograma de activación por capa

```
Fase:           F0   F1   F2   F3   F4   F5   F6
─────────────────────────────────────────────────
Infra (pgvector)    ░░   ██
Embeddings service       ██
L1 Clínico          ░░   ░░   ██
L2 Proyecto         ░░   ░░   ██
L3 Vistas                     ██
MCP server                    ██
L4 Conversaciones                       ██   ██   ██
L5 Creativa                                  ██   ██
L6 Learnings                                      ██
Evals automáticos                                 ██
```

### Fase 1 (Semana 2) — Infraestructura

- VPS 3 con Postgres 16 + pgvector
- DB `livskin_brain` creada
- Schemas de las 6 capas aplicados vía Alembic
- Container `embeddings-service` corriendo con `multilingual-e5-small`
- Endpoint `/embed` interno disponible
- Tests smoke: embed un texto, guardar en DB, buscar por similitud

### Fase 2 (Semanas 3-4) — Capas estáticas pobladas + MCP

**Populación L1:**
- Script que lee el catálogo de `Datos Livskin.xlsx` + blueprint + decisiones clínicas con la doctora
- Inserta ~50-100 registros iniciales:
  - 21 tratamientos con (descripción, contraindicaciones, precio, duración, recuperación, zonas)
  - 12 productos con (descripción, uso, precio)
  - 10-20 FAQs típicas ("¿el botox duele?", "¿cuánto dura?")
  - 5 entradas de brand voice (tono, palabras clave, frases prohibidas)
  - 5 entradas de protocolos (flujo de consulta, preparación, post-cuidado)
- Cada registro se embedea y se guarda

**Populación L2:**
- Script que escanea `docs/**/*.md` + `integrations/**/README.md`
- Chunking a 500-1000 tokens con overlap
- Embedding y storage
- Cron semanal que re-indexa (git hash para deduplicar sin re-embedding)

**Vistas L3:**
- Se crean las vistas SQL consolidadas
- Se prueban con queries representativos

**MCP server:**
- Repositorio `livskin-brain-mcp` en GitHub (puede ser parte de este repo o separado)
- Herramientas expuestas
- Cliente de prueba desde Claude Code

**Exit criteria Fase 2 cerebro:**
- Yo pregunto a Claude Code "¿cuáles son las contraindicaciones del botox?" → respuesta precisa vía MCP
- Yo pregunto "¿por qué elegimos DO VPC?" → encuentra ADR-0004 y cita
- Tests de retrieval en L1: 20 preguntas típicas → 18+/20 con respuesta útil

### Fase 4 (Semana 6) — L4 se activa con Conversation Agent

- Cada mensaje entrante/saliente de WhatsApp se persiste
- Conversation Agent, antes de responder, ejecuta:
  1. `brain_search(layer=L4, patient_id=X, limit=20)` — historial del paciente
  2. `brain_search(layer=L4, semantic=new_msg_content, limit=5)` — 5 precedentes similares
  3. `brain_search(layer=L1, topic=treatment_mentioned)` — info clínica autoritativa
  4. Consulta vistas L3 para contexto operativo (última compra, ticket promedio)
- La respuesta se genera con todo ese contexto inyectado
- El mensaje resultante se guarda (ambos lados de la conversación)

### Fase 5 (Semanas 7-8) — L5 se activa con Content + Acquisition

- Content Agent guarda cada brief generado en `creative_memory` (status='draft')
- Al aprobar: status='testing'
- Acquisition Engine lanza el ad → performance tracking por días
- Al final del testing: status='winner' | 'loser'
- Content Agent, antes de generar próximo brief, consulta `creative_memory` con `status='winner'` filtrando por `treatment_category`

### Fase 6 (Semanas 9-10) — L6 se activa con Growth + evals

- Growth Agent corre semanalmente
- Analiza data cruzada entre L3/L4/L5 + Postgres analytics
- Escribe insights como registros en `learnings` con hypothesis + evidence + confidence
- Los otros agentes consultan `learnings` relevantes antes de decisiones importantes
- Sistema auto-mejorante: learning → consulta agente → mejor decisión → nuevo learning

---

## 9. Dónde se consume el cerebro

### 9.1 Consumidores

| Consumidor | Cómo accede | Casos de uso |
|---|---|---|
| **Conversation Agent** | Tool calls n8n | Contexto paciente, clínica, precedentes |
| **Content Agent** | Tool calls n8n | Creativos ganadores pasados, brand voice |
| **Acquisition Engine** | Tool calls n8n | Performance histórica, learnings |
| **Growth Agent** | Tool calls n8n + SQL directo | Análisis transversal para escribir learnings |
| **Claude Code (yo)** | MCP server | Consulta proyecto, ayuda a usuaria |
| **Usuaria (tú)** | Metabase (L3+L5+L6) | Dashboards, exploración |
| **Langfuse** | Observación pasiva | Trackea qué retrievals hicieron los agentes |

### 9.2 Patrón de consumo típico

```
Agente recibe trigger
    ↓
Consulta al cerebro (1-N calls) para armar contexto
    ↓
Llama Claude API con system prompt + contexto recuperado + user message
    ↓
Claude genera respuesta / decisión
    ↓
Agente ejecuta (enviar WhatsApp, crear ad, actualizar Vtiger...)
    ↓
Agente persiste la interacción en el cerebro (L4 o L5 según tipo)
    ↓
Langfuse recibe trace completa
```

---

## 10. Versionado de embeddings

Toda fila con `embedding` tiene columna `embedding_model_version`. Si el modelo cambia, no se pierde la data pero sí se requiere re-embedding.

### 10.1 Runbook de cambio de modelo

1. Decidir nuevo modelo (ej: `multilingual-e5-small-v1` → `multilingual-e5-large-v1`)
2. Actualizar `embeddings-service` con ambos modelos corriendo
3. Script batch que re-embea todo fila por fila, guarda en `embedding_new` (columna temporal)
4. Cuando termina, rename: `embedding_new` → `embedding`, descarta vieja
5. Actualizar `embedding_model_version`
6. Drop modelo viejo de `embeddings-service`

Ejecutar en ventana nocturna. Tiempo estimado para 100k filas con modelo small → large: ~2-3 horas CPU.

### 10.2 Cuándo cambiaríamos

- Si retrieval quality evals muestran recall bajo (<80%) en golden set representativo
- Si llega un modelo significativamente mejor (ej: Anthropic lanza embeddings propios)
- NO antes — la regla es "mide, no migres" (principio 4).

---

## 11. Tradeoffs aceptados

| Tradeoff | Impacto | Por qué lo aceptamos |
|---|---|---|
| Embeddings self-hosted tienen ~85% del recall de OpenAI premium | Retrieval menos preciso para preguntas muy sutiles | Costo $0 vale el 15% de recall perdido en MVP |
| Postgres compartido con ERP (no instancia propia) | Contención de recursos si ERP explota | Overhead de otro container no se justifica <100k vectores |
| CLIP embeddings para visuales no están en MVP | Creative memory de L5 usa solo text embeddings al inicio | Visual embedding es valioso pero no bloqueante; se añade en mes 2-3 |
| No hay hybrid search (vector + BM25) en v1 | Precisión menor para queries que mezclan semántica y keywords exactas | pgvector lo soporta, se activa cuando haga falta |
| Latencia embedding self-hosted (~100ms) > API OpenAI (~50-150ms) | Marginal | Solo 1 embed por mensaje, dentro del budget de 60s total |
| Schema evolución requiere Alembic migrations | Más disciplina | Vale la confiabilidad |

---

## 12. Métricas de éxito del workstream

El cerebro se considera exitoso si al final de la Fase 6:

1. **Retrieval quality L1:** >90% precision en golden set de 20 preguntas clínicas
2. **Retrieval quality L4:** >80% relevancia en top-5 conversaciones similares (evaluado por LLM-as-judge)
3. **Uso por agentes:** >95% de respuestas de Conversation Agent usan al menos 1 retrieval
4. **Impact conversión:** Conversation Agent con cerebro convierte 20%+ más que sin cerebro (A/B manual)
5. **Learnings escritos:** al menos 5 learnings/semana en L6 tras Fase 6
6. **Latencia P99 retrieval:** <500ms para top-10 semantic search en 50k rows
7. **MCP server usable:** yo respondo 10 preguntas de la usuaria usando MCP, 8+/10 con cita correcta a fuente

---

## 13. Decisión

**Arquitectura aprobada:** Postgres 16 + pgvector en VPS 3, DB separada `livskin_brain`, 6 capas con activación escalonada por fase, embeddings self-hosted `multilingual-e5-small`, MCP server para Claude Code.

**Fecha de aprobación:** 2026-04-18 por Dario.

**Razonamiento de la decisora:** el segundo cerebro es estratégico, no accesorio. Debe construirse desde Fase 1 y crecer con cada fase. Cero costo SaaS. Reutilizable como pieza de portfolio. Diferenciador competitivo real versus clínicas sin sistema.

---

## 14. Consecuencias

### Desbloqueado por esta decisión
- Diseño de los 4 agentes IA con acceso a contexto semántico desde el día uno de cada agente
- Portfolio piece concreto: "Implementé RAG de 6 capas con pgvector self-hosted sobre conversaciones reales"
- Posibilidad futura de empaquetar el sistema como plantilla SaaS RevOps para clínicas peruanas
- Capacidad de evaluación continua con LLM-as-judge desde Fase 6

### Tareas derivadas (pendientes)
- [ ] Fase 1: provisionar VPS 3 + Postgres + pgvector + embeddings service
- [ ] Fase 2: escribir script de populación L1 (con input de la doctora)
- [ ] Fase 2: escribir indexador de repo para L2
- [ ] Fase 2: crear vistas SQL de L3
- [ ] Fase 2: desarrollar MCP server `livskin-brain-mcp`
- [ ] Fase 4: integrar L4 en Conversation Agent
- [ ] Fase 5: integrar L5 en Content Agent
- [ ] Fase 6: integrar L6 con Growth Agent

### Cuándo reabrir esta decisión
- Volumen supera 1M vectores (hoy proyectado para mes 18+): reevaluar instancia dedicada (opción D)
- Retrieval quality evals caen bajo 70%: reevaluar modelo de embeddings
- Anthropic o similar lanza embeddings nativos integrados a Claude API: reconsiderar
- El negocio Livskin se expande a 5+ clínicas: puede justificar vector DB dedicado

---

## 15. Referencias

- Plan maestro §7 — Segundo cerebro workstream
- ADR-0002 — Arquitectura de datos (define dónde vive físicamente)
- ADR-0006 — Embeddings self-hosted (detalle técnico del modelo)
- ADR-0018 — Schema detallado del cerebro (cuando esté escrito en Fase 1)
- Blueprint original — sección sobre memoria vectorial
- pgvector docs: https://github.com/pgvector/pgvector
- Model card multilingual-e5-small: https://huggingface.co/intfloat/multilingual-e5-small

---

## 16. Changelog

- 2026-04-18 — v1.0 — Creada, aprobada en sesión estratégica de Fase 0
