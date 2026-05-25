import logging

from fastmcp import Client
from fastmcp.client.logging import LogMessage
from fastmcp.client.sampling import RequestContext, SamplingMessage, SamplingParams
from fastmcp.client.transports import StreamableHttpTransport
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.github import GitHubProvider

from research_agent.exceptions import (
    MCPConnectionError,
    ModelConnectionError,
)
from research_agent.settings import Settings

logger = logging.getLogger(__name__)


def create_model_client(settings: Settings) -> Model:
    try:
        model = OpenAIChatModel(
            model_name=settings.LLM_NAME,
            provider=GitHubProvider(api_key=settings.API_KEY.get_secret_value()),
        )

        logger.info(f"Initialized model client for the {settings.LLM_NAME} model")
        return model

    except Exception as e:
        logger.error("Failed to initialize model client")

        raise ModelConnectionError(
            f"Could not initialize model {settings.LLM_NAME}"
        ) from e


def create_mcp_client(
    settings: Settings, log_handler, sampling_model: Model
) -> MCPToolset:
    try:
        client = Client(
            StreamableHttpTransport(settings.MCP_SERVER_URL),
            log_handler=log_handler,
            sampling_handler=SamplingHandler(sampling_model),
        )
        toolset = MCPToolset(client)
        logger.info(
            f"Initialized MCP client for MCP server at {settings.MCP_SERVER_URL}"
        )
        return toolset

    except Exception as e:
        logger.error("Failed to initialize MCP client")
        raise MCPConnectionError(
            f"Could not initialize MCP client for MCP server at {settings.MCP_SERVER_URL}"
        ) from e


async def verify_mcp_connection(toolset: MCPToolset) -> None:
    try:
        async with toolset:
            await toolset.client.ping()
        logger.info("Verified the MCP server connection")

    except Exception as e:
        logger.error("Failed to connect to MCP server")
        raise MCPConnectionError("Could not connect to MCP server") from e


async def query_mcp_toolset_info(client: MCPToolset) -> list:
    try:
        async with client:
            mcp_tool_info = await client.list_tools()
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
    LOGGING_LEVEL_MAP = logging.getLevelNamesMapping()
    level = LOGGING_LEVEL_MAP.get(message.level.upper(), logging.INFO)
    logger.log(level, msg, extra=extra)


class SamplingHandler:
    def __init__(self, model: Model):
        self._model = model

    async def __call__(
        self,
        messages: list[SamplingMessage],
        params: SamplingParams,
        context: RequestContext,
    ) -> str:
        system_prompt = params.systemPrompt or "You are a helpful assistant."
        agent = Agent(self._model, system_prompt=system_prompt)

        user_query = "\n".join(
            m.content.text for m in messages if hasattr(m.content, "text")
        )

        result = await agent.run(user_query)
        return result.output
