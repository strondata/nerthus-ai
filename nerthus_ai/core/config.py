"""
Configuration module for Nerthus AI.
Implements Singleton pattern for Settings management.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


DEFAULT_COLLECTION_NAME = "general"

_RESOURCES_DIR = Path(__file__).parent.parent / "resources"
_DEFAULT_PROMPTS_FILE = str(_RESOURCES_DIR / "prompts.yaml")


class PromptSettings(BaseModel):
    """Prompt configuration model."""
    system_prompts: Dict[str, str] = Field(default_factory=dict)
    templates: Dict[str, str] = Field(default_factory=dict)
    metadata_extraction: str = ""
    settings: Dict[str, Any] = Field(default_factory=dict)


class CollectionConfig(BaseModel):
    """Collection configuration metadata."""
    name: str
    description: str
    strict_mode: bool = False


def _default_available_collections() -> Dict[str, CollectionConfig]:
    return {
        "legacy_lab_2023": CollectionConfig(
            name="legacy_lab_2023",
            description="Histórico de testes Afinko/UFSCar, falhas e aprendizados.",
        ),
        "production_scale_2025": CollectionConfig(
            name="production_scale_2025",
            description="Parâmetros atuais, Foods Services, Máquinas de Escala.",
        ),
        DEFAULT_COLLECTION_NAME: CollectionConfig(
            name=DEFAULT_COLLECTION_NAME,
            description="Documentos gerais.",
        ),
    }


class Settings(BaseSettings):
    """
    Application settings using Pydantic.
    Implements Singleton pattern to ensure single instance.
    """
    
    # Singleton instance
    _instance: Optional['Settings'] = None
    
    # LLM Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    model_name: str = Field(default="gpt-3.5-turbo", env="MODEL_NAME")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="./chroma_db",
        env="CHROMA_PERSIST_DIRECTORY"
    )
    collection_name: str = Field(default=DEFAULT_COLLECTION_NAME, env="COLLECTION_NAME")
    available_collections: Dict[str, CollectionConfig] = Field(
        default_factory=_default_available_collections
    )
    
    # RAG Configuration
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    top_k_results: int = Field(default=4, env="TOP_K_RESULTS")
    report_context_documents: int = Field(
        default=5,
        env="REPORT_CONTEXT_DOCUMENTS"
    )
    
    # Paths
    prompts_file: str = Field(default=_DEFAULT_PROMPTS_FILE, env="PROMPTS_FILE")
    documents_directory: str = Field(default="./documents", env="DOCUMENTS_DIRECTORY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __new__(cls, *args, **kwargs):
        """Singleton implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'Settings':
        """Get singleton instance of Settings."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (useful for testing)."""
        cls._instance = None


class PromptsLoader:
    """Loader for YAML-based prompt configurations."""
    
    def __init__(self, prompts_file: str = _DEFAULT_PROMPTS_FILE):
        self.prompts_file = Path(prompts_file)
        self._prompts: Optional[PromptSettings] = None
    
    def load_prompts(self) -> PromptSettings:
        """Load prompts from YAML file."""
        if not self.prompts_file.exists():
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_file}")
        
        with open(self.prompts_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self._prompts = PromptSettings(**data)
        return self._prompts
    
    def get_system_prompt(self, prompt_type: str = "default") -> str:
        """Get system prompt by type."""
        if self._prompts is None:
            self.load_prompts()
        return self._prompts.system_prompts.get(prompt_type, "")
    
    def get_template(self, template_name: str) -> str:
        """Get template by name."""
        if self._prompts is None:
            self.load_prompts()
        return self._prompts.templates.get(template_name, "")

    def get_metadata_prompt(self) -> str:
        """Get metadata extraction prompt."""
        if self._prompts is None:
            self.load_prompts()
        return self._prompts.metadata_extraction
    
    def get_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get prompt setting by name."""
        if self._prompts is None:
            self.load_prompts()
        return self._prompts.settings.get(setting_name, default)


def get_settings() -> Settings:
    """Convenience function to get Settings singleton instance."""
    return Settings.get_instance()


def load_prompts(prompts_file: str = _DEFAULT_PROMPTS_FILE) -> PromptSettings:
    """Convenience function to load prompts from YAML."""
    loader = PromptsLoader(prompts_file)
    return loader.load_prompts()
