from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

from research_tools.main import mcp_server
from research_tools.utils import SearchEngine


@pytest_asyncio.fixture
async def main_mcp_client():
    async with Client(transport=mcp_server) as mcp_client:
        yield mcp_client


def test_health_check():
    client = TestClient(mcp_server.http_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_list_tools(main_mcp_client: Client[FastMCPTransport]):
    list_tools = await main_mcp_client.list_tools()
    assert len(list_tools) == 3


@pytest.mark.asyncio
async def test_search_tool(monkeypatch, main_mcp_client):
    expected = [
        {
            "title": "Machine Learning Basics",
            "description": "Introduction to neural networks",
        },
        {
            "title": "Deep Learning",
            "description": "Advanced machine learning techniques",
        },
    ]

    def mock_read(self, data: Path):
        return [
            {
                "title": "Machine Learning Basics",
                "description": "Introduction to neural networks",
            },
            {
                "title": "Cooking Pasta",
                "description": "Italian recipes",
            },
            {
                "title": "Deep Learning",
                "description": "Advanced machine learning techniques",
            },
        ]

    monkeypatch.setattr(SearchEngine, "_read", mock_read)

    result = await main_mcp_client.call_tool(
        "search",
        {
            "sources": "books",
            "query": "learning",
            "max_results": 2,
        },
    )

    assert result.data == expected


@pytest.mark.asyncio
async def test_synthesize_tool(main_mcp_client):
    search_results = [
        {
            "title": "Machine Learning Basics",
            "description": "Introduction to neural networks",
        },
        {
            "title": "Deep Learning",
            "description": "Advanced machine learning techniques",
        },
    ]

    result = await main_mcp_client.call_tool(
        "synthesize",
        {
            "search_results": search_results,
        },
    )

    expected = (
        "Machine Learning Basics: Introduction to neural networks [1] "
        "Deep Learning: Advanced machine learning techniques [2]"
    )

    # Since the tool returns `str`, FastMCP exposes the output directly.
    assert result.data == expected


@pytest.mark.asyncio
async def test_analyze_tool(main_mcp_client):
    synthesized_content = (
        "Machine Learning Basics: Introduction to neural networks [1] "
        "Deep Learning: Advanced machine learning techniques [2]"
    )
    user_query = "What are the main themes discussed?"

    result = await main_mcp_client.call_tool(
        "analyze",
        {
            "synthesized_content": synthesized_content,
            "user_query": user_query,
        },
    )

    expected = f"""
        You are an expert analyst.

        Analyze the synthesized content with respect to the user query.

        User Query:
        {user_query}

        Content:
        {synthesized_content}
    """

    # Normalize leading/trailing whitespace introduced by the triple-quoted string.
    assert result.data.strip() == expected.strip()
