"""Environment variable management."""

import logging
from pathlib import Path
from typing import Literal

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[0]
ENV_FILE = ROOT.parent / ".env"

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
    LOG_LEVEL: Literal["DEBUG", "INFO"] = "INFO"
    LLM_NAME: str = "openai/gpt-4o-mini"
    GITHUB_MODELS_API_GPT_4_O_MINI: SecretStr
    RETRIES: int = 3
    MCP_SERVER_URL: HttpUrl = HttpUrl("http://localhost:8001/mcp")
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    MAX_RESULTS: int = 5
