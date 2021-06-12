from typing import Any

from pydantic import BaseModel


class SettingV3(BaseModel):
    name: str
    value: Any
