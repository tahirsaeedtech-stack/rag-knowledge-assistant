
from app.services.hybrid_retrieval_service import (
    lexical_score,
    reciprocal_rank_fusion,
)


def test_lexical_score_exact_match():
    assert lexical_score(
        "professional experience",
        "Professional experience at Vibrant Dynamics",
    ) > 0


def test_lexical_score_no_match():
    assert lexical_score(
        "university",
        "Python FastAPI Docker",
    ) == 0


def test_rrf_promotes_shared_result():
    semantic = [
        {"document_id": "doc1", "chunk_id": 1},
        {"document_id": "doc1", "chunk_id": 2},
    ]

    keyword = [
        {"document_id": "doc1", "chunk_id": 2},
        {"document_id": "doc1", "chunk_id": 3},
    ]

    results = reciprocal_rank_fusion(
        semantic,
        keyword,
    )

    assert results[0]["chunk_id"] == 2
    assert len(results) == 3
