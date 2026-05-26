import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from research_agent.clients import (
    create_mcp_client,
    create_model_client,
    log_handler,
    query_mcp_toolset_info,
    verify_mcp_connection,
)
from research_agent.settings import load_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.settings = load_settings()
        app.state.model = create_model_client(app.state.settings)

        app.state.mcp_client = create_mcp_client(
            settings=app.state.settings,
            log_handler=log_handler,
            sampling_model=app.state.model,
        )

        await verify_mcp_connection(app.state.mcp_client)
        app.state.mcp_toolset_info = await query_mcp_toolset_info(app.state.mcp_client)

        yield

    except Exception:
        logger.exception("Application startup failed")
