"""
Research Tool Service

This is a template - feel free to completely rewrite or restructure as needed.
This service exposes tools via MCP protocol for agents to use.
"""

from textwrap import dedent

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

from research_tools.exceptions import DatasetNotAvailableError, NoSearchResultsError
from research_tools.models import (
    # AnalyzeOutput,
    AnalyzeParameters,
    SearchOutput,
    SearchParameters,
    SynthesizeOutput,
    SynthesizeParameters,
)
from research_tools.utils import (
    LoggingMiddleware,
    SearchEngine,
    configure_logger,
    load_config,
)

logger = configure_logger("research_tools")
config = load_config()
server = FastMCP(name=config.server_name, on_duplicate=config.on_duplicate)

server.add_middleware(
    ErrorHandlingMiddleware(include_traceback=True, transform_errors=True)
)

server.add_middleware(LoggingMiddleware())


@server.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


@server.tool(description="Search the dataset for user-requested information")
async def search(input: SearchParameters) -> SearchOutput:

    try:
        engine = SearchEngine(
            keyword=input.keyword, sources=input.sources, max_results=input.max_results
        )

        results = engine.search(data=config.data)
        logger.info(f"Found research data: {results[:2]}")
        return SearchOutput(search_output=results)

    except DatasetNotAvailableError:
        msg = "Input dataset not found"
        logger.error(msg)
        raise ToolError(msg)

    except NoSearchResultsError:
        msg = "No matching data for the user input"
        logger.error(msg)
        raise ToolError(msg)


@server.tool(description="Combine multiple search results into a coherent summary")
async def synthesize(input: SynthesizeParameters) -> SynthesizeOutput:

    summary = " ".join(
        f"{text} [{idx}]" for idx, text in enumerate(input.search_output, start=1)
    )

    logger.info("Synthesis complete")
    return SynthesizeOutput(synthesize_output=summary)


@server.tool(description="Analyze synthesized content for insights")
async def analyze(input: AnalyzeParameters, ctx: Context) -> str:  # AnalyzeOutput:
    result = await ctx.sample(
        messages=input.user_query,
        system_prompt=dedent(
            f"""
            You are an expert analyst.
            Analyze the synthesized content for insights with respect to the user query.
            The synthesized content: {input.synthesize_output}
            """,
        ),
        # result_type=AnalyzeOutput,
    )

    # return result.result
    return result.text


if __name__ == "__main__":
    server.run(
        transport=config.transport,
        host=config.host,
        port=config.port,
    )
