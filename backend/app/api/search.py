from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.retrieval_service import (
    retrieval_service,
)


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


class SearchRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
    )

    limit: int = Field(
        default=3,
        ge=1,
        le=10,
    )

    min_score: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
    )

    document_id: str | None = None


@router.post("")
def semantic_search(
    request: SearchRequest,
):
    try:

        results = retrieval_service.search(
            query=request.query,
            limit=request.limit,
            min_score=request.min_score,
            document_id=request.document_id,
        )

        return {
            "query": request.query,
            "result_count": len(results),
            "results": results,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
