import logging
from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class LoggingMiddleware(Middleware):
    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next: Callable[[MiddlewareContext], Awaitable[Any]],
    ) -> Any:
        tool_name = context.message.name
        args = context.message.arguments
        log_message = f"Called MCP tool {tool_name}."
        logger.info(log_message)
        logger.debug(f"Passed tool arguments {args}")

        if context.fastmcp_context is not None:
            await context.fastmcp_context.info(log_message)

        return await call_next(context)
