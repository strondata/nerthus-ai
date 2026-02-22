"""Resources sub-package: prompts, templates, and static assets."""

from pathlib import Path

RESOURCES_DIR = Path(__file__).parent
PROMPTS_FILE = RESOURCES_DIR / "prompts.yaml"
TEMPLATES_DIR = RESOURCES_DIR / "templates"

__all__ = ["RESOURCES_DIR", "PROMPTS_FILE", "TEMPLATES_DIR"]
