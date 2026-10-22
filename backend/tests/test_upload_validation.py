
import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile
from tempfile import TemporaryDirectory
from pathlib import Path
from io import BytesIO

from app.services.upload_validation import (
    safe_pdf_filename,
    save_validated_pdf,
)


def test_valid_filename():
    assert safe_pdf_filename("report.pdf") == "report.pdf"


def test_filename_path_sanitization():
    assert safe_pdf_filename(
        "../../report.pdf"
    ) == "report.pdf"


def test_windows_filename_sanitization():
    assert safe_pdf_filename(
        r"C:\private\report.pdf"
    ) == "report.pdf"


def test_invalid_extension():
    with pytest.raises(HTTPException) as exc:
        safe_pdf_filename("malware.exe")

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_invalid_pdf_header():
    upload = UploadFile(
        filename="fake.pdf",
        file=BytesIO(b"not actually a PDF"),
    )

    with TemporaryDirectory() as directory:
        destination = Path(directory) / "test.pdf"

        with pytest.raises(HTTPException) as exc:
            await save_validated_pdf(
                upload,
                destination,
            )

        assert exc.value.status_code == 400
        assert not destination.exists()
