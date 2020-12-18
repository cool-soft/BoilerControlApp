from pydantic import BaseModel


class ServiceConfig(BaseModel):
    port: int = 270
    host: str = "0.0.0.0"