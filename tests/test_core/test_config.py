"""
Unit tests for nerthus_ai.core.config and nerthus_ai.core.constants.

These tests run without any external dependencies (no LLM, no vector store).
"""

import pytest

from nerthus_ai.core import constants
from nerthus_ai.core.config import (
    Settings,
    CollectionConfig,
    PromptSettings,
    PromptsLoader,
    get_settings,
)
from nerthus_ai.core.constants import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K_RESULTS,
    DEFAULT_REPORT_CONTEXT_DOCUMENTS,
    DEFAULT_PROMPTS_FILE,
    DEFAULT_DOCUMENTS_DIRECTORY,
    DEFAULT_CHROMA_PERSIST_DIRECTORY,
    ENV_OPENAI_API_KEY,
    ENV_MODEL_NAME,
)

# Re-export factories from conftest via direct import so tests are explicit
from conftest import MockConfigFactory, MockRAGResponseFactory


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConstants:
    """Verify every constant has the expected value and type."""

    def test_default_collection_name(self):
        assert DEFAULT_COLLECTION_NAME == "general"

    def test_default_model_name(self):
        assert DEFAULT_MODEL_NAME == "gpt-3.5-turbo"

    def test_default_temperature_is_float(self):
        assert isinstance(DEFAULT_TEMPERATURE, float)
        assert 0.0 <= DEFAULT_TEMPERATURE <= 2.0

    def test_default_chunk_size_positive(self):
        assert DEFAULT_CHUNK_SIZE > 0

    def test_default_chunk_overlap_less_than_chunk_size(self):
        assert DEFAULT_CHUNK_OVERLAP < DEFAULT_CHUNK_SIZE

    def test_env_var_names_are_strings(self):
        for attr in dir(constants):
            if attr.startswith("ENV_"):
                assert isinstance(getattr(constants, attr), str), attr

    def test_default_values_are_defined(self):
        expected_defaults = [
            "DEFAULT_COLLECTION_NAME",
            "DEFAULT_MODEL_NAME",
            "DEFAULT_TEMPERATURE",
            "DEFAULT_CHROMA_PERSIST_DIRECTORY",
            "DEFAULT_CHUNK_SIZE",
            "DEFAULT_CHUNK_OVERLAP",
            "DEFAULT_TOP_K_RESULTS",
            "DEFAULT_REPORT_CONTEXT_DOCUMENTS",
            "DEFAULT_PROMPTS_FILE",
            "DEFAULT_DOCUMENTS_DIRECTORY",
        ]
        for name in expected_defaults:
            assert hasattr(constants, name), f"Missing constant: {name}"


# ---------------------------------------------------------------------------
# Settings model
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSettings:
    """Verify Settings defaults and singleton behaviour."""

    def setup_method(self):
        """Reset singleton before each test."""
        Settings.reset_instance()

    def teardown_method(self):
        """Reset singleton after each test."""
        Settings.reset_instance()

    def test_default_model_name(self):
        s = Settings()
        assert s.model_name == DEFAULT_MODEL_NAME

    def test_default_temperature(self):
        s = Settings()
        assert s.temperature == DEFAULT_TEMPERATURE

    def test_default_collection_name(self):
        s = Settings()
        assert s.collection_name == DEFAULT_COLLECTION_NAME

    def test_default_chunk_size(self):
        s = Settings()
        assert s.chunk_size == DEFAULT_CHUNK_SIZE

    def test_available_collections_includes_default(self):
        s = Settings()
        assert DEFAULT_COLLECTION_NAME in s.available_collections

    def test_singleton_returns_same_instance(self):
        s1 = Settings.get_instance()
        s2 = Settings.get_instance()
        assert s1 is s2

    def test_reset_clears_singleton(self):
        s1 = Settings.get_instance()
        Settings.reset_instance()
        s2 = Settings.get_instance()
        # After reset a new instance is created; they are equal in value
        assert s1.model_name == s2.model_name


# ---------------------------------------------------------------------------
# CollectionConfig model
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCollectionConfig:
    def test_strict_mode_default_false(self):
        cfg = CollectionConfig(name="test", description="A test collection")
        assert cfg.strict_mode is False

    def test_fields_are_stored(self):
        cfg = CollectionConfig(name="col", description="desc", strict_mode=True)
        assert cfg.name == "col"
        assert cfg.description == "desc"
        assert cfg.strict_mode is True


# ---------------------------------------------------------------------------
# Factory fixtures (via conftest)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMockConfigFactory:
    """Verify the factory produces expected shapes."""

    def test_build_defaults(self, mock_config):
        assert mock_config["model_name"] == DEFAULT_MODEL_NAME
        assert mock_config["collection_name"] == DEFAULT_COLLECTION_NAME
        assert mock_config["chunk_size"] == DEFAULT_CHUNK_SIZE

    def test_build_with_overrides(self):
        cfg = MockConfigFactory.build(model_name="gpt-4", temperature=0.0)
        assert cfg["model_name"] == "gpt-4"
        assert cfg["temperature"] == 0.0
        # Non-overridden fields keep defaults
        assert cfg["chunk_size"] == DEFAULT_CHUNK_SIZE

    def test_all_expected_keys_present(self, mock_config):
        required_keys = [
            "openai_api_key",
            "model_name",
            "temperature",
            "chroma_persist_directory",
            "collection_name",
            "chunk_size",
            "chunk_overlap",
            "top_k_results",
            "report_context_documents",
            "prompts_file",
            "documents_directory",
        ]
        for key in required_keys:
            assert key in mock_config, f"Missing key: {key}"


@pytest.mark.unit
class TestMockRAGResponseFactory:
    """Verify the RAG response factory produces expected shapes."""

    def test_build_defaults(self, mock_rag_response):
        assert mock_rag_response["success"] is True
        assert isinstance(mock_rag_response["answer"], str)
        assert isinstance(mock_rag_response["context"], list)

    def test_build_with_overrides(self):
        resp = MockRAGResponseFactory.build(answer="42", num_sources=3)
        assert resp["answer"] == "42"
        assert resp["num_sources"] == 3

    def test_context_items_have_required_keys(self, mock_rag_response):
        for item in mock_rag_response["context"]:
            assert "content" in item
            assert "metadata" in item
