import logging
from pathlib import Path
from typing import Literal

from pydantic import HttpUrl, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from research_agent.exceptions import ConfigurationError

ROOT = Path(__file__).resolve().parents[0]
ENV_FILE = ROOT.parent / ".env"

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=ENV_FILE)
    LLM_NAME: str = "openai/gpt-4.1-mini"
    API_KEY: SecretStr
    RETRIES: int = 3
    MCP_SERVER_URL: HttpUrl = "http://localhost:8001/mcp"


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
    LOG_LEVEL: Literal["DEBUG", "INFO"] = "INFO"


def load_settings() -> Settings:
    try:
        settings = Settings()
        logger.info("Application configuration loaded")
        return settings

    except ValidationError as e:
        invalid_fields = [".".join(map(str, err["loc"])) for err in e.errors()]
        logger.error(f"Invalid configuration: {invalid_fields}")
        raise ConfigurationError("Missing or invalid environment variables") from e
