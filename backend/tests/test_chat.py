from unittest.mock import MagicMock, patch

from app.services.rag_service import rag_service


def test_chat_returns_grounded_answer():
    mock_results = [
        {
            "score": 0.85,
            "document_id": "test-document",
            "filename": "test_resume.pdf",
            "page_number": 1,
            "chunk_id": 1,
            "text": (
                "Tahir is a Junior AI/ML Engineer backed by "
                "10+ years of front-end and software engineering experience."
            ),
            "snippet": (
                "Tahir is a Junior AI/ML Engineer backed by "
                "10+ years of front-end and software engineering experience."
            ),
        }
    ]

    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        "Tahir has 10+ years of front-end and "
        "software engineering experience. [Source 1]"
    )

    with patch(
        "app.services.rag_service.retrieval_service.search",
        return_value=mock_results,
    ):
        with patch.object(
            rag_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ) as mock_llm:

            result = rag_service.answer_question(
                question=(
                    "How many years of front-end experience "
                    "does Tahir have?"
                ),
                limit=3,
                min_score=0.20,
                session_id="pytest-session",
            )

    assert "answer" in result
    assert "sources" in result

    assert "10+" in result["answer"]
    assert "[Source 1]" in result["answer"]

    assert len(result["sources"]) == 1

    assert result["sources"][0]["filename"] == (
        "test_resume.pdf"
    )

    assert result["sources"][0]["page_number"] == 1

    mock_llm.assert_called_once()


def test_irrelevant_question_fallback():
    with patch(
        "app.services.rag_service.retrieval_service.search",
        return_value=[],
    ):
        with patch.object(
            rag_service.client.chat.completions,
            "create",
        ) as mock_llm:

            result = rag_service.answer_question(
                question="What is Tahir's favorite movie?",
                limit=3,
                min_score=0.50,
                session_id="pytest-fallback",
            )

    assert "answer" in result
    assert "sources" in result

    assert result["sources"] == []

    assert (
        "could not find sufficiently relevant"
        in result["answer"].lower()
    )

    mock_llm.assert_not_called()
