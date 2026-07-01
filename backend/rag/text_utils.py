"""PDF text extraction and chunking (no LangChain — Python 3.14 safe)."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(path: Path) -> list[tuple[int, str]]:
    """Return list of (page_number, text) starting at 1."""
    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append((i + 1, text))
    return pages


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks, breaking at natural boundaries."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]

        if end < length:
            split_at = -1
            for sep in (". ", "\n", "; ", ", ", " "):
                pos = chunk.rfind(sep)
                if pos > chunk_size // 3:
                    split_at = pos + len(sep)
                    break
            if split_at > 0:
                chunk = chunk[:split_at]
                end = start + split_at

        piece = chunk.strip()
        if piece:
            chunks.append(piece)

        if end >= length:
            break
        start = max(end - overlap, start + 1)

    return chunks
