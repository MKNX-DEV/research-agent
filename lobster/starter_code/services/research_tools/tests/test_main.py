from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

from research_tools.main import server
from research_tools.search import SearchEngine
from research_tools.models import SearchOutput


@pytest_asyncio.fixture
async def main_mcp_client():
    async with Client(transport=server) as mcp_client:
        yield mcp_client


def test_health_check():
    client = TestClient(server.http_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_list_tools(main_mcp_client: Client[FastMCPTransport]):
    list_tools = await main_mcp_client.list_tools()
    assert len(list_tools) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("mock_data", "expected_output", "found_results"),
    [
        (
            {
                "books": [
                    {
                        "title": "Machine Learning Basics",
                        "content": "Introduction to neural networks",
                        "source": "books",
                    },
                    {
                        "title": "Cooking Pasta",
                        "content": "Italian recipes",
                        "source": "books",
                    },
                    {
                        "title": "Deep Learning",
                        "content": "Advanced machine learning techniques",
                        "source": "books",
                    },
                ]
            },
            [
                "Machine Learning Basics: Introduction to neural networks",
                "Deep Learning: Advanced machine learning techniques",
            ],
            True,
        ),
        (
            {
                "books": [
                    {
                        "title": "Cooking Pasta",
                        "content": "Italian recipes",
                        "source": "books",
                    },
                ]
            },
            None,
            False,
        ),
    ],
)
async def test_search_tool(
    monkeypatch,
    main_mcp_client,
    mock_data,
    expected_output,
    found_results,
):
    def mock_read(self, data: Path):
        return mock_data

    monkeypatch.setattr(SearchEngine, "_read", mock_read)

    result = await main_mcp_client.call_tool(
        "search",
        {
            "input": {
                "sources": ["books"],
                "keyword": "learning",
                "max_results": 2,
            }
        },
    )

    assert result.structured_content["search_output"] == expected_output
    assert result.structured_content["found_results"] is found_results


@pytest.mark.asyncio
async def test_synthesize_tool(main_mcp_client):
    search_output = [
        "Machine Learning Basics: Introduction to neural networks",
        "Deep Learning: Advanced machine learning techniques",
    ]

    result = await main_mcp_client.call_tool(
        "synthesize",
        {
            "input": {
                "search_output": search_output,
            }
        },
    )

    expected = (
        "Machine Learning Basics: Introduction to neural networks [1] "
        "Deep Learning: Advanced machine learning techniques [2]"
    )

    assert (
        result.structured_content["synthesize_output"]
        == expected
    )