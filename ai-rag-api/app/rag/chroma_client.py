"""Shared ChromaDB client and collection loader for RAG endpoints."""

from functools import lru_cache
import os
from typing import Any

CHROMA_STORE_PATH = os.getenv("CHROMA_STORE_PATH", "../chroma_store")
OSHA_COLLECTION_NAME = os.getenv("OSHA_COLLECTION_NAME", "osha_regulations")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_chroma_client() -> Any:
    """Return the shared persistent ChromaDB client."""
    try:
        import chromadb
    except ImportError as error:
        raise RuntimeError("chromadb is not installed") from error

    return chromadb.PersistentClient(path=CHROMA_STORE_PATH)


@lru_cache(maxsize=1)
def get_osha_collection() -> Any:
    """Return the shared Chroma collection with an embedding function."""
    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    except ImportError as error:
        raise RuntimeError("chromadb is not installed") from error

    embedding_function = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=OSHA_COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    return collection


def preload_chroma_collection() -> Any:
    """Eagerly load the shared Chroma collection during application startup."""
    return get_osha_collection()


def clear_chroma_caches() -> None:
    """Release cached Chroma client/collection references during shutdown."""
    get_osha_collection.cache_clear()
    get_chroma_client.cache_clear()
