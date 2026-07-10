"""Ingest youth-friendly plain-language Q&A."""
from __future__ import annotations

import json
from pathlib import Path

from backend.config import DOCUMENT_PRIORITY, settings
from backend.rag.chroma_store import chunk_id, get_or_create_collection, upsert_batches
from backend.rag.sources import build_chunk_metadata


def ingest_youth_qa(path: Path | None = None) -> dict:
    path = path or settings.youth_qa_path
    if not path.exists():
        raise FileNotFoundError(f"Hakuna youth Q&A katika {path}")

    with path.open(encoding="utf-8") as f:
        items = json.load(f)

    collection = get_or_create_collection()
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for idx, item in enumerate(items):
        question = item.get("question", "").strip()
        answer = item.get("answer", "").strip()
        if not question or not answer:
            continue

        text = f"Swali: {question}\n\nJibu: {answer}"
        meta = build_chunk_metadata(
            document_name="Elimu Rahisi kwa Vijana — MuunganoAi",
            document_type="youth_plain",
            source_url="",
            publication_date="",
            page_number=0,
            section_title=item.get("section_title", ""),
            language=item.get("language", "sw"),
            government_institution="MuunganoAi (derived from official sources)",
            priority_level=DOCUMENT_PRIORITY.get("youth_plain", 2),
            source_file="youth_qa.json",
            source_kind="youth",
            chunk_index=idx,
        )
        cid = chunk_id("youth", str(idx), question[:60])
        ids.append(cid)
        documents.append(text)
        metadatas.append(meta)

    if ids:
        upsert_batches(collection, ids, documents, metadatas)

    return {
        "qa_pairs": len(ids),
        "total_chunks": len(ids),
        "collection": settings.collection_name,
    }
