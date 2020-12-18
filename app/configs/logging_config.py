from pydantic import BaseModel


class LoggingConfig(BaseModel):
    path: str = "../logs/log.log"
    level: str = "DEBUG"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    # noinspection SpellCheckingInspection
    format: str = "[%(asctime)s] %(levelname)s - %(message)s"
