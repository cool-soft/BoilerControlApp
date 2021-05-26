from datetime import datetime

from pydantic import BaseModel


class ControlAction(BaseModel):
    timestamp: datetime
    forward_temp: float
