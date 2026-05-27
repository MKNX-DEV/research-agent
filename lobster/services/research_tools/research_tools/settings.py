import logging
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
data_path = ROOT.parent / "data/mock_research_data.json"

logger = logging.getLogger(__name__)


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
    LOG_LEVEL: Literal["DEBUG", "INFO"] = "INFO"
    SERVER_NAME: str = "search"
    TRANSPORT: Literal["stdio", "http", "sse", "streamable-http"] = "streamable-http"
    ON_DUPLICATE: Literal["warn", "error", "replace", "ignore"] | None = "error"
    DATA: Path = Path(data_path)
    HOST: str = "0.0.0.0"
    PORT: int = 8001
