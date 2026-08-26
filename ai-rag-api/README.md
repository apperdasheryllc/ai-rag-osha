# ai-rag-api

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoint

- GET `/v1/health`

Response:

```json
{
  "message": "API is up and running."
}
```
