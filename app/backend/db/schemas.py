from datetime import datetime
from pydantic import BaseModel


class WeatherData(BaseModel):
    d_timestamp: datetime
    t: float = None


class PredictedData(BaseModel):
    timestamp: datetime
    forward_temp: float = None
    circuit_type: str = ""
