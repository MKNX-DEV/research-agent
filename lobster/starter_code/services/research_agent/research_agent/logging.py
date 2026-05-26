import logging

from fastmcp.client.logging import LogMessage
from uvicorn.logging import DefaultFormatter

from research_agent.settings import LoggingSettings

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


async def log_handler(message: LogMessage) -> None:
    """Receive structured logs emitted by the MCP server."""
    msg = message.data.get("msg")
    extra = message.data.get("extra")
    LOGGING_LEVEL_MAP = logging.getLevelNamesMapping()
    level = LOGGING_LEVEL_MAP.get(message.level.upper(), logging.INFO)
    logger.log(level, msg, extra=extra)
