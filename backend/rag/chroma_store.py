"""Shared ChromaDB collection helpers."""
from __future__ import annotations

import hashlib

import chromadb
from chromadb.errors import NotFoundError

from backend.config import settings
from backend.rag.embeddings import get_embedding_function

_client: chromadb.PersistentClient | None = None


def reset_chroma_cache() -> None:
    global _client
    _client = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        chroma_path = settings.chroma_dir
        chroma_path.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(chroma_path))
    return _client


def get_or_create_collection(name: str | None = None):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name or settings.collection_name,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def get_collection_safe(name: str | None = None):
    """Return collection; reset client if Chroma reports a stale collection id."""
    try:
        return get_or_create_collection(name)
    except NotFoundError:
        reset_chroma_cache()
        return get_or_create_collection(name)


def delete_collection(name: str | None = None) -> None:
    try:
        get_chroma_client().delete_collection(name or settings.collection_name)
    except Exception:
        pass


def chunk_id(*parts: str) -> str:
    raw = ":".join(parts)
    return hashlib.md5(raw.encode()).hexdigest()


def upsert_batches(
    collection,
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
    batch_size: int = 100,
) -> int:
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
    return len(ids)
