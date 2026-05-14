from typing import Literal
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevelConfig(BaseSettings):
	log_level: str


class MCPConfig(BaseSettings):
	model_config = SettingsConfigDict(case_sensitive=False)
	server_name: str = "search"
	transport: Literal["stdio", "http", "sse", "streamable-http"] = "streamable-http"
	on_duplicate: Literal["warn", "error", "replace", "ignore"] | None = "error"
	data: Path = Path("../../data/mock_reserch_data.json")


class AgentConfig(BaseSettings):
	model_config = SettingsConfigDict(case_sensitive=False)
	llm_name: str
	llm_url: str
	retries: int = 3