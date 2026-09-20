from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import rag_service


router = APIRouter(
    prefix="/chat",
    tags=["RAG"],
)


class ChatRequest(BaseModel):

    question: str = Field(
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

    session_id: str | None = None


@router.post("")
def chat(
    request: ChatRequest,
):
    try:

        result = rag_service.answer_question(
            question=request.question,
            limit=request.limit,
            min_score=request.min_score,
            document_id=request.document_id,
            session_id=request.session_id,
        )

        return {
            "question": request.question,
            **result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
