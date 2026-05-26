import json
import logging
from itertools import islice
from pathlib import Path
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext
from pydantic import ValidationError
from uvicorn.logging import DefaultFormatter

from research_tools.config import LogLevelConfig, MCPConfig
from research_tools.exceptions import (
    ConfigurationError,
    DatasetNotAvailableError,
    NoSearchResultsError,
)

logger = logging.getLogger(__name__)


def configure_logger(title: str) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(
        DefaultFormatter(
            fmt="%(levelprefix)s %(name)s: %(message)s",
            use_colors=True,
        )
    )

    logger = logging.getLogger(title)
    logger.setLevel(level=getattr(logging, LogLevelConfig().log_level))
    logger.addHandler(handler)
    return logger


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
        log_message = f"Called MCP tool {tool_name}."
        logger.info(log_message)
        logger.debug(f"Passed tool arguments {args}")
        await context.fastmcp_context.info(log_message)
        result = await call_next(context)
        return result


class SearchEngine:
    def __init__(self, keyword: str, sources: list[str] | None, max_results: int):
        self.keyword = keyword
        self.sources = sources
        self.max_results = max_results

    @staticmethod
    def _read(path: Path) -> dict[str, list[dict[str, Any]]]:
        if not path.exists():
            raise DatasetNotAvailableError(f"Dataset does not exist: {path}")
        with path.open() as f:
            data = json.load(f)

        logger.info("Input data loaded")
        return data

    def search(self, data: Path) -> list[str]:
        data = self._read(data)
        search_results = self._filter_results(data=data)
        return self._format_results(search_results)

    def _filter_results(
        self, data: dict[str, list[dict[str, Any]]]
    ) -> list[dict[str, str]]:
        filtered_data = list(
            islice(
                (
                    {
                        "title": item["title"],
                        "content": item["content"],
                    }
                    for items in data.values()
                    for item in items
                    if self._matches_query(item=item)
                    and self._matches_source(item=item)
                ),
                self.max_results,
            )
        )

        if len(filtered_data) == 0:
            raise NoSearchResultsError(
                f"No matching data for the keyword: {self.keyword} or sources: {self.sources}"
            )

        logger.info("Filtered the input data")
        return filtered_data

    def _matches_query(self, item: dict[str, Any]) -> bool:
        return (
            self.keyword in item["title"].lower()
            or self.keyword in item["content"].lower()
        )

    def _matches_source(self, item: dict[str, Any]) -> bool:
        if not self.sources:
            return True
        return any(source == item["source"] for source in self.sources)

    @staticmethod
    def _format_results(search_results: list[dict[str, str]]) -> list[str]:
        formatted_results = [
            f"{item['title'].strip()}: {item['content'].strip()}"
            for item in search_results
        ]

        logger.info("Formatted the search results")
        return formatted_results
