from dataclasses import dataclass
from typing import Literal

from mcp.types import Tool
from pydantic import BaseModel, Field


class ResearchAgentOutput(BaseModel):
    research_output: str = Field(description="Research output")


class ResearchEndpointOutput(BaseModel):
    research_output: str | None = Field(description="Research output")
    status: Literal["success", "error"] = Field(
        default="success",
        description=(
            """
			High-level processing result: 
			'success' – query processed; 
			'error' – internal error.
			"""
        ),
    )
    reason: str | None = Field(default=None, description=(""))


class ResearchQuery(BaseModel):
    """Research query model."""

    query: str = Field(description="User query to pass to the agent")
    sources: list[str] | None = Field(
        default=None, description="Preferred sources or domains"
    )
    max_results: int = Field(
        default=5, description="Maximum number of results to return"
    )


@dataclass
class AgentDeps:
    mcp_toolset_info: list[Tool] = Field(description="")
    sources: list[str] | None = Field(description="")
    max_results: int = Field(description="")
