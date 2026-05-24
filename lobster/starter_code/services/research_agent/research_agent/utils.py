import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI  # , HTTPException
from fastmcp import Client
from fastmcp.client.logging import LogMessage
from fastmcp.client.transports import StreamableHttpTransport
from pydantic import ValidationError
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.github import GitHubProvider

from research_agent.config import AgentConfig
from research_agent.exceptions import (
    ConfigurationError,
    MCPConnectionError,
    ModelConnectionError,
)
from research_agent.models import AgentDeps

logger = logging.getLogger(__name__)
LOGGING_LEVEL_MAP = logging.getLevelNamesMapping()


def load_config() -> AgentConfig:
    try:
        config = AgentConfig()
        logger.info("Application configuration loaded")
        return config

    except ValidationError as e:
        invalid_fields = [".".join(map(str, err["loc"])) for err in e.errors()]
        logger.error(f"Invalid configuration: {invalid_fields}")
        raise ConfigurationError("Missing or invalid environment variables") from e


def create_model_client(config: AgentConfig) -> Model:
    try:
        model = OpenAIChatModel(
            model_name=config.llm_name,
            provider=GitHubProvider(api_key=config.api_key.get_secret_value()),
        )

        logger.info(f"Initialized model client for the {config.llm_name} model")
        return model

    except Exception as e:
        logger.error("Failed to initialize model client")

        raise ModelConnectionError(
            f"Could not initialize model {config.llm_name}"
        ) from e


def create_mcp_toolset(config: AgentConfig, log_handler) -> MCPToolset:
    try:
        client = Client(
            StreamableHttpTransport(config.mcp_url),
            log_handler=log_handler,
        )
        toolset = MCPToolset(client)
        logger.info(f"Initialized MCP client for MCP server at {config.mcp_url}")
        return toolset

    except Exception as e:
        logger.error("Failed to initialize MCP client")
        raise MCPConnectionError(
            f"Could not initialize MCP client for MCP server at {config.mcp_url}"
        ) from e


async def verify_mcp_connection(toolset: MCPToolset) -> None:
    try:
        await toolset.client.ping()
        logger.info("Connected to MCP server")

    except Exception as e:
        logger.error("Failed to connect to MCP server")
        raise MCPConnectionError("Could not connect to MCP server") from e


async def get_mcp_tool_info(toolset: MCPToolset) -> list:
    try:
        mcp_tool_info = await toolset.list_tools()
        tool_names = [tool.name for tool in mcp_tool_info]
        logger.info(f"Retrieved {len(mcp_tool_info)} MCP tools. They are: {tool_names}")
        return mcp_tool_info

    except Exception as e:
        logger.error("Failed to retrieve MCP tools")
        raise MCPConnectionError("Unable to retrieve MCP tools") from e


async def log_handler(message: LogMessage) -> None:
    """Receive structured logs emitted by the MCP server."""
    msg = message.data.get("msg")
    extra = message.data.get("extra")
    level = LOGGING_LEVEL_MAP.get(message.level.upper(), logging.INFO)
    logger.log(level, msg, extra=extra)


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
    def _supply_tool_names(ctx: RunContext[AgentDeps]) -> str:
        return f"The mcp server tools are {ctx.deps.mcp_tools}."

    @agent.system_prompt
    def _add_context(ctx: RunContext[AgentDeps]) -> str:
        return f"""
        Preferred Sources: {ctx.deps.sources}
        Maximum Results: {ctx.deps.max_results}
        """

    return agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.agent_config = load_config()
        app.state.model = create_model_client(app.state.agent_config)

        app.state.mcp_toolset = create_mcp_toolset(
            config=app.state.agent_config, log_handler=log_handler
        )

        async with app.state.mcp_toolset:
            await verify_mcp_connection(app.state.mcp_toolset)
            app.state.mcp_tool_info = await get_mcp_tool_info(app.state.mcp_toolset)

        logger.info("Application startup completed")
        yield

    except Exception:
        logger.error("Application startup failed")
