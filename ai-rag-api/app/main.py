from fastapi import FastAPI
from dotenv import load_dotenv

app = FastAPI(title="AI RAG OSHA API")

from .routers import (
    api_health_router,
    osha_ppe_health_router
)

load_dotenv()

app.include_router(api_health_router)
app.include_router(osha_ppe_health_router)
