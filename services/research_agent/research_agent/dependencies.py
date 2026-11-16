"""Dependency injection utilities."""

from fastapi import Request
from mcp.types import Tool
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models import Model

from research_agent.settings import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_model(request: Request) -> Model:
    return request.app.state.model


def get_mcp_client(request: Request) -> MCPToolset:
    return request.app.state.mcp_client


def get_mcp_toolset_info(request: Request) -> list[Tool]:
    return request.app.state.mcp_toolset_info
