from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ControlActionAPIModel(BaseModel):
    timestamp: datetime
    circuit_type: str
    forward_temp: float


class SettingAPIModel(BaseModel):
    name: str
    value: Any
