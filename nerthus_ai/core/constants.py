"""
Centralized constants for Nerthus AI.
All default values, configuration keys, and environment variable names live here.
"""

# ---------------------------------------------------------------------------
# Environment variable names
# ---------------------------------------------------------------------------

ENV_OPENAI_API_KEY = "OPENAI_API_KEY"
ENV_MODEL_NAME = "MODEL_NAME"
ENV_TEMPERATURE = "TEMPERATURE"
ENV_CHROMA_PERSIST_DIRECTORY = "CHROMA_PERSIST_DIRECTORY"
ENV_COLLECTION_NAME = "COLLECTION_NAME"
ENV_CHUNK_SIZE = "CHUNK_SIZE"
ENV_CHUNK_OVERLAP = "CHUNK_OVERLAP"
ENV_TOP_K_RESULTS = "TOP_K_RESULTS"
ENV_REPORT_CONTEXT_DOCUMENTS = "REPORT_CONTEXT_DOCUMENTS"
ENV_PROMPTS_FILE = "PROMPTS_FILE"
ENV_DOCUMENTS_DIRECTORY = "DOCUMENTS_DIRECTORY"

# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------

DEFAULT_COLLECTION_NAME = "general"
DEFAULT_MODEL_NAME = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_CHROMA_PERSIST_DIRECTORY = "./chroma_db"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_TOP_K_RESULTS = 4
DEFAULT_REPORT_CONTEXT_DOCUMENTS = 5
DEFAULT_PROMPTS_FILE = "prompts.yaml"
DEFAULT_DOCUMENTS_DIRECTORY = "./documents"
