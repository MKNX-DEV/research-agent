import logging

from fastmcp.server.middleware import Middleware, MiddlewareContext
from uvicorn.logging import DefaultFormatter

from research_tools.settings import LoggingSettings

logger = logging.getLogger(__name__)


def configure_logger(title: str) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(
        DefaultFormatter(
            fmt="%(levelprefix)s %(name)s: %(message)s",
            use_colors=True,
        )
    )

    logger = logging.getLogger(title)
    logger.setLevel(level=getattr(logging, LoggingSettings().LOG_LEVEL))
    logger.addHandler(handler)
    return logger


class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        args = context.message.arguments
        log_message = f"Called MCP tool {tool_name}."
        logger.info(log_message)
        logger.debug(f"Passed tool arguments {args}")
        await context.fastmcp_context.info(log_message)
        result = await call_next(context)
        return result
