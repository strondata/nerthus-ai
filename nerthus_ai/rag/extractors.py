"""
Metadata extraction module for Nerthus AI.
Uses LLM to extract structured metadata during ingestion.
"""

import json
import re
from typing import Any, Dict, Optional

from langchain_openai import ChatOpenAI

from nerthus_ai.core.config import get_settings, PromptsLoader


_JSON_PATTERN = re.compile(r"\{.*\}", re.DOTALL)
METADATA_PREVIEW_CHARS = 3000


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """Parse JSON from LLM responses, returning an empty dict on failure."""
    if not response_text:
        return {}

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = _JSON_PATTERN.search(response_text)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


class MetadataExtractor:
    """Extract metadata for a document using LLM."""

    def __init__(self, llm: Optional[ChatOpenAI] = None, prompt: Optional[str] = None):
        settings = get_settings()
        self.llm = llm or ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
        )
        self.prompts_loader = PromptsLoader(settings.prompts_file)
        self.prompts_loader.load_prompts()
        self.prompt = prompt or self.prompts_loader.get_metadata_prompt()

    def extract(self, text_preview: str, filename: str) -> Dict[str, Any]:
        """
        Extract metadata JSON from the document preview and filename.
        """
        if not self.prompt:
            return {}

        prompt_text = self.prompt.format(
            text=text_preview[:METADATA_PREVIEW_CHARS],
            filename=filename,
        )

        response = self.llm.invoke(prompt_text)
        content = response.content if hasattr(response, "content") else str(response)
        return parse_json_response(content)
