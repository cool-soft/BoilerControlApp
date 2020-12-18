from pydantic import BaseModel

from configs.weather_forecast_provider_config import WeatherForecastProviderConfig


class BoilerTPredictorConfig(BaseModel):
    home_t_dispersion_coefficient: float = 0.97
    t_graph_path: str = "../../storage/t_graph.csv"
    homes_deltas_path: str = "../../storage/homes_time_delta.csv"
    optimized_t_table_path: str = "../../storage/optimized_t_table.pickle"
    weather_forecast_provider: WeatherForecastProviderConfig = WeatherForecastProviderConfig()