"""Retrieve relevant chunks from Chroma with multi-source priority boosting."""
from __future__ import annotations

from dataclasses import dataclass

from backend.config import SOURCE_KIND_BOOST, TONE_SOURCE_KIND, retrieval_k_for_tone, settings
from backend.rag.chroma_store import get_chroma_client, get_collection_safe, get_or_create_collection


@dataclass
class RetrievedChunk:
    text: str
    document_name: str
    document_title: str
    source_file: str
    source_url: str
    page: int
    document_type: str
    section_title: str
    language: str
    government_institution: str
    priority: int
    source_kind: str
    distance: float
    score: float = 0.0

    def to_citation(self) -> dict:
        return {
            "document_title": self.document_title or self.document_name,
            "document_name": self.document_name,
            "source_file": self.source_file,
            "source_url": self.source_url,
            "page": self.page,
            "document_type": self.document_type,
            "section_title": self.section_title,
            "government_institution": self.government_institution,
            "source_kind": self.source_kind,
            "excerpt": self.text[:280] + ("…" if len(self.text) > 280 else ""),
        }


_collection = None
_chunk_count: int | None = None


def is_retriever_ready() -> bool:
    return _collection is not None


def invalidate_retriever_cache() -> None:
    """Refresh cached collection after ingest."""
    global _collection, _chunk_count
    _collection = None
    _chunk_count = None


def warm_retriever() -> int:
    """Load embedding model + Chroma collection once at startup."""
    global _collection, _chunk_count
    try:
        from backend.rag.embeddings import get_embedding_function

        get_embedding_function()
        _collection = get_or_create_collection()
        _chunk_count = _collection.count()
        return _chunk_count
    except Exception:
        _collection = None
        _chunk_count = 0
        return 0


def get_chunk_count() -> int:
    if _chunk_count is not None:
        return _chunk_count
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=settings.collection_name)
        return collection.count()
    except Exception:
        return 0


def _tone_boost(source_kind: str, tone: str) -> float:
    preferred = TONE_SOURCE_KIND.get(tone, TONE_SOURCE_KIND["default"])
    if source_kind in preferred:
        rank = preferred.index(source_kind)
        return 1.0 - (rank * 0.08)
    return 0.92


def _compute_score(distance: float, priority: int, source_kind: str, tone: str) -> float:
    kind_factor = SOURCE_KIND_BOOST.get(source_kind, 1.0)
    tone_factor = _tone_boost(source_kind, tone)
    priority_factor = 1.0 / max(priority, 1)
    return (1.0 - min(distance, 1.0)) * kind_factor * tone_factor * priority_factor


def retrieve(
    query: str,
    k: int | None = None,
    tone: str = "default",
    lang: str | None = None,
) -> list[RetrievedChunk]:
    k = k or retrieval_k_for_tone(tone)
    collection = _collection
    if collection is None:
        try:
            collection = get_collection_safe()
        except Exception:
            return []

    total = _chunk_count if _chunk_count is not None else collection.count()
    if total == 0:
        return []

    fetch_k = min(k + 4, total)
    results = collection.query(query_texts=[query], n_results=fetch_k)

    chunks: list[RetrievedChunk] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances):
        source_kind = meta.get("source_kind", "pdf")
        priority = int(meta.get("priority_level", meta.get("priority", 5)))
        distance = float(dist)
        score = _compute_score(distance, priority, source_kind, tone)
        chunk_lang = (meta.get("language") or "mixed").lower()[:2]
        if lang == "en" and chunk_lang == "sw":
            score *= 0.5
        elif lang == "sw" and chunk_lang == "en":
            score *= 0.75
        chunks.append(
            RetrievedChunk(
                text=doc,
                document_name=meta.get("document_name", meta.get("document_title", "Unknown")),
                document_title=meta.get("document_title", meta.get("document_name", "Unknown")),
                source_file=meta.get("source_file", ""),
                source_url=meta.get("source_url", ""),
                page=int(meta.get("page_number", meta.get("page", 0))),
                document_type=meta.get("document_type", ""),
                section_title=meta.get("section_title", ""),
                language=meta.get("language", "mixed"),
                government_institution=meta.get("government_institution", ""),
                priority=priority,
                source_kind=source_kind,
                distance=distance,
                score=score,
            )
        )

    chunks.sort(key=lambda c: (-c.score, c.distance, c.priority))
    return chunks[:k]


def format_context(chunks: list[RetrievedChunk], max_chars: int | None = None) -> str:
    if not chunks:
        return ""

    max_chars = max_chars or settings.context_chunk_max_chars
    parts = []
    for i, chunk in enumerate(chunks, 1):
        text = chunk.text
        if len(text) > max_chars:
            text = text[:max_chars].rsplit(" ", 1)[0] + "…"

        page_part = f" p.{chunk.page}" if chunk.page else ""
        parts.append(f"[{i}] {chunk.document_name}{page_part}\n{text}")

    return "\n\n".join(parts)
