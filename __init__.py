"""
Backwards-compatibility shim.

All public symbols have moved to the ``nerthus_ai`` flat-layout package.
This file exists solely so that legacy ``import`` statements still work
during the transition period.
"""

from nerthus_ai import (  # noqa: F401
    get_settings,
    load_prompts,
    Settings,
    PromptsLoader,
    NerthusSession,
    DocumentIngester,
    DocumentLoaderFactory,
    RAGChain,
)
from nerthus_ai.core.constants import DEFAULT_COLLECTION_NAME  # noqa: F401

__version__ = "0.1.0"
__author__ = "Strondata"
