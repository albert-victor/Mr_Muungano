"""Ingest crawled official web pages into Chroma."""
from __future__ import annotations

from backend.config import settings
from backend.rag.chunking import semantic_chunk_text
from backend.rag.chroma_store import chunk_id, get_or_create_collection, upsert_batches
from backend.rag.crawl import crawl_allowlist, fetch_page
from backend.rag.sources import build_chunk_metadata, load_allowlist


def ingest_web(urls: list[str] | None = None, crawl_all: bool = False) -> dict:
    collection = get_or_create_collection()
    pages = []

    if crawl_all:
        pages = crawl_allowlist()
    elif urls:
        for url in urls:
            page = fetch_page(url)
            if page:
                pages.append(page)
    else:
        allowlist = load_allowlist()
        for entry in allowlist.entries:
            page = fetch_page(entry.url)
            if page:
                pages.append(page)

    total_chunks = 0
    pages_processed = 0

    for page in pages:
        chunks = semantic_chunk_text(page.text, section_title=page.section_title)
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for idx, chunk in enumerate(chunks):
            meta = build_chunk_metadata(
                document_name=page.document_name or page.title,
                document_type=page.document_type,
                source_url=page.url,
                publication_date=page.publication_date,
                page_number=0,
                section_title=chunk.section_title or page.section_title,
                language=page.language,
                government_institution=page.institution,
                priority_level=page.priority,
                source_file=page.url,
                source_kind="web",
                chunk_index=idx,
            )
            cid = chunk_id("web", page.url, str(idx), chunk.text[:80])
            ids.append(cid)
            documents.append(chunk.text)
            metadatas.append(meta)

        if ids:
            upsert_batches(collection, ids, documents, metadatas)
            total_chunks += len(ids)
            pages_processed += 1
            print(f"  ✓ {page.url}: {len(ids)} vipande")

    return {
        "pages_processed": pages_processed,
        "total_chunks": total_chunks,
        "collection": settings.collection_name,
    }
