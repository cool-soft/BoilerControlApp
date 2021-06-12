from datetime import datetime

from pydantic import BaseModel


class ControlActionV3(BaseModel):
    timestamp: datetime
    forward_temp: float
