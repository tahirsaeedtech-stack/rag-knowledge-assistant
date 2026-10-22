
import hashlib
import logging
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.concurrency import run_in_threadpool

from app.services.vector_store_service import (
    vector_store_service,
)
from app.services.embedding_service import (
    embedding_service,
)
from app.services.document_service import (
    extract_text_from_pdf,
)
from app.services.chunking_service import (
    chunk_text,
)
from app.services.upload_validation import (
    safe_pdf_filename,
    save_validated_pdf,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash for duplicate detection."""

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for block in iter(
            lambda: file.read(8192),
            b"",
        ):
            sha256.update(block)

    return sha256.hexdigest()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """Validate, process, embed, and index a PDF."""

    safe_name = safe_pdf_filename(file.filename)

    document_id = str(uuid.uuid4())
    unique_filename = f"{document_id}.pdf"
    file_path = UPLOAD_DIR / unique_filename

    try:
        # 1. Validate and save the uploaded PDF.
        await save_validated_pdf(
            file,
            file_path,
        )

        # 2. Calculate hash without blocking the event loop.
        file_hash = await run_in_threadpool(
            calculate_file_hash,
            file_path,
        )

        # 3. Check whether this document is indexed.
        existing_document = await run_in_threadpool(
            vector_store_service.find_document_by_hash,
            file_hash,
        )

        if existing_document:
            file_path.unlink(missing_ok=True)

            return {
                "message": (
                    "This document is already indexed."
                ),
                "duplicate": True,
                "document": existing_document,
            }

        # 4. Extract PDF text and page metadata.
        pages = await run_in_threadpool(
            extract_text_from_pdf,
            str(file_path),
        )

        # 5. Split extracted text into chunks.
        chunks = await run_in_threadpool(
            chunk_text,
            pages,
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text was found "
                    "in the uploaded PDF."
                ),
            )

        # 6. Prepare texts for embedding.
        chunk_texts = [
            chunk["text"]
            for chunk in chunks
        ]

        # 7. Generate vector embeddings.
        embeddings = await run_in_threadpool(
            embedding_service.embed_documents,
            chunk_texts,
        )

        if len(chunks) != len(embeddings):
            raise RuntimeError(
                "Chunk and embedding counts do not match."
            )

        # 8. Store embeddings and metadata in Qdrant.
        stored_vectors = await run_in_threadpool(
            vector_store_service.store_chunks,
            document_id=document_id,
            filename=safe_name,
            file_hash=file_hash,
            chunks=chunks,
            embeddings=embeddings,
        )

        # 9. Calculate document statistics.
        total_characters = sum(
            len(page["text"])
            for page in pages
        )

        # 10. Return the existing response structure.
        return {
            "message": (
                "Document uploaded and "
                "indexed successfully."
            ),
            "duplicate": False,
            "document": {
                "document_id": document_id,
                "original_filename": safe_name,
                "stored_filename": unique_filename,
                "file_hash": file_hash,
                "page_count": len(pages),
                "total_characters": total_characters,
                "chunk_count": len(chunks),
                "embedding_count": len(embeddings),
                "embedding_dimension": (
                    len(embeddings[0])
                    if len(embeddings) > 0
                    else 0
                ),
                "vectors_stored": stored_vectors,
            },
        }

    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    except Exception:
        logger.exception(
            "Document ingestion failed for %s",
            document_id,
        )

        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred "
                "while processing the document."
            ),
        )

    finally:
        await file.close()


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
):
    """Delete indexed document vectors and local PDF."""

    document_id_str = str(document_id)

    try:
        await run_in_threadpool(
            vector_store_service.delete_document,
            document_id_str,
        )

        stored_file = (
            UPLOAD_DIR / f"{document_id_str}.pdf"
        )

        stored_file.unlink(missing_ok=True)

        return {
            "message": (
                "Document deleted successfully."
            ),
            "document_id": document_id_str,
        }

    except Exception:
        logger.exception(
            "Document deletion failed for %s",
            document_id_str,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete document.",
        )
