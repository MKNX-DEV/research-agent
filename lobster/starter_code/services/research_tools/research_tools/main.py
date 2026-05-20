"""
Research Tool Service

This is a template - feel free to completely rewrite or restructure as needed.
This service exposes tools via MCP protocol for agents to use.
"""

# from fastapi import FastAPI, HTTPException
import logging

from fastapi.requests import Request
from fastapi.responses import JSONResponse

# from typing import Any
from fastmcp import FastMCP

# TODO: Import your common models
# from common import MCPSpec, ToolRequest, ToolResponse, ResearchResult, ResearchSynthesis, ...
from research_tools.config import MCPConfig
from research_tools.utils import SearchEngine

# app = FastAPI(
#     title="Research Tool Service",
#     description="MCP-compliant service providing research tools for agents",
#     version="1.0.0"
# )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @app.get("/")
# async def root():
#     """Health check endpoint."""
#     mcp_server.run(transport=mcp_config.transport)
#     return {"message": "Research Tool Service is running", "status": "healthy"}


# @app.get("/mcp/spec")
# async def get_mcp_spec():
#     """
#     Return the MCP specification of available research tools.

#     TODO: Implement this endpoint to return an MCPSpec object
#     describing the research tools this service provides.
#     """
#     # TODO: Define your tool service specification
#     # This should describe tools like 'search', 'synthesize', 'analyze'
#     pass


# @app.post("/mcp/run/{tool_name}")
# async def execute_tool(tool_name: str, request: dict[str, Any]):
#     """
#     Execute a specific research tool via MCP protocol.

#     TODO: Implement tool execution logic.
#     Expected tools:
#     - search: Search for information using mock data sources
#     - synthesize: Synthesize multiple research results
#     - analyze: Analyze research results for insights
#     """
#     # TODO: Implement tool routing and execution
#     # Use the provided mock data sources
#     # Return appropriate ToolResponse objects
#     pass


# TODO: Add any additional endpoints or helper functions you need


mcp_config = MCPConfig()
mcp_server = FastMCP(name=mcp_config.server_name, on_duplicate=mcp_config.on_duplicate)


@mcp_server.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


@mcp_server.tool
async def discover_sources() -> list[str]:
    """
    **discover sources/topics**
    - Purpose: Discover sources/topics available in mock data
    """

    logger.info("Called MCP tool 'discover_sources'")
    engine = SearchEngine(data_path=mcp_config.data)
    sources = engine.get_sources()
    logger.info(f"Discovered sources: {sources}")
    return sources


@mcp_server.tool
async def search(sources: str, query: str, max_results: int) -> list[dict[str, str]]:
    """
    **search**
    - Purpose: Search for information in mock data sources
    - Parameters:
    - `sources` (string): Knowledge base category to filter search
    - `query` (string): Search query keyword
    - `max_results` (int): Maximum number of results to return
    """

    logger.info(
        f"""
        Called MCP tool 'search' with the following parameters:
        - sources: {sources}
        - query: {query}
        - max_results: {max_results}
        """
    )
    engine = SearchEngine(data_path=mcp_config.data)
    return engine.search(source=sources, query=query, max_results=max_results)


@mcp_server.tool
async def synthesize(search_results: list[dict[str, str]]) -> str:
    """
    **synthesize**
    - Purpose: Combine multiple search results into a coherent summary
    - Parameters:
    - `search_results` (list of dictionaries): Output from the `search` tool,
      where each dictionary contains at least `title` and `content`
    - Returns: Synthesized text with inline citations
    """

    logger.info("Called MCP tool 'synthesize'")

    if not search_results:
        return "No sources provided."

    cleaned_sources = []

    for item in search_results:
        title = item.get("title", "").strip()
        content = item.get("content", "").strip()

        # Skip entries with no usable content
        if not title and not content:
            continue

        # Combine title and description into a single text block
        if title and content:
            text = f"{title}: {content}"
        else:
            text = title or content

        cleaned_sources.append(text)

    if not cleaned_sources:
        return "No valid source content provided."

    summary = " ".join(
        f"{text} [{idx}]" for idx, text in enumerate(cleaned_sources, start=1)
    )

    return summary


@mcp_server.tool
async def analyze(synthesized_content: str, user_query: str) -> str:
    """
    **analyze**
    - Purpose: Analyze synthesized content for insights
    - Parameters:
    - `synthesized_content` (string): The synthesized text to analyze
    - `user_query` (string): User query for analysis focus
    - Returns: Analysis results based on user query
    """

    logger.info("Called MCP tool analyze")

    return f"""
        You are an expert analyst.

        Analyze the synthesized content with respect to the user query.

        User Query:
        {user_query}

        Content:
        {synthesized_content}
    """


if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8001)
    mcp_server.run(
        transport=mcp_config.transport,
        host=mcp_config.host,
        port=mcp_config.port,
    )
