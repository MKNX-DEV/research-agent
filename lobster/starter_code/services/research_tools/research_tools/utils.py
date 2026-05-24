import json
import logging
from itertools import islice
from pathlib import Path
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext
from pydantic import ValidationError

from research_tools.config import MCPConfig
from research_tools.exceptions import ConfigurationError, DatasetNotAvailableError

logger = logging.getLogger(__name__)


def load_config() -> MCPConfig:
    try:
        config = MCPConfig()
        logger.info("Application configuration loaded")
        return config

    except ValidationError as e:
        invalid_fields = [".".join(map(str, err["loc"])) for err in e.errors()]
        logger.error(f"Invalid configuration: {invalid_fields}")
        raise ConfigurationError("Missing or invalid environment variables") from e


class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        args = context.message.arguments
        log_message = f"Called MCP tool {tool_name} with arguments {args}."
        logger.info(log_message)
        await context.fastmcp_context.info(log_message)
        result = await call_next(context)
        return result


class SearchEngine:
    def __init__(self, data_path: Path):
        self.data = self._read(data_path)

    @staticmethod
    def _read(path: Path) -> dict[str, list[dict[str, Any]]]:
        if not path.exists():
            raise DatasetNotAvailableError(f"Dataset does not exist: {path}")
        with path.open() as f:
            return json.load(f)

    def get_topics(self) -> list[str]:
        return list(self.data.keys())

    def get_sources(self, topic: str) -> list[str]:
        return list(set([item["source"] for item in self.data[topic]]))

    @staticmethod
    def _matches_query(keyword: str, item: dict[str, Any]) -> bool:
        return keyword in item["title"].lower() or keyword in item["content"].lower()

    def _matches_source(self, sources: list[str] | None, item: dict[str, Any]) -> bool:
        if not sources:
            return True
        return any(source == item["source"] for source in sources)

    def search(
        self,
        keyword: str,
        topic: str,
        sources: list[str] | None,
        max_results: int,
    ) -> list[str]:

        search_results = self._filter_results(
            data=self.data[topic],
            keyword=keyword.lower(),
            sources=sources,
            max_results=max_results,
        )

        return self._format_results(search_results)

    def _filter_results(
        self,
        data: list[dict[str, str]],
        keyword: str,
        sources: list[str] | None,
        max_results: int,
    ) -> list[dict[str, str]]:
        return list(
            islice(
                (
                    {
                        "title": item["title"],
                        "content": item["content"],
                    }
                    for item in data
                    if self._matches_query(item=item, keyword=keyword)
                    and self._matches_source(item=item, sources=sources)
                ),
                max_results,
            )
        )

    @staticmethod
    def _format_results(search_results: list[dict[str, str]]) -> list[str]:
        return [
            f"{item['title'].strip()}: {item['content'].strip()}"
            for item in search_results
        ]
