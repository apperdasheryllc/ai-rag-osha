from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/v1", tags=["osha/health"])

@router.get("/osha/health")
async def health():
    """Confirm the ChromaDB collection is reachable."""
    from app.rag.chroma_client import get_osha_collection
    try:
        col   = get_osha_collection()
        count = col.count()
        return {"status": "ok", "chunk_count": count}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))