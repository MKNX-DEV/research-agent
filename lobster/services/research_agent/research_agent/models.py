from dataclasses import dataclass
from typing import Literal

from mcp.types import Tool
from pydantic import BaseModel, Field, model_validator


class ResearchAgentOutput(BaseModel):
    research_output: str | None = Field(
        description="Research output from calling the tools"
    )
    found_results: bool = Field(
        description="A boolean flag indicating whether the tool call found matching data"
    )

    @model_validator(mode="after")
    def validate_consistency(self):
        if not self.found_results and self.research_output is not None:
            raise ValueError("research_output must be None when found_results=False")

        if self.found_results and not self.research_output:
            raise ValueError("research_output required when found_results=True")

        return self


class ResearchEndpointOutput(BaseModel):
    research_output: str | None = Field(
        description="Research output to return to the user"
    )
    status: Literal["success", "error", "no_result"] = Field(
        description=(
            """
			High-level processing result: 
			"success" – query processed; 
			"error" – internal error;
            "no_result" - no matches;
			"""
        ),
    )
    reason: str | None = Field(
        default=None,
        description=("Reason to expose to the user in case of no_result or error"),
    )


class ResearchQuery(BaseModel):
    query: str = Field(description="User query to pass to the agent")
    sources: list[str] | None = Field(
        default=None, description="Preferred sources or domains"
    )


@dataclass
class AgentDeps:
    mcp_toolset_info: list[Tool] = Field(description="mcp toolset metadata")
    sources: list[str] | None = Field(
        description="User input for preferred sources when conducting research"
    )
    max_results: int = Field(
        description="maximum number of resources to use in order to respond to the user query"
    )
