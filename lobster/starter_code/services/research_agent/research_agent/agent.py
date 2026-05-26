import logging
from typing import Generic, TypeVar

from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.models import AgentDeps, ResearchAgentOutput, ResearchEndpointOutput
from research_agent.settings import Settings

logger = logging.getLogger(__name__)
DepsT = TypeVar("DepsT", bound=AgentDeps)
OutputT = TypeVar("OutputT", bound=ResearchAgentOutput)


class OutputComposer:
    @staticmethod
    def build_unknown_error_output(error_msg: str) -> ResearchEndpointOutput:
        return ResearchEndpointOutput(
            research_output=None, status="error", reason=error_msg
        )

    @staticmethod
    def build_output(data: str) -> ResearchEndpointOutput:
        return ResearchEndpointOutput(
            research_output=data, status="success", reason=None
        )

    @classmethod
    def handle_search_error(cls, e: Exception | RuntimeError) -> ResearchEndpointOutput:
        error_msg = str(e)
        logger.error(f"Agent execution error: {error_msg}")
        root_cause = e.__cause__ if e.__cause__ else e
        error_msg = str(root_cause)
        logger.error(f"Error in MCP server: {error_msg}")
        return cls.build_unknown_error_output(error_msg)


class ResearchAgent(Generic[DepsT, OutputT]):
    def __init__(
        self,
        settings: Settings,
        model: Model,
        instructions: str,
        toolset: MCPToolset[DepsT],
        deps_type: type[DepsT],
        output_type: type[OutputT],
        output_composer: OutputComposer,
    ):
        self.settings = settings
        self.model = model
        self.instructions = instructions
        self.toolset = toolset
        self.deps_type = deps_type
        self.output_type = output_type
        self.output_compser = output_composer

    def _build_agent(self) -> Agent[DepsT, OutputT]:
        agent = Agent[DepsT, OutputT](
            model=self.model,
            instructions=self.instructions,
            toolsets=[self.toolset],
            retries=self.settings.RETRIES,
            output_type=self.output_type,
            deps_type=self.deps_type,
        )

        @agent.system_prompt
        def _supply_toolset_info(ctx: RunContext[DepsT]) -> str:
            return f"The mcp server tools are {ctx.deps.mcp_toolset_info}."

        @agent.system_prompt
        def _add_context(ctx: RunContext[DepsT]) -> str:
            return f"""
            Preferred Sources: {ctx.deps.sources}
            Maximum Results: {ctx.deps.max_results}
            """

        return agent

    async def run(self, query: str, deps: DepsT) -> ResearchEndpointOutput:
        agent = self._build_agent()
        try:
            async with agent:
                response = await agent.run(query, deps=deps)
            return self.output_compser.build_output(
                data=response.output.research_output
            )

        except Exception as e:
            return self.output_compser.handle_search_error(e)
