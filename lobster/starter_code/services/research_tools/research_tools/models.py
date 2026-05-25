from typing import Literal

from pydantic import BaseModel


class SearchResponse(BaseModel):
    status: Literal["success", "no_results"]
    results: list[str] | None
    message: str
