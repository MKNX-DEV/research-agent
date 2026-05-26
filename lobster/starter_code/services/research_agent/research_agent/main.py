"""
Research Agent

This is a template - feel free to completely rewrite or restructure as needed.
This agent receives natural language research requests and uses the tool service
to gather and synthesize information.
"""

# import httpx
# from fastapi.responses import JSONResponse

from fastapi import Depends, FastAPI  # , HTTPException
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.agent import OutputComposer, ResearchAgent
from research_agent.dependencies import (
    get_mcp_client,
    get_mcp_toolset_info,
    get_model,
    get_settings,
)
from research_agent.lifespan import lifespan
from research_agent.logging import configure_logger
from research_agent.models import (
    AgentDeps,
    ResearchAgentOutput,
    ResearchEndpointOutput,
    ResearchQuery,
)
from research_agent.prompts import RESEARCH_PROMPT
from research_agent.settings import Settings

logger = configure_logger("research_agent")

app = FastAPI(
    title="Research Agent",
    description="Intelligent agent that orchestrates research tasks using available tools",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Research Agent is running", "status": "healthy"}


@app.post("/research")
async def research(
    request: ResearchQuery,
    model: Model = Depends(get_model),
    settings: Settings = Depends(get_settings),
    mcp_client: MCPToolset = Depends(get_mcp_client),
    mcp_toolset_info: list = Depends(get_mcp_toolset_info),
) -> ResearchEndpointOutput:

    logger.info(f"Received user query: {request.query}")

    agent = ResearchAgent(
        model=model,
        instructions=RESEARCH_PROMPT,
        toolset=mcp_client,
        settings=settings,
        output_type=ResearchAgentOutput,
        deps_type=AgentDeps,
        output_composer=OutputComposer(),
    )

    agent_deps = AgentDeps(
        mcp_toolset_info=mcp_toolset_info,
        sources=request.sources,
        max_results=request.max_results,
    )

    return await agent.run(request.query, deps=agent_deps)
