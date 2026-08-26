"""Health check endpoint and status tracking."""
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1", tags=["health"])

app_state = {
    "is_healthy": True,
    "start_time": None,
}

class HealthResponse(BaseModel):
    status: str
    timestamp: str


def set_startup_time(start_time: datetime):
    """Set the application start time during lifespan startup."""
    app_state["start_time"] = start_time


@router.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the API.",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    status = "healthy" if app_state["is_healthy"] else "unhealthy"
    if app_state["start_time"]:
        start_time = app_state["start_time"]
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=UTC)

    return HealthResponse(
        status=status,
        timestamp=datetime.now(UTC).isoformat(),
    )
