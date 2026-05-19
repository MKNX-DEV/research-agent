import logging
from typing import Any, TypeVar

from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models import Model
from config import AgentConfig

logger = logging.getLogger(__name__)

DepsT = TypeVar("DepsT")

class ResearchAgent:
	def __init__(
		self,
		config: AgentConfig,
		model: Model,
		system_prompt: str,
		mcp_server: str | None = None,
	):
		self.config = config
		self.model = model
		self.system_prompt = system_prompt
		self.mcp_server = mcp_server

	def _build_agent(
		self, deps_type: type[DepsT], output_type: Any
	) -> Agent[DepsT, Any]:
		mcp_server_connection = self._connect_to_mcp_server()

		agent: Agent[Any, Any] = Agent(
			model=self.model,
			system_prompt=self.system_prompt,
			toolsets=mcp_server_connection,
			deps_type=deps_type,
			output_type=output_type,
			retries=self.config.retries,
		)

		return agent

	def _connect_to_mcp_server(self) -> list[MCPServerStreamableHTTP] | None:
		if self.mcp_server:
			server = MCPServerStreamableHTTP('http://localhost:8000/mcp')
			return [server]
		return None

	async def run(self, query: str) -> None:
		agent = self._build_agent()
		logger.info("Input classification agent has been initialized")

		async with agent:
			response = await agent.run(query)
		logger.info("Input classification is completed")

		logger.debug(f"Input Classification Agent messages: {response.all_messages()}")
		input_classification = response.output

		logger.debug(
			f"Input classification result: {input_classification.model_dump()}"
		)
		return input_classification