from fastapi import Request
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.config import AgentConfig


def get_agent_config(request: Request) -> AgentConfig:
    return request.app.state.agent_config


def get_model(request: Request) -> Model:
    return request.app.state.model


def get_mcp_toolset(request: Request) -> MCPToolset:
    return request.app.state.mcp_toolset


def get_mcp_tool_info(request: Request) -> list:
    return request.app.state.mcp_tool_info
