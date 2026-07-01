"""PDF ingestion — semantic token chunking with full metadata."""
from __future__ import annotations

import re
from pathlib import Path

from backend.config import settings
from backend.rag.chunking import semantic_chunk_text
from backend.rag.chroma_store import chunk_id, delete_collection, get_or_create_collection, upsert_batches
from backend.rag.metadata import pdf_metadata


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(?m)^\s*\d+\s*$", "", text)
    return text.strip()


def extract_pdf_pages(path: Path) -> list[tuple[int, str]]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append((i + 1, text))
    return pages


def ingest_pdfs(pdf_dir: Path | None = None, reset: bool = False) -> dict:
    pdf_dir = pdf_dir or settings.pdf_dir

    if reset:
        delete_collection()

    collection = get_or_create_collection()

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Hakuna PDF katika {pdf_dir}")

    total_chunks = 0
    files_processed = 0

    for pdf_path in pdf_files:
        pages = extract_pdf_pages(pdf_path)
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for page_num, page_text in pages:
            cleaned = _clean_text(page_text)
            if len(cleaned) < 40:
                continue

            chunks = semantic_chunk_text(cleaned)
            for idx, chunk in enumerate(chunks):
                if len(chunk.text.strip()) < 30:
                    continue
                chunk_meta = pdf_metadata(
                    pdf_path,
                    page_number=page_num,
                    section_title=chunk.section_title,
                )
                chunk_meta["chunk_index"] = idx
                cid = chunk_id("pdf", pdf_path.name, str(page_num), str(idx), chunk.text[:80])
                ids.append(cid)
                documents.append(chunk.text)
                metadatas.append(chunk_meta)

        if not ids:
            continue

        upsert_batches(collection, ids, documents, metadatas)
        total_chunks += len(ids)
        files_processed += 1
        print(f"  ✓ {pdf_path.name}: {len(ids)} vipande")

    return {
        "files_processed": files_processed,
        "total_chunks": total_chunks,
        "collection": settings.collection_name,
        "chroma_dir": str(settings.chroma_dir),
    }
