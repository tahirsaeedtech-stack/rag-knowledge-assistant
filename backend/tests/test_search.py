from unittest.mock import MagicMock, patch

from app.services.retrieval_service import retrieval_service


def test_retrieval_returns_results():
    mock_point = MagicMock()

    mock_point.score = 0.85
    mock_point.payload = {
        "document_id": "test-document",
        "filename": "test_resume.pdf",
        "page_number": 1,
        "chunk_id": 1,
        "text": (
            "Tahir has 10+ years of front-end "
            "and software engineering experience."
        ),
    }

    mock_query_response = MagicMock()
    mock_query_response.points = [mock_point]

    with patch(
        "app.services.retrieval_service.embedding_service.embed_query",
        return_value=[0.1] * 384,
    ):
        with patch.object(
            retrieval_service,
            "search",
            wraps=retrieval_service.search,
        ):
            with patch(
                "app.services.retrieval_service."
                "vector_store_service.client.query_points",
                return_value=mock_query_response,
            ):
                results = retrieval_service.search(
                    query="front-end developer experience",
                    limit=3,
                    min_score=0.0,
                )

    assert isinstance(results, list)
    assert len(results) > 0

    top_result = results[0]

    assert top_result["filename"] == "test_resume.pdf"
    assert top_result["page_number"] == 1
    assert top_result["score"] == 0.85

    assert "front-end" in top_result["text"].lower()
