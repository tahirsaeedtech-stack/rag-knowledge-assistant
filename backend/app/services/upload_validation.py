
from pathlib import Path

from fastapi import HTTPException, UploadFile


MAX_PDF_BYTES = 10 * 1024 * 1024
PDF_MAGIC = b"%PDF-"


def safe_pdf_filename(filename: str | None) -> str:
    """Validate and sanitize the uploaded filename."""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    name = filename.replace("\\", "/").split("/")[-1]

    if name in ("", ".", ".."):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    if not name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    return name


async def save_validated_pdf(
    upload: UploadFile,
    destination: Path,
) -> int:
    """Stream and validate a PDF with a 10 MB limit."""

    size = 0
    first_chunk = True

    try:
        with destination.open("wb") as output:
            while True:
                chunk = await upload.read(1024 * 1024)

                if not chunk:
                    break

                if first_chunk:
                    if not chunk.startswith(PDF_MAGIC):
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid PDF content.",
                        )

                    first_chunk = False

                size += len(chunk)

                if size > MAX_PDF_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the 10 MB limit.",
                    )

                output.write(chunk)

        if size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF is empty.",
            )

        return size

    except Exception:
        destination.unlink(missing_ok=True)
        raise
