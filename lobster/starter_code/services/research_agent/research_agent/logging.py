import logging

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
