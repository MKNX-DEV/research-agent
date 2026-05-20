import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI  # , HTTPException
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.github import GitHubProvider

from research_agent.config import AgentConfig
from research_agent.interfaces import AgentDeps

logger = logging.getLogger(__name__)


def connect_to_model(config: AgentConfig) -> Model:
    model = OpenAIChatModel(
        model_name=config.llm_name,
        provider=GitHubProvider(api_key=config.api_key),
    )
    return model


def connect_to_mcp(config: AgentConfig) -> MCPToolset:
    return MCPToolset(config.mcp_url)


def build_agent(
    model: Model,
    prompt: str,
    mcp_server: MCPToolset,
    config: AgentConfig,
    output_type,
    deps_type,
) -> Agent:
    agent = Agent(
        model=model,
        system_prompt=prompt,
        toolsets=[mcp_server],
        retries=config.retries,
        output_type=output_type,
        deps_type=deps_type,
    )

    @agent.system_prompt
    def inject_tool_names(ctx: RunContext[AgentDeps]) -> str:
        return f"The mcp server tools are {ctx.deps.mcp_tools}."

    return agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent_config = AgentConfig()
    app.state.model = connect_to_model(app.state.agent_config)
    app.state.mcp_server = connect_to_mcp(app.state.agent_config)

    async with app.state.mcp_server:
        app.state.mcp_tool_names = await app.state.mcp_server.list_tools()

    logger.info(f"Available MCP tools are: {app.state.mcp_tool_names}")

    yield
