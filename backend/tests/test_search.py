from app.services.retrieval_service import retrieval_service


def test_retrieval_returns_results():
    results = retrieval_service.search(
        query="front-end developer experience",
        limit=3,
        min_score=0.0,
    )

    assert isinstance(results, list)
    assert len(results) > 0

    top_result = results[0]

    assert "text" in top_result
    assert "score" in top_result
    assert "filename" in top_result
