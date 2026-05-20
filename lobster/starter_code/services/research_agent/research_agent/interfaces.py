from pydantic import BaseModel, Field
from typing import Any


class UserQuery(BaseModel):
    query: str = Field(description="User query for research")


class ResearchOutput(BaseModel):
    research_output: str = Field(description="Research output")


class AgentDeps(BaseModel):
    mcp_tools: list


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