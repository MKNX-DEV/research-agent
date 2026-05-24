from pathlib import Path
from typing import Literal

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[0]
ENV_FILE = ROOT.parent / ".env"


class LogLevelConfig(BaseSettings):
    log_level: Literal["DEBUG", "INFO"] = "INFO"


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_file=ENV_FILE)
    llm_name: str = "openai/gpt-4.1-mini"
    api_key: SecretStr
    retries: int = 1
    mcp_url: HttpUrl = "http://localhost:8001/mcp"
