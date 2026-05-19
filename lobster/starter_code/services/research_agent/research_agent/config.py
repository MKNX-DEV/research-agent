from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl

ROOT = Path(__file__).resolve().parents[0]
ENV_FILE = ROOT.parent / ".env"

class LogLevelConfig(BaseSettings):
    log_level: str


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_file=ENV_FILE)
    llm_name: str = "openai/gpt-4.1"
    api_key: str
    llm_url: str = "test"
    retries: int = 3

class MCPConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)
    server_name: str = "search"
    transport: Literal["stdio", "http", "sse", "streamable-http"] = "streamable-http"
    url: HttpUrl = "http://localhost:8001"
