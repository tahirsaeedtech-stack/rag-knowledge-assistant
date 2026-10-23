
from app.config import QDRANT_COLLECTION
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service


class RetrievalService:
    def search(
        self,
        query: str,
        limit: int = 3,
        min_score: float = 0.0,
        document_id: str | None = None,
    ) -> list[dict]:

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if limit < 1:
            raise ValueError("Search limit must be at least 1.")

        query_embedding = embedding_service.embed_query(query)

        query_filter = None

        if document_id:
            query_filter = {
                "must": [
                    {
                        "key": "document_id",
                        "match": {"value": document_id},
                    }
                ]
            }

        fetch_limit = max(limit * 5, 15)

        results = vector_store_service.client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_embedding,
            query_filter=query_filter,
            limit=fetch_limit,
            with_payload=True,
        )

        matches = []
        seen = set()

        for point in results.points:
            score = float(point.score)

            if score < min_score:
                continue

            payload = point.payload or {}
            chunk_text = payload.get("text", "")

            dedup_key = (
                payload.get("document_id"),
                payload.get("page_number"),
                chunk_text,
            )

            if dedup_key in seen:
                continue

            seen.add(dedup_key)

            matches.append(
                {
                    "score": round(score, 4),
                    "document_id": payload.get("document_id"),
                    "filename": payload.get("filename"),
                    "page_number": payload.get("page_number"),
                    "chunk_id": payload.get("chunk_id"),
                    "text": chunk_text,
                    "snippet": chunk_text[:300],
                }
            )

            if len(matches) >= limit:
                break

        return matches


retrieval_service = RetrievalService()
