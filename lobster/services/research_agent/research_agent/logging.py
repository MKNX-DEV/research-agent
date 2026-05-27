import logging

from fastmcp.client.logging import LogMessage

logger = logging.getLogger(__name__)


async def log_handler(message: LogMessage) -> None:
    """Receive structured logs emitted by the MCP server."""
    msg = message.data.get("msg")
    extra = message.data.get("extra")
    LOGGING_LEVEL_MAP = logging.getLevelNamesMapping()
    level = LOGGING_LEVEL_MAP.get(message.level.upper(), logging.INFO)
    logger.log(level, msg, extra=extra)
