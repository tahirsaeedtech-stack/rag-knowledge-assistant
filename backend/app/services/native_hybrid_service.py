
from fastembed import SparseTextEmbedding
from qdrant_client import models

from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store_service


class NativeHybridRetrievalService:
    def __init__(self):
        self.client = vector_store_service.client
        self.collection = (
            f"{vector_store_service.collection_name}_hybrid"
        )
        self.sparse_model = SparseTextEmbedding(
            model_name="Qdrant/bm25"
        )

    def search(
        self,
        query: str,
        limit: int = 3,
        document_id: str | None = None,
    ) -> list[dict]:

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if limit < 1:
            raise ValueError("Limit must be positive.")

        dense_vector = embedding_service.embed_query(
            query
        )

        sparse_embedding = next(
            iter(self.sparse_model.query_embed(query))
        )

        query_filter = None

        if document_id:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(
                            value=document_id
                        ),
                    )
                ]
            )

        candidate_limit = max(limit * 5, 15)

        response = self.client.query_points(
            collection_name=self.collection,
            prefetch=[
                models.Prefetch(
                    query=dense_vector,
                    using="dense",
                    filter=query_filter,
                    limit=candidate_limit,
                ),
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_embedding.indices.tolist(),
                        values=sparse_embedding.values.tolist(),
                    ),
                    using="sparse",
                    filter=query_filter,
                    limit=candidate_limit,
                ),
            ],
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),
            limit=limit,
            with_payload=True,
        )

        results = []

        for point in response.points:
            payload = point.payload or {}
            chunk_text = payload.get("text", "")

            results.append(
                {
                    "score": round(float(point.score), 4),
                    "document_id": payload.get("document_id"),
                    "filename": payload.get("filename"),
                    "page_number": payload.get("page_number"),
                    "chunk_id": payload.get("chunk_id"),
                    "text": chunk_text,
                    "snippet": chunk_text[:300],
                }
            )

        return results


native_hybrid_service = NativeHybridRetrievalService()
