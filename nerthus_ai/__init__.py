"""
Nerthus AI - RAG system with LangChain and ChromaDB.
"""

__version__ = "0.1.0"
__author__ = "Strondata"

from nerthus_ai.core.config import get_settings, load_prompts, Settings, PromptsLoader
from nerthus_ai.core.session import NerthusSession
from nerthus_ai.rag.ingest import DocumentIngester, DocumentLoaderFactory
from nerthus_ai.rag.chain import RAGChain

__all__ = [
    "get_settings",
    "load_prompts",
    "Settings",
    "PromptsLoader",
    "NerthusSession",
    "DocumentIngester",
    "DocumentLoaderFactory",
    "RAGChain",
]
