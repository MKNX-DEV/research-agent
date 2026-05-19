"""
Research Agent

This is a template - feel free to completely rewrite or restructure as needed.
This agent receives natural language research requests and uses the tool service
to gather and synthesize information.
"""

# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
import logging
# from typing import Any
# import httpx
from pydantic_ai.providers.github import GitHubProvider
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import Agent
from research_agent.config import AgentConfig


# TODO: Import your common models
# from common import AgentRequest, AgentResponse, MCPSpec, ToolRequest, ToolResponse, ...

# app = FastAPI(
#     title="Research Agent",
#     description="Intelligent agent that orchestrates research tasks using available tools",
#     version="1.0.0"
# )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @app.get("/")
# async def root():
#     """Health check endpoint."""
#     return {"message": "Research Agent is running", "status": "healthy"}


# @app.post("/research")
# async def research(request: dict[str, Any]):
#     """
#     Main research endpoint - accepts natural language research requests.
    
#     TODO: Implement the agent logic:
#     1. Parse and understand the research request
#     2. Decide which tools to use and in what sequence
#     3. Call the tool service via MCP to gather information
#     4. Synthesize results into a comprehensive research report
#     5. Return structured response
#     """
#     # TODO: Implement agent reasoning and tool orchestration
#     # Example flow:
#     # 1. Use LLM to understand request and plan approach
#     # 2. Call tool service /mcp/run/search with appropriate parameters
#     # 3. Analyze results and decide if more searches are needed
#     # 4. Call tool service /mcp/run/synthesize to combine results
#     # 5. Generate final research report
#     pass


# async def call_tool_service(tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
#     """
#     Helper function to call the tool service via MCP.
    
#     TODO: Implement HTTP client to call tool service endpoints.
#     """
#     # TODO: Make HTTP request to TOOL_SERVICE_URL/mcp/run/{tool_name}
#     # Handle errors and timeouts appropriately
#     pass


# TODO: Add any additional helper functions for:
# - LLM interaction and prompting
# - Result processing and analysis
# - Tool orchestration logic


# def connect_to_model(config) -> Model:
# 	model = OpenAIChatModel(
# 		model_name=config.llm_name,
# 		provider=GitHubProvider(api_key=config.api_key),
# 	)

# 	return model

config = AgentConfig()

model = OpenAIChatModel(
    model_name=config.llm_name,
    provider=GitHubProvider(api_key=config.api_key),
)
agent = Agent(model)

if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    print(agent.run_sync('What is the capital of Italy?'))
