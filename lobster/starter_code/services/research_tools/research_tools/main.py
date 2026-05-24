"""
Research Tool Service

This is a template - feel free to completely rewrite or restructure as needed.
This service exposes tools via MCP protocol for agents to use.
"""

import logging
from textwrap import dedent

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
#from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from pydantic import Field

from research_tools.exceptions import NoSearchResultsError
from research_tools.models import SearchResponse
from research_tools.utils import LoggingMiddleware, SearchEngine, load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = load_config()
server = FastMCP(name=config.server_name, on_duplicate=config.on_duplicate)

server.add_middleware(ErrorHandlingMiddleware(
    include_traceback=True,
    transform_errors=True
    )
)

#server.add_middleware(RateLimitingMiddleware())
server.add_middleware(LoggingMiddleware())


@server.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


@server.tool(description="Discover topics available in the dataset")
async def discover_topics() -> list[str]:
    engine = SearchEngine(data_path=config.data)
    topics = engine.get_topics()
    logger.info(f"Discovered topics: {topics}")
    return topics


@server.tool(
    description="Discover available sources for a topic when the user specifies a source"
)
async def discover_sources(
    topic: str = Field(description="Topic for which to retrieve available sources"),
) -> list[str]:
    engine = SearchEngine(data_path=config.data)
    sources = engine.get_sources(topic=topic)
    logger.info(f"Available sources for topic {topic}. Sources: {sources}.")
    return sources


@server.tool(description="Extract the primary search keyword from the user query")
async def extract_search_keyword(
    query: str = Field(
        description="User query from which to extract the primary search keyword"
    ),
) -> str:
    return dedent(
        f"""
        Extract the primary search keyword from the user query.
        User Query: {query}
        """
    )


@server.tool(description="Search the dataset for user-requested information")
async def search(
    topic: str = Field(description="Knowledge base topic to search within"),
    keyword: str = Field(description="Primary search keyword"),
    sources: list[str] | None = Field(description="Sources to search within"),
    max_results: int = Field(description="Maximum number of results to return"),
) -> SearchResponse:

    engine = SearchEngine(data_path=config.data)
    results = engine.search(
        keyword=keyword, topic=topic, sources=sources, max_results=max_results
    )

    if not results:
        logger.info("Search returned no results")
        search_response = SearchResponse(
            status="no_results",
            results=[],
            message=("No matching documents were found for the provided query."),
        )
        raise NoSearchResultsError(
            "No matching documents were found for the provided query."
        )
    else:
        logger.info(f"Found research data: {results}")
        search_response = SearchResponse(
            status="success",
            results=results,
            message=f"Found {len(results)} matching result(s).",
        )
    return search_response


@server.tool(description="Combine multiple search results into a coherent summary")
async def synthesize(
    search_results: list[str] = Field(description="Search results to synthesize"),
) -> str:
    """Returns: Synthesized text with inline citations."""
    summary = " ".join(
        f"{text} [{idx}]" for idx, text in enumerate(search_results, start=1)
    )
    return summary


@server.tool(description="Analyze synthesized content for insights")
async def analyze(
    synthesized_content: str = Field(description="Synthesized text to analyze"),
    user_query: str = Field(description="User query defining the analysis focus"),
) -> str:
    """Returns: Analysis results based on the user query."""
    return dedent(
        f"""
        You are an expert analyst.
        Analyze the synthesized content with respect to the user query.

        User Query: {user_query}
        Content: {synthesized_content}
        """
    )


if __name__ == "__main__":
    server.run(
        transport=config.transport,
        host=config.host,
        port=config.port,
    )
