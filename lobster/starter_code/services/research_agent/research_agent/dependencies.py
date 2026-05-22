from fastapi import Request
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.config import AgentConfig


def get_agent_config(request: Request) -> AgentConfig:
    return request.app.state.agent_config


def get_model(request: Request) -> Model:
    return request.app.state.model


def get_mcp_server(request: Request) -> MCPToolset:
    return request.app.state.mcp_server


def get_mcp_tool_names(request: Request) -> list:
    return request.app.state.mcp_tool_names
