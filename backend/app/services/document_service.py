from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text page-by-page from a PDF.

    Returns:
        [
            {
                "page_number": 1,
                "text": "..."
            }
        ]
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    pages = []

    with pymupdf.open(file_path) as document:

        for page_index, page in enumerate(document):

            text = page.get_text("text").strip()

            pages.append(
                {
                    "page_number": page_index + 1,
                    "text": text,
                }
            )

    return pages
