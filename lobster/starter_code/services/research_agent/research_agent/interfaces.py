from pydantic import BaseModel, Field


class UserQuery(BaseModel):
    query: str = Field(description="User query for research")


class ResearchOutput(BaseModel):
    research_ouput: str = Field(description="Research output")


class AgentDeps(BaseModel):
	mcp_tools: list