from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]
data_path = ROOT.parent / "data/mock_research_data.json"


class LogLevelConfig(BaseSettings):
    log_level: str


class MCPConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)
    server_name: str = "search"
    transport: Literal["stdio", "http", "sse", "streamable-http"] = "streamable-http"
    on_duplicate: Literal["warn", "error", "replace", "ignore"] | None = "error"
    data: Path = Path(data_path)
    host: str = "0.0.0.0"
    port: int = 8001
