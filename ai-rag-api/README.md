# ai-rag-api

FastAPI service for OSHA PPE RAG with ChromaDB-backed retrieval.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

Set these values in `.env`:

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_OSHA_RAG_MODEL`
- `CHROMA_STORE_PATH` (default `../chroma_store`)
- `OSHA_COLLECTION_NAME` (default `osha_regulations`)
- `EMBED_MODEL` (default `all-MiniLM-L6-v2`)

## API docs

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Endpoints

- `GET /v1/health`

  Returns the API service liveness status and current UTC timestamp.

  Example response:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-08-26T15:00:00+00:00"
  }
  ```

- `GET /v1/osha/health`

  Verifies ChromaDB connectivity and reports how many OSHA chunks are currently loaded.

  Example response:
  ```json
  {
    "status": "ok",
    "chunk_count": 1234
  }
  ```

- `POST /v1/osha/ppe`

  Retrieves relevant OSHA PPE regulation chunks and generates a grounded answer to the submitted question.

  Example request body:
  ```json
  {
    "query": "When are safety nets required?",
    "results": 5
  }
  ```

  Example response shape:
  ```json
  {
    "answer": "...",
    "sources": [
      {
        "citation": "1926.105(a)",
        "label": "1926.105 - Safety nets.",
        "source_url": "https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.105",
        "text": "..."
      }
    ]
  }
  ```
