from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ControlActionV3(BaseModel):
    timestamp: datetime
    circuit_type: str
    forward_temp: float


class SettingV3(BaseModel):
    name: str
    value: Any
