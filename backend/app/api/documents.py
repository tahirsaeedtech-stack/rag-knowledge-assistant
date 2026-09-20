from pathlib import Path
import hashlib
import shutil
import uuid

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.services.chunking_service import (
    chunk_text,
)
from app.services.document_service import (
    extract_text_from_pdf,
)
from app.services.embedding_service import (
    embedding_service,
)
from app.services.vector_store_service import (
    vector_store_service,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def calculate_file_hash(
    file_path: Path,
) -> str:

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
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file name provided.",
        )

    if not file.filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF files are supported "
                "currently."
            ),
        )

    document_id = str(uuid.uuid4())

    unique_filename = (
        f"{document_id}_{file.filename}"
    )

    file_path = (
        UPLOAD_DIR /
        unique_filename
    )

    try:

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        file_hash = calculate_file_hash(
            file_path
        )

        existing_document = (
            vector_store_service
            .find_document_by_hash(
                file_hash
            )
        )

        if existing_document:

            if file_path.exists():
                file_path.unlink()

            return {
                "message": (
                    "This document is already indexed."
                ),
                "duplicate": True,
                "document": existing_document,
            }

        pages = extract_text_from_pdf(
            str(file_path)
        )

        chunks = chunk_text(
            pages
        )

        if not chunks:
            raise ValueError(
                "No readable text was found "
                "in the uploaded PDF."
            )

        chunk_texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = (
            embedding_service
            .embed_documents(
                chunk_texts
            )
        )

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunk and embedding counts "
                "do not match."
            )

        stored_vectors = (
            vector_store_service
            .store_chunks(
                document_id=document_id,
                filename=file.filename,
                file_hash=file_hash,
                chunks=chunks,
                embeddings=embeddings,
            )
        )

        total_characters = sum(
            len(page["text"])
            for page in pages
        )

        return {
            "message": (
                "Document uploaded and "
                "indexed successfully."
            ),
            "duplicate": False,
            "document": {
                "document_id": document_id,
                "original_filename": (
                    file.filename
                ),
                "stored_filename": (
                    unique_filename
                ),
                "file_hash": file_hash,
                "page_count": len(pages),
                "total_characters": (
                    total_characters
                ),
                "chunk_count": len(chunks),
                "embedding_count": (
                    len(embeddings)
                ),
                "embedding_dimension": (
                    len(embeddings[0])
                    if embeddings
                    else 0
                ),
                "vectors_stored": (
                    stored_vectors
                ),
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to process document: "
                f"{str(exc)}"
            ),
        )

    finally:
        await file.close()


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
):

    try:

        vector_store_service.delete_document(
            document_id
        )

        return {
            "message": (
                "Document deleted successfully."
            ),
            "document_id": document_id,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete document: "
                f"{str(exc)}"
            ),
        )
