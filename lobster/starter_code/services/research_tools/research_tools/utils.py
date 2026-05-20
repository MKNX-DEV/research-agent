import json
from itertools import islice
from pathlib import Path


class SearchEngine:
    def __init__(self, data_path: Path):
        self.data = self._read(data_path)

    @staticmethod
    def _read(path: Path) -> dict[str, list[dict[str, str]]]:
        with path.open() as f:
            return json.load(f)

    def get_sources(self) -> list[str]:
        return list(self.data.keys())

    def search(
        self,
        source: str,
        query: str,
        max_results: int,
    ) -> list[dict[str, str]]:

        query = query.lower()

        return list(
            islice(
                (
                    {
                        "title": item["title"],
                        "content": item["content"],
                    }
                    for item in self.data[source]
                    if query in item["title"].lower()
                    or query in item["content"].lower()
                ),
                max_results,
            )
        )
