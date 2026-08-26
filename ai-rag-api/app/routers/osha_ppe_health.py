from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1", tags=["osha/health"])


class OshaHealthResponse(BaseModel):
    status: str = Field(description="Health status for Chroma-backed OSHA retrieval")
    chunk_count: int = Field(description="Number of chunks currently available in the collection")


@router.get(
    "/osha/health",
    summary="OSHA retrieval store health",
    description="Validates ChromaDB connectivity and returns the loaded chunk count.",
    response_model=OshaHealthResponse,
    responses={
        503: {
            "description": "Chroma store unavailable or misconfigured",
            "content": {
                "application/json": {
                    "example": {"detail": "chroma sqlite database is locked"}
                }
            },
        }
    },
)
async def health():
    """Confirm the ChromaDB collection is reachable."""
    from app.rag.chroma_client import get_osha_collection
    try:
        col   = get_osha_collection()
        count = col.count()
        return OshaHealthResponse(status="ok", chunk_count=count)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))