"""Shared interfaces used across the application."""

from dataclasses import dataclass
from typing import Literal

from mcp.types import Tool
from pydantic import BaseModel, Field, model_validator


class ResearchAgentOutput(BaseModel):
    research_output: str | None = Field(
        description="Research output returned from tool execution"
    )
    found_results: bool = Field(
        description="Whether the tool execution found matching results"
    )

    @model_validator(mode="after")
    def validate_consistency(self):
        if not self.found_results and self.research_output is not None:
            raise ValueError("research_output must be None when found_results=False")

        if self.found_results and not self.research_output:
            raise ValueError("research_output is required when found_results=True")

        return self


class ResearchEndpointOutput(BaseModel):
    research_output: str | None = Field(
        description="Research response returned to the user"
    )
    status: Literal["success", "error", "no_result"] = Field(
        description=(
            """
            High-level processing result:
            - "success": query processed successfully
            - "error": internal processing error
            - "no_result": no matching results found
            """
        ),
    )
    reason: str | None = Field(
        default=None,
        description=("Reason exposed to the user in case of an error or no results"),
    )


class ResearchQuery(BaseModel):
    query: str = Field(description="User query passed to the agent")
    sources: list[str] | None = Field(
        default=None, description="Preferred sources for the research"
    )


@dataclass
class AgentDeps:
    mcp_toolset_info: list[Tool] = Field(
        description="Metadata describing the available MCP tools"
    )
    sources: list[str] | None = Field(
        description="User-provided preferred sources for the research"
    )
    max_results: int = Field(
        description="Maximum number of results used to answer the query"
    )
