import json
import logging
from itertools import islice
from pathlib import Path
from typing import Any

from research_tools.exceptions import (
    DatasetNotAvailableError,
)

logger = logging.getLogger(__name__)


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

    def search(self, data_path: Path) -> list[str] | None:
        data = self._read(data_path)
        search_results = self._filter_results(data=data)
        if not search_results:
            return None
        return self._format_results(search_results)

    def _filter_results(
        self, data: dict[str, list[dict[str, Any]]]
    ) -> list[dict[str, str]] | None:
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
            logger.info(
                f"No matching data for keyword {self.keyword} or sources {self.sources}"
            )
            return None

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
