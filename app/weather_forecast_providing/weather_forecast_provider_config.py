from pydantic import BaseModel


class WeatherForecastProviderConfig(BaseModel):
    server_address: str = "https://lysva.agt.town/"
    server_timezone: str = "Asia/Yekaterinburg"
    update_interval: int = 600
