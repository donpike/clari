from typing import Any, Dict, List
from pathlib import Path
from pydantic import BaseModel, HttpUrl

class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter API."""
    api_key: str
    model: str = 'claude-3-sonnet'
    api_base_url: HttpUrl
    max_tokens: int = 2000
    temperature: float = 0.7

class ProjectConfig(BaseModel):
    """Configuration for the overall project."""
    openrouter: OpenRouterConfig
    analysis_settings: dict
    logging: dict

    def validate_paths(self) -> None:
        """Validate that all required paths exist."""
        required_paths = ['logs', 'src', 'tests']
        for path in required_paths:
            if not Path(path).exists():
                raise ValueError(f'Required path {path} does not exist')
