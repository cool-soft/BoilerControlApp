import logging.handlers
import sys

from app_configs import LoggingConfig


def setup_default_logger_from_config(config: LoggingConfig):
    logging_handlers = (
        logging.handlers.RotatingFileHandler(
            filename=config.path,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count
        ),
        logging.StreamHandler(
            stream=sys.stderr
        )
    )
    # noinspection PyArgumentList
    logging.basicConfig(
        level=config.level,
        datefmt=config.datetime_format,
        format=config.format,
        handlers=logging_handlers
    )
