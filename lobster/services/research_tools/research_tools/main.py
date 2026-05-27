"""Application entrypoint exposing the FastMCP endpoints."""

from textwrap import dedent

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from shared_libs.utils import configure_logger, load_settings

from research_tools.exceptions import DatasetNotAvailableError
from research_tools.logging import LoggingMiddleware
from research_tools.models import (
    AnalyzeParameters,
    SearchOutput,
    SearchParameters,
    SynthesizeOutput,
    SynthesizeParameters,
)
from research_tools.search import SearchEngine
from research_tools.settings import MCPSettings

settings = load_settings(MCPSettings)
logger = configure_logger(title="research_tools", log_level=settings.LOG_LEVEL)
server = FastMCP(name=settings.SERVER_NAME, on_duplicate=settings.ON_DUPLICATE)

server.add_middleware(
    ErrorHandlingMiddleware(include_traceback=True, transform_errors=True)
)

server.add_middleware(LoggingMiddleware())


@server.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


@server.tool(description="Search the dataset for user-requested information.")
async def search(input: SearchParameters) -> SearchOutput:

    try:
        engine = SearchEngine(
            keyword=input.keyword, sources=input.sources, max_results=input.max_results
        )

        results = engine.search(settings.DATA)
        found_results = bool(results)
        return SearchOutput(search_output=results, found_results=found_results)

    except DatasetNotAvailableError:
        msg = "Input dataset not found"
        logger.exception(msg)
        raise ToolError(msg)


@server.tool(description="Combine multiple search results into a coherent summary")
async def synthesize(input: SynthesizeParameters) -> SynthesizeOutput:

    summary = " ".join(
        f"{text} [{idx}]" for idx, text in enumerate(input.search_output, start=1)
    )

    logger.info("Synthesis complete")
    return SynthesizeOutput(synthesize_output=summary)


@server.tool(description="Analyze synthesized content for insights")
async def analyze(input: AnalyzeParameters, ctx: Context) -> str | None:
    result = await ctx.sample(
        messages=input.user_query,
        system_prompt=dedent(
            f"""
            You are an expert analyst.
            Analyze the synthesized content for insights with respect to the user query.
            The synthesized content: {input.synthesize_output}
            """,
        ),
    )

    return result.text


if __name__ == "__main__":
    server.run(
        transport=settings.TRANSPORT,
        host=settings.HOST,
        port=settings.PORT,
    )
