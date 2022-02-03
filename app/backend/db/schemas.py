from datetime import datetime
from pydantic import BaseModel


class PredictedData(BaseModel):
    timestamp: datetime
    forward_temp: float = None
    circuit_type: str = ""
