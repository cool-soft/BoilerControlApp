import logging

from pydantic import BaseModel


class LoggingConfig(BaseModel):
    path: str = "../logs/log.log"
    max_bytes: int = 102400
    backup_count = 5
    level: str = logging.DEBUG
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    # noinspection SpellCheckingInspection
    format: str = "[%(asctime)s] %(levelname)s - %(message)s"
