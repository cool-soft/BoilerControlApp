from typing import Any

from pydantic import BaseModel


class Setting(BaseModel):
    name: str
    value: Any
