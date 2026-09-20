import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving readable structure.
    """

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    return text.strip()


def chunk_text(
    pages: List[Dict],
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> List[Dict]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    chunks = []
    chunk_id = 1

    for page in pages:

        page_number = page.get("page_number")
        raw_text = page.get("text", "")

        cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            continue

        start = 0
        text_length = len(cleaned_text)

        while start < text_length:

            end = min(start + chunk_size, text_length)

            chunk = cleaned_text[start:end]

            # Prefer ending at sentence/paragraph boundary
            if end < text_length:

                possible_breaks = [
                    chunk.rfind(". "),
                    chunk.rfind("? "),
                    chunk.rfind("! "),
                    chunk.rfind("\n"),
                ]

                best_break = max(possible_breaks)

                if best_break > int(chunk_size * 0.6):
                    end = start + best_break + 1

            chunk = cleaned_text[start:end].strip()

            if chunk:

                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "page_number": page_number,
                        "text": chunk,
                        "character_count": len(chunk),
                    }
                )

                chunk_id += 1

            if end >= text_length:
                break

            new_start = max(end - chunk_overlap, 0)

            # Move forward until a safe word boundary
            while (
                new_start < end
                and new_start > 0
                and not cleaned_text[new_start - 1].isspace()
            ):
                new_start += 1

            while (
                new_start < text_length
                and cleaned_text[new_start].isspace()
            ):
                new_start += 1

            start = new_start

    return chunks
