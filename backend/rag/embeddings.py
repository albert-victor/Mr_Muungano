"""Shared embedding function for Chroma."""
import threading

from chromadb.utils import embedding_functions

from backend.config import settings

_embedding_fn = None
_lock = threading.Lock()


def get_embedding_function():
    global _embedding_fn
    if _embedding_fn is not None:
        return _embedding_fn
    with _lock:
        if _embedding_fn is None:
            _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.embedding_model
            )
    return _embedding_fn
