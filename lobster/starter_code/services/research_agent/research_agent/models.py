from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field


class ResearchAgentOutput(BaseModel):
    research_output: str = Field(description="Research output")


class ResearchEndpointOutput(BaseModel):
    research_output: str | None = Field(description="Research output")
    status: Literal["success", "no_results", "error"] = Field(
        default="success",
        description=(
            """
			High-level processing result: 
			'success' – query processed; 
			'no_results' – processed but nothing found; 
			'error' – internal error.
			"""
        ),
    )
    reason: str | None = Field(default=None, description=(""))


class ResearchQuery(BaseModel):
    """Research query model."""

    query: str = Field(description="User query to pass to the agent")
    # depth: Literal["shallow", "medium", "deep"] = Field(
    #     default="medium", description="Research depth"
    # )
    sources: list[str] | None = Field(
        default=None, description="Preferred sources or domains"
    )
    max_results: int = Field(
        default=5, description="Maximum number of results to return"
    )


@dataclass
class AgentDeps:
    mcp_toolset_info: list
    sources: list[str]
    max_results: int
