"""Construct the research agent."""

import logging
from typing import Generic, TypeVar

from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.models import AgentDeps, ResearchAgentOutput, ResearchEndpointOutput
from research_agent.settings import Settings

logger = logging.getLogger(__name__)
DepsT = TypeVar("DepsT", bound=AgentDeps)
OutputT = TypeVar("OutputT", bound=ResearchAgentOutput)


class OutputComposer:
    @staticmethod
    def build_empty_output() -> ResearchEndpointOutput:
        return ResearchEndpointOutput(
            research_output=None,
            status="no_result",
            reason="No results matching the user query",
        )

    @staticmethod
    def build_success_output(data: str) -> ResearchEndpointOutput:
        return ResearchEndpointOutput(
            research_output=data, status="success", reason=None
        )

    @staticmethod
    def build_error_output(
        e: Exception, msg: str | None = None
    ) -> ResearchEndpointOutput:
        msg = msg or "Search execution failed."
        logger.exception(msg, exc_info=e)
        return ResearchEndpointOutput(
            research_output=None, status="error", reason="Internal processing error"
        )


class ResearchAgent(Generic[DepsT, OutputT]):
    def __init__(
        self,
        settings: Settings,
        model: Model,
        instructions: str,
        toolset: MCPToolset[DepsT],
        deps_type: type[DepsT],
        output_type: type[OutputT],
        output_composer: type[OutputComposer],
    ):
        self.settings = settings
        self.model = model
        self.instructions = instructions
        self.toolset = toolset
        self.deps_type = deps_type
        self.output_type = output_type
        self.output_composer = output_composer

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
        def _add_toolset_info(ctx: RunContext[DepsT]) -> str:
            return f"The mcp server tools are {ctx.deps.mcp_toolset_info}."

        @agent.system_prompt
        def _add_user_requirements(ctx: RunContext[DepsT]) -> str:
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

            research_output = response.output.research_output

            if not research_output:
                return self.output_composer.build_empty_output()

            return self.output_composer.build_success_output(research_output)

        except ModelHTTPError as e:
            return self.output_composer.build_error_output(
                e=e, msg="Model connection failed."
            )

        except RuntimeError as e:
            if "All connection attempts failed" in str(e):
                return self.output_composer.build_error_output(
                    e=e, msg="MCP connection failed."
                )
            return self.output_composer.build_error_output(e)

        except Exception as e:
            return self.output_composer.build_error_output(e)
