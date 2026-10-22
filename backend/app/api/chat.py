
import logging
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["RAG"],
)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
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
    document_id: uuid.UUID
    session_id: uuid.UUID | None = None


@router.post("")
def chat(request: ChatRequest):
    try:
        result = rag_service.answer_question(
            question=request.question,
            limit=request.limit,
            min_score=request.min_score,
            document_id=str(request.document_id),
            session_id=(
                str(request.session_id)
                if request.session_id
                else None
            ),
        )

        return {
            "question": request.question,
            **result,
        }

    except Exception:
        logger.exception("RAG chat request failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to process the question.",
        )
