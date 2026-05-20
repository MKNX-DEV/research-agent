from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[0]
ENV_FILE = ROOT.parent / ".env"


class LogLevelConfig(BaseSettings):
    log_level: str


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_file=ENV_FILE)
    llm_name: str = "openai/gpt-4.1"
    api_key: str
    # llm_url: str
    retries: int = 3
    mcp_url: HttpUrl = "http://localhost:8001/mcp"
