from fastapi import FastAPI
from dotenv import load_dotenv

app = FastAPI(
    title="AI RAG OSHA API",
    description=(
        "API for OSHA PPE retrieval-augmented generation (RAG) and service health checks. "
        "Use the health endpoints to validate API and vector store readiness, and use the "
        "RAG endpoint to answer OSHA PPE questions from indexed regulation chunks."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "API liveness and status endpoints."},
        {"name": "osha/health", "description": "ChromaDB readiness and chunk-count checks."},
        {"name": "osha/ppe", "description": "OSHA PPE question-answering endpoint backed by RAG."},
    ],
)

from .routers import (
    api_health_router,
    osha_ppe_health_router,
    osha_ppe_rag_router
)

load_dotenv()

app.include_router(api_health_router)
app.include_router(osha_ppe_health_router)
app.include_router(osha_ppe_rag_router)
