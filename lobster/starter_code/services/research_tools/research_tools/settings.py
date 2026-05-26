import logging
from pathlib import Path
from typing import Literal

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from research_tools.exceptions import ConfigurationError

ROOT = Path(__file__).resolve().parents[3]
data_path = ROOT.parent / "data/mock_research_data.json"

logger = logging.getLogger(__name__)


class LoggingSettings(BaseSettings):
    LOG_LEVEL: Literal["DEBUG", "INFO"] = "INFO"


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
    SERVER_NAME: str = "search"
    TRANSPORT: Literal["stdio", "http", "sse", "streamable-http"] = "streamable-http"
    ON_DUPLICATE: Literal["warn", "error", "replace", "ignore"] | None = "error"
    DATA: Path = Path(data_path)
    HOST: str = "0.0.0.0"
    PORT: int = 8001


def load_settings() -> MCPSettings:
    try:
        config = MCPSettings()
        logger.info("Application configuration loaded")
        return config

    except ValidationError as e:
        invalid_fields = [".".join(map(str, err["loc"])) for err in e.errors()]
        logger.error(f"Invalid configuration: {invalid_fields}")
        raise ConfigurationError("Missing or invalid environment variables") from e
