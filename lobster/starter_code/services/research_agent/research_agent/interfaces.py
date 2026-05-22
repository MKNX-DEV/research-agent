from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field


class ResearchOutput(BaseModel):
    research_output: str = Field(description="Research output")


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

    query: str = Field(description="User query to pass to the agent")
    depth: Literal["shallow", "medium", "deep"] = Field(
        default="medium", description="Research depth"
    )
    sources: list[str] | None = Field(
        default=None, description="Preferred sources or domains"
    )
    max_results: int = Field(
        default=5, description="Maximum number of results to return"
    )


@dataclass
class AgentDeps:
    mcp_tools: list
    depth: Literal["shallow", "medium", "deep"]
    sources: list[str]
    max_results: int
