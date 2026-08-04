import logging
from typing import Literal, TypeVar

from pydantic import ValidationError
from pydantic_settings import BaseSettings
from uvicorn.logging import DefaultFormatter

from shared_libs.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseSettings)


def load_settings(settings_cls: type[T]) -> T:
    try:
        loaded_settings = settings_cls()
        logger.info(f"Application configuration loaded for {settings_cls.__name__}")
        return loaded_settings

    except ValidationError as e:
        invalid_fields = [".".join(map(str, err["loc"])) for err in e.errors()]

        msg = f"Invalid configuration: {invalid_fields}"
        logger.exception(msg)
        raise ConfigurationError(msg) from e


def configure_logger(title: str, log_level: Literal["DEBUG", "INFO"]) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(
        DefaultFormatter(
            fmt="%(levelprefix)s %(name)s: %(message)s",
            use_colors=True,
        )
    )

    logger = logging.getLogger(title)
    logger.setLevel(level=getattr(logging, log_level))
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
