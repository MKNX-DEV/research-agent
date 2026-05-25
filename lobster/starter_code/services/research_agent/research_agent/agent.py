import logging

from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.models import AgentDeps, ResearchEndpointOutput
from research_agent.settings import Settings

logger = logging.getLogger(__name__)


def build_agent(
    model: Model,
    prompt: str,
    toolset: MCPToolset,
    settings: Settings,
    output_type,
    deps_type,
) -> Agent:
    agent = Agent(
        model=model,
        system_prompt=prompt,
        toolsets=[toolset],
        retries=settings.RETRIES,
        output_type=output_type,
        deps_type=deps_type,
    )

    @agent.system_prompt
    def _supply_toolset_info(ctx: RunContext[AgentDeps]) -> str:
        return f"The mcp server tools are {ctx.deps.mcp_toolset_info}."

    @agent.system_prompt
    def _add_context(ctx: RunContext[AgentDeps]) -> str:
        return f"""
        Preferred Sources: {ctx.deps.sources}
        Maximum Results: {ctx.deps.max_results}
        """

    return agent


class OutputComposer:
    @staticmethod
    def build_unknown_error_output(error_msg: str) -> ResearchEndpointOutput:
        return ResearchEndpointOutput(
            research_output=None,
            status="error",
            reason=error_msg,
            message="Internal processing error.",
        )

    @staticmethod
    def build_output(data) -> ResearchEndpointOutput:
        return ResearchEndpointOutput(
            research_output=data,
            status="success",
            reason="",
            message="Research completed",
        )

    @classmethod
    def handle_search_error(cls, e: Exception | RuntimeError) -> ResearchEndpointOutput:
        error_msg = str(e)
        logger.error(f"Agent execution error: {error_msg}")
        root_cause = e.__cause__ if e.__cause__ else e
        error_msg = str(root_cause)
        logger.error(f"Error in MCP server: {error_msg}")
        return cls.build_unknown_error_output(error_msg)
