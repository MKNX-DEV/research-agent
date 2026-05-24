"""
Research Agent

This is a template - feel free to completely rewrite or restructure as needed.
This agent receives natural language research requests and uses the tool service
to gather and synthesize information.
"""

# import httpx
# from fastapi.responses import JSONResponse
import logging

from fastapi import Depends, FastAPI  # , HTTPException
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.config import AgentConfig
from research_agent.dependencies import (
    get_agent_config,
    get_mcp_tool_info,
    get_mcp_toolset,
    get_model,
)
from research_agent.models import AgentDeps, ResearchOutput, ResearchQuery
from research_agent.prompts import RESEARCH_PROMPT
from research_agent.utils import build_agent, lifespan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    agent_config: AgentConfig = Depends(get_agent_config),
    mcp_toolset: MCPToolset = Depends(get_mcp_toolset),
    mcp_tool_info: list = Depends(get_mcp_tool_info),
) -> ResearchOutput:
    """
    Main research endpoint - accepts natural language research requests.

    TODO: Implement the agent logic:
    1. Parse and understand the research request
    2. Decide which tools to use and in what sequence
    3. Call the tool service via MCP to gather information
    4. Synthesize results into a comprehensive research report
    5. Return structured response
    """
    # TODO: Implement agent reasoning and tool orchestration
    # Example flow:
    # 1. Use LLM to understand request and plan approach
    # 2. Call tool service /mcp/run/search with appropriate parameters
    # 3. Analyze results and decide if more searches are needed
    # 4. Call tool service /mcp/run/synthesize to combine results
    # 5. Generate final research report

    logger.info(f"Received user query: {request.query}")

    agent = build_agent(
        model=model,
        prompt=RESEARCH_PROMPT,
        mcp_server=mcp_toolset,
        config=agent_config,
        output_type=ResearchOutput,
        deps_type=AgentDeps,
    )

    agent_deps = AgentDeps(
        mcp_tools=mcp_tool_info,
        sources=request.sources,
        max_results=request.max_results,
    )

    async with agent:
        response = await agent.run(request.query, deps=agent_deps)

    return response.output
