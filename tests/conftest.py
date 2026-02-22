"""
Test configuration and shared fixtures for the Nerthus AI test suite.

Provides a Factory pattern for generating mock configurations and mock
RAG responses so that individual test modules stay clean and DRY.
"""

from __future__ import annotations

import pytest

from nerthus_ai.core.constants import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    DEFAULT_CHROMA_PERSIST_DIRECTORY,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K_RESULTS,
    DEFAULT_REPORT_CONTEXT_DOCUMENTS,
    DEFAULT_PROMPTS_FILE,
    DEFAULT_DOCUMENTS_DIRECTORY,
)


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

class MockConfigFactory:
    """Factory for generating mock configuration dictionaries."""

    @staticmethod
    def build(**overrides) -> dict:
        """
        Return a settings-like dict populated with default values.

        Keyword arguments override individual keys, e.g.::

            MockConfigFactory.build(model_name="gpt-4", temperature=0.0)
        """
        base = {
            "openai_api_key": "test-key",
            "model_name": DEFAULT_MODEL_NAME,
            "temperature": DEFAULT_TEMPERATURE,
            "chroma_persist_directory": DEFAULT_CHROMA_PERSIST_DIRECTORY,
            "collection_name": DEFAULT_COLLECTION_NAME,
            "chunk_size": DEFAULT_CHUNK_SIZE,
            "chunk_overlap": DEFAULT_CHUNK_OVERLAP,
            "top_k_results": DEFAULT_TOP_K_RESULTS,
            "report_context_documents": DEFAULT_REPORT_CONTEXT_DOCUMENTS,
            "prompts_file": DEFAULT_PROMPTS_FILE,
            "documents_directory": DEFAULT_DOCUMENTS_DIRECTORY,
        }
        base.update(overrides)
        return base


class MockRAGResponseFactory:
    """Factory for generating mock RAG query responses."""

    @staticmethod
    def build(**overrides) -> dict:
        """
        Return a RAG response dict with sensible defaults.

        Keyword arguments override individual keys, e.g.::

            MockRAGResponseFactory.build(answer="42", num_sources=3)
        """
        base = {
            "success": True,
            "question": "What is the default question?",
            "answer": "This is a mock answer.",
            "context": [
                {
                    "content": "Mock context document content.",
                    "metadata": {"source": "mock_doc.txt", "collection": DEFAULT_COLLECTION_NAME},
                }
            ],
            "num_sources": 1,
        }
        base.update(overrides)
        return base


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_config():
    """Fixture that provides a default mock configuration dict."""
    return MockConfigFactory.build()


@pytest.fixture()
def mock_rag_response():
    """Fixture that provides a default mock RAG response dict."""
    return MockRAGResponseFactory.build()
