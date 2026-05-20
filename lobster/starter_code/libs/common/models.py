"""
Common data models - feel free to modify, adapt, or create additional models as needed.
"""

from pydantic import BaseModel, Field
from typing import Any


class ToolRequest(BaseModel):
    """Request to execute a tool via MCP."""
    params: dict[str, Any]


class ToolResponse(BaseModel):
    """Response from tool execution."""
    success: bool
    result: dict[str, Any] | None = None
    error: str | None = None


class ResearchQuery(BaseModel):
    """Research query model."""
    topic: str
    depth: str = Field(default="medium", description="Research depth: shallow, medium, deep")
    sources: list[str] | None = Field(default=None, description="Preferred sources or domains")
    max_results: int = Field(default=5, description="Maximum number of results to return")