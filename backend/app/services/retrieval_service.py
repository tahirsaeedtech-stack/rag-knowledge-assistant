from app.config import QDRANT_COLLECTION
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service


class RetrievalService:

    def search(
        self,
        query: str,
        limit: int = 3,
        min_score: float = 0.20,
        document_id: str | None = None,
    ) -> list[dict]:

        if not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        query_embedding = (
            embedding_service.embed_query(query)
        )

        query_filter = None

        if document_id:
            query_filter = {
                "must": [
                    {
                        "key": "document_id",
                        "match": {
                            "value": document_id
                        },
                    }
                ]
            }

        # Fetch more than the requested limit so that
        # duplicate chunks can be removed without
        # leaving too few final results.
        fetch_limit = max(limit * 4, 10)

        results = (
            vector_store_service.client.query_points(
                collection_name=QDRANT_COLLECTION,
                query=query_embedding,
                query_filter=query_filter,
                limit=fetch_limit,
                with_payload=True,
            )
        )

        matches = []

        for point in results.points:

            score = float(point.score)

            if score < min_score:
                continue

            payload = point.payload or {}

            text = payload.get("text", "")

            matches.append(
                {
                    "score": round(score, 4),
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

        # Remove duplicate chunks.
        # The same PDF may have been uploaded more than once,
        # so identical text can exist under different document IDs.
        unique_matches = []
        seen = set()

        for match in matches:

            dedup_key = (
                match.get("filename"),
                match.get("page_number"),
                match.get("text"),
            )

            if dedup_key in seen:
                continue

            seen.add(dedup_key)
            unique_matches.append(match)

            if len(unique_matches) >= limit:
                break

        return unique_matches


retrieval_service = RetrievalService()
