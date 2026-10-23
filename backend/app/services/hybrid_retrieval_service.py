
import re
from collections import Counter

from app.services.retrieval_service import retrieval_service
from app.services.vector_store_service import vector_store_service


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def lexical_score(query: str, text: str) -> float:
    query_terms = Counter(tokenize(query))
    document_terms = Counter(tokenize(text))

    if not query_terms or not document_terms:
        return 0.0

    return sum(
        min(query_terms[term], document_terms[term])
        for term in query_terms
    ) / sum(query_terms.values())


def reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    k: int = 60,
) -> list[dict]:
    fused = {}

    for results in (semantic_results, keyword_results):
        for rank, result in enumerate(results, start=1):
            key = (
                str(result.get("document_id")),
                str(result.get("chunk_id")),
            )

            if key not in fused:
                fused[key] = {
                    **result,
                    "fusion_score": 0.0,
                }

            fused[key]["fusion_score"] += 1 / (k + rank)

    return sorted(
        fused.values(),
        key=lambda item: item["fusion_score"],
        reverse=True,
    )


class HybridRetrievalService:
    def search(
        self,
        query: str,
        limit: int = 3,
        document_id: str | None = None,
    ) -> list[dict]:

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if limit < 1:
            raise ValueError("Search limit must be at least 1.")

        candidate_limit = max(limit * 5, 15)

        semantic_results = retrieval_service.search(
            query=query,
            limit=candidate_limit,
            min_score=0.0,
            document_id=document_id,
        )

        # Starter implementation: scan Qdrant payloads
        # to build a lexical ranking.
        from qdrant_client import models

        keyword_candidates = []
        offset = None

        while True:
            scroll_filter = None

            if document_id:
                scroll_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(
                                value=document_id
                            ),
                        )
                    ]
                )

            points, offset = (
                vector_store_service.client.scroll(
                    collection_name=(
                        vector_store_service.collection_name
                    ),
                    scroll_filter=scroll_filter,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
            )

            for point in points:
                payload = point.payload or {}
                text = payload.get("text", "")

                score = lexical_score(query, text)

                if score <= 0:
                    continue

                keyword_candidates.append(
                    {
                        "score": score,
                        "document_id": payload.get(
                            "document_id"
                        ),
                        "filename": payload.get(
                            "filename"
                        ),
                        "page_number": payload.get(
                            "page_number"
                        ),
                        "chunk_id": payload.get(
                            "chunk_id"
                        ),
                        "text": text,
                        "snippet": text[:300],
                    }
                )

            if offset is None:
                break

        keyword_candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        keyword_results = keyword_candidates[
            :candidate_limit
        ]

        fused_results = reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
        )

        return fused_results[:limit]


hybrid_retrieval_service = HybridRetrievalService()
