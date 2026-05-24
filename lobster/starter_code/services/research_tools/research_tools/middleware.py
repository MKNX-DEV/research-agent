import logging

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        args = context.message.arguments
        log_message = f"Called MCP tool {tool_name} with arguments {args}"
        logger.info(log_message)
        await context.fastmcp_context.info(log_message)
        result = await call_next(context)
        return result
