import uuid

from qdrant_client import QdrantClient, models
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from app.config import (
    EMBEDDING_DIMENSION,
    QDRANT_COLLECTION,
    QDRANT_URL,
)


class VectorStoreService:

    def __init__(self):
        self.client = QdrantClient(
            url=QDRANT_URL
        )

        self.collection_name = (
            QDRANT_COLLECTION
        )

        self._ensure_collection()

    def _ensure_collection(self):

        if not self.client.collection_exists(
            collection_name=self.collection_name
        ):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

    def store_chunks(
        self,
        document_id: str,
        filename: str,
        file_hash: str,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> int:

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings count must match."
            )

        points = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "file_hash": file_hash,
                    "chunk_id": chunk["chunk_id"],
                    "page_number": chunk["page_number"],
                    "text": chunk["text"],
                },
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

        return len(points)

    def find_document_by_hash(
        self,
        file_hash: str,
    ) -> dict | None:

        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="file_hash",
                        match=models.MatchValue(
                            value=file_hash
                        ),
                    )
                ]
            ),
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if not points:
            return None

        payload = points[0].payload or {}

        return {
            "document_id": payload.get(
                "document_id"
            ),
            "filename": payload.get(
                "filename"
            ),
            "file_hash": payload.get(
                "file_hash"
            ),
        }

    def delete_document(
        self,
        document_id: str,
    ) -> None:

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(
                                value=document_id
                            ),
                        )
                    ]
                )
            ),
            wait=True,
        )


vector_store_service = VectorStoreService()
