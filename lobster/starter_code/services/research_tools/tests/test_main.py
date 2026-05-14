import pytest
import pytest_asyncio
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastapi.testclient import TestClient

from research_tools.main import mcp_server

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
    assert len(list_tools) == 0

@pytest.mark.asyncio
async def test_list_resources(main_mcp_client: Client[FastMCPTransport]):
    templates = await main_mcp_client.list_resource_templates()
    template_uris = [str(template.uriTemplate) for template in templates]
    assert "data://research_data/{sources}" in template_uris

# @pytest.mark.asyncio
# async def test_read_research_data_resource(main_mcp_client: Client[FastMCPTransport]):
#     result = await main_mcp_client.read_resource("data://research_data")
#     #assert isinstance(result, dict)
#     assert result is not None

@pytest.mark.asyncio
async def test_read_research_data_resource(
    main_mcp_client: Client[FastMCPTransport],
):
    result = await main_mcp_client.read_resource(
        "data://research_data/renewable_energy_storage"
    )

    content = result[0]
    import json
    data = json.loads(content.text)
    assert data["source"] == "renewable_energy_storage"
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0
    assert "title" in data["results"][0]