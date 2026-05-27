"""Client configuration and validation for the model and MCP services."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp import Client
from fastmcp.client.logging import LogMessage
from fastmcp.client.sampling import RequestContext, SamplingMessage, SamplingParams
from fastmcp.client.transports import StreamableHttpTransport
from mcp.types import TextContent, Tool
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.github import GitHubProvider

from research_agent.exceptions import (
    MCPClientError,
    MCPServerConnectionError,
    ModelClientError,
)
from research_agent.models import AgentDeps
from research_agent.settings import Settings

logger = logging.getLogger(__name__)


def create_model_client(settings: Settings) -> Model[Any]:
    try:
        model = OpenAIChatModel(
            model_name=settings.LLM_NAME,
            provider=GitHubProvider(
                api_key=settings.GITHUB_MODELS_API_GPT_4_O_MINI.get_secret_value()
            ),
        )

        logger.info(f"Initialized model client for the {settings.LLM_NAME} model")
        return model

    except Exception as e:
        msg = f"Failed to initialize model client for {settings.LLM_NAME}"
        logger.exception(msg)
        raise ModelClientError(msg) from e


def create_mcp_client(
    settings: Settings,
    log_handler: Callable[[LogMessage], Awaitable[None]],
    sampling_model: Model,
) -> MCPToolset[AgentDeps]:
    try:
        client = Client(
            StreamableHttpTransport(settings.MCP_SERVER_URL),
            log_handler=log_handler,
            sampling_handler=SamplingHandler(sampling_model),
        )
        toolset = MCPToolset[AgentDeps](client)
        logger.info(
            f"Initialized MCP client for MCP server at {settings.MCP_SERVER_URL}"
        )
        return toolset

    except Exception as e:
        msg = f"Could not initialize MCP client for MCP server at {settings.MCP_SERVER_URL}"
        logger.exception(msg)
        raise MCPClientError(msg) from e


async def verify_mcp_connection(toolset: MCPToolset[AgentDeps]) -> None:
    try:
        async with toolset:
            await toolset.client.ping()
        logger.info("Verified the MCP server connection")

    except Exception as e:
        msg = "Failed to connect to MCP server"
        logger.exception(msg)
        raise MCPServerConnectionError(msg) from e


async def query_mcp_toolset_info(client: MCPToolset[AgentDeps]) -> list[Tool]:
    try:
        async with client:
            mcp_tool_info = await client.list_tools()
        tool_names = [tool.name for tool in mcp_tool_info]
        logger.info(f"Retrieved {len(mcp_tool_info)} MCP tools: {tool_names}")
        return mcp_tool_info

    except Exception as e:
        msg = "Failed to retrieve MCP tools"
        logger.exception(msg)
        raise MCPServerConnectionError(msg) from e


class SamplingHandler:
    def __init__(self, model: Model):
        self._model = model

    async def __call__(
        self,
        messages: list[SamplingMessage],
        params: SamplingParams,
        context: RequestContext[Any, Any],
    ) -> str:
        system_prompt = params.systemPrompt or "You are a helpful assistant."
        agent = Agent(self._model, system_prompt=system_prompt)

        user_query = "\n".join(
            m.content.text for m in messages if isinstance(m.content, TextContent)
        )

        logger.info(f"Calling MCP sampling with the message: {user_query}")
        result = await agent.run(user_query)
        return result.output
